"""P1.3 -- counting statistics. Acceptance tests.

The propagation is numerical (a central difference through the real recovery), so the load-bearing
tests are the ones that check it against CLOSED-FORM derivatives that can be written down by hand.
Walther's Eqs 2, 4 and 9 each give an exact log-derivative of recovered x with respect to the line
being perturbed, and all three are asserted below. If the numerical differentiation were wrong,
those would not agree to six figures.

The rest check the structure: that noise cannot reach a route it has no path to, that it CAN reach
one through the thickness proxy, that sigma falls as 1/sqrt(dose), and that the answer agrees with
the counting floor `overlap.py` computes by a completely different method.

Runs against the real aggregated table -- a hermetic fixture would need a full 21-run matrix to
mean anything -- and skips cleanly if it is absent.
"""

from __future__ import annotations

import math
from pathlib import Path

import pandas as pd
import pytest

from mcxray_wrapper import overlap
from mcxray_wrapper.counting import (
    DOSE_SCALES,
    FIRST_ORDER_LIMIT,
    WALTHER_DOSE_SCALE,
    counting_uncertainty,
    dose_for_target,
    line_sensitivities,
    summarise_by_route,
    unknown_run_ids,
    write_counting,
)
from mcxray_wrapper.kfactors import calibration_curves
from mcxray_wrapper.roundtrip import recover_x_via_kl
from mcxray_wrapper.spec import AS, BI, GA

COMBINED = Path(r"C:\MCXRAY\Sim\Aggregated\combined_intensities.csv")

_KEY = ["run_id", "route", "heavy_shell", "light_shell", "definition"]


@pytest.fixture(scope="module")
def combined():
    if not COMBINED.is_file():
        pytest.skip("aggregated table not present")
    return pd.read_csv(COMBINED)


@pytest.fixture(scope="module")
def sensitivities(combined):
    return line_sensitivities(combined)


@pytest.fixture(scope="module")
def recovered(combined):
    return recover_x_via_kl(combined).set_index(_KEY)["recovered_x"]


@pytest.fixture(scope="module")
def uncertainty(combined):
    return counting_uncertainty(combined)


def _select(frame, **columns):
    mask = pd.Series(True, index=frame.index)
    for name, value in columns.items():
        mask &= frame[name] == value
    return frame[mask]


# ---- the numerical derivative against closed form -------------------------------------------
#
# Each route's inverse formula gives d(x)/d(ln I) exactly, provided the perturbed line does not
# also sit in the As K/L thickness proxy. Bi La and Ga Ka1 do not, so these three are clean.

def test_bi_ga_sensitivity_equals_x(sensitivities, recovered):
    """Eq 2 inverted gives x proportional to I_Bi, so d x / d ln I(Bi La) = x exactly."""
    rows = _select(sensitivities, route="Bi_Ga", heavy_shell="L", definition="principal",
                   atomic_number=BI, line="La")
    assert len(rows) == 10  # 5 Set B runs x 2 light shells
    for row in rows.itertuples():
        x = recovered.loc[(row.run_id, row.route, row.heavy_shell,
                           row.light_shell, row.definition)]
        assert row.sensitivity == pytest.approx(x, rel=1e-5)


def test_bi_as_sensitivity_equals_x_times_one_minus_x(sensitivities, recovered):
    """Eq 4 inverted gives x = y/(1+y) with y proportional to I_Bi, so the derivative is x(1-x)
    -- a different functional form from Eq 2, and the numerical difference must find it."""
    rows = _select(sensitivities, route="Bi_As", heavy_shell="L", definition="principal",
                   atomic_number=BI, line="La")
    assert len(rows) == 10
    for row in rows.itertuples():
        x = recovered.loc[(row.run_id, row.route, row.heavy_shell,
                           row.light_shell, row.definition)]
        assert row.sensitivity == pytest.approx(x * (1.0 - x), rel=1e-5)


def test_ga_as_sensitivity_equals_one_minus_x(sensitivities, recovered):
    """Eq 9 inverted gives x = 1 - u with u proportional to I_As/I_Ga, so d x / d ln I(Ga) = 1-x.

    This is the route's fatal weakness stated as a derivative: near x = 0 the sensitivity tends to
    1 while x itself tends to 0, so the RELATIVE error diverges. It is why Ga_As is the worst
    route at low Bi content, and it falls out of the algebra rather than being asserted.
    """
    rows = _select(sensitivities, route="Ga_As", heavy_shell="K", definition="principal",
                   atomic_number=GA, line="Ka1")
    assert len(rows) == 10
    for row in rows.itertuples():
        x = recovered.loc[(row.run_id, row.route, row.heavy_shell,
                           row.light_shell, row.definition)]
        assert row.sensitivity == pytest.approx(1.0 - x, rel=1e-5)


