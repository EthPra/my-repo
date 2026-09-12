"""Regenerate every derived output in Aggregated\\ from the stored simulation results.

The analysis counterpart to `run_sweep.py`. That script produces raw simulation output; this one
turns it into the tables the write-up quotes, and nothing else -- it never invokes the simulator.

WHY THIS EXISTS. Until now each `write_*` function was called by hand, one at a time, from
whatever session happened to be running. That made "regenerate everything" an act of memory
rather than a command, and the evidence it went wrong is already on disk: `sumpeak_sensitivity.csv`
is referenced in WORKPLAN_17AUG.md 3.5 as an existing file and is not in Aggregated\\ at all,
because the one function that writes it was never run against the full matrix. A single ordered
entry point makes that class of gap impossible.

The stages are declared in dependency order and run in it. Everything downstream of Stage 5 reads
a STORED table -- never the simulator, never another module's in-memory frame -- so any stage can
be re-run alone and the result is identical.

Usage, from the Wrapper directory:

    python run_analysis.py                  # everything, including re-aggregation from Results\\
    python run_analysis.py --derived-only   # skip Stage 5; recompute from the stored table
    python run_analysis.py --list           # show the stages and what each writes
    python run_analysis.py --only counting budget

Re-running is safe and idempotent: outputs are overwritten in place with the same content unless
the inputs or the code changed. That is the opposite of `run_sweep.py`'s posture, and
deliberately so -- derived files are cheap and re-derivable, whereas Results\\ is not.
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

from mcxray_wrapper import (
    absorption,
    aggregate,
    budget,
    corner,
    counting,
    kfactors,
    kl_index,
    overlap,
    ratios,
    roundtrip,
    sensitivity,
    sumpeak,
)
from mcxray_wrapper.executor import DEFAULT_SIM_DIR, results_dir
from mcxray_wrapper.matrix import full_matrix

DEFAULT_AGGREGATED = DEFAULT_SIM_DIR / "Aggregated"

COMBINED = "combined_intensities.csv"
RATIOS = "diagnostic_ratios.csv"


def _aggregate(sim_dir: Path, out: Path) -> dict:
    return aggregate.aggregate_runs(full_matrix(), sim_dir, results_dir(sim_dir), out)


# name, what it needs, the call. `combined` and `ratios` name the stored file each stage reads,
# so the dependency is visible here rather than buried in a function body.
STAGES = (
    ("aggregate", "Results\\", lambda sim, out: _aggregate(sim, out)),
    ("ratios", COMBINED, lambda sim, out: ratios.write_ratios(out / COMBINED, out)),
    ("kfactors", COMBINED, lambda sim, out: {
        "calibration": kfactors.write_calibration(out / COMBINED, out),
        "composition": kfactors.write_composition_curves(out / COMBINED, out),
        "invariance": kfactors.write_invariance(out / COMBINED, out),
    }),
    ("kl_index", COMBINED, lambda sim, out: kl_index.write_kl_index(out / COMBINED, out)),
    ("roundtrip", COMBINED, lambda sim, out: roundtrip.write_roundtrips(out / COMBINED, out)),
    ("corner", RATIOS, lambda sim, out: corner.write_corner_analysis(out / RATIOS, out)),
    ("absorption", RATIOS, lambda sim, out: absorption.write_absorption_analysis(out / RATIOS, out)),
    # m_band_factor is passed EXPLICITLY rather than left to the function's default of
    # M_BAND_FACTOR_SIMULATED (1.0, the bare simulated Bi Ma line). Decision 3, VERDICT_BRIEF.md,
    # Ethan 2026-08-21: the PRIMARY reported setting is M_BAND_FACTOR_MEASURED (1.743), the whole
    # unresolved M-band a real Si:Li detector actually reports -- the more defensible match to
    # what Walther's own measured Bi M values are, since his detector cannot resolve M sub-lines
    # either. Same lesson as the dose_scale comment below: the reporting basis belongs in the
    # driver, where it is visible, not in a default silently inherited.
    ("sumpeak", COMBINED, lambda sim, out: sumpeak.write_sumpeak(
        out / COMBINED, out, m_band_factor=sumpeak.M_BAND_FACTOR_MEASURED)),
    # dose_scale is passed EXPLICITLY rather than left to the function's default of 1.0 (the
    # stored 100 s basis). The bound quoted in REPORT 27 -- 3.47% counting floor at x = 0.01,
    # rising to 12.99% at 10% coupling -- is on Walther's 715.5 s acquisition, and inheriting the
    # default here silently regenerated the file at nine times that uncertainty while leaving the
    # column headings, the row count and the report's prose all unchanged. Caught on 2026-08-17
    # by hashing Aggregated\\ before and after the first full run of this script. The reporting
    # basis belongs in the driver, where it is visible, not in a default.
    ("overlap", COMBINED, lambda sim, out: overlap.write_overlap_bound(
        out / COMBINED, out, dose_scale=counting.WALTHER_DOSE_SCALE)),
    ("sensitivity", COMBINED, lambda sim, out: sensitivity.write_sensitivity(out / COMBINED, out)),
    ("counting", COMBINED, lambda sim, out: counting.write_counting(out / COMBINED, out)),
    # Same decision 3 as the sumpeak stage above -- the sum-peak bias term inside the error budget
    # must use the same primary setting, or bias_sumpeak here and sumpeak_sensitivity.csv would
    # silently disagree about what "the sum peak" means.
    ("budget", COMBINED, lambda sim, out: budget.write_budget(
        out / COMBINED, out, m_band_factor=sumpeak.M_BAND_FACTOR_MEASURED)),
)

STAGE_NAMES = tuple(name for name, _, _ in STAGES)


def _as_paths(result) -> list[Path]:
    if isinstance(result, dict):
        return [Path(v) for v in result.values()]
    return [Path(result)]


def main(argv: "list[str] | None" = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--sim-dir", default=str(DEFAULT_SIM_DIR),
                        help=f"the MC X-Ray folder (default: {DEFAULT_SIM_DIR})")
    parser.add_argument("--output-dir", default=str(DEFAULT_AGGREGATED),
                        help=f"where derived tables are written (default: {DEFAULT_AGGREGATED})")
    parser.add_argument("--derived-only", action="store_true",
                        help="skip re-aggregation and recompute from the stored combined table")
    parser.add_argument("--only", nargs="+", metavar="STAGE", choices=STAGE_NAMES,
                        help=f"run just these stages, in declared order: {', '.join(STAGE_NAMES)}")
    parser.add_argument("--list", action="store_true",
                        help="list the stages and what each reads, without running anything")
    args = parser.parse_args(argv)

    if args.list:
        print(f"{'stage':<14} reads")
        for name, needs, _ in STAGES:
            print(f"  {name:<12} {needs}")
        return 0

    sim_dir = Path(args.sim_dir)
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)

    selected = [s for s in STAGES if s[0] in args.only] if args.only else list(STAGES)
    if args.derived_only:
        selected = [s for s in selected if s[0] != "aggregate"]

    if not args.derived_only and any(s[0] == "aggregate" for s in selected):
        print(f"aggregating {len(full_matrix())} runs from {results_dir(sim_dir)}")

    written: list[Path] = []
    failures: list[tuple[str, Exception]] = []
    for name, needs, call in selected:
        start = time.time()
        try:
            paths = _as_paths(call(sim_dir, out))
        except Exception as error:  # a stage failing must not hide the ones after it
            print(f"  {name:<12} FAILED after {time.time()-start:5.1f}s -- {error}")
            failures.append((name, error))
            continue
        written.extend(paths)
        names = ", ".join(p.name for p in paths)
        print(f"  {name:<12} {time.time()-start:5.1f}s  {names}")

    print(f"\n{len(written)} files written to {out}")
    if failures:
        print(f"{len(failures)} stage(s) failed: {', '.join(n for n, _ in failures)}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
