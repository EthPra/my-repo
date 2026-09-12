# Work plan — practical work complete by Mon 17 August 2026

*Ethan's working document. Tick `[x]`, cross out `~~like this~~`, add notes in the Notes
column. Unlike `CURRENTLY_RELEVANT.md` (which I keep current), this file is yours to mark up.*

**Created:** 2026-08-13 16:20 · **Target:** practical work done by end of Mon 17 Aug
**Scope:** simulation and analysis code only. **Write-up time is NOT in this plan** — see §7.

---

## 1. Time budget — read this first

| Day | Realistically available | Notes |
|---|---|---|
| Thu 13 Aug | evening only (~2 h) | today; Set C sweep finishing |
| Fri 14 Aug | ? | |
| Sat 15 Aug | ? | |
| Sun 16 Aug | ? | |
| Mon 17 Aug | deadline day | keep clear as buffer, not as work |

**Remaining build work totals ~15 hours**, excluding overlap (i), which is unscoped. Over four
usable days that is **~4 h/day with no slack**. It fits only if nothing goes wrong.

**RECALIBRATED 2026-08-15.** The build estimates were written for hand-coding and have run
**6-8x long**: P1.2 estimated 3 h took ~25 min; P3.1 estimated 4 h took ~30 min. Two reasons — the
data was already in place, and each new module mirrors an established shape
(`ratios.py` → `kfactors.py` → `kl_index.py` → `sumpeak.py`), so it is largely assembly.

**What does NOT compress:** your review time, the decisions, the verdict, and the write-up. Those
are the same length regardless.

So the remaining build (P4.1 sweep, P1.3, figures) is realistically **2-3 hours, not 8** — the
17 Aug target has slack in it. Earlier note kept for the record: I said "15 runs ≈ 50 min" when
the timestamps show ~2 hours, and called P2.1 "~2 hr housekeeping" when the executor turned out
to be missing entirely.

**Therefore §6 defines a cut line.** Decide it in advance, not at 23:00 on the 16th.

### Walther's availability — changed 2026-08-14

> *"Just complete your simulations and prepare the plots. I am abroad, will have no internet
> 16–23 August and I have my annual work review on 25 August so a meeting will have to be after
> that, i.e. 26–28 August."*

**Three consequences:**

1. **No supervisor input from 16 Aug until ~26 Aug.** Every open modelling decision is now
   definitively yours — there is no longer an option to ask. See §8.
2. **"Prepare the plots" is an explicit instruction and was NOT in this plan.** Plotting sat in
   §4 as deliberately descoped. It is now a first-class deliverable — see the new §3.5.
3. **The hard external date is the meeting (26–28 Aug), not the 17th.** The 17 Aug target is
   self-imposed and leaves ~9 days of buffer. Useful to know if something slips — but the buffer
   is for the write-up and the plots, not for letting the build drift.

---

## 2. Where each Learning Objective actually stands

| LO | Requirement | Practical work | Honest assessment |
|---|---|---|---|
| **LO1** | Material rationale: Bi content, strain, band-gap bowing | **none needed** | **Not started — zero mentions of band-gap or bowing anywhere in the repo.** It is a *Basic* Objective and it is pure literature/analysis, so it needs no code and no simulation. It does not belong in this plan, but it cannot be forgotten: it is the only LO with nothing behind it. |
| **LO2** | Free-standing foil geometry, 200 kV, 25° TOA, no substrate; impact on absorption and escape paths | **done** | Evidence exists (soft-L collapse, K/L ratios rising, per-line detector efficiency) but is scattered as a by-product rather than framed as LO2's answer. **Write-up work, not build work.** |
| **LO3** | Bi **K**, L, M absorption relative to Ga or As | **done 2026-08-13** | Closed by adding Bi K. The answer is better than expected: Bi K is the most absorption-immune route in the matrix and unusable anyway, on counting statistics (103× fewer photons, dose-independent). A measured negative result, not an assertion. |
| **LO4** | Sweep + "determine the most reliable X-ray line pair" | **sweep done; conclusion outstanding** | The sweep exists and Set C extends it. **The conclusion does not.** "Most reliable line pair" is answered by P4.2, which needs P3.1 and P4.1 first. **This is the critical path and the whole point of the project.** |

