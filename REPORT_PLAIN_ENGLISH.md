# What happened in this session — plain English

*A companion to `REPORT.md`, which is the technical record. This one assumes no programming
knowledge. Same events, same conclusions, no jargon. Where the two disagree, `REPORT.md` is
the authority.*

---

## The job

MC X-Ray is the simulator. To make it run once, you have to hand it six settings files, and
it hands back a table of X-ray line intensities. Doing that ~24 times by hand is slow and
error-prone, so the plan is to automate it.

The automation was built up in stages. This report is chronological, so the sections below
start with the first two pieces and add the rest as they were built. As of the latest update,
the working chain is:

1. **The input generator** — writes the six settings files for one run.
2. **The output parser** — reads the results table back into something analysable.
3. **The executor** — presses "go" on the simulator (used to run all 15 production simulations).
4. **The matrix + aggregator** — defines the 15 runs and collates them into one table.
5. **The ratios** — turns the raw counts into the diagnostic thickness/composition ratios.

The two ends (generator + parser) came first because they had a strict "golden" test to prove
them correct; the rest followed as the project moved. Still to come: the sum-peak model (waiting
on a decision) and the final quantification, which is your own analysis, not automation.

*(The first sections below describe only the original two-ends build, because that is when they
were written. Keep reading for everything added since — the density work, the meeting, the
production runs, the aggregator, and the ratios.)*

---

## The problem this whole design exists to solve

MC X-Ray does not complain when you lie to it.

Tell it the foil is 100 units thick when it wanted a different unit, and it runs happily and
simulates a foil ten times too thin. Give it the wrong kind of composition number and it runs
happily and simulates a different alloy. Leave the density blank and it guesses — wrongly —
and says nothing. In every case you get a plausible-looking spectrum and no warning.

Ordinary testing cannot catch this, because there's no error to catch. So the check used here
is different: take a run that is *known* to have worked correctly, have the generator
reproduce its settings files, and then compare **every single character**. Any difference has
to be explained. Not "looks close enough" — explained, individually, or the check fails.

That known-good run is the **golden set**: the six files that were actually fed to the
simulator, plus the results it actually produced. Because the manual is known to be wrong in
places, those files — not the documentation — are the only trusted description of the format.

---

## What happened, in order

### 1. The first check stopped everything

Before writing code, I checked the golden set was complete. It wasn't — the results half was
missing. The file existed, but only in the live simulator folder, not in the project's
read-only copy. That's a halt condition by design, so I stopped and asked.

### 2. Reading the golden files raised four questions

While waiting, I read the six input files properly. Four things didn't match the brief:

- **The density was blank.** The brief said "never leave the density blank — the simulator
  will guess and guess wrong." The golden file, the supposedly-correct reference, had it
  blank. So the run everyone was treating as the trustworthy benchmark had the exact defect
  the project was most afraid of.
- **The composition numbers couldn't be reproduced.** Recalculating them from the atomic
  weights I'd been given gave answers that differed in the sixth decimal place. Not a
  rounding issue — no standard set of atomic weights produces the golden numbers.
- **The results file was from the wrong place** (the point above).
- **The run had two different names**, one for its inputs and one for its outputs, so
  "name it like the golden run" had two possible answers.

### 3. You re-ran the simulation

You confirmed the density problem was real and re-ran with the correct value, producing a new
golden set. You also settled the other three questions.

**This is the single most consequential thing that happened in the session.** Everything built
afterwards is checked against a reference that is now actually correct. Had the re-run not
happened, the automation would have been carefully, verifiably reproducing a mistake.

### 4. Re-checking the new golden set caught two more things

- **The results file was from the wrong run.** The settings echo had been copied from the old
  blank-density run rather than the corrected one. Harmless as it turned out — the two files
  are identical, because that file never records the density — but it was labelled as
  something it wasn't. You swapped it.
- **Two of the six files use different line endings from the other four**, contradicting the
  brief, the project notes, and the golden set's own README, all of which say they're
  uniform.

  The reason turned out to be mundane and provable: the file timestamps show four of them
  were written by you, and two are untouched files that shipped with the simulator. The
  simulator read both kinds happily in the same successful run. So this was never a real
  format rule — it was a fingerprint of which files had been opened in a Windows editor. The
  instruction to "make them all uniform" would have quietly altered two files that were
  supposed to be passed through untouched.

### 5. The build

The generator works by **copying the golden files and changing only what has to change** —
composition, density, thickness, run count, filenames. Every other line, including several
whose purpose nobody knows, is passed through untouched. This is deliberate: writing the
files from scratch based on the documentation would risk silently mangling settings, and the
documentation is known to be wrong.

The parser reads the results table back, handling its quirks (a stray comma at the end of
every line, stray spaces in the labels) and refusing to guess about anything it doesn't
understand.

Neither piece computes any physics. That's a firm rule, and there's a good reason for it:
several questions about the underlying atomic data are still open. Storing the raw numbers
means those questions can be answered later by recalculating — rather than by re-running two
days of simulations.

### 6. Checking that the check actually works

81 automated tests pass, and the character-by-character comparison comes out clean: eight
differences, every one accounted for.

But a passing test only proves the test passed. So I deliberately broke the generator five
times — introducing each known trap on purpose — to confirm the alarm actually sounds:

| Deliberate sabotage | Caught? |
|---|---|
| Wrong thickness unit (the 10× error) | yes |
| Wrong kind of composition number | yes |
| Density left blank | yes |
| A misspelled setting name "corrected" | yes |
| Line endings made uniform | yes |

Five out of five. The check protects; it doesn't merely pass.

That fourth one deserves a note: one setting name in the file format is *misspelled*. It has
to stay misspelled, because that's the spelling the simulator looks for. Fixing the typo
breaks the run.

---

## What was learned about the density mistake

The old run's density was about **15% too high**. Some plain-English detail on what that
means, since it's the scientific heart of the session:

**Why the simulator got it wrong.** Left blank, it estimates the alloy's density by averaging
the densities of pure gallium, pure arsenic and pure bismuth. That's a reasonable rule in
general and it's implemented correctly — it's just the wrong rule for a crystal. The paper
explains why: bismuth is much heavier than the arsenic it replaces, but it also pushes the
crystal lattice apart by almost the same proportion. Mass up, volume up, density barely
moves. Averaging the pure elements throws the lattice away entirely and lands 15% too high.

**How much it mattered.** More than expected in one way, less in another.

- Every individual line came out **15% too strong**. Denser foil, more atoms in the beam's
  path, more X-rays made.
- But your diagnostic ratios divide one line by another, and a uniform 15% on top and bottom
  cancels out. Measured on the real files, the ratios were only **1.3–3.2% wrong**.

So the raw numbers were badly off while the ratios looked nearly fine. Whether 1.3–3.2%
would have mattered for the final answer is your call — but it's a systematic bias, not
random noise, and it's a good argument for the rule that the pipeline stores raw numbers
rather than ratios. The ratio hid most of the damage.

**A number recovered from nowhere.** The simulator never reports which density it used — it
isn't in any output file. But comparing the two runs, every line's intensity changed by
*exactly* the same factor (1.152758, identical across eleven lines and three elements). That
uniformity is the fingerprint of a single cause scaling everything equally, which is what
density does. Working backwards gives the hidden value: **6.156 g/cm³**. That agrees with
your own estimate and independently supports your identification of the rule the simulator
used. It also confirms the simulation carries no meaningful random scatter at this setting —
random noise cannot reproduce a number to six digits eleven times over.

---

## The citation work

Late in the session you mentioned the density formula is your supervisor's derivation,
anchored on the paper. That exposed a genuine defect in my own work: the code credited the
**whole formula** to the published paper. It shouldn't have.

Checking against the paper, the split is:

- **Published**: exactly two numbers — the densities at x = 0.1 and x = 0.2. Quoted directly
  from the figure caption. These are now locked under test.
- **Derived locally**: everything else. The straight line drawn through those two points is
  your supervisor's work, not the paper's.
- **Not published at all**: the formula's starting value (at zero bismuth). That's the line
  extended past where the paper's evidence stops.

This matters for a dissertation, where crediting a paper with a step taken locally is a real
error even when the number is right.

