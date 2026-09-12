"""Overlap (i) -- As Ka against Bi La -- bounded, not modelled.

THE OTHER OVERLAP. The project has treated its two overlaps as a matched pair since the start.
Measured against detector resolution they are quantitatively different problems:

    sum peak     Ga La + As La 2380 eV vs Bi Ma 2423 eV   43 eV = 0.47 FWHM  -> MERGED
    overlap (i)  As Ka1 10543 eV vs Bi La 10840 eV       297 eV = 1.75 FWHM  -> RESOLVABLE

At half a linewidth the sum peak's counts are physically indistinguishable from Bi, so modelling
it as additive contamination is correct. At 1.75 linewidths As Ka and Bi La appear as two peaks
with a valley between them, and any competent fitting routine separates them. **Modelling
overlap (i) as "a fraction of As Ka is misassigned to Bi La" would therefore be wrong** -- it
assumes a blindness the detector does not have, and would overstate the damage to the one route
the sum peak cannot touch.

WHAT IT ACTUALLY COSTS is precision, not accuracy: fitting a small peak on the flank of a large
one inflates the uncertainty on the small peak's area. At x = 0.01 the As Ka1 line carries ~86x
the counts of Bi La, so a small error in the large peak is a large error in the small one.

WHY BOUNDED RATHER THAN MODELLED. A real treatment needs a peak-shape model, the low-energy tail
from incomplete charge collection, the bremsstrahlung background beneath both peaks, and a
fitting algorithm's convergence behaviour. None of those exists in this project and none is
cited anywhere in it; inventing four physical inputs at once is exactly what CLAUDE.md forbids.
So the coupling between the two peaks is left as a SWEPT parameter, on the same 0.1/1/10%
footing as the sum-peak level. One stated assumption, swept openly.

WHY IT MATTERS FOR THE CONCLUSION. The sum peak damages Bi M routes; overlap (i) would damage
Bi L routes. With only the first modelled, "Bi La / As Ka is the most robust route" is partly an
artefact of which overlap was studied. This module puts both on a level footing so that ranking
becomes a finding rather than a by-product.
"""

from __future__ import annotations

import math

import pandas as pd

from mcxray_wrapper.ratios import INTENSITY_COLUMN
from mcxray_wrapper.spec import AS, BI, GA

# --- detector resolution ---------------------------------------------------------------------
#
# FWHM(E) = sqrt(noise^2 + (2.355^2) * eps * F * E), the standard Si(Li) resolution expression.
#
#   eps = 3.86 eV   mean electron-hole pair creation energy in Si
#   F   = 0.115     Fano factor for Si
#
# Both are standard textbook values (Goldstein et al., Scanning Electron Microscopy and X-Ray
# Microanalysis) but are # pending verification vs primary source -- the book is not in this
# repo. They are NOT free parameters: the expression is checked twice below against facts this
# project already holds, and reproduces both.
ELECTRON_HOLE_PAIR_EV = 3.86   # pending verification vs primary source
FANO_FACTOR_SI = 0.115         # pending verification vs primary source

# The literature ranges for both, used by the sensitivity check in the tests. eps depends on
# temperature (Si(Li) detectors run cold, so the 77 K figure is the relevant one); F is quoted
# across a spread by different authors. The point of carrying these is that the conclusion drawn
# from the resolution model must hold across the WHOLE range, not just at the chosen value --
# otherwise a pending citation would be a pending result.
ELECTRON_HOLE_PAIR_RANGE_EV = (3.63, 3.86)   # ~300 K to the value in use
FANO_FACTOR_RANGE = (0.084, 0.130)

# Below this separation two lines merge into a single bump and cannot be fitted apart. Above it
# they show as two peaks with a valley between. The overlap (i) argument turns on which side of
# this the As Ka / Bi La pair falls.
MERGE_THRESHOLD_FWHM = 1.2

# DetectorNoise=50 is locked in the .mic by the experimental design (spec.LOCKED_DETECTOR_NOISE_EV).
DEFAULT_NOISE_EV = 50.0

