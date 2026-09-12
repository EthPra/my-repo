"""Stage 7 (part 1) -- empirical k*-factors from known ground truth.

Reads the STORED aggregated table (Stage 5's combined_intensities.csv), same as ratios.py.
Never touches the simulator and never re-derives anything ratios.py doesn't already expose --
this module only adds the twelve CROSS-element pairs Walther's Eqs (2), (4), (9) need
(Bi-vs-Ga, Bi-vs-As, Ga-vs-As), which are different from the three SAME-element pairs already
stored in diagnostic_ratios.csv (Ga K/L, As K/L, Bi L/M).

Because this project simulates every run, x_bi is exact ground truth (typed into RunSpec), not
inferred. That means k* can be solved directly and algebraically at any run, rather than built
up from a decomposed thin-foil-k x escape-fraction model:

    Bi vs Ga (Eq 2):  k*_Bi,Ga = x           * (A_Bi/A_Ga) * (I_Ga/I_Bi)
    Bi vs As (Eq 4):  k*_Bi,As = x/(1-x)     * (A_Bi/A_As) * (I_As/I_Bi)
    Ga vs As (Eq 9):  k*_Ga,As = 1/(1-x)     * (A_Ga/A_As) * (I_As/I_Ga)

(Walther, T. (2025), J. Microscopy, DOI 10.1111/jmi.70058.)

THE "A" CURRENCY QUESTION -- RESOLVED. A is the ATOMIC WEIGHT; rho is the atomic density, a
separate quantity that does not enter Eqs (2), (4) or (9) at all. (Walther, T., personal
communication to E. Pratt, August 2026.) The paper's own gloss -- "A for atomic densities" --
had conflated the two, which is why this was carried as an open question rather than assumed:
the standard Cliff-Lorimer weight-fraction conversion the equations are built on needs only
atomic weight, and that is what the answer confirms.

So ATOMIC_WEIGHTS from spec.py (IUPAC/CIAAW 2024) is the correct currency, not a placeholder,
and the k* values this module produces are correct in ABSOLUTE terms -- not merely up to a
factor that cancels. Two consequences worth keeping in view:

  - Comparison against Walther's published k* numbers is now legitimate. It has been done for
    the pair his Figure 4 quotes: k*_BiL,AsK = 2.490 +/- 0.071 (his), 2.4161 +/- 0.005 across
    Set A (ours) -- 3.0% low, 1.04 sigma, i.e. just outside his quoted uncertainty. Obtained at
    a 6.2% higher density (5.692 vs his 5.36 at x=0.2) and by direct algebraic solve rather
    than his k x escape-fraction decomposition. See REPORT.md 18.
  - A still cancels in any calibrate-then-invert round trip that uses the same route and the
    same A both times, so nothing computed before 2026-08-13 changes value. The answer removes
    a caveat; it does not invalidate a number.

Three consumers, mirroring the run matrix's own cross shape:

  calibration_curves() -- Set A only (x=0.2 fixed, thickness swept). One empirical k*(t) curve
    per pair per line-definition, read directly off simulation, analogous to Walther's Figs 3-5
    but without the k x escape-fraction decomposition.

  composition_curves() -- Set B only (t=100nm fixed, x swept). The mirror of the above along
    the run matrix's other axis: one k*(x) curve per pair per line-definition. Persisted in its
    own right because the SHAPE of any drift is diagnostic -- monotonic drift is systematic
    (absorption tracking the density change across Set B), scatter is Monte-Carlo noise, and the
    summary below cannot tell those apart.

  invariance_check() -- the summary over composition_curves(). k* is supposed to be a property
    of the instrument and line pair, not of composition -- Walther's equations already carry the
    composition dependence explicitly in the prefactor (x, x/(1-x), 1/(1-x)), so dividing that
    out should leave a constant. If a route's k* still drifts across x, the prefactor doesn't
    fully capture what MC X-Ray simulates. This matters beyond bookkeeping: the inversion
    assumes k* is transferable from a calibration to an unknown, and if k* depended on x you
    would need x to obtain the k* that yields x. This is the check that it doesn't.

NOT computed here: no inversion of an unknown spectrum back to x (that's the held-out round
trip, calibrate on Set A / test on Set B, built next), no sum-peak synthesis.
"""

from __future__ import annotations

import pandas as pd

from mcxray_wrapper.matrix import (
    SET_A_THICKNESSES_NM,
    SET_A_X_BI,
    SET_B_THICKNESS_NM,
    SET_B_X_BI,
)
from mcxray_wrapper.ratios import INTENSITY_COLUMN, SHELLS
from mcxray_wrapper.spec import AS, ATOMIC_WEIGHTS, BI, GA