It also surfaced a caveat worth knowing: the paper's two anchor points only cover the range
x = 0.1 to 0.2. **Set A sits exactly on one of them.** But three of Set B's four compositions
sit *below* that range, so their densities are extrapolated — the line extended beyond the
evidence. This is defensible, because the paper says the density barely changes, and the
numbers involved are negligible. But it is extrapolation and should be described that way.

---

## The final test: actually running the thing

Everything above compares the generated files against files that are *known* to have worked.
That's strong, but it isn't the same as proving the generated ones work. So the last step was
to hand them to the simulator for real.

**They ran, and reproduced the benchmark.** Same 21 lines, same energies, every number within
0.03%.

That 0.03% turned out to be worth chasing. Every line had shifted by roughly the same tiny
amount in the same direction, which is not what a composition difference looks like — so the
same settings were run a second time. The two runs disagreed with each other by about the
same amount. **The simulator is not perfectly repeatable**: run it twice with identical
settings and you get answers differing by ~0.04%. So the gap wasn't an error at all, it was
the simulator's own randomness. The benchmark's value actually falls *between* our two runs.

That also settles, for free, one of the outstanding questions on the list — whether the
simulator's random-number setting makes runs repeatable. It does not, at least at its current
value.

### The run that found a real bug

The first attempt to write the files where the simulator needs them **failed outright.** A
safety check I'd written to protect the read-only reference files was too aggressive: it
refused to write anywhere that contained the reference folder — and because this project
lives *inside* the simulator's folder, that included the one place the files actually have to
go.

It would have blocked the next stage entirely. All 81 tests had passed, because every one of
them wrote to a scratch folder and none had ever tried the real destination. This is exactly
what you wanted the loop closed for: nothing was wrong with the physics, but something *was*
wrong, and only running it for real could have found it.

Fixed, with two new tests that would catch it again.

### Testing the corners

The benchmark sits in the middle of your planned experiments. The extremes had never been
tried, so four more runs went through: the thinnest foil (2 nm), the thickest (1024 nm), and
the lowest bismuth content (0.02% of the arsenic sites). All ran cleanly.

These gave an independent check on the most dangerous conversion in the project — the one
where a thickness in the wrong unit runs happily and silently simulates a foil ten times too
thin. The check works like this: a foil fifty times thinner should emit about fifty times
fewer X-rays. Measured against the already-verified 100 nm foil, the 2 nm foil came out at
**0.0199 of it — essentially exactly the 0.02 expected.** Had the unit been wrong, it would
have been 0.002. The trap would have been unmissable, and it isn't there.

The rest behaved as physics says it should: absorption climbs steeply with thickness (the
softest line escapes 99.7% of the time at 2 nm, but only 34% at 1024 nm, while the hardest
line barely notices); and the bismuth signal at the lowest composition came out within 0.25%
of what its concentration and density predict.

One mild surprise, which turned out to be correct: the thickest foil emits about 3% *more*
than a straight scaling predicts. That's real — in a thicker foil electrons bounce around and
travel further than the foil is deep, so they meet more atoms than the thickness alone
suggests. Walther reports the same effect in his own curves.

### One number worth your attention tomorrow

At the lowest bismuth content you plan to simulate, **the strongest bismuth line produces
about 2 photons.** Roughly 20 even at the full production setting.

That is not a problem with the code — it's the physics of having almost no bismuth present.
But it lands squarely on a decision already on your list: whether to run every simulation at
the same dose, or to crank the low-bismuth runs up until the counting statistics stop being
the limiting factor. There's now a concrete number attached to that choice.

One subtlety that matters for how you read it: the simulator does not seem to model counting
noise the way a real detector experiences it — it reports a low-scatter *expected* value. So
it can tell you "2.3 photons" far more precisely than any real instrument could ever measure
2.3 photons. Whether your question is about *this measurement* or about *the underlying
physics* is exactly what that decision has to resolve, and it's yours to make.

---

## Chasing the density number back to its source

*This came after everything above, and it's the most significant open item in the project.*

### Why look again

The density formula in use is ρ(x) = 5.32 + 0.20x. Two points on that line — the densities at
10% and 20% bismuth — are quoted directly from the paper's figure captions. The line drawn
through them was your supervisor's step, not the paper's.

But the paper describes doing something more specific than drawing a line. It says the
densities were worked out from *standard atomic weights and the lattice parameter estimates
from Ref. (2)*. That's a calculation from measured crystal data — which means it can be
reproduced independently, and checked.

You supplied that reference: Tixier et al. (2003), the paper that measured how the GaAsBi
crystal expands as bismuth is added.

### How the check works

The density of a crystal is just its mass divided by its volume, and for this crystal type
both are known exactly if you know two things: the weight of the atoms, and the size of the
repeating cube (the "lattice parameter") they sit in. Add bismuth and two things happen at
once — the cell gets heavier, and it gets bigger. Whether the density rises or falls depends
entirely on which effect wins.

The paper's claim is that they roughly cancel: *"the mass increase … increases the unit cell
volume almost in the same proportion"*, so density barely changes. That's a testable claim.

**First, a check that the method itself is sound.** Applied to plain GaAs with no bismuth at
all, it has no adjustable knobs and must return the known density of GaAs. It returns 5.3176
against an accepted 5.3176 — exact. So the machinery works.

### Two things the Tixier paper settles

I had two worries about whether I was using their number correctly. Their full text answers
both, in one sentence:

- Their crystals were grown squashed onto a GaAs base, which distorts the cube and would give
  a misleading number. **They corrected for this** and report the value for a *free-standing*
  crystal. That is exactly what you're simulating — a foil floating in vacuum — so it's the
  right number.
- They confirm the expansion follows a **straight line** with bismuth content, so interpolating
  linearly between their endpoints is what their data supports, not an assumption I imposed.

### The result

Working the calculation through with their measured expansion:

| bismuth content | paper's density | from the crystal data | difference |
|---|---|---|---|
| x = 0.1 | 5.34 | **5.61** | +5.0% |
| x = 0.2 | 5.36 | **5.87** | +9.5% |

**The two don't agree.** And it isn't sensitive to which measurement you trust — there are
three published values for the endpoint (one measured, one from theory, one from a different
growth method) and all three give the same answer. The lowest of them makes the gap *wider*,
not narrower. To get the paper's numbers you'd need the crystal to expand about 15% more than
anyone has ever measured.

### What's actually going on

It isn't a rounding slip; the whole trend is too shallow. Testing the paper's own reasoning at
its own worked example (a quarter of the arsenic replaced by bismuth):

- the cell gets **23% heavier**
- the cell gets **9% bigger**

Those were supposed to be about equal. They differ by a factor of two and a half. Bismuth is
nearly three times the weight of the arsenic it replaces, and the crystal simply doesn't
stretch enough to absorb that. So density climbs by about 13%, where the paper expects it to
stay flat.

The upshot: the formula's rate of change is roughly **14 times too shallow**. Both versions
agree when there's almost no bismuth — which is why this is invisible at the low end and worst
at the high end.

### What it costs you

| | density difference | effect on your diagnostic ratios |
|---|---|---|
| **Set A — every run** (20% Bi) | 9.5% | **0.9–2.2%** |
| **Set B, first point** (20% Bi) | 9.5% | **0.9–2.2%** |
| validation run (10% Bi) | 5.0% | 0.5–1.2% |
| Set B, second point (2% Bi) | 1.0% | 0.1–0.2% |
| Set B, lowest two (0.2%, 0.02% Bi) | under 0.1% | nothing |

**Only Set B's three lower compositions are genuinely safe** — the two formulas converge as
the bismuth content goes to zero. Everything at 20% bismuth carries the full discrepancy, and
that includes all of Set A plus the top of Set B. It's a consistent bias, not random scatter.

For scale: this is about half the size of the density error you already caught and fixed, and
roughly a tenth of the sum-peak effect the paper is mainly about. Real, but not catastrophic.

### Nothing has been changed

The code still uses the paper's values, and the tests still lock them in place. **No code was
altered on the strength of this** — choosing a density model is a scientific decision, not a
mechanical one, so it stays with you. The full working is in a scratch file outside the
project.

Three ways forward:

1. **Keep the paper's values.** Your simulations then match his conditions, so if your curves
   disagree with his, it's because of what you changed, not the density. But you'd knowingly
   be using a density his own source contradicts.
