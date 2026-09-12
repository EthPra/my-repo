# Results number sheet — every value Ch5–Ch6 will quote

*Built 2026-09-10 (Day 0 of the five-day plan, `DISSERTATION_FRAMEWORK.md` §8). Every value below
was re-read from `C:\MCXRAY\Sim\Aggregated\*.csv` on that date under **production settings** —
`definition = principal`, threshold **Δx = 0.01 absolute**, `m_band_factor = 1.743` — unless the
row says otherwise. Each row carries **file → column → filter** so the Saturday check is a lookup,
not a re-derivation.*

**How to use this file.** When a number goes into a chapter, copy the value *and* its provenance
string into an inline comment in the draft (§8 rule 4). On Saturday, Ethan checks the draft against
this sheet, and spot-checks this sheet against the CSVs. This sheet is not authoritative — **the
CSVs are.** This is a cache with its provenance attached.

---

## 0. Discrepancies found while building this sheet

These are places where `DISSERTATION_FRAMEWORK.md` §3 quoted a number that the CSVs do not
reproduce **under the filter the framework implied**. In every case the framework's number was
*findable*, but only under a different filter than production settings.

**✅ ALL RESOLVED 2026-09-10 (Ethan). Two rulings:**

1. **Quote `principal` throughout.** It is the production definition (decision D2) — `summed`
   blends the shell's sub-lines together, so the individual line the overlap actually acts on can
   no longer be distinguished, and every `summed` row is flagged `overlap_is_lower_bound = True`.
   → closes D-1, D-2, D-3, D-6.
2. **Ch5.2 uses the `matched_rho_t` block throughout**, both figures and the growth factor. It is
   the block that measures the claim actually being made — *the Set A ρ·t curve cannot predict its
   own interior.* → closes D-4/D-5. **Ga K/L −22.79%, As K/L −1.60% at 1024 nm, growth 18.3×.**
   Do not quote 17.5× or −26.29% (those are `matched_thickness`).

Both rulings are propagated into `DISSERTATION_FRAMEWORK.md` and the `dissertation/` skeletons.

| # | Framework said | Correct under `principal` | Status |
|---|---|---|---|
| D-1 | Ch5.4: "held-out beats handed-thickness (**0.00342 vs 0.00377**)" | **0.003626 vs 0.003915** (held-out wins by 7.4%) | ✅ fixed — the old pair was the mean over **both** line definitions |
| D-2 | Ch5.4: "As K/L beats Ga K/L by **47%**" | **56%** (0.005673 / 0.003626) | ✅ fixed — 47% was the both-definitions figure |
| D-3 | Ch5.4: "calibration-transfer residual **~10⁻⁷** across 32–1024 nm" | 1.17e-07 **for route Bi_As L/K only**; file-wide mean is 1.31e-02 | ✅ fixed — must always name the route |
| D-6 | Ch6.2: "Bi K … **crosses near x ≈ 0.1**" | true **at the reference dose 7.155** (`x_limit` 0.0865–0.0933); at dose 1.0 it crosses at **x ≈ 0.0113** | ✅ fixed — dose qualifier added |
| D-4/D-5 | Ch5.2 mixed two blocks of `corner_rho_t_setA_vs_setC.csv` in one sentence: "**−22.8%** / **−1.6%**" is `matched_rho_t`, but "**17×** growth" is `matched_thickness` | **`matched_rho_t` throughout: −22.79% / −1.60% at 1024 nm, growth 18.3×** | ✅ fixed — `matched_thickness` (−26.29% / −6.96%, 17.5×) is not quoted in Ch5.2 |

---

## 1. The two counts that look contradictory (§5 rule 2) — LOAD-BEARING

Both are correct. **Label which one, every single time.** Verified 2026-09-10 from two independent
files that agree.

| Route (vs As K, `principal`) | Measurable **across the whole sampled range** x = 0.01–0.20 | Error **exceeds Δx = 0.01 at x = 0.01 specifically** |
|---|---|---|
| **Bi L / As K** | **27 / 27** scenarios | **0 of 27** |
| Bi K / As K | **9 / 27** *(18 fail)* | **0 of 27** |
| Bi M / As K | **0 / 27** *(27 fail)* | **18 of 27** |

