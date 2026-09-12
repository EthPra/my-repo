"""Stage 7 (k*-factors) acceptance tests.

Hermetic, same discipline as test_ratios.py: hand-built intensity tables with numbers picked
so the arithmetic is checkable independently of the implementation. Never touches the real
Results\\/Aggregated\\ directories.
"""

from __future__ import annotations

import pandas as pd
import pytest

from mcxray_wrapper.kfactors import (
    _k_star_bi_as,
    _k_star_bi_ga,
    _k_star_ga_as,
    calibration_curves,
    composition_curves,
    compute_k_star,
    invariance_check,
    write_calibration,
    write_composition_curves,
    write_invariance,
)
from mcxray_wrapper.ratios import INTENSITY_COLUMN
from mcxray_wrapper.spec import AS, ATOMIC_WEIGHTS, BI, GA

_SYMBOL = {GA: "Ga", AS: "As", BI: "Bi"}


def _row(run_id, x_bi, thickness_nm, z, line, intensity):
    return {
        "run_id": run_id, "x_bi": x_bi, "thickness_nm": thickness_nm,
        "Atomic number": z, "Element": _SYMBOL[z], "Line": f"Line {line}",
        INTENSITY_COLUMN: intensity,
    }


def _toy_run(run_id, x_bi, thickness_nm, ga_k, ga_l, as_k, as_l, bi_l, bi_m, bi_k=5.0):
    """One run's principal-line intensities only (enough for the principal definition).

    bi_k defaults small on purpose: Bi K is a real route (LO3 names it) but a feeble one, so a
    fixture that made it comparable to Bi L would misrepresent it.
    """
    return pd.DataFrame([
        _row(run_id, x_bi, thickness_nm, GA, "Ka1", ga_k),
        _row(run_id, x_bi, thickness_nm, GA, "La", ga_l),
        _row(run_id, x_bi, thickness_nm, AS, "Ka1", as_k),
        _row(run_id, x_bi, thickness_nm, AS, "La", as_l),
        _row(run_id, x_bi, thickness_nm, BI, "Ka1", bi_k),
        _row(run_id, x_bi, thickness_nm, BI, "La", bi_l),
        _row(run_id, x_bi, thickness_nm, BI, "Ma", bi_m),
    ])


# ---- pure formula checks (Eqs 2, 4, 9), independent of the module's wiring ----

def test_bi_ga_formula_eq2():
    # k*_Bi,Ga = x * (A_Bi/A_Ga) * (I_Ga/I_Bi)
    assert _k_star_bi_ga(x=0.2, a_bi=200.0, a_ga=50.0, i_bi=10.0, i_ga=40.0) == \
        pytest.approx(0.2 * (200.0 / 50.0) * (40.0 / 10.0))  # 3.2


def test_bi_as_formula_eq4():
    # k*_Bi,As = [x/(1-x)] * (A_Bi/A_As) * (I_As/I_Bi)
    assert _k_star_bi_as(x=0.2, a_bi=200.0, a_as=100.0, i_bi=10.0, i_as=50.0) == \
        pytest.approx((0.2 / 0.8) * (200.0 / 100.0) * (50.0 / 10.0))  # 2.5


def test_ga_as_formula_eq9():
    # k*_Ga,As = [1/(1-x)] * (A_Ga/A_As) * (I_As/I_Ga)
    assert _k_star_ga_as(x=0.2, a_ga=50.0, a_as=100.0, i_ga=40.0, i_as=50.0) == \
        pytest.approx((1.0 / 0.8) * (50.0 / 100.0) * (50.0 / 40.0))  # 0.78125


# ---- wiring: compute_k_star on a toy run, checked against the same formulas by hand ----

