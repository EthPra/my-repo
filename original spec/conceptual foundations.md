# GaAsBi EDXS — Conceptual Foundation
 
Distilled physics underpinning the dissertation. Energies are kept qualitative throughout; resolve exact line energies from the X-ray Data Booklet / NIST before quoting them.
 
---
 
## The problem in one paragraph
 
The project tests Walther's published claim (*Journal of Microscopy* 2025, DOI 10.1111/jmi.70058) that routine EDXS quantification of bismuth in GaAs₁₋ₓBiₓ is *misleading*, because two characteristic-line overlaps corrupt the bismuth signal. The distinctive leverage is that a Monte Carlo simulation fixes the true Bi fraction *x* exactly — which a physical experiment never knows — so the overlap-induced quantification error can be measured precisely against ground truth, and Walther's iterative k-factor correction assessed. The deliverable is a recommendation: which line, line-pair, or correction is most reliable as a function of foil thickness, composition, and detector configuration.
 
---
 
## 1. Characteristic X-rays — the fingerprint
 
An inner-shell electron is knocked out by the beam; an outer electron drops in to fill the hole and releases the energy as an X-ray. That X-ray's energy equals the gap between the two shells, which is set by the element's nuclear charge — so it is a fixed number, unique to each element and shell pair. That fixed energy is the fingerprint.
 
Naming: the **letter** (K, L, M) is the shell that held the hole; the **Greek letter** (α, β…) is how far the filling electron fell — α from the adjacent shell (strongest), β from further out (weaker). So As Kα = hole in arsenic's K shell, filled from L; Bi Lα = hole in bismuth's L shell, filled from M.
 
Same mechanism as ordinary atomic emission spectra, but with inner shells and X-ray energies. One step beyond chemistry: the L shell is three sub-shells (L1/L2/L3) with selection rules, so Lα splits into Lα1/Lα2. **This sub-line fine structure is exactly what McXray resolves and Casino2 cannot — the whole reason McXray is the primary tool.**
 
## 2. Peak height tracks amount
 
More atoms of an element in the beam path → more ionisations → more X-rays of its line → a taller peak. The peak is a vote count: peak size measures how much of that element is present. Within one element the proportionality is clean (double the bismuth, roughly double the Bi peak).
 
## 3. Fluorescence yield — the atoms-to-counts exchange rate
 
Not every ionisation emits an X-ray. The atom can instead eject an Auger electron and produce no X-ray. The fraction taking the X-ray route is the **fluorescence yield**, and it is element-specific — high for heavy elements (bismuth), low for light elements (mostly Auger), and higher for K than L than M shells.
 
Consequence: within one element, peak height still tracks amount. *Across* elements, equal peaks do **not** mean equal amounts, because the atoms-to-counts exchange rate differs by element.
 
## 4. The k-factor
 
You don't read absolute peak heights (they depend on beam current, time, total material). You take the **ratio** of two lines — your element against a reference — which cancels everything shared. A single per-pair correction number, the **k-factor**, converts that measured ratio into the true amount ratio:
 
> true amount ratio = k × measured peak-height ratio
 
The k-factor bundles the conversion-efficiency gap between the two lines: ionisation cross-section × fluorescence yield × sub-line share × absorption × detector efficiency, for line A relative to line B. k-factors are standard (Cliff–Lorimer); they are **not** the thing routine quantification gets wrong.
 
## 5. Detector resolution — why peaks have width
 
The detector reads an X-ray's energy by counting the charge it deposits, and that count jitters (charge-creation statistics + electronic noise). So a sharp line is recorded as a **bump of finite width** — the energy resolution, ~130 eV FWHM at the Mn Kα reference line. Two lines closer than that width merge into one hump whose counts cannot be sorted by origin; the blur destroys the information needed to separate them. A realistic detector is therefore mandatory in simulation — an idealised, too-sharp detector would falsely resolve the overlap and silently invalidate the hypothesis test.
 
---
 
## The two overlaps
 
### Overlap 1 — As Kα ≈ Bi Lα (the "misleading Bi Lα")
 
Two unrelated elements' shell gaps happen to coincide. Arsenic is the **majority** element, so the As peak dwarfs the small Bi peak sitting on its flank. Naive integration of the bright Bi Lα window scoops up arsenic counts → inflated, contaminated bismuth reading. This is a real characteristic-line overlap, so it is **simulable directly in McXray** (emit both lines, apply the detector blur). It worsens as bismuth dilutes (Set B), because arsenic dominates the window further.
 
### Overlap 2 — Ga Lα + As Lα sum peak ≈ Bi Mα
 
Bi Mα is the backup line once Bi Lα is contaminated. Its contaminant is a **sum peak (pile-up)** — a *detector artifact*: two X-rays arriving within the detector's processing window are recorded as one fake count at their combined energy. The two abundant soft host lines, Ga Lα and As Lα, sum to ≈ Bi Mα, manufacturing a phantom peak built entirely from gallium and arsenic — no bismuth required.
 
Nastier than Overlap 1 because it can fake bismuth where there is none, and it is rate-dependent (grows with beam current / total signal / thickness), so it masquerades as scatter. Being a detector artifact, **McXray (which simulates the emitted spectrum) likely won't produce it natively** → confirm McXray's pile-up handling; if absent, compute the sum peak analytically (from Ga L / As L count rates and the detector processing time) and add it in post-processing. **Open methodological question.** Window twist: windowless lets more soft Ga L / As L through, so it *feeds* the sum peak even as it helps you see Bi Mα.
 
---
 
## The two assumptions (the thesis hinge)
 
The k-factor / ratio method holds only while both are true:
 
- **Assumption 1 — the peak is pure.** Every count under a line belongs to that element. Broken by the overlaps. Studied via the overlap analysis and Set B (dilution makes it worse).
- **Assumption 2 — the bundle is constant.** k is a single fixed number. Broken because two ingredients move: absorption (changes with thickness) and detector efficiency (changes with the window). Studied via Set A (thickness sweep × ATW vs windowless).
These two assumptions failing *are* the two experimental arms.
 
## Why there is no easy answer
 
All three bismuth candidate lines are compromised, each differently:
 
- **Bi K** — bound too deep to excite efficiently at 200 keV.
- **Bi Lα** — overlapped by a real arsenic line (Overlap 1).
- **Bi Mα** — overlapped by a detector-made Ga+As phantom (Overlap 2).
No clean line exists to simply read off, which is precisely why the simulation study is needed.