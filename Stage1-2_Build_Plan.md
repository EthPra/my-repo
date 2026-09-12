# Plan — Modules 1 & 2 of the MC X-Ray wrapper

*Stage 1 (input generator) + Stage 2 (output parser). Written against the corrected ρ=5.34
golden set. Supersedes the original build prompt wherever they conflict.*

## Context

The GaAsBi EDXS project needs to run ~24 MC X-Ray simulations and collect per-line X-ray
intensities into one provenance-tracked table. Nothing can sweep until the two lowest layers
are trustworthy: generating the six input files a run needs, and parsing the one output file
that matters. Both silent-killer traps this project fears (nm-in-Å-field, atomic-fraction-in-
weight-fraction-field) live in Module 1 and produce plausible output when wrong, so the
acceptance test is a golden regression diff against a real, verified run rather than unit tests.

This session builds **only** Modules 1 and 2 plus their two golden tests and `REPORT.md`.
No executor, matrix, aggregation, ratios, or windowless mechanism.

## Step 0 — golden set validation (already run; becomes a test)

**Passed:** six inputs + CSV present; no BOM; `.sam` has `UserDefinedMassDensity=5.34`;
`.par` has `BaseFileName=Results/GaAsBi_100nm_x010_ATW_rho534`, matching the CSV stem;
CSV is LF-only, 21 rows.

**Density correction confirmed honoured — evidence stated.** The claim rests on comparing two
output files that were read directly: `Results\GaAsBi_100nm_x010_ATW_val_XrayIntensities.csv`
(density-0) against `Results\GaAsBi_100nm_x010_ATW_rho534_XrayIntensities.csv` (ρ=5.34).
The comparison is controlled, also established from the files: the two runs' `.sam` differ in
exactly one line (`UserDefinedMassDensity` 0 → 5.34; 335 → 338 bytes, +3 = that edit) and their
`.par` only in `BaseFileName` (297 → 300 bytes, +3 = `val` → `rho534`). Generated→Emitted
transmission in the ρ=5.34 run rose by +0.0145 (Ga Lα, 1.098 keV), +0.0257 (As Lα, 1.282 keV),
+0.0127 (Bi Mα, 2.423 keV), against +0.0006 (Ga Kα1, 9.251 keV) and +0.0011 (Bi Lα, 10.84 keV).

What carries the claim is the **paired difference**: every delta positive — less absorption at
the correct lower density — and ordered by how absorbed the line is. The qualitative pattern
alone would prove nothing, since a density-0 run also absorbs soft lines and passes hard ones;
this could not be established from the ρ=5.34 run in isolation.

**Two findings, both resolved with Ethan:**

1. **`.mdl` and `.rp` are LF-only, not CRLF** — they are unmodified vendor files (mtime =
   install date); the four Ethan authored are CRLF. The exe read both conventions in the same
   successful run, so line endings are *not* load-bearing — a fidelity detail, not a silent
   killer. **Rule: per-file fidelity taken from each golden file, no blanket rule.**
   "CRLF on every generated file" was the contradiction and is dropped.
2. **`Golden/outputs/*_Options.txt` carries the `_val` (density-0) stem.** Ethan is replacing
   it with the `_rho534` one. Content impact nil (the two are byte-identical — `Options.txt`
   has no specimen density line), but the provenance label is wrong. **No test reads
   `Options.txt`, so this blocks nothing in Modules 1–2.**

