# P4.3 — the verdict session. Evidence map

*Written 2026-08-17 for a clean cold-start session dedicated to the verdict. Everything cited
here is on disc; nothing needs recomputing. The verdict is Ethan's — Claude's role in that
session is to fetch, re-cut and cross-check evidence on request, never to conclude.*

**Cold start:** read `CLAUDE.md`, then `NEXT_SESSION_PROMPT.md`, then this file.

---

## The four decisions, in order

Settle them in this order — 1 feeds everything downstream.

### 1. The accuracy threshold — DECIDED 2026-08-21: absolute Δx = 0.01

**Resolved.** Adopted Walther's own stated bar — *"measuring it precisely to 0.5 at% (for
Δx = 0.01) or better is a real challenge"* (J. Microsc. 2025, p.2) — in preference to an
unanchored relative percentage. Reasoning: a flat relative target tightens the absolute demand
as x shrinks, biting hardest exactly in the low-x arm (Set C) this project adds; Walther's own
number is citable and behaves the opposite way (lenient at low x, strict at high x).

Implemented as `budget.DEFAULT_TARGET_ABSOLUTE = 0.01`; `measurability_limit()` gained a
`target_absolute` parameter (crosses `total_error`, composition units, instead of
`relative_total`) — additive, not a rewrite; the old relative path is bit-identical when
`target_absolute=None`. `write_budget()` now writes the absolute-threshold ranking as the
production `measurability_limit.csv` / `route_ranking.csv`, and keeps the relative-10% version
alongside as `measurability_limit_relative10.csv` / `route_ranking_relative10.csv` — evidence
that the top route is anchor-invariant, stored rather than re-derived on request. 301 tests
green; `Aggregated\` re-hashed before/after, only the budget outputs changed.

**The top route is unchanged by the threshold choice**: Bi_As L/K (summed) leads under both.
Under Δx=0.01 the top Bi L routes (both definitions) reach 27/27 scenarios measurable, against
18–24/27 at 10% relative — the pass/fail gap between routes narrows, but the ranking order does
not change.

### 2. Line definition: `principal` or `summed` — DECIDED 2026-08-21: principal primary

**Resolved.** `principal` reported as the primary, defensible number; `summed` retained and
stated explicitly as the robustness check (same top route, same order-of-magnitude margin over
Bi M/K, under both definitions — already true under both thresholds).

Reasoning, in decision-record form:
- **Uncertainty completeness.** `principal`'s overlap term is the true, fully-modelled cost (Bi
  Lα vs As Kα is exactly what `overlap.py` models). Every `summed` row carries
  `overlap_is_lower_bound=True` — summing pulls in As Kβ, which the code itself flags as touched
  by Ga Kβ, a second contamination channel this project never costed. `summed`'s
  slightly-better numbers are at least partly an artefact of an uncosted overlap, not a proven
  advantage.
- **Trace-level convention.** At x≈0.01, close to the detection limit, the defensible posture is
  the conservative one — the number whose error bar is honestly complete, not the one that looks
  best on paper.
- **Reproducibility.** `principal` uses one well-defined atomic transition per element;
  `summed`'s branching-ratio mix is instrument- and integration-window-dependent, a real cost
  for another lab reproducing the method.
- **Where `summed` still earns its keep**: its dominant failure mode is counting (which more
  photons genuinely fixes), while `principal`'s is overlap (which more photons does not fix) —
  so `summed` is not wrong, just carrying an unquantified risk alongside a real benefit. Kept as
  the stated secondary check, not discarded.

Background: the two definitions differ 40–90% in raw ratios (REPORT §17) — driven by how much
of each shell's intensity sits in secondary sub-lines (branching ratios), which varies by
element and shell rather than being one fixed number. Must be stated prominently in Methodology
regardless (`writeupTODO.md` §3). No code change required — both definitions were already
computed and stored side by side since Stage 6 (REPORT §17.2); `fig03_measurability.py` already
uses `DEFINITION = "principal"`, so the figure was already consistent with this decision.

### 3. Primary sum-peak settings for the prose — DECIDED 2026-08-21: intensity + M_BAND_FACTOR_MEASURED

**Resolved.** `basis=intensity` (unchanged, already the code default and already Walther's own
phrasing), `m_band_factor=M_BAND_FACTOR_MEASURED` (1.743, **changed** from the code default of
1.0). `parents=alpha_only`, `conserve=True` kept as-is — negligible influence, already
Walther-aligned. Wired explicitly into `run_analysis.py`'s `sumpeak` and `budget` stages (not a
changed function default — same "reporting basis belongs in the driver" convention as the
`overlap` stage's `dose_scale`, REPORT §32.2), so `sumpeak_sensitivity.csv` and the
`bias_sumpeak` column in `error_budget.csv` agree on what "the sum peak" means. 301 tests green;
only the sumpeak and budget outputs changed on regeneration.

Reasoning:
- **`basis=intensity`**: ties directly to Walther's own stated correction ("~15% of their line
  intensities") and is traceable/comparable to the source paper — same "match what you're
  comparing against" logic as decision 2. `rate_product` is arguably the more physically
  fundamental description of true coincidence pile-up (quadratic in dose) but is not what
  Walther described.
- **`m_band_factor=1.743`**: the whole unresolved M-band a real Si:Li detector actually reports,
  versus `1.0`, the bare simulated Mα line MC X-Ray outputs. Walther's own measured Bi M values
  are inherently whole-band (his detector cannot resolve M sub-lines either), so 1.743 is the
  more defensible match to what is actually being compared against.

**Anomaly surfaced during regeneration, worth knowing before quoting Bi M numbers:** REPORT
§26.4 describes a larger `m_band_factor` as "softening the apparent damage" — true for the raw
Bi L/M **ratio** shift that `sumpeak.synthesise()` reports directly. It is NOT true once that
artefact is propagated through calibration and inversion into `bias_sumpeak` (composition
units): at 1.743 the composition-space bias got **larger**, not smaller (0.0095 → 0.0166 in x,
same run/scenario), because the inversion's response to the M-band baseline change outweighs the
softened ratio distortion. Consequence: Bi M's measurability collapsed from 12/27 scenarios
passing (at 1.0) to **0/27** (at 1.743) under the Δx=0.01 bar — a stronger disqualification of
Bi M, not a weaker one. Verified this is not a code bug: it is two genuinely different
quantities (ratio distortion vs. propagated composition error) moving in different directions,
and the underlying `sumpeak.py` mechanics tests (which pin the ratio-level "softening" directly)
were unaffected and still pass.

**The winning route is completely unaffected**, as expected: `bias_sumpeak` for Bi_As L/K is ~0
either way (the artefact lands at 2.42 keV, Bi Lα is at 10.84 keV — no path to it). Confirmed
byte-identical in the regenerated `route_ranking.csv` top rows.

⚠ **CSV trap:** in `sumpeak_switch_influence.csv`, the `relative_difference` column stores the
**fractional** difference, so basis reads `1.176`, not `2.18`. REPORT §28.3's "2.2×" is that plus
one. Don't quote the raw column as a multiplier.

#### Sum-peak status box — what is *not* open

Settled, built and tested, so none of this needs revisiting:

- **Modelled, not bounded.** Synthesised analytically in `sumpeak.py` (MC X-Ray cannot build a
  sum peak), written into an as-measured copy of the intensities, and propagated through the
  whole held-out recovery and into the error budget as a bias term. **Contrast overlap (i),
  which is bounded rather than modelled** — the two are often spoken of as a pair and are not.
- **Where it is applied:** the unknown only, never the calibration (Walther settled this;
  enforced by a test — REPORT §26.6).
- **The mechanism:** Ga Lα + As Lα = 2.380 keV against Bi Mα 2.423 — a 43 eV gap, 0.47 FWHM,
  genuinely merged.
- **Fake counts capped at `min(I_Ga, I_As)`** — each event consumes one photon from each parent.
- **Geometric mean in the intensity basis** — this project's Ga Lα / As Lα ranges 0.97–2.02, so
  "15% of their intensities" would be ambiguous here in a way it was not for Walther.

#### Two limitations that never resolve

Keep these separate from the decision above — they are permanent write-up material, not things
awaiting a choice:

1. **The true pile-up level is unknown and unmeasurable here**, which is *why* it is swept
   (0.1/1/10%) rather than fixed. Walther's ~15% was fitted to force his measurement into
   agreement with his simulation, and is entangled with his Bi M value. REPORT §31.2 states the
   consequence: Bi M's usability depends entirely on an instrument property this project cannot
   measure and Walther fitted.
2. **The baseline carries the 1.506 ± 0.020 cross-code discrepancy**, since the artefact is
   specified relative to the Bi M peak. See caveat 1 below.

### 4. The verdict itself (LO4's "most reliable X-ray line pair")

> **⚠ Corrected 2026-08-24. The counts in this section are the 10%-relative figures, labelled as
> though they were the Δx = 0.01 ones.** Nothing below is deleted — the reasoning stands, the
> numbers attached to it do not. Against the production bar (decision 1):
>
> | at x = 0.01 | fails, Δx = 0.01 | fails, 10% relative *(what is quoted below)* |
> |---|---|---|
> | Bi M | **18** of 27 | 27 of 27 |
> | Bi K | **0** of 27 | 27 of 27 |
> | Bi L | 0 of 27 | 9 of 27 |
>
> **Across the full composition range** (the measurability question, and the one that decides the
> verdict): Bi M fails **27 of 27**, Bi K fails **18 of 27**, Bi L fails **none**.
>
> **Bi K's rejection is RANGE, not photon starvation.** It clears Δx = 0.01 at x = 0.01 even at
> the shortest acquisition swept (100 s), then crosses the bar partway up the range — typically
> near x ≈ 0.09, as low as x ≈ 0.011 in the worst corner. The mechanism behind that is still
> counting (fig06 is sound on the physics), but "needs >12× Walther's dose" is not: the
> `dose_needed` / `dose_vs_walther` columns cited below are computed against the file's
> `target_relative` column and **do not transfer to an absolute bar**.
>
> Also stale below: fig03 **was** regenerated, on 2026-08-23 — switched to the absolute metric,
> with its scenario counts now derived at render time rather than typed.
>
> Downstream deliverables already corrected: `PRESENTATION_SCRIPT.md` §C,
> `SLIDES_CONCLUSIONS_BRIEF.md`, `PRESENTATION_CONCLUSIONS_DELIVERY.md` (banner), and the deck.

The data's ranking — endorse it, qualify it, or overrule it with reasons:

- **`Aggregated\route_ranking.csv` + `Figures\fig03_measurability_limit`** (fig03 not yet
  regenerated for decisions 1/3 — Ethan will do this himself). At x = 0.01 against **Δx = 0.01**
  (decision 1): Bi M and Bi K routes (principal) fail **all 27** swept scenarios (sum peak /
  photon starvation respectively); Bi L (principal, decision 2) passes **all 27**, with its own
  dominant mechanism being **overlap (i)** — the As Kα/Bi Lα coupling, not counting statistics.
  Top route: **Bi Lα / As Kα, principal.**
- `Aggregated\error_budget.csv` — per-mechanism decomposition of any single number
  (4,320 rows; filter by route/scenario).
- `Aggregated\counting_uncertainty.csv` — `dose_needed` / `dose_vs_walther` columns: the
  quantitative "curable by counting longer" evidence (Bi L: 0.12× Walther's dose suffices at
  x = 0.01; Bi K: >12×).
- Mechanism figures for the prose: fig04 (sum-peak selectivity), fig05 (recovery clean vs
  as-measured), fig06 (Bi K: absorption-immune, photon-starved).
- Supporting: `roundtrip_summary.csv` + REPORT §25 (held-out beats handed-thickness — the
  self-calibration claim demonstrated); REPORT §23 (why As K/L is the thickness proxy).

## Caveats the verdict must carry (examiner-probe list)

1. **Bi M cross-code discrepancy, 1.506 ± 0.020** (REPORT §21) — cause unidentified; bounds
   any absolute claim resting on Bi M. Largely cancels in same-route calibrate-then-invert.
2. **The overlap coupling is swept, not derived** (REPORT §27) — a full treatment needs four
   uncitable inputs. The bound is honest but it is an assumption ladder, and the two detector
   constants are still `# pending verification vs primary source` (robustness proven across
   their literature ranges, §27.6 — cite Goldstein before submission).