- Left column → `route_ranking.csv`, col `scenarios_measurable_at_low_x`, filter
  `definition=principal`, rows `route=Bi_As`, `light_shell=K`, `heavy_shell` ∈ {L,K,M}.
- Right column → `error_budget.csv`, count of `total_error > 0.01`, filter
  `definition=principal, true_x_bi=0.01`, same route rows. n = 27 per route.
- **Semantics, verified by direct recomputation:** "measurable across the range" means the
  scenario's error stays ≤ Δx = 0.01 at *every* sampled x. It is equivalent to
  `measurability_limit.csv` `status = below_range`. `bracketed` = crosses inside the range
  (and `x_limit` is where); `above_range` = fails everywhere.
- 9 + 18 = 27 for Bi K: the deck's slide 10 and slide 12 figures are **complements**, not a
  contradiction (`PENDING_EDITS.md`).
- ⚠ `measurability_limit.csv` names its threshold column `target_relative` even in absolute mode,
  where it holds **0.01 as an absolute Δx**. Read it together with the `metric` column
  (`metric = absolute` for all 864 production rows).
- ⚠ `route_ranking.csv` col `worst_x_limit` is the **largest** x_limit across scenarios (i.e. the
  most restrictive), not the smallest. Bi_As K/K = 0.0933.

---

## 2. Ch5.7 — Error budget and measurability limit (LO4, the headline; **fig03**)

`error_budget.csv`, `definition=principal`, `light_shell=K`, `route=Bi_As`. 4320 rows total;
27 scenarios = 3 levels × 3 couplings × 3 doses, evaluated at 5 values of x.

**Total error (absolute Δx) by route and x — min/max across the 27 scenarios:**

| Route | x=0.01 | x=0.02 | x=0.05 | x=0.10 | x=0.20 |
|---|---|---|---|---|---|
| **Bi L / As K** min–max | 0.000116–0.003446 | 0.000159–0.003532 | 0.000246–0.003777 | 0.000343–0.004146 | 0.000470–0.004754 |
| Bi K / As K min–max | 0.001108–0.009397 | 0.001556–0.013218 | 0.002405–0.020494 | 0.003264–0.027943 | 0.004216–0.036238 |
| Bi M / As K min–max | 0.008415–0.097721 | 0.015537–0.103248 | 0.035377–0.118149 | 0.063733–0.138645 | 0.104670–0.165943 |

- **Bi L worst case anywhere in the range: Δx = 0.004754** (x = 0.20, worst scenario) — under half
  the bar. → `error_budget.csv` col `total_error`, max.
- **Bi L dominant mechanism: `overlap_i`** at every coupling ≥ 0.01; `counting` at coupling 0.001.
  → `route_ranking.csv` col `dominant_mechanism` = `overlap_i`; corroborated by
  `measurability_limit.csv` col `dominant_at_lowest_x`.
