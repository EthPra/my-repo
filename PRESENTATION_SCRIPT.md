# Presentation — the single spoken script

*Started 2026-08-23, merging `PRESENTATION_METHODOLOGY_DELIVERY.md` and
`PRESENTATION_CONCLUSIONS_DELIVERY.md` into one file, restructured against the School's brief
(Appendix 3 + Section 7). Not a script to read aloud verbatim — the spoken argument, beat by
beat, with the lines that should land in **bold**.* **Learn the landmarks, not the sentences.**

**Slot: 20 min total — ~15 min presenting, up to 5 min questions. 10–12 slides recommended.**

---

## Running order and budget

| slides | section | budget | script |
|---|---|---|---|
| 1–2 | Title, Overview | 0:45 | trivial — name the six sections and move |
| 3 | Background & Motivation | 1:45 | **§1 below** — from `Lit review draft.pdf` |
| 4 | Aims & Objectives | 1:00 | **§2 below** |
| 5 | Outline theory | 1:45 | **§A below** (moved out of Methodology) |
| 6–8 | Methodology | 3:30 | **§B below** — compressed from 7 slides to 3 |
| 9–10 | Results & Discussion | 4:00 | **§3 below** — 2 slides |
| 11–13 | Conclusions & Future Work | 2:00 | **§C below** — 3 slides |
| | | **14:45** | |

**All six sections are written.** The budget now lands at 14:45 rather than 15:00 — slide 8 was
shortened on 2026-08-25 — so there is a quarter-minute of genuine slack. Slide 9 has more: its
script was cut to ~200 words against a 2:00 budget, which is deliberately unhurried. **Do not
speed up to fill the time.** Slack in a first delivery is worth more than an extra sentence.

---

## Register — the one rule that governs this whole file

The School says *avoid being too technical*, and both markers come from broader technical
backgrounds. That does **not** mean removing content — it means **never letting a mechanism name
travel without the two-word reminder of what it does.**

Concretely, the swaps that matter:

| don't say | say |
|---|---|
| "the K/L ratio as a stand-in for thickness" | "**the arsenic ruler** — the sample's own brightness ratio, read off the spectrum you're already measuring" |
| "mass-thickness" | "**how much material the beam actually crosses** — thickness times density" |
| "the sum peak" *(first use)* | "**the sum peak — two X-rays arriving together and counted as one**" |
| "overlap (i)" | "**the arsenic–bismuth overlap**" |
| "0.47 FWHM" | "**closer together than the detector can separate**" |
| "Bi_As L/K, principal" | "**bismuth's L-alpha line measured against arsenic's K-alpha**, using the single strongest line of each" |

Say the plain version first and the technical name second, never the reverse. The markers who
know the jargon lose nothing; the ones who don't stay with you.

---

## §1 — Background & Motivation *(slide 3, 1:45)*

*Sourced entirely from `Lit review draft.pdf`; every claim below appears there with a citation.
The arc is the lit review's own Beat 3 synthesis — benefit arrives early, cost arrives late —
because that is what makes the project matter rather than being a methods exercise.*

**The four ideas underneath this, in case the wording slips:** (1) the *band gap* is the energy
step an electron has to climb, and it decides what colour of light the material works with —
smaller step, redder light, eventually infrared; (2) bismuth shrinks that step fast, so a tiny
amount does a lot; (3) a bismuth atom is physically bigger than the arsenic it replaces, so the
crystal ends up permanently stretched, and that stress grows with the *square* of the bismuth
content — double the bismuth, roughly quadruple the stress; (4) therefore devices live at a few
percent, which is exactly where there is barely any bismuth to measure.