2. **Switch to the crystal-data values.** Physically defensible and traceable to primary
   sources — but your curves will then differ from his published ones for a reason that has
   nothing to do with the question you're asking.
3. **Run both.** About 80 minutes of computing. Turns the uncertainty into a measured number,
   and because the pipeline stores raw counts, nothing needs re-simulating later.

**Current plan (19 July 2026): run both.**

### The loose end, and an honest correction *(closed 19 July)*

The size of the plain GaAs cube — 5.65325 Å — was the last number in this chain that I'd
supplied from general knowledge rather than read in a document. It is now sourced: the Ioffe
semiconductor database gives exactly that value, and Blakemore's 1982 review of GaAs
properties is the citation to use in the write-up.

**Worth recording how weak my original check on it was.** I'd said the number "validates
because it reproduces the known GaAs density exactly." But *that* density figure had also come
from my own recollection — so I was really only showing that two remembered numbers agree with
each other. Reference tables list them side by side, so a pair that was wrong together would
have sailed through. The check was worth something (it would have caught a mistyped digit) but
much less than I implied at the time. It stands up now because the value has a source behind
it, not because of that check.

**A useful by-product.** The database gives GaAs a density of 5.32 g cm⁻³ — which is exactly
where the paper's formula starts. So the formula is anchored correctly at zero bismuth; it's
only the *rate of increase* that's wrong. That's a cleaner way to put the problem than "the
formula is wrong": the starting point is right, the trend is 14 times too shallow.

---

## The objectives document changed the plan

*Read from your Aims & Objectives form, after everything above.*

Two numbers in LO4 mattered. One was already right; the other wasn't.

**Already right:** 200 kV, the 25° detector angle, the free-standing foil with no substrate,
and the ten thicknesses doubling from 2 to 1024 nm. All of that matches what the code does.

**Not right:** LO4 sets the bismuth range at **1% to 20%**. The old composition sweep went
down to 0.02% — fifty times below the floor. Two of its four runs were outside the objectives
entirely.

### The composition sweep, rebuilt

| | old | new |
|---|---|---|
| bismuth values | 20%, 2%, 0.2%, 0.02% | **1%, 2%, 5%, 10%, 20%** |
| runs | 4 | 5 |

Three reasons for those five: they cover the stated range, they're round enough to read in a
write-up, and **10% is the composition of the validation run**. So one point of the sweep
re-runs the already-verified benchmark configuration at full production settings — a free
consistency check the plan didn't have anywhere before.

### The windowless runs may not be needed at all

The plan had every thickness run twice — once with the detector window, once without —
doubling that arm from 10 runs to 20. But LO4 says the sweep varies **thickness and bismuth
concentration**. Two things. The window isn't mentioned anywhere in the objectives.

If that's right, the thickness arm is 10 runs rather than 20, and the unresolved question of
whether "windowless" can even be set stops blocking anything — it becomes optional extra
work. Worth confirming with Walther, but the document is clear as written.

### One worry that went away

The earlier concern about ~2 photons at the lowest bismuth content assumed a floor of 0.02%.
At the new floor of 1% there's about fifty times more bismuth: roughly **114 photons at the
test setting, ~1,140 at full production**. Comfortable. The question of whether to run
low-bismuth cases harder is now much less pressing.

### The plan, frozen

| arm | fixed | varied | runs |
|---|---|---|---|
| thickness arm | 20% bismuth | 2 → 1024 nm, ten values | 10 |
| composition arm | 100 nm | 1% → 20% bismuth, five values | 5 |
| | | **per density model** | **15** |
| | | **× 2 models** | **30** |

Roughly 100 minutes of computing, probably more — thick foils are slower.

---

## Both density models are now built

You decided to run both rather than pick one, so the code now takes the density model as a
setting per run: either the paper's values or the ones computed from crystal data. The
paper's version stays the default, so nothing that already worked has changed.

Choosing wrongly would be a silent 9.5% error, so the code refuses an unrecognised name
rather than quietly falling back to either.

### The atomic weights are now sourced too

You pulled me up on these before I built the new model, which was the right call — they feed
both the composition numbers *and* the new density calculation, so they'd have propagated
everywhere.

They're now checked against IUPAC's official 2024 table. Two of the three were already exact;
arsenic was very slightly rounded, and the difference is 0.07 parts per million — far too
small to change any number the simulation ever sees. Corrected anyway, since there's no
reason to keep a rounded value when the real one is a lookup away.

**That was the last uncited number in the code.** Every physical constant now traces to a
published source.

It also settled an old loose end. The golden reference file's composition numbers differ from
ours in the sixth decimal, and until now "someone mistyped them" was just the only explanation
left. With the official uncertainties in hand it can be shown properly: the gallium difference
is within what the uncertainty allows, but the bismuth difference is about a thousand times
too large for any real atomic-weight table to produce. So it genuinely is a transcription
slip, and now that's demonstrated rather than assumed.

### A test that immediately paid for itself

I wrote one test that recalculates the density from scratch, deliberately not reusing the
code's own logic. It failed on the first run — and the failure was in *my expected value in a
different test*, not in the code. Had I only written tests that reused the same logic, two of
them would have quietly agreed on a wrong number.

94 tests now pass, and the original golden check still comes out clean.

---

## The 30 runs — done, and one big surprise

All 30 finished in 99 minutes with no failures. The thickness arm and composition arm, each
run twice: once with the paper's densities, once with the ones computed from crystal data.

### First, the good news: the physics is right

The core prediction of the whole method is that the line ratios must rise steadily as the
foil gets thicker — that's what makes them usable as a thickness gauge. They do, at every one
of the ten thicknesses, under both density models. That's the curve that reproduces Walther's
Figure 1, and it came out the right shape.

### The surprise: the density choice matters far more at thick foils

I'd told you the two density models would differ by about 1–2%. That was measured at 100 nm,
and it's true at 100 nm. As a general statement it was wrong:

| foil thickness | difference between the two models |
|---|---|
| 2 nm | none at all |
| 32 nm | 0.3–0.7% |
| 128 nm | 1.0–2.6% |
| 512 nm | 3.4–7.0% |
| **1024 nm** | **5.6–8.4%** |

The reason is straightforward once seen. Absorption depends on density **multiplied by
thickness** — how much *stuff* the X-ray has to cross, not how tightly packed it is. In a 2 nm
foil almost nothing is absorbed whichever density you assume, so the choice is irrelevant. In
a 1024 nm foil absorption dominates, and the full 9.5% density disagreement comes through.

Your thickness arm spans that entire range, so the density question goes from "doesn't matter
at all" to "matters a lot" depending where you are on the curve.

### What that actually costs: a 9% error in measured thickness

This is the part worth taking to the meeting. Your method works by reading a measured ratio
off the curve to find out how thick the foil is. Do that with each model:

| measured Ga K/L ratio | paper's density says | crystal data says | difference |
|---|---|---|---|
| 1.5472 | 128 nm | 117 nm | −8.9% |
| 2.3559 | 512 nm | 465 nm | −9.2% |
| 3.6587 | 1024 nm | 930 nm | −9.2% |

A consistent ~9% — essentially the density disagreement itself.

There's a clean reason for that, and it's the important insight. **The ratio doesn't actually
measure thickness. It measures how much material is in the way** — density times thickness,
together. To get thickness out you have to divide by the density, so whatever error is in the
density passes straight through into the answer.

This is where the method's famous self-correcting property runs out. The k\* approach is
specifically built to shrug off errors in detector sensitivity and overall scale, because
those cancel when you take a ratio. **A density error doesn't cancel** — it's not a scale
error, it's baked into the conversion.

Whether that 9% survives into your final bismuth number is a separate question, and it may
largely cancel out when you calibrate and invert using the same curves. That's your analysis
to do — but it can no longer be assumed away.

### A correction: I was wrong about the photon counts

I told you that running at full production settings would give ten times more photons —
"~1,140 instead of ~114". **That was wrong**, and the runs proved it.

The same configuration at ten times the simulation effort gives *identical* numbers
(10150 versus 10154 — a 0.04% difference). The measured value at 1% bismuth was 115.7, not
~1,140.

