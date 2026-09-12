"""Stage 6b (sum-peak synthesis) acceptance tests.

Hermetic. The magnitude of the artefact is a modelling choice this project must state and
sweep, so these tests do NOT pin a physical answer -- they pin the MECHANICS: that each switch
does what it claims, that the arithmetic is right, and that a swept level cannot produce
nonsense (negative parents, ratios moving the wrong way).
"""

from __future__ import annotations

import math

import pandas as pd
import pytest

from mcxray_wrapper.ratios import INTENSITY_COLUMN
from mcxray_wrapper.spec import AS, BI, GA
from mcxray_wrapper.sumpeak import (
    M_BAND_FACTOR_MEASURED,
    SENSITIVITY_LEVELS,
    fake_counts,
    synthesise,
    write_sumpeak,
)

_SYMBOL = {GA: "Ga", AS: "As", BI: "Bi"}


def _row(run_id, x_bi, z, line, intensity):
    return {
        "run_id": run_id, "x_bi": x_bi, "thickness_nm": 100,
        "Atomic number": z, "Element": _SYMBOL[z], "Line": f"Line {line}",
        INTENSITY_COLUMN: intensity,
    }


def _run(run_id="r", x_bi=0.1, ga_la=1000.0, as_la=1000.0, bi_ma=100.0, bi_la=150.0,
         ga_lb=50.0, as_lb=60.0):
    return pd.DataFrame([
        _row(run_id, x_bi, GA, "La", ga_la), _row(run_id, x_bi, GA, "Lb1", ga_lb),
        _row(run_id, x_bi, AS, "La", as_la), _row(run_id, x_bi, AS, "Lb1", as_lb),
        _row(run_id, x_bi, BI, "Ma", bi_ma), _row(run_id, x_bi, BI, "La", bi_la),
    ])


# ---- the count arithmetic ----

def test_intensity_basis_is_the_geometric_mean():
    """Symmetric in the two parents, and reduces to "level x I" when they are equal."""
    assert fake_counts(1000.0, 1000.0, 0.10, "intensity") == pytest.approx(100.0)
    assert fake_counts(400.0, 900.0, 0.10, "intensity") == pytest.approx(0.10 * math.sqrt(400 * 900))
    # symmetry: swapping the parents cannot change the answer
    assert fake_counts(400.0, 900.0, 0.05, "intensity") == \
        pytest.approx(fake_counts(900.0, 400.0, 0.05, "intensity"))


def test_rate_product_scales_quadratically_with_dose():
    """The distinguishing physical feature: doubling the beam current quadruples true pile-up,
    where an intensity fraction only doubles. This is what makes the two bases separable."""
    ref = 1000.0
    single = fake_counts(1000.0, 1000.0, 0.01, "rate_product", ref)
    doubled = fake_counts(2000.0, 2000.0, 0.01, "rate_product", ref)
    assert doubled == pytest.approx(4 * single)

    lin_single = fake_counts(1000.0, 1000.0, 0.01, "intensity")
    lin_doubled = fake_counts(2000.0, 2000.0, 0.01, "intensity")
    assert lin_doubled == pytest.approx(2 * lin_single)


def test_fake_counts_cannot_exceed_the_scarcer_parent():
    """Each event consumes one photon from each parent, so the scarcer one is a hard ceiling.
    Without this a large swept level would drive a conserved parent negative."""
    assert fake_counts(50.0, 5000.0, 10.0, "intensity") == pytest.approx(50.0)


def test_unknown_basis_raises():
    with pytest.raises(ValueError, match="basis must be one of"):
        fake_counts(1.0, 1.0, 0.1, "handwaving")


# ---- choice 1: which lines feed it ----

def test_alpha_beta_uses_more_parent_intensity_than_alpha_only():
    """All four Ga-L x As-L pairings land within 59 eV of each other and of Bi Ma, so including
    Lb is the physically complete set. It must therefore give a larger artefact."""
    alpha = synthesise(_run(), levels=(0.01,), parents="alpha_only").iloc[0]
    both = synthesise(_run(), levels=(0.01,), parents="alpha_beta").iloc[0]
    assert both["i_ga_parent"] > alpha["i_ga_parent"]
    assert both["fake_counts"] > alpha["fake_counts"]


def test_unknown_parent_set_raises():
    with pytest.raises(ValueError, match="parents must be one of"):
        synthesise(_run(), parents="everything")


# ---- choice 3: photon conservation ----

def test_conserve_depletes_both_parents_by_the_fake_count():
    """One Ga La and one As La are consumed per fake Bi Ma count -- exactly what Walther's
    correction undid when it "transferred 600 counts from Bi M to each of Ga L and As L"."""
    row = synthesise(_run(), levels=(0.05,), conserve=True).iloc[0]
    assert row["i_ga_after"] == pytest.approx(row["i_ga_parent"] - row["fake_counts"])
    assert row["i_as_after"] == pytest.approx(row["i_as_parent"] - row["fake_counts"])