# ---- which lines can reach which routes ------------------------------------------------------

def test_unreachable_line_has_exactly_zero_sensitivity(sensitivities):
    """Under the principal definition a Bi_Ga L/K estimate uses Bi La and Ga Ka1 only, and Bi Lb1
    is in neither those nor the As K/L proxy. Noise on it must be unable to move the answer by
    ANY path -- exactly zero, not merely small."""
    rows = _select(sensitivities, route="Bi_Ga", heavy_shell="L", light_shell="K",
                   definition="principal", atomic_number=BI, line="Lb1")
    assert len(rows) == 5
    assert (rows["sensitivity"] == 0.0).all()


def test_thickness_proxy_opens_an_indirect_path(sensitivities):
    """A Bi_Ga estimate uses no arsenic line at all, yet noise on As La must still reach it: the
    As K/L ratio is the thickness proxy, so it selects which k* is used.

    This is the counting-statistics analogue of the indirect hit the sum peak opens through
    parent depletion, and it is the reason the propagation differentiates the whole chain instead
    of applying a two-line formula.
    """
    rows = _select(sensitivities, route="Bi_Ga", heavy_shell="L", light_shell="K",
                   definition="principal", atomic_number=AS, line="La")
    assert len(rows) == 5
    assert (rows["sensitivity"].abs() > 0).all()

    # Indirect, so it must stay far below the direct term (which equals x).
    direct = _select(sensitivities, route="Bi_Ga", heavy_shell="L", light_shell="K",
                     definition="principal", atomic_number=BI, line="La")
    pairs = rows.set_index("run_id")["sensitivity"].abs() / \
        direct.set_index("run_id")["sensitivity"].abs()
    assert (pairs < 0.05).all()


def test_noise_is_never_applied_to_the_calibration(combined):
    """The unknowns and the Set A calibration must be disjoint sets of runs. If they overlapped,
    noise would move calibration and unknown together and partly cancel -- the same failure the
    sum-peak propagation hit on 15 Aug (REPORT 26.6)."""
    unknowns = unknown_run_ids(combined)
    calibration = set(calibration_curves(combined)["run_id"])
    assert unknowns
    assert calibration
    assert not (unknowns & calibration)


# ---- dose ------------------------------------------------------------------------------------

def test_sigma_falls_as_one_over_root_dose(uncertainty):
    """Poisson's defining behaviour. If this failed, every dose statement in the write-up would
    be wrong."""
    low, high = min(DOSE_SCALES), max(DOSE_SCALES)
    index = _KEY
    a = uncertainty[uncertainty["dose_scale"] == low].set_index(index)["sigma_x"]
    b = uncertainty[uncertainty["dose_scale"] == high].set_index(index)["sigma_x"]
    expected = a / math.sqrt(high / low)
    assert list(b.reindex(a.index)) == pytest.approx(list(expected), rel=1e-12)


def test_dose_for_target_inverts_the_scaling(uncertainty):
    out = dose_for_target(uncertainty, target_relative=0.10)
    # A route already at the target needs no more dose than it already has.
    met = out[out["already_met"]]
    assert len(met)
    assert (met["dose_needed"] <= met["dose_scale"] * (1.0 + 1e-9)).all()
    # And counting for dose_needed would land exactly on the target.
    achieved = out["relative_sigma"] / (out["dose_needed"] / out["dose_scale"]) ** 0.5
    assert list(achieved) == pytest.approx([0.10] * len(out), rel=1e-9)


def test_dose_for_target_rejects_a_nonsense_target(uncertainty):
    with pytest.raises(ValueError):
        dose_for_target(uncertainty, target_relative=0.0)


# ---- agreement with the other module that counts photons -------------------------------------

