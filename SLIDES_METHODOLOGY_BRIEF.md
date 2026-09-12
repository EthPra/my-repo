# Methodology slides — handoff brief

*Written 2026-08-20 to carry the method into the slide-building session. Companion file:
`PRESENTATION_METHODOLOGY_DELIVERY.md` — the spoken script these slides sit behind. Take both.*

**Design and structure: defer entirely to the conventions already established in that session.**
This brief specifies *what goes on each slide and in what order*, never how it should look.

---

## Two hard constraints

1. **No verdict.** No recommended line pair, no ranking, no accuracy threshold. Those are the
   concluding slides, being written 21 Aug. The methodology section's job is to **earn** that
   conclusion, not to front-run it.
2. **Five minutes of speech, total.** The per-slide budgets below are measured, not estimated.
   Slide density should follow them: 28 seconds is one line and a number; 136 seconds is a
   sequence. **If a slide can't be spoken to in its budget, it has too much on it.**

---

## Slide sequence — 7 slides

| # | Landmark | Budget | Content | Figure |
|---|---|---|---|---|
| 1 | ① The frame | 28 s | Running the code is the easy part. **Almost every way of getting it wrong produces a result that looks completely normal.** | — |
| 2 | ② The wrapper and the gate | 42 s | 21 simulations × 6 input files. Three silent killers: **Ångströms not nanometres** (manual is wrong), **weight not atomic fraction**, **density must be set or it auto-mixes elemental densities**. None throw an error. Gate: byte-for-byte diff vs validated reference; faults injected deliberately, **5 of 5 caught**. | — |
| 3 | ③ Nothing invented | 31 s | Every constant traces to a source or the code stops. Density: both codes interpolate *elemental* metal densities; GaAsBi is covalent. **On Walther's advice**, endpoints **5.32 / 7.18**, interpolated — updates his own published paper. | — |
| 4 | ④ The matrix grew | 74 s | Matrix is a **cross**, which assumes the interior interpolates on mass-thickness. **Tested, and it failed — 23% wrong at 1 µm.** Not a density artefact: offset is constant, **error grows 17-fold** with thickness. Third arm added at x = 0.01. Consequence: **Ga K/L tracks composition (26%), As K/L doesn't (7%)** → index on As K/L. | **fig02** |
| 5 | ⑤a Three degradations | ~50 s | Simulation output is clean; **no detector produces that spectrum.** Three degradations, none in the output file. Both overlaps measured against detector linewidth: **sum peak 0.47 → merged; As Kα / Bi Lα 1.75 → resolvable.** Different problems, different models. | — |
| 6 | ⑤b Two overlaps | ~50 s | Sum peak fakes counts on Bi Mα (2.380 vs 2.423 keV) → **synthesised and propagated through the whole recovery; magnitude swept; all 16 switch combinations, ordering identical in every one.** Second overlap **bounded, not modelled** — four uncitable inputs, not invented. **Sum peak = bias; overlap = variance.** | **fig04** |
| 7 | ⑤c One currency → hand off | ~48 s | Counting statistics: ~**116 photons** on Bi Lα at x = 0.01. Three mechanisms, incompatible units → converted to **error on recovered composition**. **Nothing unknown gets a default: 27 scenarios swept**, and the code **refuses to extrapolate**. Ends by handing to the conclusions. | — |

---

## Figures

Rendered files live in `C:\MCXRAY\Sim\Figures\` as both `.png` (200 dpi) and `.pdf` (vector).
**Placeholder captions are fine for now** — the figures themselves already carry their annotations.

| file | use |
|---|---|
| `fig02_rho_t_insufficiency` | **Slide 4.** Two panels sharing an axis — left, the arms separate; right, they nearly coincide. *The finding is the contrast between panels*, so both must stay visible together. |
| `fig04_sumpeak_selectivity` | **Slide 6.** Shows the artefact's composition dependence. Safe here — it's a finding about the artefact, not a recommendation. |
| `fig03_measurability_limit` | ⚠ **Do NOT use in methodology.** It is the LO4 headline and gives the ranking away. **Hold it for the conclusions**, where it's the payoff. |
| `fig01`, `fig05`, `fig06` | Not in the 5-minute script. Available if a slide needs them, but they lengthen the section. |

---

## Numbers — quote these exactly

All re-derived from the stored CSVs on 2026-08-20, not transcribed from prose.

| | |
|---|---|
| Simulations / tests | **21** runs, **297** tests green |
| Fault injection | **5 of 5** caught |
| Density endpoints | **5.32** (GaAs), **7.18** (hypothetical GaBi) → ρ(x) = 5.32 + 1.86x |
| ρ·t interpolation failure | **−22.8%** at 1024 nm; matched-thickness gap **−26.3%** |
| Ga K/L vs As K/L, matched thickness | **26.3%** vs **7.0%** *(don't mix bases — see below)* |
| Ga K/L vs As K/L, matched ρ·t | **22.8%** vs **1.6%** |
| Growth of the Ga K/L gap | **1.5% → 26.3%** (17-fold) against a *constant* −6.2% density offset |
| Sum peak vs Bi Mα | 43 eV = **0.47 FWHM** (merged) |
| As Kα1 vs Bi Lα | 297 eV = **1.75 FWHM** (resolvable) |
| Sum-peak switch combinations | **16** (full factorial), route ordering identical in all |
| Scenarios swept | **27** (3 levels × 3 couplings × 3 doses) |
| Detected photons, x = 0.01, 100 nm | Bi Lα **116**, Bi Mα **76** |

⚠ **Never put 26% and 2% on the same slide.** They come from different comparisons — 26% is
matched *thickness*, 2% is matched *mass-thickness*. Quote one row or both rows, never one number
from each.

---

## Things a slide must not claim

- **Any mechanism for why Ga and As differ.** It is measured, not explained — explaining it needs
  cited mass attenuation coefficients this project doesn't hold. An absorption-edge story on a
  slide would be inventing physics.
- **That the density model corrects Walther.** He advised it. Attribute, don't editorialise.
- **Any accuracy threshold**, until it is settled on 21 Aug.
