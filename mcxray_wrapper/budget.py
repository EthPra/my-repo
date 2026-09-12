"""P4.2 -- the error budget and the measurability limit. LO4's deliverable.

THE QUESTION. LO4 asks for "the most reliable X-ray line pair". Three mechanisms have now been
quantified separately, and each one picks a different winner if read alone:

    sum peak (P3.1/P4.1)   wrecks Bi M routes, cannot touch Bi L        -> prefers Bi L
    overlap (i) (P1.3a)    costs precision on Bi La, nothing else       -> prefers Bi M
    counting (P1.3)        starves Bi K, and Ga_As at low x             -> prefers Bi L

A recommendation cannot come from any one of them. This module puts all three into ONE currency
-- absolute error on recovered composition -- adds them, and asks at what Bi content the total
exceeds a stated threshold. That crossing is the measurability limit, and the route with the
lowest limit is the answer to LO4.

THE COMMON CURRENCY, AND HOW EACH MECHANISM GETS INTO IT.

  counting    Already there. `counting.counting_uncertainty` gives sigma_x directly.

  sum peak    Already there. Re-running the recovery on as-measured intensities and differencing
              against the clean recovery gives the induced bias in x.

  overlap (i) NOT already there -- `overlap.py` reports a relative uncertainty on the Bi La peak
              AREA, which is a statement about a photon count, not about composition. It is
              converted using the sensitivity matrix P1.3 already computed:

                  sigma_x[overlap] = |d x / d ln I(Bi La)| x (excess relative uncertainty)

              where the excess is the overlap cost ABOVE the counting floor, in quadrature, so
              the photon-count part is not counted twice. This is the piece that makes the three
              comparable, and it is why P1.3 had to come first.

              The conversion is exact under the `principal` definition, where the Bi L signal IS
              Bi La. Under `summed` it is a LOWER bound: the overlap also touches the other L
              sub-lines, which this does not model. Flagged in the output, not buried.

BIAS AND VARIANCE ARE NOT ADDED BLINDLY. The sum peak is a systematic bias -- it does not average
down, and counting longer does not help. The other two are variances. They are kept in separate
columns throughout, combined as

    total = |bias| + sqrt( sigma_counting^2 + sigma_overlap^2 )

i.e. variances in quadrature, bias linearly on top. That is the conservative envelope rather than
the likeliest error, and it is stated as such. The method's OWN residual error -- what the round
trip gets wrong with no artefact at all -- is carried as a separate bias term, because a route
whose budget is dominated by its own calibration residual is failing for a different reason than
one starved of photons.

NOTHING IS DEFAULTED THAT IS NOT KNOWN. The sum-peak level, the overlap coupling and the dose are
all unsettled, so all three are SWEPT (3 x 3 x 3) and every row carries the scenario that
produced it. A recommendation that only holds in one corner of that grid is not a recommendation,
and `rank_routes` reports how often each route wins across the whole grid rather than quoting the
nominal case alone.
"""

from __future__ import annotations

import math

import pandas as pd

from mcxray_wrapper.counting import (
    DOSE_SCALES,
    FIRST_ORDER_LIMIT,
    counting_uncertainty,
    line_sensitivities,
)
from mcxray_wrapper.overlap import COUPLING_LEVELS, bi_la_uncertainty
from mcxray_wrapper.roundtrip import recover_x_via_kl
from mcxray_wrapper.spec import BI
from mcxray_wrapper.sumpeak import SENSITIVITY_LEVELS, as_measured_unknowns

# The relative precision on x that counts as "measurable". Nothing in the literature fixes this,
# so it is a stated threshold and a parameter everywhere, never a constant baked into a result.
# Retained for comparison after 2026-08-21 (below), not as the production bar.
DEFAULT_TARGET_RELATIVE = 0.10

# The ABSOLUTE precision on x that counts as "measurable" -- Walther's own stated bar: "measuring
# it precisely to 0.5 at% (for Delta x = 0.01) or better is a real challenge" (J. Microsc. 2025,
# p.2). Adopted as the PRODUCTION threshold 2026-08-21 (Ethan's decision, VERDICT_BRIEF.md
# decision 1) in preference to DEFAULT_TARGET_RELATIVE, which has no literature anchor and, being
# relative, tightens the absolute demand precisely in the low-x arm (Set C) this project adds.
DEFAULT_TARGET_ABSOLUTE = 0.01

