"""The analysis driver. Structural tests -- they guard two failures that already happened.

1. A module gains a `write_*` function and nobody wires it into the driver, so its output is
   never generated. `sumpeak_sensitivity.csv` sat in WORKPLAN_17AUG.md 3.5 as an existing file
   for two days while not being in Aggregated\\ at all.

2. A stage inherits a function default that disagrees with the reporting basis the write-up
   quotes. `write_overlap_bound` defaults to dose_scale=1.0; REPORT 27's bound is on Walther's
   715.5 s acquisition. Running the driver regenerated the file nine times noisier with every
   column heading and row count unchanged.

Neither shows up as a crash, a wrong shape, or a failing assertion anywhere else, which is
exactly why they are tested here.
"""

from __future__ import annotations

import importlib
import inspect
import pkgutil
from pathlib import Path

import pandas as pd
import pytest

import mcxray_wrapper
import run_analysis
from mcxray_wrapper.counting import WALTHER_DOSE_SCALE

AGGREGATED = Path(r"C:\MCXRAY\Sim\Aggregated")


def test_every_write_function_is_wired_into_a_stage():
    """A `write_*` function that no stage calls produces a file that never gets regenerated."""
    source = Path(run_analysis.__file__).read_text(encoding="utf-8")

    missing = []
    for info in pkgutil.iter_modules(mcxray_wrapper.__path__):
        module = importlib.import_module(f"mcxray_wrapper.{info.name}")
        for name, obj in vars(module).items():
            if not name.startswith("write_") or not inspect.isfunction(obj):
                continue
            if obj.__module__ != module.__name__:
                continue  # imported into this namespace, defined elsewhere
            if f"{name}(" not in source:
                missing.append(f"{info.name}.{name}")

    assert not missing, f"not called by run_analysis.py: {sorted(missing)}"


def test_stage_names_are_unique():
    assert len(run_analysis.STAGE_NAMES) == len(set(run_analysis.STAGE_NAMES))


def test_stages_are_declared_in_dependency_order():
    """A stage may only read a file an EARLIER stage produced. Declaration order is execution
    order, so if this holds the driver can never read a stale table."""
    produced = set()
    for name, needs, _ in run_analysis.STAGES:
        if name == "aggregate":
            produced.add(run_analysis.COMBINED)
            continue
        assert needs in produced, f"stage {name!r} reads {needs!r} before anything writes it"
        if name == "ratios":
            produced.add(run_analysis.RATIOS)


def test_overlap_stage_states_its_dose_rather_than_inheriting_one():
    """The one place a silent default changed a published number. The call must name the dose."""
    source = Path(run_analysis.__file__).read_text(encoding="utf-8")
    assert "write_overlap_bound(" in source
    call = source.split("write_overlap_bound(", 1)[1].split(")", 1)[0]
    assert "dose_scale" in call, "the overlap stage must pass dose_scale explicitly"


@pytest.mark.skipif(not (AGGREGATED / "overlap_i_bound.csv").is_file(),
                    reason="aggregated outputs not present")
def test_stored_overlap_bound_is_on_walthers_dose():
    """The file on disk, not just the call that writes it -- this is what the write-up quotes."""
    stored = pd.read_csv(AGGREGATED / "overlap_i_bound.csv")
    assert list(stored["dose_scale"].unique()) == [pytest.approx(WALTHER_DOSE_SCALE)]


def test_list_runs_without_touching_anything(capsys):
    assert run_analysis.main(["--list"]) == 0
    printed = capsys.readouterr().out
    for name in run_analysis.STAGE_NAMES:
        assert name in printed


def test_only_accepts_known_stages_and_rejects_others():
    with pytest.raises(SystemExit):
        run_analysis.main(["--only", "not-a-stage"])
