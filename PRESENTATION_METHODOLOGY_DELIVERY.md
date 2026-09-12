# Methodology — presentation talking track

*Drafted 2026-08-20 for the MSc presentation to Walther (supervisor) + one other academic marker.
Source: `REPORT.md` §§1–32, trimmed for delivery. Not a script to read aloud verbatim; it is the
spoken argument, beat by beat, with the lines that should land set in **bold**.*

**Slot: 5 minutes** (confirmed 2026-08-20). §The five-minute version is what you deliver.
Everything after it is reference — the full argument, the reserve material, and the Q&A bank.

---

## Scope — read this before anything else

**This track covers method. It does not state the verdict — because the concluding slides do,
a few slides later.** That is talk structure, not an absence: front-running your own conclusion
weakens both sections.

So the job of this section is not to withhold anything. It is to **earn the conclusion before it
arrives**:

> **"Here is how the measurement is constructed, and here is how every unknown in it is handled —
> so that when I tell you which route wins, you already know why you can believe it."**

Every "I swept it rather than assumed it" in here is a setup, not an apology. Deliver it that way.

⚠ **One dependency.** This assumes the verdict is settled before you present (Ethan is writing
the concluding slides from 2026-08-21). If for any reason you end up presenting with the
conclusion still open, see the fallback line in §"If you're asked before the conclusions".

---

## The five-minute version — this is the one you deliver

*701 spoken words — **5:24 at 130 wpm, 4:50 at 145.** Time it once out loud and you'll know which
you are. If you land long, ③ collapses to a single clause and buys you 25 seconds; that's the
designed release valve. Six landmarks, in order — **learn the landmarks, not the sentences.**
You know all of this, and the wording will come. Everything below this section is reference: the
fuller argument for your own understanding, the reserve lines, and the Q&A bank.*

| | landmark | budget |
|---|---|---|
| ① | The frame | 28 s |
| ② | The wrapper, and a gate that bites | 42 s |
| ③ | Nothing invented | 31 s ← *the release valve* |
| ④ | The matrix grew because a measurement told it to | 74 s ← *yours* |
| ⑤ | Three degradations, one currency | 136 s ← *the core* |
| ⑥ | Hand off | 12 s |

**① The frame** — *25 s*

> "The methodology here isn't 'I ran a Monte Carlo code' — running the code is the easy part.
> **The hard part is that almost every way of getting it wrong produces a result that looks
> completely normal.** So the methodology is really a set of decisions about making silent failures
> loud, and about handling the physics inputs nobody can cite."

**② The wrapper, and a gate that bites** — *45 s*

> "Twenty-one simulations, six input files each, and the failures don't announce themselves.
> Lengths are in Ångströms, not nanometres — and the manual says otherwise — so a foil ten times
> too thin runs perfectly. Composition is weight fraction, not atomic. Density has to be set
> explicitly or the code silently auto-mixes elemental densities. **None of those throw an error.**
>
> So every generated input is diffed byte-for-byte against a validated reference set — and to
> check the gate actually bites, **I injected each of those failures deliberately. Five out of
> five caught.**"

**③ Nothing invented** — *30 s*

> "Every physical constant traces to a source, or the code stops. The one worth naming is density:
> both MC X-Ray and CASINO estimate it by interpolating the *elemental* metal densities, and
> GaAsBi is covalently bonded — so that estimate is silently the wrong physical picture. **On
> Professor Walther's advice** I use 5.32 and 7.18 as the endpoints and interpolate, which updates
> the values in his own published paper."

**④ The matrix grew because a measurement told it to** — *75 s. This one is yours — slow down.*

> "The run matrix is a cross — thickness at one composition, composition at one thickness. A cross
> assumes you can interpolate the interior, on the grounds that absorption depends on mass-thickness.
> **I tested that instead of relying on it, and it failed** — interpolating onto a low-bismuth arm
> is 23% wrong at a micron. And it isn't a density artefact: the density offset is constant, but
> **the error grows seventeen-fold with thickness.** So I added a third arm, at 1% bismuth.
>
> And that changed a choice I'd otherwise have made arbitrarily. The method uses a K/L ratio as a
> stand-in for thickness, so you never have to measure the foil. But **gallium's K/L ratio also
> tracks composition — 26% at a micron — and arsenic's doesn't, at 7%.** A stand-in that follows
> the unknown puts the unknown back into the coordinate meant to remove it. **So I index on arsenic
> K/L — and that's now a measurement, not a preference.**"

**⑤ Three degradations, one currency** — *120 s. The core.*

> "Everything I've shown you so far comes out of the simulation clean. **No real detector produces
> that spectrum.** Three things degrade it, and none of them are in the output file.
>
> First, I measured both peak overlaps against the detector's linewidth — because two peaks closer
> than about one linewidth merge into a single bump. **The sum peak sits at 0.47 — merged. Arsenic
> K-alpha against bismuth L-alpha sits at 1.75 — resolvable.** Different problems, different models.
>
> The sum peak is a detector artefact: two photons arrive together and are recorded as one event at
> their combined energy — which lands on bismuth M-alpha, so **it fakes the signal I'm measuring.**
> MC X-Ray can't produce one, so I synthesise it and propagate it through the entire recovery. The
> magnitude isn't measurable from my data, so I swept it, and the four modelling choices are
> switches — **I ran all sixteen combinations, and the route ordering is identical in every one.**
>
> The second overlap I **bounded rather than modelled** — doing it properly needs four physical
> inputs I can't cite, so I didn't invent them. And the two differ in kind: **the sum peak is a
> bias, systematically wrong in one direction; the overlap is variance, noisier but unbiased.**
>
> Third, counting statistics — a real acquisition holds finitely many photons, and at 1% bismuth
> that line is about 116.
>
> Three mechanisms in incompatible units, so the last step converts all of them into one currency:
> **error on the recovered composition.** And **nothing unknown gets a default** — pile-up level,
> overlap leakage and dose are all swept, **twenty-seven scenarios** — and where the error curve
> never crosses inside the range I actually simulated, the code **reports which side it fell on
> rather than inventing a number.**"

**⑥ Hand off** — *10 s*

> "Which is what lets me give you the recommendation as a robustness statement rather than a single
> number — and that's where I'm going next."

---

### If you find yourself running early

Re-insert in this order — each is self-contained and priced in §"Cut from the spoken beat":

1. **The near-miss** (25 s) — the model the resolution measurement ruled out. Best value.
2. **Store raw, derive cheaply** (20 s) — *"the run loop stores raw intensities only, so every
   derived number is re-derivable without re-running a simulation."*
3. **The cancellation anecdote** (45 s) — only if comfortably inside time.

### If you're running long

Cut ③ to a single clause — *"every constant traces to a source, and the density model is
Professor Walther's own revision"* — and drop the second half of ④. **Never cut ⑤.**

---

---
