# Presentation — CLOSED 2026-08-24

**The deck is finished and verified.** `GaAsBi_EDXS_Presentation_Final_13_Slides (1).pptx`,
13 slides. Nothing outstanding. What remains below is dissertation-phase only.

## Final verification (2026-08-24, against the deck's own XML and embedded media)

- 13 slides, sequence matches the School's Appendix 3 requirement
- Script alignment: every slide has a beat in `PRESENTATION_SCRIPT.md`, every beat a slide;
  section budgets sum to **15:00**
- All three figures confirmed **current** by viewing the embedded images, not by trusting
  filenames: slide 8 = fig02, slide 9 = fig04 (post-2026-08-24 tick fix), slide 11 = fig03
  (Δx = 0.01 bar, derived counts)
- Every number re-derived from `Aggregated\*.csv`
- Zero stale strings: no `0.002%`, `12.2×`, `photon starvation`, `297 tests`, `~4×`,
  `principal line definition`, or `10% target` anywhere in the deck

## Two counts that look contradictory and are both right

Still the most likely way to introduce an error into the write-up. Keep it straight:

| principal, vs As K | measurable **across the range** | exceeds the bar **at x = 0.01** |
|---|---|---|
| Bi L | 27 / 27 | 0 of 27 |
| Bi K | 9 / 27 *(18 fail)* | 0 of 27 |
| Bi M | 0 / 27 *(27 fail)* | 18 of 27 |

In the deck, slide 10's "Bi K 9 / 27" and slide 12's "Fails 18 of 27" are **complements of each
other**, not a contradiction — 9 + 18 = 27. Both are the across-range column.

## Carried into the dissertation

- `measurability_limit.csv` names its threshold column `target_relative` even in absolute mode,
  where it holds 0.01. The sibling `metric` column disambiguates — read them together.
- `Lit review draft.pdf` p.1: the "predicted" semimetal claim for GaBi wants a second source.
- `Lit review draft.pdf` p.4: **0.12% misfit per %Bi** is Ethan's own interpolation from Tixier
  (3.1% → 0.37%) and Lewis (20% → 2.4%), not a cited constant. Mark it as an inference.
- **Secondary fluorescence** in MC X-Ray — never asked of the vendor. Walther's own sims
  exclude it. Still the one open question from `CLAUDE.md`.
- `PRESENTATION_METHODOLOGY.md` and `..._REFERENCE.md` retain reserve material and the full Q&A
  bank. Both predate the threshold change — **check any number in them against
  `Aggregated\` before reuse.**