- **Bi M dominant mechanism: `sum_peak`.** Bi K and Ga_As K/K: `counting`. Ga_As L/*: `method`.
- Bi K `x_limit` (where it crosses the bar), `measurability_limit.csv` col `x_limit`,
  `status=bracketed`: **0.01135–0.01145 at dose 1.0**; **0.0865–0.0933 at dose 7.155**;
  `below_range` (never crosses) at dose 71.55. → this is the evidence for D-6 above.
- Bi M `x_limit`: **0.01075–0.01215**, and only in the 9 lowest-pile-up scenarios
  (`level=0.001`); the other 18 are `above_range`.
- Full route table (all 16 route/definition combinations) for **Appendix E**:
  `route_ranking.csv` filtered `definition=principal`, sorted by `fraction_measurable` desc.
- The 10%-relative sibling files `route_ranking_relative10.csv` /
  `measurability_limit_relative10.csv` are the **scrapped** bar (decision D1). Do not quote them
  except where Ch4.8 explains why the relative bar was rejected.

**Bi L budget decomposition** (framework Ch5.7: "sum peak four orders below, counting and overlap
comparable") — `error_budget.csv` cols `sigma_counting`, `sigma_overlap`, `bias_sumpeak`,
`bias_method`, filter `route=Bi_As, heavy_shell=L, light_shell=K, definition=principal`.
*Not yet tabulated here — pull the four columns at x = 0.01, dose 7.155, level 0.01, coupling 0.01
when Ch5.7 is drafted, and paste the four values in.*

---

## 3. Ch5.6 — Counting statistics and the overlap bound (LO4)

### Counting — `counting_by_route.csv`, `definition=principal`, `true_x_bi=0.01`

| Route (heavy shell) | dose 1.0 | **dose 7.155 (Walther reference)** | dose 71.55 |
|---|---|---|---|
| **Bi_As L** | 9.25% | **3.456%** | 1.093% |
| Bi_As M | 11.36% | 4.246% | 1.343% |
| Bi_As K | 93.57% | **34.98%** | 11.06% |
| Bi_Ga L | 9.36% | 3.501% | 1.107% |
| Ga_As K | 101.7% | 38.01% | 12.02% |

→ col `mean_relative_sigma`. The framework's "**noise 3.5%** at x = 0.01, Walther's dose" is
**3.456%** on the Bi L route. Independently corroborated at 3.47% by
`overlap_i_bound.csv` col `counting_only_relative` (0.034715).

⚠ **Bi K's photon problem in one number: 34.98% counting sigma at the reference dose**, vs 3.46%
for Bi L — a factor of **10.12**. This is the honest quantitative form of the retired "12× dose" line.

**Dose equivalence, derived from those two:** since σ ∝ 1/√N and N ∝ dose, matching Bi L's
counting statistics on the Bi K route needs **10.12² = 102.4× the dose**. This is consistent with
the ~103× detected-photon deficit (§7) — as it must be, which is a free cross-check.
⚠ **Not 10⁴×** — see §10. That figure appeared in `writeupTODO.md` and squared a factor that
should not be squared; it is corrected there as of 2026-09-10.

### Overlap (i) bound — `overlap_i_bound.csv`, `thickness_nm=100`, `dose_scale=7.155`

| coupling | x=0.01 | x=0.02 | x=0.05 | x=0.10 | x=0.20 |
|---|---|---|---|---|---|
| 0.001 | 3.690% | 2.540% | 1.589% | 1.131% | 0.817% |
| 0.010 | 5.266% | 3.156% | 1.754% | 1.189% | 0.836% |
| **0.100 (worst)** | **12.994%** | 6.714% | 2.934% | 1.661% | **1.006%** |
| *counting-only floor* | *3.472%* | *2.462%* | *1.569%* | *1.124%* | *0.814%* |

→ col `relative_uncertainty`; floor row is col `counting_only_relative`.
- Framework's "**~13% at x = 0.01 vs 1% at x = 0.20**" ✓ — **12.99% and 1.006%**, worst coupling.
- Framework's "below ~1% coupling the overlap adds little over the photon floor" ✓ — at
  coupling 0.001 the bound is 3.690% against a 3.472% floor: **+0.22 percentage points**.
  At coupling 0.01 it is 5.266% vs 3.472% — that one is *not* negligible; say "below 1%", not
  "at or below 1%".
- Neighbour ratio at x = 0.01, 100 nm: **N(neighbour)/N(Bi Lα) = 130.1** (107 958 vs 829.8
  counts) → cols `neighbour_ratio`, `n_neighbour`, `n_bi_la`. This is why the low-x corner is the
  hard one — the interfering line outnumbers the signal 130 : 1.
- ⚠ `overlap_i_bound.csv` exists **only at dose_scale 7.155**. Do not quote a dose sweep from it.
- ⚠ Every overlap number is a **lower bound** (col `overlap_is_lower_bound = True`); the coupling
  was swept, not derived (Ch6.5 limitation).

---

## 4. Ch5.5 — The sum peak is composition-selective (LO4; **fig04**)

`sumpeak_sensitivity.csv`, `thickness_nm=100` (Set B), production switches
`parents=alpha_only, basis=intensity, conserve=True, m_band_factor=1.743` — the only combination
present in this file.

**Fake counts as a fraction of true Bi Mα — col `fake_fraction_of_bi_m`:**

| pile-up level | x=0.01 | x=0.02 | x=0.05 | x=0.10 | x=0.20 | selectivity (0.01 / 0.20) |
|---|---|---|---|---|---|---|
| 0.1% | 5.579% | 2.769% | 1.083% | 0.521% | 0.241% | 23.2× |
| **1% (headline)** | **55.786%** | 27.687% | 10.830% | 5.214% | **2.409%** | **23.2×** |
| 10% | 557.9% | 276.9% | 108.3% | 52.1% | 24.1% | 23.2× |

- **The headline: at 1% pile-up, fake counts are ≈ 56% of Bi Mα at x = 0.01 and ≈ 2.4% at
  x = 0.20 — a 23× swing.** The framework says "≈55%" and "≈2%"; the CSV says 55.79% and 2.41%.
  Quote **56%** and **2.4%**, or "≈55%" if matching the deck — but not 97%, which is the
  **retired** pre-`m_band_factor` value (§5 rule 1).
- Ratio corruption at 1%, x = 0.01: Bi L/M goes **0.8715 (clean) → 0.5594 (corrupted)**, a 35.8%
  shift → cols `bi_l_m_clean`, `bi_l_m_corrupted`.
- The selectivity is exactly 23.16× at every level because fake counts scale with the parents
  (Ga+As), which barely move with x, while true Bi Mα scales with x. **That is the mechanism —
  state it, it is the whole point of the section.**
- Parent intensities are near-constant across x: I(Ga Lα) 7642 → 6621, I(As Lα) 7212 → 5197 over
  x = 0.01 → 0.20 → cols `i_ga_parent`, `i_as_parent`. Bi Mα baseline 133 → 2435 over the same
  span → col `bi_m_baseline`. **18× vs 0.87×** — that asymmetry *is* the selectivity.

### Switch influence — `sumpeak_switch_influence.csv` (4 rows, all of it)

| switch | settings | `difference` | `relative_difference` | **quote as** |
|---|---|---|---|---|
| basis | intensity vs rate_product | 0.018048 | 1.176061 | **2.2×** |
| m_band_factor | 1.0 vs 1.743 | 0.012073 | 0.658510 | **1.7×** |
| parents | alpha_only vs alpha_beta | 0.004188 | 0.188029 | 1.2× |
| conserve | True vs False | 0.000126 | 0.005174 | 1.005× (negligible) |

⚠ **`relative_difference` is a fraction, not a multiplier** (§5 rule 1). 1.176 → **2.2×**, not
1.2×. Convert as `1 + relative_difference`. Two of the four rows are easy to get wrong this way.
- Route ranking survives all 16 switch combinations → `sumpeak_roundtrip_by_route.csv`
  col `switch_spread` (32 rows = 2 definitions × 16). Pull the max spread when drafting.

---

## 5. Ch5.4 — Recovery of composition (LO4; **fig05**)

**Held out in both unknowns** (x *and* t) — `roundtrip_heldout_as_k_l.csv` (As K/L as the
thickness ruler) vs `roundtrip_heldout_ga_k_l.csv` (Ga K/L), col `error`, mean of `abs()`.

| filter | As K/L ruler | Ga K/L ruler | As advantage |
|---|---|---|---|
| **`principal`, all routes (production)** | **0.003626** | **0.005673** | **56%** |
| both definitions, all routes *(framework's figure)* | 0.003416 | 0.005018 | 47% |
| `principal`, Bi routes only | 0.000394 | 0.000585 | 48% |

**Handed-thickness comparison** — `roundtrip_recovered_x.csv` (k\* looked up at the *known*
100 nm, so held out in x only):

| filter | handed thickness | held out in both | held-out advantage |
|---|---|---|---|
| **`principal`** | **0.003915** | **0.003626** | **7.4%** |
| both definitions *(framework's 0.00377 vs 0.00342)* | 0.003766 | 0.003416 | 9.3% |

**The counter-intuitive result stands under either filter: reading thickness off the spectrum
beats being handed it.** → REPORT §18.5, §25. See D-1/D-2 above before quoting.

**Best single route, `principal`, As K/L ruler** — `roundtrip_heldout_as_k_l.csv` grouped by route:

| route | mean abs error |
|---|---|
| **Bi_As L/K (the recommended route)** | **3.38e-07** |
| Bi_As K/K | 3.68e-06 |
| Bi_As M/K | 3.34e-04 |
| Ga_As L/K (worst) | 2.24e-02 |

**Set C transfer (calibration built on Set A at x = 0.20, applied to Set C at x = 0.01)** —
`roundtrip_heldout_setc_lowx_as_k_l.csv`, `definition=principal`:

| route | mean abs error over 32–1024 nm |
|---|---|
| **Bi_As L/K** | **1.17e-07** ← the "~10⁻⁷" claim, **this route only** |
| Bi_As K/K | 5.04e-06 |
| Bi_As M/K | 3.70e-04 |
| Ga_As L/K | 8.94e-02 |
| *file-wide mean, all routes* | *1.31e-02* |

This is what closes the "calibration only demonstrated at 100 nm" limitation: the same k\*
transfers across a 32× thickness span **and** a 20× composition span with a residual of 10⁻⁷ on
the recommended route. → `VERDICT_BRIEF.md` caveat 6.

Per-x summary at 100 nm (all 32 route/definition estimates pooled) —
`roundtrip_summary.csv`, col `mean_abs_error`: x=0.01 → 0.005555; 0.02 → 0.005302;
0.05 → 0.004506; 0.10 → 0.003051; 0.20 → 0.000415. ⚠ This file pools **all** routes including
the ones the project rejects, so it overstates the error badly. Use it only to show the *trend*
with x, never as a headline.

---

## 6. Ch5.3 — Cross-check against Walther 2025

| Quantity | This work | Walther 2025 | Difference | Source |
|---|---|---|---|---|
| k\*(Bi L, As K) | **2.4161 ± 0.0051** (Set A, 2–1024 nm) | 2.490 ± 0.071 (Fig. 4 caption) | **−3.0%**, 1.04σ | REPORT §18.3; `kstar_calibration_setA.csv` |
| Bi L/M ratio factor between codes | — | — | **1.506 ± 0.020** over an 8× thickness range | REPORT §21.1b, from his Fig. 1 at 128/256/512/1024 nm |
| Ga K/L between codes | — | — | 0.98–1.08× (reading error) | REPORT §21.1b |
| As K/L between codes | — | — | 0.95–1.01× (reading error) | REPORT §21.1b |

- **State the −3.0% precisely as "just outside his quoted 1σ, not inside it"** (REPORT §18.3 is
  explicit). Our thinnest-foil value 2.4192 lands on his lower bound 2.419.
- Independent on every axis: different code, **6.2% higher density** (5.692 vs his 5.36 at
  x = 0.20), direct algebraic solve rather than his k × escape-fraction decomposition.
- The framework's "**1–3%**" is a range over the several k\* comparisons; the one documented
  number is −3.0%. **Pull the others from REPORT §18.3–18.4 when drafting, or narrow the claim
  to the pair that is actually evidenced.**
- **Bi M discrepancy: cause unidentified.** Three independent confirmations (eyeballed Figs 3/4
  → 1.4–1.6×; his stated L/M ≈ 1:1 vs our 1.515 → 1.51×; his Fig. 1 four thicknesses →
  1.506 ± 0.020). A factor that flat over that range is a fixed difference in I(Bi Mα), **not**
  absorption (which would vary with path length). The `summed` definition was tested as an
  explanation and **refuted** (gives Ga 1.48×, As 1.24×, Bi 2.77× — all worse).
  Caveat: readings off a printed plot, ±0.05.

**k\* composition-invariance across Set B** — `kstar_invariance_setB.csv`, `definition=principal`,
col `relative_spread`, n_points = 5 (x = 0.01…0.20 at 100 nm):

| route | k\* mean | relative spread |
|---|---|---|
| **Bi_As L/K** | **2.417774** | **0.0062%** ← invariant to the resolution limit |
| Bi_As K/K | 250.40 | 0.087% |
| Ga_As K/K | 0.8514 | 0.107% |
| Bi_As M/K | 3.6629 | 0.727% |
| Bi_Ga M/L (worst) | 2.9427 | 5.42% |

The recommended route is the flattest of all 16 — **found from the data, not by looking for it**
(REPORT §18.3). Walther's Fig. 4 does not test composition at all; this extends his claim.

---

## 7. Ch5.2 — Attenuation vs thickness and composition (LO3; **fig02**, **fig06**)

### ρ·t is not a sufficient absorption coordinate — the corner finding

`corner_rho_t_setA_vs_setC.csv`. **This file has two blocks with different populated columns —
do not mix them in one sentence (D-5).**

**Block A, `comparison = matched_rho_t`** — Set C (x=0.01) observed vs predicted from the Set A
(x=0.20) ρ·t curve. Col `residual_pct`:

| t (nm) | Ga K/L | As K/L | Bi L/M |
|---|---|---|---|
| 32 | −1.24% | −0.16% | +0.41% |
| 100 | −3.76% | −0.47% | +1.26% |
| 256 | −8.81% | −1.10% | +3.07% |
| 512 | −15.20% | −1.69% | +5.64% |
| **1024** | **−22.79%** | **−1.60%** | **+9.54%** |

**Block B, `comparison = matched_thickness`** — Set A vs Set C at equal *t*. Col `difference_pct`:

| t (nm) | Ga K/L | As K/L | Bi L/M |
|---|---|---|---|
| 32 | −1.51% | −0.63% | +0.23% |
| **1024** | **−26.29%** | **−6.96%** | **+5.66%** |

- The framework's "**Ga K/L −22.8%, As K/L −1.6% at 1024 nm**" is **Block A** ✓.
- The framework's "**17× growth**" is **Block B** (1.505 → 26.29 = 17.5×). Block A gives
  1.244 → 22.79 = **18.3×**. Pick one block, name it, and use its own growth factor.
- **The argument:** a constant density offset would give a constant percentage offset. A residual
  that grows 17–18× from 32 nm to 1024 nm cannot be a density artefact. Therefore ρ·t does not
  capture the composition dependence of absorption, and **Set C was required to test it**
  (REPORT §23). Causality the right way round: Set C *is* the test, not the consequence.

### Bi K is absorption-immune but photon-starved — fig06

- **I(Bi Lα) / I(Bi Kα1) = 103.0** (min 96.6, max 104.3 over Set A) → REPORT §21, §1496.
  Confirmed at 100 nm, x = 0.20 from `combined_intensities.csv`, col
  `Intensity Emitted Detected (photons)`: Bi Lα = **2107.15**, Bi Kα1 = **20.357** → **103.5×**.
- Detector efficiency, same run, col `Detector efficiency`: Bi Lα **0.9998**, Bi Mα **0.9818**,
  Bi Kα1 **0.2371**, Bi Kβ1 **0.2132**. **Bi K loses 76% of its photons in the detector alone** —
  that is a second, independent reason the K route is starved, distinct from generation yield.
- Line energies for the overlap discussion: Bi Mα **2.423 keV**, Bi Lα **10.840 keV**,
  Bi Kα1 **77.097 keV** → col `Line energy (keV)`.

### Density-model divergence with thickness — REPORT §13.4 (July comparison matrix)

Two density models, relative difference on the ratios, x = 0.20:

| t (nm) | Ga K/L | As K/L | Bi L/M |
|---|---|---|---|
| 2 | +0.0% | +0.0% | +0.0% |
| 32 | +0.4% | +0.7% | +0.3% |
| 128 | +1.5% | +2.6% | +1.0% |
| 512 | +4.9% | +7.0% | +3.4% |
| **1024** | +7.3% | **+8.4%** | +5.6% |

The framework's "**0 → 8.4%**" ✓ — As K/L, 2 nm → 1024 nm. **Mechanism:** absorption depends on
ρ·t, not ρ; at 2 nm nothing is absorbed so density is irrelevant, at 1024 nm the 9.5% density
difference comes through nearly in full. Set B is mild by contrast (+0.04% at x = 0.01) because
the two models converge as x → 0. ⚠ These come from **REPORT §13.4, not from `Aggregated\`** —
the July comparison matrix predates the production aggregation. Cite the REPORT section.

---

## 8. Ch5.1 — Geometry and absorption in the free-standing foil (LO2; **fig01**)

`diagnostic_ratios.csv` — 21 rows, one per run. Cols `Ga_K_L_principal`, `As_K_L_principal`,
`Bi_L_M_principal`.

**Set A (x = 0.20), K/L ratios rising with thickness as the soft L lines are absorbed:**

| t (nm) | Ga K/L | As K/L | Bi L/M |
|---|---|---|---|
| 2 | 1.3221 | 1.1155 | 1.3844 |
| 16 | 1.3474 | 1.1540 | 1.4017 |
| 100 | 1.5066 | 1.4058 | 1.5080 |
| 256 | 1.8295 | 1.9456 | 1.7169 |
| 1024 | **3.8309** | **5.3234** | **2.9234** |

**Set B (100 nm), ratios essentially flat in x — the thickness ruler is composition-blind:**
Ga K/L 1.4384 (x=0.01) → 1.4718 (x=0.10) → 1.5066 (x=0.20); As K/L 1.3800 → 1.3923 → 1.4058.

**Absorption fits** — `absorption_fits_and_crossings.csv`, `definition=principal, x_bi=0.2`,
n_points = 11 (the full Set A):

| curve | amplitude | χ_hard (nm⁻¹) | χ_soft (nm⁻¹) | R² (absorption model) | R² (exponential) | R² (linear) |
|---|---|---|---|---|---|---|
| Ga K/L | 1.3187 | 1.12e-04 | 2.838e-03 | **1.000000** | 0.992745 | 0.995881 |
| As K/L | 1.1104 | 1.82e-04 | 5.104e-03 | **0.999999** | 0.970201 | 0.995650 |
| Bi L/M | 1.3821 | 1.73e-04 | 1.947e-03 | **1.000000** | 0.996723 | 0.997940 |

**The two-attenuation-coefficient absorption model fits to R² ≥ 0.999999; a bare exponential
manages 0.970–0.997 and a straight line 0.996–0.998.** That is the quantitative case that the
rise is absorption, not an artefact. χ_soft / χ_hard = 25.3 (Ga), 28.0 (As), 11.3 (Bi) — the
soft line is attenuated an order of magnitude faster, which *is* the physical picture.

**Curve crossings** (same file, `kind = crossing`): Ga K/L crosses Bi L/M at **102.5 nm**
(ratio 1.511); As K/L crosses Bi L/M at **152.7 nm** (1.577); Ga K/L crosses As K/L at
**178.0 nm** (1.663). Useful if fig01's crossings need naming in the caption.

**Production densities used** (col `mass_density_g_cm3`, from ρ(x) = 5.32 + 1.86x):
x=0.01 → **5.3386**; 0.02 → 5.3572; 0.05 → 5.4130; 0.10 → 5.5060; 0.20 → **5.6920**.
⚠ fig01 is rendered at **ρ = 5.692** and that must be printed on the figure, along with the
second departure from Walther's Fig. 1 (see §9).

---

## 9. Figure inventory and caption data

Six figures in `C:\MCXRAY\Sim\Figures\` (PNG + PDF each), regenerable with
`python -m figures.make_all`.

| Fig | File | Section | Render settings that MUST appear in the caption | Status |
|---|---|---|---|---|
| 1 | `fig01_ratios_vs_thickness` | Ch5.1 | `principal`; x = 0.20; **ρ = 5.692**; log thickness axis; the two declared departures from Walther Fig. 1 (density, detector crystal 0.5 cm) | check caption |
| 2 | `fig02_rho_t_insufficiency` | Ch5.2 | `principal`; Set A (x=0.20) vs Set C (x=0.01); state **which block** — matched_rho_t or matched_thickness (D-5) | check caption |
| 3 | `fig03_measurability_limit` | Ch5.7 | `principal`; **Δx = 0.01 absolute**; 27 scenarios; counts derived at render time | **regenerated 2026-08-23 — current** |
| 4 | `fig04_sumpeak_selectivity` | Ch5.5 | `principal`; `m_band_factor = 1.743`, `parents=alpha_only`, `basis=intensity`, `conserve=True`; 100 nm | tick fix applied 2026-08-24 |
| 5 | `fig05_recovery_as_measured` | Ch5.4 | `principal`; held out in both x and t; As K/L ruler | check caption |
| 6 | `fig06_bi_k_absorption_vs_photons` | Ch5.2 | `principal`; Set A | **title corrected 2026-08-24** |

⚠ §5 rule 7: fig03 and fig06 were fixed in late August; **figs 1, 2, 5 have not been re-checked
for stale captions since the Δx = 0.01 threshold change.** Open each PNG before Ch5 is signed off.

---

## 10. Numbers that are RETIRED — if one appears in a draft, it is a bug

| Retired value | Where it came from | What replaces it |
|---|---|---|
| "fake counts **97%** of Bi M at x = 0.01" | pre-`m_band_factor`=1.743 | **55.8%** (§4 above) |
| "Bi K needs **>12×** Walther's dose" | computed against the scrapped 10%-relative bar | Bi K counting sigma **34.98%** vs Bi L 3.46% at the reference dose; and Bi K fails on **range**, not dose (§2, D-6) |
| "Bi L fails only **9** dose-or-worst-coupling corners" | `WORKPLAN_17AUG.md`, 17 Aug, 10%-relative bar | Under Δx = 0.01, Bi L fails **0 / 27** |
| "**297 tests**" | 17 Aug snapshot | **304** — verified by `pytest --collect-only` on 2026-09-10 |
| "10% target" / "`target_relative` = 10%" | decision D1 superseded it | **Δx = 0.01 absolute**; `metric = absolute` |
| "photon starvation" as the reason Bi K fails | presentation-era shorthand | **range** — it clears the bar at x = 0.01 and crosses further up |
| "Bi K needs **~10⁴×** the dose for equal counting statistics" | `writeupTODO.md` §3 — **an arithmetic error, not just staleness**: it squared a factor that should not be squared (σ ∝ 1/√N, so 103× fewer photons costs √103 ≈ 10.1× in σ, restored by 103× dose — not 103²) | **~102×**. Verified: σ(Bi K) 34.98% / σ(Bi L) 3.456% at the reference dose = 10.12; squared = 102.4 |
| "~4×", "0.002%" | deck-era strings | do not reuse; re-derive |

---

## 11. Provenance one-liners for the methodology

- **21 production runs**, flat in `C:\MCXRAY\Sim\Results\`, manifest
  `Aggregated\provenance_manifest.json` (Appendix A source).
- **28 aggregated CSVs** in `C:\MCXRAY\Sim\Aggregated\` — counted 2026-09-10. `NEXT_SESSION_PROMPT.md`
  says 23; that was the 17 Aug count, before the Δx = 0.01 rework added the `*_relative10` siblings
  and the Set C round-trip files. **28 is current; 23 is stale.**
- **304 tests**, verified by `pytest --collect-only` on 2026-09-10 (297 was the 17 Aug count).
- The intensity CSV is **21 rows** (Ga 6, As 6, Bi 9) — *not* 18. "18 lines" is the count
  cross-checked against Walther Table 1 (REPORT §254, `CLAUDE.md` trap 9).
- `combined_intensities.csv` = 441 rows = 21 runs × 21 lines ✓ (a free integrity check worth
  stating).
- Intensity column used throughout: **`Intensity Emitted Detected (photons)`** (Ch4.2 declares it).
- Dose scales swept: **1.0, 7.155, 71.55**. 7.155 is the Walther reference exposure
  (1 nA × 715.5 s live, a *labelled reference* — probe current is his estimate, Ch4.2).
