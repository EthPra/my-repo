# Ch4 — Methodology: the simulation framework

**13 pp · ~3,500 words · drafted Wed 10 (AM: 4.1–4.4 ~1,500 w; PM: 4.5–4.9 ~2,000 w)**

Ordered as the pipeline runs. Every item flagged in `../writeupTODO.md` §1–3 lands here — tick
them off that file as they are written. Governing test (§5 rule 4): *if an examiner could ask
"why did you do it that way?" and the answer isn't in the text, it isn't finished.*

---

## 4.1 Architecture (~450 w)

**Sources:** REPORT §1, §16, §22, §32.

Must say:
- Six input files per run: `.sim` (master), `.sam` (specimen), `.mic` (beam + detector),
  `.par` (counts, output basename) **authored**; `.mdl` / `.rp` **passed through unchanged**.
- Pipeline stages: generate → execute → parse → aggregate → analyse.
- **The run loop stores raw, unprocessed intensities only.** No ratios, k-factors or corrections
  inside it. Every derived quantity is downstream and re-derivable without re-simulating.
  *This is a design decision with a reason — say the reason.*
- Provenance manifest (`provenance_manifest.json`) ties every output back to its inputs.
- **Figure: pipeline block diagram** (does not exist yet — either draw it or cut it Wed PM).

## 4.2 Locked experimental design (~450 w)

**Sources:** `../CLAUDE.md` design table; REPORT §15.3–15.4; `../writeupTODO.md` §2–3.

The table, verbatim from `CLAUDE.md`: 200 keV; 10⁶ trajectories (10⁷ for ≤16 nm); free-standing
foil, single BOX, no substrate, vacuum both sides; `DetectorTOA=25`, `DetectorPitch=90`;
Si:Li, crystal **0.5 cm**, `DetectorNoise=50`; `PhotonNbr=10000`, `EnergyChannelWidth=5`.

**Declared deviations — each with its reason:**
- 10⁷ trajectories for ≤16 nm — Walther, 19 Jul, for <1% MC noise on thin foils.
- Detector crystal **0.5 cm**, not the golden set's 0.3 — supervisor correction, 19 Jul.
- Exposure **1 nA × 715.5 s live** is a *labelled reference*, not a claim: probe current is
  Walther's estimate. Dose scales swept are 1.0 / **7.155** / 71.55.
- Intensity column: **`Intensity Emitted Detected (photons)`** — say why, not just which.
- The `.mic` has **no window field**: ATW (Al 0.02 µm + Moxtek 0.3 µm) is compiled in and
  windowless is impossible. The planned window arm is therefore a **scope reduction, declared**,
  not an omission (carry to Ch6.5).

## 4.3 Run matrix (~400 w)

**Sources:** REPORT §11, §23.1–23.2; `../PRESENTATION_SCRIPT.md` §B ⓷.

- Set A: x = 0.20, t ∈ {2,4,8,16,32,64,128,256,512,1024} nm — 10 runs.
- Set B: t = 100 nm, x ∈ {0.01,0.02,0.05,0.1,0.2} — 5 runs.
- Set C: x = 0.01, t ∈ {32,64,128,256,512,1024} nm — 6 runs, added 2026-08-13.
- **State the cross explicitly** — it is a cross, not a grid. Say so and say why that was
  sufficient for the question asked.
- ⚠ **Causality the right way round: Set C *is* the test, not the consequence.** It was added
  because ρ·t proved insufficient as an absorption coordinate; the cross could not predict its
  own interior. Earlier prose gets this backwards — do not copy it (§5 rule 6).
- The frozen 15 were verified byte-identical after Set C was added.

## 4.4 Physical inputs and provenance (~350 w)

**Sources:** REPORT §10, §12.1, §15.2, §27.6; `spec.py` source comments.

- **Every constant carries a cited source** — this is the governance rule and the section that
  demonstrates it. Ethan verifies each one at review.