Here's why, which I traced through the simulator's own settings file. Those photon numbers
aren't raw tallies — they're the count you'd expect from a **specific experiment**: a
100-second exposure at 1 nanoamp of beam current, both fixed in the settings. That works out
to 6.2×10¹¹ real electrons, and multiplying through reproduces the reported figure exactly.

So two things I'd been treating as one:

- **Number of simulated trajectories** — how carefully the computer estimates the answer.
- **Beam current × exposure time** — the actual experiment being simulated, which is what sets
  the photon counts.

**Three consequences worth knowing:**

1. The simulator gives you a very precise *expected* value. A real detector measuring 115
   counts would see random scatter of about ±11, roughly **9%**. If you want realistic
   measurement error in your analysis, you have to add that noise yourself — the simulator
   won't.
2. **Running more trajectories cannot improve your counting statistics.** Only a longer
   exposure or a stronger beam can. That reframes the earlier "should low-bismuth runs get
   more effort?" question entirely — it's about exposure settings, not simulation effort.
3. Those two exposure settings were inherited from the original benchmark file and have never
   been consciously chosen. They're not on the project's list of locked parameters, yet they
   directly set every photon count you'll quote. Probably worth a deliberate decision.

---

## The supervisor meeting cleared up a lot — and changed three things

Dr Walther went through the open questions. Several are now settled, and three of his answers
made the 30 comparison runs out of date, so they've been re-run. (Worth noting: "Thomas" and
"Dr Walther" are the same person — so where earlier notes talked about his paper's values
versus his guidance, that's simply him correcting his own earlier numbers.)

### Settled cleanly

- **The windowless idea is dead.** He checked the software himself: you can change the
  detector material but there's no way to specify a window, and his suggested workaround
  doesn't work either. This confirms what the files already told us, and it halves the
  thickness arm to 10 runs for good.
- **We're using the right simulator.** His published curves came from a different program
  (CASINO), which made me worry about comparing across two tools. But it turns out CASINO
  *can't* do the detailed X-ray lines or detector modelling this project needs — MC X-Ray can.
  So using MC X-Ray isn't a compromise, it's the correct choice. The worry inverts into a
  justification.

### The three things that changed

**1. A new density formula.** He explained that both simulators get compound densities wrong
for the same underlying reason (they blend the pure *metal* densities, but this crystal isn't
metallic). His fix: use 5.32 for pure GaAs, 7.18 for hypothetical pure GaBi, and draw a
straight line between them. That gives densities a bit higher than his old paper values and a
bit lower than the crystal-data ones I'd computed — it sits between the two sets we ran, so
neither of the 30 runs used it.

**2. A thicker detector.** He specified the exact detector crystal thickness (0.5 cm for the
type his paper used); ours was 0.3. This mainly affects how well the very high-energy bismuth
lines are caught — and a quick test confirmed it: the detector's efficiency for the hardest
bismuth line jumped from 15% to 24% with the thicker crystal.

**3. More electrons for thin foils.** The thinnest foils have so little material that the
simulation doesn't gather enough X-rays to be statistically precise. He asked for ten times
more electrons on those. Checking the actual numbers, the four thinnest foils (2–16 nm) fall
short, so they now run at ten million electrons instead of one million; the rest are fine as
they were.

### An honest correction

Point 3 above means I owe you a correction. I'd told you "running more electrons can't improve
the counting statistics." That was wrong, because there are two different kinds of noise and I
mixed them up:

- **How precisely the simulation estimates its answer** — this *does* improve with more
  electrons. It's what Dr Walther was talking about, and our thin foils were under-sampled.
- **The random noise a real detector would see** — this is set by beam current and exposure
  time, not by the simulation. This is the part I was right about.

The reported numbers don't change with more electrons (that bit was right); their *precision*
does.

### The most reassuring thing he said

He told me not to worry about the density being ~1% out, because the k-factor method is
self-correcting for it. This directly answers the big worry from the 30 runs — the ~9%
disagreement in inferred thickness between density models. Because you calibrate and invert
using the *same* density assumption, most of that error cancels out. So we pick the right
density for correctness, but the exact value barely affects the final answer. (This only
applies to *systematic* offsets like density — it doesn't help with random simulation noise,
which is why the thin-foil electron count still matters.)

### What was done

The code was updated: the new density formula is now the production default, the detector is
set to 0.5 cm, and thin foils run at ten million electrons. The old golden benchmark still
reproduces exactly (it deliberately uses the old settings, since that's what made it). 95
tests pass.

Then the 15 production runs were re-run with all three corrections, and **finished cleanly** —
just over two hours, no failures. The four thinnest foils at ten million electrons took about
22 minutes each and accounted for most of that time. The results check out: the thickness-arm
curves rise steadily as they should, the composition arm scales correctly, and every output
file is complete. **This is now the real dataset** — everything before it was groundwork to get
here.

One genuine finding came out of the lowest-bismuth run. The simulation itself is precise there,
but because bismuth is only 1% of the alloy, its X-ray lines are faint — a real detector would
struggle to measure them to better than about 14% at these settings. That isn't a fault to fix;
it's exactly the "how low can you go" limit the composition arm is designed to find, and it's a
result to report. (And notably, running more electrons wouldn't help — that noise is physical,
from having so little bismuth, not a simulation shortcoming.)

---

## Collating the 15 runs into one dataset (Stage 5)

With the runs done, the next piece was built: something that gathers all 15 into a single,
analysable dataset. Think of it as collating 15 separate exam papers into one gradebook, with
a cover sheet proving whose paper is whose.

It produces two files, in a new `Aggregated` folder:

- **One combined table** — every X-ray line from every run in a single spreadsheet, 315 rows in
  all. Each row also carries *what that run was* (its bismuth level, thickness, density) sitting
  right beside the numbers, so you can plot "signal versus thickness" straight away without
  cross-referencing anything. This is the table your final analysis works from.
- **A cover sheet** — one entry per run, recording its settings and pointing at the exact files
  that produced it. If you ever need to ask "where did this number come from?", it traces back.

Two things it does deliberately, both following the project's rules:

- **It stores raw numbers only** — no ratios or corrections. Those come later, computed *from*
  this table. The reason: some questions about the atomic data are still open, so anything
  derived might need recomputing — and you want to recompute from a stored table, never by
  re-running two hours of simulations. There's even a test that fails if a ratio sneaks in.
- **It checks its own paperwork.** For each run it re-opens the actual input file and confirms
  it matches what that run claims to be. If a file were mislabelled, it refuses to build rather
  than quietly corrupt your dataset.

With this done, the whole "run the simulations and store the results" half of the project is
complete from end to end. The combined table is the clean handoff into your analysis — including
the key test of whether Dr Walther's "the density barely matters, the k-factors cancel it out"
claim actually holds when you work the numbers through.

---

## Turning the raw numbers into the diagnostic (Stage 6, first half)

The stored table is just raw X-ray counts. This step turns them into the actual *diagnostic* —
the ratios that reveal thickness and, ultimately, bismuth content.

The idea: low-energy X-rays get absorbed inside the foil far more than high-energy ones. So for
each element, dividing its high-energy line by its low-energy line gives a number that grows
with thickness. Three of these are computed — gallium high/low, arsenic high/low, bismuth
mid/low — which together reproduce the calibration curves from Walther's paper. Encouragingly,
all of them rise smoothly with thickness exactly as they should.

**One real decision came up here, and you made it.** An element's "high-energy lines" is
actually a small family of lines, not one. So "the K signal" could mean just the single
strongest line, or the sum of the whole family — and the two give answers ~40–90% apart, so it
genuinely matters. Rather than pick prematurely, we compute **both** and store them side by
side, leaving the choice for the final analysis. It fits the project's habit of storing
everything and deciding late.

The result is a small table — 15 rows, one per run, six ratio columns — ready to plot and to
feed the final quantification.

**The harder half of this step is still on hold.** The bismuth measurement's biggest enemy is
the "sum peak" — two other X-rays arriving together and being mistaken for bismuth. Modelling
that is the other half of this stage, and it waits on an unresolved question about whether the
simulator produces those fake peaks itself. Until that's settled, building it would risk
double-counting. It's the one piece that bears directly on how low a bismuth level you can
actually measure.

---

## Where things stand

**Done and checked:** both pieces built, 94 tests passing, character-by-character comparison
clean, the alarm proven to work, the golden set proven untouched, and — the important one —
files this code produced have been fed to the real simulator and reproduce the benchmark to
within its own noise.

**Waiting on you:**

- **Go-ahead to run all 30.** Everything is built and frozen; nothing is blocking except
  your say-so and the naming question below.
- **How the runs should be named.** I've proposed encoding the density into each filename
  (`GaAsBi_100nm_x020_rho536` versus `..._rho587`), since around 570 output files will land
  in one flat folder and being able to read the density off the name will matter. That stem
  is permanent provenance, so it should be your choice rather than mine.
- **Confirm what your supervisor actually did.** The code says their contribution was "the
  straight line through the two published points". I inferred that from the arithmetic — the
  line through those two points *is* exactly the formula — but nothing states it. If they did
  something else, the credit is still misdescribed. Now easier to ask, since you can also put
  the density discrepancy to him directly.
- *(Closed)* ~~Which density model to use~~ — you chose both, and both are built.
- *(Closed)* ~~The atomic weights are uncited~~ — now sourced from IUPAC's 2024 table.

**Three notes for the project documentation**, which now contradicts the files in three places:
the line-endings claim, the density formula's attribution, and a reference to an archive
folder that doesn't exist. (The old run's *results* survive in the live folder, so nothing is
lost — but its *inputs* are gone, because that file was edited in place.)

