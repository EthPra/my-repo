# Conclusions & Future Work — presentation talking track

> **⚠ SUPERSEDED 2026-08-23 by `PRESENTATION_SCRIPT.md` §C. Do not deliver from this file.**
> It contains a claim now known false: *"Bismuth K fails on photon starvation … twelve times the
> acquisition time"* (§② and the Q&A bank). That was computed against the 10% relative accuracy
> bar, retired on 2026-08-21. Against Δx = 0.01 Bi K clears at the *shortest* acquisition swept.
> The correct rejection is **range** — Bi K crosses the target inside the composition range in
> 18 of 27 scenarios; Bi L crosses in none. Kept for history and for the audience note in §Scope,
> which still stands.

*Drafted 2026-08-21 for the MSc presentation to Walther (supervisor) + one other academic marker
from a broader technical background. Source: `VERDICT_BRIEF.md`, `decisions.md`, and the current
`Aggregated\*.csv`. Not a script to read aloud verbatim; it is the spoken argument, beat by beat,
with the lines that should land set in **bold**.*

**Slot: 2 minutes.** Companion to `SLIDES_CONCLUSIONS_BRIEF.md` (what goes on each slide).

---

## Scope — read this before anything else

The methodology section deliberately withheld the verdict so this section could land it. That
means the handoff line at the end of methodology — *"which is what lets me give you the
recommendation as a robustness statement rather than a single number"* — is a **promise this
section has to pay off in its first fifteen seconds.** Lead with the answer. Do not rebuild the
argument; you already earned it.

**Audience note.** One marker is your supervisor and knows this material cold; the other is an
academic from a broader technical background. Write for the second one. That means: say what a
line pair *is* for in one clause, prefer "the bismuth L-alpha line measured against arsenic
K-alpha" over route notation, and never let a mechanism name (sum peak, overlap (i)) appear
without the two-word reminder of what it does.

---

## The two-minute version — this is the one you deliver

*~275 spoken words — **2:07 at 130 wpm, 1:54 at 145.** Three landmarks. **Learn the landmarks,
not the sentences.***

| | landmark | budget |
|---|---|---|
| ① | The verdict | 15 s |
| ② | Why it holds | 70 s ← *the core* |
| ③ | Limitations and future work | 35 s |

**① The verdict** — *15 s. Say it flat and unhedged. Then pause.*

> "So — the recommendation. **Bismuth L-alpha, measured against arsenic K-alpha, using the single
> strongest line of each.** That pair quantifies bismuth reliably down to **an x of about one
> percent**, at the same acquisition time used in the paper this work builds on."

**② Why it holds** — *70 s. The core. Three failures, then three robustness checks.*

> "It wins because the other candidates fail for reasons that don't go away.
>
> **Bismuth M fails on the sum peak** — the detector artefact that fakes counts directly onto the
> line you're measuring. That's a *bias*: it's systematically wrong in one direction, and **no
> amount of counting longer fixes it.** It fails in all twenty-seven scenarios I swept.
>
> **Bismuth K fails on photon starvation.** It's genuinely the most absorption-immune line in the
> system — but it's so weak you'd need **twelve times the acquisition time** to use it. That's a
> real negative result, not an omission.
>
> **Bismuth L passes all twenty-seven.** And its own weakest point is the arsenic–bismuth overlap
> — which is **one of the two overlaps this project set out to characterise in the first place.**
> So the limiting factor on my recommendation is a quantity I've measured, not a gap I've left.
>
> And it's robust three ways. It wins **under my own accuracy target and under Professor
> Walther's published one.** It wins **under both definitions of what counts as a line.** And I
> checked it **directly across the full thickness range, thirty-two nanometres to a micron** —
> the calibration transfers with an error of **two thousandths of one percent.**"

**③ Limitations and future work** — *35 s. Forward-looking, not apologetic.*

> "Three things I'd do next. **The overlap strength is swept, not measured** — the conclusion
> survives the worst case, but measuring it directly would replace an assumption with a number.
> **I know the method works down to an x of one percent, but not where it stops** — two more
> simulations would bracket that floor. And there's **an unresolved discrepancy in the bismuth M
> data between two independent codes** that I've bounded but not explained.
>
> None of those touch the recommendation — but they're the honest next steps."

---

### If you find yourself running early

Add, in this order — each is self-contained:

1. **The atomic-percent clarification** (10 s) — *"and to be clear, an x of one percent means
   half a percent of the atoms — x is the fraction of the group-five sublattice."* **Genuinely
   worth adding for the non-specialist marker**, and it pre-empts a likely question.
2. **The 100× axis result** (15 s) — *"and the arsenic axis I chose transfers about a hundred
   times better than the gallium one across that thickness range."*

### If you're running long

Cut ③ to two items (drop the Bi M cross-code discrepancy — it's the least likely to be probed).
**Never cut the three robustness checks in ②** — they're the entire reason the verdict is worth
anything, and they're what the methodology section spent five minutes setting up.

---

## Q&A bank — the four most likely probes

**"Why Δx = 0.01 and not a relative percentage?"**
> Walther's own paper states it: measuring to 0.5 at%, an x of 0.01, "or better is a real
> challenge." A flat relative target gets *harder* in absolute terms as x shrinks — it would bite
> hardest exactly in the low-bismuth regime this project added. But the ranking is the same
> either way; I checked both and stored both.

**"Isn't 'summed' the standard thing commercial software does?"**
> Yes — and it scores slightly better on paper. But every summed result carries a flag: summing
> pulls in sub-lines that overlap *other* elements, and my model only costs one of those overlaps.
> So its apparent advantage is partly an uncosted risk. Principal is the number I can fully
> defend, and the winner is the same under both.

**"Why should I trust a simulation-only result?"**
> Because the simulation knows the true answer. Every recovered composition is graded against a
> ground truth the recovery never sees — which is exactly what you can't do with real specimens,
> and it's why the error budget can be decomposed by mechanism at all.

**"Bi K is absorption-immune — isn't that worth pursuing?"**
> Physically, yes, and that's the interesting part of the negative result. Practically it needs
> twelve times the dose, and beam damage sets in long before that. I'd call it ruled out for this
> material at these thicknesses, not ruled out in principle.
