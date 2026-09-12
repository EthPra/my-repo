# CLAUDE.md — MC X-Ray Automation Wrapper (GaAsBi EDXS dissertation)

Project-level context, loaded every session. **These instructions override default behaviour.**

> Governance, the trap list, the locked design and the run matrix are load-bearing and kept
> inline — they are reference material and do not go stale. Status does, so it lives in the
> phase's own entry-point file: **`NEXT_SESSION_PROMPT.md`** during the write-up,
> `WORKPLAN_17AUG.md` for the build history. (`CURRENTLY_RELEVANT.md` held that role until
> 2026-08-17; archived, no successor — do not recreate it.) Detail and history live in
> `REPORT.md` (technical). ⚠ `REPORT_PLAIN_ENGLISH.md` is its non-technical companion but
> **contains superseded numbers — never draft or quote from it.**

## strict rule

Always call me by my name: 'Ethan' every time you respond

## What this is

A Python wrapper around **MC X-Ray Lite v1.7.1** (`console_mcxray_lite_x64.exe`, Windows x64)
that automates **21** Monte Carlo simulations of STEM-EDXS spectra from free-standing
GaAs₁₋ₓBiₓ foils and collects the per-line X-ray intensities into one provenance-tracked table.

The science: whether Bi content *x* can be quantified from X-ray line-intensity ratios despite
two peak overlaps (As Kα ≈ Bi Lα; **Ga Lα + As Lα pile-up ≈ Bi Mα**). The simulation knows the
true *x*, so quantification error is measurable against ground truth. Future work of Walther,
*J. Microscopy* 2025 (DOI 10.1111/jmi.70058) — the central paper, in this folder.

## ▶ Read first

**The project is in its write-up phase** (dissertation due Sun 14 Sep 2026, 14:00). In that order:

- **`NEXT_SESSION_PROMPT.md`** — the entry point. What we are doing, how we work now, what is
  left. Read it before assuming anything below about progress is current.
- **`DISSERTATION_FRAMEWORK.md`** — the plan: chapter map, page budgets, cross-cutting write-up
  rules (§5), the five-day schedule with its checkpoints and cut line (§8).
- **`DISSERTATION_NUMBERS.md`** — the number sheet. **Every value quoted in the dissertation comes
  from here or from the CSV it names.** §10 is a blacklist of retired numbers.
- **`writeupTODO.md`** — everything that must be *declared* in the methodology, entries marked
  closed or live.
- **`dissertation/`** — the chapter skeletons; `dissertation/README.md` indexes them.
- **`REPORT.md`** — the full technical history and evidence, section by section. Source material,
  not a template. ⚠ Do not draft from `REPORT_PLAIN_ENGLISH.md` — superseded numbers.
- **`WORKPLAN_17AUG.md`** — Ethan's build-phase plan with per-LO status. History now; the source
  for Ch1.5's plan-vs-actual.

## Governance — hard boundaries (unchanged, non-negotiable)

- **Mechanical work is Claude's:** scripting, templating, parsing, file handling, tests.
- **Scientific judgement is Ethan's:** ratio→composition inversion, k\*-factor calibration, the
  hypothesis verdict, interpretation.
- **Physical quantities are never invented.** Line energies, densities, atomic weights,
  cross-sections: from a cited source in this repo, or Claude stops and asks. Values in code
  carry a source comment; anything uncited is marked `# pending verification vs primary source`.
- **The pipeline stores raw, unprocessed intensities.** No ratios, k-factors, or corrections
  inside the run loop — ever. Derived numbers (Stage 6+) read the stored table and must be
  re-derivable without re-running simulations.

## Trap list — every one fails SILENTLY (keep, verbatim discipline)

1. **Lengths are ÅNGSTRÖMS**, not nm (the v1.6 manual is wrong). 100 nm = 1000 in the `.sam`. A
   nm value runs fine and simulates a 10× thinner foil.
2. **Composition is WEIGHT fraction** (`WeightFraction`), not atomic. Atomic fractions run fine
   and simulate the wrong alloy.
