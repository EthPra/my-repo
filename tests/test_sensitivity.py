"""P4.1 -- the swept as-measured round trip. Acceptance tests.

Runs on the REAL aggregated table where a hermetic fixture would need a full 21-run matrix to be
meaningful; skips cleanly if it is absent. The magnitudes are swept assumptions, so nothing here
pins one -- what is pinned is the structure: the grid is complete, the baseline anchors to the
clean recovery, and the artefact reaches the routes it should and no others.
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

from mcxray_wrapper.roundtrip import recover_x_via_kl
from mcxray_wrapper.sensitivity import (
    SWITCH_GRID,
    summarise_by_route,
    sweep,
    switch_influence,
    write_sensitivity,
)

COMBINED = Path(r"C:\MCXRAY\Sim\Aggregated\combined_intensities.csv")


@pytest.fixture(scope="module")
def combined():
    if not COMBINED.is_file():
        pytest.skip("aggregated table not present")
    return pd.read_csv(COMBINED)


@pytest.fixture(scope="module")
def swept(combined):
    return sweep(combined, levels=(0.01, 0.10))


# ---- the grid is complete and self-describing ----

def test_every_switch_combination_is_present(swept):
    corrupted = swept[swept["level"] > 0]
    combos = corrupted.groupby(list(SWITCH_GRID)).ngroups
    expected = 1
    for values in SWITCH_GRID.values():
        expected *= len(values)
    assert combos == expected == 16


def test_every_row_carries_its_settings(swept):
    """A recovered number must never be separable from the assumptions that produced it."""
    for column in (*SWITCH_GRID, "level"):
        assert column in swept.columns
        assert swept[column].notna().all()


# ---- the baseline anchors the rest of the table ----

def test_zero_level_reproduces_the_clean_recovery(combined, swept):
    """If the no-artefact row did not match the ordinary recovery, every comparison drawn
    against it would be meaningless."""
    baseline = swept[swept["level"] == 0].sort_values(
        ["run_id", "route", "heavy_shell", "light_shell", "definition"])
    clean = recover_x_via_kl(combined).sort_values(
        ["run_id", "route", "heavy_shell", "light_shell", "definition"])
    assert list(baseline["recovered_x"]) == pytest.approx(list(clean["recovered_x"]))


# ---- the artefact reaches the right routes and no others ----

def test_bi_l_routes_are_reached_only_through_the_thickness_proxy(swept):
    """Bi La sits at 10.84 keV and the artefact lands at 2.4 keV, so the DIRECT hit cannot touch
    it -- and with conserve=False the recovered x is bit-identical to the clean baseline.

    With conserve=True it does move, and the only available path is the indirect one: depleting
    As L shifts the As K/L thickness proxy, which selects a different k*. That the shift is
    exactly zero without conservation and non-zero with it is what proves the mechanism, rather
    than some other leak.
    """
    bi_l = swept[swept["bi_line"] == "Bi L"]
    index = ["run_id", "route", "heavy_shell", "light_shell", "definition"]
    baseline = bi_l[bi_l["level"] == 0].set_index(index)["recovered_x"]

    def max_shift(level, conserve):
        rows = bi_l[(bi_l["level"] == level) & (bi_l["conserve"] == conserve)]
        aligned = rows.set_index(index)["recovered_x"]
        return (aligned - baseline.reindex(aligned.index)).abs().max()

    levels = sorted(l for l in bi_l["level"].unique() if l > 0)
    for level in levels:
        assert max_shift(level, False) == pytest.approx(0.0, abs=1e-12),             "no parent depletion means no route from the artefact to Bi L at all"
        assert max_shift(level, True) > 0, "conservation must open the indirect path"

    # indirect only, so small -- and it must grow with the level that drives the depletion
    shifts = [max_shift(level, True) for level in levels]
    assert shifts == sorted(shifts)
    assert max(shifts) < 0.01


def test_bi_m_routes_are_damaged_and_worsen_with_level(swept):
    bi_m = swept[swept["bi_line"] == "Bi M"]
    by_level = bi_m.groupby("level")["abs_error"].mean()
    assert list(by_level) == sorted(by_level), "damage must grow with the pile-up level"
    assert by_level.iloc[-1] > 10 * by_level.iloc[0]


def test_bi_m_is_hurt_far_more_than_bi_l(swept):
    """The headline structural result: the artefact discriminates between routes."""
    worst = swept[swept["level"] == swept["level"].max()]
    bi_m = worst[worst["bi_line"] == "Bi M"]["abs_error"].mean()
    bi_l = worst[worst["bi_line"] == "Bi L"]["abs_error"].mean()
    assert bi_m > 10 * bi_l


# ---- summaries ----

def test_summary_reports_the_spread_across_switches(swept):
    """Averaging over the switch grid is only honest if the spread is reported beside it."""
    out = summarise_by_route(swept)
    for column in ("mean_abs_error", "worst_abs_error", "best_abs_error", "switch_spread"):
        assert column in out.columns
    assert (out["switch_spread"] >= 0).all()
    assert (out["worst_abs_error"] >= out["mean_abs_error"]).all()


def test_switch_influence_covers_every_switch(swept):
    out = switch_influence(swept)
    assert set(out["switch"]) == set(SWITCH_GRID)
    assert (out["difference"] >= 0).all()
    # sorted most-influential first, so the write-up can quote the top row
    assert list(out["difference"]) == sorted(out["difference"], reverse=True)


def test_write_sensitivity_produces_all_three_files(combined, tmp_path):
    written = write_sensitivity(COMBINED, tmp_path / "Aggregated", levels=(0.01,))
    assert set(written) == {"sumpeak_roundtrip_sweep", "sumpeak_roundtrip_by_route",
                            "sumpeak_switch_influence"}
    for path in written.values():
        assert path.is_file() and len(pd.read_csv(path)) > 0
