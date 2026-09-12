# Ch5 — Results

**14 pp · ~3,800 words · drafted Fri 12 (AM: 5.1–5.4 ~2,000 w; PM: 5.5–5.7 ~1,800 w)**

**Organised by objective, not chronology.** REPORT.md is chronological and
`REPORT_PLAIN_ENGLISH.md` contains superseded numbers — **neither is a template for this chapter.**

⚠ Every number in this chapter comes from `../DISSERTATION_NUMBERS.md` with its provenance comment
attached (§8 rule 4). **Read §0 of that file before drafting** — all six filter questions were
resolved 2026-09-10 and the numbers below already reflect the rulings.

⚠ **§5 rule 2 applies throughout:** "measurable across the range" and "at x = 0.01" are different
counts and both are correct. **Label which one, every time.**

---

## 5.1 Geometry and absorption in the free-standing foil — LO2 (~550 w) · **fig01**

**Numbers:** `DISSERTATION_NUMBERS.md` §8. **Sources:** REPORT §13.2, §18.

Frame this as **LO2's answer**, not as a by-product — at present the material is scattered.
- Soft L lines collapse with thickness; K/L ratios rise. Set A: Ga K/L 1.322 → 3.831, As K/L
  1.116 → 5.323 over 2 → 1024 nm.
- The two-coefficient absorption model fits to **R² ≥ 0.999999**; bare exponential 0.970–0.997,
  linear 0.996–0.998. χ_soft/χ_hard = 25–28 (Ga, As), 11 (Bi). *This is the quantitative case
  that the rise is absorption.*
- Per-line detector efficiency and the escape-path consequence of the 25° take-off angle.
- Set B ratios essentially flat in x — **the thickness ruler is composition-blind**, which is
  what makes it usable as a ruler. This sets up 5.4.

## 5.2 Attenuation vs thickness and composition — LO3 (~700 w) · **fig02**, **fig06**

**Numbers:** `DISSERTATION_NUMBERS.md` §7. **Sources:** REPORT §13.3–13.4, §20, §23.

- Bi K / L / M relative to the Ga and As references.
- **Bi K is the most absorption-immune route yet yields ~103× fewer detected photons**
  (I(Bi Lα)/I(Bi Kα1) = 103.0 over Set A). Second, independent cause: detector efficiency
  0.237 for Bi Kα1 vs 0.9998 for Bi Lα — **76% lost in the detector alone.**
- Density-model divergence grows with thickness, 0% at 2 nm → **8.4% at 1024 nm** (As K/L),
  because absorption depends on **ρ·t, not ρ**. Evidence, not a caveat.
- **The corner finding — ρ·t is not a sufficient absorption coordinate.** Set C observed vs what
  the Set A ρ·t curve predicts, at 1024 nm: Ga K/L **−22.79%**, As K/L **−1.60%**.
  ✅ **D-4/D-5 resolved 2026-09-10: use the `matched_rho_t` block throughout, growth factor
  included.** Do not quote −26.29% or 17.5× — those are the `matched_thickness` block.
- **The argument:** a constant density offset gives a constant percentage offset; a residual that
  grows **18.3×** from 32 nm (−1.24%) to 1024 nm (−22.79%) cannot be a density artefact.
  Therefore ρ·t does not capture the composition dependence of absorption, and Set C was required
  to show it.

## 5.3 Cross-check against the published work (~450 w) · table vs Walther Figs 3–5

**Numbers:** `DISSERTATION_NUMBERS.md` §6. **Sources:** REPORT §18.3–18.4, §19, §21.

- k\*(Bi L, As K) = **2.4161 ± 0.0051** vs Walther's 2.490 ± 0.071 → **−3.0%, 1.04σ**.
  **State precisely: just *outside* his 1σ, not inside it.** Our thinnest-foil value 2.4192
  lands on his lower bound 2.419. ⚠ The framework's "1–3%" is a range over several comparisons —
  either pull the others from REPORT §18.3–18.4 or narrow the claim to the evidenced pair.
- Independent on every axis: different code, 6.2% higher density, direct algebraic solve.
- **k\* composition-invariance:** Bi_As L/K spread **0.0062%** across x = 0.01–0.20 — flattest of
  all 16 routes, **found from the data, not by looking for it.** Walther's Fig. 4 does not test
  composition; this extends his claim.
- **Bi M discrepancy: 1.506 ± 0.020 between codes, three confirmations, cause unidentified.**
  A factor that flat over an 8× thickness range is a fixed difference in I(Bi Mα), not
  absorption. The `summed`-definition explanation was tested and **refuted**. Caveat: readings
  off a printed plot, ±0.05.

## 5.4 Recovery of composition — LO4 (~600 w) · **fig05**