> "This is gallium arsenide — a standard semiconductor, used everywhere. What we're doing is
> swapping a few of its arsenic atoms for bismuth atoms.
>
> Bismuth does two things, and they pull in opposite directions.
>
> **The good thing: it shrinks the material's band gap** — the energy step an electron has to
> climb. A smaller step means the material works with redder light, and eventually infrared.
> That's what you want for fibre-optic telecoms and infrared detectors. And **a tiny amount of
> bismuth does a lot** — the first one percent moves that step more than most other substitutions
> manage at all.
>
> And that's not theoretical. **This department built photodiodes with a few percent bismuth in
> them, and the noise dropped by more than half** — down to roughly silicon levels, in a material
> that still sees into the infrared.
>
> **The bad thing: a bismuth atom is physically bigger than the arsenic atom it replaces.** Force
> enough of them in and the crystal is left permanently stretched — and that stress doesn't build
> gently. **Double the bismuth and you roughly quadruple it.** Push far enough and the crystal
> starts to come apart.
>
> **So the benefit arrives early and the damage arrives late.** Which means the useful devices all
> sit in a narrow band — just a few percent bismuth.
>
> And that's the problem. **A few percent bismuth means there's barely any bismuth in there to
> measure.** The composition that matters most is the hardest one to measure. That's what this
> project is about."

**Slide 3 already carries the right three-part structure** (the appeal / the stakes / the catch).
Two changes would sharpen it: name the Sheffield APD result under "the appeal" — it is a
fabricated, measured device rather than a calculated band structure, and it is the strongest
evidence in the review — and replace "the stakes" with the **dilute-window** point, since that is
what actually motivates the measurement problem rather than merely asserting it matters.

*If running long:* cut the strain paragraph to one clause — *"the same larger atom leaves the
crystal stretched, and that gets worse fast"* — and keep everything else. **Never cut the last
line**; it is the hinge into Aims.

---

## §2 — Aims & Objectives *(slide 4, 1:00)*

> "So the aim is to build a Monte Carlo framework for how these X-rays are generated, absorbed
> on the way out, and detected — **and to use it to find which X-ray lines give the most reliable
> bismuth measurement.**
>
> Four objectives. The first two are foundational: establish the material rationale — the strain
> and band-gap behaviour I just described — and model the specimen honestly, as a free-standing
> foil at a twenty-five degree take-off with no substrate underneath it.
>
> The second two are where the work is. **Characterise how the signal is attenuated** as the foil
> gets thicker and as the bismuth content changes — because absorption is what corrupts the
> ratios you measure. Then **sweep the whole parameter space in Python** and rank the line pairs
> on what survives.
>
> The thing worth saying about the last one is **why a simulation can answer it at all: the
> simulation knows the true composition.** Every recovered answer is graded against a ground
> truth the recovery never sees — which is exactly what you cannot do with a real specimen."

*That closing line is worth the seconds. It pre-empts the most likely marker question —
"why should I trust a simulation-only result?" — and it lands better volunteered than defended.*

---

## §A — Outline theory *(slide 5, 1:45)*

*Moved wholesale out of Methodology. This was landmarks ⑤a and ⑤b; it is theory, not method,
and the School's brief has a category for it. Nothing is lost — it is relabelled and it buys
back the slides Results & Discussion needs.*

> "Everything the simulation produces comes out clean. **No real detector produces that
> spectrum** — three things degrade it, and none of them are in the output file.
>
> Two of them are peaks landing on top of each other. I measured both against the detector's own
> resolution, because **two peaks closer together than the detector can separate stop being two
> peaks.**
>
> The first is a detector artefact. **Two X-rays arrive at the same instant and get recorded as
> one, carrying their combined energy.** Gallium's L line plus arsenic's L line adds up to
> almost exactly bismuth's M line — forty-three electron-volts apart, which no detector on earth
> separates. So every one of those coincidences **puts a fake bismuth count into the spectrum —
> it fakes the signal I'm measuring.**
>
> The second is arsenic's K-alpha sitting near bismuth's L-alpha. That pair is nearly four times
> further apart, and **is resolvable.** Different problems, so they get different treatment.
>
> And they differ in kind, which matters more than their size: **the sum peak is a bias —
> systematically wrong in one direction, and counting for longer never fixes it. The overlap is
> variance — noisier, but not wrong.**"

