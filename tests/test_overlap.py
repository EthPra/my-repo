"""Overlap (i) bound -- acceptance tests.

The coupling between the two peaks is a SWEPT assumption, so these tests pin no physical
magnitude for it. What they do pin is the resolution model, which is not swept and is doing real
work: it is the basis for the claim that the two overlaps are different kinds of problem.

Two of these tests are validations rather than unit tests -- they check the model reproduces
facts this project already holds from independent sources.
"""

from __future__ import annotations

import math

import pandas as pd
import pytest

from mcxray_wrapper.overlap import (
    COUPLING_LEVELS,
    MN_KA_EV,
    WALTHER_DOSE_SCALE,
    area_uncertainty,
    bi_la_uncertainty,
    neighbours,
    resolution_fwhm_ev,
    separation_in_fwhm,
    write_overlap_bound,
)
from mcxray_wrapper.ratios import INTENSITY_COLUMN
from mcxray_wrapper.spec import AS, BI, GA

_SYMBOL = {GA: "Ga", AS: "As", BI: "Bi"}


def _row(run_id, x_bi, z, line, energy_kev, intensity):
    return {
        "run_id": run_id, "x_bi": x_bi, "thickness_nm": 100,
        "Atomic number": z, "Element": _SYMBOL[z], "Line": f"Line {line}",
        "Line energy (keV)": energy_kev, INTENSITY_COLUMN: intensity,
    }


def _run(run_id="r", x_bi=0.01, bi_la=116.0, as_ka1=9952.0):
    return pd.DataFrame([
        _row(run_id, x_bi, BI, "La", 10.840, bi_la),
        _row(run_id, x_bi, BI, "Ma", 2.423, 76.0),
        _row(run_id, x_bi, AS, "Ka1", 10.543, as_ka1),
        _row(run_id, x_bi, AS, "Ka2", 10.507, as_ka1 * 0.5),
        _row(run_id, x_bi, GA, "Ka1", 9.251, 8000.0),
    ])


# ---- the resolution model: validated against facts held independently ----

def test_resolution_reproduces_the_si_li_specification():
    """~130 eV at Mn Ka is the textbook figure a Si(Li) detector is specified at. The model is
    not fitted to this project's data, so matching it is a genuine check."""
    assert resolution_fwhm_ev(MN_KA_EV) == pytest.approx(130.0, abs=6.0)


def test_resolution_reproduces_walthers_bi_la1_la2_statement():
    """Walther, independently: Bi La1 (10839 eV) and La2 (10731 eV) are 'usually
    indistinguishable'. The model must agree, or it is not describing this detector."""
    assert separation_in_fwhm(10839.0, 10731.0) < 1.0   # merged


def test_resolution_worsens_with_energy():
    assert resolution_fwhm_ev(2423.0) < resolution_fwhm_ev(10840.0)


def test_the_two_overlaps_are_different_kinds_of_problem():
    """The finding this module exists to establish, asserted directly."""
    sum_peak = separation_in_fwhm(2380.0, 2423.0)       # Ga La + As La vs Bi Ma
    overlap_i = separation_in_fwhm(10543.0, 10840.0)    # As Ka1 vs Bi La

    assert sum_peak < 0.6, "sum peak must come out merged"
    assert overlap_i > 1.5, "overlap (i) must come out resolvable"
    assert overlap_i > 3 * sum_peak


# ---- which lines actually sit in the window ----

def test_neighbours_finds_the_as_ka_lines_and_reads_energies_from_the_table():
    found = neighbours(_run())
    assert set(zip(found["element"], found["line"])) == {("As", "Ka1"), ("As", "Ka2")}
    assert (found["resolved"]).all()          # both are separable, not merged
    assert found["separation_fwhm"].min() > 1.5


def test_distant_lines_are_excluded():
    """Ga Ka1 at 9.251 keV is ~1.6 keV away -- nowhere near, and must not be counted."""
    found = neighbours(_run())
    assert "Ga" not in set(found["element"])


def test_missing_target_line_raises():
    df = _run()
    with pytest.raises(ValueError, match="not in the table"):
        neighbours(df[df["Line"] != "Line La"])


# ---- the uncertainty arithmetic ----

def test_zero_coupling_is_pure_counting_statistics():
    """The honest floor: even a perfectly isolated peak carries sqrt(N)."""
    assert area_uncertainty(10000.0, 1e6, 0.0) == pytest.approx(100.0)


def test_coupling_adds_the_neighbour_in_quadrature():
    assert area_uncertainty(100.0, 10000.0, 0.01) == pytest.approx(math.sqrt(100 + 100))


def test_uncertainty_grows_with_coupling():
    out = bi_la_uncertainty(_run(), couplings=COUPLING_LEVELS).sort_values("coupling")
    assert list(out["relative_uncertainty"]) == sorted(out["relative_uncertainty"])


def test_negative_coupling_raises():
    with pytest.raises(ValueError, match="non-negative"):
        area_uncertainty(1.0, 1.0, -0.1)


