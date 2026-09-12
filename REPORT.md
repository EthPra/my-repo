# Stage 1 + 2 build report

*Input generator and output parser, with their two golden regression tests. Built against
the corrected ρ=5.34 golden set. Scope was Modules 1 and 2 only — no executor, matrix,
aggregation, ratios, or windowless mechanism, and none were added.*

**Status: both gates pass. 109 tests, all green. Zero unexplained deltas. Generated inputs
have been fed to MC X-Ray and reproduce the golden output to within the simulator's own
run-to-run noise (§9). Every physical constant in the package is now traced to a primary
source (§10.10, §12.1). The run matrix is frozen at 15 runs against the Aims & Objectives
form (§11), and both density models are implemented and selectable (§12). **All 30 runs are
complete** — 98.9 min, zero failures, Set A physics correct under both models (§13).**

**Superseded by the 2026-07-19 supervisor meeting (§15):** the density model is now fixed
(Walther's 5.32/7.18 endpoints), the detector corrected to Si:Li 0.5 cm, and a 15-run
production set **run to completion (127 min, zero failures, physics verified — §15.7)**. The
§13 comparison runs are retained as evidence, not as results.

**Stage 5 built (§16):** the 15 runs are aggregated into one provenance-tracked raw-intensity
table (`Sim\Aggregated\`), the analysis-ready handoff into Stage 7. The run-and-store half of
the wrapper is now complete end to end.

**Stage 6 ratios built (§17):** the three diagnostic ratios (Ga K/L, As K/L, Bi L/M), each under
both line definitions, computed from the stored table → `diagnostic_ratios.csv`. Reproduces the
Fig. 1 shape (monotonic in thickness). Sum-peak synthesis (the other half of Stage 6) remains
route now decided (MC X-Ray can't build sum peaks → analytic synthesis; §17.4), buildable, not
yet built. **109 tests green, golden gate clean.**

**Headline finding, which still stands (§13.3–13.4): the density models diverge with
thickness**, from 0% at 2 nm to 8.4% at 1024 nm, because absorption depends on ρ·t rather than
ρ — a ~9% offset in *inferred thickness*. Walther's view (§15.5) is that k\* calibration
largely cancels this in the round trip; that it does not cancel *automatically* (unlike a
detector or scale error) is the point worth carrying forward.

---

## 1 — What was built

| File | Purpose |
|---|---|
| `mcxray_wrapper/spec.py` | `RunSpec` + locked constants + the four derived quantities |
| `mcxray_wrapper/inputgen.py` | `RunSpec` → the six input files, templated off golden |
| `mcxray_wrapper/parser.py` | `_XrayIntensities.csv` → tidy DataFrame |
| `tests/diffreport.py` | The classified diff machinery; runnable as `python -m tests.diffreport` |
| `tests/test_golden_set.py` | Step 0, as a standing test (9 checks) |
| `tests/test_inputgen.py` | Test 1a structural + Test 1b value accountability |
| `tests/test_parser.py` | Test 2 |
| `conftest.py`, `tests/conftest.py` | Import path; golden fixtures |

`pytest 9.1.1` was installed (it was absent); `pandas 2.3.3` was already present. No other
dependencies. Nothing was written outside `Wrapper\`.

**`RunSpec`** carries only what varies: `run_id`, `x_bi`, `thickness_nm`, `n_electrons`,
`window`, `density_model`. Everything else is locked at module level with a comment saying
so. `window` accepts `"ATW"` and raises `NotImplementedError` otherwise — and it is a genuine
no-op, because the `.mic` format documents **no window field at all**; ATW (Al 0.02 µm +
Moxtek 0.3 µm) is a compiled-in default. No mechanism was invented. `density_model` selects
between the two models of §10 and defaults to `"walther"` (§12).

**Three files are templated, three are copied.** `.sim`/`.sam`/`.par` are rewritten
line-by-line, substituting only known keys; `.mic`/`.mdl`/`.rp` are byte-copied (`.mic` is
read first to assert the locked constants and the misspelled key, then copied unmodified).
Templated files inherit their line endings from their own template, so per-file fidelity
is structural rather than enforced.

---

## 2 — Step 0: golden set validation

All checks pass. Re-run any time via `pytest tests/test_golden_set.py`.

| Check | Result |
|---|---|
| Six inputs + both outputs present | pass |
| No BOM on any input | pass |
| Line endings, per file | pass — see §6.1 |
| `.sam` has `UserDefinedMassDensity=5.34` | pass |
| `.par` stem matches the output filenames | pass (`GaAsBi_100nm_x010_ATW_rho534`) |
| Output CSV is LF-only | pass |

**Golden is provably untouched.** All six inputs and the CSV are byte-identical to the live
originals they were copied from, and every mtime in `Golden/` predates this session.

**Density correction confirmed honoured.** The claim rests on two files that were read
directly — `Results\GaAsBi_100nm_x010_ATW_val_XrayIntensities.csv` (ρ=0) against
`Results\..._rho534_XrayIntensities.csv` — not on prose and not on an inference within one
run. The comparison is controlled: the two `.sam` differ in exactly one line (335→338 bytes,
+3 = the density edit) and the two `.par` only in `BaseFileName` (297→300, +3). A single run
could not establish this, since a ρ=0 run also absorbs soft lines and passes hard ones; what
carries it is the paired difference. Generated→Emitted transmission rose by +0.0145 (Ga Lα),
+0.0257 (As Lα), +0.0127 (Bi Mα) against +0.0006 (Ga Kα1) and +0.0011 (Bi Lα) — every delta
positive, ordered by how absorbed the line is.

---

## 3 — Test 1a / 1b: the classified diff

Generated from `RunSpec(run_id="GaAsBi_100nm_x010_ATW_rho534", x_bi=0.1, thickness_nm=100,
n_electrons=100000, window="ATW")`, compared **by role, not filename**.

```
Test 1a -- structural identity (strict, zero tolerance)
  PASS  all six files: same fields, same order, same line endings,
        every non-parameterised line byte-for-byte identical.

Test 1b -- value accountability (parameterised fields only)
  --- .sim ---
  [1 INTENDED] sim:2 specimen    GaAsBi_val.sam -> GaAsBi_100nm_x010_ATW_rho534.sam
  [1 INTENDED] sim:3 model       GaAsBi_val.mdl -> GaAsBi_100nm_x010_ATW_rho534.mdl
  [1 INTENDED] sim:4 microscope  GaAsBi_val.mic -> GaAsBi_100nm_x010_ATW_rho534.mic
  [1 INTENDED] sim:5 parameters  GaAsBi_val.par -> GaAsBi_100nm_x010_ATW_rho534.par
  [1 INTENDED] sim:6 map         GaAsBi_val.mpp -> GaAsBi_100nm_x010_ATW_rho534.mpp
  [1 INTENDED] sim:7 results     GaAsBi_val.rp  -> GaAsBi_100nm_x010_ATW_rho534.rp
      reason: child-file reference follows run_id
  --- .sam ---
  [3 DOCUMENTED] sam:5 WeightFraction   0.441135 -> 0.441144
      reason: golden carries transcription residue; delta +9e-06, within 1e-04
  [3 DOCUMENTED] sam:9 WeightFraction   0.132233 -> 0.132224
      reason: golden carries transcription residue; delta -9e-06, within 1e-04

  totals: 6 INTENDED, 0 FORMATTING, 2 DOCUMENTED, 0 UNEXPLAINED

VERDICT: PASS  (gate: 1a clean and zero UNEXPLAINED)
```

Everything else is byte-identical to golden, including `UserDefinedMassDensity=5.34`,
`RegionParameters` (Zmax `1000.000000`), `BaseFileName`, `ElectronNbr`, and the whole of
`.mic`/`.mdl`/`.rp`. Category 3 is whitelisted to `WeightFraction` within 1e-4 — any other
field claiming it fails, and a density delta would be a defect, not a classification.

The delta set is asserted **in full**, not merely checked for absence of unexplained
entries: a generator that silently substituted nothing would produce zero deltas and sail
through a weaker check.

---

## 4 — Test 2: the parsed golden table

21 rows × 12 columns (the file's 10, plus `run_id` and `Element`). `run_id` column elided
below for width; it is `GaAsBi_100nm_x010_ATW_rho534` throughout.

```
 Index Region  Index Atom  Atomic number Element     Line  Line energy (keV)  Intensity Generated (photons/e/sr)  Intensity Generated Detected (photons)  Intensity Emitted (photons/e/sr)  Intensity Emitted Detected (photons)  Detector efficiency
            0           0             31      Ga Line Ka1              9.251                        9.280180e-07                            10188.900000                      9.244860e-07                          10150.100000             0.999623
            0           0             31      Ga Line Ka2              9.234                        4.774740e-07                             5242.270000                      4.756470e-07                           5222.220000             0.999621
            0           0             31      Ga Line Kb1             10.263                        2.044140e-07                             2244.530000                      2.038300e-07                           2238.110000             0.999723
            0           0             31      Ga Line Kb2             10.365                        0.000000e+00                                0.000000                      0.000000e+00                              0.000000             0.999731
            0           0             31      Ga  Line La              1.098                        7.845600e-07                             7727.490000                      7.024620e-07                           6918.870000             0.896763
            0           0             31      Ga Line Lb1              1.122                        2.145210e-07                             2126.320000                      1.675650e-07                           1660.900000             0.902454
            0           1             33      As Line Ka1             10.543                        7.673890e-07                             8426.350000                      7.613560e-07                           8360.100000             0.999744
            0           1             33      As Line Ka2             10.507                        3.960830e-07                             4349.190000                      3.929370e-07                           4314.650000             0.999742
            0           1             33      As Line Kb1             11.725                        1.753410e-07                             1925.470000                      1.743140e-07                           1914.190000             0.999812
            0           1             33      As Line Kb2             11.863                        7.483880e-09                               82.183000                      7.440070e-09                             81.702000             0.999818
            0           1             33      As  Line La              1.282                        7.416650e-07                             7590.960000                      5.905140e-07                           6043.930000             0.931868
            0           1             33      As Line Lb1              1.317                        2.614950e-07                             2690.260000                      2.067020e-07                           2126.540000             0.936689
            0           2             83      Bi Line Ka1             77.097                        3.974190e-09                                6.541210                      3.973880e-09                              6.540690             0.149856
            0           2             83      Bi Line Ka2             74.805                        2.376160e-09                                4.031690                      2.375960e-09                              4.031350             0.154481
            0           2             83      Bi Line Kb1             87.335                        1.390080e-09                                2.046230                      1.390000e-09                              2.046110             0.134023
            0           2             83      Bi Line Kb2             89.833                        4.134590e-10                                0.595416                      4.134360e-10                              0.595383             0.131115
            0           2             83      Bi  Line La             10.840                        9.831200e-08                             1079.540000                      9.759890e-08                           1071.710000             0.999764
            0           2             83      Bi Line Lb1             13.021                        5.210540e-08                              572.196000                      5.170280e-08                            567.775000             0.999834
            0           2             83      Bi Line Lb2             12.977                        2.359490e-08                              259.108000                      2.341100e-08                            257.089000             0.999835
            0           2             83      Bi  Line Lg             15.244                        9.831200e-09                              107.824000                      9.775350e-09                            107.211000             0.998559
            0           2             83      Bi  Line Ma              2.423                        7.244180e-08                              781.150000                      6.585250e-08                            710.097000             0.981772
```

All four intensity columns preserved. No ratios, k-factors, or derived quantities are
computed anywhere in the parser — asserted by a test.

---

## 5 — Verification beyond "the tests pass"

A passing gate proves nothing unless it also fails when it should. Each silent killer was
injected by monkeypatch (no source modified) and the gate re-run:

| Injected fault | Caught by | How it surfaced |
|---|---|---|
| nm value in the Å field (100 nm → `100.000000`) | 1b | UNEXPLAINED `RegionParameters` |
| atomic fractions in `WeightFraction` | 1b | delta +5.9e-2 — 3 orders past the 1e-4 tolerance |
| `UserDefinedMassDensity` left at 0 | 1b | UNEXPLAINED |
| `DetectorDiffusionLenght` "corrected" | 1a | field missing / field not in golden |
| line endings harmonised to CRLF | 1a | `.mdl` is CRLF, golden is LF |

5/5 caught. The script lives in the session scratchpad rather than `tests/`, to stay inside
the agreed layout — say the word and it can be promoted to a permanent regression test.

---

## 6 — Anomalies and findings

### 6.1 `.mdl` and `.rp` are LF-only — the docs say CRLF *(new this session; resolved)*

The Step 0 brief, the original prompt, `CLAUDE.md`, and `golden/README.md` all assert CRLF
on every input. Two of six are LF:

```
GaAsBi_val.sim   CRLF x7    trailing CRLF     authored  (Jul 8/15)
GaAsBi_val.sam   CRLF x12   trailing CRLF     authored
GaAsBi_val.mic   CRLF x25   trailing CRLF     authored
GaAsBi_val.par   CRLF x13   trailing CRLF     authored
GaAsBi_val.mdl   LF x44     0 CR bytes        vendor    (Jun 18 14:38 = install)
GaAsBi_val.rp    LF x10     0 CR bytes        vendor
```

The split falls exactly on authorship, and mtimes confirm it: CRLF was never a format
property, it is an artifact of which files were opened in a Windows editor. The exe read
both conventions in the same successful run, so line endings are **not** load-bearing —
this is a fidelity detail, not a silent killer. **Resolution:** per-file fidelity, no
blanket rule. "CRLF on every generated file" contradicted "pass `.mdl`/`.rp` through
byte-for-byte" and would have added 44 and 10 bytes; it is dropped.

**Docs to update:** `CLAUDE.md` trap #5, and the golden README's authorised-facts list.

### 6.2 `Options.txt` provenance *(caught by Step 0; resolved)*

`Golden/outputs/` initially held `GaAsBi_100nm_x010_ATW_val_Options.txt` — the density-0
run's echo, byte-identical to the live `_val` original. Content impact was nil (the two runs'
`Options.txt` are byte-identical, since it carries no specimen density line), but the
provenance label was wrong. Swapped for the `_rho534` file; Step 0 now passes.

### 6.3 The density defect scaled every intensity by ~15%, not just absorption

Comparing the two runs' `Intensity Generated`, the ρ=0/ρ=5.34 ratio is **1.152758, constant
to six significant figures across all eleven hard K lines and all three elements** — the
signature of pure density scaling. That implies an auto-mix density of **6.156 g/cm³**
(5.34 × 1.152758), inside the measured 6.12–6.16 bracket and within 0.13% of the
volume-additive prediction of 6.148; mass-weighted (6.344) is ruled out by a wide margin.

Treat this as corroboration of the existing identification, not a competing number: `I ∝ ρ`
ignores second-order energy-loss effects, which plausibly account for the 0.13% residual.
The load-bearing point is that the ρ=0 run's intensities were wrong **globally by ~15%**,
not merely in their absorption ratios — so re-running was necessary, not cosmetic.

It also independently confirms the "no meaningful counting noise at 10⁵ electrons" note: a
ratio reproducible to six significant figures across 11 lines leaves no room for Poisson
scatter.

### 6.4 Parser: pandas' NA sentinels were doing a silent coercion

`pd.read_csv(dtype=str)` converts `n/a`, `NA`, `null`, `NaN` and friends to NaN *during
read*, before any strict check can see them — precisely the coercion this parser exists to
refuse. It failed safe (surfacing as "missing" rather than "non-numeric"), but the
architecture was wrong. Fixed with `na_filter=False`: every field arrives as a string and
emptiness is judged in our own code, not by pandas.

### 6.5 Corrections to the original prompt, confirmed against the files

Recorded for the docs, since each came from a document that recorded intent rather than the
artifact:

| Prompt said | File says |
|---|---|
| 18 rows | **21** (Ga 6, As 6, Bi 9). "18" is the count cross-checked against Walther Table 1 |
| Bi Lα = 10.839 keV | **10.84** — energies are reported to ~4 s.f. |
| Weight fractions reproduce at the file's precision | They do not; ±9e-6 on Ga and Bi at 6 dp |
| CRLF on every input | Two of six are LF (§6.1) |
| `_XrayIntensities.csv` is the literal name | It is a **suffix**; the stem comes from `BaseFileName` |

### 6.6 ρ(x): what is published and what is derived *(citation corrected)*

The density comment originally attributed the whole of ρ(x) = 5.32 + 0.20·x to Walther. That
was wrong, and in a way that matters for a dissertation: it credited the paper with a step
taken locally. The provenance is split.

| | value | status |
|---|---|---|
| ρ(0.1) = 5.34 | Walther 2025 Fig. 3 caption | **verified verbatim** against the paper; regression-tested |
| ρ(0.2) = 5.36 | Walther 2025 Fig. 3 caption | **verified verbatim**; regression-tested |
| slope 0.20 | derived locally | the unique line through the two anchors |
| intercept 5.32 | derived locally | the x=0 **extrapolation** — not a published value |

The caption reads: *"for two alloys of different densities (5.34 g cm⁻³ for x = 0.1 and 5.36
g cm⁻³ for x = 0.2)"*. The straight line through those points is the supervisor's derivation.
It reproduces both anchors to machine precision, and `PUBLISHED_DENSITY_ANCHORS_G_CM3` now
pins them under test, so drift in either fails loudly.

**Only 0.1 ≤ x ≤ 0.2 is bracketed by the anchors.** Set A sits on the x=0.2 anchor exactly.
Set B's x = 0.02, 0.002 and 0.0002 are **extrapolations below the anchored range**. Defensible
— Walther notes density *"increases actually only very slightly because the mass increase by
substituting [an] As atom by [a] much heavier Bi atom … increases the unit cell volume almost
in the same proportion"*, i.e. +0.75% over 0 ≤ x ≤ 0.2, nearly flat — and the magnitude is
negligible against a 15% error that moved the ratios only 1.3–3.2%. But it is extrapolation
and the write-up should call it that.

This also supplies the paper's own account of why auto-mix is wrong rather than imprecise:
Bi is far heavier, but it expands the lattice by nearly the same proportion, so the alloy
stays near GaAs. Averaging elemental Ga/As/Bi densities discards the lattice entirely and
lands at ~6.15. Wrong model, not a rounding error.

> ⚠ **Superseded in part — see §10.** The provenance table above still stands: 5.34 and 5.36
> are quoted verbatim from Walther's captions, and the line through them is a local
> derivation. What §10 overturns is the *physical claim* in the last two paragraphs. Walther's
> stated reason for a nearly-flat ρ(x) — that the cell volume grows in almost the same
> proportion as the mass — is **not supported by the lattice-parameter source he cites**.
> Measured against Tixier (2003), mass rises ~2.5× faster than volume. Read §10 before using
> anything in this subsection for methodology.

---

## 7 — Open items

**Needs Ethan's confirmation — encoded on an assumption:**
- **The supervisor's derivation is described in code as "the straight line through the two
  published points".** That is inferred from the arithmetic (the line through (0.1, 5.34) and
  (0.2, 5.36) is exactly 5.32 + 0.20x), not from anything stating what they actually did. If
  the derivation was something else — a lattice-parameter calculation of their own that merely
  agrees at those two x values, or a fit to more points — the comment in `spec.py`
  misdescribes it and should be corrected. Nothing computational depends on this; the
  attribution does.
- ~~**Which density model the run matrix should use (§10).**~~ **Decided 2026-07-19: run
  both.** Both models are implemented and selectable (§12); the matrix is 15 runs × 2 = 30.
  This resolves the *engineering* question only — which model is physically right, and what
  to do if the two sets of curves disagree, remains open and is Ethan's.
- **The `run_id` convention for the doubled matrix.** Proposed
  `GaAsBi_<t>nm_x<xxx>_rho<ddd>` (e.g. `GaAsBi_100nm_x020_rho536` vs `..._rho587`), encoding
  the density so it is readable off a flat `Results\` directory holding ~570 output files.
  Not yet confirmed; the stem is permanent provenance, so it should be Ethan's call.

**The last uncited physical constant in the code:** *(RESOLVED — see §12.1. Retained for the
record.)*
- **Atomic weights** (Ga 69.723 / As 74.9216 / Bi 208.9804) carry
  `# pending verification vs primary source (NIST/IUPAC) before final write-up`. Everything
  else in the code is now either cited to a primary source or explicitly marked as derived.
  Lead worth following: Walther states he *"used the standard atomic weights"* too — pinning
  down which table he used would likely resolve both this and the ±9×10⁻⁶ golden
  weight-fraction residue (§3, §6.5) at once, since that residue is consistent with golden's
  values carrying a different atomic-weight table from the IUPAC one the generator uses.

**For the docs (no action taken):**
- `CLAUDE.md` trap #5 and the golden README both need the §6.1 line-ending correction.
- `CLAUDE.md` states "ρ(x) = 5.32 + 0.20·x, anchors from Walther 2025 Fig. 3", which reads as
  though the formula is the paper's. Per §6.6 only the two anchors are — worth rewording so
  the derived parts are not later cited to Walther by mistake.
- `archive/density0_control/` does not exist, though the golden README calls it "the sole
  evidence behind the 15% figure". The density-0 **outputs** survive in the live `Results\`
  under the `_val` stem, so the evidence is not lost. Its **inputs** are gone —
  `Sim\GaAsBi_val.sam` was edited in place to 5.34, so no copy of the `.sam` that produced
  that run exists anywhere. Reconstructing it would be trivial but would be a reconstruction.

**Unresolved, untouched, left as seams:**
- Windowless settability (spike i). `RunSpec.window` raises `NotImplementedError`. Evidence
  gathered incidentally: the `.mic` format documents no window field, so if it is settable
  at all it is via an undocumented key.
- ~~`Electrons per time slice` → native pile-up (spike ii)~~ **Resolved (§17.4): MC X-Ray
  cannot build sum peaks natively** → sum-peak route is analytic synthesis. `.sim` path
  resolution + seed (spike iii) untouched; gates parallelism only.
- ~~Whether `La` includes Lα2~~ **Resolved (§15.1):** Walther — Lα1/Lα2 bundle (~108 eV apart),
  treat `La` as the whole Lα line, not a concern. **Whether Bi M-lines beyond Mα are modelled**
  is still live — the golden output carries **only** `Line Ma` for Bi. Raw-only storage means
  it can be re-derived if answered.

**Not built, by design:** executor, matrix, aggregation, ratios, sum-peak, inversion.

---

## 8 — How to re-run

```
cd C:\MCXRAY\Sim\Wrapper
python -m pytest tests/ -q        # 109 tests
python -m tests.diffreport        # the classified diff above
```

---

## 9 — End-to-end confirmation: generated inputs were actually run

The golden gate proves the generated files are byte-accountable against files that ran. It
does not prove they *run*. That gap was closed by driving the exe with them.

Two runs, `gen01` and `gen02`, both from `RunSpec(x_bi=0.1, thickness_nm=100,
n_electrons=100000, window="ATW")`, written into `C:\MCXRAY\Sim\` and executed as
`console_mcxray_lite_x64.exe --simulation-file <run_id>.sim`. Both exited 0 in ~19.7 s.

**Result: the generated inputs reproduce the golden output to within the simulator's own
run-to-run noise.** 21 rows, identical (element, line) set, identical line energies, and
every intensity within 0.03%. Detector efficiency identical to 0 dp.

| line (Emitted Detected) | gen01 | **golden** | gen02 |
|---|---|---|---|
| Ga Kα1 | 10148.0 | **10150.1** | 10151.8 |
| Bi Lα | 1071.39 | **1071.71** | 1071.79 |
| Bi Mα | 709.887 | **710.097** | 710.119 |

The golden value falls *inside* the spread of the two runs in every case.

### 9.1 A defect this found that 81 tests did not

The first attempt to write into `C:\MCXRAY\Sim\` — the destination Stage 3 requires, since
that is where the exe resolves `.sim` child files from — **raised an error and refused**.

The guard rejected any target with the golden set inside it. But this repo lives at
`C:\MCXRAY\Sim\Wrapper`, so `Golden\` is a descendant of `Sim\`. Writing six files into
`Sim\` cannot touch `Sim\Wrapper\Golden\inputs\`, but the check could not tell the
difference. **It would have made Stage 3 impossible.** Every test passed because every test
wrote to a pytest `tmp_path` and none ever tried the real destination.

Fixed to refuse only when the target *is* the golden set or sits inside it. Two regression
tests added, including one that reproduces the Sim/Wrapper/Golden nesting.

### 9.2 `RandomNumberSeed=0` is not deterministic — partial answer to spike (iii)

`gen01` and `gen02` have byte-identical inputs (bar filenames) and produced **different
output**: run-to-run spread up to 0.0374% on individual intensities. So seed 0 does not
reproduce, and the ~0.03% gap against golden is trajectory noise rather than the ±9e-6
composition residue — which is therefore below the noise floor, confirming empirically the
"physically negligible" classification made in §3 on arithmetic alone.

Consistent with the existing observation that two invocations reproduced a derived *ratio*
to four significant figures: ratios are steadier than individual intensities because the
noise is partly common-mode.

**Still open:** whether a *non-zero* `RandomNumberSeed` reproduces. Untested. That, and the
`.sim` path-resolution half, remain spike (iii).

### 9.3 The matrix corners were run

The validation point (x=0.1, 100 nm) is the middle of the matrix. The corners had never been
through the exe. Four more runs, all at 10⁵ electrons, all **exit 0, all 21 rows**:

| run | Zmax written | ρ | w_Bi |
|---|---|---|---|
| `GaAsBi_2nm_x020_ATW_ext` | `20.000000` Å | 5.36 | 0.243771 |
| `GaAsBi_100nm_x020_ATW_ext` | `1000.000000` Å | 5.36 | 0.243771 |
| `GaAsBi_1024nm_x020_ATW_ext` | `10240.000000` Å | 5.36 | 0.243771 |
| `GaAsBi_100nm_x0002_ATW_ext` | `1000.000000` Å | 5.32004 | 0.000289 |

**The Ångström conversion holds at the extremes — confirmed by physics, not by diffing.**
Generated intensity scales with thickness, so anchoring on the already-verified 100 nm point:

| line | 2 nm / 100 nm | 1024 nm / 100 nm |
|---|---|---|
| Ga Kα1 | 0.01990 | 10.580 |
| As Kα1 | 0.01990 | 10.580 |
| Bi Lα | 0.01990 | 10.580 |

Expected ~0.02 and ~10.24. **Had 2 nm been written as 2 Å, the ratio would have been ~0.002** —
the silent killer would have shown up here as a factor of ten. All three elements give
identical ratios, the signature of a pure geometric effect.

The 1024 nm figure is 3.3% *above* linear, which is expected and reassuring: multiple
scattering makes the electron path longer than the foil is thick, so intensity grows slightly
faster than thickness. Walther observes the same in his own curves ("increase very slightly,
faster than linear"). It also explains why 2 nm/100 nm sits just under 0.02 — the 100 nm
denominator already carries a little path lengthening.

**Self-absorption behaves correctly across three decades of thickness** (Generated→Emitted):

| | Ga Lα (1.098 keV) | Bi Mα (2.423 keV) | Ga Kα1 (9.251 keV) |
|---|---|---|---|
| 2 nm | 0.9974 | 0.9982 | 0.9999 |
| 100 nm | 0.8778 | 0.9142 | 0.9954 |
| 1024 nm | 0.3438 | 0.4541 | 0.9540 |

Soft lines are progressively eaten, hard lines barely touched. Right at both ends.

**The composition reaches the simulator correctly at Set B's floor.** Bi intensity should
scale as w_Bi × ρ. Predicted ratio (x=0.0002 vs x=0.2) = (0.000289/0.243771) × (5.32004/5.36)
= 0.001177. **Observed: 0.001174** on both Bi Lα and Bi Mα — 0.25%. Ga and As rise as they
should (Ga ×1.173 vs 1.176 predicted, As ×1.466 vs 1.470), since As reclaims the weight Bi
gives up.

### 9.4 A number for the Set B floor decision

At **x = 0.0002 and 10⁵ electrons, Bi Lα yields 2.3 detected photons.** Bi Mα gives 1.5, Bi
Lβ1 gives 1.2. (Against 1986 / 1323 / 1053 at x=0.2.) At the archival 10⁶ that is ~23 photons
on the strongest Bi line.

This bears directly on the pending Set B floor policy — fixed dose vs fixed statistics
(Blueprint §5.1) — which is Ethan's decision and is not made here. One caveat that matters
for interpreting it: MC X-Ray's line intensities are **not** Poisson-sampled counts (§9.2
measured run-to-run scatter of 0.037% on lines carrying ~10⁴ photons, far below the ~1%
Poisson would give). So these are low-variance expectation values, and the simulation may
report 2.3 photons far more precisely than a real detector could ever measure 2.3 photons.
Whether the question being asked is about *this measurement* or about *the physics* is exactly
the distinction the floor policy has to settle.

---

## 10 — ρ(x) from primary sources: a discrepancy in the published anchors

*This section is written to be usable directly as methodology. It supersedes the physical
claim in §6.6; the provenance table there still holds.*

### 10.1 What prompted it

§6.6 recorded that ρ(x) = 5.32 + 0.20·x is a straight line through two values quoted in
Walther's figure captions, and that the line itself is a local derivation rather than the
paper's method. The paper describes its own method differently:

> "Here, we used the standard atomic weights and the lattice parameter estimates from
> Ref. (2) to check that the density of GaAsBi increases actually only very slightly because
> the mass increase by substituting 1 As atom by 1 much heavier Bi atom (for x = 0.25)
> increases the unit cell volume almost in the same proportion."

That is a calculation, not an interpolation — so the underlying method is reproducible from
primary sources, and the question became whether the published anchors follow from it.

### 10.2 Sources

| ref | source | DOI | role |
|---|---|---|---|
| Walther 2025 | *J. Microsc.*, the project's central paper | [10.1111/jmi.70058](https://doi.org/10.1111/jmi.70058) | supplies ρ = 5.34 (x=0.1), 5.36 (x=0.2) |
| Walther's ref (2) | Tixier et al. 2003, *Appl. Phys. Lett.* **82**, 2245–2247 | [10.1063/1.1565499](https://doi.org/10.1063/1.1565499) | a(GaBi) = 6.33 ± 0.06 Å, free-standing |
| Blakemore 1982 | *J. Appl. Phys.* **53**, R123–R181 | [10.1063/1.331665](https://doi.org/10.1063/1.331665) | a(GaAs) = 5.65325 Å (§10.10) |
| Ioffe NSM database | GaAs basic parameters, 300 K | — | cross-check: a = 5.65325 Å, ρ = 5.32 g cm⁻³ |
| Tixier's ref (2) | Janotti, Wei & Zhang 2002, *Phys. Rev. B* **65**, 115203 | — | DFT-LDA a(GaBi) = 6.324 Å |
| Tixier's ref (5) | Oe 2002, *Jpn. J. Appl. Phys.* **41**, 2801 | — | MOVPE a(GaBi) = 6.192 Å |

Both Walther and Tixier PDFs are in `Wrapper/`. Janotti and Oe are cited second-hand through
Tixier and have not been read.

### 10.3 Method

Zinc-blende has 4 formula units per cubic unit cell, so for GaAs₁₋ₓBiₓ:

```
    rho(x) = 4 * M(x) / (N_A * a(x)^3)
    M(x)   = M_Ga + (1-x)*M_As + x*M_Bi          [g/mol]
    a(x)   = (1-x)*a_GaAs + x*a_GaBi             [Vegard's law]
```

with N_A = 6.02214076×10²³ (exact, SI), M from §1's atomic weights, a_GaAs = 5.65325 Å,
a_GaBi = 6.33 Å.

### 10.4 Two assumptions, both confirmed by the source rather than assumed

Tixier's full text settles the two places this calculation could have gone wrong:

> "The parameters for the **free standing** films are obtained by correcting the x-ray data
> for the tetragonal distortion using the elastic constants of GaAs. The lattice parameters
> show a linear trend with the Bi concentration **in accordance with Vegard's law**. By
> extrapolating the trend for the free standing films to the binary GaBi, a lattice parameter
> of 6.33 ± 0.06 Å is obtained."

1. **6.33 Å is the free-standing (relaxed) value**, with strain corrected out. Their as-grown
   films are pseudomorphically strained to GaAs, so the raw XRD number would have been the
   wrong one — but they report the corrected one. Free-standing is exactly this project's
   geometry (single BOX region, vacuum both sides), so it is the correct branch of their data.
2. **Vegard's law is stated, not assumed here.** The linear interpolation is what their
   measurements follow.

### 10.5 Validation, and what it does *not* establish

At x = 0 the calculation has no free parameters and must return the density of GaAs:

```
    rho(GaAs) computed = 5.3176 g/cm3
    Ioffe NSM, GaAs 300 K = 5.32 g/cm3      agrees to the precision Ioffe quotes
```

**An earlier draft of this section overstated the strength of this check, and the correction
is worth recording.** It originally read "agreement to four decimals means neither input is
materially wrong". At the time, *both* the lattice constant and the comparison density were
recalled from general knowledge rather than read from a source, so the check demonstrated
that two remembered values are mutually consistent through a correct formula — not that
either was right. Standard reference tables list a and ρ together, so a matched-but-wrong
pair would have passed silently.

With `a_GaAs` now sourced (§10.10) the check is meaningful, but its scope is still limited:

- ✅ Confirms the zinc-blende relation and the factor of 4 formula units per cell are applied
  correctly — ρ goes as a⁻³, so a transposed digit would be glaring.
- ✅ Confirms a and ρ from an independent compilation are self-consistent.
- ❌ Does **not** validate the atomic weights, which carry their own standing caveat (§7).

The conclusion in §10.6 does not rest on this check in any case: the Walther/Tixier gap is
5–9.5%, while any plausible error in `a_GaAs` sits in the fourth decimal.

### 10.6 Result

| x | Walther | from Tixier | difference |
|---|---|---|---|
| 0.1 | 5.34 | **5.607** | +5.0% |
| 0.2 | 5.36 | **5.871** | +9.5% |

**Robust to the choice of endpoint.** Every published value for a(GaBi) gives the same
conclusion; the lowest of them (Oe) makes the discrepancy larger, not smaller:

| a(GaBi) source | value (Å) | ρ(0.1) | ρ(0.2) |
|---|---|---|---|
| Tixier 2003, free-standing | 6.33 ± 0.06 | 5.607 (+5.0%) | 5.871 (+9.5%) |
| Janotti 2002, DFT-LDA | 6.324 | 5.608 (+5.0%) | 5.875 (+9.6%) |
| Oe 2002, MOVPE | 6.192 | 5.647 (+5.8%) | 5.956 (+11.1%) |

To reproduce Walther's anchors, a(GaBi) would have to be **7.27 Å** (for ρ(0.1) = 5.34) or
**7.22 Å** (for ρ(0.2) = 5.36) — 15–16σ above Tixier's measurement, and above every value in
the literature.

### 10.7 Diagnosis: the slope, not a rounding error

Testing the paper's stated reasoning at its own example, x = 0.25 (one As of the four group-V
sites per unit cell replaced by Bi):

| quantity | change |
|---|---|
| unit-cell mass | **+23.17%** |
| unit-cell volume (a: 5.6532 → 5.8224 Å) | **+9.25%** |
| ⇒ density | **+12.74%** |

The claim requires these to be nearly equal; they differ by a factor of ~2.5. Bi is far
heavier than the As it replaces (208.98 vs 74.92 g/mol) and the lattice does not expand enough
to compensate. Extrapolated to the endpoint, GaBi would be **7.30 g/cm³** against GaAs's 5.32.

Consequently the published ρ(x) has the wrong **slope**: 0.20 g cm⁻³ per unit x, against
**2.891** from the lattice data — a factor of **14.5**. Both forms agree as x → 0, which is
why the error vanishes at low Bi content and is worst at high.

### 10.8 Consequence for this project's run matrix

| x | where it appears | ρ currently used | ρ from Tixier | difference |
|---|---|---|---|---|
| 0.2 | **Set A (all 10–20 runs) *and* Set B's first point** | 5.36000 | 5.87141 | **+9.54%** |
| 0.1 | validation run only | 5.34000 | 5.60668 | +4.99% |
| 0.02 | Set B | 5.32400 | 5.37747 | +1.00% |
| 0.002 | Set B | 5.32040 | 5.32365 | +0.06% |
| 0.0002 | Set B | 5.32004 | 5.31822 | −0.03% |

Note that x = 0.2 is Set A's fixed composition **and** the top point of Set B's sweep, so it
is the most-run composition in the matrix and carries the largest discrepancy.

Applying this project's own measured sensitivity (§9.2 and §6.3: a 13.26% density error moved
the diagnostic ratios 1.29–3.11%, i.e. 0.097–0.234% of ratio per 1% of density, at 100 nm):

| arm | density difference | ratio impact |
|---|---|---|
| **Set A — every run** (x = 0.2) | 9.54% | **0.93–2.23%** |
| **Set B, first point** (x = 0.2) | 9.54% | **0.93–2.23%** |
| validation (x = 0.1) | 4.99% | 0.48–1.17% |
| Set B, second point (x = 0.02) | 1.00% | 0.10–0.23% |
| Set B, lowest two (x ≤ 0.002) | <0.1% | negligible |

**The whole thickness arm is affected, plus the top of the composition arm** — systematically,
as a bias rather than scatter. Only Set B's three lower compositions are genuinely immune,
because the two density models converge as x → 0. For scale, this is about half the size of
the density defect already corrected in §6.3, and an order of magnitude below the ~50%
sum-peak effect that is the paper's main subject.

### 10.9 Status: decision pending, nothing changed in code

`spec.py` still emits ρ(x) = 5.32 + 0.20·x, and `PUBLISHED_DENSITY_ANCHORS_G_CM3` still pins
Walther's two values under test. **No code was changed on the strength of this analysis** —
selecting a density model is a scientific judgement reserved to Ethan under project
governance. The full working lives in the session scratchpad (`density_final.py`), not in the
package.

Three options, with the trade-off stated rather than resolved:

1. **Walther's values** — reproduces his simulation conditions, so any divergence in the
   resulting curves is attributable to this project's variables rather than to a density
   mismatch. Uses a density his own cited source contradicts.
2. **Tixier-derived values** — physically defensible for a free-standing foil and traceable to
   primary sources. Curves will then legitimately differ from the published ones for a reason
   unrelated to the hypothesis under test.
3. **Both** — 24 runs ≈ 80 min serial at 10⁶, so the ambiguity converts into a measured
   number for the cost of one afternoon. The raw-intensity storage rule means both sets remain
   re-derivable without re-simulation.

**Current intent (2026-07-19): run both.**

### 10.10 Provenance of `a_GaAs` *(resolved 2026-07-19)*

`a_GaAs = 5.65325 Å` was originally taken from general knowledge — recalled, not derived and
not read from any document. It is now sourced:

| source | value | type |
|---|---|---|
| Ioffe NSM database, GaAs 300 K | **a = 5.65325 Å**, zinc blende, ρ = 5.32 g cm⁻³ | secondary compilation, no citations given |
| Blakemore 1982, *J. Appl. Phys.* **53**, R123–R181, [10.1063/1.331665](https://doi.org/10.1063/1.331665) | the standard GaAs property review | primary review — **cite this in the write-up** |

Ioffe confirms the figure to all five significant figures used here. Blakemore is the
citation of record; Ioffe is a convenient cross-check, not a source for a dissertation.
Tixier gives the GaAs endpoint only as a plotted axis in Fig. 2, never as a number in text.

**A by-product worth noting: Walther's intercept is right.** Ioffe puts GaAs at
5.32 g cm⁻³ — exactly the intercept of ρ(x) = 5.32 + 0.20·x. So the published formula is
correctly anchored at x = 0 and only its *slope* is wrong (0.20 against ~2.891, §10.7). That
also revises §6.6, which describes the intercept as "the x=0 extrapolation — not a published
value": it is not published *by Walther*, but it coincides with the accepted GaAs density
rather than being an artefact of the fit.

The atomic weights remain the one uncited physical input (§7).

---

## 11 — The run matrix, frozen against the Aims & Objectives form

*Added 2026-07-19 after reading `Ethan Pratt - Aims_and_Objectives_Form+Feedback.docx`.*

### 11.1 What the LOs fix

LO2 and LO4 were read directly from the document (stdlib XML extraction, so tracked changes
and comments would have surfaced; the file carries none, and Walther's LO1 feedback appears
inline as plain text).

| parameter | LO text | already correct? |
|---|---|---|
| Beam energy | 200 kV (LO2), 200 keV (LO4) | ✓ `.mic` has `BeamEnergy=200.000000` |
| Trajectories | "10e6" (LO4) | ✓ read as 10⁶ — see caveat below |
| Take-off angle | 25°, fixed (LO2) | ✓ `DetectorTOA=25` |
| Geometry | free-standing foil, no substrate (LO2) | ✓ single BOX, vacuum both sides |
| Thickness | ten-value doubling series, 2 → 1024 nm (LO4) | ✓ matches Set A already |
| **Bi concentration** | **x = 0.01–0.2 (LO4)** | ✗ **broke the old Set B** |

The thickness clause had been revised before this reading: the form originally said
5–500 nm, which contradicted the series Walther actually specified (2ⁿ for n = 1…10, with
1 nm dropped as too noisy). Four of the ten thicknesses fell outside the old range at both
ends. LO4 now enumerates all ten values explicitly.

⚠ **"10e6" is ambiguous.** Read literally it is 10 × 10⁶ = 10⁷. The intent is plainly 10⁶
(and that is what CLAUDE.md and this project use), but it is a factor-of-ten ambiguity
sitting in a formal objectives document, and worth tidying if the form is revised again.

### 11.2 Set B rebuilt

The old Set B reached x = 0.002 and 0.0002, **below the LO floor of 0.01**. Replaced:

| | old | new |
|---|---|---|
| Set B compositions | {0.2, 0.02, 0.002, 0.0002} | **{0.01, 0.02, 0.05, 0.1, 0.2}** |
| runs | 4 | 5 |

Chosen for three reasons: the five values span the full LO range, they are round enough to
read cleanly in a write-up, and **x = 0.1 reproduces the validation configuration** (100 nm,
x = 0.1) at archival dose. Set B's x=0.1 point is therefore the same physical configuration
as the golden run at 10⁶ rather than 10⁵ trajectories — a consistency check the matrix
previously had nowhere.

### 11.3 The window arm has no basis in the LOs

LO4 varies **thickness and Bi concentration only**. LO2 fixes geometry and take-off angle
and never mentions the entrance window. The previous Set A design ran every thickness twice
(ATW and windowless) for 20 runs.

**Consequence: Set A is 10 runs, not 20, and spike (i) no longer gates the matrix.**
Windowless moves from blocker to optional scope. Worth confirming with Walther, but the
document is unambiguous as written.

### 11.4 The frozen matrix

| arm | fixed | varied | runs |
|---|---|---|---|
| Set A | x = 0.2 | thickness 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024 nm | 10 |
| Set B | 100 nm | x = 0.01, 0.02, 0.05, 0.1, 0.2 | 5 |
| | | **per density model** | **15** |
| | | **× 2 models (§12)** | **30** |

At ~3.3 min per run at 10⁶ (extrapolated from 19.7 s at 10⁵), roughly 100 minutes serial —
a floor, since thick foils run longer than thin ones.

### 11.5 The Set B statistical floor is no longer pressing

§9.4 recorded ~2 detected photons on the strongest Bi line at x = 0.0002. The new floor is
x = 0.01, carrying ~50× more Bi:

| | w(Bi) | Bi Lα at 10⁵ | at 10⁶ |
|---|---|---|---|
| old floor, x = 0.0002 | 0.000289 | ~2 photons | ~23 |
| **new floor, x = 0.01** | 0.014315 | **~114 photons** | **~1140** |

Fixed dose at 10⁶ across the matrix is therefore likely sufficient, and the fixed-dose vs
fixed-statistics decision (Blueprint §5.1) is much less consequential than it appeared.
The estimate is a linear scaling from measured runs, not itself measured.

---

## 12 — Two density models, implemented

*Added 2026-07-19. Implements the choice analysed in §10; does not make it.*

`RunSpec.density_model` selects `"walther"` (default) or `"tixier"`. The default is
deliberate: it is what the golden set was generated with, so the golden gate and every
existing run are unaffected, and an unknown value raises rather than falling back — silently
defaulting either way would be a 9.5% error at x = 0.2.

```
WALTHER : rho(x) = 5.32 + 0.20x                       [published anchors, Walther 2025]
TIXIER  : rho(x) = 4*M(x) / (N_A * a(x)^3)            [zinc blende, 4 units per cell]
          a(x)   = (1-x)*a_GaAs + x*a_GaBi            [Vegard, per Tixier]
```

Emitted densities across the frozen matrix:

| x | walther | tixier | difference |
|---|---|---|---|
| 0.01 | 5.32200 | 5.34767 | +0.48% |
| 0.02 | 5.32400 | 5.37747 | +1.00% |
| 0.05 | 5.33000 | 5.46531 | +2.54% |
| 0.1 | 5.34000 | 5.60668 | +4.99% |
| 0.2 | 5.36000 | 5.87141 | +9.54% |

### 12.1 Atomic weights, now sourced *(closes the last open constant)*

Verified against **IUPAC/CIAAW Standard Atomic Weights, 2024 edition** (a revision of the
Atomic Weights 2021 report), https://www.ciaaw.org/atomic-weights.htm:

| | CIAAW 2024 | previously in code | change |
|---|---|---|---|
| Ga | 69.723(1) | 69.723 | exact |
| As | 74.921 595(6) | 74.9216 | rounded — now full precision |
| Bi | 208.980 40(1) | 208.9804 | exact |

**The correction is inconsequential**: 0.07 ppm on As, leaving every weight fraction
identical at the 6 dp written to the `.sam` and the molar mass unchanged to 5 dp. The full
values are used regardless, since there is no reason to carry a rounded constant when the
source value is known. Uncertainties are also recorded, for anyone propagating an error
budget later.

**This retires the `pending verification` marker; no uncited physical constant remains in
the package.**

**It also lets the golden composition residue be classified on evidence rather than
assertion.** Ga carries ~14 ppm relative uncertainty; As and Bi are effectively exact, both
being mononuclidic. Against that budget, the residue's Ga offset is ~1.4σ — consistent with
an atomic-weight difference — but its Bi offset is ~1460σ, which is not. No real
atomic-weight table can produce the golden values, so "transcription residue" (§3, §6.5) is
now the evidenced conclusion rather than the only remaining explanation.

### 12.2 Tests

Ten added (94 total). Three carry the weight:

- **`test_tixier_model_matches_hand_calculation`** recomputes ρ from first principles,
  independently of the implementation. It earned its place immediately: a hardcoded
  expectation in a *sibling* test was wrong (`5.871413` for `5.871405`), and this test
  localised the error to the expectation rather than the code. Without it, two tests could
  have agreed on a wrong number.
- **`test_tixier_model_reproduces_gaas_at_x_zero`** promotes the §10.5 check to a standing
  test. It exercises the a³ path, so a wrong formula-units-per-cell factor or Å→cm
  conversion fails loudly.
- **`test_density_model_reaches_the_generated_sam`** asserts the choice changes
  `UserDefinedMassDensity` in the written file, not merely the Python value.

The §10.8 discrepancy figures are also pinned as a parametrised test, so the percentages
quoted in this report cannot drift from what the code emits.

---

## 13 — The 30-run matrix: results

*Executed 2026-07-19. All 30 runs completed, exit 0, all CSVs present, 98.9 minutes serial.*

### 13.1 Execution

`run_id` convention adopted: `GaAsBi_<t>nm_x<xxx>_<wal|tix>_rho<ddd>` — composition,
thickness, density model and resulting density all readable off a flat `Results\`
directory. Order was all 15 Walther runs, then all 15 Tixier.

**Runtime scales strongly with thickness**, which the earlier ~3.3 min/run estimate did not
capture: 133 s at 2 nm against 558 s at 1024 nm, a 4.2× spread (thicker foils mean more
scattering events per trajectory). The per-run average happened to land near the estimate,
so the ~100 min total was right by cancellation rather than by a good model.

The pre-flight smoke test (§13.5) cleared the one gap the previous draft flagged: no
Tixier-density `.sam` had ever been through the exe.

### 13.2 Set A physics is correct

All three diagnostic ratios rise **monotonically across all ten thicknesses**, under both
density models — which is what Walther states must happen ("K/L and L/M ratios should always
increase monotonically with thickness"). This is the shape that reproduces his Figure 1.

| t (nm) | Ga K/L | As K/L | Bi L/M |
|---|---|---|---|
| 2 | 1.3219 | 1.1152 | 1.3843 |
| 32 | 1.3734 | 1.1941 | 1.4192 |
| 128 | 1.5472 | 1.4719 | 1.5348 |
| 1024 | 3.6587 | 5.0505 | 2.8217 |

*(Walther density, x=0.2. Ratios computed ad hoc for verification only — no ratio logic
exists in the package; the raw-only storage rule is intact.)*

### 13.3 The density models diverge with thickness — the headline result

**This was not predicted.** §10.8 estimated 0.93–2.23% on the ratios at x = 0.2, from a
measurement at 100 nm. That figure is correct *at 100 nm* and wrong as a general claim.

| t (nm) | Ga K/L | As K/L | Bi L/M |
|---|---|---|---|
| 2 | +0.0% | +0.0% | +0.0% |
| 32 | +0.4% | +0.7% | +0.3% |
| 128 | +1.5% | +2.6% | +1.0% |
| 512 | +4.9% | +7.0% | +3.4% |
| **1024** | **+7.3%** | **+8.4%** | **+5.6%** |

**Mechanism:** absorption depends on **ρ·t**, not ρ alone. At 2 nm nothing is absorbed under
either model and density is irrelevant; at 1024 nm absorption dominates and the 9.5% density
difference comes through nearly in full. Set A spans that whole regime.

Set B, by contrast, is mild — the models converge as x → 0:

| x | Ga K/L | Bi L/M |
|---|---|---|
| 0.01 | +0.04% | +0.04% |
| 0.05 | +0.24% | +0.23% |
| 0.2 | +1.18% | +0.77% |

### 13.4 Consequence: a ~9% offset in inferred thickness

The method reads thickness off the Ga K/L curve. The same measured ratio maps differently
under each model:

| measured Ga K/L | t (Walther) | t (Tixier) | difference |
|---|---|---|---|
| 1.5472 | 128 nm | 116.6 nm | −8.9% |
| 1.7972 | 256 nm | 232.9 nm | −9.0% |
| 2.3559 | 512 nm | 464.8 nm | −9.2% |
| 3.6587 | 1024 nm | 930.1 nm | −9.2% |

The offset is near-constant at ~9% — essentially the density difference itself, because the
ratio constrains **areal density (ρ·t)**, not thickness. Converting one to the other requires
ρ, so an error in ρ passes straight through.

**This is the limit of the self-calibration property.** The k\* method is explicitly designed
to be robust against detector-sensitivity and scale errors, which cancel in a ratio. A density
error does not cancel: it changes the ρ·t → t conversion. Whether it survives the
calibrate-then-invert round trip into recovered *x* is a Stage 7 question and remains Ethan's.

### 13.5 Correction: intensity columns do not scale with dose

An earlier statement in this report — that Bi Lα would give "~23 photons at 10⁶" at
x = 0.0002, and "~1140 at 10⁶" at x = 0.01 (§9.4, §11.5) — was **wrong**. The intensity
columns are normalised and do not scale with `ElectronNbr`.

Measured: the same configuration at 10⁵ and 10⁶ trajectories gives identical output —
Ga Kα1 = 10150 vs 10154, a 0.04% difference. The observed value at x = 0.01 with 10⁶
trajectories is **115.7 photons**, matching the 10⁵-based prediction rather than ten times it.

**Mechanism, confirmed from the run's own echo:** the "(photons)" columns are absolute
predicted counts for the acquisition defined in the `.mic` — `BeamCurrent=1e-9` and
`AcquisitionTime=100`, i.e. 6.242×10¹¹ real electrons, which matches the
`xrayCharacteristicConstant` the simulator prints. Multiplying generated photons/e/sr by the
solid angle (0.0175973 sr) and that electron count reproduces the reported figure to 0.04%.

Two quantities that had been conflated:

| | controls |
|---|---|
| `ElectronNbr` (10⁶) | Monte Carlo sample size — precision of the *estimate* |
| `BeamCurrent` × `AcquisitionTime` (1 nA × 100 s) | physical dose — sets the *predicted counts* |

**Implications:**

- The simulator reports a low-variance *expectation*. A real detector measuring 115 counts
  carries Poisson noise of √115 ≈ 11, i.e. **~9%**. Realistic measurement precision must be
  modelled by applying Poisson noise to the simulated expectation; the simulator will not do
  it (consistent with §9.2's 0.037% run-to-run scatter, which is estimation error, not
  counting statistics).
- **Raising `ElectronNbr` cannot improve counting statistics.** Only beam current or
  acquisition time can. This substantially reframes the Set B floor policy (Blueprint §5.1):
  the "fixed dose vs fixed statistics" choice is about `.mic` acquisition fields, not
  trajectory count.
- ⚠ `BeamCurrent` and `AcquisitionTime` are **not on CLAUDE.md's locked-parameter list**.
  They are inherited from the golden `.mic` and now known to set the reported photon counts
  directly. They deserve an explicit decision rather than silent inheritance.

---

## 14 — What was NOT verified

Recorded so no one later mistakes silence for a check.

- **The two density anchors were verified against the paper's text, supplied by Ethan** —
  not read off the PDF by this session. Stdlib extraction gave readable prose but masked
  every digit (the PDF uses custom font encodings sharing a code space), and no PDF library
  was installed to finish the job. The prose quoted in §6.6 is from that extraction; the
  numerals are from Ethan's transcription.
- ~~**Atomic weights: unverified.**~~ **RESOLVED (§12.1):** IUPAC/CIAAW 2024.
- **CASINO cross-check not attempted.** Walther confirmed (§15) that MC X-Ray is the correct
  tool for this work — it does sub-lines and detector properties, which CASINO does not — so a
  cross-code comparison is no longer the natural validation. But it also means nothing here is
  checked against a second independent code.
- **Only the validation point is checked against a known-correct answer.** §9.3 ran the matrix
  corners and confirms MC X-Ray accepts them and that the physics scales as it should — but
  there is no golden output at 2 nm, 1024 nm or x=0.0002 to compare against. Those runs
  demonstrate the generator is *self-consistent and physically sensible* across the range,
  not that the numbers are right in some absolute sense. Only x=0.1 at 100 nm has an
  independent answer to be right about.
- **Everything was run at 10⁵ electrons.** The archival sweep is 10⁶. Nothing suggests that
  matters — it should only reduce scatter — but it has not been exercised.
- ~~**No Tixier-model run has been simulated.**~~ **RESOLVED (§13):** 15 Tixier runs
  completed, exit 0, output sane. The highest density in the matrix (5.871405) was smoke-
  tested first.
- ~~**The ~114-photon figure at x = 0.01 is extrapolated.**~~ **RESOLVED (§13.5):**
  measured at 115.7. But the companion claim of "~1140 at 10⁶" was **wrong** — the intensity
  columns do not scale with trajectory count. See §13.5.
- ~~**The ~100-minute runtime estimate is a floor.**~~ **RESOLVED:** 98.9 min actual. The
  estimate was right by cancellation, not by a good model — thick foils ran 4.2× slower than
  thin ones (§13.1).
- **Recovered *x* has not been computed under any density model.** §13.4 shows a ~9%
  offset in *inferred thickness* between models; Walther expects this to largely cancel in the
  k\*-calibrate-then-invert round trip (§15.5), but that has not been demonstrated. Stage 7,
  Ethan's.
- **The production re-run (§15) supersedes the 30 comparison runs but has its own gaps.** It
  uses the correct density and detector, but at the time of writing recovered *x* is still
  uncomputed, and the low-x Set B Bi lines (x=0.01: Bi ~1% by weight) may be statistically
  ragged even at the raised dose — flagged in §15.4, not yet checked.
- **Windowless was never exercised** — `RunSpec` refuses it, and Walther confirmed (§15) it is
  not settable at all, so this is now closed rather than pending.

---

## 15 — Supervisor meeting (2026-07-19): resolutions and the production re-run

Walther reviewed the open questions. His answers close several and change three things that
sent the 30 comparison runs (§13) out of date. Note: **Walther and "Thomas" are the same
person** — where this report earlier split a "Walther model" from "supervisor guidance", it
was one source revising his own published values.

### 15.1 Resolved cleanly

- **Windowless is not possible.** He checked: the detector material is settable but a window
  is not, and his suggested workaround (extra Al in a top contact to mimic parylene) fails
  because there is no metal top contact to specify. Confirms the finding of §6.6/§11.3. Set A
  is 10 runs; the windowless spike is closed, not merely downgraded.
- **MC X-Ray is the correct tool, not a compromise.** CASINO lets you change physical models
  but not detector properties, and does **not** compute sub-lines (Lα, Lβ, Lγ). MC X-Ray fixes
  the models but exposes the detector and returns sub-line intensities, and models complete
  spectra. This work needs sub-lines and detector behaviour, so MC X-Ray is the right choice —
  the earlier "comparing across two codes" worry (§13, his Fig. 1 is CASINO) inverts into a
  justification.
- **Line set confirmed:** Kα, Kβ, Lα, Lβ, Lγ, and Mα for Bi.
- **Lα2 is not a concern** (Walther, later clarification). Bi Lα1 (10839 eV) and Lα2 (10731 eV)
  sit ~108 eV apart — within a single detector resolution element — so they bundle and are never
  separable in practice. The reported `La` is treated as the whole Lα bundle. This closes the
  "does Lα fold in Lα2" open question and confirms the ratios' `principal` definition (§17.2),
  which already uses `La` as a complete line rather than a partial one.

### 15.2 Density: the production model (supersedes both §10 models)

Walther's guidance: CASINO and MC X-Ray both mis-estimate compound densities because their
auto-mix interpolates the **elemental metal** densities of Ga/As/Bi, whereas GaAsBi bonding is
covalent with slight ionicity. Use endpoint densities **GaAs 5.32, hypothetical GaBi 7.18**
and interpolate. Per Ethan's decision, interpolate **linearly in density**:

> **ρ(x) = 5.32 + (7.18 − 5.32)·x = 5.32 + 1.86·x**

| x | ρ (production) | old WALTHER_PAPER | old TIXIER run |
|---|---|---|---|
| 0.01 | 5.339 | 5.322 | 5.348 |
| 0.05 | 5.413 | 5.330 | 5.465 |
| 0.1 | 5.506 | 5.340 | 5.607 |
| 0.2 | 5.692 | 5.360 | 5.871 |

It lands between the two models we ran — neither of the 30 comparison runs used it. His 7.18
is consistent with the lattice route of §10 (a(GaBi) = 6.36 Å against Tixier's 6.33), so the
two pictures agree to ~2%. This is now the **only** production model; `WALTHER_PAPER` is
retained solely to reproduce the golden set.

### 15.3 Detector: Si:Li, crystal thickness 0.5 cm

He specified Si:Li → 0.5 cm crystal, SDD → 0.04 cm, radius 0.3 cm fine (~30 mm²). Ours was
0.3 cm — neither. Production uses **0.5 cm (Si:Li**, his paper's detector). Smoke-tested: the
change is real and correct — Bi Kα1 (77 keV) detector efficiency rises from 0.150 (0.3 cm) to
0.237 (0.5 cm), as a thicker crystal should capture more hard X-rays. Soft lines are unchanged
(already ~1.0).

### 15.4 Electron counts: two different noises, and a correction

His guidance: run 10⁶ electrons for thick samples, **10⁷ for thin**, to get >10,000 X-ray
counts so relative noise is <1%.

Measured "Counts original" (the simulator's raw characteristic-count statistics) at 10⁶:

| foil | counts | ≈ noise | |
|---|---|---|---|
| 2 nm | 749 | 3.7% | **thin → 10⁷** |
| 8 nm | 2,985 | 1.8% | **thin → 10⁷** |
| 16 nm | 5,933 | 1.3% | **thin → 10⁷** |
| 32 nm | 11,734 | 0.9% | ok at 10⁶ |
| 1024 nm | 286,683 | 0.19% | ok at 10⁶ |

The cutoff is clean at ≤16 nm. Production runs 2/4/8/16 nm at 10⁷, the rest at 10⁶. (The 2 nm
foil still reaches only ~1.2% even at 10⁷; within his "negligible" and not worth 1.3×10⁷.)

**Correction to §13.5.** §13.5 stated "raising the trajectory count cannot improve counting
statistics." That conflated two distinct noises:

- **Monte-Carlo estimation noise** — how precisely the sim estimates the true expectation.
  = 1/√(Counts original). *Improves* with electron count. This is Walther's point, and our
  thin runs at 10⁶ were under-sampled.
- **Physical Poisson noise** — what a real detector sees for the fixed 100 s × 1 nA
  acquisition. Set by current × time, not electron count. This is what §13.5 was right about.

The reported intensity *value* does not change with electron count (§13.5's measurement
stands); its *precision* does. So more trajectories help the simulation, not the modelled
experiment.

⚠ Still standing: `BeamCurrent` and `AcquisitionTime` set the absolute photon counts and are
**not** on the locked-parameter list (§13.5). Unchanged from golden here, but they deserve an
explicit decision.

### 15.5 The k-factor point — what it defuses

Walther's most consequential remark: the choice of density model is **negligible for the final
result**, because k\*-factor calibration is self-correcting against a density offset — it
cancels in the calibrate-then-invert round trip. This directly addresses the §13.3–13.4
headline (the ~9% divergence in inferred thickness at the thick end): that offset is expected
to largely cancel when k\* is calibrated and inverted on the same density assumption. So the
density model is fixed for *correctness*, not because the last few percent change the answer.

**It does not cover Monte-Carlo noise** (random, uncorrelated — does not cancel in a ratio),
which is why §15.4's thin-sample requirement stands on its own.

### 15.6 Code changes

- `RunSpec.density_model` now selects `WALTHER_REVISED` (default, production: 5.32 + 1.86x) or
  `WALTHER_PAPER` (5.32 + 0.20x, retained only to reproduce the golden set). The TIXIER
  lattice model and its constants were removed.
- `RunSpec.detector_crystal_thickness_cm` added, default 0.3 (golden), production 0.5. The
  `.mic` moved from byte-copy to templated for that one field; crystal radius and everything
  else still pass through byte-for-byte.
- The golden fixture pins `density_model=WALTHER_PAPER, detector_crystal_thickness_cm=0.3`
  explicitly, so the byte-for-byte golden gate is unaffected. **95 tests green, gate clean.**

### 15.7 The production re-run — completed

15 runs (Set A 10 + Set B 5), single production density model, 0.5 cm Si:Li detector,
2/4/8/16 nm at 10⁷ and the rest at 10⁶. run_id `GaAsBi_<t>nm_x<xxx>_rho<dddd>` (ρ×1000), so
these do not collide with the obsolete `_wal_`/`_tix_` runs. **The 30 comparison runs of §13
are superseded** — wrong density and wrong detector — but retained as the evidence behind the
ρ·t divergence finding (§13.3), which stands regardless of the absolute density.

**Completed 2026-07-19: all 15 runs exit 0, all CSVs present, 127.2 minutes serial.** The four
thin foils at 10⁷ took ~22 min each (88 min of the total); everything else ran at 10⁶.
Verified after the fact:

- **Set A physics correct** — all three ratios (Ga K/L, As K/L, Bi L/M) rise monotonically
  across every thickness under the new density and detector, the shape reproducing Walther's
  Fig. 1.
- **Set B scales cleanly** with composition; the x=0.1 point reproduces the validation
  configuration at archival dose (the free consistency check of §11.2).
- **Integrity:** all 15 CSVs have 21 rows, no negative intensities, no failures.

This is the definitive dataset. Everything earlier — the golden validation run and the 30
comparison runs — was scaffolding to reach it.

**One finding surfaced from Set B's low-x point** (x=0.01, checked directly): the simulation is
well-sampled (26,387 raw counts, past Walther's threshold), so the *simulated* Bi L/M = 1.382
is precise — but the Bi lines carry only ~117 detected photons because Bi is 1% by weight, so a
*real* detector at 100 s / 1 nA would see ~14% Poisson scatter on that ratio. This is a
**result**, not a defect: it is the statistical floor the composition arm exists to map, and
crucially it cannot be reduced by more electrons (physical noise, not MC noise — the §15.4
distinction). Only more dose would help. The simulated expectation is used as-is.

### 15.8 Still open after this session

- **Stage 5 (aggregator) is now unblocked** — the 15 production tables exist; concatenating
  them into one provenance-tracked table + manifest is the natural next build.
- **The obsolete 30 comparison runs remain in `Results\`** alongside the 15 production ones
  (~570 files, flat, clearly named `_wal_`/`_tix_` vs `_rho5xxx`). Not yet cleared — retained
  as the ρ·t divergence evidence unless Ethan decides otherwise.
- **Recovered x, the k\* round trip, the verdict** — Stage 7, Ethan's, untouched.

---

## 16 — Stage 5: aggregator + provenance manifest

*Built 2026-07-19, after the production re-run. `mcxray_wrapper/matrix.py` (Stage 4) +
`mcxray_wrapper/aggregate.py` (Stage 5). 7 new tests, 102 total, golden gate still clean.*

### 16.1 What it produces

Two files in a new `C:\MCXRAY\Sim\Aggregated\` directory (a sibling of `Results\`, never
inside it — `Results\` stays the flat raw store, indexed *by* the manifest, not written into):

- **`combined_intensities.csv`** — 315 rows (15 runs × 21 lines). Every parsed line from every
  production run, with each run's spec parameters (x_bi, thickness_nm, n_electrons,
  density_model, mass_density, detector thickness) attached as leading columns. Self-contained:
  each intensity row carries the run conditions beside it, so Stage 6/7 can plot ratio-vs-
  thickness without any cross-reference.
- **`provenance_manifest.json`** — one entry per run linking run_id → spec → the six input
  files (in `Sim\`) → the intensity CSV and a count of all 19 output files (in `Results\`).

### 16.2 Design, per governance

- **Raw only.** No ratios, k-factors, or corrections — those are Stage 6, reading this table.
  A test (`test_no_derived_columns_are_added`) fails if a ratio/k-factor column ever appears.
  This preserves the load-bearing rule: the open atomic-data questions (Lα2 folding, Bi
  M-lines) mean derived numbers may need re-deriving, and that must be possible from this table
  without re-simulating.
- **Driven by the matrix, not by globbing.** `production_matrix()` is the authoritative 15-run
  list; the aggregator resolves each spec to its files. The obsolete `_wal_`/`_tix_` runs in the
  same `Results\` directory are therefore never picked up — confirmed, they are absent from the
  output.
- **Provenance is verified, not labelled.** For each run the stored `.sam` is re-read and its
  density and Ga weight fraction checked against the spec. A run_id pointing at a mismatched
  file fails the whole aggregation loudly (`test_sam_not_matching_spec_fails_loudly`) rather
  than mislabelling data. On the real 15: all 15 verified, 19 output files linked each.

### 16.3 Consequence

The run-and-store half of the wrapper (Stages 1–5) is complete end to end: generate → run →
parse → aggregate, every stage gated. `Aggregated\combined_intensities.csv` is the clean input
to Stage 7 — including the test of whether Walther's "density cancels in the k\* round trip"
claim (§15.5) holds in practice. That analysis is Ethan's.

---

## 17 — Stage 6: the three diagnostic ratios

*Built 2026-07-25. `mcxray_wrapper/ratios.py`. 7 new tests, 109 total, golden gate clean. This
is the *ratios* half of Stage 6; sum-peak synthesis is separate and still gated on the pile-up
spike.*

### 17.1 What it produces

`Aggregated\diagnostic_ratios.csv` — one row per run (15), carrying the run metadata plus the
three diagnostics, **each under both line definitions**:

`Ga_K_L`, `As_K_L`, `Bi_L_M`, each with a `_principal` and a `_summed` column (six ratio
columns total). Computed from the `Intensity Emitted Detected (photons)` column of the stored
aggregated table — the measured-count quantity (CLAUDE.md) that reproduces Walther's curves.

### 17.2 The line-definition decision (Ethan, 2026-07-25)

The ratios can define each shell's intensity two ways, and they differ by ~40–90% — not
cosmetic:

- **principal** — the single strongest line (Ka1, La, Ma). Clean, well-separated, overlap-free.
- **summed** — all reported sub-lines in the shell. More counts, but includes lines that
  physically overlap other elements (Ga Kβ on As Kα / Bi Lα — Walther's issue (i)).

| | Ga K/L principal | Ga K/L summed | Bi L/M principal | Bi L/M summed |
|---|---|---|---|---|
| 100 nm, x=0.2 | 1.507 | 2.106 | 1.508 | 2.821 |
| 1024 nm, x=0.2 | 3.831 | 5.811 | 2.923 | 5.476 |

**Decision: store both**, deferring the choice for inversion to Stage 7. This fits the
store-raw-derive-cheaply rule and forces no premature science commitment. Note `La` is already
Lα1+Lα2 physically (Walther: "usually indistinguishable"; MC X-Ray reports one `La`), so
"principal" is not discarding Lα2.

### 17.3 Verification

All six ratio columns rise **monotonically with thickness** across Set A under both definitions
— the shape that reproduces Walther's Fig. 1. Governance guards in the tests: a zero denominator
raises (not silent inf), a missing principal line raises, and a test fails if any k-factor /
correction / inverted-x column ever appears — ratios only, nothing derived beyond them.

### 17.4 What remains in Stage 6 — sum-peak synthesis

**Pile-up spike resolved (2026-07-25): MC X-Ray cannot build sum peaks itself.** So the route is
now decided — **analytic synthesis**: add a modelled pile-up onto the stored Bi Mα (never a
re-run). This is the fallback the blueprint anticipated, now the confirmed path.

The physics, from Walther's paper: the sum peak is **Ga Lα + As Lα** landing on Bi Mα
(1098 + 1282 = 2380 eV vs 2423 — one resolution element; "no standard solid-state detector could
distinguish"). Each pile-up event consumes one Ga Lα and one As Lα photon to fake one Bi Mα
count — his correction "transferred 600 counts from Bi M to *each* of Ga L and As L." His
measured level was ~600 counts ≈ 15% of the Ga L / As L intensities, found by iterative fitting
on one spectrum; the project models a **sensitivity sweep at 0.1% / 1% / 10%, never 15% as a
default** (CLAUDE.md).

**Not built yet — needs a modeling spec** (see CURRENTLY_RELEVANT.md "Sum-peak synthesis"). It
touches the low-Bi measurability conclusion directly, so the modeling choices (exact lines,
what the fraction multiplies, whether Ga/As L are depleted to conserve photons) are surfaced for
Ethan/Walther rather than chosen unilaterally.

---

## 18 — The Set A k\* table, the "A" resolution, and a literature cross-check

*2026-08-13. `kfactors.write_calibration` added (1 new test, 133 total, golden gate clean).
Output: `Aggregated\kstar_calibration_setA.csv`. No simulations re-run.*

### 18.1 The table

`calibration_curves()` had existed since 2026-08-03 but its output was never persisted — the
Set A table only existed while the function was running. `write_calibration` now writes it,
mirroring `ratios.write_ratios` exactly (read the stored combined table, compute, one file out).

**240 rows = 10 thicknesses × 12 element/shell pairs × 2 line definitions**, i.e. 24 curves of
10 points each, all at x = 0.20. Asserted from the file, not from prose: `x_bi` has exactly one
distinct value; every (route, heavy_shell, light_shell, definition) group has exactly 10 points.

The curves split into two families, and the split is the whole content of the table:

| Family | Behaviour, 2 → 1024 nm |
|---|---|
| Hard (K) line denominator | flat — worst case 3.7% |
| Soft (L) line denominator | collapses — up to 4.95× |

Soft L photons are absorbed on the way out of the foil; k\* absorbs that loss. Extremes
(principal definition): **Bi Lα ÷ As Kα, 2.4192 → 2.4034 (0.7%)** and **Ga Kα ÷ As Lα,
0.7665 → 0.1548 (4.95×)**.

Running `invariance_check()` on Set B alongside it puts the same pair in front on the second
axis too: **relative spread 0.0001 across x = 0.01–0.20**, against 0.0011 for the next best.
`Bi_As L/K` is invariant in thickness *and* in composition.

### 18.2 The "A" currency question — RESOLVED

Carried as an open question since `kfactors.py` was written (§ its module docstring): the paper
glosses *A* as "atomic densities", but the Cliff–Lorimer weight-fraction form of Eqs (2), (4),
(9) needs only atomic **weight**.

**Answer (Walther, personal communication to E. Pratt, August 2026): *A* is the atomic weight.
ρ is the atomic density — a separate quantity that does not enter those equations at all.** The
paper's gloss had conflated the two.

Consequences:

- `ATOMIC_WEIGHTS` (IUPAC/CIAAW 2024, `spec.py`) is the **correct** currency, not a placeholder.
  Cross-referenced there and in `kfactors.py`.
- Every k\* already computed is correct in **absolute** terms, not merely up to a cancelling
  factor. **No stored number changes value** — the answer removes a caveat, it does not
  invalidate anything. (A always cancelled in a same-route calibrate-then-invert round trip;
  what it blocked was absolute reporting and literature comparison.)
- Comparison against the published k\* values becomes legitimate. See 18.3.

### 18.3 Cross-check against Walther 2025, Figure 4

Figure 4's caption quotes **k\*<sub>BiL,AsK</sub> ≈ 2.490 ± 0.071**, "almost constant for
thicknesses up to 1 µm as both X-ray lines are of very similar energy, so the selection of this
line pair would also seem well suited for quantification."

That is the same pair this calibration independently identifies as flattest of the 24 — found
from the data, not by looking for it.

| | |
|---|---|
| This work, Set A mean | **2.4161** ± 0.0051 (2–1024 nm) |
| Walther 2025, Fig. 4 | 2.490 ± 0.071 |
| Difference | −3.0% relative, **1.04σ** |

**Stated precisely: just *outside* his quoted 1σ, not inside it.** Our thinnest-foil value
(2.4192) lands on his lower bound (2.419).

Arrived at independently on every axis — a different simulation code, a **6.2% higher density**
(5.692 vs his 5.36 at x = 0.2), and a direct algebraic solve from known *x* rather than his
k × escape-fraction decomposition. A few percent offset is what those differences predict, and
the agreement is quantitative support for his "density largely cancels" claim (§15.5).

The qualitative claim reproduces and extends: 0.7% drift over 512× in thickness, plus 0.01%
spread across x = 0.01–0.20, which Figure 4 does not test.

### 18.4 Figure-by-figure status against the paper

| Walther figure | Content | Status |
|---|---|---|
| Fig. 1 | Ga K/L, As K/L, Bi L/M ratios vs thickness (MC) | **Reproduced** — §17, `diagnostic_ratios.csv` |
| Fig. 2 | Measured EDXS spectrum, JEOL 2010F | Not reproducible — real acquisition |
| Fig. 3 (top) | k\* Bi-vs-Ga **vs thickness** | **Reproduced** — `kstar_calibration_setA.csv` |
| Fig. 3 (bottom), 4, 5 | k\* **vs the heavy element's K/L ratio** | **Not yet** — both halves exist in `Aggregated\`, unjoined |
| Figs. 6, 7 | ADF-STEM images, column statistics | Out of scope |

### 18.5 Consequence — the K/L re-indexing, and a weakness it exposes

Figs 3–5 plot k\* against the heavy element's **K/L ratio**, not thickness, and the paper is
explicit about why: it "reduces both the dependence on real foil thickness measurements and the
effect of detector sensitivities changing with detector type or entrance window thickness …
providing an inherent self-calibration."

This exposes something in the round trip. `roundtrip.py` (§ its docstring) looks up k\*(100 nm)
using the **known** thickness of the Set B runs — see `_interpolate_k_star(calibration[key],
target_thickness)`. A real experimenter does not have that. **The round trip is held out in *x*
but not in *t*: it is handed one of the two unknowns.**

Re-indexing the calibration on the measurable K/L ratio makes it held out in both, and
reproduces three published figures at the same time. Unblocked, no new simulations, no pending
decisions — both input tables are already in `Aggregated\` and join on `run_id`.

### 18.6 Not addressed here

- Stage 7 parts 1–3 (`kfactors.py`, `roundtrip.py`, built 2026-08-03/05) have **no REPORT
  section** — the record jumps from §17 to this one. A gap worth closing.
- Sum-peak synthesis remains blocked on its modelling decisions, now **four** (see
  CURRENTLY_RELEVANT.md). None had been put to Walther as of 2026-08-13.

---

## 19 — Stage 7: the Set B invariance check, persisted

*2026-08-13. `kfactors.composition_curves` + `write_composition_curves` + `write_invariance`
added (6 new tests, 149 total, golden gate clean). Outputs:
`Aggregated\kstar_composition_setB.csv` (120 rows) and `Aggregated\kstar_invariance_setB.csv`
(24 rows). No simulations re-run.*

### 19.1 Why it exists

k\* is supposed to be a property of the **instrument and the line pair**, not of the specimen's
composition. Walther's equations already carry the composition dependence explicitly in the
prefactor (*x*, *x*/(1−x), 1/(1−x)), so dividing that out should leave a constant.

This is not bookkeeping. **The inversion assumes k\* is transferable** from a calibration to an
unknown; if k\* depended on *x*, you would need *x* to obtain the k\* that yields *x* — circular,
and the recovery would need an iterative scheme rather than a lookup. `invariance_check()` is
the test that it doesn't.

`invariance_check()` had existed since 2026-08-03 but its output was never written to a file —
the table lived only while the function ran. It is the strongest single result in the repo and
was the least durable thing in it.

### 19.2 Two files, not one

`composition_curves()` was added as the Set B mirror of `calibration_curves()`, and is persisted
in its own right. The summary reports mean/min/max/spread, which **cannot distinguish a
systematic drift from Monte-Carlo scatter** — and that distinction is the whole interpretation.
The curves are the evidence; the summary is the verdict on them.

That separation immediately paid: **all 24 curves are strictly monotonic in *x*. Zero are
non-monotonic.** The drift is systematic everywhere it appears, with no scatter anywhere — so
MC noise sits below the drift across the board, and every non-flat route is responding to real
physics rather than statistics.

### 19.3 Result

Relative spread (max−min)/mean across x = 0.01 → 0.20 at 100 nm sorts almost perfectly by
**line softness**:

| Routes | Spread |
|---|---|
| Both lines hard — Bi Lα÷As Kα, Bi Lα÷Ga Kα, Ga Kα÷As Kα | 0.0001 – 0.0011 |
| One soft line at 2.4 keV — Bi Mα÷Ga Kα, Bi Mα÷As Kα | 0.007 – 0.008 |
| Anything against Ga Lα (1.098 keV) or As Lα (1.282 keV) | 0.017 – **0.054** |

The four worst all involve **Ga Lα**, the softest line in the system. That ordering is the tell:
the drift is not the equation form failing, it is absorption tracking the density change across
Set B (ρ = 5.339 → 5.692 g cm⁻³, 6.6%), so ρt changes and soft-line escape changes with it.

**On the routes where absorption is negligible, k\* is constant to ~1 part in 10⁴ across a 20×
change in *x*.** That is strong evidence the *x* and *x*/(1−x) prefactors are exactly right —
and it is a separate confirmation from the literature cross-check in §18.3, because it tests the
equation's *form* rather than its absolute value.

### 19.4 One route is invariant to the limit of resolution

Measured against this project's own established Monte-Carlo noise floor — **0.037%**, from
byte-identical inputs under `RandomNumberSeed=0` (§ the seed finding) — exactly one route's
entire drift sits below it:

**Bi Lα ÷ As Kα, principal: 0.0062% across x = 0.01 → 0.20.**

Six times smaller than the noise floor, i.e. composition-invariant to the limit of what the
simulation can resolve. Every other route has a resolvable, systematic drift.

Combined with §18's thickness result (0.7% over a 512× change in *t*), `Bi_As L/K` is the only
route in the matrix that is flat on **both** axes. That is what makes it the standout, rather
than merely the flattest curve on one plot — **and it remains the route sitting on overlap (i)**
(As Kα1 10.543 keV vs Bi Lα 10.840 keV, 297 eV apart), which is the tension the dissertation
turns on.

### 19.5 Ground the paper does not cover

Walther's Figs 3–5 show two compositions (x = 0.1 and 0.2). Set B has five, reaching down to
x = 0.01 — the region where the measurability question actually lives. Nothing in the paper
tests invariance at that granularity.

**Limitation to keep attached:** Set B is 100 nm only, so invariance is demonstrated at a single
thickness. Whether it holds at low *x* **and** high *t* is untested — the corner P2.2 would fill
(see CURRENTLY_RELEVANT.md).

---

## 20 — Bi K lines admitted to the analysis (LO3), and what they revealed

*2026-08-13. `SHELLS[BI]` gains a `K` entry; `ROUTES` gives Bi three heavy shells (K, L, M)
instead of two. 149 tests green, golden gate clean. All derived tables regenerated: calibration
240 → **320 rows**, K/L index 240 → **320**, Set B curves 120 → **160**, invariance 24 → **32**,
round trip 120 → **160**. No simulations re-run.*

### 20.1 Why

LO3 reads "the absorption of bismuth **K**, L, and M lines relative to either gallium K or L or
arsenic K or L as reference." The analysis covered L and M only. The Bi K lines were parsed and
stored from the start (Ka1 77.097, Ka2 74.805, Kb1 87.335, Kb2 89.833 keV) but never used.

This had been carried as an open question — *does LO3 really want Bi K, given Walther calls them
"too hard for any standard EDS detector"?* That framing was backwards. The objective names them,
so the defensible move is to include them and **measure** the failure rather than assert it.

Adding a third Bi shell made every hermetic fixture fail on the missing-principal-line guard.
That is the guard working: a shell cannot be silently half-present.

### 20.2 The result inverts the expectation

The prediction was that Bi K would be a poor route. **In the simulation it is the best one.**

| | Bi K routes | All other routes |
|---|---|---|
| Composition invariance, `Bi_As K/K` | **0.0009** | 0.0001 – 0.054 |
| Thickness drift, `Bi_As K/K`, 2→1024 nm | **8%** | 0.7% – 495% |
| Round-trip recovery, mean abs error | **0.00177** | 0.00496 |

Bi Kα1 at 77 keV is barely absorbed by anything, so the routes pairing it against Ga Kα or As Kα
are close to absorption-immune. k\* sits around 250 (Bi–As) and 294 (Bi–Ga) — roughly **100× the
Bi L values**, because k\* goes as 1/I(Bi), so they will never share an axis with the Bi L/M
routes and must be plotted on their own scale.

### 20.3 Why it is nevertheless unusable — and the number is dose-independent

The photon yield settles it. Across all 15 production runs:

**I(Bi Lα) / I(Bi Kα1) = 103.0** (min 96.6, max 104.3)

This ratio is **independent of dose** — `BeamCurrent` and `AcquisitionTime` cancel in it, which
matters because those two were inherited from the golden files and never explicitly decided
(they remain an open item). It is also near-independent of thickness and composition.

So Bi K delivers ~103× fewer detected photons than Bi L for the same acquisition, and equal
counting statistics would require **~10⁴× the dose**. Poisson uncertainty at the stored dose:

| Line | Worst case in the matrix | Best case |
|---|---|---|
| Bi Kα1 | 0.41 photons → **157%** | 215 → 6.8% |
| Bi Lα | 42.3 → 15.4% | 20818 → 0.69% |
| Bi Mα | 30.5 → 18.1% | 7121 → 1.19% |

That is the LO3 answer, quantified: **Bi K fails on counting statistics, not on absorption.**
On absorption it is the *best* route in the matrix. Stating it that way is a stronger and more
specific result than repeating "too hard for standard EDS."

### 20.4 The structural gap this exposes

The simulation reports **expectation values**, and the k\* algebra closes on them regardless of
how few photons underlie the number. That is why 0.4 photons still produces an excellent
recovered *x*.

**Nothing in the pipeline models counting statistics.** Absorption is modelled; the overlaps
will be (Stage 6b); Poisson noise is not, anywhere.

This matters well beyond Bi K. The dissertation asks at what *x* Bi stops being measurable, and
measurability is fundamentally a counting-statistics question. At x = 0.01 and 100 nm the stored
Bi Lα intensity is 116 photons — 9.3% Poisson — and Bi Mα is 76 photons at 11.4%. Those
uncertainties propagate straight into recovered *x*, and at present nothing carries them.

**Counting statistics may well dominate the low-x failure mode ahead of either peak overlap.**
Added to the roadmap as P1.3 — unblocked, needing no input from Walther, since it is standard
Poisson propagation applied to intensities already stored.

---

## 21 — Walther's reply: the Bi M discrepancy confirmed and re-explained

*2026-08-13. Walther, T., personal communication to E. Pratt. No code change; this section
records what the answers settle and what they change.*

### 21.1 The discrepancy is corroborated without eyeballing

§18–20 reported that every route containing Bi M sits ~1.4–1.6× above his published curves.
**That figure was read off his printed figures by eye** — none of the three caption constants
covers a Bi M route, so nothing quantitative backed it.

His reply supplies an independent number in text: **his simulated Bi L/M ratio is ≈ 1:1.**

| | Bi L/M, principal |
|---|---|
| This work, 100 nm | **1.515** |
| Walther, simulated | ~1.0 |
| Walther, measured | ~0.667 (2:3) |

**Ours is 1.51× his** — inside the eyeballed range, from a value he wrote down rather than one
read off a plot. The claim no longer depends on figure reading.

Since our Bi **L** routes reproduce his published constants to 3% (§18.3), the deduction is
clean: Bi L is right, therefore **our Bi Mα is ~1.5× weaker than his**.

### 21.1b Third confirmation: his Figure 1, and the factor pinned to 1.506 +/- 0.020

*Added 2026-08-14, on seeing his Fig. 1 for the first time.*

Fig. 1 plots the same three diagnostic ratios against thickness that this project computes, so
it is a direct four-point comparison. **It is CASINO, not MC X-Ray** (REPORT 13, 15), which
makes the agreement below a cross-code result rather than a self-check.

Values read off his plotted markers, against ours (principal definition, x = 0.20):

| t (nm) | Ga K/L | As K/L | Bi L/M |
|---|---|---|---|
| 128 | 1.08x | 1.01x | **1.51x** |
| 256 | 1.03x | 0.97x | **1.52x** |
| 512 | 1.01x | 0.96x | **1.51x** |
| 1024 | 0.98x | 0.95x | **1.48x** |

**Ga K/L and As K/L agree to within reading error** across two different simulation codes. Since
both share the same 6.2% density difference, that also disposes of density as an explanation for
anything here.

**Bi L/M is a flat 1.506 +/- 0.020** over an 8x thickness range. This is the strongest form of
the Bi M evidence so far, and the third independent line of it:

| Evidence | Factor |
|---|---|
| Eyeballed off his Figs 3 and 4 (21.1) | 1.4-1.6x |
| His stated simulated L/M ~ 1:1 vs ours 1.515 | 1.51x |
| **His Fig. 1, four thicknesses** | **1.506 +/- 0.020** |

A scale factor that constant, over that range, is a fixed difference in I(Bi Ma) -- not an
absorption effect, which would vary with path length. It confirms by measurement what 21.1
deduced from the algebra.

**A speculation corrected.** It was suggested that CASINO's inability to resolve sub-lines might
mean his ratios are whole-shell sums, and that ours should therefore be compared under the
`summed` definition. The numbers refute it: summed gives Ga 1.48x, As 1.24x, Bi 2.77x -- all
markedly worse. CASINO reporting one line per shell IS the principal definition, so the existing
comparison was correct as it stood.

**Caveat.** The readings are off a printed plot, so about +/-0.05. The 1.5x sits far outside
that; the Ga/As agreement is at the edge of it, and should be reported as "within reading error"
rather than as specific percentages.

### 21.2 The mechanism proposed in §20 was wrong

§20 hypothesised that his "Bi M" was the whole M band while MC X-Ray reports only Mα. **That is
not the explanation.** His answer: *"I think CASINO only simulates Bi M_alpha only and MC X-ray
probably also, however, the references may numerically differ."*

Both codes model Mα alone, so band coverage cannot produce the gap. The cause is a **code-to-code
difference in the Bi Mα atomic data** — cross-section, fluorescence yield or transition
probability. Right quantity, wrong mechanism.

His "probably" about MC X-Ray is confirmed from our side: the parsed output carries exactly one
Bi M line (`Line Ma`) in all 21 rows. **This also closes the standing open question** "are Bi
M-lines beyond Mα modelled?" — nothing beyond Mα is reported, so nothing beyond Mα is usable.

### 21.3 A separate result: the simulation → experiment M-band factor

His table of the Bi M series, with relative intensities, for simulated Mα1 = 100:

| Line | Transition | Energy (keV) | Relative |
|---|---|---|---|
| Mζ | M5–N3 | 2.213 | 1.6 |
| Mα2 | M5–N6 | 2.411 | 5.2 |
| **Mα1** | M5–N7 | **2.423** | **100** |
| Mβ | M4–N6 | 2.526 | 62.4 |
| Mγ | M3–N5 | 2.738 | 5.1 |

Sum of the non-Mα1 lines = **74.3**, so a measured spectrum contains **174.3** where the
simulation produces 100 — **×1.743**.

This is *not* the explanation for §21.1; it is a **simulation → experiment conversion**. Both
codes emit Mα only; a real detector sees the whole unresolved band. Mβ dominates it (62.4 of
74.3) and sits 103 eV from Mα — comparable to the Bi Lα1/Lα2 separation this project already
treats as unresolvable.

It matters directly for Stage 6b: **the sum peak lands on the experimental M peak, not on the
simulated Mα.** Sources he cites for the relative strengths: Salem et al. (At. Data Nucl. Data
Tables, S0092640X74800197), Phys. Rev. A 78 022518, and J. Anal. At. Spectrom. 10.1039/d6ja00069j.

### 21.4 Sum peak: where it is applied — DECIDED

> *"The sum peak correction was only applied to the experimental spectrum, not to simulations.
> This is because our detector was rather slow. The correction was chosen so that the Bi L/M
> ratio measured (about 2:3) would agree better with the simulation (about 1:1)."*

Two consequences, both load-bearing for P3.1:

**The artefact belongs on the unknown only, never the calibration.** His k\* comes from
simulation (clean); his unknown is a measurement (corrupted). That is the
**calibrate-clean → invert-corrupted** variant — the one that does *not* self-cancel, and so the
one where the induced error is largest. This resolves the fourth modelling decision (added
2026-08-13, flagged as changing the answer more than the other three).

**His 600 counts was fitted, not measured.** The magnitude was chosen to force his measurement
into agreement with his simulation. It is therefore entangled with *his* Bi M value — which
§21.1 shows differs from ours by ~1.5×. **The 15% figure is not transferable to this pipeline**,
which vindicates the standing decision to sweep 0.1 / 1 / 10% rather than adopt it as a default.

### 21.5 Exposure — SETTLED

> *"The probe current was not measured but will have been about 1nA (my estimate). 743 s total
> acquisition time, 3.7% deadtime mean that the livetime will have been 715.5s."*

Reference acquisition: **1 nA × 715.5 s live**. This project's runs already use 1 nA, so the
scale factor from the stored 100 s basis is exactly **7.155** — and the linearity was verified
against the stored table in the exposure analysis (photons = photons/e/sr × dose × solid angle
0.0176 sr × detector efficiency, efficiency correlation 1.0000). **No re-runs required.**

The current is his estimate, not a measurement, so it carries unstated uncertainty. P1.3
therefore still sweeps dose, with 1 nA × 715.5 s as the labelled reference point rather than a
hard assumption.

### 21.6 What remains open on the sum peak

His answer reframes rather than closes the first three modelling questions: the magnitude he used
was obtained by *fitting to agreement*, not derived from a pile-up rate. So "what the fraction
multiplies" has no published answer to inherit — it is a modelling choice for this project,
which should be stated as such and swept.

---

## 22 — Stage 3 rebuilt: the executor

*2026-08-13. `mcxray_wrapper/executor.py` + `tests/test_executor.py` (15 new tests, 164 total,
golden gate clean). Validated end-to-end against the real simulator on a quarantined run_id,
then the artifacts removed.*

### 22.1 Why it had to be rebuilt rather than promoted

`CURRENTLY_RELEVANT.md` had described Stage 3 for weeks as *"works as a script
(`scratchpad/rerun_production.py`); not yet a module"* — which read as a tidy-up job. It was
not. The script lived in a **Claude session scratchpad**
(`AppData\Local\Temp\claude\<project>\<session-id>\scratchpad\`), a per-session temp directory
cleared when the session ends. It ran the 15 production simulations and was swept.

Confirmed by inspection: ~130 prior scratchpad folders exist for this project and **every one is
empty**. Nothing was deleted by the user; the file was never in the repo.

**Consequence, stated plainly: the 15 production runs were executed by something that no longer
existed, so the run *step* was not reproducible.** Their inputs, all ~19 outputs each, and the
provenance manifest were unaffected — no scientific data was lost — but a simulation project
whose simulations cannot be re-launched is a fair target for an examiner.

This is a governance lesson as much as a build one. `CLAUDE.md` says *assert from files, never
from prose*; that applies to the project's own status notes, not only to the vendor's
documentation. The status file asserted a script that had not existed for some time, and nobody
checked the disk.

### 22.2 What it does

Interface, from CLAUDE.md and re-confirmed against the stored runs:

```
console_mcxray_lite_x64.exe --simulation-file <run_id>.sim      cwd = C:\MCXRAY\Sim
```

Only the `.sim` is named; it resolves its five siblings **by name** from the same directory —
hence inputs flat in `Sim\`, and cwd set there. The `.par` carries
`BaseFileName=Results/<run_id>`, so the 19 outputs land in `Sim\Results\` under a `<run_id>_`
prefix.

`run_simulation(spec)` generates the six inputs, invokes the simulator, and verifies the result.
`run_matrix(specs)` loops serially, continuing past failures by default (an unattended sweep is
more useful finishing and accounting than halting on run 3 of 15).

### 22.3 Two failure modes, deliberately distinguished

- **crash** — non-zero exit, or timeout. Stderr is surfaced in the result, not swallowed.
- **sim failure** — **exit status 0 but no usable primary output.** This is the dangerous one:
  the simulator can return success having written nothing, and a loop checking only
  `returncode` would report a clean sweep over missing data. The check is that
  `<run_id>_XrayIntensities.csv` exists and is non-empty.

A run producing other than 19 output files is reported in `detail` but still counted as ok —
the primary output exists, so the run is usable, but a changed file count suggests the interface
understanding may be wrong, which CLAUDE.md says to surface immediately.

### 22.4 Overwrite protection

`Results\` holds the 15 definitive production runs, flat and unversioned. **A run whose outputs
already exist is refused** (`status="skipped"`) unless `overwrite=True` is passed explicitly.
The guard is on outputs, not inputs: regenerating input files is harmless and deterministic;
destroying simulated results is not.

Prefix matching requires the trailing underscore, so `RUN_x01` does not match
`RUN_x010_...` — without that boundary the guard would both refuse unrelated runs and let a
narrower run_id appear already-run.

Verified against the real directory: attempting to re-run `GaAsBi_2nm_x020_rho5692` is refused,
naming the 19 existing files.

### 22.5 Validation

15 hermetic tests run a **stand-in executable** (a Python script driven through the same
`--simulation-file` interface, fabricating the same output naming) against `tmp_path` — never
MC X-Ray, never the real directories. The two load-bearing tests are the overwrite guard (which
asserts the pre-existing file is byte-identical afterward) and the exit-zero-without-output
case.

Then one **real** end-to-end run, on a quarantined run_id that could not collide
(`SMOKETEST_20260813_2nm_x020`, 2 nm, 10⁴ trajectories):

| | |
|---|---|
| Status | completed, exit 0, **5.6 s** |
| Output files | **19**, as expected |
| Parsed by `parse_xray_intensities` | **21 rows**, Ga/As/Bi, all 9 Bi lines |
| Files added to `Results\` | 19 |
| **Files removed or modified** | **0** |

Generate → run → parse proven on the real binary. The 25 artifacts (6 inputs, 19 outputs) were
then deleted under a prefix guard; `Results\` returned to its prior 1007 `GaAsBi_*` files.

### 22.6 What this unblocks

Any re-run, the low-x/high-t corner probe, and the possible x = 0.10 sweep (P2.2) — none of
which could have been attempted before. It also closes the reproducibility hole independently
of whether the matrix is ever extended.

---

## 23 — Set C: the low-x thickness arm, and what it proves about the matrix design

*2026-08-13. Six new runs (x = 0.01, 32–1024 nm), executed with the rebuilt Stage 3 executor in
25.4 min, all clean. `matrix.py` gains `extension_matrix()` and `full_matrix()`; 167 tests green.
Aggregated table 315 → 441 rows.*

### 23.1 Why these six runs

Sets A and B form a **cross**: A sweeps thickness at x = 0.20, B sweeps composition at 100 nm.
Nothing sat at **low x *and* high t** — precisely where the Bi signal is weakest and the
absorption path longest, i.e. where "at what x does Bi stop being measurable" is answered.

The prior assumption was that the interior could be interpolated, absorption being a function of
**ρ·t**. Set C tests that assumption directly.

### 23.2 The frozen 15 are untouched — verified, not asserted

`production_matrix()` still returns exactly the original 15. `extension_matrix()` adds Set C;
`full_matrix()` is all 21. This matters because every result derived before today came from that
list, and the Set A / Set B filters in `kfactors.py` and `roundtrip.py` are defined against it.

Checksummed before and after re-aggregating on all 21 runs:

| File | Status |
|---|---|
| `combined_intensities.csv` | changed (315 → 441 rows) |
| `diagnostic_ratios.csv` | changed (15 → 21 rows) |
| `provenance_manifest.json` | changed (21 runs) |
| `kstar_calibration_setA.csv` | **byte-identical** |
| `kstar_composition_setB.csv` | **byte-identical** |
| `kstar_invariance_setB.csv` | **byte-identical** |
| `kstar_vs_kl_ratio_setA.csv` | **byte-identical** |
| `roundtrip_recovered_x.csv` | **byte-identical** |
| `roundtrip_summary.csv` | **byte-identical** |

Set C is x = 0.01 and never at 100 nm, so the Set A/Set B filters exclude it structurally.
Adding data **cannot** silently alter an existing result.

### 23.3 Result: ρ·t is NOT a sufficient absorption coordinate

Interpolating Set A onto Set C's ρ·t values — if absorption depended on ρ·t alone, this would be
exact:

| t (nm) | ρ·t | Ga K/L predicted | observed | error |
|---|---|---|---|---|
| 32 | 171 | 1.3732 | 1.3561 | −1.24% |
| 128 | 683 | 1.5465 | 1.4731 | −4.74% |
| 512 | 2733 | 2.3558 | 1.9976 | **−15.20%** |
| 1024 | 5467 | 3.6570 | 2.8237 | **−22.79%** |

**Two guards against this being an artifact.** Log-log interpolation gives the same answer
(−23.12% at 1024 nm), so it is not a curvature artifact of linear interpolation. And an
assumption-free check — comparing at **identical thickness**, where ρ·t differs by a constant
−6.2% at every point — shows the Ga K/L gap growing from −1.5% to **−26.3%**. A constant offset
in ρ·t cannot produce an effect that grows 17-fold.

**The cross cannot predict its own interior.** P2.2 was necessary, not optional.

### 23.4 The finding that matters: the effect is strongly line-dependent

Composition sensitivity at fixed thickness, 100·(Set C − Set A)/Set A:

| Ratio | 32 nm | 128 nm | 512 nm | 1024 nm |
|---|---|---|---|---|
| **Ga K/L** principal | −1.5% | −5.7% | −17.8% | **−26.3%** |
| **As K/L** principal | −0.6% | −2.3% | −5.9% | **−7.0%** |
| **Bi L/M** principal | +0.2% | +0.9% | +3.3% | **+5.7%** (opposite sign) |

Reading the two framings together is what sharpens this:

| Ratio | residual at matched **ρ·t** | total at matched **thickness** |
|---|---|---|
| Ga K/L | **−22.8%** | −26.3% |
| As K/L | **−1.6%** | −7.0% |

**As K/L responds to composition almost entirely *through* density** — which ρ·t already
captures, leaving a ~2% residual. **Ga K/L does not**: most of its 26% is unexplained by
density, i.e. a genuine change in the alloy's mass attenuation coefficient with Bi content.

*Mechanism not asserted.* Ga Lα (1.098 keV) and As Lα (1.282 keV) sit differently relative to
the absorption structure of Bi, whose weight fraction falls from ~24% to ~1.4% across this
comparison — but attributing the asymmetry to specific edges requires cited mass attenuation
coefficients, which this project does not have to hand. **Recorded as an observation, flagged as
needing a primary source before any mechanistic claim.**

### 23.5 Consequence — this changes a decision, not just a table

Walther's method uses a **K/L ratio as a thickness proxy**, its stated virtue being that it
"reduces both the dependence on real foil thickness measurements and the effect of detector
sensitivities". His Figs 3 (bottom) and 5 use **Ga K/L**; Fig. 4 uses **As K/L**.

This result says the two are not interchangeable: **Ga K/L conflates thickness with composition
(26% at 1024 nm), while As K/L is close to composition-robust once density is accounted for
(~2%).** Using Ga K/L as a thickness proxy re-introduces composition dependence into the very
coordinate meant to remove it.

**Direct input to P1.2** (re-indexing the round trip on a measurable K/L): index on **As K/L**,
not Ga K/L. That decision was previously arbitrary; it is now evidence-based.

His paper cannot show this — Figs 3–5 carry two compositions at unswept thickness, so the
composition-dependence of the axis itself is invisible there. **This is a new result, and it is
this project's own.**

### 23.6 Limitation

Set C is a single composition (x = 0.01) at the thick end only. It establishes *that* the effect
exists and its rough size; it does not map it across x. Whether the Ga K/L sensitivity varies
smoothly between x = 0.01 and 0.20 is untested — an x = 0.10 thickness arm (10 runs, ~1.9 h)
would settle it and would also complete the replication of Figs 3–5.

---

## 24 — Figures: a presentation layer, and the corner analysis persisted

*2026-08-14. `mcxray_wrapper/corner.py` (10 tests) + a new `figures/` package. 177 tests green,
golden gate clean. First figures the project has ever produced.*

### 24.1 Why now

Walther, 2026-08-14: *"just complete your simulations and prepare the plots."* He is offline
16–23 Aug and unavailable until 26–28 Aug, so this was the last instruction before a ten-day
silence — and **no plots had ever been sent to him.** Plotting had been sitting in the work plan
as deliberately descoped.

It serves three audiences at once: his meeting, Ethan's presentation, and the dissertation.

### 24.2 `corner.py` — persisting what §23 computed ad hoc

§23's ρ·t result was real but was computed in a **throwaway shell command** and transcribed into
the report. That is the same failure mode as the Set B invariance check before P0.1: a
load-bearing result that is neither stored, tested, nor re-derivable.

`corner.py` mirrors the established module shape (`ratios.py`, `kfactors.py`, `kl_index.py`) and
exposes **two deliberately separate comparisons**, because neither is sufficient alone:

- `compare_arms()` — matches on **ρ·t**, isolating the residual density does *not* explain. This
  is the "is ρ·t sufficient" test proper.
- `matched_thickness()` — matches on **geometry**. No interpolation, no model. ρ·t differs by a
  constant −6.2% at every point, so an effect that *grows* with thickness cannot be a density
  artefact.

Output: `Aggregated\corner_rho_t_setA_vs_setC.csv`, 84 rows (42 per comparison).

**The load-bearing test** is `test_pure_rho_t_dependence_gives_zero_residual`: a synthetic table
where the ratio genuinely *is* a function of ρ·t alone must return zero residual. Without it, a
non-zero residual on the real data would be uninterpretable — it could just mean the method
always reports one. A second test pins the real numbers (Ga K/L −22.8%, As K/L −1.6% at
1024 nm), so **§23's headline figures are now machine-checked rather than transcribed.**

One fixture bug worth recording: the first synthetic table gave both arms identical thicknesses,
and the extrapolation guard fired. That was the guard working — the test arm is less dense, so
at a shared thickness its ρ·t is *lower*, and only the reference arm's thin points keep those
values inside the interpolation range. The real Set A spans 2–1024 nm; the fixture now mirrors
that.

### 24.3 The dependency boundary

CLAUDE.md mandates **"pandas + stdlib only"**. matplotlib is a real deviation, so it is confined
by construction:

- `mcxray_wrapper/` imports **nothing new**. Verified: no matplotlib reference anywhere in the
  package.
- `figures/` is a separate top-level package, free to import it.
- **No figure computes anything.** Every number on a plot comes from a tested module — the
  residual annotations are read from `corner.py`, never hard-coded. A presentation-layer
  computation must never quietly become a result nobody can trace.

Output goes to `C:\MCXRAY\Sim\Figures\`, a sibling of `Aggregated\`, never inside `Results\`.
PNG at 200 dpi (slides) and vector PDF (LaTeX) written together so they cannot drift apart.

### 24.4 Two figures

**`fig01_ratios_vs_thickness`** — replicates Walther Fig. 1. The three diagnostic ratios have
been reproduced in *data* since July but never drawn; this was the one replication the project
could not show. Eleven points, not ten: the Set B run at 100 nm shares Set A's conditions
exactly, so the curve gains a free extra point.

Two departures from his presentation, both stated on the figure: a **log thickness axis** (the
runs are a geometric doubling series; on his linear axis everything below 100 nm collapses into
the origin) and **ρ = 5.692 rather than his 5.36** (his own revised model, REPORT §15).

**`fig02_rho_t_insufficiency`** — the project's own result, two panels sharing an axis. Left:
Ga K/L, arms separate. Right: As K/L, arms nearly coincide. The finding is carried by the
**contrast between panels**, not by either alone.

`sharey=True` is load-bearing here, not cosmetic: independent y-scales would stretch each panel
to fill its own range and make the two gaps look comparable when they are not.

### 24.5 Design notes

The three-hue palette (blue / orange / aqua) was **validated with a colour-vision checker**
rather than chosen by eye — it clears the all-pairs separation gates at three slots; a fourth
hue does not, which is why no figure carries more than three colour-coded series. Every series
also carries a distinct marker, so the figures survive greyscale printing and colour-blind
readers. Fonts are matplotlib's bundled DejaVu Sans: naming an uninstalled font makes matplotlib
substitute one silently, and the figure would render wrong without erroring.

Both figures were inspected after rendering, and both needed a second pass — the ρ·t panels
originally had overlapping annotations, unreadable `4×10⁰` log-axis labels, and independent
y-scales; Fig. 1 had colliding 100/128 nm tick labels. Worth noting that rendering and
*looking at* the output are separate steps.

---

## 25 — P1.2: recovery held out in both unknowns

*2026-08-15. `roundtrip.recover_x_via_kl()` + `write_roundtrips()`, 5 new tests, 182 green.
Outputs: `roundtrip_heldout_as_k_l.csv`, `roundtrip_heldout_ga_k_l.csv`, alongside the existing
thickness-indexed pair.*

### 25.1 The weakness being removed

`recover_x()` calibrates on Set A, then looks that calibration up **at the Set B runs' known
thickness (100 nm)**. A real experimenter has no such number: thickness is exactly as unknown as
composition. So that round trip was held out in *x* but **not** in *t* — it was handed one of
the two answers it claims to infer.

`recover_x_via_kl()` reads each run's **own measured K/L ratio** — available from the same
spectrum being quantified — looks the Set A calibration up at that ratio, and inverts. Neither
the run's thickness nor its composition is used.

The old function is **kept, not replaced**: the difference between them is itself a result, and
deleting the weaker one would destroy the comparison.

### 25.2 Which axis, and why it is no longer arbitrary

Set C measured that Ga K/L carries a ~23% composition residual beyond density while As K/L
carries ~2% (§23.5). A thickness proxy that also tracks composition re-introduces the dependence
it exists to remove — and composition is the unknown. **As K/L is therefore the default.**

Walther's Figs 3 and 5 use Ga K/L; his data (two compositions, unswept thickness) could not have
revealed it to be the weaker axis.

### 25.3 Interpolation error — measured, not assumed

The x = 0.20 run at 100 nm exists but is **excluded** from the Set A calibration
(`SET_A_THICKNESSES_NM` has no 100), making it a free held-out test point. Predicting its k\*
from its measured As K/L and comparing with truth, across all 16 pairs:

| Method | mean error | worst |
|---|---|---|
| Linear between nearest neighbours | 0.17% | 0.55% |
| Local quadratic (3 points) | 0.03% | 0.10% |

Quadratic is ~5x better and both are negligible beside the effects under study (Bi M 50%,
composition sensitivity 23%). **Linear retained** — it matches `_interpolate_k_star`'s existing
rationale, adds no fitted parameters, and the choice is now backed by a measurement rather than
a preference.

### 25.4 Result: removing the crutch does not cost accuracy — it slightly helps

Mean |error| in recovered *x*:

| true x | handed *t* | held out, As K/L | held out, Ga K/L |
|---|---|---|---|
| 0.01 | 0.00556 | **0.00488** | 0.00729 |
| 0.02 | 0.00530 | **0.00468** | 0.00699 |
| 0.05 | 0.00451 | **0.00404** | 0.00603 |
| 0.10 | 0.00305 | **0.00289** | 0.00429 |
| 0.20 | 0.00041 | 0.00059 | 0.00049 |
| **overall** | 0.00377 | **0.00342** | 0.00502 |

Two findings, neither expected:

**Held-out recovery is slightly BETTER than handed-thickness recovery** (0.00342 vs 0.00377),
and markedly so at low x. Counter-intuitive, but explicable, and it is exactly the property
Walther claims for the K/L axis: *"providing an inherent self-calibration."* When a run's
composition shifts its absorption, its measured K/L shifts with it, and the lookup partly
compensates. Fixing the thickness at 100 nm ignores that correction. **His claim is now
demonstrated empirically rather than quoted.**

**As K/L beats Ga K/L by 47%** on recovery error (0.00342 vs 0.00502). This is an independent
confirmation of §23.5 — that result came from ratio residuals, this one from end-to-end
quantification error. Two different measurements, same conclusion, same direction.

### 25.5 The guards

Two leakage tests, both on a fixture where the Set B runs share intensities exactly:

- **Composition** — different true x, identical intensities, must recover identical x.
- **Thickness** — relabel the runs 100 nm → 777 nm, change no intensity: `recover_x_via_kl`
  returns bit-identical results, while `recover_x` moves. That difference *is* the weakness P1.2
  removes, asserted as code.

One test was hollow on first writing — it set the thickness to 100 in both branches and so
proved nothing. Corrected. Worth recording: a leakage guard that cannot fail is worse than no
guard, because it reads as protection.

---

## 26 — Stage 6b: sum-peak synthesis, built with the open choices as switches

*2026-08-15. `mcxray_wrapper/sumpeak.py`, 17 tests, 199 green. Built while four modelling
decisions remain open — deliberately, as parameters rather than defaults.*

### 26.1 Why it is built before the decisions are made

Walther is unavailable until 26–28 Aug, so the three questions that were his are now Ethan's.
Rather than wait or guess, every choice is a **switch**, and the stored output records which
settings produced it. The decisions become configuration, and the sensitivity sweep the project
always intended becomes trivial.

Confirmed from this project's own stored line energies, not from prose:
**Ga Lα 1.098 + As Lα 1.282 = 2.380 keV against Bi Mα 2.423 — a 43 eV gap.**

### 26.2 The four switches

| Switch | Options | Note |
|---|---|---|
| `parents` | `alpha_only` / `alpha_beta` | All four Ga-L × As-L pairings land within **59 eV** of each other and 16–43 eV of Bi Mα (Ga Lα+As Lβ = 2.415 is *closer* than the pair the paper names). `alpha_beta` is the physically complete set; `alpha_only` is what the paper states. |
| `basis` | `intensity` / `rate_product` | Distinguishing feature is **dose scaling**: an intensity fraction is linear in dose, true random coincidence is quadratic. |
| `conserve` | `True` / `False` | `True` removes one Ga L and one As L photon per fake Bi M count — exactly what Walther's correction undid. |
| `m_band_factor` | 1.0 / **1.743** | Simulated Mα versus the whole unresolved M band a detector actually sees. |

**A parent asymmetry the paper did not face.** Walther's Ga L and As L were within 9%, so "15%
of their line intensities" was unambiguous for him. In this data **Ga Lα / As Lα ranges 0.97 to
2.02**, so the `intensity` basis uses the **geometric mean** — symmetric in the two parents and
reducing to his reading when they match.

Fake counts are capped at `min(I_Ga, I_As)`: each event consumes one photon from each parent, so
the scarcer one is a hard ceiling. Without it a large swept level drives a conserved parent
negative.

### 26.3 The result that matters for LO4

Recorded as a prediction before building: **I(Ga Lα)/I(Bi Mα) spans 3.7 at x = 0.20 to 107.7 at
x = 0.01.** The same pile-up fraction is therefore far more damaging at low Bi content. Measured,
at 100 nm, `alpha_only` / `intensity`:

| x | fake counts as % of Bi M, 0.1% level | 1% | 10% |
|---|---|---|---|
| 0.01 | 9.7% | **97.2%** | 972% |
| 0.05 | 1.9% | 18.9% | 189% |
| 0.20 | 0.4% | 4.2% | 42.0% |

Bi L/M at the 1% level: **1.519 → 0.770 (−49.3%) at x = 0.01**, against 1.508 → 1.447 (−4.0%) at
x = 0.20. **The same artefact does 23× more damage at the low end.**

At the 10% level — still below Walther's measured ~15% — the x = 0.01 Bi M peak is roughly ten
times fake.

**This is the strongest candidate yet for the low-x failure mechanism**, and it makes the
sensitivity sweep the substance of LO4's answer rather than a robustness check. It also sharpens
the P1.3 comparison: counting statistics at x = 0.01 are ~9% (100 s) or ~3.4% (715.5 s), an order
of magnitude smaller than a 1% sum peak's effect. On present evidence **the sum peak, not
Poisson noise, sets the low-x limit** — to be confirmed once P1.3 lands.

### 26.4 What the tests do and do not pin

They pin **mechanics**, never a physical magnitude — the magnitude is a swept choice. Each switch
is asserted to do what it claims (quadratic vs linear dose scaling; parents depleted or not;
band factor raising the baseline and *softening* the apparent damage), plus direction guards: the
ratio must always fall, damage must grow with level, parents must never go negative.

### 26.5 Still to decide — now purely a reporting choice

Which settings the dissertation reports as primary. The machinery runs all sixteen combinations;
the swept result is the deliverable either way. **Where** it is applied is not open: Walther
settled it — the unknown only, never the calibration.

### 26.6 Propagating the artefact: the second-order hit, and an error worth recording

*Added later on 2026-08-15. `apply_to_intensities()` + `as_measured_unknowns()`, 3 more tests,
207 green.*

`synthesise()` reports what the artefact does to the Bi L/M ratio. It does not rewrite the
intensities, so nothing downstream can see it. `apply_to_intensities()` returns an **as-measured**
copy of the stored table -- same columns, same rows, deliberately interchangeable -- so ratios,
k\*, the thickness proxy and the recovery all run on it unchanged.

That exposes the **second-order hit**. One leak, two consequences:

- **Direct** -- fake counts land on Bi Ma, so the Bi signal reads high.
- **Indirect** -- each event consumed one Ga L and one As L photon, so those lines read low. As
  K/L is the thickness proxy, so depleting As L raises it and the foil reads as *thicker*, which
  selects the wrong k\* and moves the answer again.

**An error caught by the numbers looking wrong.** The first run applied the artefact to the whole
table -- corrupting the **calibration** as well as the unknown. Recovered x at x = 0.20 then
showed no shift at all, because both sides moved together and cancelled. That is precisely the
variant Walther's answer rules out ("only ... to the experimental spectrum, not to simulations").
`as_measured_unknowns()` now names the correct treatment, `run_ids` enforces it, and a test
asserts the calibration survives untouched. **The near-perfect cancellation is itself worth
reporting: it shows how much of the sum peak's apparent harmlessness in a self-consistent
workflow is an artefact of corrupting both sides.**

Applied correctly -- 1% level, artefact on the unknown only:

| | true x | clean | direct only | both hits |
|---|---|---|---|---|
| Bi Ma ÷ As Ka | 0.01 | 0.0099 | 0.0193 | **0.0193** |
| Bi La ÷ As Ka | 0.01 | 0.0100 | 0.0100 | **0.0100** |
| Ga Ka ÷ As Ka | 0.01 | 0.0114 | 0.0114 | 0.0112 |
| Bi Ma ÷ As Ka | 0.20 | 0.1999 | 0.2066 | 0.2073 |
| Bi La ÷ As Ka | 0.20 | 0.2000 | 0.2000 | **0.2000** |

Four predictions, recorded before running, all borne out:

1. **Bi M routes over-estimate badly at low x** -- recovered x nearly **doubles** at x = 0.01
   (0.0099 → 0.0193), against +3.7% at x = 0.20.
2. **Bi L routes are immune.** Bi La sits at 10.84 keV, nowhere near the 2.4 keV artefact --
   unchanged to four decimal places at every composition.
3. **Ga/As routes shift** despite containing no bismuth, purely through parent depletion.
4. **`Bi_As L/K` is the most robust route in the matrix** -- it touches no Bi M, and its k\* is
   flat in thickness so the proxy error cannot reach it either.

**The second-order hit is small.** It moves the answer by roughly 0.3-2% relative, against a
direct effect of up to 95%. It also *reinforces* rather than cancels. Worth having measured
rather than assumed, but the direct hit dominates completely.

**And point 4 restates the project's central tension in its sharpest form yet.** The route immune
to the sum peak, flat in thickness, and invariant in composition is `Bi_As L/K` -- which is the
route sitting on the 297 eV As Ka / Bi La overlap that remains unmodelled. Every route is
compromised by one of the two overlaps the dissertation set out to study.

---

## 27 - Overlap (i) bounded, and the two overlaps separated

*2026-08-15. `mcxray_wrapper/overlap.py`, 16 tests, 223 green. Output:
`Aggregated/overlap_i_bound.csv`.*

### 27.1 The two overlaps are not the same kind of problem

The project has treated its two overlaps as a matched pair since the beginning. Measured against
detector resolution they are quantitatively different:

| | Separation | vs FWHM | |
|---|---|---|---|
| Sum peak (Ga La + As La vs Bi Ma) | 43 eV | **0.47 FWHM** | merged |
| Overlap (i) (As Ka1 vs Bi La) | 297 eV | **1.74 FWHM** | **resolvable** |

At half a linewidth the sum peak's counts are physically indistinguishable from Bi, so additive
contamination is the correct model. At 1.74 linewidths the two appear as separate peaks with a
valley between; standard fitting separates them.

**This ruled out the obvious model.** Treating overlap (i) as "a fraction of As Ka is misassigned
to Bi La" assumes a blindness the detector does not have. It would have overstated the damage to
the one route the sum peak cannot touch - and that route is the project's leading recommendation.

### 27.2 The resolution model is validated, not fitted

FWHM(E) = sqrt(noise^2 + 2.355^2 x eps x F x E), with eps = 3.86 eV and F = 0.115 (standard
textbook values, marked *pending verification vs primary source*; the reference is not in this
repo). It is not tuned to this project's data, and it reproduces two facts held independently:

- **130 eV at Mn Ka** - the conventional Si(Li) specification.
- **Bi La1/La2 at 0.63 FWHM, i.e. merged** - independently reproducing Walther's statement that
  they are "usually indistinguishable".

Getting two known answers right is why the third is credible. Both are asserted as tests.

### 27.3 Bounded, not modelled

A real treatment needs peak shapes, low-energy tailing, the background beneath both peaks, and a
fitting algorithm's behaviour - four physical inputs this project neither holds nor can cite.
Inventing them is what CLAUDE.md forbids.

Instead the cost is expressed as a fitted-area uncertainty,

    sigma(Bi La) = sqrt( N_BiLa + coupling x N_neighbour )

with **coupling swept** over 0.1 / 1 / 10% - deliberately the same ladder as the sum-peak level,
so the two overlaps are compared on identical footing. The first term is irreducible Poisson
counting statistics and is reported separately, so "overlap cost" can be told apart from "too few
photons". Neighbours are found from the stored energy column, not typed in: As Ka1 and As Ka2,
both resolvable.

### 27.4 Result: the recommendation survives

Relative uncertainty on Bi La at 100 nm, at Walther's acquisition (1 nA x 715.5 s):

| x | counting floor | coupling 0.1% | 1% | 10% |
|---|---|---|---|---|
| 0.01 | 3.47% | 3.69% | 5.27% | **12.99%** |
| 0.05 | 1.57% | 1.59% | 1.75% | 2.93% |
| 0.20 | 0.81% | 0.82% | 0.84% | 1.01% |

**Even at the most pessimistic coupling, overlap (i) costs ~13% at x = 0.01.** The sum peak, at a
1% level, makes Bi M routes report ~0.019 for a true 0.010 - a **~100% error**. The Bi L route
remains better by roughly an order of magnitude under the worst assumption allowed here.

Two further points worth carrying into the write-up:

**Bias versus variance.** The sum peak *biases* the answer: it is systematically wrong in one
direction and no amount of averaging removes it. Overlap (i) adds *variance*: the answer is
noisier but unbiased, and more counts or repeat measurements improve it. Different in kind, not
just in size.

**At low coupling the overlap adds almost nothing.** At 0.1% the uncertainty is 3.69% against a
3.47% counting floor - the overlap contributes 0.2 points. Below roughly 1% coupling the route's
precision is limited by photon count, not by its neighbour.

### 27.5 What this closes

The ranking is no longer an artefact of which overlap was studied. Both are now on the table with
stated, swept assumptions, and **Bi La / As Ka survives as the recommended route** - not because
its weakness was ignored, but because it was quantified and found to be an order of magnitude
smaller than the alternative's.

### 27.6 The two uncited constants, and why they do not threaten the finding

*Added 2026-08-17. `resolution_sensitivity()` + 3 tests, 241 green.*

The resolution model carries the only uncited physics in this module:

  **eps = 3.86 eV** -- the mean energy needed to create one electron-hole pair in silicon. An
  incoming X-ray is not measured directly; it liberates charge, and the detector infers the
  photon energy from how much. A 10 keV photon makes ~2,600 pairs. It is 3.86 rather than
  silicon's 1.12 eV band gap because most of the energy goes into lattice vibrations, not into
  freeing carriers.

  **F = 0.115** -- the Fano factor. If pair creation were purely random the carrier count would
  fluctuate by sqrt(N). It is not: the total energy is fixed, so producing more pairs in one
  interaction leaves less for the rest, and that constraint suppresses the fluctuation. F is the
  ratio of the real variance to the Poisson one, so the detector is about sqrt(1/0.115) ~ 3x
  sharper than naive counting would allow (Fano, 1947).

They enter as the statistical term of FWHM = sqrt(noise^2 + 2.355^2 . eps . F . E), which is a
derivation rather than a fit: N = E/eps carriers, variance F.N, converted back to energy. The
50 eV noise term is not a physical constant at all -- it is `DetectorNoise=50` from the locked
`.mic`.

**The whole overlap (i) argument rests on these**, since it turns on whether the As Ka / Bi La
pair sits above or below the merge threshold. So the ranges were swept rather than trusted:

| | eps range | F range | separation | verdict |
|---|---|---|---|---|
| Overlap (i) | 3.63 - 3.86 | 0.084 - 0.130 | **1.65 - 2.07 FWHM** | resolvable at every corner |
| Sum peak | 3.63 - 3.86 | 0.084 - 0.130 | **0.45 - 0.53 FWHM** | merged at every corner |

The two never approach each other: the worst-case overlap (i) separation (1.65) is still **3.1x**
the best-case sum peak separation (0.53). And the margin to overturning the result is large --
eps.F would have to be **2.2x** its accepted value before As Ka and Bi La merged. Nothing in the
literature is close.

The 130 eV Mn Ka validation also survives the sweep, landing between 115 and 138 eV across all
four corners -- inside the band a Si(Li) detector is specified at.

**So the pending citation bounds a NUMBER, not a FINDING.** That distinction is asserted in three
tests, so it cannot quietly stop being true. The values should still be cited properly before
submission (Goldstein et al. is the standard reference, and eps is temperature-dependent --
Si(Li) detectors run cold, so the 77 K figure is the relevant one).

## 28 - P4.1: the recovery re-run on as-measured data, swept across every modelling choice

*2026-08-17 morning. `mcxray_wrapper\sensitivity.py`, 10 tests, 250 green. Outputs:
`sumpeak_roundtrip_sweep.csv` (7,840 rows), `sumpeak_roundtrip_by_route.csv`,
`sumpeak_switch_influence.csv`.*

Everything recovered so far came from pristine simulated intensities. No detector produces
those. P4.1 runs the whole held-out recovery on as-measured data - the stored table with the
sum peak synthesised onto the unknown runs - under **every combination of the four unsettled
modelling choices**: 3 levels x 2 parent sets x 2 bases x 2 conservation x 2 M-band baselines,
plus a clean baseline anchoring the table.

### 28.1 Why a full factorial rather than a chosen setting

Walther fitted his ~15% to close a disagreement with his own data; there is no published recipe
to inherit, and he is unreachable until late August. Choosing one setting and hoping was the
alternative. Running all 16 costs seconds and converts the question from "which setting is
right?" to "**does the conclusion depend on the setting?**" - which is answerable.

### 28.2 It does not. The route ranking survives every combination

At the 1% level, principal definition, mean |error| on recovered x averaged over the grid:

| routes using | mean abs error | worst | spread across switches |
|---|---|---|---|
| Bi L | 0.0003 | 0.0016 | 0.0016 |
| Bi M | **0.0308** | 0.1623 | 0.1621 |

Bi M routes are two orders worse than Bi L routes in **all 16** switch combinations. The
finding is robust to every choice nobody could settle.

### 28.3 Which switches actually matter

`switch_influence` answers the factorial's second question - of the four choices, which move
the answer at the 10% level:

| switch | difference in mean abs error | relative |
|---|---|---|
| basis (intensity vs rate_product) | 0.0180 | 2.2x |
| m_band_factor (1.0 vs 1.743) | 0.0121 | 1.7x |
| parents (alpha vs alpha+beta) | 0.0042 | 1.2x |
| conserve (True vs False) | **0.0001** | 1.005x |

So the two that matter are the level's *meaning* (what it multiplies) and the *baseline* it is
measured against - both statements about magnitude. The two that barely matter are the physics
details (which lines feed it, whether parents are depleted). For the write-up: state basis and
baseline prominently; the rest can be a sentence.

### 28.4 The structural test worth keeping

The acceptance tests pin the mechanism, not the magnitudes: with `conserve=False` the recovered
x on every Bi L route is **bit-identical** to the clean baseline (no path from a 2.4 keV
artefact to a 10.8 keV line), and with `conserve=True` it moves - through the As K/L thickness
proxy and only through it, growing with level and staying under 0.01. Zero without the
mechanism, non-zero with it: that is what proves the leak is the one claimed, not some other.

## 29 - Repo housekeeping before the context loss: nothing lives in a scratchpad any more

*2026-08-17 midday. No new science; recorded because two of the finds were near-misses.*

A pre-compaction audit (Ethan's request) found and fixed:

- **The published artifact's page source existed only in a session scratchpad** - the same
  class of location the Stage 3 executor was lost from (§22). Losing it would have made the
  live artifact unupdatable, only replaceable. Moved into the repo (`artifact\
  kstar-calibration.html`) together with `make_standalone.py`, which wraps it into the
  offline-viewable snapshot; regeneration re-verified.
- **CLAUDE.md had gone stale in seven places** - still said 15 simulations, no Set C, carried a
  status block describing the sum peak as unbuilt weeks after it was done. All fixed; the
  status section now explicitly defers to `CURRENTLY_RELEVANT.md` rather than pretending to be
  current.
- **`NEXT_SESSION_PROMPT.md` created** - a cold-start prompt for post-compaction sessions: read
  order, where the Aims & Objectives form is and how to read a .docx, the flag that LO1 has
  nothing behind it, and the standing instruction to keep both reports current.

## 30 - P1.3: counting statistics, propagated to recovered composition

*2026-08-17 afternoon. `mcxray_wrapper\counting.py`, 20 tests, 290 green. Outputs:
`counting_line_sensitivities.csv`, `counting_uncertainty.csv`, `counting_by_route.csv`.*

The last unmodelled mechanism, and the simplest: a spectrum holds a finite number of photons.
At x = 0.01 the stored Bi La is ~116 detected photons and Bi Ma ~76.

### 30.1 How: differentiate the whole chain, not a formula

Each line count is an independent Poisson variable, so Var(ln N) = 1/N and

    sigma_x^2 = SUM_i S_i^2 / N_i,    S_i = d(recovered x) / d(ln N_i)

The sensitivities are obtained **numerically** - perturb one line at a time, re-run the actual
`recover_x_via_kl`, central-difference in log-intensity. Deliberate, for three reasons: it
captures the indirect path through the As K/L thickness proxy automatically; it gets the
correlation right when one line (As Ka1) appears in both the route and the proxy; and the
log-derivative is scale-free, so one set of sensitivities prices every dose.

**Validated against closed form.** Walther's three equations give exact derivatives for lines
outside the proxy: Bi_Ga yields dx/dlnI(Bi La) = x, Bi_As yields x(1-x), Ga_As yields (1-x).
All three reproduced to six figures across all five Set B runs - asserted as tests. A line with
no path to a route (Bi Lb1 against a principal L/K estimate) comes out at exactly zero, and As
La reaches a Bi_Ga route *only* through the proxy, at under 5% of the direct term.

**Cross-checked against `overlap.py`,** which computes the Bi La counting floor as 1/sqrt(N) by
a completely different code path: 3.47% there, 3.46-3.49% here, the small spread explained by
each route's own algebra (the Bi_As inversion damps Bi La's contribution by (1-x); the other
lines add a little back). No shared code, same number.

### 30.2 What it found, at x = 0.01 and Walther's dose (715.5 s live)

| route family | relative sigma on x | dominant line |
|---|---|---|
| Bi L (all four pairings) | **3.5%** | Bi La (~99% of variance) |
| Bi M | 4.3% | Bi Ma (~100%) |
| Ga_As (L pairings) | 10-11% | Ga La |
| Bi K | **35%** | Bi Ka1 (100%) |
| Ga_As (K pairings) | 31-45% | As/Ga Ka1 |

Three findings for the write-up:

1. **The 13 Aug assumption inverts, as predicted on the 15th.** Noise at x = 0.01 is ~3.5%
   against the 1% sum peak's ~97% error on Bi M. Counting statistics are the *lesser* low-x
   mechanism by more than an order of magnitude - the opposite of what the plan assumed when
   P1.3 was first scheduled.
2. **Bi K's failure is now a dose statement.** To reach 10% relative on x at x = 0.01, a Bi L
   route needs **0.12x** Walther's acquisition - it is already there five times over. A Bi K
   route needs **>12x**. LO3's negative result, priced in count time.
3. **Ga_As fails by algebra, not photons.** Eq 9's sensitivity to its own lines is (1-x), which
   tends to 1 as x tends to 0 while x itself vanishes - so relative error diverges no matter
   how well counted. That falls out of the derivative, not out of an assertion.

A first-order propagation stops being meaningful when relative error is large; rows past 30%
are flagged `first_order_valid=False` rather than silently trusted (all Bi K and most Ga_As
rows at low x).

## 31 - P4.2: the error budget and the measurability limit. LO4's deliverable

*2026-08-17 afternoon. `mcxray_wrapper\budget.py`, 20 tests, 297 green. Outputs:
`error_budget.csv` (4,320 rows), `measurability_limit.csv`, `route_ranking.csv`.*

Three mechanisms, each quantified separately, each preferring a different route if read alone:
the sum peak wrecks Bi M and cannot touch Bi L; overlap (i) costs precision on Bi La and
nothing else; counting starves Bi K. P4.2 puts them in **one currency** - absolute error on
recovered x - and asks where the total crosses a stated 10% relative threshold.

### 31.1 The construction

- **Counting** enters directly (sigma_x from §30). **Sum peak** enters directly (recovery on
  as-measured minus recovery on clean = induced bias). **Overlap (i)** needed converting: it is
  stored as uncertainty on a peak *area*, and becomes uncertainty on *composition* through the
  d(x)/d(ln I(Bi La)) sensitivity from §30 - the piece that makes the three comparable, and why
  P1.3 had to come first. The overlap's cost is taken *above* the counting floor in quadrature,
  so no photon is charged twice.
- **Bias and variance are not conflated**: total = |bias| + sqrt(sigma_counting^2 +
  sigma_overlap^2), a stated conservative envelope. The method's own clean residual is a
  separate bias column - a route that is merely hard to calibrate must not look sum-peak-damaged.
- **Nothing unknown is defaulted.** Sum-peak level, overlap coupling and dose are all swept
  (3 x 3 x 3 = 27 scenarios); every row carries its scenario, and the limit-finding
  interpolation (log-log, matching the power-law behaviour) **refuses to extrapolate** - a curve
  that never crosses inside the sampled x range reports which side it fell, never a number.

### 31.2 The answer

At x = 0.01, against the 10% target:

| | scenarios failing (of 27) | which scenarios |
|---|---|---|
| Bi M routes | **27** | all - dominant mechanism: sum peak |
| Bi K routes | **27** | all - dominant mechanism: counting |
| Ga_As routes | 27 | all - dominant: method residual / counting |
| **Bi L routes** | **9** | *only* the 100 s basis or the pessimistic 10% coupling |

Every one of Bi L's nine failures is curable by counting longer or is the worst-corner coupling
assumption; at Walther's own 715.5 s with coupling at or below 1%, **Bi L always clears the
target across the whole sampled range**. Bi M's and Bi K's failures are not curable by dose -
one is a bias, the other needs >12x the acquisition. That asymmetry - failures that dose fixes
versus failures it cannot - is the substance of the recommendation.

The bracketed measurability limits for the Bi M route span x = 0.013 to 0.124 depending on
scenario, which is itself the honest statement: Bi M's usability depends entirely on an
instrument property (the pile-up level) that this project cannot measure and Walther fitted.

**LO4's answer, as the data ranks it: Bi La referenced to As Ka.** The `summed` variants of the
Bi L routes score slightly higher still, but carry a flagged caveat: the overlap term is a
lower bound under `summed` (the artefact also touches sub-lines the bound does not model), so
the principal-definition result is the defensible one. The verdict itself - whether 10% is the
right threshold, and what to recommend Walther's readers - **remains Ethan's (P4.3), not
computed**.

### 31.3 What the budget is careful about

The tests enforce separability: dose moves the variances and no bias (bit-identical bias
columns across the dose sweep); level moves only the sum-peak bias; coupling only the overlap
variance. If any of those leaked, `dominant_mechanism` would be untrustworthy and the
recommendation with it. And the k* invariance result (§19) shows up again from the other side:
the winning route's method residual is ~1e-7 in x because k*(Bi L, As K) is flat to the fifth
decimal - the route is good *because* the calibration transfer it rests on is nearly exact.

## 32 - The analysis driver, and the silent regression it caught on its first run

*2026-08-17 afternoon. `run_analysis.py`, 7 tests, 297 green. Figures 3-6 rendered;
`figures\make_all.py` now builds all six.*

### 32.1 One command instead of an act of memory

Every `write_*` function was previously invoked by hand from whatever session was open.
`run_analysis.py` declares the twelve stages in dependency order and runs them; `--list`,
`--only <stage>`, `--derived-only` for skipping re-aggregation. The evidence this was needed
was already on disk: `sumpeak_sensitivity.csv` had been cited in WORKPLAN §3.5 as existing
data, and **did not exist** - `write_sumpeak` had never been run against the full matrix. A
structural test now walks every module, finds every `write_*`, and fails if the driver does not
call it, so a new module cannot silently produce nothing.

### 32.2 The dose regression - caught by hashing, restored byte-identical

Before the first full run, every existing Aggregated file was SHA256-hashed. After: 16 of 17
byte-identical, 7 new - and **one changed that should not have**. `write_overlap_bound`
defaults to `dose_scale=1.0` (the stored 100 s basis); the file on disk, and the 3.47% / 5.27% /
12.99% figures quoted in §27 and the workplan, were generated at Walther's 7.155. The driver
had inherited the default and regenerated the file **nine times noisier with every column
heading and row count unchanged** - the exact shape of failure the trap list exists for.

Fixed by passing the dose explicitly in the driver with a comment carrying the incident;
regenerated; **hash-identical to the 15 Aug file**, so §27's numbers stand. Two guard tests:
the driver source must name `dose_scale` in that call, and the stored CSV's dose column must
equal Walther's. The general lesson joins the record: *a reporting basis belongs in the driver,
visible, never in a function default* - and hash-before-regenerate is cheap enough to do every
time.

### 32.3 Figures 3-6

All read stored CSVs only; no physics recomputed, no number typed in (fig06's caption values
are collected from the plotted series at draw time, same discipline as fig02's residuals).

- **Fig 3 - the measurability limit** (LO4 headline). Left: total error vs x for the three Bi
  shells, all against As K so only the Bi line differs; scenario band over all 27 combinations;
  10% target line. Right: the recommended route's budget decomposed - counting and overlap (i)
  comparable, sum peak three orders down. First draft's title overclaimed ("only Bi L stays
  measurable") and was corrected against the scenario counts before anything shipped: the
  defensible claim is that Bi M and Bi K fail under *every* assumption and Bi L's failures are
  the dose-curable ones.
- **Fig 4 - sum-peak selectivity.** Fake counts as % of true Bi M (97% at x = 0.01 vs 4% at
  x = 0.20 at the 1% level), and the corrupted Bi L/M curve a detector would record.
- **Fig 5 - the round trip under fire.** Recovered vs true x, clean and as-measured, Bi M route
  and Bi L route side by side on shared axes. The Bi M panel bends away from the diagonal; the
  Bi L panel's three levels coincide exactly (annotated, since the overplot would otherwise
  read as one series).
- **Fig 6 - Bi K.** Escape fraction vs thickness (Bi Ka1 flat at ~1.0, Bi Ma down to 0.45 at
  1 um) beside absolute detected photons (Bi Ka1 ~100x below Bi La). Absorption-immune and
  photon-starved on the same page - LO3's negative result as one figure. First draft said Bi Ma
  was "almost entirely reabsorbed"; the plotted number is 0.45, and the caption now reads its
  endpoints from the data.

State at end of day: **297 tests green, golden gate clean. 21 runs, 23 aggregated outputs, 6
figures.** Remaining: P4.3 (the verdict - Ethan's), LO1 (literature, no code), write-up.
