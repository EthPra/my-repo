# Orientation map — what's what, and what's related

*Written 2026-08-23. Every value here was read from source or from `Aggregated\*.csv`, not from
prose. Purpose: this project carries seven independent axes and several of them share vocabulary,
so two things that sound alike are routinely conflated. This file is the disambiguator.*

**Not a status file.** `WORKPLAN_17AUG.md` is authoritative for progress; `VERDICT_BRIEF.md` for
the decisions and their reasoning. This file only says *what each thing is* and *how it differs
from the thing it gets confused with*.

---

## 1. The four confusions that actually bite

### "K/L" means two completely different things

| | **As K/L ratio** | **Bi L / As K** |
|---|---|---|
| what it is | the **thickness proxy** — "the arsenic ruler" | the **quantification route** |
| shells | *one* element (As), *two* shells | *two* elements, *one* shell each |
| answers | *How thick is this foil?* | *How much bismuth is in it?* |
| why it exists | a real experimenter doesn't know the thickness, so it's read from the spectrum instead | it's the measurement the whole project is for |
| where it's decided | methodology beat ④ — index on As, not Ga | the verdict |

Both are "a ratio with a K and an L in it." They are unrelated jobs. **`Bi_As L/K` is not a K/L
ratio** — it is a Bi L line over an As K line.

### The route name packs three axes into one string

`Bi_As` + `heavy_shell=L` + `light_shell=K` reads as **Bi Lα measured against As Kα**.

- `route` — which *element pair* (`Bi_As` or `Bi_Ga`)
- `heavy_shell` — which **Bi** line (`L`, `M`, `K`)
- `light_shell` — which **reference** line (`K`, `L`)

Said aloud, without notation: *"the bismuth L-alpha line measured against arsenic K-alpha."*

### The two overlaps are different animals

| | **the sum peak** | **overlap (i)** |
|---|---|---|
| what | Ga Lα + As Lα recorded as one photon at 2380 eV, landing on Bi Mα (2423 eV) | As Kα sitting near Bi Lα |
| separation | 43 eV = **0.47 FWHM** → *merged*, unresolvable | 297 eV = **1.75 FWHM** → *resolvable* |
| statistical kind | **bias** — systematically one direction, more counting does not fix it | **variance** — noisier but unbiased |
| how handled | synthesised and propagated (MC X-Ray cannot produce pile-up) | **bounded, not modelled** — needs four uncitable inputs |
| hits which line | Bi **M** | Bi **L** |

### Three different things are all called "10%"

- the **retired accuracy threshold** (10% relative on x) — scrapped 2026-08-21
- an **overlap coupling level** (0.1 / 1 / **10**%) — a legitimate swept level, still in use
- a **sum-peak level** (0.1 / 1 / **10**%) — also a swept level, still in use

Only the first was scrapped. Seeing "10%" in a caption does not mean the figure is stale.

---

## 2. The axes, one at a time

### Decided axes — settled, not configurable without a new decision

| axis | values | production | recorded in |
|---|---|---|---|
| **Line definition** | `principal` / `summed` | **`principal`** | VERDICT_BRIEF decision 2 |
| **Accuracy threshold** | absolute Δx / relative % | **absolute Δx = 0.01** | VERDICT_BRIEF decision 1 |
| **Sum-peak `parents`** | `alpha_only` / `alpha_beta` | **`alpha_only`** (Ga Lα + As Lα) | VERDICT_BRIEF decision 3 |
| **Sum-peak `basis`** | `intensity` / `rate_product` | **`intensity`** | VERDICT_BRIEF decision 3 |
| **Sum-peak `conserve`** | `True` / `False` | **`True`** (parents depleted) | VERDICT_BRIEF decision 3 |
| **Sum-peak `m_band_factor`** | 1.0 simulated / **1.743** measured | **1.743** | VERDICT_BRIEF decision 3 |

