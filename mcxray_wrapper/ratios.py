"""Stage 6 (part 1) -- the three diagnostic ratios.

Reads the STORED aggregated table (Stage 5's combined_intensities.csv) and computes the three
diagnostic line-intensity ratios per run. It never touches the simulator: the load-bearing
rule is that everything derived is re-derivable from the stored raw table, so if an open
atomic-data question is answered later (e.g. are Bi M-lines beyond Ma modelled) the ratios are
recomputed from the same table, not by re-running. The related La/La2 question is settled:
Walther confirmed La1/La2 bundle (~108 eV apart, one resolution element), so `La` is the whole
La bundle -- which is why the `principal` La below is a complete line, not a partial one.

The three ratios reproduce Walther's Fig. 1 (Ga K/L, As K/L, Bi L/M vs thickness). Each is
computed under BOTH line definitions and stored side by side (Ethan's decision 2026-07-25):

  principal -- the single strongest line of each shell (Ka1, La, Ma). Clean, well-separated,
    overlap-free.
  summed    -- the total intensity of all reported sub-lines in the shell. More counts, but
    pulls in lines that overlap other elements (Ga Kb on As Ka / Bi La -- Walther issue (i)).

Neither is designated correct; the choice for inversion is Stage 7, Ethan's.

Intensity source: "Intensity Emitted Detected (photons)" -- the measured-count quantity
(CLAUDE.md), which is what reproduces Walther's measured curves.

NOT computed here: no k-factors, no absorption correction, no inversion to x, no sum-peak
synthesis (that half of Stage 6 is gated on the pile-up spike). Ratios only.
"""

from __future__ import annotations

import pandas as pd

from mcxray_wrapper.spec import AS, BI, GA

INTENSITY_COLUMN = "Intensity Emitted Detected (photons)"

# Per element, the reported lines making up each shell and the shell's principal (strongest)
# line. Line labels match the parser's stripped "Line Xxx" values with the "Line " prefix
# removed. Membership is asserted against the golden 21-row line set.
SHELLS: dict[int, dict[str, tuple[list[str], str]]] = {
    GA: {"K": (["Ka1", "Ka2", "Kb1", "Kb2"], "Ka1"), "L": (["La", "Lb1"], "La")},
    AS: {"K": (["Ka1", "Ka2", "Kb1", "Kb2"], "Ka1"), "L": (["La", "Lb1"], "La")},
    # Bi K is present because LO3 names "bismuth K, L, and M lines". It is reported by MC X-Ray
    # (Ka1 77.097, Ka2 74.805, Kb1 87.335, Kb2 89.833 keV) and is non-zero in all 15 production
    # runs, so it is safe to divide by -- but it is not a usable line: 0.405 detected photons at
    # 2 nm against Bi La's 42.3, at detector efficiency 0.237 vs 0.9998. Carried so that
    # "unusable" is a measured result rather than an assertion. Not used by DIAGNOSTICS below.
    BI: {
        "K": (["Ka1", "Ka2", "Kb1", "Kb2"], "Ka1"),
        "L": (["La", "Lb1", "Lb2", "Lg"], "La"),
        "M": (["Ma"], "Ma"),
    },
}

# The three diagnostics: (label, element, numerator shell, denominator shell).
DIAGNOSTICS = (
    ("Ga_K_L", GA, "K", "L"),
    ("As_K_L", AS, "K", "L"),
    ("Bi_L_M", BI, "L", "M"),
)

# Run metadata carried through onto each ratio row, so the ratio table is self-contained
# for plotting and inversion. These are constant within a run in the aggregated table.
_METADATA_COLUMNS = (
    "run_id",
    "x_bi",
    "thickness_nm",
    "n_electrons",
    "density_model",
    "mass_density_g_cm3",
    "detector_crystal_thickness_cm",
)


def _shell_intensity(run_lines: dict[str, float], members: list[str], principal: str,
                     run_id: str, shell: str) -> tuple[float, float]:
    """Return (principal intensity, summed intensity) for one shell of one run."""
    if principal not in run_lines:
        raise ValueError(f"{run_id}: principal line {principal!r} missing for shell {shell!r}")
    principal_value = run_lines[principal]
    summed_value = sum(run_lines.get(m, 0.0) for m in members)
    return principal_value, summed_value


def compute_ratios(combined: pd.DataFrame) -> pd.DataFrame:
    """One row per run, with the three diagnostics each under both definitions.

    Columns: the run metadata, then Ga_K_L_principal, Ga_K_L_summed, As_K_L_principal,
    As_K_L_summed, Bi_L_M_principal, Bi_L_M_summed.
    """
    # Strip the "Line " prefix once, for shell matching.
    work = combined.copy()
    work["_line"] = work["Line"].str.replace("Line ", "", regex=False)

    rows = []
    for run_id, run in work.groupby("run_id", sort=False):
        row = {col: run.iloc[0][col] for col in _METADATA_COLUMNS if col in run.columns}

        for label, element, num_shell, den_shell in DIAGNOSTICS:
            el = run[run["Atomic number"] == element]
            run_lines = dict(zip(el["_line"], el[INTENSITY_COLUMN]))

            num_p, num_s = _shell_intensity(
                run_lines, *SHELLS[element][num_shell], run_id=run_id, shell=num_shell)
            den_p, den_s = _shell_intensity(
                run_lines, *SHELLS[element][den_shell], run_id=run_id, shell=den_shell)

            for kind, num, den in (("principal", num_p, den_p), ("summed", num_s, den_s)):
                if den == 0:
                    raise ValueError(
                        f"{run_id}: {label} {kind} has a zero denominator "
                        f"({den_shell} = 0) -- ratio undefined"
                    )
                row[f"{label}_{kind}"] = num / den

        rows.append(row)

    return pd.DataFrame(rows)


def write_ratios(combined_csv: "str | object", output_dir) -> object:
    """Read Stage 5's combined table, compute ratios, write ratios.csv into output_dir."""
    from pathlib import Path

    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    combined = pd.read_csv(combined_csv)
    ratios = compute_ratios(combined)
    out = output_dir / "diagnostic_ratios.csv"
    ratios.to_csv(out, index=False)
    return out
