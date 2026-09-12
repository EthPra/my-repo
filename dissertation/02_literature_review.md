# Ch2 — Literature review

**11 pp · ~1,600 new words (2.1 already drafted) · drafted Thu 11 (AM: 2.2–2.4; PM: 2.1 hand-off)**

**This chapter holds the largest unwritten block.** 2.1 exists; 2.2–2.4 are blank (~5 pp).

---

## 2.1 GaAs₁₋ₓBiₓ: incorporation, band structure, strain — **LO1** (~3,400 w, DRAFTED)

**Status: ~3,400 words already drafted in `../Lit review draft.pdf` ≈ 7 pp. This *is* LO1's
deliverable — LO1 has nothing else behind it.**

Beats 0–3 of the existing draft:
- Isovalent substitution on the As sublattice (Tixier)
- VBAC and ~90 meV bowing per x = 0.01 (Alberi; Usman)
- ΔSO engineering and Auger suppression → the Sheffield APD result (Liu 2021)
- Misfit strain and critical thickness (Tixier vs Lewis; kinetics)
- Trade-off synthesis (Richards)

**Work needed:**
- Paste the drafted text in.
- ⚠ **Ethan writes the closing hand-off paragraph himself** — one paragraph, his argument:
  *"so the composition worth measuring is dilute, and dilute is where the measurement is hardest."*
- ⚠ **Two corrections carried from `../PENDING_EDITS.md`:**
  - p.1: the "predicted" semimetal claim for GaBi wants a **second source**.
  - p.4: **0.12% misfit per %Bi is Ethan's own interpolation** from Tixier (3.1% → 0.37%) and
    Lewis (20% → 2.4%), **not a cited constant. Mark it as an inference.**

## 2.2 Quantitative EDXS of thin foils (~800 w, ~2.5 pp) — NOT DRAFTED

⚠ **Draft this with the Walther PDF open.** It is the one block where a drafted summary of a
source must be checked against the source itself, not against this repo's notes.

- Cliff–Lorimer ratio method and k-factors.
- Absorption correction and its thickness dependence.
- Why free-standing foils at fixed take-off are the standard geometry.
- **Walther 2025 (DOI 10.1111/jmi.70058) as the central paper:** his self-calibrating k\* method
  (Eqs 2/4/9), his Fig. 1 ratios, his stated precision bar (**Δx = 0.01, p.2** — this is where
  the project's threshold comes from), his sum-peak treatment (fitted, ~15%, applied to
  experiment only).
- ⚠ **Goldstein et al. must be cited** for detector physics (REPORT §27.6 flag).

## 2.3 Monte Carlo simulation of X-ray emission (~500 w, ~1.5 pp) — NOT DRAFTED

- What MC X-Ray models: trajectories, ionisation cross-sections, absorption on exit, detector
  efficiency **including the compiled-in ATW window**.
- What it does **not** model: pile-up / sum peaks (REPORT §17.4) — which is why Ch4.7 synthesises
  them; and **secondary fluorescence, never confirmed with the vendor** — Walther's own
  simulations exclude it. ⚠ This remains the project's one open question; state it as open.
- Why simulation can answer LO4 at all: **it knows the ground truth**, so quantification error is
  measurable rather than estimated.
- ⚠ Cite the MC X-Ray documentation but note **the manual is out of date** (units, line endings).
  Ch4.5 carries the evidence.

## 2.4 Detector physics used later (~300 w, ~1 p) — NOT DRAFTED

Sets up Ch3. Keep it to what is actually used downstream.
- Si(Li) resolution: FWHM² = (2.355)² · ε · F · E + noise².
- ε = 3.86 eV, F = 0.115 (**Goldstein — cite, and state the temperature caveat**).
- **Pile-up is a bias; peak overlap is a variance.** Introduce the distinction here; Ch3.3 uses it
  and the entire error budget rests on it.

---

**Cut 3 (if behind at Fri 22:00): 2.3 + 2.4 combine to one page.**
