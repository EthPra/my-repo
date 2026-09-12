"""P4.2 -- the error budget and measurability limit. Acceptance tests.

The budget's whole value is that the three mechanisms stay SEPARABLE after being added together.
Most of what follows tests exactly that, by checking that each swept magnitude moves the one term
it is supposed to move and leaves the others bit-identical:

    dose      -> the variances only, never a bias
    level     -> the sum-peak bias only
    coupling  -> the overlap variance only

If any of those leaked, the dominant-mechanism column would be untrustworthy and so would the
recommendation built on it. The interpolation that turns a budget into a limit is tested
hermetically, because a crossing that silently extrapolates would look exactly like a result.

Runs on the real aggregated table and skips cleanly if it is absent.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import pytest

from mcxray_wrapper.budget import (
    DEFAULT_TARGET_RELATIVE,
    _crossing,
    error_budget,
    measurability_limit,
    rank_routes,
    write_budget,
)
from mcxray_wrapper.counting import WALTHER_DOSE_SCALE

COMBINED = Path(r"C:\MCXRAY\Sim\Aggregated\combined_intensities.csv")

_KEY = ["run_id", "route", "heavy_shell", "light_shell", "definition"]
_ROUTE_KEY = ["route", "heavy_shell", "light_shell", "definition"]
_SCENARIO = ["level", "coupling", "dose_scale"]


@pytest.fixture(scope="module")
def combined():
    if not COMBINED.is_file():
        pytest.skip("aggregated table not present")
    return pd.read_csv(COMBINED)


@pytest.fixture(scope="module")
def budget(combined):
    return error_budget(combined)


@pytest.fixture(scope="module")
def limits(budget):
    return measurability_limit(budget, DEFAULT_TARGET_RELATIVE)


# ---- the arithmetic of the combination -------------------------------------------------------

def test_the_terms_add_up_exactly(budget):
    """Variances in quadrature, bias linearly on top. Stated in the docstring, enforced here."""
    expected_sigma = (budget["sigma_counting"] ** 2 + budget["sigma_overlap"] ** 2) ** 0.5
    assert list(budget["sigma_combined"]) == pytest.approx(list(expected_sigma), rel=1e-12)

    expected_total = budget["bias_method"] + budget["bias_sumpeak"] + budget["sigma_combined"]
    assert list(budget["total_error"]) == pytest.approx(list(expected_total), rel=1e-12)


def test_every_term_is_non_negative(budget):
    for column in ("sigma_counting", "sigma_overlap", "bias_method", "bias_sumpeak",
                   "sigma_combined", "total_error"):
        assert (budget[column] >= 0).all(), column


def test_dominant_mechanism_really_is_the_largest_term(budget):
    parts = budget[["sigma_counting", "sigma_overlap", "bias_sumpeak", "bias_method"]]
    renamed = parts.rename(columns={"sigma_counting": "counting", "sigma_overlap": "overlap_i",
                                    "bias_sumpeak": "sum_peak", "bias_method": "method"})
    assert list(renamed.idxmax(axis=1)) == list(budget["dominant_mechanism"])


# ---- each swept magnitude moves exactly one term ---------------------------------------------

def _split(budget, column):
    values = sorted(budget[column].unique())
    index = [c for c in _KEY + ["level", "coupling", "dose_scale"] if c != column]
    low = budget[budget[column] == values[0]].set_index(index)
    high = budget[budget[column] == values[-1]].set_index(index)
    return low, high.reindex(low.index)


def test_dose_moves_the_variances_and_no_bias(budget):
    low, high = _split(budget, "dose_scale")
    for column in ("bias_method", "bias_sumpeak"):
        assert list(high[column]) == pytest.approx(list(low[column]), rel=1e-12), column
    assert (high["sigma_counting"] < low["sigma_counting"]).all()
    # More dose cannot make the overlap term worse; where Bi La is unused both are zero.
    assert (high["sigma_overlap"] <= low["sigma_overlap"] + 1e-15).all()


def test_sumpeak_level_moves_only_the_sumpeak_bias(budget):
    low, high = _split(budget, "level")
    for column in ("sigma_counting", "sigma_overlap", "bias_method"):
        assert list(high[column]) == pytest.approx(list(low[column]), rel=1e-12), column
    assert (high["bias_sumpeak"] >= low["bias_sumpeak"] - 1e-15).all()
    assert (high["bias_sumpeak"] > low["bias_sumpeak"]).any()


def test_overlap_coupling_moves_only_the_overlap_variance(budget):
    low, high = _split(budget, "coupling")
    for column in ("sigma_counting", "bias_method", "bias_sumpeak"):
        assert list(high[column]) == pytest.approx(list(low[column]), rel=1e-12), column
    assert (high["sigma_overlap"] >= low["sigma_overlap"] - 1e-15).all()
    assert (high["sigma_overlap"] > low["sigma_overlap"]).any()


# ---- a mechanism must not reach a route it has no path to ------------------------------------

def test_overlap_cannot_touch_a_route_that_does_not_use_bi_la(budget):
    """Overlap (i) is As Ka against Bi La. A Bi M or Bi K route never reads Bi La, so its overlap
    term must be exactly zero -- not small. This is the structural claim that lets the module
    rank Bi M above Bi L on this one axis, and it has to be exact to be worth anything."""
    untouched = budget[(budget["definition"] == "principal")
                       & (budget["heavy_shell"] != "L")
                       & (budget["route"].str.startswith("Bi"))]
    assert len(untouched)
    assert (untouched["sigma_overlap"] == 0.0).all()


def test_zero_coupling_removes_the_overlap_term_entirely(combined):
    """The excess is measured ABOVE the counting floor, so at zero coupling it must vanish
    completely -- otherwise the same photons would be charged twice, once as counting statistics
    and once as overlap."""
    small = error_budget(combined, levels=(0.01,), couplings=(0.0, 0.01),
                         dose_scales=(WALTHER_DOSE_SCALE,))
    assert (small[small["coupling"] == 0.0]["sigma_overlap"] == 0.0).all()
    assert (small[small["coupling"] == 0.01]["sigma_overlap"] >= 0).all()
    assert (small[small["coupling"] == 0.01]["sigma_overlap"] > 0).any()


def test_sum_peak_cannot_touch_bi_l_without_photon_conservation(combined):
    """The artefact lands at 2.4 keV and Bi La is at 10.84, so with no parent depletion there is
    no path to a Bi L route at all -- the same mechanism check `test_sensitivity.py` makes, here
    carried through into the budget so the ranking inherits it."""
    small = error_budget(combined, levels=(0.10,), couplings=(0.01,),
                         dose_scales=(WALTHER_DOSE_SCALE,), conserve=False)
    bi_l = small[(small["definition"] == "principal") & (small["heavy_shell"] == "L")
                 & (small["route"].str.startswith("Bi"))]
    assert len(bi_l)
    assert bi_l["bias_sumpeak"].abs().max() < 1e-12

    bi_m = small[(small["definition"] == "principal") & (small["heavy_shell"] == "M")]
    assert (bi_m["bias_sumpeak"] > 0).all()


# ---- the crossing, tested without data -------------------------------------------------------

def test_crossing_finds_a_bracketed_target():
    # A clean power law: error = 0.1 * (x/0.01)^-1, so 10% falls exactly at x = 0.01.
    points = [(0.01, 0.10), (0.10, 0.01)]
    assert _crossing(points, 0.10) == pytest.approx(0.01, rel=1e-9)
    assert _crossing(points, 0.01) == pytest.approx(0.10, rel=1e-9)
    # And a value inside the span lands inside the span.
    middle = _crossing(points, 0.0316227766)
    assert 0.01 < middle < 0.10


def test_crossing_refuses_to_extrapolate():
    """A curve that never reaches the target must return None rather than an extrapolated x.
    Reporting a limit outside the range that was actually simulated would be a fabricated
    number wearing the same column heading as a measured one."""
    always_good = [(0.01, 0.001), (0.10, 0.0001)]
    always_bad = [(0.01, 5.0), (0.10, 2.0)]
    assert _crossing(always_good, 0.10) is None
    assert _crossing(always_bad, 0.10) is None


def test_crossing_handles_a_flat_curve():
    assert _crossing([(0.01, 0.05), (0.10, 0.05)], 0.10) is None


# ---- limits and ranking ----------------------------------------------------------------------

def test_limit_status_matches_the_numbers(limits):
    for row in limits.itertuples():
        if row.status == "below_range":
            assert row.relative_at_lowest_x <= DEFAULT_TARGET_RELATIVE
            assert pd.isna(row.x_limit)
        elif row.status == "above_range":
            assert row.relative_at_lowest_x > DEFAULT_TARGET_RELATIVE
            assert pd.isna(row.x_limit)
        else:
            assert 0.01 <= row.x_limit <= 0.20


def test_best_outcome_sorts_first(limits):
    """`below_range` means measurable everywhere sampled -- the best result available. It has no
    x_limit, so a naive sort on that column would bury it at the bottom."""
    statuses = list(limits["status"])
    assert statuses[0] == "below_range"
    assert statuses.count("below_range") == statuses.index("bracketed")


def test_error_grows_as_bi_runs_out(budget):
    """Every mechanism gets relatively worse at low x. If the total did not, there would be no
    measurability limit to find."""
    key = _KEY[1:] + ["level", "coupling", "dose_scale"]
    for _, group in budget.groupby(key, sort=False):
        ordered = group.sort_values("true_x_bi")
        assert ordered["relative_total"].iloc[0] > ordered["relative_total"].iloc[-1]


def test_a_bi_l_route_is_the_recommendation(limits):
    """LO4's answer. The top-ranked route across the whole 27-scenario grid must be a Bi L pair
    -- Bi M is destroyed by the sum peak, Bi K by photon count, and Ga_As by its own inversion
    residual at low x."""
    ranked = rank_routes(limits)
    best = ranked.iloc[0]
    assert best["route"].startswith("Bi")
    assert best["heavy_shell"] == "L"

    # And it must beat every Bi M and Bi K route, not merely edge them.
    others = ranked[ranked["heavy_shell"].isin(["M", "K"])]
    assert best["fraction_measurable"] > others["fraction_measurable"].max()


def test_bi_m_fails_on_the_sum_peak_and_bi_k_on_photons(limits):
    """The two failures are different and the budget must say which is which -- that distinction
    is most of what the error budget is for."""
    ranked = rank_routes(limits)
    bi_m = ranked[(ranked["heavy_shell"] == "M") & ranked["route"].str.startswith("Bi")]
    bi_k = ranked[(ranked["heavy_shell"] == "K") & ranked["route"].str.startswith("Bi")]
    assert len(bi_m) and len(bi_k)
    assert (bi_m["dominant_mechanism"] == "sum_peak").all()
    assert (bi_k["dominant_mechanism"] == "counting").all()


def test_summed_definition_carries_its_caveat(limits):
    """Under `summed` the overlap term is a lower bound, so a summed route can look better than
    a principal one for a reason that is a modelling gap rather than physics. The flag must
    survive into the ranking, where the comparison is actually made."""
    ranked = rank_routes(limits)
    assert (ranked[ranked["definition"] == "summed"]["overlap_is_lower_bound"]).all()
    assert not (ranked[ranked["definition"] == "principal"]["overlap_is_lower_bound"]).any()


def test_ranking_covers_every_route_once(budget, limits):
    ranked = rank_routes(limits)
    expected = budget.groupby(_KEY[1:]).ngroups
    assert len(ranked) == expected
    assert ranked["n_scenarios"].nunique() == 1


# ---- absolute threshold, anchored to Walther's own stated bar --------------------------------

def test_absolute_mode_defaults_to_relative_and_is_unaffected(budget):
    """Not passing `target_absolute` must reproduce the original relative-only behaviour exactly
    -- this is an additive capability, not a rewrite of the default path."""
    default = measurability_limit(budget, DEFAULT_TARGET_RELATIVE)
    explicit = measurability_limit(budget, DEFAULT_TARGET_RELATIVE, target_absolute=None)
    pd.testing.assert_frame_equal(default, explicit)
    assert (default["metric"] == "relative").all()


def test_absolute_mode_crosses_total_error_not_relative_total(budget):
    """The whole point of an absolute target is that it is measured against a different column.
    Picking one route/scenario and re-deriving the crossing by hand from `total_error` must match
    what `measurability_limit` reports -- otherwise `target_absolute` would silently still be
    reading `relative_total` and the two modes would coincide by accident."""
    absolute_limits = measurability_limit(budget, target_absolute=0.01)
    assert (absolute_limits["metric"] == "absolute").all()
    assert (absolute_limits["target_relative"] == 0.01).all()

    key, group = next(iter(budget.groupby(_ROUTE_KEY + _SCENARIO, sort=False)))
    ordered = group.sort_values("true_x_bi")
    expected = _crossing(list(zip(ordered["true_x_bi"], ordered["total_error"])), 0.01)

    row = absolute_limits[
        (absolute_limits["route"] == key[0]) & (absolute_limits["heavy_shell"] == key[1])
        & (absolute_limits["light_shell"] == key[2]) & (absolute_limits["definition"] == key[3])
        & (absolute_limits["level"] == key[4]) & (absolute_limits["coupling"] == key[5])
        & (absolute_limits["dose_scale"] == key[6])
    ].iloc[0]
    if expected is None:
        assert pd.isna(row["x_limit"])
    else:
        assert row["x_limit"] == pytest.approx(expected)


def test_absolute_and_relative_targets_rank_low_x_routes_differently(budget):
    """A relative target tightens the absolute demand as x shrinks; an absolute one does not. If
    the two metrics never disagreed at low x there would be no decision to make in the first
    place, so this asserts they actually diverge on the real data rather than just trusting the
    docstring's claim."""
    relative = rank_routes(measurability_limit(budget, target_relative=0.10))
    absolute = rank_routes(measurability_limit(budget, target_absolute=0.01))
    merged = relative.merge(absolute, on=_ROUTE_KEY, suffixes=("_rel", "_abs"))
    assert (merged["fraction_measurable_rel"] != merged["fraction_measurable_abs"]).any()