### Critical evaluation — the three things worth being uncomfortable about

1. **The replication is verification, not contribution.** Reproducing Walther's three constants
   to 1–3% proves the pipeline works. It does not answer the research question. An examiner
   will ask what you found that the paper did not — and today the honest answer is the Bi M
   discrepancy, the composition-invariance result, and (pending) the corner finding. All real,
   all modest. **The contribution is still ahead of you and it starts at P3.1.**

2. **Overlap (i) is unscoped and lands on your best route.** `Bi_As L/K` is the standout on both
   axes *and* sits on the 297 eV As Kα / Bi Lα overlap. If it stays unmodelled, the dissertation
   models one of its two named overlaps. That may be acceptable as a declared limitation — but
   it must be a **decision**, not an omission. **It is also the largest schedule risk in this
   plan.** See §5.

3. **Counting statistics may matter more than the sum peak.** At x = 0.01 the stored Bi Lα is
   ~116 photons (9.3% Poisson) and Bi Mα ~76 (11.4%). Nothing in the pipeline models this.
   It is plausible that noise, not either overlap, sets the low-x measurability limit — which
   would make P1.3 the more decisive result for LO4. Currently scheduled *after* the sum peak.
   **Reconsider that order if the corner result shows low-x intensities are marginal.**

---

## 3. Day-by-day plan

### Thu 13 Aug — evening (in flight)

| ✓ | Task | Est | Notes |
|---|---|---|---|
| [x] | Set C sweep finishes (6 runs, x = 0.01, 32→1024 nm) | done | 25.4 min, all 6 clean |
| [x] | Re-aggregate on `full_matrix()` (21 runs) | done | 441 rows; k\*/roundtrip files verified **byte-identical** |
| [x] | **Corner analysis** — does Set A predict Set C on a ρ·t axis? | done | **No.** −22.8% at 1024 nm. Ga K/L composition-sensitive, As K/L not. REPORT §23 |
| [x] | Send the Walther email + meeting request | done | sent 13 Aug eve; replied 14 Aug |

### Fri 14 Aug — REPLANNED: plots first (Walther's instruction)

| ✓ | Task | Est | Notes |
|---|---|---|---|
| [x] | `corner.py` + 10 tests — persist the ρ·t analysis | done | REPORT §23's numbers were computed in a throwaway shell command; now stored and machine-checked |
| [x] | `figures/` package + shared style | done | matplotlib confined to the presentation layer; `mcxray_wrapper/` unchanged |
| [x] | Fig. 1 + Fig. 2 rendered, inspected, corrected | done | both needed a second pass after looking at them |

### Sat 15 Aug — done

| ✓ | Task | Est | Notes |
|---|---|---|---|
| [x] | **P1.2 — round trip held out in *x* AND *t*** | done | `recover_x_via_kl()`, As K/L axis. Interpolation error **measured** on a held-out point (0.17% mean) rather than guessed. **Held-out beats handed-thickness** (0.00342 vs 0.00377) — Walther's self-calibration claim demonstrated. **As K/L beats Ga K/L by 47%**, independently confirming Set C. REPORT §25 |
| [x] | **P3.1 — sum-peak synthesis** | done | `sumpeak.py`, 17 tests. All four open choices built as **switches**, so the decisions are configuration not code. REPORT §26 |
| [x] | **Propagate the artefact** (the second half of P3.1) | done | `apply_to_intensities()` + `as_measured_unknowns()`. Rewrites the intensities, so ratios / k\* / the thickness proxy / the recovery all run on as-measured data. **This is most of P4.1.** REPORT §26.6 |
| [x] | **Overlap (i) — DECIDED: bound it.** Built. | done | `overlap.py`, 16 tests. Ethan's call, 15 Aug. Not modelled — a full treatment needs four uncitable physics inputs. REPORT §27 |
| [ ] | Decide: which sum-peak settings the write-up reports as primary | — | No longer blocks the build — all 16 combinations run |