def test_conserve_false_leaves_parents_untouched():
    row = synthesise(_run(), levels=(0.05,), conserve=False).iloc[0]
    assert row["i_ga_after"] == pytest.approx(row["i_ga_parent"])
    assert row["i_as_after"] == pytest.approx(row["i_as_parent"])


def test_parents_never_go_negative_even_at_absurd_levels():
    for row in synthesise(_run(ga_la=10.0, as_la=10.0), levels=(5.0,), conserve=True).itertuples():
        assert row.i_ga_after >= 0
        assert row.i_as_after >= 0


# ---- choice 4: the M-band baseline ----

def test_m_band_factor_raises_the_baseline_and_softens_the_damage():
    """A detector sees the whole unresolved M band, so measuring the pile-up against simulated
    Ma alone uses a baseline 1.743x too small and OVERSTATES the corruption."""
    simulated = synthesise(_run(), levels=(0.01,)).iloc[0]
    measured = synthesise(_run(), levels=(0.01,), m_band_factor=M_BAND_FACTOR_MEASURED).iloc[0]

    assert measured["bi_m_baseline"] == pytest.approx(
        simulated["bi_m_simulated"] * M_BAND_FACTOR_MEASURED)
    assert measured["fake_fraction_of_bi_m"] < simulated["fake_fraction_of_bi_m"]


# ---- direction and magnitude sanity ----

def test_corruption_always_lowers_bi_l_over_m():
    """The artefact ADDS counts to Bi M, so the L/M ratio must fall. If it ever rose, a sign
    error would be masquerading as a physical effect."""
    out = synthesise(_run(), levels=SENSITIVITY_LEVELS)
    assert (out["bi_l_m_corrupted"] < out["bi_l_m_clean"]).all()


def test_damage_grows_with_level():
    out = synthesise(_run(), levels=SENSITIVITY_LEVELS).sort_values("level")
    assert list(out["fake_fraction_of_bi_m"]) == sorted(out["fake_fraction_of_bi_m"])


def test_weak_bi_m_is_hurt_far_more_by_the_same_level():
    """The prediction that makes this matter for LO4: identical parents, weaker Bi M, same
    level -> far larger fractional corruption. This is why low x is the dangerous regime."""
    strong = synthesise(_run(bi_ma=1000.0), levels=(0.01,)).iloc[0]
    weak = synthesise(_run(bi_ma=10.0), levels=(0.01,)).iloc[0]
    assert weak["fake_fraction_of_bi_m"] == pytest.approx(
        100 * strong["fake_fraction_of_bi_m"])


def test_zero_bi_m_raises():
    with pytest.raises(ValueError, match="cannot form a ratio"):
        synthesise(_run(bi_ma=0.0))


# ---- provenance and the writer ----

def test_every_row_records_the_settings_that_produced_it():
    """A stored result must carry its modelling choices; these are decisions, not defaults."""
    out = synthesise(_run(), levels=(0.01,), parents="alpha_beta", basis="intensity",
                     conserve=False, m_band_factor=M_BAND_FACTOR_MEASURED).iloc[0]
    assert out["parents"] == "alpha_beta"
    assert out["basis"] == "intensity"
    assert out["conserve"] is False or out["conserve"] == False  # noqa: E712
    assert out["m_band_factor"] == pytest.approx(M_BAND_FACTOR_MEASURED)


def test_one_row_per_run_per_level():
    combined = pd.concat([_run("a"), _run("b")], ignore_index=True)
    out = synthesise(combined, levels=SENSITIVITY_LEVELS)
    assert len(out) == 2 * len(SENSITIVITY_LEVELS)


def test_write_sumpeak_round_trips(tmp_path):
    combined_csv = tmp_path / "combined.csv"
    _run().to_csv(combined_csv, index=False)
    out = write_sumpeak(combined_csv, tmp_path / "Aggregated", levels=(0.01,))
    assert out.name == "sumpeak_sensitivity.csv"
    assert len(pd.read_csv(out)) == 1


# ---- apply_to_intensities: the as-measured table, and the second-order hit ----

def test_as_measured_table_is_interchangeable_with_the_real_one():
    """Same columns, same rows -- nothing downstream should need to know it is synthetic."""
    from mcxray_wrapper.sumpeak import apply_to_intensities

    original = _run()
    out = apply_to_intensities(original, level=0.01)
    assert list(out.columns) == list(original.columns)
    assert len(out) == len(original)


def test_direct_hit_raises_bi_m():
    from mcxray_wrapper.sumpeak import apply_to_intensities

    out = apply_to_intensities(_run(), level=0.01, conserve=False)
    bi_m = out[(out["Atomic number"] == BI) & (out["Line"] == "Line Ma")][INTENSITY_COLUMN].iloc[0]
    assert bi_m > 100.0  # the clean value


