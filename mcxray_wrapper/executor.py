"""Stage 3 -- invoke MC X-Ray Lite for one run, or for a matrix of runs.

REBUILT 2026-08-13. The original was an ephemeral Claude session scratchpad script
(`rerun_production.py`) that ran the 15 production simulations and was swept when that session
ended -- discovered missing when every one of ~130 prior scratchpad folders turned out to be
empty. The runs' inputs, outputs and provenance manifest all survived; only the ability to
re-execute was lost. This module is that ability, in the repo and tested.

The interface, from CLAUDE.md and confirmed against the stored production runs:

    console_mcxray_lite_x64.exe --simulation-file <run_id>.sim        cwd = C:\\MCXRAY\\Sim

Only the .sim is named on the command line; it resolves its five siblings (.sam/.mic/.par/
.mdl/.rp) BY NAME from the same directory. That is why inputs must be written flat into the Sim
folder rather than a per-run subdirectory, and why cwd must be that folder. The .par carries
`BaseFileName=Results/<run_id>`, so the ~19 outputs land in Sim\\Results\\ prefixed by run_id --
run_id prefixes are what keep that flat directory collision-free.

TWO FAILURE MODES, deliberately distinguished (Wrapper_Blueprint.md 2):

  crash        -- non-zero exit status, or the process timed out / could not start.
  sim failure  -- exit status 0 but the run did not actually produce its primary output.
                  This is the dangerous one: the simulator can return success while writing
                  nothing usable, and a batch loop that only checks returncode would record a
                  clean sweep over missing data.

OVERWRITE PROTECTION. `Results\\` holds the 15 definitive production runs, flat, with no
version control. Re-running an existing run_id would silently replace that run's 19 output
files. So a run whose outputs already exist is REFUSED unless overwrite=True is passed
explicitly. The guard is on the outputs, not on the inputs: regenerating the six input files is
harmless and deterministic, but destroying simulated results is not.

This module does not parse, aggregate or derive anything -- it runs the simulator and reports
what happened. Reading results back is Stage 2/5's job.
"""

from __future__ import annotations

import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Sequence

from mcxray_wrapper.inputgen import generate_inputs
from mcxray_wrapper.spec import RunSpec

# The Sim folder: where inputs are written, where cwd is set, and the parent of Results\.
DEFAULT_SIM_DIR = Path(r"C:\MCXRAY\Sim")

# The x64 console build. Three other executables sit beside it in the Sim folder (a 32-bit
# console build and two GUI builds); this project uses the x64 console one only.
DEFAULT_EXECUTABLE_NAME = "console_mcxray_lite_x64.exe"

RESULTS_SUBDIR = "Results"

# The primary output -- the per-line intensity table this project's analysis reads. Its
# presence is what distinguishes a real run from a silent no-op.
INTENSITY_SUFFIX = "_XrayIntensities.csv"

# Every production run emitted exactly 19 files. Asserted from the stored runs, not from
# prose: a run producing fewer is reported, not silently accepted.
EXPECTED_OUTPUT_COUNT = 19

# A 10^7-trajectory run takes minutes, not hours. An hour per run is a generous ceiling that
# still catches a genuinely hung process rather than waiting forever.
DEFAULT_TIMEOUT_S = 3600


@dataclass(frozen=True)
class RunResult:
    """What happened to one run. `ok` is the only thing a caller should branch on."""

    run_id: str
    ok: bool
    status: str  # "completed" | "crashed" | "timed_out" | "sim_failed" | "skipped"
    returncode: int | None
    duration_s: float
    intensity_csv: Path | None
    output_files: list[Path] = field(default_factory=list)
    detail: str = ""

    def __str__(self) -> str:
        mark = "OK  " if self.ok else "FAIL"
        return (f"[{mark}] {self.run_id}: {self.status} "
                f"({len(self.output_files)} files, {self.duration_s:.1f}s) {self.detail}".rstrip())


def results_dir(sim_dir: Path | str = DEFAULT_SIM_DIR) -> Path:
    return Path(sim_dir) / RESULTS_SUBDIR


def existing_outputs(run_id: str, sim_dir: Path | str = DEFAULT_SIM_DIR) -> list[Path]:
    """Output files already on disk for `run_id`. Non-empty means re-running would destroy data.

    Matches on the `<run_id>_` prefix the simulator itself uses. The trailing underscore
    matters: without it `GaAsBi_100nm_x01` would also match `GaAsBi_100nm_x010...`.
    """
    out = results_dir(sim_dir)
    if not out.is_dir():
        return []
    return sorted(p for p in out.iterdir() if p.is_file() and p.name.startswith(f"{run_id}_"))


def resolve_executable(sim_dir: Path | str = DEFAULT_SIM_DIR,
                       name: str = DEFAULT_EXECUTABLE_NAME) -> Path:
    """The simulator, in the Sim folder or on PATH. Raises if it cannot be found."""
    candidate = Path(sim_dir) / name
    if candidate.is_file():
        return candidate
    on_path = shutil.which(name)
    if on_path:
        return Path(on_path)
    raise FileNotFoundError(
        f"MC X-Ray executable {name!r} not found in {sim_dir} or on PATH"
    )


def _command(executable: Path | Sequence[str], sim_filename: str) -> list[str]:
    """Build the argv. A sequence is accepted so tests can substitute a stand-in binary."""
    prefix = [str(executable)] if isinstance(executable, (str, Path)) else [str(p) for p in executable]
    return [*prefix, "--simulation-file", sim_filename]


