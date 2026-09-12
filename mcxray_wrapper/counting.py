"""P1.3 -- counting statistics, propagated all the way through to recovered composition.

WHAT THIS ANSWERS. Every uncertainty quoted so far has been about MODELLING: the sum peak's
magnitude, the overlap coupling, the line definition. None of them is about the simplest limit of
all -- a spectrum contains a finite number of photons, and at x = 0.01 the stored Bi La is ~116
detected photons and Bi Ma ~76. Nothing in the pipeline has modelled that. This does.

WHY IT MATTERS FOR LO4. The measurability limit is set by whichever mechanism is largest at low
x, and until now that was assumed to be an overlap. It is worth stating the expectation before
the numbers: on the 15 Aug evidence, noise at x = 0.01 runs ~3.4% against a 1% sum peak's ~97%
error on Bi M routes -- so this is expected to be the LESSER mechanism by an order of magnitude,
inverting what was assumed on 13 Aug. An expectation recorded before measurement, not after.

HOW THE PROPAGATION IS DONE. Not by resampling. Each detected line count N_i is an independent
Poisson variable, so Var(ln N_i) = 1/N_i, and the recovered composition's variance is

    sigma_x^2 = SUM_i  S_i^2 / N_i        with  S_i = d(x_recovered) / d(ln N_i)

The sensitivities S_i are obtained by perturbing ONE line at a time and re-running the actual
recovery (`roundtrip.recover_x_via_kl`) -- a central difference in log-intensity. That choice is
deliberate and buys three things a hand-written analytic formula would not:

  * It captures the INDIRECT path automatically. Noise on As Ka1 and As La moves the As K/L
    thickness proxy, which selects a different k*, which moves x again -- the same second-order
    route `sumpeak.apply_to_intensities` opens through parent depletion. Nobody has to remember
    to include it.
  * It handles CORRELATION correctly. As Ka1 appears both in the Bi_As route and in the thickness
    proxy, so those two contributions are not independent. Differentiating the whole chain with
    respect to the underlying counts gets the cross-term right by construction; adding two
    separately-computed sigmas in quadrature would not.
  * S_i is a LOG-derivative, so it is scale-free. The sensitivities are computed once and every
    dose is then free -- sigma scales as 1/sqrt(dose) with no re-differentiation.

It is a first-order propagation, which is the standard treatment and is accurate while the
relative errors are small. At the weakest line in the matrix (Bi Ka1) they are not small, and
that is flagged in the output rather than hidden -- see `counting_uncertainty`'s
`first_order_valid` column.

WHERE THE NOISE IS APPLIED. To the UNKNOWN runs only, never to the Set A calibration -- the same
rule `sumpeak.as_measured_unknowns` enforces, and for the same reason. Walther's calibration was
simulated and his unknown measured. Applying noise to both sides would let it partly cancel and
would understate the limit. (The calibration carries Monte-Carlo noise of its own, from 10^6
trajectories; that is a different and much smaller quantity, and it is not modelled here.)
"""

from __future__ import annotations

import math

import pandas as pd

from mcxray_wrapper.matrix import SET_B_THICKNESS_NM, SET_B_X_BI
from mcxray_wrapper.ratios import INTENSITY_COLUMN
from mcxray_wrapper.roundtrip import recover_x_via_kl

# Walther's acquisition -- 1 nA x 715.5 s live -- against this project's stored 100 s basis.
# Identical to overlap.WALTHER_DOSE_SCALE; kept here as its own name so the two modules can be
# read independently, and asserted equal in the tests so they can never drift apart.
WALTHER_DOSE_SCALE = 7.155

# Swept, not fixed. The stored basis, Walther's actual acquisition, and a 10x longer count --
# enough to show the sqrt(dose) scaling and to answer "would counting longer fix it?".
DOSE_SCALES = (1.0, WALTHER_DOSE_SCALE, 10.0 * WALTHER_DOSE_SCALE)

# Step for the central difference in ln(intensity). Small enough that second-order curvature is
# negligible, large enough to stay well clear of float64 cancellation: the recovery's own
# arithmetic is ~1e-16 relative, so a 1e-4 step leaves ~12 significant figures in the difference.
RELATIVE_STEP = 1e-4