**Deliberately untouched:** the three hands-on experiments still pending, the two questions
out to the software's author, and the question to your supervisor. Where the code runs into
any of them it stops with a clear error rather than guessing.

---

## What was *not* checked

The most important section here, because silence can be mistaken for a clean bill of health.

- **Only the benchmark point has a known-correct answer to be judged against.** The corner
  runs show the simulator accepts them and that the physics scales sensibly — but there is no
  independent answer at 2 nm, 1024 nm or the lowest bismuth content to check them against.
  They demonstrate the generator is self-consistent and behaves plausibly across the range,
  not that those numbers are right in any absolute sense.
- **The density numbers came from your transcription of the paper**, not from me reading the
  PDF. My attempt to extract the text got the words but not the numerals, and I didn't
  install extra software to finish the job without asking.
- *(Closed)* ~~No simulation has yet used the crystal-data densities~~ — 15 such runs are
  now done and came out sane.
- *(Closed)* ~~The ~114-photon figure is calculated, not measured~~ — measured at 115.7. But
  my companion claim that production settings would give ~1,140 was **wrong**; see the
  correction above.
- **The final bismuth number has not been worked out under either density model.** We know
  the two models disagree by ~9% on *thickness*. Whether that carries through to the
  composition you finally report is untested — and that calculation is yours.
- **None of this has been compared against Walther's published curves.** His came from a
  different simulator (CASINO), and the outstanding questions about which X-ray lines are
  bundled together mean a like-for-like comparison isn't possible yet.
- **Only the ends and the middle were run.** Three of your ten thicknesses and two of your
  four compositions. The points in between are inference, not observation.
- **The windowless configuration has never been exercised**, by design — the code refuses it
  rather than guessing, because whether it's even possible is still an open question.

---

## Moving into the analysis phase: can bismuth content actually be measured? (Stage 7)

*This section is a walkthrough of one working session, not a finished chapter. It's left
open-ended on purpose — the plan, the mistakes, and the results below will keep growing as
the work continues.*

### The plan

Everything up to here built the machine that runs simulations and stores results. This session
started the next phase: using those stored results to actually answer the dissertation's
question — can you work out how much bismuth is in a sample just from how bright its X-ray
lines are?

The tool for doing that is something called a **k-factor**: a conversion number that turns a
brightness comparison between two elements' X-ray signals into a composition estimate. Your
supervisor's paper extends the classic version of this into a **thickness-aware** version
(written k\*), because thicker samples absorb more of their own signal before it escapes, which
throws off the simple version.

The plan going in had two parts:

1. Work out how well this k\* approach actually holds up, using your own simulated data —
   which has a big advantage your supervisor's real experimental data doesn't: you already
   know the true bismuth content of every sample, because you told the simulator what to
   build. His real sample's true composition was something he had to *infer*, not something
   he actually knew.
2. Send your supervisor a short, sharp question about one genuine ambiguity in his paper
   before building anything that depended on the answer.

### Bump 1: nearly building the wrong check

Early on, there was a real risk of building a test that would look convincing without proving
anything. If you calibrate a tool using a sample and then test it on *that same sample*, of
course it comes back right — you haven't learned anything. The fix was to split your 15
simulated samples into two separate batches: one batch (ten samples, same bismuth level,
different thicknesses) used only to build the tool, and a second, separate batch (five samples,
same thickness, different bismuth levels) held back and used only to check whether the tool —
built without ever seeing them — could correctly guess their composition.

### Bump 2: a currency question that looked like it would block everything, then didn't

Your supervisor's equations use a term he only defines once, in five words, as "atomic
densities" — but the type of calculation it sits inside normally uses something else
("atomic weight," a plain periodic-table number), and those two things give meaningfully
different answers. First instinct was that this had to be pinned down before anything else
could be trusted.

Working through the actual algebra properly showed that instinct was wrong, in a useful way:
because the tool gets calibrated and then applied using the *same* assumed number both times,
that number cancels itself out completely, regardless of what it's worth — as long as it's used
consistently. So the ambiguity turned out not to block the real test at all. It still matters
for one thing: making sure the final number you report is traceable to a specific, citable
definition rather than an arbitrary one — which is the actual reason a short email went to your
supervisor, not because the work was stuck waiting on it.

### Bump 3: trying to check a number from before this session, and not being able to

You mentioned having worked out, in an earlier session, that getting this currency question
wrong shifts recovered bismuth content by about six percentage points — a number worth putting
in the email as evidence the ambiguity has real consequences. Trying to track down exactly how
that number was calculated turned up a file with your supervisor's raw published numbers in it,
but no record of the actual calculation. Redoing a version of it by hand landed close to your
number, but didn't cleanly reproduce your supervisor's own published answer for that same case —
which suggests his real method is more layered than the simple version either of us used.
Rather than quietly patch over that gap, it seemed more honest to say plainly: the six-point
figure is plausible and worth keeping in the email, but not independently verified end to end.

### What got built

Two small, tested pieces of code, following the same house rules as everything before them
(nothing invented without a source, nothing derived that can't be recomputed from stored data
without re-running the simulator, every claim backed by a test that fails loudly if it stops
being true):

- **One that works out k\* for all twelve useful line-pair combinations**, directly from the
  known truth in each simulated sample — no need to separately model how much signal gets
  absorbed inside the foil, because the simulator's own output already carries that
  information.
- **One that runs the actual held-out check**: build the tool from the ten-sample batch only,
  then use it to guess the composition of each of the five held-back samples, *without* letting
  the guessing step see their real answer — that real answer only gets used afterward, to grade
  the guess. There's a specific test whose entire job is to catch it if that rule is ever
  accidentally broken.

### What it found, so far

Run against your real 15 simulated samples, the held-out check gave a genuinely readable
result:

- Recovery is excellent near the sample the tool was built around (20% bismuth) — off by about
  a twentieth of a percentage point.
- It gets steadily less accurate the further away you test it — down at 1% bismuth, the
  average estimate is off by around three-quarters of a percentage point.
- The more interesting finding is *which* estimates drive that error. The combinations that
  look directly at bismuth's own X-ray signal stay accurate even at the lowest bismuth level.
  The one combination that has to *infer* bismuth indirectly — by noticing how it very slightly
  disturbs the gallium-to-arsenic balance — is far less reliable at low bismuth, and one version
  of it even comes back with an impossible negative composition.

That pattern makes physical sense (a direct, if faint, signal beats a very small indirect
disturbance), and it looks like exactly the kind of finding a dissertation result is built
around — but that reading is yours to make, not something settled here.

### Where this leaves things

Nothing here is a verdict. The email to your supervisor is out; his reply isn't needed to keep
going, but it will matter for how the final numbers get reported and for comparing against his
own published figures. The two batches used so far only cover one thickness's worth of held-out
testing (100nm) — whether the same pattern holds at other thicknesses hasn't been checked yet.
And the currency question, while no longer blocking, is still formally open until he answers.