# ---- output ----------------------------------------------------------------------------------

def test_write_budget_default_produces_absolute_primary_plus_relative_reference(combined, tmp_path):
    """Production default (2026-08-21): the un-suffixed files are the ABSOLUTE-threshold ranking
    (Ethan's decision), and the relative-10% version is kept alongside as evidence, not dropped."""
    written = write_budget(COMBINED, tmp_path / "Aggregated",
                           levels=(0.01,), couplings=(0.01,),
                           dose_scales=(WALTHER_DOSE_SCALE,))
    assert set(written) == {
        "error_budget", "measurability_limit", "route_ranking",
        "measurability_limit_relative10", "route_ranking_relative10",
    }
    for path in written.values():
        assert path.is_file() and len(pd.read_csv(path)) > 0

    primary = pd.read_csv(written["measurability_limit"])
    reference = pd.read_csv(written["measurability_limit_relative10"])
    assert (primary["metric"] == "absolute").all()
    assert (reference["metric"] == "relative").all()


def test_write_budget_can_still_produce_just_three_files(combined, tmp_path):
    """`target_absolute=None` restores the original relative-only contract exactly -- callers that
    only want the relative threshold are not forced to carry the reference files."""
    written = write_budget(COMBINED, tmp_path / "Aggregated", target_absolute=None,
                           levels=(0.01,), couplings=(0.01,),
                           dose_scales=(WALTHER_DOSE_SCALE,))
    assert set(written) == {"error_budget", "measurability_limit", "route_ranking"}
    for path in written.values():
        assert path.is_file() and len(pd.read_csv(path)) > 0