# Above this relative uncertainty a first-order propagation is no longer trustworthy -- the
# distribution of a ratio with a noisy denominator becomes visibly skewed and sigma stops
# describing it. Reported as a flag, never silently corrected.
FIRST_ORDER_LIMIT = 0.30

# The columns identifying one recovered-composition estimate.
_KEY = ["run_id", "route", "heavy_shell", "light_shell", "definition"]


def unknown_run_ids(combined: pd.DataFrame) -> set:
    """The Set B runs -- the unknowns. Noise is applied to these and to nothing else."""
    unknowns = combined[
        (combined["thickness_nm"] == SET_B_THICKNESS_NM) & (combined["x_bi"].isin(SET_B_X_BI))
    ]
    return set(unknowns["run_id"])


def _stripped_lines(combined: pd.DataFrame) -> pd.Series:
    return combined["Line"].str.replace("Line ", "", regex=False)


def _indexed(recovered: pd.DataFrame) -> pd.Series:
    return recovered.set_index(_KEY)["recovered_x"]


def line_sensitivities(combined: pd.DataFrame, axis: str = "As_K_L",
                       relative_step: float = RELATIVE_STEP) -> pd.DataFrame:
    """d(recovered x) / d(ln N) for every line, against every recovered estimate.

    One row per (recovered estimate, perturbed line). A line the estimate does not depend on
    gets a sensitivity of exactly zero, which is informative in itself -- it says the noise on
    that line cannot reach this route by any path, direct or through the thickness proxy.

    All five Set B runs are perturbed together in a single pass per line. That is safe because
    `recover_x_via_kl` treats each unknown run independently: it reads that run's own ratios and
    its own intensities against a calibration built from Set A alone. So one call yields the
    sensitivity for every run at once, and the whole matrix costs 2 x (number of lines) recovery
    passes rather than 2 x (lines) x (runs).
    """
    unknowns = unknown_run_ids(combined)
    if not unknowns:
        raise ValueError("no Set B runs in the table -- nothing to put noise on")

    stripped = _stripped_lines(combined)
    line_keys = sorted({(int(z), str(l))
                        for z, l in zip(combined["Atomic number"], stripped)})

    # Stored counts per (run, line), for the variance term later.
    counts = {(run_id, int(z), str(l)): float(v) for run_id, z, l, v in
              zip(combined["run_id"], combined["Atomic number"], stripped,
                  combined[INTENSITY_COLUMN])}

    step = math.log1p(relative_step)
    in_unknowns = combined["run_id"].isin(unknowns)

    frames = []
    for z, line in line_keys:
        mask = in_unknowns & (combined["Atomic number"] == z) & (stripped == line)
        if not mask.any():
            continue

        shifted = []
        for sign in (+1.0, -1.0):
            scaled = combined.copy()
            scaled.loc[mask, INTENSITY_COLUMN] = \
                scaled.loc[mask, INTENSITY_COLUMN] * math.exp(sign * step)
            shifted.append(_indexed(recover_x_via_kl(scaled, axis=axis)))

        sensitivity = ((shifted[0] - shifted[1]) / (2.0 * step)).rename("sensitivity")
        frame = sensitivity.reset_index()
        frame["atomic_number"] = z
        frame["line"] = line
        frame["stored_counts"] = [counts.get((r, z, line), 0.0) for r in frame["run_id"]]
        frames.append(frame)

    return pd.concat(frames, ignore_index=True)