---

# Catching up: 3–15 August

*This file went quiet on 3 August while the technical record kept going. Nine sections' worth of
work happened in that gap, including most of the results that actually matter. This part closes
it.*

---

## The conversion table, and a question that finally got answered

The k-factor calculation was finished and run across all ten thickness samples. That produced a
table of conversion numbers — one for every combination of which bismuth X-ray line you compare
against which gallium or arsenic line, under two different ways of defining "how bright is this
line". Two hundred and forty numbers in total.

The interesting thing wasn't the size of the table. It was that the numbers split into two
completely different families.

Some comparisons barely change no matter how thick the sample gets — one of them shifts by less
than 1% while the sample gets **512 times thicker**. Others collapse: one falls to a fifth of its
starting value over the same range. The pattern turned out to be simple once you saw it. X-rays
come in "hard" (high energy, penetrating) and "soft" (low energy, easily absorbed). Comparisons
between two hard lines are stable, because neither gets absorbed much on the way out. Any
comparison involving a soft line falls apart, because the thicker the sample, the more of that
soft line gets swallowed before it escapes.

**And the currency question got its answer.** Your supervisor confirmed that the ambiguous term
in his equations is the plain periodic-table atomic weight, and that the other quantity (atomic
density) doesn't enter those equations at all. The paper's own five-word description had merged
two different things. That mattered less than feared — as established earlier, it cancels out —
but it upgraded your numbers from "correct up to a factor" to simply correct.

Which meant, for the first time, you could compare directly against his published values.

| | Yours | His |
|---|---|---|
| Bismuth-L vs arsenic-K | 2.416 | 2.490 ± 0.071 |
| Bismuth-L vs gallium-K | 2.847 | 2.895 ± 0.034 |
| Gallium-K vs arsenic-K | 0.849 | 0.861 ± 0.011 |

All three within a few percent, all three slightly low in the same direction — which is the
signature of a small systematic difference (density, atomic data tables) rather than a mistake.
A mistake would hit them unevenly.

---

## Checking the tool doesn't secretly depend on the answer

There's a trap buried in this kind of calibration, and it's worth spelling out because it's the
sort of thing that quietly invalidates a result.

The whole point of a k-factor is that it's a property of the *instrument and the line pair* — not
of the sample. You measure it once and apply it to unknown samples. But if the k-factor secretly
changed depending on how much bismuth was in the sample, you'd need to know the bismuth content
in order to pick the k-factor that tells you the bismuth content. Circular, and useless.

So: a check. Take the five samples that share a thickness but differ in bismuth content, and see
whether the k-factor drifts across them.

It doesn't — or rather, it drifts in a way that makes sense. The comparisons involving only hard
X-ray lines are constant to about **one part in ten thousand** across a twentyfold change in
bismuth content. The ones involving soft lines drift by a few percent, and they drift because the
sample's density changes slightly with composition, which changes how much absorption happens.
That's physics behaving correctly, not the equations failing.

One comparison — bismuth-L against arsenic-K — was so flat that its entire drift was **six times
smaller than the simulation's own random noise**. In other words, invariant to the limit of what
the simulation can even resolve.

That comparison is worth remembering. It comes back later, and not in a good way.

---

## The bismuth X-rays nobody can use

Your objectives list says the project should look at bismuth's K, L **and** M X-ray lines. The
analysis had only ever used L and M. The K lines were being recorded and stored, then ignored.

The reason they'd been ignored is that your supervisor's paper calls them "too hard for any
standard EDS detector" — they sit at around 77,000 electron-volts, which is an enormous energy
for this kind of measurement. So the working assumption was: not worth including.

Adding them anyway turned out to be the right call, and the result was the opposite of what
anyone expected.

**In the simulation, bismuth's K lines are the best-behaved of the lot.** Because they're so
energetic, almost nothing absorbs them — so comparisons using them are nearly immune to the
sample-thickness problem that wrecks the softer lines. On paper they look ideal.

They're still completely unusable, but for a different reason than assumed. Bismuth produces
about **103 times fewer** K-line photons than L-line photons for the same measurement. To collect
the same quality of signal you'd need to run the experiment roughly **ten thousand times longer**.
It's not that the physics is bad — it's that you'd be waiting a year for one spectrum.

That's a much better answer to the objective than leaving them out. "We didn't include them" is an
omission; "we included them, and here is exactly why they fail, and it isn't the reason usually
given" is a result.

It also exposed a gap that had been sitting there invisibly: **nothing in the pipeline models
counting statistics at all.** The simulation reports the *average* number of photons you'd expect,
and the arithmetic works perfectly on that average even if it's built from half a photon. Real
measurements have random noise that gets worse the fewer photons you collect. That's now a task in
its own right.

---

## Your supervisor's reply, and the bismuth-M mystery

You'd spotted that every calculation involving bismuth's M line came out about 1.5 times higher
than his published curves, while everything not involving it matched. His reply confirmed the
difference is real, and corrected the explanation.

The guess had been that his "bismuth M" might include several closely-spaced lines while your
simulation reports only the strongest one. He said no — **both simulation programs model only that
one line.** The difference is that the two programs use different reference data for it. Somewhere
in each program's internal tables of atomic physics constants, the numbers for that particular
X-ray emission disagree.

Then he sent you his Figure 1, and it pinned the difference down properly. Reading his curves
against yours at four different thicknesses:

- gallium and arsenic comparisons: **agree within reading error**
- bismuth L/M comparison: **1.506 ± 0.020**, flat at every thickness

A discrepancy that constant, across an eightfold thickness change, can only be a fixed difference
in one quantity. Not an absorption effect — that would grow with thickness. It confirmed by
measurement what had been deduced from the algebra.

He also supplied something unexpectedly useful: a table of bismuth's M-series emission strengths.
For every 100 photons in the line your simulation reports, a real detector would see about 174,
because it can't separate them from their close neighbours. That's not the explanation for the
1.5× — it's a separate correction, converting "what the simulation says" into "what a detector
would show". It matters a lot later.

And on the sum peak — the artefact at the heart of the project — he revealed something important
about his own method. **His correction was fitted, not measured.** He noticed his measurement
disagreed with his simulation, assumed the sum peak caused the gap, and turned the correction up
until they agreed. The 600 counts he quotes is "however much I needed to close the disagreement",
and it's entangled with his bismuth-M value — the very number that differs from yours by 1.5×.

So there is no published recipe to inherit. That's not a criticism of his work; it's a fact about
what you can and can't reuse.

---

## The script that ran your simulations, and had already vanished

This one is uncomfortable and worth recording honestly.

The project's status notes said, for weeks, that the piece of code which actually *launches*
simulations "works as a script, not yet a proper module" — implying a tidy-up job. Someone went
looking for it.

It wasn't there. It had never been in your project folder. It had been written into a temporary
scratch folder that gets wiped when a working session ends, and it had been wiped. Around 130 such
folders existed for this project; every one was empty.

**Nothing scientific was lost.** All 21 simulations, every input file, every output file, and the
records linking them were intact. But the ability to *re-run* anything was gone, and had been gone
for some time without anyone noticing. For a project whose entire subject is simulation, that's a
hole an examiner could reasonably poke at.

Two lessons came out of it. The obvious one: anything the project depends on lives in the project
folder, never in a temporary one. The subtler one: the project's own notes had been asserting
something about a file that hadn't existed for weeks. There's a rule in the project's guidelines
about checking the actual files rather than trusting written descriptions — it had been applied
carefully to the simulation software's documentation, and not at all to the project's own notes.

The replacement is better than what was lost: a properly tested module, plus a command-line tool
to run a batch of simulations. It refuses point-blank to overwrite results that already exist,
which matters because your 21 finished runs sit in a single flat folder with no version control
and no undo.

---

## The corner nobody had tested — and what was hiding in it

Your 21 simulations form a cross shape. One arm varies thickness at a fixed bismuth content. The
other varies bismuth content at a fixed thickness. They meet at one point.

That leaves the corners empty — in particular, the one where bismuth content is *lowest* and the
sample is *thickest*. Which is unfortunate, because that's exactly where the signal is weakest and
absorption is worst. It's where "at what point does this stop working?" actually gets answered.

