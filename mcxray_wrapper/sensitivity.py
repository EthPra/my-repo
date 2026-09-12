"""P4.1 -- the as-measured round trip, swept across every modelling choice.

WHAT THIS ANSWERS. Every recovered composition so far has come from PRISTINE simulated
intensities. A real spectrometer never produces those: it produces the same signal plus a sum
peak sitting on Bi Ma. This runs the whole recovery on as-measured data instead, and reports how
far the answer moves.

WHY A FULL FACTORIAL. `sumpeak.py` exposes four modelling choices as switches precisely because
none of them could be settled -- Walther fitted his own magnitude to close a gap, so there is no
published recipe to inherit, and he is unreachable until late August. Rather than pick a set and
hope, every combination is run:

    3 levels x 2 parent sets x 2 bases x 2 conservation x 2 M-band baselines = 48 configurations

plus a clean baseline. The point is not the 48 numbers. It is the question **does the conclusion
depend on the choices?** If the route ranking survives all of them, the choices did not matter
and the finding is robust. If it flips somewhere, that instability is itself the result -- and
either way it is reported rather than hidden behind a default.

WHAT IS HELD FIXED, AND WHY. The artefact is applied to the UNKNOWN runs only, never to the
calibration (`sumpeak.as_measured_unknowns`). That is Walther's own practice -- his calibration
was simulated, his unknown measured -- and it is not a swept choice. Corrupting both sides makes
the error largely self-cancel, which understates the damage; measured on this data it removed
the effect at x = 0.20 entirely (REPORT 26.6).

Recovery uses the As K/L thickness proxy throughout (`roundtrip.recover_x_via_kl`), so the round
trip stays held out in both composition AND thickness.
"""

from __future__ import annotations

from itertools import product

import pandas as pd

from mcxray_wrapper.roundtrip import recover_x_via_kl
from mcxray_wrapper.sumpeak import (
    M_BAND_FACTOR_MEASURED,
    M_BAND_FACTOR_SIMULATED,
    SENSITIVITY_LEVELS,
    as_measured_unknowns,
)

# The four switches, and the values each is swept over. Named here rather than inline so the
# stored output and the write-up describe the same grid.
SWITCH_GRID = {
    "parents": ("alpha_only", "alpha_beta"),
    "basis": ("intensity", "rate_product"),
    "conserve": (True, False),
    "m_band_factor": (M_BAND_FACTOR_SIMULATED, M_BAND_FACTOR_MEASURED),
}

# The Bi line each route family uses -- the sum peak lands on Bi Ma, so this is what separates
# the routes it wrecks from the ones it cannot touch.
_BI_SHELL_LABEL = {"K": "Bi K", "L": "Bi L", "M": "Bi M"}


def sweep(combined: pd.DataFrame,
          levels: "tuple[float, ...]" = SENSITIVITY_LEVELS,
          axis: str = "As_K_L") -> pd.DataFrame:
    """Recover x under every (level x switch) combination, plus a clean baseline.

    One row per (configuration, Set B run, route, shell pair, line definition). Every row carries
    the settings that produced it, so a number can never be separated from its assumptions.

    `level = 0` is included as the baseline: with no artefact the result must equal the ordinary
    clean recovery, which is the anchor the rest of the table is read against.
    """
    frames = []

    baseline = recover_x_via_kl(combined, axis=axis)
    baseline = baseline.assign(level=0.0, parents="none", basis="none",
                               conserve=False, m_band_factor=M_BAND_FACTOR_SIMULATED)
    frames.append(baseline)

    keys = tuple(SWITCH_GRID)
    for level in levels:
        for values in product(*(SWITCH_GRID[k] for k in keys)):
            settings = dict(zip(keys, values))
            as_measured = as_measured_unknowns(combined, level, **settings)
            recovered = recover_x_via_kl(as_measured, axis=axis)
            frames.append(recovered.assign(level=level, **settings))

    out = pd.concat(frames, ignore_index=True)
    out["bi_line"] = out["heavy_shell"].map(_BI_SHELL_LABEL).where(
        out["route"].str.startswith("Bi"), "no Bi")
    out["abs_error"] = out["error"].abs()
    return out


def summarise_by_route(swept: pd.DataFrame) -> pd.DataFrame:
    """Mean |error| per (level, Bi line used, definition), averaged over the switch grid.

    Collapsing the 16 switch combinations into a mean is only defensible if they agree; the
    spread column says whether they do. A large spread means a modelling choice is driving the
    answer and must be reported, not averaged away.
    """
    grouped = swept.groupby(["level", "bi_line", "definition"], sort=False)["abs_error"]
    out = grouped.agg(mean_abs_error="mean", worst_abs_error="max",
                      best_abs_error="min").reset_index()
    out["switch_spread"] = out["worst_abs_error"] - out["best_abs_error"]
    return out.sort_values(["level", "bi_line", "definition"]).reset_index(drop=True)


def switch_influence(swept: pd.DataFrame) -> pd.DataFrame:
    """How much each individual switch moves the answer, at the highest level swept.

    Answers the question the factorial exists for: of the four choices nobody could settle,
    which actually matter? A switch whose two settings give the same error is a choice that can
    be stated and moved on from.
    """
    worst_level = swept[swept["level"] == swept["level"].max()]
    rows = []
    for switch, values in SWITCH_GRID.items():
        means = {v: worst_level[worst_level[switch] == v]["abs_error"].mean() for v in values}
        low, high = min(means.values()), max(means.values())
        rows.append({
            "switch": switch,
            "settings": " vs ".join(str(v) for v in values),
            **{f"mean_abs_error[{v}]": means[v] for v in values},
            "difference": high - low,
            "relative_difference": (high - low) / low if low else float("inf"),
        })
    return pd.DataFrame(rows).sort_values("difference", ascending=False).reset_index(drop=True)


def write_sensitivity(combined_csv: "str | object", output_dir, **kwargs) -> dict:
    """Run the sweep and write the full table plus both summaries."""
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    swept = sweep(pd.read_csv(combined_csv), **kwargs)

    written = {}
    for name, frame in (("sumpeak_roundtrip_sweep", swept),
                        ("sumpeak_roundtrip_by_route", summarise_by_route(swept)),
                        ("sumpeak_switch_influence", switch_influence(swept))):
        path = output_dir / f"{name}.csv"
        frame.to_csv(path, index=False)
        written[name] = path
    return written
