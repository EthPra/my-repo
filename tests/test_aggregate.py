"""Stage 5 acceptance tests.

Hermetic: builds a small run set in tmp_path by generating real inputs and copying the
golden intensity CSV as each run's output, so nothing depends on the mutable Results\
directory or the 15 production runs.
"""

from __future__ import annotations

import json

import pandas as pd
import pytest

from mcxray_wrapper.aggregate import aggregate_runs, resolve_provenance
from mcxray_wrapper.inputgen import generate_inputs
from mcxray_wrapper.matrix import (
    N_ELECTRONS_THICK,
    THIN_CUTOFF_NM,
    extension_matrix,
    production_matrix,
)
from mcxray_wrapper.spec import WALTHER_PAPER, RunSpec
from tests.conftest import GOLDEN_CSV, GOLDEN_RUN_ID


def _build_run(sim_dir, results_dir, spec):
    """Generate a run's inputs into sim_dir and give it an output CSV (the golden table)."""
    generate_inputs(spec, sim_dir)
    results_dir.mkdir(exist_ok=True)
    (results_dir / f"{spec.run_id}_XrayIntensities.csv").write_bytes(GOLDEN_CSV.read_bytes())
    # a couple of extra output files, so n_output_files is realistic
    (results_dir / f"{spec.run_id}_Options.txt").write_text("stub", encoding="utf-8")


@pytest.fixture
def two_run_set(tmp_path):
    """Two runs sharing the golden intensity table but differing in spec."""
    sim, results, out = tmp_path / "Sim", tmp_path / "Results", tmp_path / "Aggregated"
    sim.mkdir()
    specs = [
        RunSpec(run_id="run_a", x_bi=0.1, thickness_nm=100, n_electrons=1000),
        RunSpec(run_id="run_b", x_bi=0.2, thickness_nm=512, n_electrons=1000),
    ]
    for s in specs:
        _build_run(sim, results, s)
    return specs, sim, results, out


def test_combined_table_has_all_rows_and_spec_columns(two_run_set):
    specs, sim, results, out = two_run_set
    paths = aggregate_runs(specs, sim, results, out)
    df = pd.read_csv(paths["combined_table"])

    # 21 golden rows per run, 2 runs.
    assert len(df) == 42
    assert set(df["run_id"]) == {"run_a", "run_b"}
    # spec columns present and correct per run.
    for col in ("x_bi", "thickness_nm", "mass_density_g_cm3", "detector_crystal_thickness_cm"):
        assert col in df.columns
    a = df[df["run_id"] == "run_a"].iloc[0]
    assert a["x_bi"] == 0.1 and a["thickness_nm"] == 100
    b = df[df["run_id"] == "run_b"].iloc[0]
    assert b["thickness_nm"] == 512


def test_no_derived_columns_are_added(two_run_set):
    """The load-bearing rule: raw intensities only, never a ratio or k-factor."""
    specs, sim, results, out = two_run_set
    df = pd.read_csv(aggregate_runs(specs, sim, results, out)["combined_table"])
    banned = [c for c in df.columns if any(t in c.lower() for t in ("ratio", "kfactor", "k_factor", "k*"))]
    assert banned == []


def test_manifest_links_every_run_to_its_files(two_run_set):
    specs, sim, results, out = two_run_set
    manifest = json.loads(aggregate_runs(specs, sim, results, out)["manifest"].read_text())
    assert manifest["n_runs"] == 2
    ids = {r["run_id"] for r in manifest["runs"]}
    assert ids == {"run_a", "run_b"}
    for run in manifest["runs"]:
        assert run["sam_matches_spec"] is True
        assert len(run["input_files"]) == 6
        assert run["intensity_csv"].endswith("_XrayIntensities.csv")


def test_missing_output_fails_loudly(two_run_set):
    specs, sim, results, out = two_run_set
    (results / "run_b_XrayIntensities.csv").unlink()
    with pytest.raises(ValueError, match="missing"):
        aggregate_runs(specs, sim, results, out)


def test_sam_not_matching_spec_fails_loudly(two_run_set):
    """If a run_id points at a .sam that does not match the spec (wrong density), the
    aggregator must refuse rather than mislabel provenance."""
    specs, sim, results, out = two_run_set
    # Corrupt run_a's stored .sam density so it no longer matches the spec.
    sam = sim / "run_a.sam"
    text = sam.read_text(encoding="ascii")
    sam.write_text(text.replace("UserDefinedMassDensity=5.506", "UserDefinedMassDensity=9.99"),
                   encoding="ascii", newline="")
    with pytest.raises(ValueError, match="does not match"):
        aggregate_runs(specs, sim, results, out)


def test_output_dir_is_created_and_not_results(two_run_set):
    specs, sim, results, out = two_run_set
    assert not out.exists()
    aggregate_runs(specs, sim, results, out)
    assert out.is_dir()
    assert out.resolve() != results.resolve()


def test_production_matrix_run_ids_are_unique_and_well_formed():
    specs = production_matrix()
    assert len(specs) == 15
    assert len({s.run_id for s in specs}) == 15
    assert all(s.run_id.startswith("GaAsBi_") and "_rho" in s.run_id for s in specs)


# ---- Set C: the low-x thickness arm, added without disturbing the frozen 15 ----

def test_set_c_extension_does_not_change_the_frozen_fifteen():
    """Everything derived before 2026-08-13 was computed from production_matrix(). If adding
    Set C altered it, those results would silently stop being reproducible."""
    from mcxray_wrapper.matrix import extension_matrix, full_matrix

    assert len(production_matrix()) == 15
    assert len(extension_matrix()) == 6
    assert len(full_matrix()) == 21
    # full_matrix must be exactly the 15 followed by the 6 -- no reordering, no substitution.
    assert [s.run_id for s in full_matrix()] == \
        [s.run_id for s in production_matrix()] + [s.run_id for s in extension_matrix()]


def test_set_c_is_the_low_x_thick_arm():
    from mcxray_wrapper.matrix import SET_C_THICKNESSES_NM, SET_C_X_BI, extension_matrix

    specs = extension_matrix()
    assert {s.x_bi for s in specs} == {SET_C_X_BI}
    assert [s.thickness_nm for s in specs] == SET_C_THICKNESSES_NM
    # Thick arm only -- every run is above the thin-foil cutoff, so all run at 10^6.
    assert all(s.thickness_nm > THIN_CUTOFF_NM for s in specs)
    assert {s.n_electrons for s in specs} == {N_ELECTRONS_THICK}


def test_set_c_run_ids_do_not_collide_with_the_frozen_fifteen():
    """Set B already contains x=0.01 at 100 nm, so the density stem rho5339 is shared. Only the
    thickness distinguishes them -- worth asserting, since Results\\ is a flat directory."""
    from mcxray_wrapper.matrix import full_matrix

    ids = [s.run_id for s in full_matrix()]
    assert len(ids) == len(set(ids)) == 21
    assert all("_rho5339" in s.run_id for s in extension_matrix())
