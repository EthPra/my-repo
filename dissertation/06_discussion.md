# Ch6 — Discussion

**6 pp · ~1,700 words · drafted Sat 13 AM**

⚠ **Lowest AI leverage of the week — Ethan-led.** Claude assembles the limitations list and the
future-work items; the argument is Ethan's.

---

## 6.1 The verdict (~350 w) — **ETHAN'S FINISHED CONTENT, DO NOT REDRAFT**

⚠ **Lift verbatim from `../PRESENTATION_SCRIPT.md` §C ⓵ (slide 11).** Not paraphrased, not
"tightened", not restructured. §5 rule 6.

The substance, for reference only: **Bi Lα referenced to As Kα, principal line definition,
quantifiable to x ≈ 0.01 at the reference dose.** Robust three ways — under both thresholds,
under both line definitions, and across 32 nm – 1 µm.

## 6.2 Why the alternatives fail (~400 w)

**Sources:** `../PRESENTATION_SCRIPT.md` §C ⚠ box; `../ORIENTATION_MAP.md` §4.

- **Bi M fails on bias.** Sum-peak contamination, **uncurable by counting longer** — a bias does
  not average away. 27/27 across the range.
- **Bi K fails on *range*, not photon starvation.** It *clears* the bar at x = 0.01 and crosses
  it further up — a window whose edge needs the answer in order to locate it. That is a worse
  failure than a straightforwardly noisy line, and worth saying so.
  - ⚠ **The "12× dose" line is retired.** Use: Bi K counting sigma 34.98% vs Bi L 3.46% at the
    reference dose; clears at 100 s at x = 0.01.
  - ⚠ **D-6, resolved 2026-09-10: "crosses near x ≈ 0.1" holds only at the reference dose
    7.155** (`x_limit` 0.0865–0.0933). At dose 1.0 it crosses at **x ≈ 0.0113**; at dose 71.55 it
    never crosses. **Always qualify by dose** — unqualified, the claim is wrong for a third of
    the 27 scenarios.
- Secondary references: Ga_As routes fail on `method`.

## 6.3 The central tension (~350 w)

**Sources:** `../writeupTODO.md` §5; `../PRESENTATION_SCRIPT.md` fig03 Q&A.

- **The best-conditioned route on both axes is the one sitting on overlap (i).**
- No route is both stable and spectrally clean.
- **The artefact the project set out to study does not limit the line it recommends**
  (fig03, right panel). Say this plainly — it is the most interesting thing in the chapter and
  it is not a negative result.

## 6.4 Relation to Walther 2025 (~350 w)

**Sources:** `../WORKPLAN_17AUG.md` §2 critical evaluation; `../writeupTODO.md` §3, §5.

Separate cleanly: **what this work verifies** vs **what it adds.**
- Verifies: the k\* method reproduces (−3.0%, 1.04σ), his Fig. 1 ratios reproduce.
- Adds: **composition-invariance of k\*** (his Fig. 4 does not test x at all); **the corner
  finding** — ρ·t insufficiency and As as the ruler; **the Bi M discrepancy** between codes
  (1.506 ± 0.020, cause unidentified); **sum-peak selectivity**; **the bounded low-x limit**.
- The density model **supersedes the paper's own values, on his advice** — say so, it is not a
  disagreement.

## 6.5 Limitations (~250 w)

**Sources:** `../writeupTODO.md` §4; `../VERDICT_BRIEF.md` caveats 1–5.

Each as a **declared decision with a reason**, never as an apology or an oversight:
- Bi M cross-code factor unexplained.
- **Overlap coupling swept, not derived** — the assumption ladder; two constants to cite.
  Every overlap result is therefore a **lower bound**.
- First-order propagation flags (~30% relative).
- **The floor below x = 0.01 is unbracketed** — the project refuses to extrapolate outside the
  sampled range. Ch7 turns this into a concrete future-work item.
- **The window arm is a declared scope reduction, not an omission** — a windowless configuration
  is impossible in MC X-Ray Lite; the ATW is compiled in.
- The `summed` line definition gives a **lower bound** on the overlap.
- **Golden files are format truth only, never physics.**
- **Secondary fluorescence never confirmed with the vendor.**