3. **`UserDefinedMassDensity` must be set** (g/cm³). Leaving 0 auto-mixes *elemental* Ga/As/Bi
   densities — wrong for a covalent zinc-blende alloy, ~15–20% too dense, no error raised.
   **Production model: ρ(x) = 5.32 + 1.86·x** (Walther's endpoints GaAs 5.32 / GaBi 7.18,
   2026-07-19). The golden `.sam` carries **5.34** (the old paper model 5.32 + 0.20·x, kept only
   to reproduce the golden set). Golden files are ground truth for FORMAT ONLY, never physics.
4. **`DetectorDiffusionLenght`** is misspelled in the format. Reproduce verbatim; correcting it
   breaks parsing.
5. **CRLF with trailing CRLF at EOF** on the four Ethan-authored inputs (`.sim/.sam/.mic/.par`);
   the two vendor files (`.mdl/.rp`) are **LF-only**, and output CSVs are **LF-only**. Per-file
   fidelity — do not harmonise.
6. Output CSV: separator is **`", "`** (comma+space); rows end in a **trailing comma** (10 real
   fields, not 11); `Line` labels have **trailing spaces**; key on **`Atomic number`**
   (31/33/83), never `Index Atom`.
7. The `.mic` has **no window field** — ATW (Al 0.02 µm + Moxtek 0.3 µm) is compiled in, and
   windowless is confirmed impossible. A `window` param is metadata that writes nothing.
8. The manual is out of date. **Golden files > documentation** for format; **neither** is
   authoritative for physics values (cited primary sources only).
9. **"18 lines" is not a row count** — it is the lines cross-checked against Walther's Table 1.
   The intensity CSV has **21 rows** (Ga 6, As 6, Bi 9). Assert counts from the file, not prose.

## Locked experimental design (do not make configurable without an explicit decision)

| Parameter | Value |
|---|---|
| Beam energy | 200 keV |
| Trajectories | 10⁶ (thin foils ≤16 nm: 10⁷, for <1% MC noise — Walther) |
| Geometry | Free-standing foil, single BOX, no substrate, vacuum both sides |
| Take-off angle | `DetectorTOA=25`, azimuth `DetectorPitch=90` |
| Detector | Si:Li, crystal thickness **0.5 cm** (production; golden was 0.3), `DetectorNoise=50` |
| Photon count / channel width | `PhotonNbr=10000`, `EnergyChannelWidth=5` |

