"""Stage 6b -- analytic synthesis of the Ga L + As L sum peak onto Bi Ma.

THE ARTEFACT. Two soft X-rays arriving at the detector within its resolving time are recorded
as ONE photon at their combined energy. Ga La (1.098 keV) + As La (1.282) = 2.380 keV, against
Bi Ma at 2.423 -- a 43 eV gap, confirmed from this project's own stored line energies. No
solid-state detector resolves that, so the fake counts are indistinguishable from Bi.

MC X-Ray cannot produce sum peaks (confirmed 2026-07-25), so they are synthesised analytically
onto the STORED table. Nothing is re-simulated.

WHY THIS IS A MODELLING EXERCISE, NOT A REPRODUCTION. Walther did not derive his magnitude from
a pile-up rate. His measured Bi L/M (~2:3) disagreed with his simulated one (~1:1); he assumed
the sum peak caused the gap and raised it until they agreed, arriving at 600 counts ~ 15% of the
Ga L / As L intensities. That is a quantity fitted to close a disagreement, and it is entangled
with HIS Bi M -- which differs from MC X-Ray's by a measured 1.506 +/- 0.020 (REPORT 21.1b). The
15% is therefore not portable and there is no published method to inherit. Levels are SWEPT
(0.1 / 1 / 10%), never defaulted to 15%.

FOUR MODELLING CHOICES, all exposed as parameters rather than baked in. Three were Walther's to
answer and now are not (he is unavailable until 26-28 Aug); the fourth he answered directly.
Defaults below are PROVISIONAL -- state whichever is used, and sweep it.

  1. parents=      which lines feed the pile-up
  2. basis=        what the level multiplies
  3. conserve=     whether parent lines are depleted
  4. m_band_factor whether the pile-up lands on simulated Ma or on the whole measured M band

WHERE IT IS APPLIED -- settled, not a choice. Walther: "only applied to the experimental
spectrum, not to simulations." His calibration is simulated (clean), his unknown is measured
(corrupted). So the artefact belongs on the UNKNOWN only, never on the calibration -- the
variant that does not self-cancel and therefore gives the largest induced error.

A PREDICTION WORTH RECORDING before any result: I(Ga La)/I(Bi Ma) spans 3.7 at x=0.20 to 107.7
at x=0.01. The same pile-up fraction is therefore ~20x more damaging at low Bi content, which is
precisely where the measurability question lives.
"""

from __future__ import annotations

import math

import pandas as pd

from mcxray_wrapper.ratios import INTENSITY_COLUMN
from mcxray_wrapper.spec import AS, BI, GA

# The line this project sweeps. Walther's measured ~15% is the thing being bracketed, not a
# default (CLAUDE.md).
SENSITIVITY_LEVELS = (0.001, 0.01, 0.10)

BI_M_LINE = "Ma"

# --- choice 1: which lines feed the pile-up -------------------------------------------------
#
# Every pairing of a Ga L line with an As L line lands within 59 eV of the others and within
# 43-16 eV of Bi Ma (2.423 keV):
#
#     Ga La + As La  = 1.098 + 1.282 = 2.380      Ga Lb1 + As La  = 1.122 + 1.282 = 2.404
#     Ga La + As Lb1 = 1.098 + 1.317 = 2.415      Ga Lb1 + As Lb1 = 1.122 + 1.317 = 2.439
#
# All four are unresolvable from Bi Ma and from each other, so "alpha_beta" is the physically
# complete set. "alpha_only" is what the paper states. Sweep both.
PARENT_SETS = {
    "alpha_only": {GA: ("La",), AS: ("La",)},
    "alpha_beta": {GA: ("La", "Lb1"), AS: ("La", "Lb1")},
}

