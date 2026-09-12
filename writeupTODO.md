# Write-up TODO — notes for the Methodology section

*Working notes, not prose. Each entry is something that **must be declared** in the dissertation
because it is a choice, a deviation, or a limitation a reader could otherwise mistake for an
accident.*

**The test for whether something belongs here:** if an examiner could ask "why did you do it
that way?" and the answer isn't obvious from the code, it goes here.

**Sources:** `REPORT.md` is the chronological evidence record. `DISSERTATION_FRAMEWORK.md` says
*where* each item goes (chapter, section, page budget); this file says *what to say*. They are
complementary — the framework is the plan, this is the content.
Numbers: `DISSERTATION_NUMBERS.md`, never from prose.

---

> ## ⚠ Reconciled 2026-09-10 — read this before using the file
>
> Entries are now marked:
> - **✅ CLOSED** — the decision was made or the work was done. **The entry still has to be
>   *written up*** — closed means "no longer an open question", not "no longer needed in the
>   dissertation". The reasoning under a closed entry is exactly what the write-up needs.
> - **⚠ LIVE** — still an open limitation or an undeclared choice.
>
> **Corrections applied at reconciliation** (each flagged inline where it appears):
> 1. §3 "Bi K … equal counting statistics needs ~10⁴× the dose" was **arithmetically wrong** —
>    it squared a factor that should not be squared. Corrected to **~102×**. See the flag in §3.
> 2. §2 run matrix: Set C did not exist when this was written. The "untested corner" is now
>    tested, not merely acknowledged.
> 3. §3/§4: the 10%-relative target was replaced by **Δx = 0.01 absolute** (decision D1).
> 4. §3 line definition: no longer deferred — **`principal`** (decision D2).
> 5. §4 counting statistics: **are** now modelled (P1.3 landed 17 Aug).
> 6. §4 "every result at 100 nm": **closed** 21 Aug by pushing Set C through the recovery.
> 7. Bi M cross-code factor tightened from "~1.5×" to **1.506 ± 0.020**, three confirmations.
> 8. Header no longer points at `CURRENTLY_RELEVANT.md` (archived 17 Aug).
>
> Nothing was deleted. Every justification argument in the original is preserved.

---

## 1. Sum-peak modelling choices

*The two that came out of Walther's 2026-08-13 reply, and the reason Stage 6b is a modelling
exercise rather than a reproduction.*

**Background that makes them necessary — ⚠ LIVE, and the strongest justification in the
methodology. This paragraph exists nowhere else; do not lose it.**

Walther did not derive his sum-peak magnitude from a pile-up rate. He observed that his measured
Bi L/M ratio (~2:3) disagreed with his simulated one (~1:1), assumed the sum peak caused the gap,
and increased it until the two agreed — arriving at 600 counts, ~15% of the Ga L / As L
intensities. **It is a fitted quantity, inferred from a disagreement, not a measurement of
pile-up.** It is also entangled with *his* simulated Bi M, which this project's simulation
disagrees with by **1.506 ± 0.020** (REPORT §21.1b, three independent confirmations).
**So the 15% is not portable and there is no published method to inherit.**

- **✅ CLOSED (decision D3, 2026-08-21) — STATE the modelling choices explicitly**, as decisions
  with reasoning, not as defaults. Production settings and what each one is:
  - which lines feed the sum peak → **`parents = alpha_only`** (Ga Lα + As Lα only, not Lβ);
  - what the fraction multiplies → **`basis = intensity`** (a fraction of the Ga Lα / As Lα
    intensity, not a true pile-up rate ∝ the product of count rates);
  - whether photons are conserved → **`conserve = True`** (fake Bi Mα counts are also *removed*
    from Ga Lα / As Lα, not merely added).

  Each still needs a sentence of justification in the prose so a reader can judge the choice
  rather than guess at it. Reasoning is in `decisions.md` D3.

- **✅ CLOSED — SWEEP the magnitude rather than fixing it.** Swept at **0.1% / 1% / 10%**,
  explicitly **never 15% as a default**. Report how the conclusion moves across the range.
  *Result to state: the route ranking is stable across all 27 scenarios and all 16 switch
  combinations — so the choice did not change the answer, and that is worth saying.*