**Run matrix — 21 runs.** The first 15 are frozen against the Aims & Objectives form and must
stay so: every result derived before 2026-08-13 came from exactly that list, and `matrix.py`
keeps `production_matrix()` returning it unchanged.
- **Set A (thickness):** x = 0.2; thickness ∈ {2,4,8,16,32,64,128,256,512,1024} nm = 10 runs.
- **Set B (composition):** 100 nm; x ∈ {0.01, 0.02, 0.05, 0.1, 0.2} = 5 runs.
- **Set C (low-x thickness arm, added 2026-08-13 on Ethan's sign-off):** x = 0.01;
  thickness ∈ {32,64,128,256,512,1024} nm = 6 runs. `extension_matrix()`; `full_matrix()` is all 21.
  Added because ρ·t proved insufficient as an absorption coordinate — the cross could not predict
  its own interior (REPORT §23).

## Where it stands (summary — see the phase file named below)

**Do not trust a status summary in this file.** This section went stale twice — it once described
the sum peak as unbuilt weeks after it was done, and it later described the verdict as outstanding
for two and a half weeks after Ethan reached it. Everything below the "Locked experimental design"
heading is reference material and stays true; this section is the one that rots.

**The project is in its write-up phase. There is no build or simulation work left.**

- **Build complete** (2026-08-17): 21 production runs, **304 tests** green, **28** CSVs in
  `Sim\Aggregated\`, **6** figures in `Sim\Figures\`. `run_analysis.py` regenerates every derived
  output; `python -m figures.make_all` renders the figures.
- **Verdict reached 2026-08-22** — `VERDICT_BRIEF.md`, `PRESENTATION_SCRIPT.md` §C. **Done, not
  outstanding.**
- **Presentation delivered and closed** 2026-08-24 — `PENDING_EDITS.md`.
- **Remaining: the dissertation, due Sun 14 Sep 2026, 14:00.** Read `NEXT_SESSION_PROMPT.md`
  first — it is the write-up phase's entry point and names the reading order.
  `DISSERTATION_FRAMEWORK.md` is the plan (chapter map, page budgets, five-day schedule);
  `DISSERTATION_NUMBERS.md` is the number sheet **every quoted value must come from**;
  `writeupTODO.md` is what the methodology must declare; `dissertation/` holds the chapter
  skeletons.

⚠ **Never lift a number from prose — including from `REPORT.md` and from this file.** Go to
`DISSERTATION_NUMBERS.md`, which carries each value's file, column and filter, or to the CSV.

## MC X-Ray interface

- **Input:** six files per run — `.sim` (master), `.sam` (specimen), `.mic` (beam+detector),
  `.par` (counts, output basename), `.mdl`/`.rp` (pass through unchanged). Flat in `C:\MCXRAY\Sim\`.
- **Command:** `console_mcxray_lite_x64.exe --simulation-file <run_id>.sim`, cwd = the Sim folder.
- **Primary output:** `<run_id>_XrayIntensities.csv` — the per-line intensity table (the analysis
  input, not the broadened spectrum). ~19 output files per run; keep all.

## Engineering conventions

- Python ≥3.10. **The pipeline (`mcxray_wrapper/`) is pandas + stdlib**, with two declared
  exceptions, both Ethan's decision and both to be stated in the write-up:
  **numpy + scipy** in `absorption.py` (non-linear curve fitting and root-finding, 2026-08-16),
  and **matplotlib** confined entirely to the separate top-level `figures/` package, which the
  pipeline never imports. Windows-safe (`pathlib`, explicit encodings/newlines).
- pytest; golden regression tests are the acceptance criterion. Small, boring functions;
  comments cite sources for constants.
- **`Golden/` is read-only** — never regenerate, edit, or clean it.
- Output stays flat in `C:\MCXRAY\Sim\Results\` (run_id prefixes prevent collisions). Inputs are
  written flat in `C:\MCXRAY\Sim\` at run time (where `.sim` child-resolution expects them).
  Aggregated deliverables go in `C:\MCXRAY\Sim\Aggregated\`, never inside `Results\`; figures
  go in `C:\MCXRAY\Sim\Figures\`.
- **Anything the project depends on lives in the repo, never a session scratchpad.** The Stage 3
  executor was lost that way (REPORT §22); the artifact page source nearly went the same way.

## Working style

- When a design question isn't answered here or in the task: **ask, don't decide.**
- Surface anomalies immediately (a diff that won't classify, an unexpected column) — an anomaly
  usually means the interface understanding is wrong, which is what the golden tests exist to catch.
- Prefer a small validated step over a large unvalidated one.

## Open questions (still live — do not resolve unilaterally)

- **Secondary fluorescence** in MC X-Ray? (Walther's own sims exclude it.) Never asked.


## Traps that stay true regardless (don't re-learn these)

- Lengths in the `.sam` are **Ångströms**, not nm. 100 nm → 1000.
- Composition is **weight** fraction, not atomic.
- `UserDefinedMassDensity=0` triggers a wrong auto-mix silently — always set it.
- `DetectorDiffusionLenght` misspelling is load-bearing. Never "correct" it.
- CRLF with trailing CRLF at EOF on the four Ethan-authored inputs; `.mdl`/`.rp` are LF-only;
  output CSVs are LF-only. Per-file fidelity — do not harmonise.
- Output CSV separator is `", "`; rows end in a trailing comma; key on **`Atomic number`**.
- Golden files are ground truth for **format**, never for **physics values**.
- `Golden/` is read-only.
- **"18 lines" is not a row count** — the intensity CSV has **21 rows** (Ga 6, As 6, Bi 9).
  Assert counts from the file, not prose.