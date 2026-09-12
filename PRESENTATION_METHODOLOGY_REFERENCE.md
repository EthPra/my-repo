# Reference — the full argument

*Everything below is for your own understanding and for questions. It is roughly 11 minutes of
material; you are not delivering it. Beat timings below are measured, not estimated.*

## The frame — say this first (measured 0.6 min)

> "The methodology in this project is not 'I ran a Monte Carlo code'. Running the code is the
> easy part. **The hard part is that almost every way of getting it wrong produces a result that
> looks completely normal.** So the methodology is really a set of decisions about how to make
> silent failures loud, and how to handle the physics inputs nobody can cite. That's what I want
> to take you through."

That sentence buys you the next eight minutes. It tells the second marker why this is a
methodology worth presenting, and it tells Walther you understand what his code does and does
not warn you about.

---

## Beat 1 — Why a wrapper at all (measured ~1 min)

**The spine:** 21 simulations × 6 input files each = 126 files that must be internally
consistent. Hand-editing them is not the risk; the risk is that the failures don't announce
themselves.

Three to name out loud — pick two if you're short:

- **Lengths are in Ångströms, not nanometres** — and the manual says otherwise. A 100 nm foil is
  `1000` in the file. Put `100` in and it runs perfectly and simulates a foil ten times too thin.
- **Composition is weight fraction, not atomic fraction.** Atomic fractions run fine and simulate
  a different alloy.
- **The mass density has to be set explicitly.** Leave it at zero and the code auto-mixes the
  *elemental* densities of gallium, arsenic and bismuth. No warning, no error, ~15–20% too dense.

> "**None of those three throws an error. All three change the answer.** So the design constraint
> was reproducibility with a gate on it."

**The gate, in two sentences:** every generated input is diffed byte-for-byte against a validated
reference set, and every difference has to classify as intended, formatting, or documented — one
unexplained difference and the gate fails. Then, to check the gate actually bites, **I injected
each of those silent failures on purpose. All five were caught.** The suite is now 297 tests.

*If someone looks sceptical:* the point of the fault injection is that a passing test proves
nothing unless it also fails when it should.

---

## Beat 2 — Physics inputs are cited, or the pipeline stops (measured 1.3 min)

**The rule, stated as a rule:** no physical quantity is invented. Every constant traces to a
primary source or it is flagged in the code as pending verification.

**Lead with density.** Deliver it flat and unhurried — there is nothing to defend here, and any
hedging in your voice will invent a problem that doesn't exist.

> "Both MC X-Ray and CASINO estimate compound densities by interpolating the *elemental* metal
> densities of gallium, arsenic and bismuth. But in GaAsBi the bonds aren't metallic — they're
> covalent, with a little ionicity. **So that estimate is the wrong physical picture, and it's
> wrong silently.**"

Then attribute it, in one sentence, and move on:

> "**On Professor Walther's advice** I use endpoint densities of 5.32 for GaAs and 7.18 for a
> hypothetical GaBi, and interpolate between them — which updates the values in his own published
> paper."

That sentence is doing a specific job: **the second marker doesn't know where the number came
from**, and without it they see a student quietly using a density that disagrees with the cited
source. With it, the question never forms. For Walther it's simply accurate.

**The one part that is genuinely yours is the interpolation scheme**, and it's worth knowing that
before someone asks:

> "He specified the endpoints; interpolating **linearly in density** is my choice, which gives
> ρ(x) = 5.32 + 1.86x."

*If pushed on that:* the alternative is the lattice route — Vegard's law on the lattice parameter,
then ρ = 4M/N\_A·a³ — and the two agree to about 2%, since his 7.18 implies a(GaBi) ≈ 6.36 Å
against 6.33 from the lattice picture. So the scheme choice isn't load-bearing. **That is the
defence if you need one, and you probably won't.**

**Keep the "it largely cancels" argument out of this beat** — it belongs in Q&A. It's true, and
it's his (k\* calibration is self-correcting against a density offset because you calibrate and
invert on the same assumption), but volunteering it here answers a question nobody asked and
deflates the beat you just delivered.

**Then the geometry, fast** (one breath — this is settled and nobody will challenge it): 200 keV,
25° take-off, free-standing foil, no substrate, Si:Li detector with a 0.5 cm crystal.