MN_KA_EV = 5895.0  # the energy detector resolution is conventionally specified at

# Swept coupling between the two peaks: the share of the neighbour's counts that propagate into
# the uncertainty on the target peak's fitted area. Deliberately the same 0.1/1/10% ladder as
# sumpeak.SENSITIVITY_LEVELS, so the two overlaps are compared on identical footing.
COUPLING_LEVELS = (0.001, 0.01, 0.10)

# Walther's acquisition: 1 nA x 715.5 s live, against this project's stored 100 s basis.
WALTHER_DOSE_SCALE = 7.155


def resolution_fwhm_ev(energy_ev: float, noise_ev: float = DEFAULT_NOISE_EV,
                       electron_hole_pair_ev: float = ELECTRON_HOLE_PAIR_EV,
                       fano: float = FANO_FACTOR_SI) -> float:
    """Detector FWHM at a given photon energy.

    Two independent checks that this is not a fitted curve:
      * returns ~130 eV at Mn Ka -- the textbook specification for a good Si(Li) detector;
      * puts Bi La1/La2 (108 eV apart) at 0.63 FWHM, i.e. merged, independently reproducing
        Walther's statement that they are "usually indistinguishable".
    """
    return math.sqrt(noise_ev**2 + (2.355**2) * electron_hole_pair_ev * fano * energy_ev)


def separation_in_fwhm(energy_a_ev: float, energy_b_ev: float,
                       noise_ev: float = DEFAULT_NOISE_EV, **constants) -> float:
    """How far apart two lines are, in linewidths. Below MERGE_THRESHOLD_FWHM they merge."""
    midpoint = 0.5 * (energy_a_ev + energy_b_ev)
    return abs(energy_a_ev - energy_b_ev) / resolution_fwhm_ev(midpoint, noise_ev, **constants)


def resolution_sensitivity(energy_a_ev: float, energy_b_ev: float,
                           noise_ev: float = DEFAULT_NOISE_EV) -> pd.DataFrame:
    """Separation of two lines across the full literature range of eps and F.

    eps and F are the only uncited constants in this module. Rather than leave the conclusion
    resting on them, this walks the corners of their quoted ranges: if the pair stays resolvable
    (or stays merged) throughout, the pending citation bounds a NUMBER but not the FINDING.
    """
    rows = []
    for eps in ELECTRON_HOLE_PAIR_RANGE_EV:
        for fano in FANO_FACTOR_RANGE:
            gap = separation_in_fwhm(energy_a_ev, energy_b_ev, noise_ev,
                                     electron_hole_pair_ev=eps, fano=fano)
            rows.append({
                "electron_hole_pair_ev": eps, "fano": fano,
                "fwhm_ev": resolution_fwhm_ev(0.5 * (energy_a_ev + energy_b_ev), noise_ev,
                                              electron_hole_pair_ev=eps, fano=fano),
                "separation_fwhm": gap,
                "resolved": gap > MERGE_THRESHOLD_FWHM,
            })
    return pd.DataFrame(rows).sort_values("separation_fwhm").reset_index(drop=True)

def neighbours(combined: pd.DataFrame, element: int = BI, line: str = "La",
               within_fwhm: float = 3.0, noise_ev: float = DEFAULT_NOISE_EV) -> pd.DataFrame:
    """Every other reported line within `within_fwhm` linewidths of the target.

    Read from the stored table's own energy column rather than typed in, so the window can never
    drift from the data it describes.
    """
    work = combined.copy()
    work["_line"] = work["Line"].str.replace("Line ", "", regex=False)
    energies = work[["Atomic number", "Element", "_line", "Line energy (keV)"]].drop_duplicates()

    target = energies[(energies["Atomic number"] == element) & (energies["_line"] == line)]
    if target.empty:
        raise ValueError(f"target line {line!r} for element {element} not in the table")
    target_ev = float(target["Line energy (keV)"].iloc[0]) * 1000.0

    rows = []
    for _, row in energies.iterrows():
        energy_ev = float(row["Line energy (keV)"]) * 1000.0
        if energy_ev == target_ev:
            continue
        gap = separation_in_fwhm(energy_ev, target_ev, noise_ev)
        if gap <= within_fwhm:
            rows.append({
                "element": row["Element"], "line": row["_line"],
                "atomic_number": int(row["Atomic number"]),
                "energy_ev": energy_ev,
                "separation_ev": abs(energy_ev - target_ev),
                "separation_fwhm": gap,
                "resolved": gap > MERGE_THRESHOLD_FWHM,
            })
    return pd.DataFrame(rows).sort_values("separation_fwhm").reset_index(drop=True)