def counting_uncertainty(combined: pd.DataFrame, dose_scales: "tuple[float, ...]" = DOSE_SCALES,
                         axis: str = "As_K_L", **kwargs) -> pd.DataFrame:
    """Poisson uncertainty on recovered x, per estimate, per dose.

    sigma_x = sqrt( SUM_i S_i^2 / N_i ), N_i = stored_i x dose_scale. Because sigma goes as
    1/sqrt(dose), the whole dose sweep comes from one set of sensitivities.

    `dominant_line` and `dominant_share` name the single line carrying the largest share of the
    variance. That is the actionable number for LO4: it says which line a longer count would
    actually help, and it is usually not the one being quantified.
    """
    sensitivities = line_sensitivities(combined, axis=axis, **kwargs)
    baseline = recover_x_via_kl(combined, axis=axis).set_index(_KEY)

    rows = []
    for key, group in sensitivities.groupby(_KEY, sort=False):
        base = baseline.loc[key]
        # Lines with no counts cannot contribute noise. A line with no counts AND a non-zero
        # sensitivity would be a contradiction (the recovery cannot depend on a line it never
        # saw), so it is raised rather than dropped.
        live = group[group["stored_counts"] > 0]
        dead = group[(group["stored_counts"] <= 0) & (group["sensitivity"] != 0.0)]
        if len(dead):
            raise ValueError(
                f"{key}: sensitivity to a line with zero counts -- {list(dead['line'])}"
            )

        for dose in dose_scales:
            counts = live["stored_counts"] * dose
            contributions = live["sensitivity"] ** 2 / counts
            total = float(contributions.sum())
            sigma = math.sqrt(total)
            top = contributions.idxmax()

            recovered = float(base["recovered_x"])
            rows.append({
                **dict(zip(_KEY, key)),
                "dose_scale": dose,
                "true_x_bi": float(base["true_x_bi"]),
                "recovered_x": recovered,
                "sigma_x": sigma,
                "relative_sigma": sigma / recovered if recovered else float("inf"),
                "dominant_line": f"{live.at[top, 'atomic_number']} {live.at[top, 'line']}",
                "dominant_share": float(contributions[top] / total) if total else 0.0,
                "n_lines_contributing": int((contributions > 0).sum()),
                "first_order_valid": (sigma / recovered if recovered else float("inf"))
                                     <= FIRST_ORDER_LIMIT,
            })

    return pd.DataFrame(rows)


def dose_for_target(uncertainty: pd.DataFrame, target_relative: float = 0.10) -> pd.DataFrame:
    """The dose each estimate would need to reach `target_relative` precision on x.

    sigma goes as 1/sqrt(dose), so dose_needed = dose x (relative_sigma / target)^2. Reported
    relative to Walther's own acquisition as well, because "40x Walther's count time" is a
    statement an examiner can weigh and "dose_scale = 286" is not.

    This is what turns counting statistics from a caveat into a design answer: a route that needs
    a plausible extra count time is limited by dose, and one that needs a thousandfold is limited
    by physics.
    """
    if target_relative <= 0:
        raise ValueError(f"target_relative must be positive, got {target_relative}")

    out = uncertainty.copy()
    out["target_relative"] = target_relative
    factor = (out["relative_sigma"] / target_relative) ** 2
    out["dose_needed"] = out["dose_scale"] * factor
    out["dose_vs_walther"] = out["dose_needed"] / WALTHER_DOSE_SCALE
    out["already_met"] = out["relative_sigma"] <= target_relative
    return out


def summarise_by_route(uncertainty: pd.DataFrame) -> pd.DataFrame:
    """Mean and worst relative sigma per (route family, Bi line, definition, composition, dose).

    Grouped so the LO4 question -- which line pair survives at low x -- reads straight off the
    table, with x on the rows rather than averaged away. Averaging over composition would hide
    the entire effect: the whole point is that the limit is composition-dependent.
    """
    grouped = uncertainty.groupby(
        ["dose_scale", "true_x_bi", "route", "heavy_shell", "definition"], sort=False
    )["relative_sigma"]
    out = grouped.agg(mean_relative_sigma="mean", worst_relative_sigma="max",
                      best_relative_sigma="min", n_estimates="size").reset_index()
    return out.sort_values(
        ["dose_scale", "true_x_bi", "mean_relative_sigma"]
    ).reset_index(drop=True)


def write_counting(combined_csv: "str | object", output_dir, target_relative: float = 0.10,
                   **kwargs) -> dict:
    """Run the propagation and write the sensitivity matrix, the budget and the route summary."""
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    combined = pd.read_csv(combined_csv)

    uncertainty = counting_uncertainty(combined, **kwargs)
    written = {}
    for name, frame in (
        ("counting_line_sensitivities", line_sensitivities(combined, **kwargs)),
        ("counting_uncertainty", dose_for_target(uncertainty, target_relative)),
        ("counting_by_route", summarise_by_route(uncertainty)),
    ):
        path = output_dir / f"{name}.csv"
        frame.to_csv(path, index=False)
        written[name] = path
    return written