_KEY = ["run_id", "route", "heavy_shell", "light_shell", "definition"]
_ROUTE_KEY = ["route", "heavy_shell", "light_shell", "definition"]
_SCENARIO = ["level", "coupling", "dose_scale"]


def _sumpeak_bias(combined: pd.DataFrame, levels, axis: str, **switches) -> pd.DataFrame:
    """Induced bias in recovered x per (estimate, level), plus the method's own clean residual.

    The clean residual is the error the round trip makes with no artefact present at all -- the
    calibration interpolation and whatever the k* model does not capture. Separating it matters:
    otherwise a route that is simply hard to calibrate looks like a route damaged by the sum peak.
    """
    clean = recover_x_via_kl(combined, axis=axis).set_index(_KEY)
    rows = []
    for level in levels:
        as_measured = as_measured_unknowns(combined, level, **switches)
        corrupted = recover_x_via_kl(as_measured, axis=axis).set_index(_KEY)
        for key, row in corrupted.iterrows():
            base = clean.loc[key]
            rows.append({
                **dict(zip(_KEY, key)),
                "level": level,
                "true_x_bi": float(base["true_x_bi"]),
                "recovered_x_clean": float(base["recovered_x"]),
                "bias_method": abs(float(base["error"])),
                "bias_sumpeak": abs(float(row["recovered_x"]) - float(base["recovered_x"])),
            })
    return pd.DataFrame(rows)


def _overlap_excess(combined: pd.DataFrame, couplings, dose_scale: float) -> pd.DataFrame:
    """Overlap (i)'s cost on the Bi La area, ABOVE the counting floor, per (run, coupling).

    `overlap.bi_la_uncertainty` reports the total, which already contains the photon-count term.
    Subtracting the floor in quadrature isolates the part attributable to sitting on As Ka's
    flank -- otherwise the same photons would be charged to the budget twice, once here and once
    as counting statistics.
    """
    raw = bi_la_uncertainty(combined, couplings=couplings, dose_scale=dose_scale)
    excess = (raw["relative_uncertainty"] ** 2 - raw["counting_only_relative"] ** 2)
    raw = raw.assign(excess_relative=excess.clip(lower=0.0) ** 0.5)
    return raw[["run_id", "coupling", "excess_relative", "neighbour_ratio"]]


def error_budget(
    combined: pd.DataFrame,
    levels=SENSITIVITY_LEVELS,
    couplings=COUPLING_LEVELS,
    dose_scales=DOSE_SCALES,
    axis: str = "As_K_L",
    **switches,
) -> pd.DataFrame:
    """One row per (recovered estimate, sum-peak level, overlap coupling, dose).

    Columns separate the mechanisms and then combine them, so the combination can always be
    taken apart again: sigma_counting, sigma_overlap, bias_method, bias_sumpeak, sigma_combined,
    total_error, relative_total, dominant_mechanism.
    """
    counting = counting_uncertainty(combined, dose_scales=dose_scales, axis=axis)
    counting = counting.set_index(_KEY + ["dose_scale"])

    # d x / d ln I(Bi La) -- the lever that turns an overlap cost on a peak area into an error on
    # composition. Zero for any estimate that does not use Bi La, which is exactly right: the
    # overlap then contributes nothing, by construction rather than by a hand-written rule.
    sensitivities = line_sensitivities(combined, axis=axis)
    bi_la = sensitivities[(sensitivities["atomic_number"] == BI)
                          & (sensitivities["line"] == "La")]
    bi_la = bi_la.set_index(_KEY)["sensitivity"]

    bias = _sumpeak_bias(combined, levels, axis, **switches).set_index(_KEY + ["level"])

    rows = []
    for dose in dose_scales:
        overlap = _overlap_excess(combined, couplings, dose).set_index(["run_id", "coupling"])
        for key in bi_la.index:
            run_id = key[0]
            counting_row = counting.loc[key + (dose,)]
            sigma_counting = float(counting_row["sigma_x"])
            lever = abs(float(bi_la.loc[key]))
            recovered = float(counting_row["recovered_x"])

            for coupling in couplings:
                excess = float(overlap.loc[(run_id, coupling), "excess_relative"])
                sigma_overlap = lever * excess
                sigma_combined = math.hypot(sigma_counting, sigma_overlap)

                for level in levels:
                    bias_row = bias.loc[key + (level,)]
                    bias_method = float(bias_row["bias_method"])
                    bias_sumpeak = float(bias_row["bias_sumpeak"])
                    total = bias_method + bias_sumpeak + sigma_combined

                    parts = {
                        "counting": sigma_counting,
                        "overlap_i": sigma_overlap,
                        "sum_peak": bias_sumpeak,
                        "method": bias_method,
                    }
                    dominant = max(parts, key=parts.get)

                    rows.append({
                        **dict(zip(_KEY, key)),
                        "level": level, "coupling": coupling, "dose_scale": dose,
                        "true_x_bi": float(bias_row["true_x_bi"]),
                        "recovered_x": recovered,
                        "sigma_counting": sigma_counting,
                        "sigma_overlap": sigma_overlap,
                        "bias_method": bias_method,
                        "bias_sumpeak": bias_sumpeak,
                        "sigma_combined": sigma_combined,
                        "total_error": total,
                        "relative_total": total / recovered if recovered else float("inf"),
                        "dominant_mechanism": dominant,
                        "dominant_share": parts[dominant] / total if total else 0.0,
                        # The overlap conversion is exact only for `principal` -- see the module
                        # docstring. Carried per row so a summary cannot lose it.
                        "overlap_is_lower_bound": key[4] == "summed",
                        "first_order_valid": bool(counting_row["first_order_valid"]),
                    })

    return pd.DataFrame(rows)


