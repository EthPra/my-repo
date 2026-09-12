"""Stage 7 (round trip) acceptance tests.

Hermetic, same discipline as test_kfactors.py. The most important test here isn't an
arithmetic check -- it's test_recovered_x_does_not_use_true_x_bi, which enforces the actual
design requirement (calibrate on Set A, infer Set B blind, grade only afterward) as code, not
just as a description in a docstring.
"""

from __future__ import annotations

import pandas as pd
import pytest

from mcxray_wrapper.kfactors import _k_star_bi_as, _k_star_bi_ga, _k_star_ga_as
from mcxray_wrapper.ratios import INTENSITY_COLUMN
from mcxray_wrapper.roundtrip import (
    _interpolate_k_star,
    _recover_x_bi_as,
    _recover_x_bi_ga,
    _recover_x_ga_as,
    recover_x,
    summarize,
)
from mcxray_wrapper.spec import AS, ATOMIC_WEIGHTS, BI, GA

_SYMBOL = {GA: "Ga", AS: "As", BI: "Bi"}


def _row(run_id, x_bi, thickness_nm, z, line, intensity):
    return {
        "run_id": run_id, "x_bi": x_bi, "thickness_nm": thickness_nm,
        "Atomic number": z, "Element": _SYMBOL[z], "Line": f"Line {line}",
        INTENSITY_COLUMN: intensity,
    }


