"""Stage 3 (executor) acceptance tests.

Hermetic: every test runs a STAND-IN executable -- a small Python script written into tmp_path
-- never MC X-Ray itself, and never against the real Sim\\ or Results\\ directories. The
stand-in is driven through the same `--simulation-file` interface as the real binary and
fabricates the same output-file naming, so the wiring under test is real even though the
simulator is not.

The tests that matter most are not the happy path:

  * test_refuses_to_overwrite_existing_outputs -- Results\\ holds the 15 definitive production
    runs, flat and unversioned. This is the guard that stops a re-run destroying them.
  * test_exit_zero_without_intensity_csv_is_a_failure -- the simulator can return success
    having written nothing usable. A loop checking only returncode would report a clean sweep
    over missing data.
"""

from __future__ import annotations

import sys
import textwrap
from pathlib import Path

import pytest

from mcxray_wrapper.executor import (
    EXPECTED_OUTPUT_COUNT,
    INTENSITY_SUFFIX,
    existing_outputs,
    resolve_executable,
    results_dir,
    run_matrix,
    run_simulation,
    summarise,
)
from mcxray_wrapper.spec import RunSpec

# Mirrors the real 19 outputs closely enough to exercise the counting and prefix logic.
_OUTPUT_SUFFIXES = [
    "_ElectronResults.dat", "_Options.txt", "_ProgramVersion.dat",
    "_SimulatedSpectraCharacteristicRegion_0.csv", "_SimulatedSpectraRegionInfo_0.dat",
    "_SimulatedSpectraRegion_0.csv", "_SimulatedSpectraSpecimen.csv",
    "_SpectraAtomDetectedLines_Region0.csv", "_SpectraAtomEmittedDetectedLines_Region0.csv",
    "_SpectraAtomPerElectronLines_1_srkeV_Region0.csv", "_SpectraDetectedRegion_0.csv",
    "_SpectraEmittedDetectedRegion_0.csv", "_SpectraPerElectron_1_srkeV_Region_0.csv",
    "_SpectraRegionInfo_0.dat", "_SpectraSpecimen.csv", "_SpectraSpecimenEmittedDetected.csv",
    "_SpectraSpecimenInfo.dat", "_XrayDetectorEfficiency.csv",
]


def _spec(run_id="TESTRUN_2nm_x020", thickness_nm=2, x_bi=0.2, n_electrons=1000):
    return RunSpec(run_id=run_id, x_bi=x_bi, thickness_nm=thickness_nm, n_electrons=n_electrons)


def _fake_exe(tmp_path: Path, mode: str = "ok", n_extra: int = len(_OUTPUT_SUFFIXES)):
    """A stand-in for console_mcxray_lite_x64.exe.

    Returns a command prefix (list) rather than a path -- `run_simulation` accepts a sequence
    precisely so a stand-in can be substituted without depending on Windows .bat semantics.

    modes: ok | crash | silent (exit 0, no intensity csv) | empty (exit 0, zero-byte csv) | hang
    """
    script = tmp_path / f"fake_mcxray_{mode}.py"
    script.write_text(textwrap.dedent(f'''
        import sys, time
        from pathlib import Path

        mode = {mode!r}
        argv = sys.argv[1:]
        sim = argv[argv.index("--simulation-file") + 1]
        run_id = Path(sim).stem

        if mode == "hang":
            time.sleep(30)
            sys.exit(0)
        if mode == "crash":
            sys.stderr.write("MC X-Ray: fatal error in region 0\\n")
            sys.exit(3)

        # cwd is the Sim folder, so this is Sim\\Results\\ -- the .par's BaseFileName convention.
        results = Path("Results")
        results.mkdir(exist_ok=True)
        for suffix in {_OUTPUT_SUFFIXES[:n_extra]!r}:
            (results / (run_id + suffix)).write_text("stand-in output\\n")

        if mode == "silent":
            sys.exit(0)
        intensity = results / (run_id + "{INTENSITY_SUFFIX}")
        intensity.write_text("" if mode == "empty" else "Atomic number, Line, Intensity,\\n")
        sys.exit(0)
    ''').strip() + "\n", encoding="utf-8")
    return [sys.executable, str(script)]


# ---- happy path ----

def test_successful_run_reports_ok_and_finds_the_intensity_csv(tmp_path):
    result = run_simulation(_spec(), sim_dir=tmp_path, executable=_fake_exe(tmp_path))

    assert result.ok
    assert result.status == "completed"
    assert result.returncode == 0
    assert result.intensity_csv is not None and result.intensity_csv.is_file()
    assert len(result.output_files) == EXPECTED_OUTPUT_COUNT
    assert result.detail == ""  # no anomaly to report


def test_all_six_inputs_are_written_flat_into_the_sim_dir(tmp_path):
    """The .sim resolves its five siblings BY NAME from its own directory -- so they must be
    flat beside it, not in a per-run subfolder."""
    spec = _spec()
    run_simulation(spec, sim_dir=tmp_path, executable=_fake_exe(tmp_path))

    for role in ("sim", "sam", "mic", "par", "mdl", "rp"):
        assert (tmp_path / f"{spec.run_id}.{role}").is_file(), f"missing {role} beside the .sim"


def test_outputs_land_in_the_results_subdirectory(tmp_path):
    spec = _spec()
    run_simulation(spec, sim_dir=tmp_path, executable=_fake_exe(tmp_path))

    assert results_dir(tmp_path).is_dir()
    assert all(p.parent == results_dir(tmp_path) for p in existing_outputs(spec.run_id, tmp_path))