**Slide 5 carries:** the two pairs with their separations, the merged/resolvable verdict, and the
bias-vs-variance distinction. **fig04** belongs in Results, not here.

---

## §B — Methodology *(slides 6–8, 3:45)*

*Compressed from seven slides to three. ⑤a/⑤b moved to §A; ⑤c (the error budget) moved to
Results & Discussion, where it is a finding rather than a method. What remains is the three
things that are genuinely about how the work was done.*

### ⓵ Silent failure, and a gate that bites — *slide 6, 1:20*

> "The methodology here isn't 'I ran a Monte Carlo code' — running the code is the easy part.
> **The hard part is that almost every way of getting it wrong produces a result that looks
> completely normal.**
>
> Twenty-one simulations, six input files each. The lengths are in Ångströms, not nanometres —
> and **the manual says otherwise** — so a foil ten times too thin runs perfectly and tells you
> nothing is wrong. Composition is by weight, not by atom count. Density has to be set by hand or
> the code quietly invents one. **None of those throw an error.**
>
> So every generated input is checked character-by-character against a known-good reference. But a
> check that never fires might mean nothing is wrong — or might mean the check itself is broken,
> and you can't tell those apart by looking. **So I broke the inputs on purpose, one fault at a
> time** — the wrong units, the wrong kind of fraction, the density left blank, the misspelling
> tidied up, the line endings standardised. **Five faults, five caught.**"

*What was actually done (REPORT §5): each fault was injected by monkeypatch — **the real code was
never modified**, only the input, and only for the duration of the test. That distinction is the
whole point. Changing the code to make the check fail would be rewriting what counts as a fault;
sabotaging the input leaves the system under test untouched. The five: nanometres written into the
Ångström field; atomic fractions written into the weight-fraction field; the density field left at
zero; the `DetectorDiffusionLenght` misspelling "corrected"; line endings harmonised across all six
files. Three were caught on value, two on structure.*

*⚠ **If asked to show it:** the result is documented in REPORT §5 with each fault and how it
surfaced, but the injection script lived in a session scratchpad and was never promoted into
`tests/`. Say that plainly if pushed — the finding stands, the harness wasn't kept.*

### ⓶ Nothing invented — *slide 7, 1:00*

> "Every physical constant traces to a published source, or the code refuses to run.
>
> The one worth naming is density. Both this simulator and the standard alternative estimate it
> by **mixing the densities of the pure metals** — but this material isn't a mixture of metals,
> it's a bonded crystal, so that estimate is quietly the wrong physical picture and **nothing
> warns you.** **On Professor Walther's advice** I use his own measured endpoints and interpolate
> between them, which updates the values in his published paper."

*⚠ If Walther is not one of the two markers, invert this: lead with the physical reason, attribute
second. See the audience note in `PRESENTATION_CONCLUSIONS_DELIVERY.md`.*

### ⓷ The matrix grew because a measurement told it to — *slide 8, 1:10. This one is yours — slow down.*

*Rewritten 2026-08-25, twice. Figure-led — it is a spot-the-difference, which any technical
audience reads instantly with no background. **No numbers to recall**; the slide displays them.*

⚠ **Get the causality the right way round.** The third arm (Set C) was **not** added *because* of
this figure — **the third arm IS the second curve in this figure.** REPORT §23.1: Sets A and B
formed a cross, leaving the low-x/high-t corner empty; the assumption was that the corner could be
interpolated via ρ·t; **Set C was run specifically to test that assumption**, and the test failed
for gallium (−22.8% at 1024 nm) while nearly holding for arsenic (−1.6%). Saying "the figure
showed me I needed more runs" is circular — the plot cannot exist without those runs. The honest
line is *"I ran the corner instead of assuming it"*, which is the same move as proving the check
can fail before trusting that it passed.