The hope was that you wouldn't need to go there. Absorption is normally treated as depending on
how much *material* the X-ray passes through — density multiplied by thickness. If that were true,
you could work out the empty corner from the data you already had.

Six new simulations tested it. **It isn't true.**

Think of it as fog. How much light gets through depends on how much fog there is — but fog made of
smoke blocks light differently from fog made of water droplets. Same amount of stuff, different
material. Your alloy does exactly this: going from 20% bismuth to 1% bismuth changes the material
from **a quarter bismuth by weight to almost none**, while the density barely moves (6%). Bismuth
is heavy, so a little of it weighs a lot — and it's also a strong absorber.

Predicting the new samples from the old ones was off by **23%** at the thickest point, roughly 600
times the simulation's noise. The corner genuinely had to be run.

**And the failure wasn't uniform, which is the useful part.** The gallium-based measurement was
wrong by 23%; the arsenic-based one by only 2%.

That matters because these measurements get used as a *stand-in for thickness*. You can't easily
measure how thick a foil is, but you can read a brightness ratio off the spectrum — so the ratio
becomes your ruler. The whole point is to remove your dependence on something you don't know.

But if your ruler also responds to composition, you've swapped one unknown for two — and
composition is the thing you're trying to measure. The arsenic ruler is sound. The gallium one
isn't. Your supervisor's figures use the gallium one, and his data couldn't have shown him this: he
had two compositions, each at a single thickness, so the effect was invisible.

---

## The first pictures

Your supervisor's reply to the plot request was brief and specific: *"Just complete your
simulations and prepare the plots."* He was about to travel with no internet for a week.

Worth noting: **no plots had ever been sent to him.** Every result up to this point existed as
numbers in spreadsheets and prose in reports. Plotting had actually been listed as deliberately out
of scope.

Two figures were produced. The first reproduces his Figure 1 from your simulations — three
brightness ratios against sample thickness. Reproduced in *data* since July, but never actually
drawn, which made it the one replication you couldn't show anyone.

The second is your own result: the corner finding, as two side-by-side panels. If absorption
depended only on density-times-thickness, each panel would show two curves lying on top of each
other. On the left (gallium) they separate visibly. On the right (arsenic) they don't. The finding
is carried by the contrast between the panels rather than by any number.

A note on how these were made, because it's a small point of discipline: **no figure calculates
anything.** Every number on a plot is read from a tested piece of code. A calculation done inside a
drawing routine is a result nobody can trace or check.

Both figures needed a second pass after actually looking at them — labels sitting on top of data,
axis numbers in unreadable scientific notation, and one case where the two panels had different
vertical scales, which made the left-hand gap look bigger than it really was. Rendering a figure and
*looking* at it are separate steps.

---

## Taking away the crutch

Here's a flaw that had been sitting in the main result.

The test works like this: build the tool on one batch of samples, then use it to guess the
composition of a different batch. Honest so far. But to use the tool you need to know how thick the
unknown sample is — and the code was simply *told* the right thickness, because it's recorded in
the simulation settings.

A real experimenter doesn't have that. Thickness is exactly as unknown as composition. So the test
was hiding one of the two answers in its sleeve.

The fix uses the arsenic ruler from the previous section: read the sample's own brightness ratio —
available from the same spectrum you're already measuring — and use that instead of the true
thickness. Now nothing is handed over.

The expectation was that accuracy would get worse, and that this would be the honest price of a
fairer test.

**It got slightly better.** Average error fell from 0.0038 to 0.0034 in recovered bismuth fraction,
and improved most at low bismuth content, which is the difficult end.

That sounds like a paradox but isn't, and your supervisor predicted it in his paper: the ratio
provides "an inherent self-calibration". When a sample's composition changes its absorption, it
changes the measured ratio too — and looking the tool up at that shifted ratio partly compensates
for the change. Pinning the thickness to its true value throws that correction away.

You've now demonstrated his claim rather than quoted it.

The arsenic ruler also beat the gallium one by 47% — an entirely separate confirmation of the
corner finding, arrived at by a different route.

Two small notes on rigour. The interpolation method was chosen by **measurement**, not preference:
one of your samples happens to sit outside the calibration set, so it works as a free test case,
and it showed the simple method is accurate to 0.17%. And one of the safety checks written for this
— the one meant to prove the code can't peek at the true thickness — was initially written in a way
that **couldn't fail**. It was rewritten. A safety check that can't fail is worse than none, because
it looks like protection.

---

## The sum peak: the artefact the whole project is about

Finally, the thing the dissertation exists to investigate.

When two X-rays hit the detector at the same instant, it can't tell them apart and records them as
a single photon carrying their combined energy. In this material, gallium's L line (1,098 eV) plus
arsenic's L line (1,282 eV) sums to 2,380 eV. Bismuth's M line sits at 2,423 eV.

**Forty-three electron-volts apart.** No detector in existence separates those. So every one of
these coincidences puts a fake bismuth count into your spectrum.

The simulation can't produce this effect, so it's added afterwards, arithmetically, to the stored
results. Four modelling decisions were genuinely open — and since your supervisor is unreachable
until late August, they became yours. Rather than guess, all four were built as **switches**, so the
choices are settings rather than assumptions baked into code, and every stored result records which
settings produced it.

One detail worth knowing: your supervisor's two contributing lines were within 9% of each other, so
his phrase "15% of their line intensities" was unambiguous for him. In your data they range from
equal to a factor of two apart, so the same phrase has no single meaning. That needed a stated
choice.

Then the numbers came out, and they're the most important result so far.

At a pile-up level of 1%:

| Bismuth content | Fake counts, as a share of the real bismuth-M signal |
|---|---|
| 1% bismuth | **97%** |
| 5% bismuth | 19% |
| 20% bismuth | 4% |

At the low end, a 1% pile-up **roughly doubles** the bismuth-M peak. The measured ratio drops by
half. At the high end, the same artefact shifts things by 4%.

**The identical artefact does more than twenty times the damage at low bismuth content.**

The reason is simple once stated: the gallium signal is around 100 times stronger than the
bismuth-M signal in a low-bismuth sample, but only about 4 times stronger in a high-bismuth one. A
small leak from a large pool into a small one is a big deal for the small pool.

This is very likely the answer to the dissertation's central question. The thing that stops you
measuring bismuth at low concentrations isn't that the signal gets faint — it's that a contaminating
artefact from the *other* elements grows to swamp it. And it also puts the earlier
counting-statistics worry into perspective: random noise at that composition is a few percent,
against a sum peak's ninety-seven. On present evidence the artefact dominates, and by a wide margin.

That's the sensitivity sweep turning into the substance of the answer rather than a robustness check
on it.

## The other overlap turned out to be a different animal

*(Technical report: §27)*

From the start, this project talked about "the two peak overlaps" as if they were twins: the sum
peak sitting on bismuth-M, and the arsenic peak sitting next to bismuth-L. Same problem, two
places. That framing turned out to be wrong, and finding out why mattered more than the numbers.

A detector doesn't see X-ray lines as infinitely sharp spikes. Each one is smeared into a bump
with a width, and the width can be calculated from how the detector physically works — how much
electric charge an X-ray of a given energy liberates in the silicon, and how much that amount
naturally varies. So the real question about any two neighbouring peaks is: *how far apart are
they, measured in bump-widths?*

The answer split the twins apart:

- **The sum peak and bismuth-M are 0.47 widths apart.** They melt into a single bump. No
  software can un-melt them — the fake counts genuinely become part of the bismuth signal.
- **Arsenic-K and bismuth-L are 1.74 widths apart.** They look like two humps with a dip
  between them, and standard peak-fitting software separates them routinely.

So modelling the second overlap the way the first was modelled — counts simply landing in the
wrong peak — would have been wrong, and unfairly hard on the very route the project was about to
recommend. What the arsenic neighbour *really* costs is precision: fitting a small peak on the
shoulder of one about 86 times bigger makes your measurement of the small one wobblier. It
doesn't push the answer in a wrong direction; it makes repeat measurements scatter more.

That distinction — a **push** versus a **wobble** — runs through everything that follows. A push
(the sum peak) stays wrong no matter how long you measure. A wobble (this overlap) shrinks if
you collect more photons. They fail differently, and they are fixed differently.