- **✅ CLOSED — state where the artefact is applied:** on the **unknown only, never the
  calibration**. This follows Walther's own practice ("only applied to the experimental spectrum,
  not to simulations") and is the variant that does *not* self-cancel, so it is the conservative
  choice.

- **⚠ LIVE — say plainly that the sum peak is MODELLED and overlap (i) is BOUNDED**
  *(added 2026-08-20)*. The two overlaps are named as a pair throughout the project and are **not
  handled alike**: the sum peak is synthesised onto the intensities and propagated through the
  entire recovery; overlap (i) is expressed as an uncertainty with no artefact synthesised,
  because a real treatment needs four physical inputs this project cannot cite. A reader who
  assumes symmetric treatment will misread both. **State the asymmetry and the reason for it**,
  alongside the bias-vs-variance distinction in §4.

- **⚠ LIVE — two sum-peak limitations that never resolve.** Keep these distinct from the
  modelling *choices* above, which are now settled:
  (a) the true pile-up level is unknown and unmeasurable here, which is why it is swept;
  (b) the baseline it is measured against carries the **1.506 ± 0.020** Bi M cross-code
  discrepancy, since the artefact is specified relative to the Bi M peak.
  Consequence worth stating outright (REPORT §31.2): **Bi M's usability depends entirely on an
  instrument property this project cannot measure and Walther fitted.**

- **✅ CLOSED — state whether the M-band correction is applied before the pile-up.** It is:
  production runs at **`m_band_factor = 1.743`**. Both baselines were built as a flag and the
  comparison reported.

  The reasoning to write up: the sum peak lands on what a *detector* sees — the whole unresolved
  M band — but the simulation produces Mα alone. Adding pile-up to simulated Mα directly makes
  the same pile-up look like a larger fractional corruption, because the baseline is 1.743× too
  small, and would **overstate the sum peak's damage**. *The switch is worth **1.7×** on mean
  absolute error (`sumpeak_switch_influence.csv`) — the second most influential of the four.*

  ⚠ *Related, and worth a footnote rather than a claim — still true, still not to be claimed:*
  if the ×1.743 factor is applied to Walther's own comparison, his simulated target moves from
  L/M = 1.0 to 0.574, while his measurement sits at 0.667 — i.e. **less** M than predicted,
  whereas a sum peak adds M. His band factor was supplied as a "new estimate" in Aug 2026
  correspondence and so post-dates the paper's analysis. **Not a claim to make in the
  dissertation without his confirmation**, but it is why this project's sum-peak magnitude is
  swept rather than inherited.

---

## 2. Declared deviations from the Aims & Objectives form

- **⚠ LIVE — trajectory count.** LO4 specifies 10⁶ electron trajectories. Foils ≤ 16 nm were run
  at **10⁷** to reach <1% Monte-Carlo noise (Walther's advice, 2026-07-19 meeting). Deliberate,
  justified, and must be declared as a departure rather than left for a reader to notice.

- **⚠ LIVE — run matrix is a cross plus an extension arm, not a grid.**
  *(Rewritten 2026-09-10: Set C did not exist when this entry was first written.)*
  Set A = 10 runs, 2→1024 nm, all at x = 0.20. Set B = 5 runs, x = 0.01→0.20, all at 100 nm.
  **Set C = 6 runs, x = 0.01, 32→1024 nm, added 2026-08-13.** LO4's wording ("varying thickness …
  and Bi-concentration") admits a grid reading, so **state the cross explicitly and justify it**.

  ⚠ **The old instruction — "acknowledge the untested corner (low x *and* high t) as a
  limitation" — is superseded. That corner was tested.** Set C exists precisely because ρ·t
  proved insufficient as an absorption coordinate and the cross could not predict its own
  interior (REPORT §23). **Get the causality the right way round: Set C *is* the test, not a
  consequence of one.** Earlier prose in this repo states it backwards.

- **⚠ LIVE — the detector-window arm was dropped.** *(Added at reconciliation 2026-09-10; it was
  a declared deviation missing from this file.)* The `.mic` has no window field — the ATW
  (Al 0.02 µm + Moxtek 0.3 µm) is compiled into MC X-Ray Lite and a windowless configuration is
  confirmed impossible. Declare it as a **scope reduction with a cause**, not an omission.

---

## 3. Choices needing justification

- **⚠ LIVE — density model.** ρ(x) = 5.32 + 1.86x, from Walther's endpoints (GaAs 5.32,
  hypothetical zinc-blende GaBi 7.18). This **supersedes the values in his own published paper**
  (5.34 / 5.36), which is a claim needing explanation: both codes, left to auto-mix, interpolate
  *elemental* densities, wrong for a covalent zinc-blende alloy.