> "My simulations started as a cross — one arm sweeping thickness, the other sweeping composition.
> That leaves one corner empty: **low bismuth and thick.** Which is exactly where the hard question
> lives.
>
> The convenient assumption is that you don't need to go there — that absorption depends only on
> how much material the X-rays cross, so the corner can be predicted from the arms. **I ran it
> instead of assuming it.** A third set of simulations, at one percent bismuth, across the whole
> thickness range — **and that's the second curve in each of these two panels.**
>
> **If the assumption held, that curve would sit on top of the first one.** On the right, for
> arsenic, it very nearly does. **On the left, for gallium, it doesn't.**
>
> So the third arm stays — the cross genuinely couldn't predict its own interior. And more useful
> than that: **arsenic is the element whose ratio follows thickness and almost nothing else.**
> That's what makes it the ruler you read the thickness off. **A measurement, not a preference.**"

*Held back for questions, not said aloud: the gap is **not** a density artefact — the density
offset stays constant while the error grows seventeen-fold with thickness. That is the obvious
counter-explanation and it is already ruled out, but it is defensive detail and it slows the beat.
Keep it in your pocket.*

**If running long:** cut ⓶ to one clause — *"every constant traces to a source, and the density
model is Professor Walther's own revision"* — and drop the second half of ⓷. **Never cut ⓵.**

---

## §3 — Results & Discussion *(slides 9–10, 4:00)*

*Every number below re-derived from `Aggregated\*.csv` on 2026-08-24 under production settings
(principal, absolute Δx = 0.01, m_band_factor 1.743). Slide 9 absorbs the parked ⑤c slide.*

### ⓵ What corrupts the measurement — *slide 9, 2:00*

**"Pile-up rate" — what it means, since the slide says it and you need to own it.** Pile-up is two
X-rays hitting the detector so close together in time that the electronics can't separate them, so
it records **one** event carrying their **combined** energy — a photon that was never emitted. A
"one-percent pile-up rate" means one in a hundred of the relevant events is one of these
coincidences. **It is not something the simulation knows or that you can look up** — it depends on
the instrument and how hard it is being driven. That is exactly why it was swept at 0.1, 1 and 10
percent rather than chosen. Saying "at a one-percent rate" out loud is naming *which assumption
these particular numbers came from*, which is what stops them looking like claims you can't support.

> "Two problems. They look similar and they behave completely differently.
>
> **First — the fake peak.** How often the doubling-up happens depends on the instrument, so I
> never picked a number. **At one-in-a-hundred, the fake counts come to about half the real
> bismuth M signal at one percent bismuth — and about two percent at twenty percent bismuth.**
> Same artefact, twenty-odd times worse at the low end.
>
> Why? The gallium and arsenic signals causing it are the loud ones. Bismuth's M signal is faint.
> **A small spill from a loud signal barely dents it and swamps the faint one.** In a dilute
> sample that loud signal is about a hundred times bigger; in a rich one, about five.
>
> **Second — counting.** At one percent bismuth I catch about a hundred bismuth photons in total.
> Count anything a hundred times and there's scatter in the answer.
>
> **And here's the difference that matters. Scatter averages out if you measure for longer. The
> fake counts don't — measure longer and you just get more of them.**
>
> **One is noise. The other is bias. Only one of them is curable.**"

**Slide 9 carries:** fig04; the 56% → 2% pair with the 23× callout; the 100× vs 5× loud/faint
explanation; 116 / 76 detected photons; the bias-vs-noise contrast. *Say the round numbers — "about
half", "a couple of percent", "about a hundred" — and let the slide carry the exact figures.*

### ⓶ What survives it — *slide 10, 2:00*

*Compressed and de-jargoned 2026-08-24. **Three points only**, and the only thing to memorise is
the three-line result at the end — the rest can be improvised. Budgeted at 2:00 for ~180 words,
which is deliberately slow: this is the section to take your time over, not race.*

