# Dissertation framework — chapter plan, sources, page budget

*Drafted 2026-09-08 against `dissertation_outline_and_limits.md` (Sheffield MSc handbook, Jan 2026).
A proposal for Ethan to redirect, not a decision. Every "source" pointer is to a file in this repo;
every number quoted in the dissertation must be re-read from `Aggregated\*.csv` under production
settings, never lifted from prose (see §5, stale-number traps).*

**Constraints from the handbook:** main body ≤ **70 pages** (penalty ×(1 − pages over/100));
front matter, references and appendices excluded; 11–12 pt, 1.5 spacing; single PDF ≤ 20 MB;
appendices are unmarked and may not hold anything essential.

**Target: ~58–62 pages of main body**, leaving 8+ pages of slack for figures growing on layout.
At 1.5 spacing with figures, budget ~300 words/page → **~18,000 words** of main-body prose.

---

## 1. Chapter map

| # | Chapter | Pages | Answers | Drafted material |
|---|---|---|---|---|
| — | Title, Abstract, Individual contribution, Contents | excl. | — | nothing yet |
| 1 | Introduction | 6 | why + LO list + plan vs actual | `PRESENTATION_SCRIPT.md` §1–2, `WORKPLAN_17AUG.md` |
| 2 | Literature review | 11 | LO1 + the EDXS/MC background | `Lit review draft.pdf` (LO1 half only) |
| 3 | Theory | 5 | the inversion, the two overlaps | `PRESENTATION_SCRIPT.md` §A, REPORT §18.2, §27.1 |
| 4 | Methodology — the simulation framework | 13 | LO2 setup, LO4 sweep design | REPORT §1–5, 9–12, 15–17, 22, 26–27, 30–31; `writeupTODO.md` |
| 5 | Results | 14 | LO2, LO3, LO4 evidence | REPORT §13, 18–21, 23, 25, 28, 30–31; figs 1–6; `Aggregated\` |
| 6 | Discussion | 6 | the verdict and its caveats | `PRESENTATION_SCRIPT.md` §C, `VERDICT_BRIEF.md` caveats, `writeupTODO.md` §4–5 |
| 7 | Conclusions & future work | 3 | — | `PRESENTATION_SCRIPT.md` §C ⓶ |
| — | References, Appendices | excl. | — | see §4 |
| | **Total main body** | **58** | | |

**Results and Discussion stay separate** (Ethan, 2026-09-08) — the verdict gets its own chapter
so a marker can find it; the presentation's merged "Results & Discussion" is not the template.

---

## 2. Front matter (excluded from page count)

### Abstract (½–1 page)
Problem → why it matters → approach → result. Technical audience. Write **last**. Must contain the
verdict sentence (Ch6) and the three headline numbers, all re-read from CSV on the day.

### Individual contribution (max 1 page, before Contents — mandatory)
The handbook wants the student's specific role and every existing resource used. This project's
governance split (`CLAUDE.md`) is already that statement in draft form:
- **Ethan:** research question framing, all scientific judgement — density model choice, line
  definition, accuracy threshold, sum-peak settings, overlap treatment (bound vs model), the
  verdict; all supervisor correspondence; validation and interpretation of every result.
- **Existing resources to reference:** MC X-Ray Lite v1.7.1 (Gauvin, console build, Windows x64);
  Walther, *J. Microscopy* 2025 (DOI 10.1111/jmi.70058) and personal communications (July–Aug
  2026 — density endpoints, M-band factor, sum-peak application, "A" definition); Python 3,
  pandas, numpy, scipy (curve fitting/root finding only), matplotlib (figures only), pytest.
- **AI assistance — no School policy to comply with** (Ethan, 2026-09-09; see §6). The wrapper code
  was produced with an AI assistant doing mechanical scripting under Ethan's direction, and the
  dissertation prose is drafted the same way under the five-day plan (§8). **⚠ Still Ethan's call:**
  whether to declare it anyway and in what words. No longer a blocker on drafting this page.

---

## 3. Chapter-by-chapter

### Ch1 — Introduction (6 pp)

| § | Content | Source |
|---|---|---|
| 1.1 Background & motivation | GaAs → dilute bismide; benefit early (band gap), cost late (strain ∝ misfit²); devices live at a few % Bi; therefore the composition that matters is the hardest to measure. Sheffield APD result as the concrete stake. | `PRESENTATION_SCRIPT.md` §1; lit review Beat 3 |
| 1.2 The measurement problem | EDXS in STEM on thin foils; two peak overlaps (As Kα≈Bi Lα; Ga Lα+As Lα≈Bi Mα); absorption varies with thickness and composition; a simulation knows ground truth so quantification error is measurable. | `CLAUDE.md` "What this is"; `PRESENTATION_SCRIPT.md` §2 closing line |
| 1.3 Aim and objectives | Aim verbatim from the form; LO1–LO4 verbatim; **a map table: LO → chapter/section where answered**. Declare the deviations here in one line each and point to Ch4 (10⁷ trajectories ≤16 nm; matrix is cross + Set C, not grid; window arm dropped). | `Project Aims and Objectives.md`; `writeupTODO.md` §2 |
| 1.4 Report overview | one paragraph per chapter | — |
| 1.5 Project management | **Mandatory.** Original plan vs actual with a **revised Gantt**. Material: the Stage 1–2 build (Jul), supervisor meeting 19 Jul (density/detector corrections → production re-run), Stage 3 executor loss and rebuild (REPORT §22 — a real lesson about where deliverables live), 13 Aug Set C decision, 15 Aug recalibration (build estimates ran 6–8× fast; review/decisions/write-up did not compress), Walther offline 16–23 Aug forcing the modelling decisions onto Ethan, practical work complete 17 Aug, verdict 21–22 Aug, presentation, write-up. | `WORKPLAN_17AUG.md` §1, §3, §8; REPORT §15, §22 |

The original Gantt is transcribed in §7.1 and the actuals for the revised chart are in §7.2.

### Ch2 — Literature review (11 pp)

| § | Content | Status |
|---|---|---|
| 2.1 GaAs₁₋ₓBiₓ: incorporation, band structure, strain (LO1) | Beats 0–3 of the draft: isovalent substitution on the As sublattice (Tixier), VBAC and ~90 meV per x=0.01 bowing (Alberi; Usman), ΔSO engineering and Auger suppression → Sheffield APDs (Liu 2021), misfit strain and critical thickness (Tixier vs Lewis; kinetics), trade-off synthesis (Richards). | **~3,400 words drafted** = ~7 pp. This *is* LO1's deliverable — LO1 has nothing else behind it (WORKPLAN §2). Needs a closing paragraph handing off to 2.2: "so the composition worth measuring is dilute." |
| 2.2 Quantitative EDXS of thin foils | Cliff–Lorimer ratio method and k-factors; absorption correction and its thickness dependence; why free-standing foils at fixed take-off are the standard geometry; Walther 2025 as the central paper — his self-calibrating k\* method (Eqs 2/4/9), his Fig. 1 ratios, his stated precision bar (Δx = 0.01, p.2), his sum-peak treatment (fitted, ~15%, applied to experiment only). | **Not drafted.** ~2.5 pp. The Walther PDF is in the folder. Goldstein et al. is the reference for detector physics and must be cited (REPORT §27.6 flag). |
| 2.3 Monte Carlo simulation of X-ray emission | What MC X-Ray models (trajectories, ionisation cross-sections, absorption on exit, detector efficiency incl. the compiled-in ATW window); what it does not (pile-up/sum peaks — REPORT §17.4; secondary fluorescence — never confirmed, Walther's sims exclude it); why simulation can answer LO4 (known ground truth). | **Not drafted.** ~1.5 pp. Cite the MC X-Ray documentation but note the manual is out of date (units, line endings) — Ch4 carries the evidence. |
| 2.4 Detector physics used later | Si(Li) resolution: FWHM² = (2.355)²·ε·F·E + noise²; ε = 3.86 eV, F = 0.115 (Goldstein — cite, temperature caveat); pile-up as a bias, peak overlap as a variance. Sets up Ch3. | **Not drafted.** ~1 p. |

**This chapter holds the largest unwritten block (2.2–2.4, ~5 pp).** Schedule it early.

### Ch3 — Theory (5 pp)

Moved out of Methodology exactly as the presentation did (§A). Nothing here is a method; it is
what the methods rest on.

| § | Content | Source |
|---|---|---|
| 3.1 Ratio → composition | Walther's inversion; the three closed forms x, x(1−x), 1−x (Eqs 2/4/9); *A* is atomic weight, ρ atomic density (personal comm., resolves the paper's gloss). k\* as a self-calibrating constant; why a thickness proxy read from the spectrum (As K/L — "the arsenic ruler") is needed. | REPORT §18.2, §25.2; `ORIENTATION_MAP.md` §1 |
| 3.2 Absorption and mass-thickness | why ρ·t is the naive coordinate; the density model ρ(x) = 5.32 + 1.86x and why auto-mixed elemental densities are the wrong physical picture; the ~15% intensity effect of getting it wrong. | REPORT §6.3, §10, §15.2; `writeupTODO.md` §3 |
| 3.3 The two overlaps | sum peak: Ga Lα + As Lα = 2.380 keV vs Bi Mα 2.423 — 43 eV, 0.47 FWHM, merged; overlap (i): As Kα / Bi Lα — 297 eV, 1.74 FWHM, resolvable. **Bias vs variance** — the distinction the whole error budget rests on. | REPORT §27.1; `WORKPLAN_17AUG.md` §5 |
| 3.4 Counting statistics | Var(ln N) = 1/N; why expectation values from the simulator must be re-noised; first-order validity limit (~30% relative). | REPORT §30.1; `writeupTODO.md` §3, §4 |

### Ch4 — Methodology: the simulation framework (13 pp)

Ordered as the pipeline runs. Every item flagged in `writeupTODO.md` §1–3 lands here; tick them
off that file as they are written.

| § | Content | Source |
|---|---|---|
| 4.1 Architecture | six input files per run (`.sim/.sam/.mic/.par` authored, `.mdl/.rp` passed through); generate → execute → parse → aggregate → analyse; stored raw intensities only, derived quantities downstream and re-derivable; provenance manifest. Figure: pipeline block diagram. | REPORT §1, §16, §22, §32 |
| 4.2 Locked experimental design | the table from `CLAUDE.md` (200 keV, 10⁶/10⁷, free-standing box, TOA 25°, Si:Li 0.5 cm, noise 50, 10 000 photons, 5 eV channels). **Declared deviations:** 10⁷ trajectories ≤16 nm (Walther, 19 Jul); detector 0.5 cm not golden 0.3; exposure 1 nA × 715.5 s live as a *labelled reference*, probe current is Walther's estimate. Intensity column choice (`Intensity Emitted Detected`). | `CLAUDE.md`; REPORT §15.3–15.4; `writeupTODO.md` §2–3 |
| 4.3 Run matrix | Set A (10, thickness at x=0.2), Set B (5, composition at 100 nm), Set C (6, thickness at x=0.01). State the cross explicitly; Set C added 13 Aug because the cross could not predict its own interior — **causality the right way round** (Set C *is* the test, not the consequence). Frozen 15 verified byte-identical after Set C. | REPORT §11, §23.1–23.2; `PRESENTATION_SCRIPT.md` §B ⓷ |
| 4.4 Physical inputs and provenance | every constant to a cited source; density model derivation and the discrepancy in published anchors; atomic weights; line energies; the two `pending verification` detector constants and their robustness range. | REPORT §10, §12.1, §15.2, §27.6 |
| 4.5 Verification of the pipeline | (a) golden-set regression and classified diff; (b) **fault injection — five silent faults, five caught** (Å vs nm, weight vs atomic fraction, density 0, misspelling "corrected", line endings harmonised) — say plainly the harness was not kept; (c) end-to-end: generated inputs reproduce golden output within MC noise; (d) replication of Walther's three k\* constants to 1–3% — **framed as calibration against a known standard, not a finding**. | REPORT §2–5, §9, §18.3; `writeupTODO.md` §5 |
| 4.6 Analysis chain | diagnostic ratios under both line definitions (`principal` primary, `summed` robustness check — **decision 2**, reasons); k\* per route; As K/L as thickness proxy (a measurement — Set C — not a preference); held-out recovery in both unknowns, interpolation error measured on a held-out point. | REPORT §17, §18, §19, §25; `decisions.md` D2 |
| 4.7 Artefact modelling | **Sum peak — modelled:** analytic synthesis (MC X-Ray cannot), four switches (parents / basis / conserve / m_band_factor) with production settings and reasons (**decision 3**), level swept 0.1/1/10% never fixed, applied to the unknown only, fake counts capped at min(I_Ga, I_As), geometric mean in intensity basis. **Overlap (i) — bounded, not modelled:** σ = √(N + coupling·N_neighbour), coupling swept, resolution model validated at Mn Kα and against Walther's Lα1/Lα2 statement. **State the asymmetry and why.** **Counting statistics:** numerical propagation through the whole recovery, validated against three closed-form derivatives. | REPORT §26, §27, §30; `writeupTODO.md` §1; `decisions.md` D3 |
| 4.8 Error budget and measurability limit | three mechanisms in one currency (composition error); variances in quadrature + \|bias\| linear — a stated conservative envelope; clean-recovery residual carried separately; **27 scenarios** (3 levels × 3 couplings × 3 doses) and the separate **16 switch combinations**; refusal to extrapolate outside the sampled x range; **accuracy threshold Δx = 0.01 (decision 1)** — Walther's bar, why not 10% relative, both stored. | REPORT §28, §31; `decisions.md` D1; `ORIENTATION_MAP.md` §2 |
| 4.9 Software engineering (short) | pandas + stdlib with two declared exceptions (numpy/scipy in `absorption.py`; matplotlib confined to `figures/`); 304 tests; `run_analysis.py` regenerates everything; the hash-check that caught a silent dose regression. | `CLAUDE.md`; REPORT §29, §32 |

### Ch5 — Results (14 pp)

**Organised by objective, not chronology.** REPORT.md is chronological and REPORT_PLAIN_ENGLISH
contains superseded numbers — neither is a template for this chapter.

| § | LO | Content | Figures / tables | Source |
|---|---|---|---|---|
| 5.1 Geometry and absorption in the free-standing foil | LO2 | soft-L collapse with thickness; K/L ratios rising; per-line detector efficiency; escape-path consequence of 25° TOA. Presently scattered as by-product — frame it as LO2's answer. | **fig01** (ratios vs thickness, log axis, ρ = 5.692 — both departures from Walther's Fig. 1 printed on the figure) | REPORT §13.2, §18; `WORKPLAN_17AUG.md` §2 LO2 row |
| 5.2 Attenuation vs thickness and composition | LO3 | Bi K/L/M relative to Ga and As references; Bi K is the most absorption-immune route yet yields ~103× fewer photons; density-model divergence with thickness (0 → 8.4%, ρ·t not ρ) as evidence; **ρ·t is not a sufficient absorption coordinate** — Set C observed vs the Set A ρ·t prediction: Ga K/L **−22.79%** at 1024 nm, As K/L **−1.60%**; not a density artefact (a constant offset cannot give **18.3×** growth from 32 nm). *Ruling 2026-09-10: quote the `matched_rho_t` block throughout, growth factor included — the earlier "17×" came from the `matched_thickness` block and must not be mixed in.* | **fig02** (ρ·t insufficiency), **fig06** (Bi K absorption vs photons); k\* table (Set A) | REPORT §13.3–13.4, §20, §23; `Aggregated\corner_rho_t_setA_vs_setC.csv`, `kstar_calibration_setA.csv` |
| 5.3 Cross-check against the published work | — | k\* constants reproduced to 1–3%; k\* composition-invariance (one route invariant to resolution limit); **Bi M discrepancy 1.506 ± 0.020 between codes**, three confirmations, cause unidentified. | table vs Walther Figs 3–5 | REPORT §18.3–18.4, §19, §21 |
| 5.4 Recovery of composition | LO4 | held-out recovery: held-out beats handed-thickness (**0.003626 vs 0.003915**, +7.4%); As K/L beats Ga K/L by **56%**; Set C pushed through as unknowns — calibration-transfer residual **~10⁻⁷ for the Bi Lα/As Kα route specifically** (1.17e-07) across 32–1024 nm (closes the "only at 100 nm" limitation). *Corrected 2026-09-10: the previous figures (0.00342 / 0.00377 / 47%) were means over **both** line definitions; these are `principal`, per decision D2. The 10⁻⁷ must always name its route — the file-wide mean is 1.31e-02.* | **fig05** (recovery clean vs as-measured) | REPORT §25; `VERDICT_BRIEF.md` caveat 6; `roundtrip_*.csv`; `DISSERTATION_NUMBERS.md` §5 |
| 5.5 The sum peak is composition-selective | LO4 | at 1% pile-up: fake counts ≈ 55% of Bi M at x = 0.01 vs ≈ 2% at x = 0.20 (~23×); the calibration-corruption cancellation error caught and what it shows; route ranking survives all 16 switch combinations; which switches matter (basis 2.2×, M-band 1.7×). | **fig04** (sum-peak selectivity) | REPORT §26.3, §26.6, §28; `sumpeak_*.csv` |
| 5.6 Counting statistics and the overlap bound | LO4 | at x = 0.01, Walther's dose: noise 3.5% vs sum peak on Bi M; overlap (i) worst case ~13% at x = 0.01 vs 1% at x = 0.20; below ~1% coupling the overlap adds little over the photon floor. | table (WORKPLAN §5 bound table, re-read from CSV) | REPORT §27.4, §30.2; `counting_*.csv`, `overlap_i_bound.csv` |
| 5.7 Error budget and measurability limit | LO4 | the 27-scenario band per route; **across the range: Bi M fails 27/27, Bi K fails 18/27 (crosses near x ≈ 0.1), Bi L fails 0/27**; at x = 0.01 specifically: Bi M 18/27, Bi K 0/27, Bi L 0/27 — both counts are correct, never "fix" one to match the other; the Bi L budget decomposition — sum peak four orders below, counting and overlap comparable. | **fig03** (headline) | REPORT §31; `route_ranking.csv`, `measurability_limit.csv`, `error_budget.csv` |

### Ch6 — Discussion (6 pp)

| § | Content | Source |
|---|---|---|
| 6.1 The verdict | **Ethan's finished content — lift from `PRESENTATION_SCRIPT.md` §C ⓵ (slide 11), do not redraft:** Bi Lα referenced to As Kα, principal definition, quantifiable to x ≈ 0.01 at the reference dose. Robust three ways: both thresholds, both line definitions, 32 nm–1 µm. | `PRESENTATION_SCRIPT.md` §C |
| 6.2 Why the alternatives fail | Bi M: sum-peak bias, uncurable by counting, 27/27. Bi K: **range**, not photon starvation — clears at 100 s at x = 0.01, crosses partway up; a window whose edge needs the answer to locate. **The "12× dose" line is retired** (use instead: Bi K counting σ **34.98%** vs Bi L **3.46%** at the reference dose). ⚠ **"Crosses near x ≈ 0.1" holds only at the reference dose 7.155** (`x_limit` 0.0865–0.0933); at dose 1.0 it crosses at **x ≈ 0.0113**, and at 71.55 it never crosses. Qualify by dose or the claim is wrong for a third of the scenarios *(added 2026-09-10)*. | `PRESENTATION_SCRIPT.md` §C ⚠ box; `ORIENTATION_MAP.md` §4; `DISSERTATION_NUMBERS.md` §2–3 |
| 6.3 The central tension | the best-conditioned route on both axes is the one sitting on overlap (i); no route is both stable and spectrally clean; the artefact the project set out to study does not limit the line it recommends (fig03 right panel). | `writeupTODO.md` §5; `PRESENTATION_SCRIPT.md` fig03 Q&A |
| 6.4 Relation to Walther 2025 | what the replication verifies vs what this work adds: composition-invariance of k\*, the corner finding (ρ·t insufficiency / As as ruler), the Bi M discrepancy, sum-peak selectivity, the bounded low-x limit. The density model supersedes the paper's own values on his advice. | `WORKPLAN_17AUG.md` §2 critical evaluation; `writeupTODO.md` §3, §5 |
| 6.5 Limitations | the `writeupTODO.md` §4 list, each as a declared decision: Bi M cross-code factor; overlap coupling swept not derived (assumption ladder; two constants to cite); first-order flags; floor below x = 0.01 unbracketed; window arm dead (scope reduction, not omission); `summed` overlap is a lower bound; golden files are format truth only. Secondary fluorescence never confirmed with vendor. | `writeupTODO.md` §4; `VERDICT_BRIEF.md` caveats 1–5 |

### Ch7 — Conclusions and future work (3 pp)

Restate aim → the LO-by-LO answers in one paragraph each → the verdict sentence → future work
as three doable items (measure the overlap coupling; two dilution runs x = 0.002 / 0.0002 at
100 nm to bracket the floor — ~20 min compute; resolve the Bi M discrepancy between codes) plus
the two reserves (Bi K error bars past first order; the detector window). **Forward-looking, not
apologetic** — `PRESENTATION_SCRIPT.md` §C ⓶ framing.

---

## 4. Appendices (unmarked, uncounted — nothing essential goes here)

| App. | Content | Source |
|---|---|---|
| A | Run matrix: all 21 run_ids, thickness, x, ρ, trajectories, wall time | `provenance_manifest.json` |
| B | Annotated input-file templates (`.sim/.sam/.mic/.par`) showing the load-bearing fields and the trap list (Å, weight fraction, density, misspelling, line endings) | `Golden\`, `CLAUDE.md` trap list |
| C | Physical constants with sources (densities, atomic weights, line energies, ε, F) | `spec.py` source comments; REPORT §10, §12.1 |
| D | Output schema: the 21-row intensity CSV format; `Aggregated\` file inventory with one-line descriptions | `ORIENTATION_MAP.md` §3; REPORT §16.1 |
| E | Full 27-scenario measurability table and 16-combination switch table | `measurability_limit.csv`, `route_ranking.csv`, `sumpeak_switch_influence.csv` |
| F | Fault-injection record (the five faults and how each surfaced) | REPORT §5 |
| G | Repository structure, module list, test count; how to regenerate every result (`run_analysis.py`) | REPORT §32.1 |
| H | Supplementary figures: k\* vs thickness, k\* vs K/L ratio (from the artifact) | `artifact\` |

---

## 5. Cross-cutting rules for the write-up

1. **Re-read every number from CSV under production settings** (`principal`, Δx = 0.01,
   `m_band_factor` 1.743, set 2026-08-21). Anything quoted before that date may be stale.
   Known stale figures still in the prose sources:
   - "fake counts 97% of Bi M at x = 0.01" → now **≈ 55%** (m_band_factor change)
   - "Bi K needs >12× Walther's dose" → **retired**; computed against the scrapped 10% relative bar
   - "Bi L fails only 9 dose-or-worst-coupling corners" (WORKPLAN, 17 Aug) → 10%-relative figure; under Δx = 0.01 Bi L fails **0/27**
   - `sumpeak_switch_influence.csv` `relative_difference` is fractional (1.176 → "2.2×", not "1.2×")
   - `measurability_limit.csv` column `target_relative` holds 0.01 in absolute mode — read with `metric`
   - **Filter traps found 2026-09-10** (`DISSERTATION_NUMBERS.md` §0) — several figures quoted in
     §3 above were means over **both** line definitions, not `principal`. Ethan confirmed
     2026-09-10 that `principal` is quoted throughout (decision D2). Corrected: recovery
     0.00342/0.00377 → **0.003626/0.003915**; As-beats-Ga 47% → **56%**; the ~10⁻⁷ transfer
     residual is **route-specific** (Bi Lα/As Kα), not file-wide. **Before quoting any aggregate,
     check whether it was filtered to `principal`.**
   - "297 tests" → **304** (`pytest --collect-only`, 2026-09-10); "23 aggregated CSVs" → **28**
2. **Two counts that look contradictory are both right:** "across the range" vs "at x = 0.01".
   Label which one every time.
3. **Golden files are format truth, never physics** — say so where the regression tests appear,
   or a reader takes them as physics validation.
4. **Every choice as a decision with a reason**, never a default — the `writeupTODO.md` test:
   "if an examiner could ask 'why did you do it that way?' and the answer isn't in the code."
5. **Plain first, jargon second** (the presentation's register rule) — but the dissertation's
   audience is technical, so the technical term must always follow.
6. **The verdict is Ethan's text.** Ch6.1 and the abstract's verdict sentence are lifted from the
   script, not redrafted; the causality in 4.3 (Set C is the test) and the Bi K reason (range)
   are the two places where earlier prose gets it wrong and must not be copied.
7. **Figure captions must be self-contained** and must carry the settings they were rendered
   under (fig03 was regenerated 2026-08-23 with counts derived at render time — the others should
   be checked for stale captions; fig06's title was corrected 2026-08-24).

---

## 6. Inputs from Ethan — status

- **Submission deadline: Sun 14 Sep 2026, 14:00.** Received 2026-09-08.
- **Original Gantt:** received 2026-09-08 as an image; transcribed in §7 so it lives in the repo.
- **Ch5/Ch6: keep separate.** Decided 2026-09-08.
- **Writing window shortened to five days: Wed 10 → Sun 14 Sep.** Ethan, 2026-09-09. §8 rewritten;
  Tuesday 9 is now a Claude-only prep evening with no Ethan time in it.
- **AI assistance: permitted, no School policy exists.** Ethan, 2026-09-09 — the university
  publishes no guidelines on AI use, so §8 assumes Claude drafts and Ethan directs and verifies
  throughout. **Residual, still Ethan's call:** no policy is not the same as no declaration. A
  short statement on the Individual contribution page — what the assistant did (mechanical
  scripting, drafting under direction) and what stayed Ethan's (all scientific judgement, every
  number verified) — costs a paragraph and forecloses a question a marker would otherwise answer
  for himself. Recommended, not decided.
- Still open: chapter-order preference from Walther (if any); referencing style (draft uses
  Harvard author–date).

---

## 7. Project management material for Ch1.5

### 7.1 Original plan — transcribed from the submitted Gantt ("Dissertation Timeline")

Dates read off the chart's weekly axis (14 Jun → 06 Sep); ±2 days.

| Phase | Task | Planned |
|---|---|---|
| 1. Theory | T1.1–T1.2 Literature review & physics of Bi L-line spectral overlap and fitting limitations | ~10–20 Jun |
| | T1.3 Draft Introduction & Lit Review chapters | ~19–24 Jun |
| 2. Baseline | T2.1 MCXray installation and manual geometry configuration | ~26 Jun–2 Jul |
| | T2.2 Manual validation run (100 nm, 0.1 Bi) to verify spectra output | ~3–7 Jul |
| Milestone | Submit Project Progress Form | ~9 Jul |
| 3. Sweep | T3.1–T3.2 Write and debug Python batch automation script | ~10–18 Jul |
| | T3.3 Execute 30-parameter matrix via automated script | ~19–26 Jul |
| | T3.4 Draft Methodology chapter (parallel to T3.3) | ~19–26 Jul |
| 4. Analysis | T4.1 Data extraction and filtering | ~27 Jul–1 Aug |
| | T4.2 Prove/disprove supervisor's L-line hypothesis via data | ~2–14 Aug |
| | T4.3 Generate final graphs, absorption curves, and heatmaps | ~15–27 Aug |
| 5. Synthesis | T5.1 Draft Results, Discussion, and Conclusion chapters | ~9–24 Aug |
| | T5.2 Build and rehearse oral presentation | ~23–28 Aug |
| Milestone | Oral Presentation (in person) | ~29 Aug |
| | T5.3 Formatting & Polish | ~29 Aug–4 Sep |
| Deadline | Submit Final Dissertation (14:00) | **~6 Sep** (actual deadline: **14 Sep**) |

### 7.2 Actuals — for the revised Gantt (dates from REPORT.md / WORKPLAN / decisions.md)

| Task as it actually happened | Actual | Evidence | Maps to plan |
|---|---|---|---|
| Aims & Objectives form signed | 18 May | form | — |
| Lit review Section A (LO1) drafted | Jun (confirm) | `Lit review draft.pdf` | T1.1–T1.3 (Intro/Lit *chapters* not drafted) |
| Golden set produced by hand in MC X-Ray; format traps discovered | Jun–early Jul (confirm) | REPORT §2, §6 | T2.1–T2.2 |
| Stage 1+2: input generator, parser, golden regression tests (109 tests) | early–mid Jul | REPORT §1–5, §9 | T3.1–T3.2 |
| Density-model investigation; two models built; 30-run comparison matrix executed (98.9 min) | mid Jul | REPORT §10–13 | T3.3 ("30-parameter matrix") |
| Supervisor meeting: density endpoints, Si:Li 0.5 cm, 10⁷ for thin foils; 15-run production re-run (127 min) | **19 Jul** | REPORT §15 | — (unplanned correction cycle) |
| Stage 5 aggregation + provenance manifest | ~19–25 Jul | REPORT §16 | T4.1 |
| Stage 6 diagnostic ratios; line-definition question deferred | **25 Jul** | REPORT §17 | T4.1 |
| k\* tables, cross-check vs Walther Figs 3–5; Set B invariance persisted | **3 Aug** | REPORT §18–19 | T4.2 |
| Bi K admitted (LO3 closed); Walther's reply — Bi M discrepancy pinned 1.506; sum-peak placement decided; **Stage 3 executor rebuilt after loss**; **Set C decided and run** (6 runs, 25.4 min); corner analysis | **13 Aug** | REPORT §20–23; WORKPLAN §3 | T4.2 (+ unplanned matrix extension) |
| Walther unavailable 16–23 Aug; plots promoted to first-class deliverable | 14 Aug | WORKPLAN §1, §3.5 | — |
| Figures package; figs 1–2 | **14 Aug** | REPORT §24 | T4.3 |
| Held-out recovery; sum-peak synthesis; overlap (i) bounded | **15 Aug** | REPORT §25–27 | T4.2 |
| Sensitivity sweep; counting statistics; error budget / measurability limit; figs 3–6; analysis driver; 297 tests — **practical work complete** | **17 Aug** | REPORT §28–32; WORKPLAN §3 | T4.2–T4.3 |
| Decisions 1–3 (threshold, line definition, sum-peak settings); Set C pushed through recovery | **21 Aug** | `decisions.md`; `VERDICT_BRIEF.md` | T4.2 |
| Verdict reached | **22 Aug** | memory / `PRESENTATION_SCRIPT.md` §C | T4.2 |
| Presentation script and deck built; fig03 regenerated; stale claims corrected | 23–25 Aug | `PRESENTATION_SCRIPT.md` header, §C ⚠ | T5.2 |
| Oral presentation delivered | (Ethan to confirm date) | — | Milestone |
| Dissertation chapters drafted | **10–13 Sep** | this file §8 | T1.3 + T3.4 + T5.1 (all three planned drafting windows slipped into the final week) |
| Formatting, PDF, submission | **14 Sep** | — | T5.3 + Deadline |

**The honest management story for 1.5:** the build phases ran roughly to plan or faster (the 15 Aug
recalibration: code estimates ran 6–8× fast); two things were not in the plan and consumed the
slack — a supervisor-driven physics correction cycle (19 Jul) and the loss/rebuild of the executor
(REPORT §22) — and the chapter drafting scheduled in parallel with the build (T1.3, T3.4, T5.1)
did not happen in parallel. The lesson worth stating is the one already recorded: build work
compresses, writing and decisions do not.

---

## 8. Five-day writing plan — Wed 10 → Sun 14 Sep

**Revised 2026-09-09.** The original six-day plan (Tue 9 → Sun 14) lost its first day. Two things
changed with it: one working day is gone (~4.5 h), and **Ethan is drafting with Claude** — the
School publishes no AI-use policy (Ethan, 2026-09-09), so AI-assisted drafting is permitted and is
assumed throughout below.

**What that changes.** Not the page budget, not the chapter structure, not the §3 section order.
It changes *where Ethan's hours go*. Under the six-day plan the constraint was composition —
~500 words/hour worked up from source notes. The constraint is now **review bandwidth**: Claude
drafts from the repo sources, Ethan reads, corrects and approves. Reviewed-and-corrected technical
prose runs ~1,200–1,500 words/hour, so ~15,500 new words costs roughly **11 h of Ethan's
attention** rather than ~30 h of typing. That recovered time is what absorbs the lost day. It is
not spare capacity — it is Tuesday's replacement.

**The risk moves with it.** A drafting assistant is fastest at precisely the failure this project
is most exposed to: fluent prose wrapped around a stale number. §5 rule 1 already lists five
values wrong in the repo's own prose. **Every number in a drafted paragraph is unverified until
Ethan has matched it to a CSV cell.** The Saturday number check is therefore promoted from polish
to the single item that cannot be cut, and rule 4 below is load-bearing, not bookkeeping.

**Time assumed — correct it if wrong:** Wed–Fri ~2 h before work + ~2.5 h evening = ~4.5 h/day;
Sat ~8 h; Sun 09:00–12:00. ≈ **24.5 h** for ~15,500 new words plus assembly.

**Rules (1 and 2 are reversed from the six-day plan):**

1. ~~Claude's job each session is mechanical prep, not prose~~ → **Claude drafts prose; Ethan
   directs and verifies.** Each session runs: ~10 min brief (which §, which sources, what it must
   say, what it must not claim) → Claude drafts → Ethan corrects and approves. Ethan writes from
   scratch only where the text is genuinely his: **Ch6.1 (the verdict), Ch1.5 (project
   management), the Individual contribution page.**
2. ~~Draft in order of difficulty~~ → **draft in dependency order.** The old rule put the hardest
   blank page first because blank pages were the expensive thing. With a drafting assistant the
   blank page is cheap and the **results number sheet is the bottleneck** — Ch5 and Ch6 cannot be
   drafted safely without it. It moves ahead of all results prose, to Day 0.
3. No polishing before Saturday. *(unchanged)*
4. Every number typed carries its file/column/filter in an inline comment for the Saturday check.
   *(unchanged, and now the main defence — see the risk note above)*
5. **Nothing counts as done until Ethan has read it.** A section Claude has drafted and Ethan has
   not read scores zero in that day's tally. This is the rule that keeps the schedule honest.

| Day | Slot | Task | Words | Ethan / Claude |
|---|---|---|---|---|
| **Day 0 — Tue 9, tonight** | — | **Claude only, no Ethan time.** (a) **Results number sheet** — every value Ch5–6 will quote, re-read from `Aggregated\*.csv` under production settings (`principal`, Δx = 0.01, `m_band_factor` 1.743), each with file/column/filter; (b) chapter skeleton files, headings + source pointers per §3; (c) figure-caption data with the render settings each figure was produced under, stale captions flagged. | — | Claude |
| **Wed 10** | AM 2 h | **Number-sheet spot-check (~30 min, Ethan alone)** — take six values spanning the five stale-figure traps in §5 and confirm them against the CSVs yourself. Everything downstream trusts this sheet; it is the cheapest half-hour of the week. Then **Ch4.1–4.4** — architecture, locked design + declared deviations, run matrix (Set C *is* the test), physical inputs and provenance. | ~1,500 | Claude drafts from `CLAUDE.md` tables + REPORT §1, §10–12, §15–16, §23; Ethan verifies every constant carries a cited source |
| | PM 2.5 h | **Ch4.5–4.9** — verification (golden regression, five-faults fault injection incl. "harness not kept", replication **framed as calibration**), analysis chain, artefact modelling (sum peak modelled / overlap bounded — state the asymmetry), error budget construction, software note. | ~2,000 | Claude drafts; Ethan checks that decisions D1–D3 read as *his* reasoning |
| | *overnight* | Claude: draft Ch2.2–2.4 and Ch3 against the skeletons, so Thursday is a review pass rather than a drafting pass. | — | Claude |
| **Thu 11** | AM 2 h | **Ch2.2–2.4** — Cliff–Lorimer and k-factors, Walther's self-calibrating k\* (Eqs 2/4/9), his Δx = 0.01 bar, his sum-peak treatment; what MC X-Ray models and what it does not; Si(Li) resolution, pile-up-as-bias vs overlap-as-variance. | ~1,600 | Review + correct the overnight draft, **with the Walther PDF open** — the one block where a drafted summary of a source must be checked against the source itself |
| | PM 2.5 h | **Ch3 Theory** (inversion, ρ(x) = 5.32 + 1.86x, the two overlaps, counting statistics) + **Ch2.1**: paste lit-review Section A in and write the hand-off paragraph to 2.2. | ~1,600 | Review + correct; Ethan writes the 2.1→2.2 hand-off himself — one paragraph, his argument |
| | *overnight* | Claude: draft Ch5.1–5.7 strictly from the number sheet, every quoted value carrying its source comment per rule 4. | — | Claude |
| **Fri 12** | AM 2 h | **Ch5.1–5.4** — LO2 geometry/absorption, LO3 attenuation + the ρ·t insufficiency corner, cross-check vs Walther (k\* to 1–3%, Bi M 1.506 discrepancy), held-out recovery. Figs 1, 2, 6, 5. | ~2,000 | Review with the number sheet open beside it; **tick each value as checked** |
| | PM 2.5 h | **Ch5.5–5.7** — sum-peak selectivity (≈55%, not the retired 97%), counting statistics + overlap bound, error budget and measurability limit. Fig 4, **fig03**. Both the "across the range" and "at x = 0.01" counts labelled every time (§5 rule 2). | ~1,800 | Review; Ethan personally checks the 27/27, 18/27 and 0/27 counts and their labels |
| | **22:00** | **⚑ Decision point — see below.** | | |
| **Sat 13** | AM 3 h | **Ch6 Discussion** + **Ch7 Conclusions & future work**. 6.1 is **lifted verbatim** from `PRESENTATION_SCRIPT.md` §C ⓵ — not redrafted, and not paraphrased by Claude. 6.2: Bi K fails on **range**, not dose (the "12× dose" line is retired). 6.3 central tension, 6.4 relation to Walther, 6.5 limitations. Ch7 forward-looking, not apologetic. | ~2,600 | **Lowest AI leverage of the week** — Ethan-led; Claude assembles the limitations list and future-work items from `writeupTODO.md` §4–5 |
| | midday 2 h | **Ch1** — background, measurement problem, aim + LO1–LO4 verbatim with the **LO→section map table**, report overview, and **1.5 project management with the revised Gantt** (§7.1 plan vs §7.2 actuals; the honest story is at the end of §7). | ~1,800 | Ethan writes 1.5 himself; Claude drafts 1.1–1.4 and renders the Gantt table |
| | PM 3 h | **Abstract** (written last; carries the verdict sentence and the three headline numbers), **Individual contribution** (see §6 — now unblocked), **appendices A–D and G** (E/F/H if time), figure captions with render settings; then the two checks: full read-through against `writeupTODO.md` — every entry written or consciously dropped — and the **number check**, every quoted value against the number sheet. | ~600 | Claude generates appendices A–D/G mechanically and the `writeupTODO.md` coverage report; **the number check and the read-through are Ethan's and are not delegable** |
| | **18:00** | **⚑ Hard line — see below.** | | |
| **Sun 14** | 09:00–12:00 | Formatting (11–12 pt, 1.5 spacing, numbered figures/tables), page count against 70, PDF export ≤ 20 MB, **open the PDF and confirm every figure actually rendered**, submit **by 12:00**. The two hours to the 14:00 deadline are the morning's deliverable — do not spend them writing. | — | Ethan |

### Checkpoints and the cut line

Decide these now, not at the moment they bite.

- **Wed 10, 22:00** — Ch4 drafted *and read*. If it is not, the week has no slack left in it: take
  cut 3 that night and compress Ch4.9 to a single paragraph.
- **Fri 12, 22:00 — the decision point.** Ch2, Ch3 and Ch5 should all be complete. Saturday can
  absorb Ch6, Ch7, Ch1 and the entire assembly block, but it cannot also absorb an unfinished Ch5.
  If Ch5.5–5.7 is not done, take cuts 1 and 2 immediately.
- **Sat 13, 18:00 — hard line.** All prose complete; the read-through and number check begin.
  Anything unwritten at 18:00 is **cut, not moved to Sunday.** Sunday morning is formatting and
  submission only — an overrun there spends the buffer, and the buffer is what protects a 14:00
  deadline from a 20 MB PDF export that fails at 11:50.

**Cut in this order if behind** *(unchanged from the six-day plan — the ordering was right)*:
1. Appendices E, F, H (uncounted, nice-to-have).
2. Ch5.3 cross-check → a single table with two sentences.
3. Ch2.3–2.4 → one page combined.
4. Ch3 folded into Ch4 as a 2-page "basis" subsection.

**Never cut:** Ch1.5 project management (mandatory), Individual contribution (mandatory), the
declared deviations in Ch4.2–4.3, Ch5.7 + fig03, Ch6.1 verdict, Ch7 — **and, new under the
five-day plan, the Saturday number check.** Without the first six the report fails the handbook or
has no answer; without the last it is a fluent report that quotes retired figures.