# ---- the overwrite guard: this is what protects the 15 production runs ----

def test_refuses_to_overwrite_existing_outputs(tmp_path):
    spec = _spec()
    out = results_dir(tmp_path)
    out.mkdir(parents=True)
    precious = out / f"{spec.run_id}{INTENSITY_SUFFIX}"
    precious.write_text("irreplaceable production data\n")

    result = run_simulation(spec, sim_dir=tmp_path, executable=_fake_exe(tmp_path))

    assert not result.ok
    assert result.status == "skipped"
    assert "refusing to overwrite" in result.detail
    # The decisive assertion: the existing file is untouched.
    assert precious.read_text() == "irreplaceable production data\n"


def test_overwrite_true_proceeds(tmp_path):
    spec = _spec()
    out = results_dir(tmp_path)
    out.mkdir(parents=True)
    (out / f"{spec.run_id}{INTENSITY_SUFFIX}").write_text("stale\n")

    result = run_simulation(spec, sim_dir=tmp_path, executable=_fake_exe(tmp_path),
                            overwrite=True)

    assert result.ok
    assert result.intensity_csv.read_text() != "stale\n"


def test_existing_outputs_requires_the_underscore_boundary(tmp_path):
    """`GaAsBi_x01` must not match `GaAsBi_x010_...` -- otherwise the guard would refuse
    unrelated runs, or worse, a narrower run_id would appear already-run."""
    out = results_dir(tmp_path)
    out.mkdir(parents=True)
    (out / "RUN_x010_XrayIntensities.csv").write_text("other run\n")

    assert existing_outputs("RUN_x01", tmp_path) == []
    assert len(existing_outputs("RUN", tmp_path)) == 1


# ---- failure modes, kept distinct ----

def test_nonzero_exit_is_a_crash(tmp_path):
    result = run_simulation(_spec(), sim_dir=tmp_path, executable=_fake_exe(tmp_path, "crash"))

    assert not result.ok
    assert result.status == "crashed"
    assert result.returncode == 3
    assert "fatal error" in result.detail  # stderr surfaced, not swallowed


def test_exit_zero_without_intensity_csv_is_a_failure(tmp_path):
    """The dangerous case: the simulator reports success having written nothing usable."""
    result = run_simulation(_spec(), sim_dir=tmp_path, executable=_fake_exe(tmp_path, "silent"))

    assert not result.ok
    assert result.status == "sim_failed"
    assert result.returncode == 0  # it really did claim success
    assert "missing" in result.detail


def test_exit_zero_with_empty_intensity_csv_is_a_failure(tmp_path):
    result = run_simulation(_spec(), sim_dir=tmp_path, executable=_fake_exe(tmp_path, "empty"))

    assert not result.ok
    assert result.status == "sim_failed"
    assert "empty" in result.detail


def test_timeout_is_reported_not_raised(tmp_path):
    result = run_simulation(_spec(), sim_dir=tmp_path, executable=_fake_exe(tmp_path, "hang"),
                            timeout_s=1.0)

    assert not result.ok
    assert result.status == "timed_out"
    assert result.returncode is None


def test_unexpected_output_count_is_reported_but_not_fatal(tmp_path):
    """The primary output exists, so the run is usable -- but a changed file count means the
    interface understanding may be wrong, which CLAUDE.md says to surface immediately."""
    result = run_simulation(_spec(), sim_dir=tmp_path,
                            executable=_fake_exe(tmp_path, "ok", n_extra=3))

    assert result.ok
    assert f"expected {EXPECTED_OUTPUT_COUNT}" in result.detail


def test_missing_executable_raises(tmp_path):
    with pytest.raises(FileNotFoundError, match="not found"):
        resolve_executable(tmp_path, name="definitely_not_here_x64.exe")


# ---- batch ----

def test_run_matrix_continues_past_a_failure(tmp_path):
    """An unattended sweep is more useful finishing and accounting for failures than halting."""
    specs = [_spec(f"BATCH_{i}", thickness_nm=2 ** i) for i in range(1, 4)]
    out = results_dir(tmp_path)
    out.mkdir(parents=True)
    (out / f"{specs[1].run_id}{INTENSITY_SUFFIX}").write_text("blocks run 2\n")

    results = run_matrix(specs, sim_dir=tmp_path, executable=_fake_exe(tmp_path), progress=False)

    assert len(results) == 3
    assert [r.ok for r in results] == [True, False, True]
    assert results[1].status == "skipped"


def test_run_matrix_stop_on_failure_aborts_early(tmp_path):
    specs = [_spec(f"BATCH_{i}", thickness_nm=2 ** i) for i in range(1, 4)]
    out = results_dir(tmp_path)
    out.mkdir(parents=True)
    (out / f"{specs[1].run_id}{INTENSITY_SUFFIX}").write_text("blocks run 2\n")

    results = run_matrix(specs, sim_dir=tmp_path, executable=_fake_exe(tmp_path),
                         stop_on_failure=True, progress=False)

    assert len(results) == 2  # third never attempted
    assert not results[-1].ok


def test_summarise_counts_by_status(tmp_path):
    specs = [_spec(f"BATCH_{i}", thickness_nm=2 ** i) for i in range(1, 4)]
    out = results_dir(tmp_path)
    out.mkdir(parents=True)
    (out / f"{specs[0].run_id}{INTENSITY_SUFFIX}").write_text("blocks run 1\n")

    line = summarise(run_matrix(specs, sim_dir=tmp_path, executable=_fake_exe(tmp_path),
                                progress=False))

    assert "3 runs" in line
    assert "2 completed" in line
    assert "1 skipped" in line
