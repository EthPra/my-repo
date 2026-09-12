# Ch1 — Introduction

**6 pp · ~1,800 words · drafted Sat 13 midday**

⚠ **1.5 is mandatory and is Ethan's own text.** Claude drafts 1.1–1.4 and renders the Gantt table.

---

## 1.1 Background and motivation (~450 w)

**Sources:** `../PRESENTATION_SCRIPT.md` §1; lit review Beat 3.

- GaAs → dilute bismide.
- **The trade-off that frames the whole project: the benefit arrives early (band gap, ΔSO) and
  the cost arrives late (strain ∝ misfit²).** Devices therefore live at a few percent Bi.
- **Therefore the composition that matters is the hardest one to measure.** That sentence is the
  motivation — everything else in the chapter serves it.
- The Sheffield APD result as the concrete stake.

## 1.2 The measurement problem (~350 w)

**Sources:** `../CLAUDE.md` "What this is"; `../PRESENTATION_SCRIPT.md` §2 closing line.

- EDXS in STEM on thin foils.
- **Two peak overlaps:** As Kα ≈ Bi Lα; and Ga Lα + As Lα pile-up ≈ Bi Mα.
- Absorption varies with **both** thickness and composition.
- **A simulation knows the ground truth, so quantification error is measurable rather than
  estimated.** This is the methodological justification for the whole approach — state it here.

## 1.3 Aim and objectives (~400 w)

**Sources:** `../Project Aims and Objectives.md`; `../writeupTODO.md` §2.

- **Aim verbatim from the form. LO1–LO4 verbatim.** Do not paraphrase the assessment criteria.
- ⚠ **A map table: LO → chapter/section where it is answered.** A marker should not have to hunt.
  Draft version:

  | LO | Answered in |
  |---|---|
  | LO1 material rationale | Ch2.1 |
  | LO2 simulation setup / geometry | Ch4.1–4.4, Ch5.1 |
  | LO3 attenuation vs thickness & composition | Ch5.2 |
  | LO4 quantification limit | Ch4.6–4.8, Ch5.4–5.7, Ch6 |

- **Declare the three deviations here, one line each, pointing to Ch4:**
  1. 10⁷ trajectories for foils ≤16 nm (not 10⁶ throughout) → Ch4.2
  2. The matrix is a **cross plus Set C**, not a full grid → Ch4.3
  3. The detector-window arm was **dropped** — windowless is impossible in MC X-Ray Lite → Ch4.2, Ch6.5

## 1.4 Report overview (~200 w)

One paragraph per chapter. Write after the chapters exist.

## 1.5 Project management (~400 w) — **MANDATORY · ETHAN WRITES THIS**

**Sources:** `../WORKPLAN_17AUG.md` §1, §3, §8; REPORT §15, §22.
**Gantt material:** `../DISSERTATION_FRAMEWORK.md` §7.1 (original plan, transcribed) and
§7.2 (actuals). Claude renders both tables; the narrative is Ethan's.

Required: original plan vs actual, **with a revised Gantt**.

Material to draw on:
- Stage 1–2 build (Jul).
- **Supervisor meeting 19 Jul** — density and detector corrections forced a full production
  re-run. An unplanned correction cycle.
- **Stage 3 executor loss and rebuild** (REPORT §22) — a real, statable lesson about where
  deliverables live.
- 13 Aug: Set C decision.
- **15 Aug recalibration: build estimates ran 6–8× fast; review, decisions and write-up did not
  compress.**
- Walther offline 16–23 Aug, forcing the modelling decisions onto Ethan.
- Practical work complete 17 Aug; verdict 21–22 Aug; presentation; write-up.

⚠ **The honest story (framework §7, end):** the build phases ran to plan or faster; two unplanned
things consumed the slack (the 19 Jul physics correction cycle and the executor loss/rebuild);
and the chapter drafting scheduled *in parallel* with the build (T1.3, T3.4, T5.1) did not happen
in parallel — all three windows slipped into the final week. **The lesson worth stating:
build work compresses; writing and decisions do not.**