**`principal` vs `summed`, in one line:** `principal` uses the single strongest line of each
shell; `summed` adds the shell's lines together. `summed` scores *better* but every `summed` row
carries `overlap_is_lower_bound=True`, because summing pulls in As Kβ, which is itself touched by
Ga Kβ — a second contamination channel this project never costed. So its advantage is partly an
uncosted risk. **Same top route under both**, which is why `summed` is kept as a stated
robustness check rather than discarded.

**Threshold, in one line:** Δx = 0.01 is Walther's own stated bar (*J. Microsc.* 2025, p.2 —
"0.5 at%", i.e. half a percent of *all* atoms, because x is the fraction of the group-V
sublattice). The retired 10% relative had no literature anchor and, being relative, tightened the
absolute demand exactly where x is smallest — punishing the low-x arm the project added. Both
rankings are stored (`route_ranking.csv`, `route_ranking_relative10.csv`): the top route is the
same under both, which is the point of keeping the second.

**`m_band_factor` matters more than it looks.** It changed from 1.0 → 1.743 on 2026-08-21, which
rescaled the Bi M baseline and moved every sum-peak magnitude. Any number quoted about sum-peak
size from before that date is stale — including "97% of the Bi M signal at x = 0.01", which is
now ≈55%.

### Swept axes — never defaulted, always reported as a range

**27 scenarios = 3 × 3 × 3.** Nothing here gets a single value, because none of the three
magnitudes is knowable from this data.

| axis | values | meaning |
|---|---|---|
| sum-peak `level` | 0.001 / 0.01 / 0.1 | how much pile-up there is |
| overlap `coupling` | 0.001 / 0.01 / 0.1 | how much As Kα leaks into Bi Lα |
| `dose_scale` | 1.0 / **7.155** / 71.55 | 100 s / **Walther's 715.5 s** / 2 h |

Separately, the four sum-peak switches give **16 combinations** (2⁴) — a *different* sweep,
checking that the route ordering survives every modelling choice. **27 and 16 are not the same
grid.** 27 = magnitudes; 16 = modelling choices.

### The run matrix — 21 simulations

| set | what varies | held fixed | runs |
|---|---|---|---|
| **A** | thickness 2→1024 nm | x = 0.2 | 10 |
| **B** | x = 0.01→0.2 | 100 nm | 5 |
| **C** | thickness 32→1024 nm | x = 0.01 | 6 |

Set C was added 2026-08-13 because ρ·t proved insufficient as an absorption coordinate — the
cross could not predict its own interior. That failure is what fig02 shows, and it is also why
the As-vs-Ga ruler choice became a measurement rather than a preference.

---

## 3. Where each thing is recorded

| you want | look in |
|---|---|
| a decision and *why* | `VERDICT_BRIEF.md` |
| what still needs declaring in the write-up | `writeupTODO.md` |
| the technical history, section by section | `REPORT.md` |
| the same history in plain English | `REPORT_PLAIN_ENGLISH.md` — **chronological, contains superseded numbers** |
| the run-by-run intensities | `Aggregated\combined_intensities.csv` |
| route standings | `Aggregated\route_ranking.csv` (+ `_relative10`) |
| the error decomposition | `Aggregated\error_budget.csv` |
| what a figure actually plots | that figure's module docstring in `figures\` |

⚠ **Reading `measurability_limit.csv`:** the column is named `target_relative` even in absolute
mode, where it holds 0.01. The sibling `metric` column (`"absolute"` / `"relative"`) is what
disambiguates. Read them together.

---

## 4. Still open

- **Why Bi K is rejected.** Its "needs 12× the acquisition" rationale was computed against the
  retired 10% relative bar. Against Δx = 0.01 it clears at 100 s at x = 0.01 — no extra dose at
  all. The recommendation is unaffected (Bi L beats it ~19× vs ~2.9× on margin at x = 0.01), but
  the *stated reason* needs replacing. Candidates visible in the data: Bi K only clears in a
  window (fails at x ≥ 0.1 at Walther's dose, where Bi L never does), or margin. Ethan's call.
- **Secondary fluorescence** in MC X-Ray — never asked of the vendor. Walther's own sims exclude
  it.
