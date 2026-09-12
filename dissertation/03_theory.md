# Ch3 — Theory

**5 pp · ~1,600 words · drafted Thu 11 PM**

Moved out of Methodology exactly as the presentation did (`../PRESENTATION_SCRIPT.md` §A).
**Nothing here is a method** — it is what the methods rest on.

---

## 3.1 Ratio → composition (~500 w)

**Sources:** REPORT §18.2, §25.2; `../ORIENTATION_MAP.md` §1.

- Walther's inversion and the three closed forms — x, x(1−x), 1−x (Eqs 2/4/9).
- ⚠ ***A* is atomic weight; ρ is atomic density and does not enter these equations at all.**
  Personal communication resolved the paper's gloss, which had conflated the two. Consequence:
  every k\* is correct in **absolute** terms, not merely up to a cancelling factor — which is
  what makes the literature comparison in Ch5.3 legitimate at all.
- k\* as a **self-calibrating** constant.
- Why a thickness proxy read from the spectrum is needed — the "arsenic ruler". A real
  experimenter is not handed the foil thickness; the round trip must be held out in **both**
  unknowns.

## 3.2 Absorption and mass-thickness (~400 w)

**Sources:** REPORT §6.3, §10, §15.2; `../writeupTODO.md` §3.

- Why ρ·t is the *naive* coordinate — and flag forward that Ch5.2 shows it is insufficient.
- The density model **ρ(x) = 5.32 + 1.86x**, from Walther's endpoints (GaAs 5.32, GaBi 7.18).
- Why auto-mixed *elemental* Ga/As/Bi densities are the wrong physical picture for a covalent
  zinc-blende alloy — and that leaving `UserDefinedMassDensity = 0` triggers exactly that,
  **silently, ~15–20% too dense.**
- The ~15% intensity consequence of getting it wrong.

## 3.3 The two overlaps (~450 w)

**Sources:** REPORT §27.1; `../WORKPLAN_17AUG.md` §5.

- **The sum peak:** Ga Lα + As Lα = 2.380 keV against Bi Mα at 2.423 keV — **43 eV apart,
  0.47 FWHM: merged, not resolvable.**
- **Overlap (i):** As Kα against Bi Lα — **297 eV, 1.74 FWHM: resolvable.**
- ⚠ **Bias vs variance — the distinction the whole error budget rests on.** The sum peak adds
  counts that are not there (a bias, uncurable by longer counting); the overlap adds uncertainty
  to a line that is there (a variance, which dose reduces). Get this right here and Ch5.7 and
  Ch6.2 both follow from it.
- This asymmetry is *why* Ch4.7 models one and bounds the other.

## 3.4 Counting statistics (~250 w)

**Sources:** REPORT §30.1; `../writeupTODO.md` §3, §4.

- Var(ln N) = 1/N.
- **Why expectation values from the simulator must be re-noised:** MC X-Ray returns expectation
  values, not a realisation. A real spectrum carries Poisson noise the simulation does not.
- First-order validity limit (~30% relative) and where it bites — flagged per row in the CSVs
  (`first_order_valid`).

---

**Cut 4 (last resort): fold this chapter into Ch4 as a 2-page "basis" subsection.**