def area_uncertainty(n_target: float, n_neighbour: float, coupling: float) -> float:
    """Absolute uncertainty on a fitted peak area beside an overlapping neighbour.

        sigma = sqrt( N_target + coupling * N_neighbour )

    The first term is the target's own Poisson counting statistics -- irreducible. The second is
    the neighbour's contribution to the fit: how much of a large adjacent peak's uncertainty
    leaks into the small one. `coupling` is SWEPT, not derived, because deriving it needs peak
    shapes and tailing this project cannot cite.

    coupling = 0 reduces to pure counting statistics, which is the honest floor: even a perfectly
    isolated peak carries sqrt(N).
    """
    if coupling < 0:
        raise ValueError(f"coupling must be non-negative, got {coupling}")
    return math.sqrt(max(n_target, 0.0) + coupling * max(n_neighbour, 0.0))


def bi_la_uncertainty(
    combined: pd.DataFrame,
    couplings: "tuple[float, ...]" = COUPLING_LEVELS,
    dose_scale: float = 1.0,
    noise_ev: float = DEFAULT_NOISE_EV,
) -> pd.DataFrame:
    """Relative uncertainty on the Bi La peak area, per run, per coupling level.

    `dose_scale` multiplies every intensity before the statistics are taken -- the stored table
    is a 100 s acquisition, and WALTHER_DOSE_SCALE (7.155) puts it on his 715.5 s live footing.
    Counting statistics improve as sqrt(dose), so this is not cosmetic.

    Recovered x scales with I(Bi), so the relative uncertainty reported here propagates directly
    into a relative uncertainty on recovered composition.
    """
    work = combined.copy()
    work["_line"] = work["Line"].str.replace("Line ", "", regex=False)

    window = neighbours(combined, BI, "La", noise_ev=noise_ev)
    interferers = [(int(r.atomic_number), r.line) for r in window.itertuples()]

    rows = []
    for run_id, run in work.groupby("run_id", sort=False):
        lines = {(int(z), l): float(v) for z, l, v in
                 zip(run["Atomic number"], run["_line"], run[INTENSITY_COLUMN])}

        n_bi = lines.get((BI, "La"), 0.0) * dose_scale
        if n_bi <= 0:
            raise ValueError(f"{run_id}: Bi La has no counts -- cannot form an uncertainty")
        n_neighbour = sum(lines.get(key, 0.0) for key in interferers) * dose_scale

        meta = {c: run.iloc[0][c] for c in ("x_bi", "thickness_nm") if c in run.columns}
        for coupling in couplings:
            sigma = area_uncertainty(n_bi, n_neighbour, coupling)
            rows.append({
                "run_id": run_id, **meta, "coupling": coupling, "dose_scale": dose_scale,
                "n_bi_la": n_bi, "n_neighbour": n_neighbour,
                "neighbour_ratio": n_neighbour / n_bi,
                "sigma_counts": sigma,
                "relative_uncertainty": sigma / n_bi,
                # the irreducible floor, for separating "overlap cost" from "just too few photons"
                "counting_only_relative": math.sqrt(n_bi) / n_bi,
            })
    return pd.DataFrame(rows)


def write_overlap_bound(combined_csv: "str | object", output_dir, **kwargs) -> object:
    """Read the stored table, bound the overlap, write it into output_dir."""
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = bi_la_uncertainty(pd.read_csv(combined_csv), **kwargs)
    out = output_dir / "overlap_i_bound.csv"
    result.to_csv(out, index=False)
    return out