def test_agrees_with_the_overlap_modules_counting_floor(combined, uncertainty):
    """`overlap.py` computes the Bi La counting floor directly as 1/sqrt(N). This module reaches
    the same number by differentiating the entire recovery chain. They share no code path, so
    agreement is a real cross-check rather than a tautology.

    The two routes bracket the floor, for a reason worth recording:

      Bi_Ga -- Eq 2 gives d x / d ln I(Bi La) = x exactly, so Bi La's contribution to the
        RELATIVE error is exactly 1/sqrt(N), i.e. the floor itself. Adding Ga Ka1 and the
        thickness proxy can only push it up, so this route must land strictly ABOVE.

      Bi_As -- Eq 4 gives x(1-x) instead, so Bi La contributes (1-x)/sqrt(N). At x = 0.01 that
        is a 1% damping, and it is very slightly more than the other lines add back. The route
        therefore sits marginally BELOW the naive floor -- not an error, but the algebra of the
        inversion very slightly working in its favour.
    """
    floor = overlap.bi_la_uncertainty(combined, couplings=(0.0,),
                                      dose_scale=WALTHER_DOSE_SCALE)
    # x = 0.01 alone is not unique -- Set C is a whole x = 0.01 thickness arm. The unknown is the
    # 100 nm run, so both coordinates are needed to pick it out.
    floor = floor[(floor["x_bi"] == 0.01) & (floor["thickness_nm"] == 100)]
    assert len(floor) == 1
    expected = float(floor["counting_only_relative"].iloc[0])

    at_low_x = uncertainty[(uncertainty["dose_scale"] == WALTHER_DOSE_SCALE)
                           & (uncertainty["true_x_bi"] == 0.01)
                           & (uncertainty["heavy_shell"] == "L")
                           & (uncertainty["light_shell"] == "K")
                           & (uncertainty["definition"] == "principal")]

    def relative(route):
        rows = at_low_x[at_low_x["route"] == route]
        assert len(rows) == 1
        return float(rows["relative_sigma"].iloc[0])

    bi_ga, bi_as = relative("Bi_Ga"), relative("Bi_As")

    assert bi_ga > expected                              # floor plus the other lines
    assert bi_as < expected                              # the (1-x) damping wins, just
    assert bi_as > 0.99 * expected                       # but only just -- (1-x) = 0.99
    for measured in (bi_ga, bi_as):
        assert measured == pytest.approx(expected, rel=0.05)


def test_dose_scale_matches_the_overlap_module(combined):
    """Two modules quoting Walther's acquisition must quote the same number."""
    assert WALTHER_DOSE_SCALE == overlap.WALTHER_DOSE_SCALE


# ---- the findings the write-up will quote ----------------------------------------------------

def test_bi_l_routes_are_the_best_in_the_matrix_at_low_x(uncertainty):
    """The headline ranking, stated as an ordering rather than a magnitude.

    At x = 0.01 and Walther's dose every Bi L route beats every other route in the matrix
    outright -- the worst Bi L estimate is better than the best non-Bi-L one. That is a stronger
    and more durable claim than any single percentage, and it is the counting-statistics half of
    the case for recommending a Bi L pair.
    """
    at_low_x = uncertainty[(uncertainty["dose_scale"] == WALTHER_DOSE_SCALE)
                           & (uncertainty["true_x_bi"] == 0.01)
                           & (uncertainty["definition"] == "principal")]
    is_bi_l = at_low_x["route"].str.startswith("Bi") & (at_low_x["heavy_shell"] == "L")
    bi_l, others = at_low_x[is_bi_l], at_low_x[~is_bi_l]

    assert len(bi_l) == 4 and len(others) == 12
    assert bi_l["relative_sigma"].max() < others["relative_sigma"].min()
    assert bi_l["relative_sigma"].max() < 0.04
    assert bi_l["first_order_valid"].all()


def test_the_weak_line_routes_break_the_first_order_limit_at_low_x(uncertainty):
    """Every Bi K route, and the Ga_As pairings resting on As Ka1, exceed the limit at x = 0.01.

    Both failures are photon starvation, but they arrive by different routes and it is worth
    keeping them apart: Bi K because the line itself is faint, and Ga_As because its sensitivity
    tends to 1 while x tends to 0, so even a well-counted ratio gives a large RELATIVE error on a
    small x. The second is a property of Eq 9's algebra, not of the spectrum.
    """
    at_low_x = uncertainty[(uncertainty["dose_scale"] == WALTHER_DOSE_SCALE)
                           & (uncertainty["true_x_bi"] == 0.01)
                           & (uncertainty["definition"] == "principal")]

    bi_k = at_low_x[at_low_x["route"].str.startswith("Bi")
                    & (at_low_x["heavy_shell"] == "K")]
    assert len(bi_k) == 4
    assert not bi_k["first_order_valid"].any()

    ga_as = at_low_x[at_low_x["route"] == "Ga_As"]
    # Even its best pairing is several times worse than any Bi L route.
    best_bi_l = at_low_x[at_low_x["route"].str.startswith("Bi")
                         & (at_low_x["heavy_shell"] == "L")]["relative_sigma"].min()
    assert ga_as["relative_sigma"].min() > 2.5 * best_bi_l