ELEMENT_SYMBOLS = {GA: "Ga", AS: "As", BI: "Bi"}


def _k_star_bi_ga(x: float, a_bi: float, a_ga: float, i_bi: float, i_ga: float) -> float:
    """Eq 2: k*_Bi,Ga = x * (A_Bi/A_Ga) * (I_Ga/I_Bi)."""
    return x * (a_bi / a_ga) * (i_ga / i_bi)


def _k_star_bi_as(x: float, a_bi: float, a_as: float, i_bi: float, i_as: float) -> float:
    """Eq 4: k*_Bi,As = [x/(1-x)] * (A_Bi/A_As) * (I_As/I_Bi)."""
    return (x / (1.0 - x)) * (a_bi / a_as) * (i_as / i_bi)


def _k_star_ga_as(x: float, a_ga: float, a_as: float, i_ga: float, i_as: float) -> float:
    """Eq 9: k*_Ga,As = [1/(1-x)] * (A_Ga/A_As) * (I_As/I_Ga)."""
    return (1.0 / (1.0 - x)) * (a_ga / a_as) * (i_as / i_ga)


# label, heavy element Z, heavy element's shells, light element Z, light element's shells, formula
#
# Bi K is included because LO3 names "bismuth K, L, and M lines relative to either gallium K or
# L or arsenic K or L as reference". It is expected to fail as a quantification route -- Bi Ka1
# is 0.405 detected photons at 2 nm, and k* for a Bi K route runs ~100x the Bi L value because
# k* goes as 1/I_Bi -- but quantifying that failure answers LO3, whereas omitting it leaves the
# objective silently unaddressed. Plot Bi K routes on their own scale; they will not share an
# axis with the Bi L/M routes.
ROUTES = (
    ("Bi_Ga", BI, ("K", "L", "M"), GA, ("K", "L"), _k_star_bi_ga),
    ("Bi_As", BI, ("K", "L", "M"), AS, ("K", "L"), _k_star_bi_as),
    ("Ga_As", GA, ("K", "L"), AS, ("K", "L"), _k_star_ga_as),
)

_METADATA_COLUMNS = ("run_id", "x_bi", "thickness_nm")


def _shell_value(run_lines: dict[str, float], element: int, shell: str,
                  definition: str, run_id: str) -> float:
    """Principal or summed intensity for one shell, mirrors ratios.py's _shell_intensity."""
    members, principal = SHELLS[element][shell]
    if principal not in run_lines:
        raise ValueError(f"{run_id}: principal line {principal!r} missing for shell {shell!r}")
    if definition == "principal":
        return run_lines[principal]
    return sum(run_lines.get(m, 0.0) for m in members)


def compute_k_star(combined: pd.DataFrame) -> pd.DataFrame:
    """One row per (run, route, heavy shell, light shell, line definition).

    Columns: run_id, x_bi, thickness_nm, route, heavy_shell, light_shell, definition,
    i_heavy, i_light, k_star. i_heavy/i_light are exposed (not just consumed internally) so
    a held-out inversion (roundtrip.py) can reuse the same intensity extraction and apply a
    DIFFERENT k* -- one calibrated elsewhere -- without duplicating the shell-lookup logic.
    x=0 or x=1 rows are skipped (Bi_Ga's and Ga_As's formulas divide by x or by (1-x)
    respectively) -- none of the 15 production runs hit either edge.
    """
    work = combined.copy()
    work["_line"] = work["Line"].str.replace("Line ", "", regex=False)

    rows = []
    for run_id, run in work.groupby("run_id", sort=False):
        meta = {col: run.iloc[0][col] for col in _METADATA_COLUMNS if col in run.columns}
        x = meta["x_bi"]

        lines_by_element = {
            z: dict(zip(run[run["Atomic number"] == z]["_line"],
                        run[run["Atomic number"] == z][INTENSITY_COLUMN]))
            for z in (GA, AS, BI)
        }

        for label, heavy_z, heavy_shells, light_z, light_shells, formula in ROUTES:
            for heavy_shell in heavy_shells:
                for light_shell in light_shells:
                    for definition in ("principal", "summed"):
                        i_heavy = _shell_value(
                            lines_by_element[heavy_z], heavy_z, heavy_shell, definition, run_id)
                        i_light = _shell_value(
                            lines_by_element[light_z], light_z, light_shell, definition, run_id)
                        if i_heavy == 0:
                            raise ValueError(
                                f"{run_id}: {label} {heavy_shell} has zero intensity "
                                "-- k* undefined"
                            )
                        k_star = formula(
                            x, ATOMIC_WEIGHTS[heavy_z], ATOMIC_WEIGHTS[light_z],
                            i_heavy, i_light,
                        )
                        rows.append({
                            **meta,
                            "route": label,
                            "heavy_shell": heavy_shell,
                            "light_shell": light_shell,
                            "definition": definition,
                            "i_heavy": i_heavy,
                            "i_light": i_light,
                            "k_star": k_star,
                        })

    return pd.DataFrame(rows)