Open, non-blocking: `archive/density0_control/` (per golden README) does not exist. The
density-0 *outputs* survive in the live `Results\` under the `_val` stem; its *inputs* do not —
`Sim\GaAsBi_val.sam` was edited in place to 5.34. Flag in `REPORT.md`, don't act.

## Layout

```
mcxray_wrapper/__init__.py
mcxray_wrapper/spec.py       RunSpec + locked constants + derived quantities
mcxray_wrapper/inputgen.py   RunSpec + target_dir -> six files
mcxray_wrapper/parser.py     _XrayIntensities.csv -> DataFrame
tests/conftest.py            golden path fixtures
tests/diffreport.py          classified diff machinery (also runnable to emit REPORT.md text)
tests/test_golden_set.py     Step 0, as a standing test
tests/test_inputgen.py       Test 1a structural + Test 1b value accountability
tests/test_parser.py         Test 2
conftest.py                  repo root, so `mcxray_wrapper` imports under pytest
REPORT.md
```

pandas + stdlib only. No `pyproject.toml` — a root `conftest.py` is enough for imports.
`Golden/` keeps its on-disk capitalisation.

**Boundary.** The repo lives *inside* the install, at `C:\MCXRAY\Sim\Wrapper`. The original
"nothing under `C:\MCXRAY\`" rule was written assuming otherwise. Correct reading:
**reads from `C:\MCXRAY\Sim\` and `Results\` are fine; writes outside `Wrapper\` are not.**
`Golden/` is read-only. The generator's target directory is always an explicit argument with
no default — at Stage 3 it will be `C:\MCXRAY\Sim\` itself, but that is not this session.

## Module 1 — `spec.py`

`RunSpec(run_id: str, x_bi: float, thickness_nm: float, n_electrons: int, window: str = "ATW")`.

`__post_init__`: `window != "ATW"` → `NotImplementedError` (no window field exists in the
`.mic` at all; ATW is a compiled-in default — settability is spike (i), not ours). Validate
`0 <= x_bi <= 1`, `thickness_nm > 0`, `n_electrons > 0`.

Derived, each a small function with a source comment:
- `atomic_fractions()` → `{31: 0.5, 33: (1-x)/2, 83: x/2}`, assert sums to 1
- `weight_fractions()` → `wᵢ = aᵢMᵢ / ΣaⱼMⱼ`
- `mass_density()` → `5.32 + 0.20·x` (Walther 2025 Fig. 3 caption)
- `thickness_angstrom()` → `thickness_nm * 10` — **Å, not nm**

Locked constants (module-level, commented as locked-by-design): beam 200 keV, `DetectorTOA=25`,
`DetectorPitch=90`, `DetectorNoise=50`, `PhotonNbr=10000`, `EnergyChannelWidth=5`,
`WindowNbr=64` (**energy windows, NOT the detector window**), single BOX region.

`ATOMIC_WEIGHTS = {31: 69.723, 33: 74.9216, 83: 208.9804}` — marked
`# pending verification vs primary source (NIST/IUPAC) before final write-up`.

## Module 1 — `inputgen.py`