# --- choice 2: what the level multiplies ----------------------------------------------------
#
# "intensity"    N = level * sqrt(I_Ga * I_As). Walther's phrasing ("15% of their line
#                intensities"). The geometric mean is used because it is symmetric in the two
#                parents and reduces to his reading when they are comparable -- his were within
#                9%, but in this project's data Ga L / As L reaches 2.0, so the choice matters.
#                Scales LINEARLY with dose.
#
# "rate_product" N = level * (I_Ga * I_As) / I_reference. The true random-coincidence form: the
#                rate goes as the product of the two count rates. Scales QUADRATICALLY with
#                dose, which is the physically distinguishing feature -- doubling the beam
#                current quadruples the pile-up. I_reference normalises the level so the two
#                bases agree on the run with the largest geometric-mean parent intensity,
#                making a swept level comparable between them.
BASES = ("intensity", "rate_product")

# --- choice 4: the M-band baseline ----------------------------------------------------------
#
# The simulation reports Bi Ma only; a detector sees the whole unresolved M band. Walther's
# relative intensities (personal communication, Aug 2026) give, for Ma1 = 100:
# Mz 1.6 + Ma2 5.2 + Mb 62.4 + Mg 5.1 = 74.3, so a measured spectrum holds 174.3 where the
# simulation holds 100.
#
# Applying the pile-up to simulated Ma alone measures it against a baseline 1.743x too small and
# so OVERSTATES the damage. Both are offered; the comparison is itself a result.
M_BAND_FACTOR_SIMULATED = 1.0
M_BAND_FACTOR_MEASURED = 1.743


def _line_intensities(run: pd.DataFrame) -> dict[tuple[int, str], float]:
    """{(Z, line): intensity} for one run."""
    return {
        (int(z), str(line).replace("Line ", "")): float(value)
        for z, line, value in zip(run["Atomic number"], run["Line"], run[INTENSITY_COLUMN])
    }


def _parent_totals(lines: dict, parents: dict, run_id: str) -> tuple[float, float]:
    """Summed Ga-side and As-side parent intensities."""
    totals = []
    for element in (GA, AS):
        total = 0.0
        for member in parents[element]:
            key = (element, member)
            if key not in lines:
                raise ValueError(f"{run_id}: parent line {member!r} missing for element {element}")
            total += lines[key]
        totals.append(total)
    return totals[0], totals[1]


def fake_counts(
    i_ga: float,
    i_as: float,
    level: float,
    basis: str = "intensity",
    reference_geometric_mean: float | None = None,
) -> float:
    """Number of pile-up events, i.e. fake Bi Ma counts. See BASES for the two forms.

    Capped at min(i_ga, i_as): each event consumes one photon from each parent, so more events
    than the scarcer parent can supply is physically impossible. Without the cap a large swept
    level would silently produce negative parent intensities under conserve=True.
    """
    if basis not in BASES:
        raise ValueError(f"basis must be one of {BASES}, got {basis!r}")

    geometric_mean = math.sqrt(i_ga * i_as)
    if basis == "intensity":
        count = level * geometric_mean
    else:
        if not reference_geometric_mean:
            raise ValueError("rate_product basis needs reference_geometric_mean")
        count = level * geometric_mean * (geometric_mean / reference_geometric_mean)

    return min(count, i_ga, i_as)