def run_simulation(
    spec: RunSpec,
    sim_dir: Path | str = DEFAULT_SIM_DIR,
    executable: Path | Sequence[str] | None = None,
    overwrite: bool = False,
    timeout_s: float = DEFAULT_TIMEOUT_S,
) -> RunResult:
    """Generate the six inputs for `spec`, run the simulator, and verify it produced output.

    Refuses (status "skipped", ok=False) if outputs for this run_id already exist and
    overwrite is False -- see the module docstring on why Results\\ is protected.

    Never raises on a failed *simulation*; a failure is reported in the returned RunResult so a
    batch can continue and account for it. Genuine programming/environment errors -- a missing
    executable, an unwritable Sim folder -- still raise.
    """
    sim_dir = Path(sim_dir)
    started = time.monotonic()

    prior = existing_outputs(spec.run_id, sim_dir)
    if prior and not overwrite:
        return RunResult(
            run_id=spec.run_id, ok=False, status="skipped", returncode=None,
            duration_s=0.0, intensity_csv=None, output_files=prior,
            detail=(f"{len(prior)} output files already exist in {results_dir(sim_dir)} -- "
                    "refusing to overwrite. Pass overwrite=True only if that is intended."),
        )

    if executable is None:
        executable = resolve_executable(sim_dir)

    # Inputs go flat into Sim\ because the .sim resolves its siblings by name from there.
    inputs = generate_inputs(spec, sim_dir)
    results_dir(sim_dir).mkdir(parents=True, exist_ok=True)

    command = _command(executable, inputs["sim"].name)
    try:
        completed = subprocess.run(
            command,
            cwd=str(sim_dir),
            capture_output=True,
            text=True,
            timeout=timeout_s,
        )
    except subprocess.TimeoutExpired:
        return RunResult(
            run_id=spec.run_id, ok=False, status="timed_out", returncode=None,
            duration_s=time.monotonic() - started, intensity_csv=None,
            output_files=existing_outputs(spec.run_id, sim_dir),
            detail=f"no exit after {timeout_s}s",
        )

    duration = time.monotonic() - started
    produced = existing_outputs(spec.run_id, sim_dir)
    intensity = results_dir(sim_dir) / f"{spec.run_id}{INTENSITY_SUFFIX}"

    if completed.returncode != 0:
        return RunResult(
            run_id=spec.run_id, ok=False, status="crashed", returncode=completed.returncode,
            duration_s=duration, intensity_csv=None, output_files=produced,
            detail=_tail(completed.stderr) or _tail(completed.stdout),
        )

    # Exit status 0 is NOT sufficient -- see the module docstring on silent sim failure.
    if not intensity.is_file() or intensity.stat().st_size == 0:
        return RunResult(
            run_id=spec.run_id, ok=False, status="sim_failed", returncode=0,
            duration_s=duration, intensity_csv=None, output_files=produced,
            detail=(f"exit status 0 but {intensity.name} is "
                    f"{'missing' if not intensity.is_file() else 'empty'}"),
        )

    detail = ""
    if len(produced) != EXPECTED_OUTPUT_COUNT:
        # Reported, not fatal: the primary output exists, so the run is usable. A changed file
        # count means the interface understanding may be off, which is worth surfacing.
        detail = f"expected {EXPECTED_OUTPUT_COUNT} output files, found {len(produced)}"

    return RunResult(
        run_id=spec.run_id, ok=True, status="completed", returncode=0,
        duration_s=duration, intensity_csv=intensity, output_files=produced, detail=detail,
    )


def _tail(text: str, lines: int = 3, width: int = 400) -> str:
    """Last few lines of captured output, for the failure detail."""
    if not text:
        return ""
    kept = [ln.strip() for ln in text.strip().splitlines() if ln.strip()][-lines:]
    return " | ".join(kept)[:width]


def run_matrix(
    specs: Sequence[RunSpec],
    sim_dir: Path | str = DEFAULT_SIM_DIR,
    executable: Path | Sequence[str] | None = None,
    overwrite: bool = False,
    timeout_s: float = DEFAULT_TIMEOUT_S,
    stop_on_failure: bool = False,
    progress: bool = True,
) -> list[RunResult]:
    """Run each spec in turn. Serial by design -- parallelism is gated on the .sim path
    resolution / non-zero seed spike, and 15 runs is under an hour anyway.

    Returns one RunResult per spec attempted. By default a failure does not stop the sweep:
    an unattended batch is more useful finishing and reporting than halting on run 3 of 15.
    Pass stop_on_failure=True to abort early instead.
    """
    if executable is None:
        executable = resolve_executable(sim_dir)  # fail fast, before any run starts

    results: list[RunResult] = []
    for index, spec in enumerate(specs, start=1):
        result = run_simulation(
            spec, sim_dir=sim_dir, executable=executable,
            overwrite=overwrite, timeout_s=timeout_s,
        )
        results.append(result)
        if progress:
            print(f"({index}/{len(specs)}) {result}", flush=True)
        if stop_on_failure and not result.ok:
            break
    return results


def summarise(results: Sequence[RunResult]) -> str:
    """One-line-per-status summary of a sweep, for a human reading the console."""
    if not results:
        return "no runs attempted"
    by_status: dict[str, int] = {}
    for r in results:
        by_status[r.status] = by_status.get(r.status, 0) + 1
    parts = [f"{count} {status}" for status, count in sorted(by_status.items())]
    total_s = sum(r.duration_s for r in results)
    return f"{len(results)} runs: " + ", ".join(parts) + f" ({total_s / 60:.1f} min total)"
