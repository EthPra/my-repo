"""Stage 7 (part 3) -- the held-out round trip. The actual pass/fail gate.

Calibrates k*(t) from Set A ONLY (known x=0.2, thickness swept, kfactors.calibration_curves).
Then, for each Set B run (known t=100nm, x swept), pretends x is unknown: looks up the
Set-A-calibrated k* at 100nm and inverts it against that run's OWN measured intensities to
produce a recovered x. The run's real x_bi is never touched during that computation -- it is
attached afterward, purely for grading. See test_recovered_x_does_not_use_true_x_bi below for
the check that enforces this isn't accidentally violated.

Interpolating k*(100nm): Set A doesn't include exactly 100nm (nearest neighbours are 64 and
128). A straight line between those two real, simulated points is used -- NOT a fitted
exponential across the full 2-1024nm range. Checked earlier (this project's own numbers): the
k*(t) curve is close to exponential at thin foils but visibly flattens by the thick end, so a
global exponential fit would introduce its own error near 100nm. Linear interpolation between
the nearest real neighbours has no such distortion.

Governance: this module reads the stored aggregated table only, never re-simulates, and the
recovered x it produces is Ethan's evidence to interpret, not a verdict computed here.
"""

from __future__ import annotations

import pandas as pd

from mcxray_wrapper.kfactors import ROUTES, calibration_curves, compute_k_star
from mcxray_wrapper.kl_index import index_on_kl
from mcxray_wrapper.ratios import compute_ratios
from mcxray_wrapper.matrix import (
    SET_B_THICKNESS_NM,
    SET_B_X_BI,
    SET_C_THICKNESSES_NM,
    SET_C_X_BI,
)
from mcxray_wrapper.spec import AS, ATOMIC_WEIGHTS, BI, GA


def _recover_x_bi_ga(k_star: float, a_bi: float, a_ga: float, i_bi: float, i_ga: float) -> float:
    """Eq 2 inverted: k* = x * (A_Bi/A_Ga) * (I_Ga/I_Bi)  =>  x = k* / [(A_Bi/A_Ga)(I_Ga/I_Bi)]."""
    return k_star / ((a_bi / a_ga) * (i_ga / i_bi))


def _recover_x_bi_as(k_star: float, a_bi: float, a_as: float, i_bi: float, i_as: float) -> float:
    """Eq 4 inverted: k* = [x/(1-x)] * (A_Bi/A_As) * (I_As/I_Bi)  =>  solve the x/(1-x) form."""
    y = k_star / ((a_bi / a_as) * (i_as / i_bi))
    return y / (1.0 + y)


def _recover_x_ga_as(k_star: float, a_ga: float, a_as: float, i_ga: float, i_as: float) -> float:
    """Eq 9 inverted: k* = [1/(1-x)] * (A_Ga/A_As) * (I_As/I_Ga)  =>  x = 1 - .../k*."""
    return 1.0 - (a_ga / a_as) * (i_as / i_ga) / k_star


# route label -> inverse formula, paired with kfactors.ROUTES' forward formula by label.
_INVERSE_FORMULAS = {
    "Bi_Ga": _recover_x_bi_ga,
    "Bi_As": _recover_x_bi_as,
    "Ga_As": _recover_x_ga_as,
}

_ROUTE_ELEMENTS = {label: (heavy_z, light_z) for label, heavy_z, _, light_z, _, _ in ROUTES}


def _interpolate_k_star(sorted_points: list[tuple[float, float]], target: float) -> float:
    """Linear interpolation between the two calibration points bracketing `target`.

    `sorted_points` is [(thickness, k_star), ...] sorted by thickness. Raises if target falls
    outside the calibrated range -- extrapolation is a different, riskier claim than
    interpolation and isn't done silently.
    """
    for (t0, k0), (t1, k1) in zip(sorted_points, sorted_points[1:]):
        if t0 <= target <= t1:
            if t1 == t0:
                return k0
            return k0 + (k1 - k0) * (target - t0) / (t1 - t0)
    raise ValueError(
        f"target thickness {target} is outside the Set A calibration range "
        f"({sorted_points[0][0]}-{sorted_points[-1][0]}nm) -- would be extrapolation"
    )


def _calibration_lookup(combined: pd.DataFrame) -> dict[tuple, list[tuple[float, float]]]:
    """Set A's k*(t) curves, as {(route, heavy_shell, light_shell, definition): [(t, k*), ...]}."""
    cal = calibration_curves(combined)
    lookup = {}
    group_cols = ["route", "heavy_shell", "light_shell", "definition"]
    for key, group in cal.groupby(group_cols, sort=False):
        lookup[key] = list(zip(group["thickness_nm"], group["k_star"]))
    return lookup