**Headline 1 — the sum peak is composition-selective.** At a 1% level the fake counts are **97% of
Bi M at x = 0.01** but **4% at x = 0.20**. Recovered *x* from a Bi M route nearly **doubles** at
x = 0.01 (0.0099 → 0.0193). The same artefact does ~23× more damage at the low end, which makes
the sensitivity sweep the substance of LO4's answer rather than a robustness check on it.

**Headline 2 — an error the numbers caught.** The first propagation run corrupted the
**calibration** as well as the unknown, and recovered *x* at x = 0.20 then showed no shift at all
— the two sides cancelled. That is the variant Walther's answer rules out. Now enforced in code
with a test. **The cancellation is itself worth reporting:** it shows how much of the sum peak's
apparent harmlessness in a self-consistent workflow is an artefact of corrupting both sides.

**Headline 3 — the central tension, sharpest form yet.** `Bi_As L/K` is the most robust route in
the matrix: no Bi M so no direct hit, and flat k\* so the thickness-proxy error cannot reach it.
It is also the route sitting on the **297 eV As Kα / Bi Lα overlap** — the one still unmodelled.
**Every route is compromised by one of the two overlaps the project set out to study.** The Bi M
routes fall to the sum peak; the clean, stable route falls to the peak overlap.

### Sun 16 Aug — the payoff (completed 17 Aug)

| ✓ | Task | Est | Notes |
|---|---|---|---|
| [x] | **P4.1 — sweep and persist the as-measured round trip** | done 17 Aug | `sensitivity.py`, 10 tests. **Route ranking survives all 16 switch combinations** — Bi M ~100× worse than Bi L in every one. Which switches matter, measured: basis (2.2×) and M-band baseline (1.7×); parents and conservation barely. REPORT §28 |
| [x] | **P1.3 — counting statistics** | done 17 Aug | `counting.py`, 20 tests. Numerical propagation through the *whole* recovery, validated against three closed-form derivatives (6 figures) and cross-checked vs `overlap.py`'s floor. **The 13 Aug inversion confirmed:** noise 3.5% vs sum peak ~97% at x = 0.01. Bi K needs >12× Walther's dose; Ga_As fails by algebra (sensitivity → 1 as x → 0). REPORT §30 |
| [x] | **Figures for the new results** | done 17 Aug | figs 3–6: measurability limit (LO4 headline, 27-scenario band), sum-peak selectivity, recovery clean-vs-as-measured, Bi K absorption-vs-photons. `make_all.py` builds all six. REPORT §32.3 |

### Mon 17 Aug — conclusion and buffer