- Density model **ρ(x) = 5.32 + 1.86x** (Walther's endpoints GaAs 5.32 / GaBi 7.18, 19 Jul).
  Production densities: 5.3386 / 5.3572 / 5.4130 / 5.5060 / 5.6920. Note the discrepancy in
  published anchors and how it was resolved.
- Atomic weights: IUPAC/CIAAW 2024 (`spec.py`). *A* in Walther's equations is **atomic weight**;
  ρ is atomic density and does not enter — personal comm. resolved the paper's gloss (REPORT §18.2).
- Line energies from the output table (Bi Mα 2.423, Bi Lα 10.840, Bi Kα1 77.097 keV).
- The two `# pending verification vs primary source` detector constants and their robustness
  range — name them and say what they would have to be wrong by to matter.

## 4.5 Verification of the pipeline (~600 w)

**Sources:** REPORT §2–5, §9, §18.3; `../writeupTODO.md` §5.

Four independent legs:
- **(a) Golden-set regression + classified diff.** ⚠ **Golden files are ground truth for FORMAT
  ONLY, never physics** (§5 rule 3) — say this explicitly here or a reader takes the regression
  suite as physics validation.
- **(b) Fault injection: five silent faults, five caught** — Ångström vs nm, weight vs atomic
  fraction, `UserDefinedMassDensity = 0`, the `DetectorDiffusionLenght` misspelling "corrected",
  line endings harmonised. Each fails *silently* in the simulator — that is why the harness
  existed. **Say plainly the harness was not kept** (Appendix F holds the record).
- **(c) End-to-end:** generated inputs reproduce golden output within MC noise.
- **(d) Replication of Walther's k\* constants to a few percent** — **frame as calibration
  against a known standard, not as a finding.** Detail belongs in Ch5.3.

## 4.6 Analysis chain (~500 w)

**Sources:** REPORT §17, §18, §19, §25; `../decisions.md` D2.

- Diagnostic ratios under **both** line definitions: `principal` is production, `summed` is the
  robustness check — **decision D2**, give the reasons as Ethan's reasoning.
- k\* per route, calibrated on Set A.
- **As K/L as the thickness proxy — a measurement, not a preference.** Set C is what measured it.
- Held-out recovery in **both** unknowns (x and t), not just x: the earlier round trip was handed
  the thickness, which a real experimenter does not have (REPORT §18.5).
- Interpolation error measured on a held-out point.

## 4.7 Artefact modelling (~700 w)

**Sources:** REPORT §26, §27, §30; `../writeupTODO.md` §1; `../decisions.md` D3.

**State the asymmetry up front and justify it:** the sum peak is *modelled*; overlap (i) is
*bounded*. They are treated differently because the evidence available for each is different.

- **Sum peak — modelled.** MC X-Ray cannot produce it, so it is synthesised analytically.
  Four switches with production settings and reasons (**decision D3**): `parents=alpha_only`,
  `basis=intensity`, `conserve=True`, `m_band_factor=1.743`. Level **swept** 0.1 / 1 / 10%,
  never fixed. Applied to the **unknown only**, never the calibration. Fake counts capped at
  min(I_Ga, I_As). Geometric mean taken in the intensity basis.
- **Overlap (i) — bounded, not modelled.** σ = √(N + coupling·N_neighbour); coupling swept
  0.001 / 0.01 / 0.1. Resolution model validated at Mn Kα and against Walther's Lα1/Lα2
  statement. ⚠ Every result from it is a **lower bound** — carry to Ch6.5.
- **Counting statistics:** numerical propagation through the whole recovery, validated against
  three closed-form derivatives. Var(ln N) = 1/N; first-order validity flagged past ~30% relative.

## 4.8 Error budget and measurability limit (~600 w)

**Sources:** REPORT §28, §31; `../decisions.md` D1; `../ORIENTATION_MAP.md` §2.

- Three mechanisms reduced to **one currency: composition error Δx**.
- Combination rule: **variances in quadrature, |bias| added linearly** — a *stated conservative
  envelope*, not a claim about the true distribution. Say why conservative was chosen.
- Clean-recovery residual carried **separately**, not folded in.
- **27 scenarios** = 3 pile-up levels × 3 couplings × 3 doses; and a **separate** 16-combination
  switch table. Do not conflate the two counts.
- **Accuracy threshold Δx = 0.01 absolute (decision D1)** — Walther's own bar. Say why the
  10%-relative alternative was rejected, and note that both were computed and stored
  (`*_relative10.csv` files exist).
- **Refusal to extrapolate outside the sampled x range** — a declared limit, not an oversight.

## 4.9 Software engineering (~250 w — first to compress if Wed overruns, cut 3)

**Sources:** `../CLAUDE.md`; REPORT §29, §32.

- pandas + stdlib, with **two declared exceptions**: numpy/scipy confined to `absorption.py`
  (curve fitting, root finding); matplotlib confined to the separate `figures/` package which
  the pipeline never imports.
- **304 tests** <!-- NUM: 304 | pytest --collect-only | 2026-09-10 -->; golden regression is the
  acceptance criterion.
- `run_analysis.py` regenerates every derived output in dependency order.
- The hash-check on `Aggregated\` that caught a silent dose regression on 17 Aug (REPORT §32.2)
  — one sentence, it is a real engineering lesson.