def _kl_calibration_lookup(combined: pd.DataFrame, axis: str) -> dict[tuple, list[tuple[float, float]]]:
    """Set A's k* curves indexed on a MEASURABLE K/L ratio rather than on thickness.

    {(route, heavy_shell, light_shell, definition): [(K/L, k*), ...]} sorted by K/L. The K/L
    value is taken under the same line definition as the k* on that row -- never a summed k*
    against a principal ratio.
    """
    indexed = index_on_kl(combined)
    column = axis.lower()
    if column not in indexed.columns:
        raise ValueError(f"unknown K/L axis {axis!r}; available: ga_k_l, as_k_l")

    lookup = {}
    group_cols = ["route", "heavy_shell", "light_shell", "definition"]
    for key, group in indexed.groupby(group_cols, sort=False):
        ordered = group.sort_values(column)
        lookup[key] = list(zip(ordered[column], ordered["k_star"]))
    return lookup


def recover_x_via_kl(
    combined: pd.DataFrame,
    axis: str = "As_K_L",
    target_thickness: float = SET_B_THICKNESS_NM,
    unknowns: "pd.DataFrame | None" = None,
) -> pd.DataFrame:
    """Recovery held out in BOTH unknowns -- the honest version of recover_x().

    `recover_x()` looks up the calibration at the Set B runs' KNOWN thickness. A real
    experimenter has no such number: thickness is exactly as unknown as composition. That round
    trip is therefore held out in x but NOT in t -- it is handed one of the two answers.

    This function removes that. For each Set B run it reads the run's OWN measured K/L ratio --
    a quantity available from the same spectrum being quantified -- looks the Set A calibration
    up at that ratio, and inverts. Neither the run's thickness nor its composition is used.

    `unknowns`, if given, REPLACES the Set B selection (thickness == target_thickness, x in
    SET_B_X_BI) with an arbitrary subset of `combined` treated as the unknown runs -- e.g. Set
    C's low-x thickness arm, to test whether this recovery generalises beyond the single
    thickness (100 nm) Set B tests at each composition. Because the function never reads a run's
    own thickness anyway (that is the whole point of it), no other change is needed to run it on
    a run at any thickness; `target_thickness` is then unused and ignored. Default (None)
    reproduces the original Set B behaviour exactly -- additive, not a rewrite.

    WHY As K/L AND NOT Ga K/L. Set C measured how much each ratio depends on composition once
    density is accounted for: Ga K/L carries a ~23% residual, As K/L ~2% (REPORT 23.5). A
    thickness proxy that also tracks composition re-introduces the very dependence it exists to
    remove -- and composition is the unknown being solved for. So As K/L by default. Walther's
    Figs 3 and 5 use Ga K/L, which his data could not have shown to be the weaker axis.

    Interpolation is linear between the two nearest calibration points, matching
    _interpolate_k_star's rationale. Measured on a held-out point (the x=0.20 100 nm run, which
    is absent from the Set A calibration): mean error 0.17%, worst 0.55% across all 16 pairs --
    negligible beside the effects under study. A local quadratic reaches 0.03%/0.10%, and the
    difference does not matter at this scale.
    """
    calibration = _kl_calibration_lookup(combined, axis)
    ratios = compute_ratios(combined).set_index("run_id")

    if unknowns is None:
        unknowns = combined[
            (combined["thickness_nm"] == target_thickness) & (combined["x_bi"].isin(SET_B_X_BI))
        ]
    measured = compute_k_star(unknowns)

    rows = []
    for _, row in measured.iterrows():
        key = (row["route"], row["heavy_shell"], row["light_shell"], row["definition"])
        # The run's own measured ratio, under this row's line definition.
        ratio_column = f"{axis}_{row['definition']}"
        if ratio_column not in ratios.columns:
            raise ValueError(f"{ratio_column!r} missing from the ratio table")
        measured_kl = ratios.at[row["run_id"], ratio_column]

        k_star_used = _interpolate_k_star(calibration[key], measured_kl)

        heavy_z, light_z = _ROUTE_ELEMENTS[row["route"]]
        recovered = _INVERSE_FORMULAS[row["route"]](
            k_star_used, ATOMIC_WEIGHTS[heavy_z], ATOMIC_WEIGHTS[light_z],
            row["i_heavy"], row["i_light"],
        )

        rows.append({
            "run_id": row["run_id"],
            "route": row["route"],
            "heavy_shell": row["heavy_shell"],
            "light_shell": row["light_shell"],
            "definition": row["definition"],
            "kl_axis": axis,
            "measured_kl": measured_kl,
            "k_star_used": k_star_used,
            "recovered_x": recovered,
            "true_x_bi": row["x_bi"],
            "error": recovered - row["x_bi"],
            # Attached for grading only, exactly like true_x_bi -- the recovery never reads it.
            "true_thickness_nm": row["thickness_nm"],
        })

    return pd.DataFrame(rows)


def _set_c_unknowns(combined: pd.DataFrame) -> pd.DataFrame:
    """Set C: x = 0.01, thickness swept 32-1024 nm -- the low-x thickness arm."""
    return combined[
        (combined["x_bi"] == SET_C_X_BI) & (combined["thickness_nm"].isin(SET_C_THICKNESSES_NM))
    ]


