"""Render every figure. `python -m figures.make_all`

Each entry is independent, so one failing figure reports and the rest still render -- an
unattended regeneration before a deadline is more useful finishing than halting on the first
problem. Exit status is non-zero if anything failed.
"""

from __future__ import annotations

import sys
import traceback

from figures import (
    fig01_ratios,
    fig02_corner,
    fig03_measurability,
    fig04_sumpeak,
    fig05_recovery,
    fig06_bi_k,
)
from figures.style import FIGURES_DIR

FIGURES = (
    ("Fig 1  ratios vs thickness (Walther Fig. 1)", fig01_ratios.make),
    ("Fig 2  rho.t insufficiency (Set A vs Set C)", fig02_corner.make),
    ("Fig 3  measurability limit (LO4 headline)", fig03_measurability.make),
    ("Fig 4  sum-peak composition selectivity", fig04_sumpeak.make),
    ("Fig 5  recovery, simulated vs as-measured", fig05_recovery.make),
    ("Fig 6  Bi K: absorption-immune, photon-starved", fig06_bi_k.make),
)


def main() -> int:
    print(f"writing to {FIGURES_DIR}\n")
    failures = 0
    for label, make in FIGURES:
        try:
            written = make()
            print(f"[ OK ] {label}")
            for path in written:
                print(f"         {path.name}")
        except Exception:
            failures += 1
            print(f"[FAIL] {label}")
            traceback.print_exc(limit=3)
    print(f"\n{len(FIGURES) - failures}/{len(FIGURES)} figures rendered")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
