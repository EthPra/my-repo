# decisions.md — P4.3 verdict session decision record

*A chronological log of the four verdict decisions (`VERDICT_BRIEF.md`), kept separate from that
file so the reasoning and code changes behind each choice are quick to find without re-reading
the full evidence map. `VERDICT_BRIEF.md` still carries the fuller evidence citations; this file
is the shorter reference — what was decided, when, why, and what changed as a result.*

---

## Decision 1 — accuracy threshold

**Decided 2026-08-21: absolute Δx = 0.01**, replacing the unanchored 10%-relative default.

**Why.** 10% relative had no literature anchor. Walther's own paper states a precision bar
directly: *"measuring it precisely to 0.5 at% (for Δx = 0.01) or better is a real challenge"*
(J. Microsc. 2025, p.2). A flat relative target also tightens the *absolute* demand as x shrinks
— it bites hardest exactly in the low-x arm (Set C) this project adds, a regime Walther's own
paper never tested. His number does the opposite: lenient at low x, strict at high x.

**What changed in code:**
- `mcxray_wrapper/budget.py` — added `DEFAULT_TARGET_ABSOLUTE = 0.01`; `measurability_limit()`
  gained a `target_absolute` parameter (crosses `total_error`, composition units, instead of
  `relative_total`) — additive, the relative-only path is bit-identical when `target_absolute`
  is not passed.
- `write_budget()` now writes the absolute-threshold ranking as the production
  `measurability_limit.csv` / `route_ranking.csv`. The relative-10% version is kept alongside as
  `measurability_limit_relative10.csv` / `route_ranking_relative10.csv` — evidence, not deleted.
- `tests/test_budget.py` — 3 new tests for the absolute path, 2 replacing the old 3-file output
  contract test.

**Result:** the top route is unchanged by the threshold choice — Bi_As L/K (summed) leads under
both. Under Δx=0.01 the top Bi L routes reach 27/27 scenarios measurable (vs. 18–24/27 at 10%
relative); the pass/fail *gap* between routes narrows, the ranking *order* does not.

---

## Decision 2 — line definition

**Decided 2026-08-21: `principal` primary, `summed` reported as the stated robustness check.**

**Why** (materials-science framing — completeness of the claim over apparent precision):
- **Uncertainty completeness.** `principal`'s overlap term is the true, fully-modelled cost (Bi
  Lα vs As Kα is exactly what `overlap.py` models). Every `summed` row carries
  `overlap_is_lower_bound=True` — summing pulls in As Kβ, which the code itself flags as touched
  by Ga Kβ, a second contamination channel never costed. `summed`'s slightly-better numbers are
  at least partly an artefact of an uncosted overlap, not a proven advantage.
- **Trace-level convention.** At x≈0.01, near the detection limit, the defensible posture is the
  conservative one — the number whose error bar is honestly complete.
- **Reproducibility.** `principal` uses one well-defined atomic transition per element;
  `summed`'s branching-ratio mix is instrument- and integration-window-dependent.
- **Where `summed` still earns its keep:** its dominant failure mode is counting (which more
  photons genuinely fixes); `principal`'s is overlap (which does not). Kept as the stated
  secondary check, not discarded — same top route, same order-of-magnitude margin over Bi M/K,
  under both definitions and both thresholds.

**Background.** The two definitions differ 40–90% in raw ratios (REPORT §17) — not one fixed
number, because it depends on how much of each shell's intensity sits in secondary sub-lines
(branching ratios), which varies by element and shell. Worked example: Bi's L shell gains 87%
extra intensity when summed, but Bi's M shell (only one reported line, Mα) gains 0% — so a Bi
L/M ratio's full 87% inflation lands on one side only, near the top of the 40–90% range.

**What changed in code:** none needed. Both definitions were already computed and stored side by
side since Stage 6 (REPORT §17.2, "store both, defer the choice for inversion to Stage 7").
`fig03_measurability.py` already used `DEFINITION = "principal"`, so the headline figure was
already consistent with this decision before it was formally made.

---

## Decision 3 — primary sum-peak settings for the prose

**Decided 2026-08-21: `basis=intensity` (unchanged), `m_band_factor=M_BAND_FACTOR_MEASURED`
(1.743, changed from the code default of 1.0).** `parents=alpha_only`, `conserve=True` kept —
negligible influence (1.19×, 1.005× on mean abs error, vs. 2.18× for basis and 1.66× for
m_band_factor — `sumpeak_switch_influence.csv`).