def write_roundtrips(combined_csv: "str | object", output_dir) -> dict:
    """Write both round trips and their summaries, so the two can be compared side by side.

    Keeping the thickness-indexed version is deliberate: the DIFFERENCE between them is itself
    a result (REPORT 25), and deleting the weaker one would destroy the comparison.

    Also writes the held-out recovery run on Set C (the low-x thickness arm) instead of Set B --
    closing a gap REPORT 23.2 notes but never itself closed: Set C informed the choice of As K/L
    over Ga K/L as the recovery axis (23% vs 2% composition residual, REPORT 23.5), but was
    structurally excluded from the Set B filter this recovery otherwise uses, so the recovery's
    OWN accuracy at x = 0.01 had only ever been demonstrated at the single thickness Set B tests
    (100 nm), never across the thickness range Set C exists to probe. `recover_x_via_kl` never
    reads a run's own thickness regardless, so running it on Set C needed no new mechanism --
    only the `unknowns` parameter to point it at a different set of rows.
    """
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    combined = pd.read_csv(combined_csv)

    written = {}
    handed = recover_x(combined)
    handed.to_csv(output_dir / "roundtrip_recovered_x.csv", index=False)
    summarize(handed).to_csv(output_dir / "roundtrip_summary.csv", index=False)
    written["handed_thickness"] = output_dir / "roundtrip_recovered_x.csv"

    set_c = _set_c_unknowns(combined)
    for axis in ("As_K_L", "Ga_K_L"):
        recovered = recover_x_via_kl(combined, axis=axis)
        path = output_dir / f"roundtrip_heldout_{axis.lower()}.csv"
        recovered.to_csv(path, index=False)
        written[axis] = path

        low_x_arm = recover_x_via_kl(combined, axis=axis, unknowns=set_c)
        low_x_path = output_dir / f"roundtrip_heldout_setc_lowx_{axis.lower()}.csv"
        low_x_arm.to_csv(low_x_path, index=False)
        written[f"{axis}_setc_lowx"] = low_x_path
    return written


def recover_x(combined: pd.DataFrame, target_thickness: float = SET_B_THICKNESS_NM) -> pd.DataFrame:
    """Held-out recovery: Set-A-calibrated k*(target_thickness), inverted against each Set B
    run's own measured intensities.

    Columns: run_id, thickness_nm, route, heavy_shell, light_shell, definition, k_star_used,
    recovered_x, true_x_bi, error (recovered_x - true_x_bi). true_x_bi is attached for grading
    only -- it plays no part in computing recovered_x (see the leakage-guard test).
    """
    calibration = _calibration_lookup(combined)

    set_b = combined[
        (combined["thickness_nm"] == target_thickness) & (combined["x_bi"].isin(SET_B_X_BI))
    ]
    # i_heavy/i_light per (run, route, shell, shell, definition), reusing kfactors' own
    # extraction rather than re-implementing shell lookups here.
    measured = compute_k_star(set_b)

    rows = []
    for _, row in measured.iterrows():
        key = (row["route"], row["heavy_shell"], row["light_shell"], row["definition"])
        k_star_used = _interpolate_k_star(calibration[key], target_thickness)

        heavy_z, light_z = _ROUTE_ELEMENTS[row["route"]]
        inverse = _INVERSE_FORMULAS[row["route"]]
        recovered = inverse(
            k_star_used, ATOMIC_WEIGHTS[heavy_z], ATOMIC_WEIGHTS[light_z],
            row["i_heavy"], row["i_light"],
        )

        rows.append({
            "run_id": row["run_id"],
            "thickness_nm": row["thickness_nm"],
            "route": row["route"],
            "heavy_shell": row["heavy_shell"],
            "light_shell": row["light_shell"],
            "definition": row["definition"],
            "k_star_used": k_star_used,
            "recovered_x": recovered,
            "true_x_bi": row["x_bi"],
            "error": recovered - row["x_bi"],
        })

    return pd.DataFrame(rows)


def summarize(recovered: pd.DataFrame) -> pd.DataFrame:
    """One row per Set B run: how the 24 recovered-x estimates for that run spread out
    around the true x_bi. mean_abs_error is the headline number; min/max show the worst-case
    disagreement, which is often more informative than the mean when a route is badly off.
    """
    rows = []
    for (run_id, true_x), group in recovered.groupby(["run_id", "true_x_bi"], sort=False):
        rows.append({
            "run_id": run_id,
            "true_x_bi": true_x,
            "n_estimates": len(group),
            "mean_recovered_x": group["recovered_x"].mean(),
            "mean_abs_error": group["error"].abs().mean(),
            "min_recovered_x": group["recovered_x"].min(),
            "max_recovered_x": group["recovered_x"].max(),
        })
    return pd.DataFrame(rows).sort_values("true_x_bi").reset_index(drop=True)
