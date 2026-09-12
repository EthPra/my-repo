"""Launch a sweep of MC X-Ray simulations. The command-line front end to executor.py.

This script is deliberately IN THE REPO rather than a scratchpad: its predecessor
(`rerun_production.py`) lived in a Claude session temp folder, ran the 15 production
simulations, and was swept when that session ended -- leaving the project unable to re-execute
its own runs (REPORT.md 22).

Usage, from the Wrapper directory:

    python run_sweep.py extension        # Set C only -- the 6 low-x thickness runs
    python run_sweep.py production       # the frozen 15
    python run_sweep.py full             # all 21
    python run_sweep.py extension --dry-run

Existing outputs are never overwritten: a run whose results are already on disk is reported as
"skipped" and left alone. `--overwrite` disables that guard and is not something to pass
casually -- Results\\ is flat, unversioned, and holds the definitive production data.
"""

from __future__ import annotations

import argparse
import sys

from mcxray_wrapper.executor import (
    DEFAULT_SIM_DIR,
    existing_outputs,
    resolve_executable,
    run_matrix,
    summarise,
)
from mcxray_wrapper.matrix import extension_matrix, full_matrix, production_matrix

MATRICES = {
    "production": production_matrix,
    "extension": extension_matrix,
    "full": full_matrix,
}


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("matrix", choices=sorted(MATRICES), help="which run list to execute")
    parser.add_argument("--sim-dir", default=str(DEFAULT_SIM_DIR),
                        help=f"the MC X-Ray folder (default: {DEFAULT_SIM_DIR})")
    parser.add_argument("--dry-run", action="store_true",
                        help="list what would run, and what already exists, without running")
    parser.add_argument("--overwrite", action="store_true",
                        help="DESTRUCTIVE: replace existing outputs instead of skipping them")
    parser.add_argument("--stop-on-failure", action="store_true",
                        help="abort the sweep at the first failure instead of continuing")
    args = parser.parse_args(argv)

    specs = MATRICES[args.matrix]()
    print(f"{args.matrix} matrix: {len(specs)} runs, sim_dir={args.sim_dir}")

    if args.dry_run:
        for spec in specs:
            prior = existing_outputs(spec.run_id, args.sim_dir)
            state = f"{len(prior)} existing outputs -> WOULD SKIP" if prior else "would run"
            print(f"  {spec.run_id:<30} t={spec.thickness_nm:>6g}nm  x={spec.x_bi:<5} "
                  f"n={spec.n_electrons:>9,}  {state}")
        print(f"\nexecutable: {resolve_executable(args.sim_dir)}")
        return 0

    if args.overwrite:
        print("WARNING: --overwrite is set. Existing outputs WILL be replaced.", flush=True)

    results = run_matrix(
        specs,
        sim_dir=args.sim_dir,
        overwrite=args.overwrite,
        stop_on_failure=args.stop_on_failure,
    )

    print("\n" + summarise(results))
    failures = [r for r in results if not r.ok and r.status != "skipped"]
    for failure in failures:
        print(f"  FAILED {failure.run_id}: {failure.status} -- {failure.detail}")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
