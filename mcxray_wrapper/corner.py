"""Is rho.t a sufficient absorption coordinate? -- the Set A vs Set C comparison.

X-ray absorption on the way out of the foil is usually treated as a function of the mass
thickness rho.t (g/cm3 x nm here): two specimens with the same rho.t are assumed to absorb
alike. If that held for GaAs(1-x)Bi(x), the run matrix's CROSS (Set A sweeps thickness at
x=0.2, Set B sweeps x at 100 nm) could predict its own interior and the low-x/high-t corner
would never need running.

Set C (x=0.01, 32-1024 nm) tests it directly. It does not hold: Bi is a heavy absorber, so the
alloy's mass attenuation coefficient moves with COMPOSITION, not only with density. Across this
comparison Bi falls from ~24% to ~1.4% of the foil's weight while the density moves only 6.6%.

This module persists that comparison, which REPORT.md 23 originally computed in a throwaway
shell command -- the same failure mode as the Set B invariance check before P0.1: a load-bearing
result that was neither stored nor tested. Reads the STORED ratio table; never re-simulates and
never recomputes a ratio (that is ratios.py's job).

TWO COMPARISONS, deliberately kept separate -- they answer different questions and neither is
sufficient alone:

  compare_arms()      matches on rho.t. Isolates the residual that density does NOT explain,
                      because rho.t is held equal by construction. This is the "is rho.t
                      sufficient" test proper.
  matched_thickness() matches on geometry. Assumption-free -- no interpolation, no model. Here
                      rho.t differs by a constant -6.2% at every point, so an effect that GROWS
                      with thickness cannot be a density artefact.

Ga K/L carries a ~23% residual at matched rho.t; As K/L carries ~2%. As K/L therefore responds
to composition almost entirely THROUGH density, which rho.t already captures, and Ga K/L does
not. That matters wherever a K/L ratio is used as a thickness proxy (Walther's Figs 3-5), and
it is why roundtrip.py should index on As K/L. REPORT.md 23.5.

Not asserted here: the mechanism. Ga La (1.098 keV) and As La (1.282 keV) sit differently
against Bi's absorption structure, but attributing the asymmetry to specific edges needs cited
mass attenuation coefficients this project does not hold (CLAUDE.md: never invent physics).
"""

from __future__ import annotations

import pandas as pd

RHO_T_COLUMN = "rho_t"

# The three diagnostics, both line definitions. Defaults for the comparison functions.
RATIO_COLUMNS = (
    "Ga_K_L_principal", "Ga_K_L_summed",
    "As_K_L_principal", "As_K_L_summed",
    "Bi_L_M_principal", "Bi_L_M_summed",
)

# The two thickness arms of the production matrix.
REFERENCE_X_BI = 0.20  # Set A
TEST_X_BI = 0.01       # Set C

_METADATA_COLUMNS = ("run_id", "x_bi", "thickness_nm", "mass_density_g_cm3")


def rho_t_table(ratios: pd.DataFrame) -> pd.DataFrame:
    """Add the rho.t column. The single place that product is defined."""
    for column in ("mass_density_g_cm3", "thickness_nm"):
        if column not in ratios.columns:
            raise ValueError(f"ratio table is missing {column!r}")
    out = ratios.copy()
    out[RHO_T_COLUMN] = out["mass_density_g_cm3"] * out["thickness_nm"]
    return out


def _arm(ratios: pd.DataFrame, x_bi: float) -> pd.DataFrame:
    """One composition arm, sorted by rho.t."""
    arm = ratios[ratios["x_bi"] == x_bi]
    if arm.empty:
        raise ValueError(f"no runs at x_bi={x_bi} in the ratio table")
    return arm.sort_values(RHO_T_COLUMN).reset_index(drop=True)