3. **First-order flags** — σ values past 30% relative (`first_order_valid=False`: all Bi K,
   most Ga_As at low x) do not describe symmetric distributions. Quote them as "beyond
   usability", not as precise uncertainties.
4. **The floor below x = 0.01 is unbracketed.** Bi L is measurable at every *sampled*
   composition; where it actually dies is unknown because the budget refuses to extrapolate.
   The original spec's dilution plan (x = 0.002, 0.0002 at 100 nm — see
   `original spec\design decisons.md`) would bracket it: two runs, ~20 min compute, if the
   verdict wants an empirical floor rather than "below the studied range".
5. **The window arm is dead** (windowless impossible in MC X-Ray Lite) — "detector
   configuration" dropped out of the deliverable's dimensions. A declared scope reduction, not
   a limitation to bury (`writeupTODO.md`).
6. **CLOSED 2026-08-21 — Set C never fed into the recovery/error-budget pipeline.** REPORT §23.2
   notes, but the write-up never states, that the held-out recovery (`recover_x_via_kl`) is
   filtered to Set B only, so "measurable to x≈0.01" had only ever been directly demonstrated at
   ONE thickness (100 nm) — Set C existed to test exactly the low-x/high-t regime but was never
   itself pushed through this pipeline. Closed by adding an `unknowns` parameter to
   `recover_x_via_kl` (additive; default reproduces the original Set B path exactly, 304 tests
   green) and running Set C's 6 runs through it. Result, principal definition, Bi Lα/As Kα: the
   calibration-transfer residual stays **~1–2×10⁻⁷ in x (≤0.002% relative) at every one of the
   six thicknesses 32–1024 nm** — the same order of magnitude as Set B's own residual
   (3.7×10⁻⁸), utterly negligible beside the ~0.0034 overlap-dominated uncertainty that actually
   limits this route. The Ga K/L axis (the one NOT chosen) does noticeably worse on the same
   test (up to 0.18% relative at 1024 nm, ~100× larger) but is still negligible next to the
   error budget — confirming, with direct evidence rather than the indirect "As K/L was chosen
   because Set C showed it's thickness-robust" argument, that the recovery genuinely
   generalises across the full thickness range at low x. Persisted as
   `roundtrip_heldout_setc_lowx_as_k_l.csv` / `..._ga_k_l.csv` (`roundtrip.write_roundtrips`).
   **This strengthens the verdict — it does not merely fail to weaken it.**
7. **The verdict sentence the data supports, for reference** (Ethan's to adopt or not; needs a
   different clause after "limited by" now that decision 2 settled `principal` as primary —
   its own dominant mechanism is overlap (i), not counting):
   *Bi Lα referenced to As Kα (principal definition), quantifiable to x ≈ 0.01 at the reference
   dose, limited by the As Kα/Bi Lα overlap (i) rather than by counting statistics or the sum
   peak — the calibration transfer itself is essentially exact at every thickness tested,
   32–1024 nm — while Bi M fails on the sum peak and Bi K on photon starvation at any
   composition.*

## What NOT to redo in that session

Nothing needs rebuilding. 297 tests green as of 2026-08-17; `python run_analysis.py`
regenerates everything (hash `Aggregated\` first — REPORT §32.2). If the threshold changes,
re-run stage `budget` only. Any new cut of the evidence is a read of the stored CSVs, never a
re-simulation.