> "Three problems, then — **two from this section, and the arsenic–bismuth overlap from the theory
> slide.** They come in different units; you can't compare a fake count against a photon count
> against a leak. So the last step **converts all three into the same thing: how wrong the final
> answer ends up.** Once everything's in that one unit, you can rank the lines against each other
> directly.
>
> The catch is that I don't know how big any of the three problems really are. **So I didn't
> choose values — I tried every plausible combination.** Twenty-seven of them, and on top of that
> sixteen different ways of modelling the fake peak. **The ranking came out identical every single
> time.** That's the whole point: the answer isn't resting on an assumption I picked.
>
> And the ranking is clean. **Bismuth's L line works across the entire composition range.
> Bismuth's K line works across part of it. Bismuth's M line never works.**
>
> One last thing. **Where the method runs out of data, the code says so instead of guessing.**
> That's the difference between a limit I measured and a limit I made up."

**Slide 10 carries:** the one-number framing; 27 scenarios and 16 combinations; the 27 / 9 / 0
result line; the doesn't-guess point.

*Removed from the spoken version: "incompatible units", "one currency", "switch combinations",
"route ordering", "refuses to extrapolate", and Δx notation. The slide still shows Δx = 0.01 with
its gloss; you don't need to say it.*

⚠ **Figures for slide 10 — none, or fig05.** Hold **fig03** for the verdict slide; spending it
here costs the payoff. fig06 was reviewed and corrected on 2026-08-24 (its title and caption
carried the retired "photon-starved" framing; both panels were threshold-independent so no
re-render was needed for correctness) — it is safe to use now, but it belongs to LO3's absorption
comparison rather than this slide.

⚠ **Two counts that look contradictory and are both correct.** "Bi M fails all 27" is measurability
**across the range**; fig03's caption says Bi M exceeds the bar in **18 of 27 at x = 0.01
specifically**. Same for Bi K — 18 of 27 across the range, 0 of 27 at x = 0.01. Never
"correct" one to match the other.

---

## §C — Conclusions & Future Work *(slides 11–13, 2:00)*

*Two slides, down from three. Lead with the answer — the methodology section deliberately
withheld it so this section could land it, and that promise pays off in the first fifteen
seconds. Do not rebuild the argument; you already earned it.*

### ⓵ The verdict and why it holds — *slides 11 and 12, 1:25*

*Slide 11 is the verdict alone — say it, then pause, then advance. Slide 12 is the three-column
"why it holds". The pause is the slide change; don't talk through it.*

> "So — the recommendation. **Bismuth's L-alpha line, measured against arsenic's K-alpha, using
> the single strongest line of each.** That pair measures bismuth reliably down to **an x of
> about one percent** — half a percent of the atoms — at the same acquisition time used in the
> paper this work builds on.
>
> *(pause)*
>
> It wins because the other candidates fail for reasons that don't go away.
>
> **Bismuth M fails on the sum peak** — the artefact that fakes counts directly onto the line
> you're reading. That's a bias: **counting for longer never fixes it.** It fails in all
> twenty-seven scenarios I swept.
>
> **Bismuth K fails on range.** It's genuinely the most absorption-immune line in the system, and
> at one percent bismuth it clears the target — but **it stops clearing partway up the range, in
> eighteen of twenty-seven scenarios.** You can't use a line that only works in a window whose
> edge you can't find without already knowing the answer. **Bismuth L never crosses, in any of
> the twenty-seven.**
>
> And it's robust three ways: it wins **under my accuracy target and under Professor Walther's
> published one**, **under both definitions of what counts as a line**, and **across the full
> thickness range, thirty-two nanometres to a micron.**"

⚠ **The "twelve times the acquisition time" line is retired** — it was computed against the 10%
relative threshold, which was scrapped on 21 August. Against Δx = 0.01 Bi K clears at the
*shortest* acquisition swept, so the claim is false. The range argument above replaces it, is
stronger, and needs no dose figure. **`SLIDES_CONCLUSIONS_BRIEF.md` slide 2 still carries the old
claim — fix it there too.**

### ⓶ Limitations & future work — *slide 13, 0:35. Forward-looking, not apologetic.*