def _crossing(points: "list[tuple[float, float]]", target: float) -> "float | None":
    """Where a falling relative-error curve crosses `target`, interpolated log-log in x.

    `points` is [(x, relative_error), ...] sorted by x. Returns None if the curve never crosses
    inside the sampled range -- the caller reports which side it fell, rather than being handed
    an extrapolated number that looks like a measurement. Same refusal to extrapolate as
    `roundtrip._interpolate_k_star`.

    Log-log because both axes span decades and every mechanism here is close to a power law in x
    over that span; interpolating linearly across 0.01 to 0.20 would badly misplace the crossing.
    """
    for (x0, e0), (x1, e1) in zip(points, points[1:]):
        if (e0 - target) * (e1 - target) <= 0 and e0 != e1:
            if e0 <= 0 or e1 <= 0 or x0 <= 0 or x1 <= 0:
                return None
            span = (math.log(x1) - math.log(x0)) / (math.log(e1) - math.log(e0))
            return math.exp(math.log(x0) + (math.log(target) - math.log(e0)) * span)
    return None


def measurability_limit(budget: pd.DataFrame,
                        target_relative: float = DEFAULT_TARGET_RELATIVE,
                        target_absolute: "float | None" = None) -> pd.DataFrame:
    """The lowest Bi content each route can quantify, per scenario.

    Two different definitions of "measurable to X" are supported, and they are NOT the same curve
    re-scaled:

        RELATIVE (default)  crosses `relative_total` against `target_relative`. Nothing in the
                             literature fixes this magnitude -- it is a stated, arbitrary choice.
                             Because it is relative, the ABSOLUTE demand on x tightens as x shrinks,
                             which bites hardest exactly in the low-x arm (Set C) this project adds.

        ABSOLUTE             pass `target_absolute` to cross `total_error` (composition units)
                             instead. Anchored to Walther's own stated bar: "measuring it precisely
                             to 0.5 at% (for Delta x = 0.01) or better is a real challenge"
                             (J. Microsc. 2025, p.2) -- i.e. target_absolute=0.01. Behaves oppositely
                             to the relative target: lenient at low x, strict at high x.

    Only one metric is active per call; `metric` in the output records which. One row per (route,
    shell pair, definition, sum-peak level, overlap coupling, dose). A lower limit is a better
    route. Where the curve does not cross inside the sampled 0.01-0.20 range the limit is reported
    as unbracketed with the side recorded, never extrapolated:

        `below_range`  measurable at every composition sampled -- the limit is under x = 0.01
                       and this matrix cannot say where.
        `above_range`  not measurable anywhere in the range, including at x = 0.20.
    """
    metric = "absolute" if target_absolute is not None else "relative"
    value_column = "total_error" if metric == "absolute" else "relative_total"
    target = target_absolute if metric == "absolute" else target_relative

    rows = []
    group_cols = _ROUTE_KEY + _SCENARIO
    for key, group in budget.groupby(group_cols, sort=False):
        ordered = group.sort_values("true_x_bi")
        points = list(zip(ordered["true_x_bi"], ordered[value_column]))
        limit = _crossing(points, target)

        if limit is not None:
            status = "bracketed"
        elif points[0][1] <= target:
            status = "below_range"
        else:
            status = "above_range"

        rows.append({
            **dict(zip(group_cols, key)),
            "metric": metric,
            "target_relative": target,
            "x_limit": limit,
            "status": status,
            "relative_at_lowest_x": points[0][1],
            "relative_at_highest_x": points[-1][1],
            "dominant_at_lowest_x": ordered["dominant_mechanism"].iloc[0],
            "any_first_order_invalid": not bool(ordered["first_order_valid"].all()),
            "overlap_is_lower_bound": bool(ordered["overlap_is_lower_bound"].any()),
        })

    out = pd.DataFrame(rows)
    # Unbracketed-below is the best possible outcome, so it must sort FIRST, not last. Sorting on
    # x_limit alone would push those NaN rows to the bottom and invert the ranking.
    order = {"below_range": 0, "bracketed": 1, "above_range": 2}
    out["_rank"] = out["status"].map(order)
    return out.sort_values(["_rank", "x_limit"]).drop(columns="_rank").reset_index(drop=True)


