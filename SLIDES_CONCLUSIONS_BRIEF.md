# Conclusions & Future Work slides — handoff brief

*Written 2026-08-21 to carry the verdict into the slide-building session. Companion file:
`PRESENTATION_CONCLUSIONS_DELIVERY.md` — the spoken script these slides sit behind. Take both.*

> **⚠ Superseded in part, 2026-08-23.** The deck was restructured to the School's brief (10 active
> slides + 1 parked); this section is now **slides 9–10**, not 1–3, and the three conclusion
> slides were merged to two. The spoken script has moved to `PRESENTATION_SCRIPT.md` §C.
> **What is still authoritative here: the numbers table and the "must not claim" list.**
> Slide numbering and the 3-slide sequence below are historical. See `PENDING_EDITS.md`.

**Design and structure: defer entirely to the conventions already established across slides
1–11** (`GaAsBi_EDXS_Presentation_Slides_1-11.pptx`) — the circled sequence numbers restarting
at ① for each new section, the arrow-bullet phrasing, the bold stat callouts, the terse
one-punchline-per-slide density. This brief specifies *what goes on each slide and in what
order*, never how it should look.

**Scope: this is ONLY the "Conclusions & Future Work" section** — the fifth and final item on
the Overview slide (slide 2). It does not cover Results & Discussion / key findings, which are
being built separately. Do not duplicate the mechanism figures or route-ranking detail from that
section here — this section's job is to *land* the verdict and hand back for questions, not
re-derive it.

---

## Two hard constraints

1. **State the verdict plainly — this section exists to do that.** Unlike the methodology
   section (which was explicitly forbidden from front-running it), this is where the
   recommendation, the ranking, and the accuracy threshold finally get said.
2. **Two minutes of speech, total.** ~275 words at 130–145 wpm. Slide density should follow —
   this is a *landing*, not a re-argument. If a slide needs its own sub-argument to be
   understood, it belongs in Results & Discussion, not here.

---

## Slide sequence — 3 slides

| # | Landmark | Budget | Content | Figure |
|---|---|---|---|---|
| 1 | ① The verdict | ~15 s | **Bi Lα referenced to As Kα, principal line definition** — quantifiable to **x ≈ 0.01** at Walther's own acquisition time (715.5 s). Stated as the headline, not hedged. | **fig03_measurability_limit** ⚠ regenerate first (see below) |
| 2 | ② Why it holds | ~70 s | Three mechanisms, one currency (error on recovered x). **Bi M fails on the sum peak — a bias, every composition, uncurable by dose.** **Bi K fails on range — it clears the bar at x = 0.01 but crosses it partway up the composition range, in 18 of 27 scenarios; Bi L crosses in none.** *(Corrected 2026-08-23: the previous "photon starvation / 12× Walther's dose" claim was computed against the retired 10% relative bar and is false under Δx = 0.01 — Bi K clears at the shortest acquisition swept. Do not reinstate it, and do not substitute another dose multiplier.)* **Bi L passes all 27 swept scenarios**; its own weak point is overlap (i) — the thing this project set out to characterise, not an unknown gap. Then robustness: same winner under a **10% relative bar and Walther's own Δx = 0.01 literature bar**; same winner under **both line definitions**; **directly verified** (not just argued) across the full thickness range **32–1024 nm** — calibration-transfer residual **≤0.002%** at every thickness tested. | none needed — numbers carry it |
| 3 | ③ Limitations & future work | ~35 s | Framed forward-looking, not defensive. **Since 2026-08-23 only (1)–(3) go on the slide; (4) and (5) are held as question material** — five limitations in 35 seconds reads as a list, not a point: **(1)** overlap coupling is swept, not measured — survives the worst case regardless; **(2)** detection floor below x=0.01 unbracketed — two more runs would find it; **(3)** Bi M cross-code discrepancy (1.506±0.020) unresolved; **(4)** Bi K's own error bars break down past first order — needs a higher-order treatment to quote precisely; **(5)** detector window untested — windowless proved impossible in this simulator, a declared scope reduction. | none |

---

## Figures

| file | use |
|---|---|
| `fig03_measurability_limit` | **Slide 1.** The LO4 headline — reserved for exactly this moment (`SLIDES_METHODOLOGY_BRIEF.md` held it back for this reason). **✅ Regenerated 2026-08-23 — the hold is lifted.** `figures/fig03_measurability.py` was switched from `relative_total` (%) to `total_error` (absolute), the reference line now marks Δx = 0.01, and the title and caption counts are **derived from `error_budget.csv` at render time** rather than typed — the old hardcoded "Bi L in 9 of 27" is what survived the threshold decision as a false statement. The title now reads "Only Bi M misses the target at the lowest x", which is what the data says. 304 tests green. |

---

## Numbers — quote these exactly

All re-derived from the current `Aggregated\*.csv` on 2026-08-21, post decisions 1–3.

| | |
|---|---|
| Winning route | **Bi Lα / As Kα, principal definition** |
| Measurable to | **x ≈ 0.01**, all **27/27** swept scenarios pass |
| Accuracy bar used | **Δx = 0.01** (Walther, J. Microsc. 2025, p.2) — also holds at 10% relative |
| Bi L's own dominant limitation | **overlap (i)**, not counting statistics (worst-case error **0.0034** in x) |
| Bi M | fails **all 27** scenarios; dominant mechanism **sum peak** (bias, uncurable by dose) |
| Bi K | fails **18 of 27** (principal, vs As K) — crosses Δx = 0.01 inside the range, typically near x ≈ 0.09 and as low as **x ≈ 0.011** in the worst corner; **Bi L crosses in none of the 27**. Clears the bar *at* x = 0.01, so the failure is range, **not** dose |
| Thickness-generalisation check (Set C, 32–1024 nm) | calibration-transfer residual **≤0.002%** at every thickness — same order as Set B's own residual |
| Ga K/L axis (not chosen), same check | up to **0.18%** — ~100× larger, still negligible vs the error budget |
| Line-definition sensitivity | raw ratios differ **40–90%** between principal/summed (REPORT §17) — verdict unchanged either way |

⚠ **Do not say "x = 0.01" as "one percent bismuth" without qualification.** x is the Bi fraction
of the group-V sublattice, not atomic percent — Walther's own paper: "the Bi content only
amounts to 50x at%." Say "an x of one percent" / "a Bi content of x equals 0.01", not "1%
bismuth" — the atomic-percent equivalent (0.5 at%) is a different, correct number that must not
get silently substituted for x.

---

## Things a slide must not claim

- **That the overlap (i) magnitude is known.** It is swept across a plausible range (0.1/1/10%
  coupling), not measured or derived — state that the verdict is robust to the sweep, not that
  the sweep was unnecessary.
- **A single "the accuracy threshold is X%" without attribution.** Δx = 0.01 is Walther's stated
  bar, cite it as his; don't present it as if self-evidently correct.
- **That Bi M or Bi K are unusable in all circumstances.** They fail at THIS composition/dose
  regime under a stated threshold — precise about scope, not a blanket dismissal.
- **Any claim the detection floor is below x = 0.01.** Only "measurable everywhere sampled";
  where it actually breaks is explicitly unknown (caveat 2 above).