- **⚠ LIVE — exposure.** 1 nA × **715.5 s live** (743 s total, 3.7% dead), matching Walther's
  Fig. 2 acquisition. Note his probe current is an **estimate, not a measurement** — so dose is
  swept (×1, ×7.155, ×71.55) with this as a **labelled reference point**, not fixed.

- **✅ CLOSED (decision D2, 2026-08-21) — line definition: `principal`.**
  Every ratio and k\* is stored under *both* `principal` (Kα1 / Lα / Mα) and `summed` (all
  sub-lines); they differ by 40–90%. **`principal` is used for the final inversion; `summed` is
  reported as the stated robustness check.**

  The reasoning to write up (full version in `decisions.md` D2): `principal`'s overlap term is the
  true, fully-modelled cost — Bi Lα vs As Kα is exactly what `overlap.py` models — whereas every
  `summed` row carries `overlap_is_lower_bound = True`, because summing pulls in As Kβ, a second
  contamination channel never costed. `summed`'s slightly better numbers are at least partly an
  artefact of an *uncosted* overlap, not a proven advantage. At x ≈ 0.01 the defensible posture
  is the conservative one: the number whose error bar is honestly complete.

- **⚠ LIVE — Bi K lines included.** LO3 names "bismuth K, L, and M". Bi K is included and shown
  to fail — quantifying the failure answers the objective, whereas omitting it leaves it silently
  unaddressed.

  > 🛑 **ARITHMETIC CORRECTION, 2026-09-10.** This entry previously read: *"unusable anyway
  > because it yields ~103× fewer photons than Bi L (dose-independent), so equal counting
  > statistics needs ~10⁴× the dose."* **The 10⁴ is wrong** — it squares a factor that should not
  > be squared. Since σ_rel ∝ 1/√N and N ∝ dose, 103× fewer photons makes σ **√103 ≈ 10.1×**
  > worse, and restoring it needs **~102× the dose, not ~10⁴×.**
  > Verified against `counting_by_route.csv` (`principal`, x = 0.01): σ(Bi K) = 34.98% vs
  > σ(Bi L) = 3.456% at the reference dose — a ratio of **10.12**, whose square is **102.4**.

  **The result is counter-intuitive and worth the space:** Bi K is the *most* absorption-immune
  route in the matrix and unusable anyway, because it yields **~103× fewer detected photons** than
  Bi L (dose-independent), so matching Bi L's counting statistics needs **~102× the dose**.
  ⚠ There is a **second, independent** cause worth stating alongside it: detector efficiency is
  **0.237** for Bi Kα1 against **0.9998** for Bi Lα — **76% of Bi K's photons are lost in the
  detector alone**, before any question of generation yield.
  ⚠ And note the *framing*: Bi K's headline failure in Ch6.2 is **range**, not photon starvation
  — it clears the Δx = 0.01 bar at x = 0.01 and crosses it further up. The dose numbers explain
  *why the margin is thin*; they are not the reason it fails.

- **⚠ LIVE — numpy/scipy and matplotlib as declared dependencies.** `CLAUDE.md` specifies
  "pandas + stdlib only". **Two declared exceptions**, both to be stated:
  **numpy + scipy** in `absorption.py` (non-linear curve fitting and root finding, 2026-08-16),
  and **matplotlib confined to the separate top-level `figures/` package**, which
  `mcxray_wrapper/` never imports and where no figure computes anything. State the boundary and
  why it holds — the pipeline stays installable and testable with no plotting stack.

- **⚠ LIVE — Figure 1 departs from Walther's presentation in two ways**, both deliberate and both
  printed on the figure: a **log thickness axis** (the runs are a geometric doubling series; on
  his linear axis every point below 100 nm collapses into the origin) and **ρ = 5.692 rather than
  his published 5.36** (his own revised model). Justify both rather than leaving a reader to spot
  them.