**Why:**
- **`basis=intensity`** ties directly to Walther's own stated correction ("~15% of their line
  intensities") — traceable to the source paper, same logic as decision 2.
- **`m_band_factor=1.743`** represents the whole unresolved M-band a real Si:Li detector actually
  reports, versus `1.0`, the bare simulated Mα line MC X-Ray outputs. Walther's own measured Bi M
  values are inherently whole-band too (his detector can't resolve M sub-lines either), so 1.743
  is the more defensible match to what is actually being compared against.

**What changed in code:** `run_analysis.py`'s `sumpeak` and `budget` stages now pass
`m_band_factor=sumpeak.M_BAND_FACTOR_MEASURED` explicitly (not a changed function default — same
"reporting basis belongs in the driver" convention already used for the `overlap` stage's
`dose_scale`, REPORT §32.2, after that exact failure mode bit once). Regenerated
`sumpeak_sensitivity.csv`, `error_budget.csv`, `measurability_limit.csv`,
`measurability_limit_relative10.csv`, `route_ranking.csv`, `route_ranking_relative10.csv` — only
those six files changed (hash-verified), 301 tests still green.

**Anomaly surfaced while regenerating — worth knowing before quoting Bi M numbers.** REPORT
§26.4 describes a larger `m_band_factor` as "softening the apparent damage" — true for the raw
Bi L/M **ratio** shift `sumpeak.synthesise()` reports directly. It is **not** true once that
artefact is propagated through calibration and inversion into `bias_sumpeak` (composition
units): at 1.743 the composition-space bias got *larger*, not smaller (0.0095 → 0.0166 in x,
same run/scenario) — the inversion's response to the raised M-band baseline outweighs the
softened ratio distortion. Consequence: **Bi M's measurability collapsed from 12/27 scenarios
passing (at 1.0) to 0/27 (at 1.743)** under the Δx=0.01 bar — a *stronger* disqualification of Bi
M, not weaker. Checked this is not a bug: two genuinely different quantities (ratio distortion
vs. propagated composition error) moving in different directions; the ratio-level "softening" is
still pinned and passing in `sumpeak.py`'s own tests, untouched by this change.

**The winning route is completely unaffected**, as expected: `bias_sumpeak` for Bi_As L/K is ~0
either way (the artefact lands at 2.42 keV, Bi Lα is at 10.84 keV — no path to it). Verified
byte-identical in `route_ranking.csv`'s top rows before and after this regeneration.

---

## Evidence-closing work — Set C never fed into the recovery pipeline

Not a decision (nothing to choose — this closes a gap, it doesn't weigh options), but done in
this session and worth its own entry: while cross-checking evidence for decision 4, confirmed
that the held-out recovery (`roundtrip.recover_x_via_kl`) only ever ran on Set B (x swept, fixed
100nm) — Set C (x=0.01, thickness swept 32–1024nm) was structurally excluded (REPORT §23.2), so
"measurable to x≈0.01" had only been directly demonstrated at one thickness, even though Set C
was built specifically to test the low-x/high-t regime.

**Closed 2026-08-21.** Added an `unknowns` parameter to `recover_x_via_kl` (additive — default
behaviour unchanged, verified by an explicit equivalence test) and ran Set C through it. Result:
for the winning route (Bi_As L/K, principal), the calibration-transfer residual stays
**~1–2×10⁻⁷ in x at every one of the six thicknesses** — same tiny order of magnitude as Set B's
own residual, negligible beside the ~0.0034 overlap-dominated uncertainty that actually limits
the route. Persisted as `roundtrip_heldout_setc_lowx_as_k_l.csv` /
`roundtrip_heldout_setc_lowx_ga_k_l.csv`. 304 tests green; only these two new files appeared on
regeneration, everything else byte-identical. **This is a genuine strengthening of the verdict**
— direct evidence in place of an indirect argument — recorded as caveat 6 (now closed) in
`VERDICT_BRIEF.md` §4.

---

## Still open — Decision 4: the verdict itself

Not yet decided. `VERDICT_BRIEF.md` §4 has the full evidence map (`route_ranking.csv`,
`error_budget.csv`, `counting_uncertainty.csv`, figures 4–6, REPORT §25/§23) and a candidate
verdict sentence for Ethan to adopt, edit, or reject, plus the six-item caveat list an examiner
would probe. This is the one decision `VERDICT_BRIEF.md` is explicit Claude's role stops short
of — evidence only, never the conclusion.