# ---- what makes low x dangerous ----

def test_low_bi_is_hurt_far_more_than_high_bi():
    """Same neighbour, weaker target -> both a worse counting floor and a worse overlap cost.
    This is the same structural problem as the sum peak, expressed as variance not bias."""
    weak = bi_la_uncertainty(_run(bi_la=116.0), couplings=(0.01,)).iloc[0]
    strong = bi_la_uncertainty(_run(bi_la=2107.0), couplings=(0.01,)).iloc[0]
    assert weak["relative_uncertainty"] > 3 * strong["relative_uncertainty"]
    assert weak["neighbour_ratio"] > strong["neighbour_ratio"]


def test_counting_floor_is_reported_separately():
    """So 'the overlap cost' can be told apart from 'there were simply too few photons'."""
    row = bi_la_uncertainty(_run(), couplings=(0.01,)).iloc[0]
    assert row["counting_only_relative"] < row["relative_uncertainty"]
    assert row["counting_only_relative"] == pytest.approx(1.0 / math.sqrt(row["n_bi_la"]))


def test_dose_scaling_improves_the_statistics_as_sqrt():
    """The stored table is a 100 s acquisition; Walther's is 715.5 s live."""
    base = bi_la_uncertainty(_run(), couplings=(0.0,), dose_scale=1.0).iloc[0]
    scaled = bi_la_uncertainty(_run(), couplings=(0.0,), dose_scale=WALTHER_DOSE_SCALE).iloc[0]
    assert scaled["relative_uncertainty"] == pytest.approx(
        base["relative_uncertainty"] / math.sqrt(WALTHER_DOSE_SCALE))


def test_zero_bi_la_raises():
    with pytest.raises(ValueError, match="no counts"):
        bi_la_uncertainty(_run(bi_la=0.0))


def test_write_overlap_bound_round_trips(tmp_path):
    combined_csv = tmp_path / "combined.csv"
    _run().to_csv(combined_csv, index=False)
    out = write_overlap_bound(combined_csv, tmp_path / "Aggregated", couplings=(0.01,))
    assert out.name == "overlap_i_bound.csv"
    assert len(pd.read_csv(out)) == 1


# ---- the two uncited constants: does the conclusion depend on them? ----

def test_conclusion_holds_across_the_whole_literature_range():
    """eps and F are the only uncited numbers here, so the finding must not rest on the exact
    values chosen. Across every corner of their quoted ranges, As Ka / Bi La stays RESOLVABLE
    and the sum peak stays MERGED. The pending citation therefore bounds a number, not a result.
    """
    from mcxray_wrapper.overlap import MERGE_THRESHOLD_FWHM, resolution_sensitivity

    overlap_i = resolution_sensitivity(10543.0, 10840.0)   # As Ka1 vs Bi La
    sum_peak = resolution_sensitivity(2380.0, 2423.0)      # Ga La + As La vs Bi Ma

    assert overlap_i["resolved"].all(), "overlap (i) must stay resolvable everywhere"
    assert not sum_peak["resolved"].any(), "the sum peak must stay merged everywhere"
    # and they must never come close to swapping character
    assert overlap_i["separation_fwhm"].min() > 1.5
    assert sum_peak["separation_fwhm"].max() < 0.7
    assert overlap_i["separation_fwhm"].min() > 2 * sum_peak["separation_fwhm"].max()


def test_the_constants_would_have_to_be_far_wrong_to_change_the_answer():
    """Quantifies the margin: eps*F would need to roughly double before the two peaks merged.
    Nothing in the literature is near that, which is what makes the pending citation tolerable.
    """
    import math

    from mcxray_wrapper.overlap import (
        DEFAULT_NOISE_EV, ELECTRON_HOLE_PAIR_EV, FANO_FACTOR_SI, MERGE_THRESHOLD_FWHM,
    )

    separation_ev, energy_ev = 297.0, 10690.0
    fwhm_to_merge = separation_ev / MERGE_THRESHOLD_FWHM
    product_to_merge = ((fwhm_to_merge**2 - DEFAULT_NOISE_EV**2)
                        / (2.355**2 * energy_ev))
    in_use = ELECTRON_HOLE_PAIR_EV * FANO_FACTOR_SI

    assert product_to_merge / in_use > 2.0    # measured: ~2.2x


def test_mn_ka_check_also_survives_the_range():
    """The 130 eV validation must not be an artefact of the chosen constants either."""
    from mcxray_wrapper.overlap import (
        ELECTRON_HOLE_PAIR_RANGE_EV, FANO_FACTOR_RANGE, MN_KA_EV, resolution_fwhm_ev,
    )

    values = [resolution_fwhm_ev(MN_KA_EV, electron_hole_pair_ev=e, fano=f)
              for e in ELECTRON_HOLE_PAIR_RANGE_EV for f in FANO_FACTOR_RANGE]
    # a Si(Li) detector is specified somewhere in the 115-140 eV band; every corner lands there
    assert min(values) > 110.0
    assert max(values) < 145.0