`generate_inputs(spec: RunSpec, target_dir: Path, golden_dir: Path) -> dict[str, Path]`.
Target dir is an explicit argument — no default anywhere near `C:\MCXRAY\`; never writes into
`Golden/`. Files are written as `<run_id>.{sim,sam,mic,par,mdl,rp}`.

**Three templated, three copied.** Templated files get their line ending *detected from their
own golden template*, not hardcoded:

| file | action | substitutions |
|---|---|---|
| `.sim` | template | 5 child refs + `map=` → `<run_id>.<ext>` |
| `.sam` | template | 3 × `WeightFraction`, `UserDefinedMassDensity`, `RegionParameters` Zmax |
| `.par` | template | `BaseFileName=Results/<run_id>`, `ElectronNbr` |
| `.mic` | byte copy | none — but assert locked constants present and correct |
| `.mdl` | byte copy | none (stays LF) |
| `.rp` | byte copy | none (stays LF) |

Line-oriented rewriter: decode ascii, split preserving endings, replace only known keys, rejoin.
Everything unrecognised passes through byte-for-byte, including `DetectorDiffusionLenght`.

Specific care:
- `WeightFraction` lines are **positionally tied** to the preceding `AtomicNumber` — track the
  last-seen Z and write that element's fraction. Error if golden's element set ≠ spec's.
- `RegionParameters`: replace **only the 6th token** textually; leave the five lateral-extent
  tokens as their original strings so they can't drift. Assert golden's Zmin is `0.000000`.

Number formatting (verified to reproduce golden byte-for-byte):
- `WeightFraction` → `f"{w:.6f}"`
- `RegionParameters` Zmax → `f"{z:.6f}"` (100 nm → `1000.000000`)
- `UserDefinedMassDensity` → `f"{ρ:.6f}".rstrip("0").rstrip(".")` → `5.34`.
  **Not `.2f`** — that reproduces golden but silently collapses Set B's x=0.002 and x=0.0002 to `5.32`.
- `ElectronNbr` → plain int

## Module 2 — `parser.py`

`parse_xray_intensities(path: Path, run_id: str) -> pd.DataFrame`, one row per (line, region).

Read with `dtype=str, skipinitialspace=True` (separator is `", "`), then convert explicitly with
`pd.to_numeric(..., errors="raise")` — non-numeric is an **error**, never a silent NaN. Assert the
trailing 11th field is empty and drop it; assert exactly the 10 known columns after stripping.
Strip whitespace from `Line` ("Line La " → "Line La"). Map `Atomic number` → `Element`
(31/33/83), raising on any unknown Z rather than producing NaN. Key on **`Atomic number`**,
never `Index Atom`.

Columns out: `run_id`, then the file's 10 in original order, with `Element` inserted after
`Atomic number`. All four intensity columns preserved — the pairwise differences carry physics
(Generated→Emitted = specimen self-absorption; Emitted→Emitted Detected = window + detector).

**No ratios, k-factors, or derived quantities.** Hard architectural rule.

## Tests

**`test_golden_set.py` (Step 0):** presence, no BOM, per-file line endings asserted from the
files (CRLF+trailing for `.sim/.sam/.mic/.par`; LF-only for `.mdl/.rp`), `.sam` density 5.34,
`.par` stem matches the CSV filename, CSV LF-only. Any `*_Options.txt` present must match the
stem — currently red until the file is swapped; that is the correct signal.

**`test_inputgen.py`** — generate with `run_id="GaAsBi_100nm_x010_ATW_rho534"`, `x_bi=0.1`,
`thickness_nm=100`, `n_electrons=100000`, `window="ATW"` into `tmp_path`; compare **by role, not
filename**.

- *Test 1a — structural, zero tolerance:* same line count; same field names in the same order;
  same line-ending convention as that file's golden; every non-parameterised line byte-for-byte;
  a field in one and not the other is a FAIL. `.mic/.mdl/.rp` must be byte-identical entirely.
- *Test 1b — value accountability:* every delta on a parameterised field classified as
  **(1) intended** / **(2) formatting-only** / **(3) documented deviation** / **(4) unexplained → FAIL**.
  Category 3 is whitelisted to `WeightFraction` within **1e-4 absolute** only; any other field
  claiming it fails. Passes only when 1a is clean and 4 is empty.

Expected report for this spec — **6 intended + 2 documented, nothing else**:

```
.sim  [1 INTENDED]  specimen/model/microscope/parameters/map/results
                    GaAsBi_val.<ext> -> GaAsBi_100nm_x010_ATW_rho534.<ext>   (6 lines)
.sam  [3 DOCUMENTED] WeightFraction Z=31  0.441135 -> 0.441144  (+9e-06)
      [3 DOCUMENTED] WeightFraction Z=83  0.132233 -> 0.132224  (-9e-06)
      [ok] WeightFraction Z=33, UserDefinedMassDensity, RegionParameters identical
.par  [ok] BaseFileName, ElectronNbr identical
.mic .mdl .rp  [ok] byte-identical
```

A density delta here would be a **defect** — golden now reads 5.34 and so do we.

**`test_parser.py`** — every expected literal below was read from the golden file, not from a
reference table or this plan's prose:

- 21 rows; (element, line) set = Ga×6 (Ka1,Ka2,Kb1,Kb2,La,Lb1), As×6 (same),
  Bi×9 (Ka1,Ka2,Kb1,Kb2,La,Lb1,Lb2,Lg,Ma)
- energy spot-checks: Bi La `10.84`, Bi Ma `2.423` (~4 s.f. — **not** 10.839)
- all intensity columns numeric and **non-negative, never strictly positive**; Ga Kb2 is
  legitimately all-zero with efficiency `0.999731` and must survive
- `Detector efficiency` ∈ [0, 1]; `Line` values carry no trailing space; `run_id` present
- round-trip: `to_csv` → `read_csv` → `assert_frame_equal`

## Verification

1. `python -m pytest tests/ -v` from `C:\MCXRAY\Sim\Wrapper` — all green except the known
   `Options.txt` stem check until the file is swapped.
2. `python -m tests.diffreport` — prints the classified diff; **zero category-4 entries** is the
   Module 1 gate.
3. Confirm `Golden/` mtimes are unchanged (read-only respected) and nothing was written under
   `C:\MCXRAY\Sim\` outside `Wrapper\`.
4. `REPORT.md`: what was built, Step 0 result, the classified diff, the parsed 21-row table,
   and the open items (`Options.txt` stem, missing `archive/density0_control/`, atomic-weight
   deviation, `.mdl`/`.rp` LF finding for the docs to absorb).
