"""Absorption-model fits and curve crossings -- acceptance tests.

The load-bearing tests here are the two limits of the absorption factor and the round trip
(generate data from known parameters, recover them). If the fitter cannot recover parameters it
generated itself, its R^2 on real data means nothing.
"""

from __future__ import annotations

import math

import pandas as pd
import pytest

from mcxray_wrapper.absorption import (
    absorption_factor,
    compare_models,
    crossing,
    crossing_table,
    fit_diagnostics,
    fit_ratio_curve,
    ratio_model,
    write_absorption_analysis,
)

_THICKNESSES = [2, 4, 8, 16, 32, 64, 100, 128, 256, 512, 1024]


def _ratio_frame(params, x_bi=0.20):
    """A ratio table generated FROM the model, so the true parameters are known."""
    rows = []
    for t in _THICKNESSES:
        row = {"run_id": f"r{t}", "x_bi": x_bi, "thickness_nm": t,
               "mass_density_g_cm3": 5.692}
        for stem, (A, ch, cs) in params.items():
            row[f"{stem}_principal"] = ratio_model(t, A, ch, cs)
        rows.append(row)
    return pd.DataFrame(rows)


_TRUTH = {
    "Ga_K_L": (1.32, 1.1e-4, 2.8e-3),
    "As_K_L": (1.11, 1.8e-4, 5.1e-3),
    "Bi_L_M": (1.38, 1.7e-4, 1.9e-3),
}


# ---- the absorption factor's two limits ----

def test_thin_foil_absorbs_nothing():
    """f(X) -> 1 as X -> 0. A vanishingly thin foil cannot absorb its own emission."""
    assert absorption_factor(0.0) == pytest.approx(1.0)
    assert absorption_factor(1e-12) == pytest.approx(1.0)


def test_thick_foil_tends_to_one_over_x():
    """f(X) -> 1/X for large X: only those born near the exit surface escape, so the escaping
    FRACTION falls as 1/thickness rather than exponentially."""
    for x in (50.0, 200.0):
        assert absorption_factor(x) == pytest.approx(1.0 / x, rel=1e-6)


def test_absorption_factor_is_continuous_across_the_series_switch():
    """The small-X branch uses a series expansion; it must join the closed form smoothly."""
    below, above = absorption_factor(9.9e-9), absorption_factor(1.01e-8)
    assert below == pytest.approx(above, rel=1e-6)


def test_factor_decreases_with_x():
    values = [absorption_factor(x) for x in (0.1, 1.0, 10.0, 100.0)]
    assert values == sorted(values, reverse=True)


# ---- the fitter recovers parameters it generated ----

def test_fit_recovers_known_parameters():
    A, chi_hard, chi_soft = 1.32, 1.1e-4, 2.8e-3
    ratios = [ratio_model(t, A, chi_hard, chi_soft) for t in _THICKNESSES]
    fit = fit_ratio_curve(_THICKNESSES, ratios)

    assert fit["r_squared"] == pytest.approx(1.0, abs=1e-9)
    assert fit["amplitude"] == pytest.approx(A, rel=0.02)
    assert fit["chi_hard"] == pytest.approx(chi_hard, rel=0.15)
    assert fit["chi_soft"] == pytest.approx(chi_soft, rel=0.15)


def test_fit_is_deterministic():
    """Grid refinement, no random starts -- the same input must give the same answer."""
    ratios = [ratio_model(t, 1.3, 1e-4, 3e-3) for t in _THICKNESSES]
    assert fit_ratio_curve(_THICKNESSES, ratios) == fit_ratio_curve(_THICKNESSES, ratios)


def test_too_few_points_raises():
    with pytest.raises(ValueError, match="at least 3 points"):
        fit_ratio_curve([1.0, 2.0], [1.0, 2.0])


# ---- the model comparison: the point Walther's question turns on ----

def test_absorption_beats_exponential_on_data_that_flattens():
    """Generated from the absorption form, so the exponential MUST fit worse. This is the
    measurement behind 'the exponential is the wrong model' -- without it that is an opinion."""
    ratios = [ratio_model(t, 1.11, 1.8e-4, 5.1e-3) for t in _THICKNESSES]
    scores = compare_models(_THICKNESSES, ratios)
    assert scores["absorption"] > scores["exponential"]
    assert scores["absorption"] == pytest.approx(1.0, abs=1e-9)


def test_exponential_wins_on_genuinely_exponential_data():
    """The comparison must not be rigged: given real exponential data, the exponential wins."""
    ratios = [1.2 * math.exp(1.5e-3 * t) for t in _THICKNESSES]
    scores = compare_models(_THICKNESSES, ratios)
    assert scores["exponential"] == pytest.approx(1.0, abs=1e-9)
    assert scores["exponential"] >= scores["absorption"]


# ---- crossings ----

def test_crossing_is_where_the_two_models_are_equal():
    a = {"amplitude": 1.32, "chi_hard": 1.1e-4, "chi_soft": 2.8e-3}
    b = {"amplitude": 1.11, "chi_hard": 1.8e-4, "chi_soft": 5.1e-3}
    where = crossing(a, b)
    assert ratio_model(where, **a) == pytest.approx(ratio_model(where, **b), rel=1e-6)


def test_non_crossing_curves_raise():
    """Two identical-shaped curves at different amplitudes never meet -- must not return a
    silently wrong midpoint."""
    a = {"amplitude": 2.0, "chi_hard": 1e-4, "chi_soft": 3e-3}
    b = {"amplitude": 1.0, "chi_hard": 1e-4, "chi_soft": 3e-3}
    with pytest.raises(ValueError, match="do not cross"):
        crossing(a, b)


def test_crossing_table_covers_all_three_pairs():
    table = crossing_table(_ratio_frame(_TRUTH))
    assert len(table) == 3
    assert set(zip(table["curve_a"], table["curve_b"])) == {
        ("Ga_K_L", "As_K_L"), ("Ga_K_L", "Bi_L_M"), ("As_K_L", "Bi_L_M")}
    assert (table["crossing_nm"] > 0).all()


# ---- wiring ----

def test_fit_diagnostics_reports_all_three_models_per_curve():
    out = fit_diagnostics(_ratio_frame(_TRUTH))
    assert set(out["curve"]) == set(_TRUTH)
    assert (out["r2_absorption"] >= out["r2_exponential"]).all()
    assert (out["r2_absorption"] > 0.999).all()


def test_missing_composition_arm_raises():
    with pytest.raises(ValueError, match="no runs at x_bi"):
        fit_diagnostics(_ratio_frame(_TRUTH), x_bi=0.99)


def test_write_absorption_analysis_round_trips(tmp_path):
    ratios_csv = tmp_path / "diagnostic_ratios.csv"
    _ratio_frame(_TRUTH).to_csv(ratios_csv, index=False)
    out = write_absorption_analysis(ratios_csv, tmp_path / "Aggregated")
    assert out.name == "absorption_fits_and_crossings.csv"

    written = pd.read_csv(out)
    assert set(written["kind"]) == {"fit", "crossing"}
    assert len(written[written["kind"] == "crossing"]) == 3