- **⚠ LIVE — detector resolution constants.** The resolution model uses ε = 3.86 eV (electron-hole
  pair creation energy in Si) and F = 0.115 (Fano factor). Both are standard textbook values but
  the reference is not in the repo, so both are flagged `# pending verification vs primary
  source`. **Cite them** — Goldstein et al., *Scanning Electron Microscopy and X-Ray
  Microanalysis* — and note that ε is temperature-dependent, so quote the figure for a cooled
  Si(Li) detector.

  **Then add the robustness sentence** *(these numbers are only recorded here and in REPORT
  §27.6 — do not lose them)*: the conclusion holds across the whole literature range — overlap (i)
  stays **resolvable at 1.65–2.07 FWHM**, the sum peak stays **merged at 0.45–0.53 FWHM** — and
  **ε·F would have to be 2.2× its accepted value** to change it. That turns a dependency into a
  stated robustness result, machine-checked by three tests.

- **⚠ LIVE — intensity column.** `Intensity Emitted Detected (photons)` — the measured-count
  quantity — rather than the generated or dose-independent columns. Say why.

- **⚠ LIVE — counting-statistics propagation method** (REPORT §30). Not a two-line formula: each
  line is perturbed one at a time and the *whole* recovery re-run (central difference in
  log-intensity), so the As K/L thickness-proxy path and the shared-line correlation are priced in
  by construction. **State the validation:** three closed-form derivatives (x, x(1−x), 1−x from
  Eqs 2/4/9) reproduced **to six figures**, and the Bi Lα floor cross-checked against the overlap
  module's **independent 1/√N**. Var(ln N) = 1/N is the standard Poisson result.

- **⚠ LIVE (rule) / ✅ CLOSED (the target) — error-budget combination rule** (REPORT §31).
  Variances in quadrature, |bias| added linearly on top — a stated **conservative envelope**, not
  a likeliest error. The method's own clean-recovery residual is carried as a **separate** bias
  term so calibration difficulty is never mislabelled as artefact damage.

  ⚠ **Superseded:** this entry used to end *"the 10% relative target is a stated choice with no
  literature anchor — defend it or replace it."* **It was replaced.** Decision D1 (2026-08-21)
  set the bar at **Δx = 0.01 absolute**, which *is* anchored — it is Walther's own stated
  precision (2025, p.2). The 10%-relative results were kept and stored
  (`*_relative10.csv`) as the robustness check. **Write up why the relative bar was rejected**,
  and note that the route ranking is the same under both.

- **⚠ LIVE — the 27-scenario sweep and the refusal to extrapolate.** Sum-peak level, overlap
  coupling and dose are all unknown, so the recommendation is quoted as a **win-rate across all
  27 combinations, never at one corner**. Measurability limits are interpolated log-log *inside*
  the sampled x-range only; a curve that never crosses reports which side it fell
  (`status = below_range` / `above_range`, vs `bracketed`). Both belong in Methodology as
  **posture**, not buried in captions.

---

## 4. Limitations to declare, not bury

- **⚠ LIVE — Bi Mα disagrees between codes by 1.506 ± 0.020** and the cause is **unidentified**
  (REPORT §21). *(Tightened from "~1.5×" at reconciliation — there are now three independent
  confirmations and the factor is flat over an 8× thickness range, which is what rules out
  absorption as the explanation.)* It cancels in a same-route calibrate-then-invert round trip, so
  recovered *x* is largely immune, but it **bounds any absolute claim resting on Bi M** and
  affects the sum peak, which is specified relative to that peak.