*Trajectory counts are deliberately not covered here* — the LO slides carry them, and the
thin-foil switch is written up in the dissertation methodology instead (Ethan's call, 2026-08-20).
The one idea worth salvaging from it, the two-noises distinction, has moved to Beat 5 where it
does real work.

**Close the beat with the one check that the physics comes out right** — this is validation, not a
result, and it's the strongest single sentence you have for the second marker:

> "As a check that the pipeline produces the right numbers at all: **k\* for bismuth L-alpha over
> arsenic K-alpha comes out at 2.416, against the 2.490 published in the paper — 3% apart, just
> outside his quoted sigma.** That's from a different simulation code, a 6% different density, and
> a different way of deriving the constant. **It's the instrument being calibrated against a known
> standard.**"

⚠ Say **"just outside his quoted sigma"**, not "about one sigma". It's 1.04σ — your own record
(REPORT §18.3) is careful about this, and Walther knows his own error bar. Claiming agreement he'd
read as marginal is a bad trade for one word.

---

## Beat 3 — The run matrix, and why it grew (measured 3.4 min)

**Set A** — thickness, 2 to 1024 nm in a doubling series, at x = 0.20. Ten runs.
**Set B** — composition, x = 0.01 to 0.20, at 100 nm. Five runs.

> "That's a **cross, not a grid**, and it's frozen against my objectives form. The implicit
> assumption in a cross is that you can interpolate the interior — and here the justification for
> that was that absorption depends on ρ·t, the mass-thickness, so a thin dense foil should behave
> like a thick light one."

**The turn — this is the strongest methodology beat you have. Slow down here.**

> "**I tested that assumption instead of relying on it, and it failed.** If I interpolate Set A
> onto the mass-thickness of a low-bismuth arm, the Ga K/L ratio comes out **23% wrong at
> 1024 nm**."

**Two comparisons were run, not one, because each on its own has an obvious objection** — worth
knowing even if you only say the second out loud:

| objection | the comparison that answers it |
|---|---|
| *"That's an interpolation artefact."* | Log-log interpolation gives the same answer, so it isn't linear-interpolation curvature. |
| *"That's just the two arms having different densities."* | A **model-free** check at matched thickness — no interpolation at all. The density offset there is a **constant −6.2% at every point**, but the gap **grows 17-fold**, from 1.5% at 32 nm to 26.3% at 1024 nm. **A constant offset cannot produce an effect that grows.** |

The second is the one that closes it. If you have time for only one, use that one.

> "**So the cross could not predict its own interior.** That's why there's a third arm: six runs
> at x = 0.01 across the thick end, at thicknesses the first arm already covers — so for the first
> time there's the *same geometry at two very different compositions*. Twenty-one runs total.
> **The matrix grew because a measurement told me to, not because I wanted more data.**"

*Worth knowing, in case you're asked why the composition arm didn't already answer this:* it
couldn't. Set B sits at 100 nm only, and **the effect grows with thickness** — 1.5% at 32 nm,
5.7% at 128, 17.8% at 512, 26.3% at 1024. A single slice at 100 nm catches it near its smallest
and makes it look negligible. **You need a second composition across a range of thicknesses to see
the gap open up**, which is exactly what the third arm is.

**Then the design consequence — this is a methodology decision, which is why it belongs here.**

First set up *why* a thickness proxy exists at all, or the rest doesn't land:

> "To get composition out of a spectrum you need the right k\*, and k\* depends on how thick the
> foil is — thickness controls how much of the soft signal is absorbed on the way out. But a real
> experimenter doesn't know the thickness either. **So the method reads a stand-in for thickness
> off the same spectrum: the K/L ratio.** Hard K lines escape, soft L lines get absorbed, so K/L
> climbs steadily with thickness. Measure K/L and you've measured thickness without measuring
> thickness."

Then the catch, which is the actual point:

> "**But a stand-in only works if it responds to one thing.** If K/L also moves with composition,
> then a given value is ambiguous — it could be a thick foil with little bismuth or a thinner one
> with more. And composition is the unknown I'm trying to measure. **You've put the unknown back
> into the coordinate that was meant to remove it.**"

Then what the third arm measured:

> "**Ga K/L and As K/L are not interchangeable for this.** At the same thickness, changing the
> bismuth content moves Ga K/L by **26%** and As K/L by **7%**. And once you account for the two
> arms having different densities — which mass-thickness already handles — As K/L's response
> almost entirely disappears, down to about **2%**, while Ga K/L's barely moves, still **23%**.
> **So arsenic's sensitivity is the harmless kind and gallium's isn't.** I index on As K/L, and
> that's now an evidence-based choice rather than a preference."

Close it generously:

> "Figures 3 and 5 in the paper use Ga K/L — and with two compositions at unswept thickness, that
> dependence simply cannot appear in that data. It's an unobservable in the design, not a mistake
> in it."

⚠ **Quote the numbers like-for-like.** An earlier draft put 26% next to 2%, which mixes two
different comparisons and overstates the gap. The clean pairs:

| | matched thickness | matched ρ·t (density accounted) |
|---|---|---|
| Ga K/L | **26.3%** | **22.8%** |
| As K/L | **7.0%** | **1.6%** |

Either row carries the argument on its own — Ga is ~4× worse on one basis, ~14× worse on the
other. Say both rows, or one row, but never one number from each.

⚠ **If asked *why* gallium and arsenic differ — you have not established that, and should say so.**
It would need mass attenuation coefficients for the alloy at 1.098 and 1.282 keV as a function of
bismuth content, cited rather than asserted. **Do not improvise a mechanism** — an absorption-edge
story is exactly the plausible-sounding physics that would come apart in front of Walther. The good
answer: *"I haven't established the mechanism. What I can say is the effect is real, it's 26%
against 7% at matched thickness, and it's large enough to determine which ratio I use."* The
decision needs the measurement, not the explanation.

*Visual:* `fig02_rho_t_insufficiency` — two panels, shared axis. Left panel the arms separate,
right panel they nearly coincide. The finding is the contrast between panels; say that.
**Result-free — safe to show.**

---

## Beat 4 — Store raw, derive cheaply (measured 1.0 min)

Short beat. It's governance, and governance told well reads as rigour.

> "There's one rule the pipeline enforces in code: **the run loop stores raw, unprocessed
> intensities and nothing else.** No ratios, no k-factors, no corrections anywhere near the
> simulation. A test fails if a derived column ever appears in the aggregated table."

Why it matters, in one sentence — this is the sentence, not the rule:

> "**Every derived number in the project can be re-derived without re-running a single
> simulation.** Which matters, because several of the atomic-data questions are still open, and
> if one of them moves I re-derive rather than re-simulate."

*It also quietly answers "how do you know your conclusion isn't fragile?" before it's asked* —
every scenario, every switch combination and every threshold is a re-read of stored numbers, not a
re-simulation. That's why the conclusion can be quoted across 27 scenarios rather than at one
favourable corner.

Two details worth ten seconds each if you have them:

- **Provenance is verified, not labelled.** For each run the stored specimen file is re-read and
  its density and weight fractions checked back against the spec. A run pointing at a mismatched
  file fails the whole aggregation loudly, rather than quietly mislabelling data.
- **The recovery is held out in both unknowns.** An earlier version looked the calibration up at
  the run's *known* thickness — but a real experimenter doesn't have that; thickness is exactly
  as unknown as composition. The current version reads the run's own measured As K/L, off the
  same spectrum being quantified, and uses neither the thickness nor the composition.

> "And removing that crutch **improved** the recovery — mean error 0.0034 against 0.0038. Which
> is the self-calibration property the paper claims for the K/L axis, **demonstrated rather than
> quoted.** When a sample's composition shifts its absorption, its measured K/L shifts with it,
> and the lookup partly compensates. Fixing the thickness throws that correction away."

---

## Beat 5 — Pricing what the simulator doesn't give you (measured 4.8 min)

**This is the methodological core. If you cut anything, do not cut this.**

### Memorise these six landmarks, not the words

Everything below is 460 spoken words. **Don't learn it.** Learn these six, and talk around each one
for twenty or thirty seconds — the wording will come, because you know all of this:

1. **"The simulation is clean. No detector is."** → three things degrade it.
2. **0.47 versus 1.75 linewidths** → one merged, one resolvable → *different problems, different
   models.*
3. **Sum peak fakes counts.** Swept, all sixteen combinations, ordering identical in every one.
4. **The overlap I bounded, not modelled** — four inputs I couldn't cite, so I didn't invent them.
5. **Bias versus variance.**
6. **One currency → 27 scenarios →** hand off to the conclusions.

*If you lose your place mid-beat, the recovery line is "so that's the second of three" — the
three-degradations frame is the thing that keeps you oriented.*

**Open with the premise. It's the sentence that makes the rest necessary:**

> "Everything I've shown you so far comes out of the simulation clean — every photon counted where
> it belongs. **No real detector produces that spectrum.** Three things stand between the
> simulation and a measurement, and none of them are in the output file: two peak overlaps, and
> the fact that a real acquisition contains a finite number of photons. **So I had to put a price
> on each one.**"

### First move: measure the overlaps, don't assume them

> "Every detector smears a photon's energy, and the width of that smear is the linewidth. **Two
> peaks closer than about one linewidth merge into a single bump; further apart, you still see two.**
> So I measured both overlaps against it. **The sum peak sits at 0.47 of a linewidth — merged. The
> arsenic K-alpha / bismuth L-alpha pair sits at 1.75 — resolvable.** So they're not the same kind
> of problem, and they don't get the same kind of model."

*What that sentence is doing: merged means the contaminating counts are indistinguishable from
bismuth, so you must **add** them. Resolvable means nothing lands in the wrong peak — the fit is
just imperfect, so the cost is **precision**, not fake signal. That one measurement determines the
treatment of both, which is why it's the first thing you say.*

### Degradation 1 — the sum peak: modelled

> "**A sum peak is a detector artefact, not physics.** Two photons arrive together, the electronics
> can't separate them, and it records one event at their combined energy. Gallium L-alpha plus
> arsenic L-alpha is 2.380 keV; **bismuth M-alpha sits at 2.423.** So pile-up manufactures counts
> inside the bismuth peak — it fakes the signal I'm measuring.
>
> MC X-Ray doesn't produce sum peaks, so I synthesise one and **propagate it through the entire
> recovery** — everything downstream sees the corrupted spectrum. The magnitude isn't measurable
> from my data, so **I swept it**, and the four modelling choices are switches, so **I ran all
> sixteen combinations. The ordering of the routes is identical in every one.**"

*The claim in that last clause is the one that matters: running all sixteen answers a question
picking one can't — whether the conclusion depends on the setting at all. Say it as a result,
because it is one.*

### Degradation 2 — the As Kα / Bi Lα overlap: bounded

> "**This one I bounded rather than modelled — deliberately.** Doing it properly needs peak shapes,
> tailing, the background beneath both peaks and how a fitting algorithm behaves. **Four inputs I
> can't cite — so I didn't invent them.** Instead the cost is carried as extra uncertainty on the
> fitted bismuth peak area, with the leakage swept over the same range as the sum peak so the two
> are directly comparable."

**Then the distinction to land — this is the best single line in the beat:**

> "**They're different in kind, not just in size. The sum peak is a bias — systematically wrong in
> one direction, and no amount of averaging removes it. The overlap is variance — noisier but
> unbiased, and it improves with counts.**"

### Degradation 3 — counting statistics

> "Third: a real acquisition contains a finite number of photons. **And this is a different noise
> from the Monte Carlo's** — more trajectories improve the simulation, but they don't improve the
> experiment being modelled; that's set by beam current and time. The simulation reports averages,
> and the algebra closes on them however few photons sit underneath. **At x = 0.01, bismuth L-alpha
> is about 116 photons.** So I propagate that through the whole recovery numerically, and check it
> against the closed-form answer where one exists."

### The finish — one currency

**This is the climax of the beat. It's the step that makes a recommendation possible at all, so
don't let it trail off as a footnote.**

> "So I have three mechanisms — **and measured in their own units they can't be compared.** One is
> contaminating counts, one is uncertainty on a fitted peak area, one is photon noise. **And read
> on its own, each one prefers a different route.** So the last step converts all three into a
> single currency — **absolute error on recovered composition**, which is the thing I actually care
> about — and asks where the total crosses my accuracy target. **That crossing point is where the
> recommendation comes from, and I'll show it in a moment.**"

Then one closing sentence — **this is the methodology's thesis and the last thing you say:**

> "**And nothing unknown gets a default.** The pile-up level, the overlap leakage and the dose are
> all genuinely unknown, so all three are swept — **twenty-seven scenarios**, and every number I
> quote carries the scenario it came from. Where the error curve never crosses the target inside
> the compositions I actually simulated, the code **reports which side it fell on rather than
> inventing a number.**"

*Held in reserve, not spoken by default:* the combination rule is total = |bias| +
√(σ²counting + σ²overlap) — variances in quadrature, bias added linearly on top. If challenged on
it, the phrase is **"a conservative envelope, not a likeliest error."** Don't volunteer it; it
costs 15 seconds and answers a question nobody has asked yet.

*That second bullet is the methodology section's thesis — **where I can't know a number, I sweep
it and report how much the answer depends on it.** It used to have its own closing beat; it works
better landed here, in context, where the 27 scenarios make it concrete rather than a claim about
your own rigour. This is the last thing you say before handing to the conclusions.*

⚠ **Say the threshold you settle on 21 Aug — and say it's a chosen target.** Once it's decided
there's no reason to be vague about the number. What survives from the earlier caution is the
honesty, not the hedging: *"a 10% relative target — which is a choice I've made and stated, not
something derived from the literature."* Naming it as a choice pre-empts "why that number?"
far better than avoiding it does. **Check this wording matches whatever you actually pick.**

*Visual:* `fig04` (sum-peak selectivity) fits this beat well and doesn't front-run the ranking.
`fig03` is the LO4 headline — **save it for the conclusions**, where it's the payoff. If you want
something purpose-built, a two-minute sketch of the two separations, 43 eV and 297 eV, against one
detector linewidth carries the whole beat on its own.

### Cut from the spoken beat — kept here, not lost

**None of this is deleted; it's demoted to on-demand.** Say any of it only if you're asked, or if
you find yourself running short. Each item is priced so you can pick by the clock.

| | ~time | when to use it |
|---|---|---|
| **The near-miss.** *"That ruled out the model I'd otherwise have written — treating the overlap as arsenic counts misassigned to bismuth assumes a blindness the detector doesn't have, and would have overstated the damage to the route I'm recommending. That's the kind of error that survives, because it makes your error bars look conservative."* | 25 s | The single best re-insert if you have spare time. Follows straight after the 0.47/1.75 line. |
| **Resolution model validated, not fitted.** Returns 130 eV at Mn Kα (the Si(Li) spec) and independently predicts Bi Lα1/Lα2 are inseparable — both asserted as tests. | 15 s | Only if someone questions the linewidth number. Getting two known answers right is why the third is credible. |
| **Why not the published 15%.** It wasn't measured from a pile-up rate — it was tuned to make a measured L/M ratio agree with a simulated one, so it's tied to a Bi M value differing from yours by 1.5×. Fitted quantities don't transfer between codes. | 25 s | Already in the Q&A bank. Walther may raise it himself. |
| **The cancellation anecdote.** First propagation applied the artefact to the calibration as well as the unknown; recovered composition didn't move, because both sides cancelled — the variant Walther's own practice rules out. The cancellation is itself worth reporting. | 45 s | The beat's only narrative moment, and the most expensive thing here. Re-insert only if you're comfortably inside time. |
| **The counting method in full.** Perturb one line at a time, re-run the whole recovery, central difference in log intensity — so the indirect path through the As K/L proxy and the shared-line correlation are priced in by construction. Validated against three closed-form derivatives to six figures. | 30 s | Already in the Q&A bank. Strong if asked "is it just Poisson?" |

---

## If you're asked before the conclusions

Walther may well interrupt to ask what the plots show — his last instruction to you was to prepare
them. **Defer, don't answer.** Answering here spends the conclusion's moment and derails the beat
you're mid-way through:

> "I'm coming to that in a few slides — let me first show you why you can trust it when I do."

That's the whole script. Said warmly it reads as confidence, not evasion.

**Fallback, only if you end up presenting with the verdict still open.** Don't improvise this;
name the open choices precisely so it reads as judgement rather than an excuse:

> "I'm stopping short of the recommendation today rather than giving you a soft version of it.
> **Three choices are still mine to make: the accuracy target the answer is quoted against,
> whether I quantify on the principal line or the summed shell, and which sum-peak settings I
> report as primary.** All three change how the result is *stated*; none of them change the
> machinery."

And with your supervisor in the room, turning it into a question is the better move:

> "The target is the one I'd genuinely value your view on. It's a stated choice with no literature
> anchor behind it, and it sets every number downstream."

**What not to do, in either case:** don't say "the data suggests…" and then hedge. A half-stated
conclusion is worse than a deferred one — it invites the follow-up you can't answer, and it spends
the credibility the rest of the talk just earned.

---

## Timing

**Five beats, ending on the handoff to your conclusions.** There is no closing beat by design —
a middle section shouldn't have one, and Beat 5's one-currency finish already points forward.

| | Beats | Notes |
|---|---|---|
| **4½ min (cut)** | Frame → 1 → 2 (density only) → 3 → 5 | Drop Beat 4 entirely, plus the counting-statistics sub-beat and the sum-peak anecdote. Keep the ρ·t failure and the two-overlaps split; they are the two moments that are *yours*. |
| **7 min (core)** | All of the above as written | |
| **10 min (expand)** | Add: fault-injection detail (Beat 1), provenance verification (Beat 4), the dose-regression story (below), and — of the four sum-peak switches — that the two moving the answer are what the level multiplies and what it's measured against, while the physics details barely register (Beat 5) | |

*Spare anecdote, if you have room or the sum-peak one has already been used:* **the dose
regression.** Before regenerating every output I hashed them all. Afterwards, sixteen of seventeen
were byte-identical and one had changed that shouldn't have — a function default had regenerated a
file **nine times noisier, with every column heading and row count unchanged.** Exactly the shape
of failure the whole approach exists to catch. Fixed, regenerated, hash-identical to the original.
*Fits Beat 1, whose theme is making silent failures loud.*

**If you only get three minutes:** the frame, the ρ·t failure, and "the sum peak is a bias, the
overlap is variance — and where I can't know a number I sweep it." Those three land the
methodology as a *designed* thing.

---

## Handle with care — Walther is in the room

| Topic | The move |
|---|---|
| **Density differs from his published paper** | Not a problem — **he told you to use these values** (personal communication, 2026-07-19). Attribute it in one flat sentence and move on. The sentence is for the second marker, who doesn't know the provenance; for Walther it's just accurate. Don't hedge, and don't pre-emptively defend it. |
| **As K/L beats Ga K/L as the thickness proxy** | Never "the paper used the wrong axis." Use: *"his data couldn't have revealed it — two compositions at unswept thickness makes the dependence invisible. It's an unobservable in the design, not a mistake in it."* True, and generous. |
| **His 15% sum peak was fitted, not measured** | He told you this himself, in writing. Attribute it: *"as he explained to me, it was chosen to force agreement."* Neutral, not a critique. |
| **The Bi M 1.5× cross-code discrepancy** | If it comes up: state the number (1.506 ± 0.020, three independent lines of evidence) and then **stop**. Cause unidentified. Do not speculate on a mechanism — one hypothesis has already been wrong. |
| **Bi K included even though he calls it too hard** | Method framing only: the objective names it, so measuring the failure is stronger than asserting it. **Don't give the outcome** — that's LO3's result. |

---

## Q&A defence bank

*Method questions only. Anything that reaches for a result routes to §"If you're asked before the
conclusions" — defer it, don't answer it early.*

**"Why MC X-Ray rather than CASINO?"**
CASINO lets you change physical models but not detector properties, and it doesn't compute
sub-lines — no Lα, Lβ, Lγ separately. This work needs both the sub-lines and the detector
behaviour. (This is Walther's own answer, so it's safe ground.)

**"Why is your density different from the paper?"**
Lead with the provenance, because it settles the question immediately: *"Those are the values
Professor Walther advised me to use — they revise his paper. Both codes auto-mix the elemental
densities, and GaAsBi is covalently bonded, so the auto-mix is the wrong picture."*

**Then, only if they press on how much it matters** — this is where the cancellation argument
earns its place: k\*-factor calibration is self-correcting against a density offset, because you
calibrate and invert on the same assumption. Evidence that this holds in practice: k\* agrees with
the published Figure 4 value to 3% despite a 6.2% density difference and a different code.

*Be precise about what that supports.* Three things differ between the two numbers — code,
density, and how the constant was derived — so it is **consistent with** the offset cancelling
rather than proof of it. If you want it stronger, the direct evidence is that k\* for that route
is flat to 0.66% across a 512× change in thickness and 0.006% across composition, i.e. it isn't
tracking absorption at all.

**"A cross rather than a grid is a weakness, isn't it?"**
It was, and I tested it rather than assuming it. The interior isn't interpolable — 23% error at
the thick end. That's why the third arm exists. **Remaining limitation, state it before they do:**
that third arm is a single composition at the thick end, so I've established that the effect
exists and roughly how big it is, not how it varies across composition. A ten-run arm at x = 0.10
would map it, at about two hours of compute.

**"At what thickness did you validate the recovery?"** ⚠️
**100 nm — all of it.** Verified 2026-08-20: `roundtrip_recovered_x.csv`,
`roundtrip_heldout_as_k_l.csv`, `counting_uncertainty.csv` and `error_budget.csv` each carry
exactly the five Set B runs, and every one is at 100 nm. Don't be surprised by this question:

> "All the quantification results sit at 100 nm — that's where the composition arm is. The
> thickness behaviour is characterised separately, through the k\* calibration across ten
> thicknesses and the corner analysis, but the round trip itself hasn't been run at other
> thicknesses. **The data to do it already exists — the low-bismuth arm spans 32 to 1024 nm — I
> just haven't pointed the recovery at it yet.**"

Honest, bounded, and it names the fix. That last sentence is what stops it sounding like an
oversight.

**"Why didn't your composition arm already show that?"**
Because it sits at one thickness. The effect grows with thickness — 1.5% at 32 nm up to 26.3% at
1024 nm — so a single slice at 100 nm catches it near its smallest and it reads as negligible.
Seeing it needs a second composition swept across thickness, which is what the third arm is.

**"Why do gallium and arsenic behave differently?"** ⚠️
**Not established — don't improvise one.** See the warning in Beat 3. *"I haven't established the
mechanism; it would need cited mass attenuation coefficients for the alloy at those energies. What
I can say is the effect is real, 26% against 7% at matched thickness, and large enough to
determine which ratio I use."*

**"Why sweep the sum peak rather than use the published 15%?"**
Because it was fitted to close a disagreement, not measured from a pile-up rate — and it's
entangled with a bismuth M value that differs from mine by a factor of 1.5. It doesn't port.

**"How do you know the wrapper writes correct input files?"**
Byte-for-byte regression against a validated reference set, with every difference classified —
plus deliberate injection of each known silent failure. Five out of five caught.

**"Is your counting-statistics treatment just Poisson?"**
Poisson on the stored detected intensities, but propagated *numerically through the whole
recovery* rather than through a closed-form formula, so the indirect path through the thickness
proxy and the shared-line correlation are included by construction. And first-order propagation
stops being meaningful past about 30% relative — those rows are flagged, not corrected.

**"Principal or summed line definition?"**
Legitimate method answer, and it's honest: *"Both are computed and stored for every ratio and
every k-factor — they differ by 40 to 90%, so it isn't cosmetic. Which one the final
quantification uses is one of the three choices I've still got open, and whichever I pick has to
be declared prominently in the methodology because of how far apart they are."*

**"Does MC X-Ray include secondary fluorescence?"** ⚠️
**You do not currently know, and it has never been asked.** Best answer, and it's a good one:
*"I haven't established that for MC X-Ray — I know your own simulations exclude it, and I'd want
to confirm rather than assume. It's on my list to ask you."* Turning it into a question for him is
better than a hedge. **Don't claim either way.**

**"What's actually yours, as opposed to the paper's?"**
The single most likely marker question. Answer it **at the level of method**, which is both true
and keeps you inside today's scope:

> "The replication is verification — reproducing the published constants to a few percent proves
> the pipeline works, it doesn't answer the research question. **What's mine, methodologically, is
> three things.** One: mass-thickness is not a sufficient absorption coordinate, which changes
> which K/L ratio you should use as a thickness proxy — and that's a measurement, not a
> preference. Two: the two overlaps are different in kind, one a bias and one a variance, and
> separating them by detector resolution changes how each has to be modelled. Three: all three
> error mechanisms converted into one currency, with every unknown swept rather than assumed
> — which is what lets the conclusion be quoted as a robustness statement instead of a single
> number."

---

## Numbers card — every row re-derived from the files, 2026-08-20

*Not transcribed from `REPORT.md`. Each figure below was recomputed from `Aggregated\*.csv` or
called directly out of the module, because these are the numbers you say out loud in front of
your supervisor. Three needed correcting against the prose — flagged inline.*

**Method and validation figures only. Ranking, measurability limits and the accuracy threshold are
deliberately absent — they live in `VERDICT_BRIEF.md` until P4.3 is settled.**

| | |
|---|---|
| Simulations | **21** (Set A 10, Set B 5, Set C 6) |
| Tests green | **297**, golden gate clean *(re-run and confirmed 2026-08-20)* |
| Fault injection | **5 of 5** silent killers caught |
| Aggregated outputs / figures | 23 / 6 |
| Density model | ρ(x) = 5.32 + 1.86x — endpoints **on Walther's advice** (pers. comm. 2026-07-19); linear-in-density interpolation is Ethan's choice |
| Lattice-route cross-check on 7.18 | implies a(GaBi) ≈ 6.36 Å vs 6.33 Å — the two pictures agree to **~2%** |
| k\* Bi Lα ÷ As Kα, pipeline check | this work **2.4161 ± 0.0051**; paper 2.490 ± 0.071 → −3.0%, **1.04σ — just outside**, not inside |
| Composition sensitivity @ 1024 nm, **matched thickness** | Ga K/L **−26.3%** vs As K/L **−7.0%** |
| Composition sensitivity @ 1024 nm, **matched ρ·t** | Ga K/L **−22.8%** vs As K/L **−1.6%** |
| Growth of the Ga K/L gap, 32 → 1024 nm | **1.5% → 26.3%** (17-fold) against a *constant* −6.2% density offset |
| Recovery, held out vs handed thickness | **0.00342** vs 0.00377 mean abs error |
| As K/L vs Ga K/L recovery error | As K/L better by **47%** |
| Sum peak vs Bi Mα | 43 eV = **0.47 FWHM** (merged) |
| As Kα1 vs Bi Lα | 297 eV = **1.75 FWHM** (resolvable) — REPORT §27 quotes 1.74; rounding, immaterial |
| Resolution model validation | **130.4 eV at Mn Kα**; Bi Lα1/Lα2 at 0.63 FWHM (merged) |
| Robustness of that split | resolvable at every corner of the ε/F literature range; ε·F would need **2.2×** its accepted value to overturn |
| Sum-peak switch combinations run | **16** (full factorial) |
| Scenarios swept | **27** (3 levels × 3 couplings × 3 doses) |
| Bi M cross-code factor | **1.506 ± 0.020**, cause unidentified |
| Detected photons at x = 0.01, 100 nm | Bi Lα **116**, Bi Mα **76** |

---

## Pre-flight — after the conclusions are written

You settle these on 21 Aug while writing the concluding slides (P4.3, `VERDICT_BRIEF.md`). **Once
you have, come back and reconcile this track against them** — three specific places:

1. **The accuracy target** — whatever you pick, Beat 5's ⚠ note currently says 10% as an example.
   Make it match, and keep the "a choice I've made and stated" framing either way.
   `VERDICT_BRIEF.md` §1 has the evidence; the re-run is one line if you change the number.
2. **Principal vs summed line definition** — deferred since 2026-07-25. Once chosen, the Q&A
   answer in this track should say which one you use, not just that both are stored.
   `route_ranking.csv` has both side by side; the summed rows all carry
   `overlap_is_lower_bound=True`.
3. **The route you recommend** — name it in Beat 5's near-miss line, which currently reads
   "the very route I'm going to recommend". Concrete beats generic there.

**Plus one that stays open regardless:** secondary fluorescence has never been put to Walther.
Consider asking him in the room — see the Q&A entry.