def _toy_run(run_id, x_bi, thickness_nm, ga_k, ga_l, as_k, as_l, bi_l, bi_m, bi_k=5.0):
    """Principal lines only -- enough for the principal definition.

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


# ---- inverse formulas undo the forward ones (Eqs 2, 4, 9), independent of the module's wiring ----

def test_ga_as_inverse_undoes_forward():
    x = 0.2
    k = _k_star_ga_as(x, 50.0, 100.0, i_ga=40.0, i_as=50.0)
    assert _recover_x_ga_as(k, 50.0, 100.0, i_ga=40.0, i_as=50.0) == pytest.approx(x)


def test_bi_ga_inverse_undoes_forward():
    x = 0.1
    k = _k_star_bi_ga(x, 200.0, 50.0, i_bi=10.0, i_ga=40.0)
    assert _recover_x_bi_ga(k, 200.0, 50.0, i_bi=10.0, i_ga=40.0) == pytest.approx(x)


def test_bi_as_inverse_undoes_forward():
    x = 0.15
    k = _k_star_bi_as(x, 200.0, 100.0, i_bi=10.0, i_as=50.0)
    assert _recover_x_bi_as(k, 200.0, 100.0, i_bi=10.0, i_as=50.0) == pytest.approx(x)


# ---- interpolation ----

def test_interpolate_midpoint():
    points = [(64.0, 2.0), (128.0, 4.0)]
    assert _interpolate_k_star(points, 96.0) == pytest.approx(3.0)  # exact midpoint


def test_interpolate_uneven_fraction():
    points = [(64.0, 2.326533), (128.0, 2.714289)]
    frac = (100.0 - 64.0) / (128.0 - 64.0)  # 0.5625
    expected = 2.326533 + (2.714289 - 2.326533) * frac
    assert _interpolate_k_star(points, 100.0) == pytest.approx(expected)


def test_interpolate_outside_range_raises():
    points = [(64.0, 2.0), (128.0, 4.0)]
    with pytest.raises(ValueError, match="outside the Set A calibration range"):
        _interpolate_k_star(points, 2000.0)


# ---- end-to-end: calibrate on toy "Set A" (t=64, t=128, x=0.2), recover toy "Set B" (t=100) ----

def _toy_matrix():
    set_a = pd.concat([
        _toy_run("a64", x_bi=0.2, thickness_nm=64,
                 ga_k=100, ga_l=40, as_k=200, as_l=50, bi_l=30, bi_m=20),
        _toy_run("a128", x_bi=0.2, thickness_nm=128,
                 ga_k=90, ga_l=35, as_k=210, as_l=55, bi_l=28, bi_m=22),
    ], ignore_index=True)
    set_b = pd.concat([
        _toy_run("b001", x_bi=0.01, thickness_nm=100,
                 ga_k=95, ga_l=38, as_k=205, as_l=52, bi_l=29, bi_m=21),
        _toy_run("b002", x_bi=0.02, thickness_nm=100,
                 ga_k=95, ga_l=38, as_k=205, as_l=52, bi_l=29, bi_m=21),  # same intensities
    ], ignore_index=True)
    return pd.concat([set_a, set_b], ignore_index=True)


def test_recovered_x_matches_hand_worked_ga_as_k_k():
    combined = _toy_matrix()
    out = recover_x(combined, target_thickness=100)
    row = out[(out["run_id"] == "b001") & (out["route"] == "Ga_As")
              & (out["heavy_shell"] == "K") & (out["light_shell"] == "K")
              & (out["definition"] == "principal")].iloc[0]

    a_ga, a_as = ATOMIC_WEIGHTS[GA], ATOMIC_WEIGHTS[AS]
    k64 = _k_star_ga_as(0.2, a_ga, a_as, i_ga=100, i_as=200)
    k128 = _k_star_ga_as(0.2, a_ga, a_as, i_ga=90, i_as=210)
    frac = (100 - 64) / (128 - 64)
    k100 = k64 + (k128 - k64) * frac
    expected_x = 1.0 - (a_ga / a_as) * (205 / 95) / k100

    assert row["k_star_used"] == pytest.approx(k100)
    assert row["recovered_x"] == pytest.approx(expected_x)
    assert row["true_x_bi"] == 0.01
    assert row["error"] == pytest.approx(expected_x - 0.01)


def test_produces_all_32_combos_per_set_b_run():
    combined = _toy_matrix()
    out = recover_x(combined, target_thickness=100)
    assert len(out) == 2 * 32  # 2 Set B runs * 16 pairs * 2 definitions


# ---- the leakage guard: recovered_x must not depend on the run's own true x_bi ----

def test_recovered_x_does_not_use_true_x_bi():
    """b001 (x=0.01) and b002 (x=0.02) have IDENTICAL measured intensities in the toy matrix
    above. If recovered_x were computed correctly -- from intensities and the Set A
    calibration only -- both runs must get the EXACT same recovered_x despite their different
    true composition. If this test ever fails, the inversion has started reading the run's
    own known answer, which would make the whole round trip meaningless."""
    combined = _toy_matrix()
    out = recover_x(combined, target_thickness=100)

    b001 = out[out["run_id"] == "b001"].sort_values(
        ["route", "heavy_shell", "light_shell", "definition"]).reset_index(drop=True)
    b002 = out[out["run_id"] == "b002"].sort_values(
        ["route", "heavy_shell", "light_shell", "definition"]).reset_index(drop=True)

    assert (b001["recovered_x"].to_numpy() == pytest.approx(b002["recovered_x"].to_numpy()))
    assert (b001["true_x_bi"] != b002["true_x_bi"]).all()
    assert (b001["error"].to_numpy() != pytest.approx(b002["error"].to_numpy()))


# ---- summarize ----

def test_summarize_one_row_per_set_b_run():
    combined = _toy_matrix()
    out = summarize(recover_x(combined, target_thickness=100))
    assert len(out) == 2
    assert set(out["run_id"]) == {"b001", "b002"}
    assert (out["n_estimates"] == 32).all()


def test_summarize_mean_abs_error_is_nonnegative():
    combined = _toy_matrix()
    out = summarize(recover_x(combined, target_thickness=100))
    assert (out["mean_abs_error"] >= 0).all()


# ---- P1.2: recovery held out in BOTH unknowns, indexed on a measurable K/L ratio ----

def _kl_matrix():
    """Set A spanning a range of K/L, plus two Set B runs with IDENTICAL intensities.

    Identical intensities but different recorded x_bi AND different recorded thickness -- so a
    single fixture tests both leakage guards at once.
    """
    set_a = pd.concat([
        _toy_run(f"a{t}", x_bi=0.2, thickness_nm=t,
                 ga_k=100 + t, ga_l=max(5.0, 60 - t / 20),
                 as_k=200 + t, as_l=max(5.0, 80 - t / 15),
                 bi_l=30, bi_m=20)
        for t in (2, 4, 8, 16, 32, 64, 128, 256, 512, 1024)
    ], ignore_index=True)
    set_b = pd.concat([
        _toy_run("b001", x_bi=0.01, thickness_nm=100,
                 ga_k=150, ga_l=40, as_k=250, as_l=55, bi_l=29, bi_m=21),
        _toy_run("b002", x_bi=0.02, thickness_nm=100,
                 ga_k=150, ga_l=40, as_k=250, as_l=55, bi_l=29, bi_m=21),
    ], ignore_index=True)
    return pd.concat([set_a, set_b], ignore_index=True)


def test_kl_recovery_never_reads_the_true_composition():
    """b001 (x=0.01) and b002 (x=0.02) share intensities exactly, so both must recover the same
    x. If they differ, the inversion has started reading the answer it is meant to infer."""
    from mcxray_wrapper.roundtrip import recover_x_via_kl

    out = recover_x_via_kl(_kl_matrix())
    key = ["route", "heavy_shell", "light_shell", "definition"]
    b001 = out[out["run_id"] == "b001"].sort_values(key).reset_index(drop=True)
    b002 = out[out["run_id"] == "b002"].sort_values(key).reset_index(drop=True)

    assert b001["recovered_x"].to_numpy() == pytest.approx(b002["recovered_x"].to_numpy())
    assert (b001["true_x_bi"] != b002["true_x_bi"]).all()


def test_kl_recovery_never_reads_the_true_thickness():
    """The whole point of P1.2. Change only the recorded thickness -- which a real experimenter
    would not know -- and every recovered x must be unchanged.

    recover_x() cannot pass this: it looks the calibration up AT that thickness.
    """
    from mcxray_wrapper.roundtrip import recover_x_via_kl

    combined = _kl_matrix()
    original = recover_x_via_kl(combined)

    # Relabel the Set B runs as a wildly different thickness, leaving every intensity untouched.
    # thickness_nm still selects which runs are Set B, so target_thickness moves with it -- the
    # point is that it must play no part in the COMPUTATION, not that it is unused entirely.
    relabelled = combined.copy()
    mask = relabelled["run_id"].isin(["b001", "b002"])
    relabelled.loc[mask, "thickness_nm"] = 777.0
    lied = recover_x_via_kl(relabelled, target_thickness=777.0)

    assert list(lied["true_thickness_nm"]) == [777.0] * len(lied)   # the lie really landed
    assert list(original["recovered_x"]) == pytest.approx(list(lied["recovered_x"]))
    assert list(original["k_star_used"]) == pytest.approx(list(lied["k_star_used"]))

    # recover_x(), by contrast, CANNOT survive this: it looks the calibration up AT the
    # thickness it is handed, so relabelling moves its answer even though no intensity changed.
    # That difference is precisely the weakness P1.2 exists to remove.
    before = recover_x(combined, target_thickness=100.0)["recovered_x"].to_numpy()
    after = recover_x(relabelled, target_thickness=777.0)["recovered_x"].to_numpy()
    assert after != pytest.approx(before)


def test_unknowns_override_reproduces_default_set_b_selection():
    """Passing `unknowns` explicitly set to the Set B subset must reproduce the default (None)
    behaviour exactly -- the whole claim that this is additive, not a rewrite, rests on this."""
    from mcxray_wrapper.roundtrip import recover_x_via_kl
    from mcxray_wrapper.matrix import SET_B_THICKNESS_NM, SET_B_X_BI

    combined = _kl_matrix()
    default = recover_x_via_kl(combined)
    set_b = combined[
        (combined["thickness_nm"] == SET_B_THICKNESS_NM) & (combined["x_bi"].isin(SET_B_X_BI))
    ]
    explicit = recover_x_via_kl(combined, unknowns=set_b)
    pd.testing.assert_frame_equal(default, explicit)


def test_unknowns_override_runs_a_different_thickness_arm():
    """The actual point of the parameter: run the SAME held-out recovery on runs at a thickness
    Set B never tests, using their own ratios only -- exactly Set C's low-x thickness arm. This
    must not raise (the calibration lookup is on K/L, not thickness) and must produce one row set
    per route/definition for the runs actually passed in, not for Set B.

    `unknowns` selects WHICH rows of `combined` count as unknowns for the inversion, but the
    ratio lookup still reads from `combined` as a whole -- so the low-x rows must be added to
    `combined` itself, exactly as `_set_c_unknowns` does (it filters `combined`, never rows from
    outside it)."""
    from mcxray_wrapper.roundtrip import recover_x_via_kl

    low_x_arm = pd.concat([
        _toy_run("c032", x_bi=0.01, thickness_nm=32,
                 ga_k=140, ga_l=45, as_k=230, as_l=58, bi_l=28, bi_m=19),
        _toy_run("c064", x_bi=0.01, thickness_nm=64,
                 ga_k=145, ga_l=42, as_k=240, as_l=56, bi_l=28, bi_m=19),
    ], ignore_index=True)
    combined = pd.concat([_kl_matrix(), low_x_arm], ignore_index=True)

    out = recover_x_via_kl(combined, unknowns=low_x_arm)
    assert set(out["run_id"]) == {"c032", "c064"}
    assert set(out["true_thickness_nm"]) == {32.0, 64.0}
    # Recovery must still have succeeded -- a real number, not a fabricated placeholder.
    assert out["recovered_x"].notna().all()


def test_write_roundtrips_includes_set_c_low_x_arm(tmp_path):
    """`write_roundtrips` must persist the Set C low-x-thickness-arm recovery alongside the
    original two -- this is the gap closed 2026-08-21 (decisions.md), and losing it back to a
    scratch script would reopen exactly that gap."""
    from mcxray_wrapper.roundtrip import write_roundtrips
    from mcxray_wrapper.matrix import SET_C_THICKNESSES_NM, SET_C_X_BI

    set_c = pd.concat([
        _toy_run(f"c{t}", x_bi=SET_C_X_BI, thickness_nm=t,
                 ga_k=140 + t / 100, ga_l=45, as_k=230 + t / 100, as_l=58, bi_l=28, bi_m=19)
        for t in SET_C_THICKNESSES_NM
    ], ignore_index=True)
    combined = pd.concat([_kl_matrix(), set_c], ignore_index=True)
    combined_csv = tmp_path / "combined.csv"
    combined.to_csv(combined_csv, index=False)

    written = write_roundtrips(combined_csv, tmp_path / "out")
    assert "As_K_L_setc_lowx" in written
    assert "Ga_K_L_setc_lowx" in written

    out = pd.read_csv(written["As_K_L_setc_lowx"])
    assert set(out["run_id"]) == {f"c{t}" for t in SET_C_THICKNESSES_NM}
    assert (out["true_x_bi"] == SET_C_X_BI).all()


def test_kl_axis_selection_changes_the_lookup():
    """As K/L and Ga K/L are different axes and must give different k* -- otherwise the axis
    argument is not doing anything and the Set C result could not be acted on."""
    from mcxray_wrapper.roundtrip import recover_x_via_kl

    as_axis = recover_x_via_kl(_kl_matrix(), axis="As_K_L")
    ga_axis = recover_x_via_kl(_kl_matrix(), axis="Ga_K_L")
    assert set(as_axis["kl_axis"]) == {"As_K_L"}
    assert list(as_axis["measured_kl"]) != pytest.approx(list(ga_axis["measured_kl"]))


def test_kl_recovery_matches_ratio_definition():
    """A summed k* must be looked up at a summed K/L, never a principal one."""
    from mcxray_wrapper.ratios import compute_ratios
    from mcxray_wrapper.roundtrip import recover_x_via_kl

    combined = _kl_matrix()
    out = recover_x_via_kl(combined)
    ratios = compute_ratios(combined).set_index("run_id")

    for definition in ("principal", "summed"):
        row = out[(out["run_id"] == "b001") & (out["definition"] == definition)].iloc[0]
        assert row["measured_kl"] == pytest.approx(ratios.at["b001", f"As_K_L_{definition}"])


def test_unknown_kl_axis_raises():
    from mcxray_wrapper.roundtrip import recover_x_via_kl

    with pytest.raises(ValueError, match="unknown K/L axis"):
        recover_x_via_kl(_kl_matrix(), axis="Bi_L_M")