def rank_routes(limits: pd.DataFrame) -> pd.DataFrame:
    """How each route fares ACROSS the whole scenario grid -- the LO4 answer.

    Quoting the best route under one set of assumptions would be worthless when none of the three
    magnitudes is known. This counts, for every route, in how many of the swept scenarios it is
    measurable at the lowest sampled composition, and its worst-case limit. A route that wins
    everywhere is a recommendation; one that wins only at the optimistic corner is not, and the
    difference is visible in `scenarios_measurable_at_low_x`.
    """
    rows = []
    for key, group in limits.groupby(_ROUTE_KEY, sort=False):
        measurable = group["status"] == "below_range"
        bracketed = group[group["status"] == "bracketed"]
        rows.append({
            **dict(zip(_ROUTE_KEY, key)),
            "n_scenarios": len(group),
            "scenarios_measurable_at_low_x": int(measurable.sum()),
            "fraction_measurable": float(measurable.mean()),
            "worst_relative_at_lowest_x": float(group["relative_at_lowest_x"].max()),
            "best_relative_at_lowest_x": float(group["relative_at_lowest_x"].min()),
            "worst_x_limit": float(bracketed["x_limit"].max()) if len(bracketed) else float("nan"),
            "dominant_mechanism": group["dominant_at_lowest_x"].mode().iloc[0],
            "any_first_order_invalid": bool(group["any_first_order_invalid"].any()),
            "overlap_is_lower_bound": bool(group["overlap_is_lower_bound"].any()),
        })
    out = pd.DataFrame(rows)
    return out.sort_values(
        ["fraction_measurable", "worst_relative_at_lowest_x"], ascending=[False, True]
    ).reset_index(drop=True)


def write_budget(combined_csv: "str | object", output_dir,
                 target_relative: float = DEFAULT_TARGET_RELATIVE,
                 target_absolute: "float | None" = DEFAULT_TARGET_ABSOLUTE,
                 also_write_relative: bool = True, **kwargs) -> dict:
    """Run the budget and write the full table, the limits and the route ranking.

    Production default (since 2026-08-21) is the ABSOLUTE threshold: `measurability_limit.csv`
    and `route_ranking.csv` are computed at `target_absolute` (Walther's own Delta x = 0.01 bar).
    Pass `target_absolute=None` to fall back to the relative-only threshold as the primary output
    instead.

    The relative-10% version is ALSO written, suffixed `_relative10`, whenever both a relative and
    an absolute target are active (`also_write_relative`, default True) -- not because it is used,
    but because the write-up's claim that the recommendation is anchor-invariant needs both
    stored as evidence, not recomputed from a throwaway script each time someone asks.
    """
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    budget = error_budget(pd.read_csv(combined_csv), **kwargs)

    written = {}
    budget_path = output_dir / "error_budget.csv"
    budget.to_csv(budget_path, index=False)
    written["error_budget"] = budget_path

    primary = measurability_limit(budget, target_relative, target_absolute)
    for name, frame in (("measurability_limit", primary), ("route_ranking", rank_routes(primary))):
        path = output_dir / f"{name}.csv"
        frame.to_csv(path, index=False)
        written[name] = path

    if also_write_relative and target_absolute is not None:
        reference = measurability_limit(budget, target_relative)
        for name, frame in (("measurability_limit_relative10", reference),
                            ("route_ranking_relative10", rank_routes(reference))):
            path = output_dir / f"{name}.csv"
            frame.to_csv(path, index=False)
            written[name] = path

    return written
