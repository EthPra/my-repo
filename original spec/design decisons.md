# GaAsBi EDXS — Design Decisions & Methodology Log
 
A record of the experimental design, the parameters, and the reasoning behind each choice, as settled with the supervisor (Dr Thomas Walther). Companion to the Conceptual Foundation note.
 
---
 
## Locked simulation parameters
 
Fixed across every run, never adjusted:
 
- Beam energy: **200 keV**
- Trajectories: **10⁶** electrons per run
- Geometry: **free-standing foil** — a single GaAs₁₋ₓBiₓ region, no substrate, vacuum both sides
- Take-off angle: **25°**
- Detector: realistic energy resolution **~130 eV FWHM at Mn Kα**, with window
The only quantities adjusted run-to-run are those defined by Set A and Set B below.
 
## The cross design (not a full factorial)
 
A full thickness × composition × window grid would be too many McXray runs. Instead the design is an orthogonal **cross**: vary one main axis per arm through a shared central region.
 
**Set A — thickness arm (tests Assumption 2).**
Fix x = 0.2 (bismuth rich). Sweep the ten thicknesses, and run each twice (ATW window vs windowless). Cross-check against Casino.
- Thicknesses: **2, 4, 8, 16, 32, 64, 128, 256, 512, 1024 nm** (geometric doubling, 2ⁿ for n = 1…10).
- Runs: 10 thicknesses × 2 detector windows = **20**.
**Set B — composition arm (tests Assumption 1 worsening).**
Fix one intermediate thickness (100 nm). Sweep bismuth downward to find each line's sensitivity floor (where it vanishes into the bremsstrahlung background).
- Compositions: **x = 0.2 → 0.02 → 0.002 → 0.0002**.
- Runs: 4 compositions × single detector config = **4**.
**Total ≈ 24 runs** (matches the brief's "≈20–25").
 
### Open design points to settle
- The two arms do **not** share an identical run: Set A's doubling series doesn't include 100 nm, and Set B sits at 100 nm, so the "centre" of the cross is conceptual. If an exact shared anchor is wanted (for arm-to-arm cross-check), Set B's thickness could be aligned to a Set A value (e.g. 128 nm); 100 nm was chosen to match the paper.
- Decide Set B's single detector config — **windowless** is the natural pick, since the sensitivity floor lives at the low-energy end where the window bites hardest.
## LO4 change (form edit made)
 
- **Original LO4 thickness range:** 5 nm – 500 nm.
- **Revised LO4 thickness range:** geometric doubling series 2 nm – 1024 nm (2, 4, 8, 16, 32, 64, 128, 256, 512, 1024 nm).
- **Driver:** Walther's email — start at 2 nm, double (2ⁿ, n = 1…10, so up to 1024 nm), omit 1 nm as too noisy.
- **Scope of edit:** only the thickness clause of LO4 changed. Beam energy (200 keV), trajectory count (10⁶), composition range (0.01–0.2), and the objective's goal were all left exactly as submitted.
**Justification (for the methodology write-up):** this is a supervisor-directed refinement made in consultation (the A&O form is completed in consultation with the supervisor), not a unilateral scope change. LO4's 5–500 nm was the indicative target; it was extended to bracket the X-ray self-absorption that LO3 characterises — a thin limit (≈ generation-limited, negligible self-absorption) and a thick limit (strong differential attenuation of low-energy lines). The ×2 spacing distributes the ten points evenly on a log-thickness axis. t = 1 nm is dropped because at low x it holds too few Bi emitters for usable statistics. This mirrors how Set B already samples below LO4's nominal composition floor (down to x = 0.0002) for a diagnostic purpose — both are documented excursions beyond the indicative main-study ranges.
 
Note: four of the ten thicknesses (2, 4, 512, 1024 nm) lie outside the original 5–500 nm range, which is what required the LO4 update.
 
## Why free-standing (no substrate)
 
A GaAs substrate would generate a flood of extra gallium and arsenic X-rays unrelated to the thin layer's composition — amplifying the very lines that cause both overlaps (As Kα onto Bi Lα; Ga L + As L into the Bi Mα sum peak). A gold backing would be worse still (its own Au lines, extra absorption, electron backscatter). Free-standing isolates the foil's intrinsic X-ray behaviour, and is the only geometry in which the question stays clean.
 
## Detector window trade-off
 
The window protects the detector — it seals the cold crystal so the chamber can be vented for sample changes, and blocks stray light, infrared, and scattered electrons — but it absorbs low-energy X-rays on the way in. Windowless gives the best low-energy transmission (so the soft lines, Bi M / Ga L / As L, come through) but leaves the detector exposed and fragile. Set A compares both. A second consequence: windowless, by passing more soft Ga L / As L, also enlarges the Bi Mα sum peak — so the window choice cuts both ways for that line.
 
## Tooling & automation 
 
- Both programs run on Windows, fully extracted (the exe needs its `data` folder; an isolated exe will open but fail to simulate).
- Use the x64 builds: `console_mcxray_lite_x64.exe`, `wincasino2_64.exe`.
- **Scriptability confirmed:** the console executable is bundled, so McXray is automatable (generate input files → call the console exe → parse output).
- `pymcxray` exists (Python wrapper) but is old (Python-2 era, last release 2019) and its default config expects a non-Lite exe name. A thin custom runner built off the McXray `examples/` input format is likely cleaner.
## Validation criteria (T2.2 — what "success" means)
 
Not "a spectrum appeared," but:
 
- Peaks land on tabulated line energies (checked against X-ray Data Booklet / NIST).
- As Kα and Bi Lα crowd / partially overlap at realistic resolution.
- Sub-lines resolve individually (Bi Lα as its own line), not lumped into "L."
- Absorption responds correctly: thicker foil preferentially attenuates the low-energy lines.
- McXray's lumped intensities cross-check sanely against Casino's.
## Governance
 
Scientific judgement — the hypothesis verdict and interpretation — stays with the student. Mechanical work (scripting, parsing, plotting, drafting) may be delegated. All physical quantities (line energies) are verified against primary sources (X-ray Data Booklet / NIST); citations and values are never invented.