def _interpolate(points: list[tuple[float, float]], target: float) -> float:
    """Linear interpolation between the two points bracketing `target`.

    Raises outside the range rather than extrapolating -- extrapolation is a different and
    riskier claim, and this comparison exists precisely to test a prediction, so a silently
    extrapolated prediction would defeat the point. Mirrors roundtrip._interpolate_k_star.
    """
    for (x0, y0), (x1, y1) in zip(points, points[1:]):
        if x0 <= target <= x1:
            if x1 == x0:
                return y0
            return y0 + (y1 - y0) * (target - x0) / (x1 - x0)
    raise ValueError(
        f"rho_t {target:.1f} is outside the reference arm's range "
        f"({points[0][0]:.1f}-{points[-1][0]:.1f}) -- would be extrapolation"
    )


def compare_arms(
    ratios: pd.DataFrame,
    reference_x: float = REFERENCE_X_BI,
    test_x: float = TEST_X_BI,
    columns: "tuple[str, ...] | None" = None,
) -> pd.DataFrame:
    """Predict the test arm from the reference arm at matched rho.t, and report the residual.

    If rho.t were a sufficient absorption coordinate, `predicted` would equal `observed` for
    every row and every ratio. One row per (test run, ratio column):

        run_id, thickness_nm, rho_t, ratio, observed, predicted, residual_pct
    """
    work = rho_t_table(ratios)
    reference = _arm(work, reference_x)
    test = _arm(work, test_x)
    columns = tuple(columns) if columns else tuple(
        c for c in RATIO_COLUMNS if c in work.columns)
    if not columns:
        raise ValueError("no ratio columns found in the table")

    rows = []
    for _, run in test.iterrows():
        for column in columns:
            curve = list(zip(reference[RHO_T_COLUMN], reference[column]))
            predicted = _interpolate(curve, run[RHO_T_COLUMN])
            observed = run[column]
            rows.append({
                "run_id": run["run_id"],
                "thickness_nm": run["thickness_nm"],
                RHO_T_COLUMN: run[RHO_T_COLUMN],
                "ratio": column,
                "observed": observed,
                "predicted": predicted,
                "residual_pct": 100.0 * (observed - predicted) / predicted,
            })
    return pd.DataFrame(rows)


def matched_thickness(
    ratios: pd.DataFrame,
    reference_x: float = REFERENCE_X_BI,
    test_x: float = TEST_X_BI,
    columns: "tuple[str, ...] | None" = None,
) -> pd.DataFrame:
    """The assumption-free companion: compare the two arms at IDENTICAL thickness.

    No interpolation and no model. rho.t differs between the arms by a constant fraction (the
    density ratio), so an effect that grows with thickness cannot be explained by density.

    One row per (shared thickness, ratio column): thickness_nm, ratio, reference, test,
    difference_pct, plus rho_t for each arm.
    """
    work = rho_t_table(ratios)
    reference = _arm(work, reference_x).set_index("thickness_nm")
    test = _arm(work, test_x).set_index("thickness_nm")
    shared = sorted(set(reference.index) & set(test.index))
    if not shared:
        raise ValueError(
            f"arms at x_bi={reference_x} and x_bi={test_x} share no thickness")
    columns = tuple(columns) if columns else tuple(
        c for c in RATIO_COLUMNS if c in work.columns)

    rows = []
    for thickness in shared:
        ref_row, test_row = reference.loc[thickness], test.loc[thickness]
        for column in columns:
            rows.append({
                "thickness_nm": thickness,
                "ratio": column,
                "reference": ref_row[column],
                "test": test_row[column],
                "difference_pct": 100.0 * (test_row[column] - ref_row[column]) / ref_row[column],
                "reference_rho_t": ref_row[RHO_T_COLUMN],
                "test_rho_t": test_row[RHO_T_COLUMN],
            })
    return pd.DataFrame(rows)


def write_corner_analysis(ratios_csv: "str | object", output_dir) -> object:
    """Read the stored ratio table, run both comparisons, write them into output_dir."""
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    ratios = pd.read_csv(ratios_csv)

    matched = compare_arms(ratios)
    matched["comparison"] = "matched_rho_t"
    geometric = matched_thickness(ratios)
    geometric["comparison"] = "matched_thickness"

    out = output_dir / "corner_rho_t_setA_vs_setC.csv"
    pd.concat([matched, geometric], ignore_index=True).to_csv(out, index=False)
    return out
