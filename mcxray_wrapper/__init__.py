"""Automation wrapper around MC X-Ray Lite v1.7.1 (console build, Windows x64).

Two halves, deliberately decoupled (Wrapper_Blueprint.md 2):

  Run + store -- 1 (input generator), 2 (output parser), 3 (executor), 4 (run matrix),
    5 (aggregator + provenance manifest).
  Derive -- 6a (the three diagnostic ratios), 7a (empirical k*), 7b (k* re-indexed on the
    measurable K/L ratio), 7c (the held-out round trip).

**The load-bearing rule joining them:** the run loop stores RAW, unprocessed intensities and
nothing derived. Everything in the derive half reads that stored table back and never re-runs
the simulator, so an answered atomic-data question costs a re-derivation rather than a re-sweep.

Still downstream: 6b sum-peak synthesis (blocked on modelling decisions with Walther) and the
inversion verdict (Ethan's, not automated).
"""

from mcxray_wrapper.aggregate import aggregate_runs
from mcxray_wrapper.executor import run_matrix, run_simulation
from mcxray_wrapper.kfactors import (
    calibration_curves,
    composition_curves,
    compute_k_star,
    invariance_check,
)
from mcxray_wrapper.kl_index import index_on_kl
from mcxray_wrapper.matrix import production_matrix
from mcxray_wrapper.ratios import compute_ratios
from mcxray_wrapper.roundtrip import recover_x, summarize
from mcxray_wrapper.spec import RunSpec

__all__ = [
    # run + store
    "RunSpec",
    "production_matrix",
    "run_simulation",
    "run_matrix",
    "aggregate_runs",
    # derive
    "compute_ratios",
    "compute_k_star",
    "calibration_curves",
    "composition_curves",
    "invariance_check",
    "index_on_kl",
    "recover_x",
    "summarize",
]
