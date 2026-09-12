# `golden/` — reference set

**Read-only.** Never edit, regenerate, or "clean up" anything in this directory.

## What this is

One matched pair: the six input files that were actually fed to MC X-Ray, and the outputs that run actually produced. Verified byte-for-byte as the files that ran — not reconstructed, not retyped.

- **Run:** GaAs₀.₉Bi₀.₁ free-standing foil, 100 nm, 200 keV, 10⁵ electrons, 25° take-off, ATW window
- **Executable:** `console_mcxray_lite_x64.exe` (MC X-Ray Lite v1.7.1), invoked as
  `console_mcxray_lite_x64.exe --simulation-file GaAsBi_val.sim` from `C:\MCXRAY\Sim\`
- **Output stem:** `GaAsBi_100nm_x010_ATW_rho534`

## What it authorises, and what it does not

**Authorises: format and field semantics.** Field names, ordering, units (lengths in **Ångströms**), fraction type (**weight**, not atomic), the misspelled `DetectorDiffusionLenght`, CRLF line endings with a trailing CRLF at EOF, the output CSV's `", "` separator and trailing comma. MC X-Ray consumed these files and emitted line energies agreeing with Walther (2025) Table 1 — that is what this set proves.

**Does NOT authorise physics values.** Those come from cited primary sources. Two values in here are known to be imperfect:

1. **Composition (`WeightFraction`)** — `0.441135 / 0.426632 / 0.132233`. The 6th decimal place does not reproduce from any real atomic-weight set. IUPAC-derived values are `0.441144 / 0.426632 / 0.132224`; the deviation is ±9×10⁻⁶, compensating between Ga and Bi with As identical, and both sets sum to exactly 1.000000. It is transcription residue — ~2×10⁻⁵ relative, physically negligible. **The generator emits the IUPAC values; this delta is a documented deviation, not a defect to match.**
2. Nothing else. `UserDefinedMassDensity=5.34` is correct (see below).

## Density — read this before touching anything

The **original** validation run carried `UserDefinedMassDensity=0`, which makes MC X-Ray auto-mix from elemental densities. Measured from the two runs, that produced **ρ ≈ 6.12–6.16 g/cm³** against the true 5.34 — about **15% too dense**. The rule was identified as volume-additive (1/ρ = Σwᵢ/ρᵢ, predicting 6.148); mass-weighted linear (6.344) is ruled out. The rule is standard and correctly implemented — it is simply the wrong rule for a zinc-blende compound, whose open structure puts GaAs at 5.32 g/cm³ despite both elemental constituents being denser.

This set is the **corrected** run: `UserDefinedMassDensity=5.34` (ρ(x) = 5.32 + 0.20·x; anchors 5.34 at x=0.1, 5.36 at x=0.2, Walther 2025 Fig. 3 caption).

The density-0 run is preserved at `archive/density0_control/`. It is the only record of the auto-mix behaviour and the sole evidence behind the 15% figure. **It is a control, not a reference.**

## Facts asserted from these files (not from prose)

- The intensity CSV has **21 rows** (Ga 6, As 6, Bi 9). "18" appears in the project docs and is *not* a row count — it is the number of lines cross-checked against Walther's Table 1.
- Line energies are reported to ~4 significant figures (Bi Lα appears as `10.84`, not `10.839`). Do not assert higher-precision literals from reference tables against this file.
- `Options.txt` echoes model, simulation, beam, and detector parameters. **It contains no specimen density line** — the only density in it (`2.33`) is the detector's silicon crystal.
- `WindowNbr=64` in the `.par` is **not** the detector window; `Options.txt` echoes it as "Number of energy windows". The detector window lives elsewhere (`Al=0.02 µm`, `Moxtek=0.3 µm`, with Be/Ti/Oil/H₂O/air all 0).

## Standing rule

**Assert from files, never from prose.** Both errors this set has caught — the density field and the "18 lines" — came from documents that recorded intent rather than the artifact. Any test, count, or value must be read from the file at the time it is written.