def synthesise(
    combined: pd.DataFrame,
    levels: "tuple[float, ...]" = SENSITIVITY_LEVELS,
    parents: str = "alpha_only",
    basis: str = "intensity",
    conserve: bool = True,
    m_band_factor: float = M_BAND_FACTOR_SIMULATED,
) -> pd.DataFrame:
    """Corrupt each run's Bi M (and optionally its parents) at each level; report Bi L/M.

    conserve=True removes each fake count's two parent photons from Ga L and As L, which is what
    physically happens -- one Ga La and one As La are consumed to fake one Bi Ma. Walther's
    correction moved counts both ways ("transferred 600 counts from Bi M to EACH of Ga L and
    As L"), i.e. it undid exactly this. conserve=False adds to Bi M only, which is simpler but
    leaves the parents holding photons that were counted twice.

    One row per (run, level): clean and corrupted Bi L/M, the fake count, and the settings used
    -- so a stored result always carries the modelling choices that produced it.
    """
    if parents not in PARENT_SETS:
        raise ValueError(f"parents must be one of {tuple(PARENT_SETS)}, got {parents!r}")
    parent_lines = PARENT_SETS[parents]

    work = combined.copy()
    work["_line"] = work["Line"].str.replace("Line ", "", regex=False)

    # Reference for the rate_product basis: the largest geometric-mean parent intensity in the
    # table, so `level` means the same thing under either basis at that run.
    reference = 0.0
    if basis == "rate_product":
        for _, run in work.groupby("run_id", sort=False):
            i_ga, i_as = _parent_totals(_line_intensities(run), parent_lines, "reference scan")
            reference = max(reference, math.sqrt(i_ga * i_as))

    rows = []
    for run_id, run in work.groupby("run_id", sort=False):
        lines = _line_intensities(run)
        i_ga, i_as = _parent_totals(lines, parent_lines, run_id)

        bi_m_simulated = lines[(BI, BI_M_LINE)]
        if bi_m_simulated <= 0:
            raise ValueError(f"{run_id}: Bi {BI_M_LINE} is zero -- cannot form a ratio")
        bi_m_baseline = bi_m_simulated * m_band_factor

        # Bi L, principal definition: the numerator of the diagnostic, untouched by this artefact
        # (the sum peak lands at 2.4 keV; Bi La is at 10.84).
        bi_l = lines[(BI, "La")]

        meta = {c: run.iloc[0][c] for c in ("x_bi", "thickness_nm") if c in run.columns}

        for level in levels:
            fake = fake_counts(i_ga, i_as, level, basis, reference or None)
            corrupted_m = bi_m_baseline + fake
            rows.append({
                "run_id": run_id, **meta, "level": level,
                "i_ga_parent": i_ga, "i_as_parent": i_as,
                "bi_m_simulated": bi_m_simulated,
                "bi_m_baseline": bi_m_baseline,
                "fake_counts": fake,
                "fake_fraction_of_bi_m": fake / bi_m_baseline,
                "bi_l_m_clean": bi_l / bi_m_baseline,
                "bi_l_m_corrupted": bi_l / corrupted_m,
                "i_ga_after": i_ga - fake if conserve else i_ga,
                "i_as_after": i_as - fake if conserve else i_as,
                "parents": parents, "basis": basis, "conserve": conserve,
                "m_band_factor": m_band_factor,
            })

    return pd.DataFrame(rows)