def test_compute_k_star_matches_formula_for_one_pair():
    run = _toy_run("toy", x_bi=0.2, thickness_nm=100,
                    ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
    out = compute_k_star(run)

    row = out[(out["route"] == "Ga_As") & (out["heavy_shell"] == "K")
              & (out["light_shell"] == "K") & (out["definition"] == "principal")].iloc[0]
    expected = _k_star_ga_as(0.2, ATOMIC_WEIGHTS[GA], ATOMIC_WEIGHTS[AS], 100, 200)
    assert row["k_star"] == pytest.approx(expected)

    row = out[(out["route"] == "Bi_Ga") & (out["heavy_shell"] == "M")
              & (out["light_shell"] == "L") & (out["definition"] == "principal")].iloc[0]
    expected = _k_star_bi_ga(0.2, ATOMIC_WEIGHTS[BI], ATOMIC_WEIGHTS[GA], 20, 40)
    assert row["k_star"] == pytest.approx(expected)


def test_compute_k_star_produces_all_sixteen_pairs_times_two_definitions():
    run = _toy_run("toy", x_bi=0.1, thickness_nm=100,
                    ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
    out = compute_k_star(run)
    # Bi_Ga 3x2 + Bi_As 3x2 + Ga_As 2x2 = 16 pairs, x 2 definitions = 32 rows.
    # Bi contributes THREE heavy shells (K, L, M) since LO3 names all three.
    assert len(out) == 32
    assert set(out["route"]) == {"Bi_Ga", "Bi_As", "Ga_As"}


def test_zero_intensity_raises():
    run = _toy_run("toy", x_bi=0.1, thickness_nm=100,
                    ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=0, bi_m=20)
    with pytest.raises(ValueError, match="zero intensity"):
        compute_k_star(run)


def test_no_inversion_or_recovered_x_columns():
    """This module computes k*, nothing beyond it -- inverting a spectrum to a recovered x is
    the next, separate stage. Guard against scope creep the way ratios.py guards against
    k-factors leaking into Stage 6."""
    run = _toy_run("toy", x_bi=0.1, thickness_nm=100,
                    ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
    cols = compute_k_star(run).columns
    banned = [c for c in cols if any(t in c.lower() for t in ("x_recovered", "inverted", "quant"))]
    assert banned == []


# ---- calibration_curves: Set A only, sorted by thickness ----

def test_calibration_curves_keeps_only_set_a():
    set_a_run = _toy_run("a", x_bi=0.2, thickness_nm=2,  # in SET_A_THICKNESSES_NM
                          ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
    set_b_run = _toy_run("b", x_bi=0.01, thickness_nm=100,  # SET_B only, not SET_A
                          ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
    off_matrix_run = _toy_run("c", x_bi=0.05, thickness_nm=512,  # neither set
                               ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
    combined = pd.concat([set_a_run, set_b_run, off_matrix_run], ignore_index=True)

    out = calibration_curves(combined)
    assert set(out["run_id"]) == {"a"}


def test_calibration_curves_sorted_by_thickness():
    runs = [
        _toy_run(f"t{t}", x_bi=0.2, thickness_nm=t,
                 ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
        for t in (1024, 2, 128)  # deliberately out of order
    ]
    combined = pd.concat(runs, ignore_index=True)
    out = calibration_curves(combined)
    one_pair = out[(out["route"] == "Ga_As") & (out["heavy_shell"] == "K")
                   & (out["light_shell"] == "K") & (out["definition"] == "principal")]
    assert list(one_pair["thickness_nm"]) == [2, 128, 1024]


# ---- invariance_check: Set B only, spread across composition ----

def test_invariance_check_zero_spread_when_ratio_scales_with_prefactor():
    """Construct intensities so k*_Ga,As is EXACTLY constant across x by design: since
    k*_Ga,As = [1/(1-x)] * (A_Ga/A_As) * (I_As/I_Ga), holding I_As/I_Ga fixed while x varies
    should NOT give constant k* (the 1/(1-x) prefactor moves) -- so to build a truly invariant
    case, I_As/I_Ga must move to exactly cancel the prefactor: I_As/I_Ga = (1-x) * constant.
    """
    runs = []
    for x in (0.01, 0.05, 0.2):
        as_k = 200 * (1.0 - x)  # cancels the 1/(1-x) prefactor exactly
        runs.append(_toy_run(f"x{x}", x_bi=x, thickness_nm=100,
                              ga_k=100, ga_l=40, as_k=as_k, as_l=50, bi_l=30, bi_m=20))
    combined = pd.concat(runs, ignore_index=True)

    out = invariance_check(combined)
    row = out[(out["route"] == "Ga_As") & (out["heavy_shell"] == "K")
              & (out["light_shell"] == "K") & (out["definition"] == "principal")].iloc[0]
    assert row["relative_spread"] == pytest.approx(0.0, abs=1e-9)
    assert row["n_points"] == 3


def test_invariance_check_nonzero_spread_when_ratio_is_flat():
    """Holding I_As/I_Ga literally flat across x means k* does NOT stay constant (the 1/(1-x)
    prefactor alone moves it) -- the spread should be clearly nonzero, and by a computable
    amount: k*(x=0.2)/k*(x=0.01) = (1-0.01)/(1-0.2) = 0.99/0.8 = 1.2375.
    """
    runs = [
        _toy_run(f"x{x}", x_bi=x, thickness_nm=100,
                 ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
        for x in (0.01, 0.2)
    ]
    combined = pd.concat(runs, ignore_index=True)

    out = invariance_check(combined)
    row = out[(out["route"] == "Ga_As") & (out["heavy_shell"] == "K")
              & (out["light_shell"] == "K") & (out["definition"] == "principal")].iloc[0]
    ratio = row["k_star_max"] / row["k_star_min"]
    assert ratio == pytest.approx(0.99 / 0.8, rel=1e-6)


def test_invariance_check_keeps_only_set_b():
    set_b_run = _toy_run("b", x_bi=0.02, thickness_nm=100,
                          ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
    set_a_run = _toy_run("a", x_bi=0.2, thickness_nm=64,
                          ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
    combined = pd.concat([set_b_run, set_a_run], ignore_index=True)

    out = invariance_check(combined)
    one_pair = out[(out["route"] == "Ga_As") & (out["heavy_shell"] == "K")
                   & (out["light_shell"] == "K") & (out["definition"] == "principal")]
    assert one_pair.iloc[0]["n_points"] == 1  # only the Set B run


# ---- composition_curves: the per-point Set B data behind the summary ----

def test_composition_curves_keeps_only_set_b():
    set_b_run = _toy_run("b", x_bi=0.05, thickness_nm=100,  # in SET_B_X_BI at SET_B_THICKNESS_NM
                          ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
    set_a_run = _toy_run("a", x_bi=0.2, thickness_nm=64,  # Set A only
                          ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
    combined = pd.concat([set_b_run, set_a_run], ignore_index=True)

    out = composition_curves(combined)
    assert set(out["run_id"]) == {"b"}


def test_composition_curves_sorted_by_x():
    runs = [
        _toy_run(f"x{x}", x_bi=x, thickness_nm=100,
                 ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
        for x in (0.2, 0.01, 0.05)  # deliberately out of order
    ]
    combined = pd.concat(runs, ignore_index=True)
    out = composition_curves(combined)
    one_pair = out[(out["route"] == "Ga_As") & (out["heavy_shell"] == "K")
                   & (out["light_shell"] == "K") & (out["definition"] == "principal")]
    assert list(one_pair["x_bi"]) == [0.01, 0.05, 0.2]


def test_invariance_check_summarises_the_same_numbers():
    """The summary must describe composition_curves' values, not a separately computed set."""
    runs = [
        _toy_run(f"x{x}", x_bi=x, thickness_nm=100,
                 ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
        for x in (0.01, 0.05, 0.2)
    ]
    combined = pd.concat(runs, ignore_index=True)
    curves = composition_curves(combined)
    summary = invariance_check(combined)

    key = ("Ga_As", "K", "K", "principal")
    values = curves[(curves["route"] == key[0]) & (curves["heavy_shell"] == key[1])
                    & (curves["light_shell"] == key[2]) & (curves["definition"] == key[3])]["k_star"]
    row = summary[(summary["route"] == key[0]) & (summary["heavy_shell"] == key[1])
                  & (summary["light_shell"] == key[2]) & (summary["definition"] == key[3])].iloc[0]

    assert row["k_star_mean"] == pytest.approx(values.mean())
    assert row["k_star_min"] == pytest.approx(values.min())
    assert row["k_star_max"] == pytest.approx(values.max())
    assert row["n_points"] == len(values)


def test_invariance_check_sorted_worst_first():
    runs = [
        _toy_run(f"x{x}", x_bi=x, thickness_nm=100,
                 ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
        for x in (0.01, 0.2)
    ]
    out = invariance_check(pd.concat(runs, ignore_index=True))
    assert list(out["relative_spread"]) == sorted(out["relative_spread"], reverse=True)


# ---- write_calibration: persists the Set A table, nothing more ----

def test_write_calibration_round_trips(tmp_path):
    runs = [
        _toy_run(f"t{t}", x_bi=0.2, thickness_nm=t,
                 ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
        for t in (2, 128)
    ]
    combined_csv = tmp_path / "combined.csv"
    pd.concat(runs, ignore_index=True).to_csv(combined_csv, index=False)

    out = write_calibration(combined_csv, tmp_path / "Aggregated")
    assert out.name == "kstar_calibration_setA.csv"

    written = pd.read_csv(out)
    expected = calibration_curves(pd.read_csv(combined_csv))
    assert list(written["k_star"]) == pytest.approx(list(expected["k_star"]))
    assert list(written["thickness_nm"]) == list(expected["thickness_nm"])


def test_write_composition_curves_round_trips(tmp_path):
    runs = [
        _toy_run(f"x{x}", x_bi=x, thickness_nm=100,
                 ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
        for x in (0.01, 0.05, 0.2)
    ]
    combined_csv = tmp_path / "combined.csv"
    pd.concat(runs, ignore_index=True).to_csv(combined_csv, index=False)

    out = write_composition_curves(combined_csv, tmp_path / "Aggregated")
    assert out.name == "kstar_composition_setB.csv"

    written = pd.read_csv(out)
    expected = composition_curves(pd.read_csv(combined_csv))
    assert list(written["k_star"]) == pytest.approx(list(expected["k_star"]))
    assert list(written["x_bi"]) == pytest.approx(list(expected["x_bi"]))


def test_write_invariance_round_trips(tmp_path):
    runs = [
        _toy_run(f"x{x}", x_bi=x, thickness_nm=100,
                 ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20)
        for x in (0.01, 0.05, 0.2)
    ]
    combined_csv = tmp_path / "combined.csv"
    pd.concat(runs, ignore_index=True).to_csv(combined_csv, index=False)

    out = write_invariance(combined_csv, tmp_path / "Aggregated")
    assert out.name == "kstar_invariance_setB.csv"

    written = pd.read_csv(out)
    expected = invariance_check(pd.read_csv(combined_csv))
    assert list(written["relative_spread"]) == pytest.approx(list(expected["relative_spread"]))
    assert len(written) == 32  # 16 pairs x 2 line definitions