- **✅ CLOSED — counting statistics ARE modelled.** *(This entry previously read "not modelled
  (until P1.3 lands)". P1.3 landed 2026-08-17.)* The simulation reports **expectation values**,
  and the algebra would close on them however few photons underlie the number — so the counts are
  **re-noised** and the uncertainty propagated numerically through the whole recovery.
  **State clearly that the final error budget does include Poisson noise**, and that it is one of
  the three mechanisms combined in §3's envelope.

- **⚠ LIVE — golden files are format ground truth only, never physics.** They carry
  `UserDefinedMassDensity = 0` and a 0.3 cm detector. **Explain the distinction so a reader does
  not read the regression tests as physics validation.**

- **⚠ LIVE — overlap (i), As Kα1 / Bi Lα, 297 eV, is bounded, not modelled** (decided 15 Aug,
  built same day). Declare the model: the cost is **variance** on the fitted Bi Lα area,
  σ = √(N + coupling·N_neighbour), with coupling **swept** (0.1 / 1 / 10%) because deriving it
  needs peak shapes and tailing this project cannot cite. State that the resolution model showing
  the pair *resolvable* (1.74 FWHM) was validated at Mn Kα and against Walther's Lα1/Lα2
  statement, and survives the full literature range of ε and F (REPORT §27.6).

- **⚠ LIVE — the overlap→composition conversion is exact only under `principal`.** Under `summed`
  it is a **lower bound** — the artefact also touches L sub-lines the bound does not model. The
  flag is carried per row (`overlap_is_lower_bound`). Quote the principal-definition result as the
  defensible one (REPORT §31.2). *This is one of the reasons D2 chose `principal` — see §3.*

- **⚠ LIVE — first-order error propagation stops being meaningful past ~30% relative.** Rows
  beyond it are flagged `first_order_valid = False`, **not corrected**. Affects all Bi K and most
  Ga_As rows at low x; say so rather than quoting their σ as if it described a symmetric
  distribution.

- **✅ CLOSED 2026-08-21 — quantification is no longer demonstrated at a single thickness.**

  *The original limitation (recorded 2026-08-20):* the round trip, the counting-statistics
  propagation, the error budget and the measurability limit each contained exactly the five Set B
  runs, **all at 100 nm** — so the whole downstream chain was demonstrated at one thickness.

  *How it was closed, at zero compute cost:* an `unknowns` parameter was added to
  `recover_x_via_kl` (additive; default behaviour unchanged, verified by an explicit equivalence
  test) and **Set C was run through it as unknowns**. The calibration transfers across
  **32–1024 nm** with a residual of **1.17e-07 for the Bi Lα / As Kα route**
  (`roundtrip_heldout_setc_lowx_as_k_l.csv`). ⚠ **Always name the route** — the file-wide mean
  across all routes, including the ones the project rejects, is 1.31e-02.

  ⚠ *Still worth the distinction when writing this up, because it is what makes the result
  legible:* thickness **behaviour** was always well characterised — k\* across ten thicknesses
  (§18), the ρ·t corner analysis (§23), Set C spanning 32–1024 nm. What was **not** demonstrated
  until 21 Aug is that **recovered x** is accurate away from 100 nm. It now is.

  *(For Ch1.5, the project-management chapter: an x = 0.10 thickness arm was weighed for this and
  rejected — 10 runs / ~2 h — because Set C answered the same question for free. The arm's real
  value would have been completing the replication of Walther's Figs 3–5, which is a different
  justification.)*

---

## 5. Results that need framing, not just reporting

- **⚠ LIVE — the replication is verification, not a finding.** Reproducing Walther's published
  k\* constants validates the pipeline; it does **not** answer the research question. Frame it as
  the instrument being calibrated against a known standard, and be explicit that the contribution
  lies in what follows.

  ⚠ *Narrow the claim before writing it.* This entry says "to 1–3%", but the one fully documented
  comparison is **k\*(Bi L, As K) = 2.4161 ± 0.0051 vs his 2.490 ± 0.071 → −3.0%, 1.04σ**
  (REPORT §18.3). State that one precisely — **just *outside* his quoted 1σ, not inside it** —
  or pull the others from REPORT §18.3–18.4 before quoting a range.

- **⚠ LIVE — the central tension.** `Bi Lα ÷ As Kα` is the best-conditioned route on both axes —
  **0.7% thickness drift over 512×**, and composition drift below the Monte-Carlo noise floor
  (spread 0.0062% across x = 0.01–0.20) — **and it is the route sitting on the 297 eV As Kα
  overlap.** No route is both stable and spectrally clean. **That trade-off is this project's own
  result and is not in the paper.**

- **⚠ LIVE — "A" resolved.** Walther confirmed *A* is the **atomic weight**, ρ the **atomic
  density** (personal communication, August 2026). Worth a line, since the paper's own gloss
  conflates them. Consequence: every k\* is correct in **absolute** terms, not merely up to a
  cancelling factor — which is what makes the literature comparison legitimate at all.