One honesty note: the smearing formula uses two silicon constants that come from a standard
textbook not physically in this folder. Rather than trust them, the code slides both across the
entire range the literature quotes and re-asks the question at every corner. The two peaks stay
separable at every corner, and the sum peak stays merged at every corner — the constants would
have to be off by more than double before either conclusion flipped. So the missing citation
affects a decimal place, not a finding.

## Same recovery, every assumption at once

*(Technical report: §28)*

The sum-peak model had four knobs nobody could settle — which lines feed it, what its size is
measured against, whether the feeding peaks lose the counts they donate, and what the bismuth-M
baseline should be. Your supervisor is unreachable until late August, so no answer is coming.

The old approach would be: pick sensible settings, say so, hope. The approach taken instead:
**run the entire recovery under every combination of all four knobs** — sixteen configurations,
at three artefact sizes each, plus an untouched baseline. It costs seconds of computer time, and
it changes the question from *"which setting is right?"* (unanswerable) to *"does the answer
depend on the setting?"* (measurable).

It doesn't. In all sixteen configurations, routes that measure bismuth through its M peak come
out roughly **a hundred times less accurate** than routes using the L peak. Whatever the truth
about those four knobs, the ranking is the same. That's what lets the recommendation survive a
supervisor asking "but what if you'd assumed differently?" — the answer is "we did, all sixteen
ways, here's the table."

The sweep also revealed *which* knobs matter. Two turn out to move the numbers (what the
artefact's size is measured against, and the baseline); two barely matter at all (which lines
feed it, and whether they're depleted). So the write-up needs one careful paragraph, not four.

## Tidying up before the memory loss

*(Technical report: §29)*

A short housekeeping pass, recorded because two finds were near-misses. The web page that was
published for your supervisor — its source file existed only in a temporary session folder, the
same kind of folder the simulation-runner script was lost from weeks ago. If it had vanished,
the published page could never have been updated again. It's in the project folder now, along
with the script that turns it into an offline copy. The project instructions file had also
drifted out of date in seven places (it still said 15 simulations when there are 21), and a
"start here" note now exists for future sessions that begin with no memory of this one.

## Counting the photons, properly

*(Technical report: §30)*

One limit had never been modelled, and it's the humblest: a spectrum is made of a finite number
of photons. In the 1%-bismuth sample, the bismuth-L peak holds about 116 detected photons.
Random arrival noise on 116 photons is about 9% — before anything else goes wrong.

The obvious way to turn photon noise into "error on the final bismuth answer" is a pen-and-paper
formula. The code does something more thorough: it nudges each X-ray line one at a time, re-runs
the *entire* recovery — thickness estimate, calibration lookup, inversion, everything — and
watches how far the final answer moves. That way, sneaky indirect paths are priced in
automatically. (There is one: noise on an arsenic line jiggles the thickness estimate, which
picks a slightly different calibration value, which moves the bismuth answer — even for routes
that never use arsenic directly.)

Because this numerical approach *could* hide a bug, it was checked against pen-and-paper in the
three cases where pen-and-paper is exact. All three match to six decimal places. It was also
cross-checked against the completely separate photon-count calculation from the overlap work:
same number from two codebases that share nothing.

The results, at your supervisor's own measurement time, for the hardest sample (1% bismuth):

| Route | Noise on the final answer |
|---|---|
| Bismuth-L based | **3.5%** — comfortably usable |
| Bismuth-M based | 4.3% |
| Bismuth-K based | 35% — hopeless |
| Gallium/arsenic only | 10–45% — hopeless at low bismuth |

Three things worth knowing:

1. **The August-13th worry inverts, officially.** Photon noise at low bismuth is ~3.5%; the sum
   peak's damage on the same routes is ~97%. Noise is the *smaller* problem by a factor of
   twenty-odd. The opposite of what was assumed when this task was first scheduled — and that
   inversion is itself a result.
2. **Bismuth-K's failure now has a price tag.** To get a decent answer from it you'd need over
   **twelve times** your supervisor's measurement time. The L route is already there with time
   to spare. "Unusable" became a number an examiner can check.
3. **The gallium/arsenic route fails for a strange, elegant reason** — not too few photons, but
   the algebra of its own equation. Its sensitivity to noise stays fixed while the thing being
   measured shrinks toward zero, so the *relative* error blows up regardless of counting time.
   No better detector fixes that.

## Adding it all up: the error budget

*(Technical report: §31 — this is the deliverable Learning Objective 4 asks for)*

Three separate enemies had now been measured: the sum peak (a push), the arsenic overlap (a
wobble), and photon noise (another wobble). Each on its own terms. The final step converts all
three into the same currency — error on the recovered bismuth content — adds them up honestly
(wobbles combine the statistical way; the push goes on top at full strength, which is the
cautious choice), and asks: **below what bismuth content does each route stop working?**

None of the three enemy sizes is known exactly, so nothing was assumed: three sum-peak sizes,
three overlap strengths, three measurement times — 27 scenarios, every route scored in all of
them. Asking "which route wins" only in the friendliest scenario would be worthless.

The verdict of the table, for the hardest sample (1% bismuth, aiming for 10% accuracy):

- **Bismuth-M routes fail in all 27 scenarios.** Killer: the sum peak. Measuring longer doesn't
  help — a push doesn't average away.
- **Bismuth-K routes fail in all 27.** Killer: too few photons, and the shortfall is twelvefold.
- **Gallium/arsenic routes fail in all 27.** Killer: their own algebra.
- **Bismuth-L routes fail in 9 of 27** — and every single one of those nine is either the
  shortest measurement time or the most pessimistic overlap assumption. At your supervisor's
  actual measurement time with any reasonable overlap, **they pass everywhere**.

That last distinction is the whole answer. Bismuth-L's failures are the kind you fix by
measuring longer. The others' failures are the kind you can't fix at all. So the analysis ranks
**bismuth-L against arsenic-K** as the route — the same one every earlier chapter kept pointing
at, but now it wins a 27-scenario stress test rather than a beauty contest.

Two cautions, both stored in the output rather than footnoted: where a route never reaches the
target inside the tested range, the code says so instead of guessing a number beyond its data
(no extrapolated limits, ever); and the final *verdict* — whether 10% is the right bar, and what
to actually tell the world — is yours, not the computer's. The table is evidence, not a
conclusion.

## One command to rebuild everything — and the bug it caught immediately

*(Technical report: §32)*

Until today, regenerating the analysis outputs meant remembering which of twelve functions to
run in which order. Now one script does it, in the right order, every time. The need was proven
by an embarrassment found while building it: one output file that the workplan confidently
described *did not exist* — the function that makes it had simply never been run on the full
dataset. A new automatic check now makes that impossible to repeat: if anyone adds an output
function and forgets to wire it in, a test fails.

The script's very first full run then caught something better. Before running it, every
existing output file was fingerprinted. Afterwards, one file that should have been untouched had
changed. Investigation: the overlap calculation defaults to a 100-second measurement, but the
file on disk — and the numbers already quoted in the technical report — used your supervisor's
715.5 seconds. The rebuild had silently regenerated the file **nine times noisier**, with
identical column headings, identical row count, nothing visibly wrong. The classic failure mode
of this entire project: wrong numbers that run fine.

Fixed by making the script state the measurement time out loud instead of inheriting a default;
the regenerated file came back byte-for-byte identical to the original, which both confirms the
diagnosis and certifies the report's quoted numbers. Two new tests stand guard. And the
fingerprint-everything-before-rebuilding habit earned a permanent place in the routine.

Four new pictures came out of the day as well: the headline chart answering Objective 4 (which
bismuth line survives, with the uncertainty band across all 27 scenarios), the sum peak's
lopsided damage, the recovery running clean on bismuth-L while bismuth-M bends away from the
truth, and bismuth-K's strange double life — the most absorption-proof line in the whole matrix
and still useless, because immunity doesn't matter when almost no photons arrive.

**Where the day ends:** 297 automated checks pass, six figures rendered, 23 output tables, all
rebuildable by one command. What's left is the verdict (yours), the band-gap literature work for
Objective 1 (no code involved), and the writing.