def calibration_curves(combined: pd.DataFrame) -> pd.DataFrame:
    """Set A only (x=0.2 fixed, thickness swept) -- one empirical k*(t) curve per pair.

    Sorted by thickness so each (route, heavy_shell, light_shell, definition) group reads
    top-to-bottom as a curve, the shape Walther's Figs 3-5 show.
    """
    set_a = combined[
        (combined["x_bi"] == SET_A_X_BI) & (combined["thickness_nm"].isin(SET_A_THICKNESSES_NM))
    ]
    k_star = compute_k_star(set_a)
    return k_star.sort_values(
        ["route", "heavy_shell", "light_shell", "definition", "thickness_nm"]
    ).reset_index(drop=True)


def composition_curves(combined: pd.DataFrame) -> pd.DataFrame:
    """Set B only (t=100nm fixed, x swept) -- one empirical k*(x) curve per pair.

    The composition-axis mirror of calibration_curves(). Sorted by x_bi so each
    (route, heavy_shell, light_shell, definition) group reads top-to-bottom as a curve, which
    is what makes a systematic drift distinguishable from scatter by eye.
    """
    set_b = combined[
        (combined["thickness_nm"] == SET_B_THICKNESS_NM) & (combined["x_bi"].isin(SET_B_X_BI))
    ]
    k_star = compute_k_star(set_b)
    return k_star.sort_values(
        ["route", "heavy_shell", "light_shell", "definition", "x_bi"]
    ).reset_index(drop=True)


def invariance_check(combined: pd.DataFrame) -> pd.DataFrame:
    """Does k* stay constant across composition? The summary over composition_curves().

    One row per (route, heavy_shell, light_shell, definition), with the k* values seen across
    the 5 Set B compositions and a spread statistic: (max - min) / mean. A route/pair close to
    0 is behaving as Walther's equations assume; a large value means the x (or x/(1-x)) prefactor
    isn't fully capturing what MC X-Ray simulates for that pair.

    Sorted worst-first, so the routes that fail the assumption are the ones you read first.
    """
    k_star = composition_curves(combined)

    rows = []
    group_cols = ["route", "heavy_shell", "light_shell", "definition"]
    for key, group in k_star.groupby(group_cols, sort=False):
        values = group["k_star"]
        mean = values.mean()
        spread = (values.max() - values.min()) / mean if mean != 0 else float("inf")
        rows.append({
            **dict(zip(group_cols, key)),
            "n_points": len(values),
            "k_star_mean": mean,
            "k_star_min": values.min(),
            "k_star_max": values.max(),
            "relative_spread": spread,
        })
    return pd.DataFrame(rows).sort_values("relative_spread", ascending=False).reset_index(drop=True)


def write_calibration(combined_csv: "str | object", output_dir) -> object:
    """Read Stage 5's combined table, compute the Set A k*(t) curves, write them into output_dir.

    Mirrors ratios.write_ratios -- same read-the-stored-table-only discipline, one file out.
    """
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    combined = pd.read_csv(combined_csv)
    cal = calibration_curves(combined)
    out = output_dir / "kstar_calibration_setA.csv"
    cal.to_csv(out, index=False)
    return out


def write_composition_curves(combined_csv: "str | object", output_dir) -> object:
    """Read Stage 5's combined table, compute the Set B k*(x) curves, write them into output_dir."""
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    combined = pd.read_csv(combined_csv)
    curves = composition_curves(combined)
    out = output_dir / "kstar_composition_setB.csv"
    curves.to_csv(out, index=False)
    return out


def write_invariance(combined_csv: "str | object", output_dir) -> object:
    """Read Stage 5's combined table, compute the Set B invariance summary, write it out.

    Written separately from write_composition_curves so each file has one job: the curves are
    the evidence, this is the verdict on them.
    """
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    combined = pd.read_csv(combined_csv)
    summary = invariance_check(combined)
    out = output_dir / "kstar_invariance_setB.csv"
    summary.to_csv(out, index=False)
    return out