| ✓ | Task | Est | Notes |
|---|---|---|---|
| [x] | **P4.2 — measurability limit / error budget** | done 17 Aug | `budget.py`, 20 tests. All three mechanisms in one currency, 27 scenarios swept, no extrapolated limits. **At x = 0.01 / 10% target: Bi M, Bi K and Ga_As fail all 27; Bi L fails only the 9 dose-or-worst-coupling corners** — its failures are curable by counting longer, theirs are not. Ranking: **Bi Lα / As Kα**. REPORT §31 |
| [ ] | **P4.3 — the verdict** | yours | Not automatable. Needs thinking time, not compute time — protect it. The `route_ranking.csv` + fig 3 are the evidence in front of you. |
| [x] | Final: full test suite, regenerate all `Aggregated\` outputs, update REPORT | done 17 Aug | **297 green.** `run_analysis.py` rebuilds all 23 outputs in one command; its first run caught a silent dose regression in `overlap_i_bound.csv` (restored byte-identical — REPORT §32.2). Both REPORTs current through §32. `CURRENTLY_RELEVANT.md` retired (archived 17 Aug, Ethan's decision — this file holds the status role now). |

---

## 3.5 Plots — Walther asked for these explicitly

*Added 2026-08-14. Previously descoped; now a named deliverable for the 26–28 Aug meeting.*

| ✓ | Plot | Status |
|---|---|---|
| [x] | **Three diagnostic ratios vs thickness** (his Fig. 1) | **DONE 14 Aug** — `Figures\fig01_ratios_vs_thickness.png/.pdf`. 11 points (Set B's 100 nm run shares Set A's conditions). Log axis + ρ = 5.692, both deviations stated on the figure. |
| [x] | k\* vs thickness, all routes | in the published artifact |
| [x] | k\* vs K/L ratio (his Figs 3 bottom, 4, 5) | in the published artifact |
| [x] | **Set C: ρ·t insufficiency** — Set A vs Set C on a ρ·t axis, and the Ga K/L vs As K/L split | **DONE 14 Aug** — `Figures\fig02_rho_t_insufficiency.png/.pdf`. Two shared-axis panels; residuals read from `corner.py`, not hard-coded. |
| [x] | **Bi K** — why it fails on counting statistics, not absorption | **DONE 17 Aug** — `fig06_bi_k_absorption_vs_photons`. Escape fraction beside absolute photons: immune and starved on one page. |
| [x] | **Sum-peak sensitivity vs x** | **DONE 17 Aug** — `fig04_sumpeak_selectivity`. (`sumpeak_sensitivity.csv` turned out never to have been generated — it exists now; REPORT §32.1.) |
| [x] | Recovered *x* vs true *x*, simulated vs as-measured | **DONE 17 Aug** — `fig05_recovery_as_measured`. Bi M bends off the diagonal; Bi L's three levels coincide exactly. |
| [x] | Measurability limit (after P4.2) | **DONE 17 Aug** — `fig03_measurability_limit`, **the headline plot**. 27-scenario band, 10% target line, budget decomposition alongside. |

**Where they go:** the existing artifact already carries the k\* plots and regenerates to a
standalone HTML file in the repo. Extending it is cheaper than starting a new deliverable, and
gives one link to send him. Budget ~2 h once the results exist.

---

## 4. Not scheduled — deliberately

| Task | Why it is out |
|---|---|
| ~~**PX.1 — plot Fig. 1**~~ | **Promoted to §3.5** — Walther asked for plots explicitly. No longer optional. |
| **PX.2 — digitise Walther's Figs 3–5** (2 h) | Would turn the Bi M offset from eyeballed into measured per route. **Superseded**: his stated L/M ≈ 1:1 already gives 1.51× from a number he wrote down. Nice-to-have only. |
| **PX.3 — obsolete `_wal_`/`_tix_` runs** | ~570 files in a flat directory. Housekeeping, zero scientific effect. |
| **x = 0.10 full sweep** (10 runs, ~1.9 h compute) | Would complete the replication of Figs 3–5 (both alloy curves). Serves the replication story, not the research question. Out unless the corner result demands it. |

---

## 5. ~~THE SCHEDULE RISK~~ — overlap (i): RESOLVED 15 Aug

**Decision: bound it.** Built same day, ~1 hour, no invented physics.

### What the resolution numbers changed

The two overlaps had been treated as a matched pair since the project began. They are not:

| | Separation | vs detector FWHM | |
|---|---|---|---|
| Sum peak | 43 eV | **0.47 FWHM** | merged — additive contamination is correct |
| Overlap (i) | 297 eV | **1.74 FWHM** | **resolvable** — two peaks, a valley between |

**This ruled out the obvious model.** Treating overlap (i) as "a fraction of As Kα is misassigned
to Bi Lα" assumes a blindness the detector does not have, and would have overstated the damage
to the very route the project is recommending.

The resolution model is validated rather than fitted: it returns **130 eV at Mn Kα** (the Si(Li)
specification) and independently reproduces **Walther's statement that Bi Lα1/Lα2 are
indistinguishable**. Both are asserted as tests.

### The bound, and the result

Cost expressed as fitted-area uncertainty, σ = sqrt(N_BiLα + coupling × N_neighbour), with
coupling **swept** on the same 0.1/1/10% ladder as the sum peak so the two are directly
comparable. Counting statistics reported separately, so "overlap cost" is distinguishable from
"too few photons".

| x | counting floor | 0.1% | 1% | 10% |
|---|---|---|---|---|
| 0.01 | 3.47% | 3.69% | 5.27% | **12.99%** |
| 0.20 | 0.81% | 0.82% | 0.84% | 1.01% |

**The recommendation survives.** Worst-case overlap cost is ~13% at x = 0.01, against the sum
peak's **~100% error** on Bi M routes. Bi Lα / As Kα remains better by roughly an order of
magnitude — and now because its weakness was quantified, not ignored.

**Two points for the write-up:** the sum peak is a *bias* (systematic, unremovable by averaging);
overlap (i) is *variance* (noisier but unbiased, improves with counts). And below ~1% coupling
the overlap adds barely anything over the photon-count floor.

### Why this mattered beyond tidiness

The sum peak damages Bi **M** routes; overlap (i) would damage Bi **L** routes. With only the
first modelled, "Bi Lα / As Kα is the most robust route" was partly an artefact of which overlap
had been studied. Both are now on the table with stated, swept assumptions, so the ranking is a
finding rather than a by-product.

---

## 6. Cut line — if you are behind on Sun 16 Aug

Drop in this order. Do not improvise the order at the time.

1. **P1.3 (counting statistics)** — unless the corner result shows low-x intensities are
   marginal, in which case cut P3.2 instead and keep this.
2. ~~**Overlap (i)**~~ — done 15 Aug, and it cost about an hour rather than the 4+ feared.
3. **P1.2 (K/L round trip)** — painful, because it leaves the acknowledged weakness in the
   headline result. Cut only as a last resort, and declare it explicitly in the write-up.

**Never cut:** P3.1 → P4.1 → P4.2. That chain *is* the dissertation's answer. Without it the
project is a replication exercise with no conclusion.

---

## 7. What this plan does NOT cover

- **The write-up.** `writeupTODO.md` lists what must be declared in Methodology. That is
  separate work and is not costed here.
- **LO1 entirely** — band-gap bowing, strain, optoelectronic rationale. Zero code, but a Basic
  Objective with nothing behind it. **Book time for it separately.**
- **LO2's framing.** The evidence exists; presenting it as LO2's answer is write-up work.
- **Walther's meeting.** If it lands before the 17th it could change P3.1/P3.2. If after, you
  proceed on your own stated choices — which is legitimate, since those are yours to make.

---

## 8. Decisions needed from Ethan (with dates)

**All of these are now yours alone** — Walther is offline 16–23 Aug and unavailable until 26–28.
Whatever you choose, state it and justify it in the write-up; a defended choice is worth more
than a deferred one.

| By | Decision |
|---|---|
| Fri 14 | P1.2 interpolation: linear between nearest K/L neighbours, or a fit? *(the **axis** question is now settled by Set C — use As K/L)* |
| ~~Fri 14~~ | ~~**Overlap (i)**~~ — **decided 15 Aug: bound it.** Built. |
| Sat 15 | Sum peak: which lines, what the fraction multiplies, photon conservation |
| Sat 15 | M-band baseline: simulated Mα or ×1.743 band-corrected |
| Sun 16 | Line definition for the final inversion: `principal` or `summed` (deferred since 2026-07-25 — it cannot stay deferred through P4.2) |

---

## 9. Ethan's notes

*(free space — add as you go)*

-
-
-