def test_dose_separates_the_usable_routes_from_the_starved_ones(uncertainty):
    """Reaching 10% on x at x = 0.01: a Bi L route is already there at a fraction of Walther's
    count time, while a Bi K route needs more than ten times it. That is LO3's negative result
    turned into a number an experimenter can act on."""
    out = dose_for_target(uncertainty, target_relative=0.10)
    out = out[(out["dose_scale"] == WALTHER_DOSE_SCALE) & (out["true_x_bi"] == 0.01)
              & (out["definition"] == "principal") & (out["route"].str.startswith("Bi"))]

    bi_l = out[out["heavy_shell"] == "L"]
    bi_k = out[out["heavy_shell"] == "K"]
    assert bi_l["already_met"].all()
    assert bi_l["dose_vs_walther"].max() < 0.2
    assert not bi_k["already_met"].any()
    assert bi_k["dose_vs_walther"].min() > 10.0


def test_counting_noise_is_worse_at_low_bi_content(uncertainty):
    """Relative precision must degrade monotonically as Bi runs out -- fewer Bi photons, same
    everything else. Checked on the recommended route so the write-up can quote the trend."""
    rows = uncertainty[(uncertainty["dose_scale"] == WALTHER_DOSE_SCALE)
                       & (uncertainty["route"] == "Bi_As")
                       & (uncertainty["heavy_shell"] == "L")
                       & (uncertainty["light_shell"] == "K")
                       & (uncertainty["definition"] == "principal")].sort_values("true_x_bi")
    assert len(rows) == 5
    assert list(rows["relative_sigma"]) == sorted(rows["relative_sigma"], reverse=True)


def test_bi_k_routes_are_dominated_by_the_bi_k_line(uncertainty):
    """LO3's negative result, expressed as a variance share: Bi K fails on photon count, and the
    Bi Ka1 line itself is essentially the entire error budget."""
    rows = uncertainty[(uncertainty["route"].str.startswith("Bi"))
                       & (uncertainty["heavy_shell"] == "K")
                       & (uncertainty["definition"] == "principal")]
    assert len(rows)
    assert (rows["dominant_line"] == f"{BI} Ka1").all()
    assert (rows["dominant_share"] > 0.9).all()


def test_first_order_flag_is_reported_not_silently_applied(uncertainty):
    """A relative sigma above the limit must be present in the table AND flagged, never dropped
    -- the reader decides what to do with an out-of-range number."""
    assert not uncertainty["first_order_valid"].all()
    invalid = uncertainty[~uncertainty["first_order_valid"]]
    assert (invalid["relative_sigma"] > FIRST_ORDER_LIMIT).all()
    valid = uncertainty[uncertainty["first_order_valid"]]
    assert (valid["relative_sigma"] <= FIRST_ORDER_LIMIT).all()


# ---- bookkeeping -----------------------------------------------------------------------------

def test_every_row_carries_its_dose(uncertainty):
    assert set(uncertainty["dose_scale"]) == set(DOSE_SCALES)
    assert uncertainty["dose_scale"].notna().all()


def test_summary_keeps_composition_on_the_rows(uncertainty):
    """Averaging over x would destroy the result, which is that the limit depends on x."""
    out = summarise_by_route(uncertainty)
    assert "true_x_bi" in out.columns
    assert set(out["true_x_bi"]) == set(uncertainty["true_x_bi"])
    assert (out["worst_relative_sigma"] >= out["mean_relative_sigma"]).all()
    assert (out["mean_relative_sigma"] >= out["best_relative_sigma"]).all()


def test_write_counting_produces_all_three_files(combined, tmp_path):
    written = write_counting(COMBINED, tmp_path / "Aggregated")
    assert set(written) == {"counting_line_sensitivities", "counting_uncertainty",
                            "counting_by_route"}
    for path in written.values():
        assert path.is_file() and len(pd.read_csv(path)) > 0