def apply_to_intensities(
    combined: pd.DataFrame,
    level: float,
    parents: str = "alpha_only",
    basis: str = "intensity",
    conserve: bool = True,
    m_band_factor: float = M_BAND_FACTOR_SIMULATED,
    run_ids: "set[str] | None" = None,
) -> pd.DataFrame:
    """Return an AS-MEASURED copy of the stored table: what a real detector would have recorded.

    `run_ids` LIMITS which runs are affected, and defaults to every run. Getting this wrong is
    easy and quiet: applying the artefact to the whole table corrupts the CALIBRATION runs as
    well as the unknown, and the two then partly cancel -- at x=0.20 they cancel almost exactly,
    so the artefact appears to do nothing at all. Walther settled the correct treatment: the
    sum peak belongs on the experimental spectrum only, "not to simulations". His calibration
    came from simulation (clean) and his unknown from measurement (corrupted). Pass the unknown
    runs' ids -- see `as_measured_unknowns()`.

    `synthesise()` reports what the artefact does to the Bi L/M ratio. This instead rewrites the
    intensities themselves, so the whole downstream pipeline -- ratios, k*, the thickness proxy,
    the recovery -- can be run on it unchanged. That is what makes the SECOND-ORDER effect
    visible.

    Two hits, from one leak:

      Direct   -- fake counts land on Bi Ma, so the Bi signal reads high.
      Indirect -- each event consumed one Ga L and one As L photon, so those lines read LOW.
                  As K/L is the thickness proxy (roundtrip.recover_x_via_kl), so depleting As L
                  raises that ratio and the foil looks THICKER than it is. The wrong thickness
                  selects the wrong k*, which moves the recovered composition again -- on top of
                  the direct error, and possibly against it.

    Only conserve=True produces the indirect hit; conserve=False leaves the parents untouched and
    models the direct one alone. Depletion is shared across a parent element's lines in
    proportion to their intensity, since a pile-up event consumes whichever photon arrived.

    Returns a copy with the same columns and row count as `combined` -- deliberately
    interchangeable with the real table, so nothing downstream needs to know it is synthetic.
    """
    if parents not in PARENT_SETS:
        raise ValueError(f"parents must be one of {tuple(PARENT_SETS)}, got {parents!r}")
    parent_lines = PARENT_SETS[parents]

    out = combined.copy()
    out["_line"] = out["Line"].str.replace("Line ", "", regex=False)

    reference = 0.0
    if basis == "rate_product":
        for _, run in out.groupby("run_id", sort=False):
            i_ga, i_as = _parent_totals(_line_intensities(run), parent_lines, "reference scan")
            reference = max(reference, math.sqrt(i_ga * i_as))

    for run_id, run in out.groupby("run_id", sort=False):
        if run_ids is not None and run_id not in run_ids:
            continue  # a calibration run: leave it exactly as simulated
        lines = _line_intensities(run)
        i_ga, i_as = _parent_totals(lines, parent_lines, run_id)
        fake = fake_counts(i_ga, i_as, level, basis, reference or None)

        in_run = out["run_id"] == run_id

        # Direct hit: the band factor first (what the detector sees), then the fake counts.
        bi_m = (out["Atomic number"] == BI) & (out["_line"] == BI_M_LINE)
        out.loc[in_run & bi_m, INTENSITY_COLUMN] = \
            lines[(BI, BI_M_LINE)] * m_band_factor + fake

        if not conserve:
            continue

        # Indirect hit: remove the consumed parent photons, split across each element's parent
        # lines in proportion to how many photons each contributed.
        for element, total in ((GA, i_ga), (AS, i_as)):
            for member in parent_lines[element]:
                share = lines[(element, member)] / total if total else 0.0
                mask = in_run & (out["Atomic number"] == element) & (out["_line"] == member)
                out.loc[mask, INTENSITY_COLUMN] = lines[(element, member)] - fake * share

    return out.drop(columns="_line")


def as_measured_unknowns(combined: pd.DataFrame, level: float, **kwargs) -> pd.DataFrame:
    """The correct application: corrupt the UNKNOWN runs only, leave the calibration simulated.

    Set A is the calibration (known composition, swept thickness) and Set B the unknowns. Walther
    applied his sum-peak correction "only ... to the experimental spectrum, not to simulations",
    so the artefact belongs on Set B alone.

    This is not a detail. Corrupting both sides makes the error largely SELF-CANCEL -- measured
    on this project's data, applying it to the whole table leaves recovered x at x=0.20 visibly
    unchanged, because calibration and unknown shift together. Applying it correctly is the
    variant that does NOT cancel, and therefore the one that shows the real damage.
    """
    from mcxray_wrapper.matrix import SET_B_THICKNESS_NM, SET_B_X_BI

    unknowns = combined[
        (combined["thickness_nm"] == SET_B_THICKNESS_NM) & (combined["x_bi"].isin(SET_B_X_BI))
    ]
    return apply_to_intensities(combined, level, run_ids=set(unknowns["run_id"]), **kwargs)


def write_sumpeak(combined_csv: "str | object", output_dir, **kwargs) -> object:
    """Read the stored table, synthesise the sum peak, write it into output_dir."""
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    result = synthesise(pd.read_csv(combined_csv), **kwargs)
    out = output_dir / "sumpeak_sensitivity.csv"
    result.to_csv(out, index=False)
    return out