**What the three items actually are, in plain terms:**

1. **The leak size is a range, not a measurement.** How much the arsenic peak bleeds into the
   bismuth peak isn't published anywhere. Rather than invent a value you tried everything from
   small to large, and **the recommendation holds even at the worst end.** Someone could measure it
   properly and turn your range into a fact.
2. **You know the floor is *at least* this low, not where it actually is.** The method works down
   to one percent bismuth because that's the lowest you simulated. It might work far lower — you
   haven't looked. Two more simulations would find the real floor.
3. **Two codes disagree about one bismuth line and nobody knows why.** Yours and your supervisor's
   differ by a consistent factor of about one and a half on the Bi M line. You have **measured that
   difference precisely** but can't explain it. It doesn't touch the recommendation, because Bi M
   isn't the line you're recommending.

**The framing:** this is not apologising. Each item is a specific, doable next piece of work rather
than a vague caveat, and the pattern across all three is the discipline running through the whole
project — **where you didn't know something, you said so and bounded it instead of inventing a
number.** This is the slide where that gets its credit.

*If pushed on item 3: state the number, say the cause is unidentified, and **stop.** Don't
speculate on a mechanism — one hypothesis has already turned out to be wrong.*

> "Three things I'd do next. **The overlap strength is swept, not measured** — the conclusion
> survives the worst case, but measuring it would replace an assumption with a number. **I know
> the method works down to one percent, but not where it stops** — two more simulations would
> bracket that floor. And there's **a discrepancy in the bismuth M data between two independent
> codes** that I've bounded but not explained.
>
> None of those touch the recommendation — but they're the honest next steps."

*Two further items are in `SLIDES_CONCLUSIONS_BRIEF.md` (Bi K's error bars past first order; the
untested detector window). Keep them in reserve for questions rather than on the slide — five
limitations in thirty-five seconds is a list, not a point.*

---

## Figure Q&A — if a marker asks about a plot

*Three figures are on screen long enough to be asked about. Each entry: what is plotted, what it
says, and the questions most likely to come.*

### fig02 — slide 8, the ρt figure

**Plotted:** two panels sharing an x-axis of **mass thickness ρt** (density × thickness). Each
panel is one element's **K/L intensity ratio**, with two curves — x = 0.20 and x = 0.01.

⚠ **The x = 0.01 curve is Set C** — the six extra runs. They were commissioned *to test* whether
the corner could be interpolated; this figure is the test's result, not its motivation.

**Says:** the title is the argument — *"if ρt determined absorption, each panel would show one
curve."* Left (Ga K/L) the curves separate, **−22.8%** at 1024 nm; right (As K/L) they nearly
coincide, **−1.6%**. So gallium's ratio carries composition information beyond what ρt explains,
and arsenic's does not. That does two jobs at once: it is why the cross matrix failed, and why
arsenic is the thickness ruler.

- *"How did you test it — where did the low-x curve come from?"* → **I ran it.** The original
  matrix was a cross and left that corner empty; rather than assume the corner could be
  interpolated, six more simulations were run at x = 0.01 across the full thickness range, and
  those are the second curve here. The frozen fifteen were verified untouched — every prior
  result's file came back byte-identical after re-aggregating (REPORT §23.2).
- *"Why plot against ρt, not thickness?"* → Absorption depends on the **mass** the X-ray crosses,
  not geometric distance. Against thickness the curves would separate trivially, because the two
  compositions have different densities. ρt removes that.
- *"Could the gap be an artefact of how you interpolated?"* → Checked two ways. Log-log
  interpolation gives the same answer (−23.1% vs −22.8%), so it is not a curvature artefact. And
  comparing at **identical thickness** instead — where the ρt offset is a constant −6.2% — the gap
  still grows from −1.5% to −26.3%. **A constant offset cannot produce a seventeen-fold growth.**
- *"What is the residual −1.6%?"* → Real but small — it is why the method still needs calibration
  rather than being exact.
