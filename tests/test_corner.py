"""Corner analysis acceptance tests -- is rho.t a sufficient absorption coordinate?

Mostly hermetic, on synthetic tables where the answer is known by construction. The two that
carry the weight:

  test_pure_rho_t_dependence_gives_zero_residual -- builds a table where the ratio genuinely IS
    a function of rho.t alone. If the method could not return "sufficient" for such a table, a
    non-zero residual on the real data would mean nothing.
  test_real_data_residuals_match_the_report -- pins REPORT.md 23's headline numbers, so they are
    machine-checked rather than transcribed by hand.
"""

from __future__ import annotations

import pandas as pd
import pytest

from mcxray_wrapper.corner import (
    RHO_T_COLUMN,
    compare_arms,
    matched_thickness,
    rho_t_table,
    write_corner_analysis,
)

# Mirrors the real matrix: the reference arm (Set A) runs 2-1024 nm, the test arm (Set C) only
# the thick half. That span matters -- the test arm is LESS dense, so at a shared thickness its
# rho.t is lower, and only the reference arm's thin points keep those values inside the
# interpolation range. An earlier fixture gave both arms identical thicknesses and tripped the
# extrapolation guard, which was the guard working, not a bug.
_REFERENCE_THICKNESSES = [2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
_THICKNESSES = [32, 64, 128, 256, 512, 1024]


def _table(reference_fn, test_fn, ref_density=5.692, test_density=5.3386):
    """Two composition arms, with ratios from the given functions.

    Each function receives rho_t and returns the ratio, so a test can make the ratio depend on
    rho.t alone (or not) by construction.
    """
    rows = []
    for x_bi, density, fn, thicknesses in (
        (0.20, ref_density, reference_fn, _REFERENCE_THICKNESSES),
        (0.01, test_density, test_fn, _THICKNESSES),
    ):
        for t in thicknesses:
            rho_t = density * t
            rows.append({
                "run_id": f"x{x_bi}_{t}nm", "x_bi": x_bi, "thickness_nm": t,
                "mass_density_g_cm3": density,
                "Ga_K_L_principal": fn(rho_t),
                "As_K_L_principal": fn(rho_t),
            })
    return pd.DataFrame(rows)


# ---- the definition of rho.t ----

def test_rho_t_is_density_times_thickness():
    df = rho_t_table(_table(lambda r: 1.0, lambda r: 1.0))
    row = df.iloc[0]
    assert row[RHO_T_COLUMN] == pytest.approx(row["mass_density_g_cm3"] * row["thickness_nm"])


def test_missing_column_raises():
    with pytest.raises(ValueError, match="mass_density_g_cm3"):
        rho_t_table(pd.DataFrame({"thickness_nm": [1]}))


# ---- the load-bearing pair: can the method return BOTH answers? ----

def test_pure_rho_t_dependence_gives_zero_residual():
    """Both arms share one function of rho.t, so rho.t IS sufficient by construction.

    Without this test a non-zero residual on the real data would be uninterpretable -- it could
    just mean the method always reports one.
    """
    curve = lambda rho_t: 1.0 + 3.0e-4 * rho_t
    out = compare_arms(_table(curve, curve))
    assert out["residual_pct"].abs().max() == pytest.approx(0.0, abs=1e-9)


def test_composition_dependence_is_detected_with_the_right_sign():
    """The test arm absorbs LESS (less Bi), so its K/L sits BELOW the rho.t prediction."""
    reference = lambda rho_t: 1.0 + 3.0e-4 * rho_t
    test = lambda rho_t: 1.0 + 2.0e-4 * rho_t          # same rho.t, weaker response
    out = compare_arms(_table(reference, test))
    assert (out["residual_pct"] < 0).all()
    # and the discrepancy must GROW with rho.t -- the signature of an absorption effect
    ga = out[out["ratio"] == "Ga_K_L_principal"].sort_values(RHO_T_COLUMN)
    assert list(ga["residual_pct"]) == sorted(ga["residual_pct"], reverse=True)


# ---- guards ----

def test_extrapolation_raises():
    """A test point beyond the reference arm's span must not be silently extrapolated."""
    df = _table(lambda r: 1.0 + 3e-4 * r, lambda r: 1.0 + 3e-4 * r)
    # push one test run far past the reference arm's thickest point
    df.loc[(df.x_bi == 0.01) & (df.thickness_nm == 1024), "thickness_nm"] = 100_000
    with pytest.raises(ValueError, match="outside the reference arm"):
        compare_arms(df)


def test_missing_arm_raises():
    df = _table(lambda r: 1.0, lambda r: 1.0)
    with pytest.raises(ValueError, match="no runs at x_bi"):
        compare_arms(df, test_x=0.99)


# ---- matched-thickness companion ----

def test_matched_thickness_needs_no_interpolation():
    """Compares only at shared thicknesses, so it makes no modelling assumption at all."""
    out = matched_thickness(_table(lambda r: 1.0 + 3e-4 * r, lambda r: 1.0 + 2e-4 * r))
    assert sorted(out["thickness_nm"].unique()) == _THICKNESSES
    assert (out["difference_pct"] < 0).all()
    # rho.t differs by a CONSTANT fraction -- that is what makes a growing effect meaningful
    frac = out["test_rho_t"] / out["reference_rho_t"]
    assert frac.std() == pytest.approx(0.0, abs=1e-12)


def test_matched_thickness_without_shared_thickness_raises():
    df = _table(lambda r: 1.0, lambda r: 1.0)
    df.loc[df.x_bi == 0.01, "thickness_nm"] *= 3  # no overlap
    with pytest.raises(ValueError, match="share no thickness"):
        matched_thickness(df)


# ---- regression against the real production data ----

def test_real_data_residuals_match_the_report():
    """Pins REPORT.md 23: Ga K/L ~ -22.8% at 1024 nm, As K/L ~ -1.6%, at matched rho.t.

    This is what turns those numbers from transcription into a checked result. Skips rather
    than fails if the aggregated table is absent, so the suite stays runnable anywhere.
    """
    from pathlib import Path

    stored = Path(r"C:\MCXRAY\Sim\Aggregated\diagnostic_ratios.csv")
    if not stored.is_file():
        pytest.skip("aggregated ratio table not present")

    out = compare_arms(pd.read_csv(stored))
    thickest = out[out["thickness_nm"] == 1024].set_index("ratio")["residual_pct"]

    assert thickest["Ga_K_L_principal"] == pytest.approx(-22.8, abs=0.3)
    assert thickest["As_K_L_principal"] == pytest.approx(-1.6, abs=0.3)
    # the finding itself: Ga K/L is an order of magnitude more composition-sensitive
    assert abs(thickest["Ga_K_L_principal"]) > 10 * abs(thickest["As_K_L_principal"])


def test_write_corner_analysis_round_trips(tmp_path):
    df = _table(lambda r: 1.0 + 3e-4 * r, lambda r: 1.0 + 2e-4 * r)
    ratios_csv = tmp_path / "diagnostic_ratios.csv"
    df.to_csv(ratios_csv, index=False)

    out = write_corner_analysis(ratios_csv, tmp_path / "Aggregated")
    assert out.name == "corner_rho_t_setA_vs_setC.csv"

    written = pd.read_csv(out)
    assert set(written["comparison"]) == {"matched_rho_t", "matched_thickness"}
    assert len(written[written["comparison"] == "matched_rho_t"]) == len(compare_arms(df))