**Numbers:** `DISSERTATION_NUMBERS.md` §5. **Sources:** REPORT §25; `../VERDICT_BRIEF.md` caveat 6.

✅ **D-1, D-2, D-3 resolved 2026-09-10 — quote `principal`.** The numbers below are already the
corrected ones; the framework has been updated to match.
- **Held out in both unknowns beats being handed the thickness** — 0.003626 vs 0.003915 under
  `principal` (7.4%). Counter-intuitive and worth a sentence of explanation: reading thickness
  off the spectrum removes the detector-sensitivity dependence that a measured thickness carries.
- **As K/L beats Ga K/L as the ruler** — 56% under `principal` (47% over both definitions).
- Best route Bi_As L/K: mean abs error **3.38e-07**.
- **Set C pushed through as unknowns:** calibration-transfer residual **1.17e-07 across
  32–1024 nm, for the Bi Lα/As Kα route specifically.** This closes the "demonstrated only at
  100 nm" limitation — the same k\* transfers across a 32× thickness span *and* a 20×
  composition span. **Never state the 10⁻⁷ as a property of the transfer in general** (D-3).

## 5.5 The sum peak is composition-selective — LO4 (~550 w) · **fig04**

**Numbers:** `DISSERTATION_NUMBERS.md` §4. **Sources:** REPORT §26.3, §26.6, §28.

- **Headline: at 1% pile-up, fake counts are ≈ 56% of Bi Mα at x = 0.01 and 2.4% at x = 0.20 —
  a 23× swing.** ⚠ **97% is retired** (pre-`m_band_factor` = 1.743).
- **The mechanism, which is the whole point:** fake counts scale with the parents (Ga Lα + As Lα),
  which barely move with x (7642 → 6621, 7212 → 5197); true Bi Mα scales with x (133 → 2435).
  18× against 0.87×. The artefact is therefore worst exactly where the science is.
- Ratio corruption at 1%, x = 0.01: Bi L/M 0.8715 → 0.5594 (35.8% shift).
- The calibration-corruption cancellation error that was caught, and what it shows.
- **Route ranking survives all 16 switch combinations.** Which switches matter:
  **basis 2.2×, m_band_factor 1.7×**, parents 1.2×, conserve negligible.
  ⚠ `relative_difference` is fractional — convert as `1 + value` (1.176 → 2.2×, not 1.2×).

## 5.6 Counting statistics and the overlap bound — LO4 (~500 w) · table

**Numbers:** `DISSERTATION_NUMBERS.md` §3. **Sources:** REPORT §27.4, §30.2.

- At x = 0.01, Walther's reference dose: counting noise **3.46%** on Bi L (corroborated
  independently at 3.47%), against **34.98% on Bi K** — a factor of 10.1. *This is the honest
  quantitative form of the retired "12× dose" line.*
- Overlap (i) worst case: **13.0% at x = 0.01 vs 1.0% at x = 0.20**, coupling 0.1.
- **Below 1% coupling the overlap adds little over the photon floor** — at 0.001 it is 3.690%
  against a 3.472% floor, +0.22 pp. ⚠ At coupling 0.01 it is 5.27% vs 3.47%, which is *not*
  negligible. Say "below 1%", not "at or below 1%".
- Why the low-x corner is hard, in one number: **the interfering line outnumbers Bi Lα 130 : 1**
  at x = 0.01, 100 nm.
- ⚠ Every overlap figure is a **lower bound** — coupling was swept, not derived.

## 5.7 Error budget and measurability limit — LO4 (~450 w) · **fig03** (the headline figure)

**Numbers:** `DISSERTATION_NUMBERS.md` §1–2. **Sources:** REPORT §31.

- The 27-scenario band per route (3 levels × 3 couplings × 3 doses).
- **Across the range:** Bi M fails **27/27**, Bi K fails **18/27** (measurable in 9),
  Bi L fails **0/27**.
- **At x = 0.01 specifically:** Bi M exceeds the bar in **18/27**, Bi K in **0/27**,
  Bi L in **0/27**.
- ⚠ **Both counts are correct. Never "fix" one to match the other.** For Bi K, 9 + 18 = 27 —
  complements, not a contradiction. Label the column every time.
- **Bi L worst case anywhere in the range: Δx = 0.004754** — under half the bar.
- Bi L budget decomposition: sum peak four orders below; counting and overlap comparable.
  *(Pull the four columns `sigma_counting`, `sigma_overlap`, `bias_sumpeak`, `bias_method` at
  x = 0.01, dose 7.155, level 0.01, coupling 0.01 when drafting — not yet tabulated.)*
- Dominant mechanism by route: Bi L → `overlap_i`; Bi K → `counting`; Bi M → `sum_peak`.
  **Each route fails for a different reason.** That is the finding, not an aside.