def test_indirect_hit_depletes_the_parents_only_when_conserving():
    """The leak: fake Bi counts are paid for out of Ga L and As L."""
    from mcxray_wrapper.sumpeak import apply_to_intensities

    def parent(df, z):
        return df[(df["Atomic number"] == z) & (df["Line"] == "Line La")][INTENSITY_COLUMN].iloc[0]

    conserved = apply_to_intensities(_run(), level=0.01, conserve=True)
    naive = apply_to_intensities(_run(), level=0.01, conserve=False)

    assert parent(conserved, GA) < 1000.0
    assert parent(conserved, AS) < 1000.0
    assert parent(naive, GA) == pytest.approx(1000.0)


def test_depletion_is_shared_in_proportion_to_line_intensity():
    """With alpha_beta, a pile-up consumes whichever photon arrived, so the loss is split
    across an element's parent lines by their share of the total, not taken from La alone."""
    from mcxray_wrapper.sumpeak import apply_to_intensities

    run = _run(ga_la=900.0, ga_lb=100.0)
    out = apply_to_intensities(run, level=0.01, parents="alpha_beta", conserve=True)

    def line(z, name):
        return out[(out["Atomic number"] == z) & (out["Line"] == f"Line {name}")][INTENSITY_COLUMN].iloc[0]

    lost_la, lost_lb = 900.0 - line(GA, "La"), 100.0 - line(GA, "Lb1")
    assert lost_la == pytest.approx(9 * lost_lb)  # 900:100 share
    assert lost_la + lost_lb > 0


def test_depletion_raises_the_thickness_proxy():
    """THE SECOND-ORDER EFFECT, asserted directly. As L is depleted while As K is untouched, so
    As K/L rises -- and since that ratio is the thickness proxy, the foil reads as THICKER than
    it is. That mis-read then selects the wrong k*."""
    from mcxray_wrapper.ratios import compute_ratios
    from mcxray_wrapper.sumpeak import apply_to_intensities

    run = pd.concat([_run(), pd.DataFrame([
        _row("r", 0.1, AS, "Ka1", 5000.0), _row("r", 0.1, GA, "Ka1", 4000.0),
    ])], ignore_index=True)

    clean = compute_ratios(run).iloc[0]["As_K_L_principal"]
    measured = compute_ratios(apply_to_intensities(run, level=0.01, conserve=True)).iloc[0]["As_K_L_principal"]

    assert measured > clean          # looks thicker than it is
    # and without conservation the proxy is untouched -- isolating the two hits
    naive = compute_ratios(apply_to_intensities(run, level=0.01, conserve=False)).iloc[0]["As_K_L_principal"]
    assert naive == pytest.approx(clean)


def test_zero_level_reproduces_the_original_table():
    """A sanity anchor: no artefact must mean no change at all."""
    from mcxray_wrapper.sumpeak import apply_to_intensities

    original = _run()
    out = apply_to_intensities(original, level=0.0)
    assert list(out[INTENSITY_COLUMN]) == pytest.approx(list(original[INTENSITY_COLUMN]))


def test_run_ids_limits_which_runs_are_affected():
    """The calibration must stay as simulated. Corrupting both sides makes the error largely
    self-cancel, which silently understates the damage -- measured on the real data, applying it
    to the whole table left recovered x at x=0.20 visibly unchanged."""
    from mcxray_wrapper.sumpeak import apply_to_intensities

    combined = pd.concat([_run("unknown"), _run("calibration")], ignore_index=True)
    out = apply_to_intensities(combined, level=0.01, run_ids={"unknown"})

    def bi_m(df, run_id):
        m = (df["run_id"] == run_id) & (df["Atomic number"] == BI) & (df["Line"] == "Line Ma")
        return df[m][INTENSITY_COLUMN].iloc[0]

    assert bi_m(out, "unknown") > 100.0
    assert bi_m(out, "calibration") == pytest.approx(100.0)   # untouched


def test_as_measured_unknowns_leaves_the_calibration_clean():
    """Set A is the calibration and must survive untouched; Set B is the unknown and must not."""
    from mcxray_wrapper.matrix import SET_A_THICKNESSES_NM, SET_A_X_BI
    from mcxray_wrapper.sumpeak import as_measured_unknowns

    rows = []
    for t in SET_A_THICKNESSES_NM:                       # calibration
        rows.append(_run(f"a{t}", x_bi=SET_A_X_BI))
        rows[-1]["thickness_nm"] = t
    unknown = _run("b", x_bi=0.01)                        # Set B: 100 nm, x in SET_B_X_BI
    unknown["thickness_nm"] = 100
    combined = pd.concat(rows + [unknown], ignore_index=True)

    out = as_measured_unknowns(combined, level=0.01)

    def bi_m(run_id):
        m = (out["run_id"] == run_id) & (out["Atomic number"] == BI) & (out["Line"] == "Line Ma")
        return out[m][INTENSITY_COLUMN].iloc[0]

    assert bi_m("b") > 100.0
    for t in SET_A_THICKNESSES_NM:
        assert bi_m(f"a{t}") == pytest.approx(100.0)