- *"Why does gallium behave differently?"* → **Measured, not explained.** Explaining it needs
  cited mass attenuation coefficients this project does not hold. Say that and **stop** — an
  absorption-edge story would be inventing physics.

### fig04 — slide 9, the sum-peak figure

**Plotted:** x-axis is true Bi content. **Left** — fake counts as a percentage of the true Bi M
signal, at three assumed pile-up levels (0.1 / 1 / 10%); the dashed line at 100% marks *fake
counts equal the real signal*. **Right** — what a detector would actually record, the Bi L/M
ratio, against the clean simulated value in dotted grey.

**Says:** the same artefact is ~23× more damaging at x = 0.01 than at x = 0.20, and the right
panel is the consequence — at 10% pile-up the measured ratio is roughly halved at x = 0.01.

- *"Why three curves?"* → The pile-up rate is not knowable from this data, so it is swept over two
  orders of magnitude rather than assumed.
- *"What does the dashed line mean?"* → Above it the artefact contributes more counts than the
  real signal. At 10% pile-up that holds for everything below x ≈ 0.05.
- *"Why is the clean curve flat?"* → It is the simulated truth, unaffected by a detector artefact
  the simulation does not produce.

### fig03 — slide 11, the verdict figure

**Plotted, left:** total error on recovered x in **absolute composition units**, for the three Bi
shells, all referenced to As K so the *only* difference between the curves is which Bi line is
used. Dashed line at **0.01** is Walther's bar. Shaded bands are the spread across all **27
scenarios**. **Right:** the recommended route decomposed into its contributing mechanisms.

**Says:** Bi L sits lowest everywhere and its whole band stays under the bar. Bi K starts under it
and **crosses around x ≈ 0.1**. Bi M is above it throughout. And on the right — **the sum peak
contributes essentially nothing to the Bi L route**, four orders of magnitude below the others,
because it lands at 2.42 keV while Bi Lα is at 10.84 keV. What actually limits Bi L is counting
and the arsenic–bismuth overlap, and they are comparable.

**That right panel is the payoff of the whole project: the artefact this work was built to study
turns out not to limit the line being recommended.**

- *"Why do the curves rise with x?"* → It is **absolute** error. Roughly fixed relative precision
  means growing absolute error as x grows.
- *"Is the shaded band a confidence interval?"* → **No.** It is the range of answers the unknown
  assumptions permit — every combination of the three swept unknowns. A single line would be a
  claim the data cannot support.
- *"Bi K looks fine at low x — why reject it?"* → **Because it crosses partway up, and you would
  need to know x already to know whether you are inside its safe window.** Do not reach for photon
  starvation — that argument was retired with the 10% relative bar.

---

## Q&A — 5 minutes, the likely probes

Full bank in `PRESENTATION_METHODOLOGY_REFERENCE.md`. The four most likely:

**"Why Δx = 0.01 and not a percentage?"**
> Walther's own paper states it: measuring to 0.5 at% "or better is a real challenge." A flat
> relative target gets *harder* in absolute terms as x shrinks — it would bite hardest exactly in
> the low-bismuth regime this project added. The ranking is the same either way; I checked both
> and stored both.

**"Why should I trust a simulation-only result?"**
> Because the simulation knows the true answer. Every recovered composition is graded against a
> ground truth the recovery never sees — which is exactly what you can't do with real specimens,
> and it's why the error budget can be split by mechanism at all.

**"Isn't summing the lines what commercial software does?"**
> Yes, and it scores slightly better on paper. But summing pulls in extra lines that overlap
> *other* elements, and my model only costs one of those. Its apparent advantage is partly an
> uncosted risk — so I report the number I can fully defend, and the winner is the same either
> way.

**"Bi K is absorption-immune — isn't that worth pursuing?"**
> Physically yes, and that's the interesting half of the negative result. But it only clears the
> target across part of the composition range, and you'd have to know the composition to know
> whether you're inside it. Ruled out for this material at these thicknesses, not in principle.
