# Prompt to paste after /compact

*Copy everything below the line into the chat after compacting — or just say
"Read NEXT_SESSION_PROMPT.md and follow it."*

*Updated 2026-09-10: the project is in its **write-up phase**. The build is finished and the
verdict is reached. If you are reading this expecting simulation work, there isn't any.*

---

MC X-Ray wrapper — GaAsBi EDXS dissertation. **We are writing the dissertation. Nothing else.**

**Deadline: Sunday 14 September 2026, 14:00.** Single PDF ≤ 20 MB via Turnitin, main body
≤ 70 pages.

**Read these first, in this order:**

1. `CLAUDE.md` — governance (physics is never invented; scientific judgement is mine, not yours)
   and the silent-killer trap list. Non-negotiable, still.
2. `DISSERTATION_FRAMEWORK.md` — the chapter map (§1–3), appendices (§4), the cross-cutting
   write-up rules (§5), the Gantt material for Ch1.5 (§7), and the **five-day plan with its
   checkpoints and cut line (§8)**.
3. `DISSERTATION_NUMBERS.md` — **the results number sheet.** Every value Ch5–Ch6 will quote,
   re-read from `Aggregated\*.csv` on 2026-09-10 under production settings, each with its
   file → column → filter. **§10 is a blacklist of retired numbers** — if one of those appears in
   a draft, it is a bug.
4. `dissertation/` — nine chapter skeletons; `dissertation/README.md` indexes them and holds the
   two drafting rules.

`REPORT.md` (technical, append-only, current through §32) and `writeupTODO.md` (what the
methodology must *declare*) are the source material. `REPORT_PLAIN_ENGLISH.md` contains
superseded numbers — do not draft from it.

## How we work now (changed 2026-09-09)

**You draft dissertation prose; I direct and verify.** The old rule — "Claude does mechanical
prep, not prose" — is retired. The School publishes no AI-use policy, so AI-assisted writing is
permitted. The binding constraint is **my review bandwidth**, not composition.

- Each session: ~10 min brief (which §, which sources, what it must say, what it must *not*
  claim) → you draft → I correct and approve.
- **I write three things myself:** Ch6.1 (the verdict — lift verbatim from `PRESENTATION_SCRIPT.md`
  §C ⓵, do not paraphrase it), Ch1.5 (project management), the Individual contribution page.
- **Every number you type carries its file/column/filter in an inline comment**
  (`<!-- NUM: value | file.csv | column | filter -->`). Saturday's check reads those comments.
- **Nothing counts as done until I have read it.**

## The failure mode to watch

A drafting assistant is fastest at exactly the thing this project is most exposed to: **fluent
prose wrapped around a stale number.** `DISSERTATION_FRAMEWORK.md` §5 rule 1 and
`DISSERTATION_NUMBERS.md` §10 both list values already wrong in this repo's own prose. Never lift
a number from prose — including from `REPORT.md`. Go to the CSV, or to the number sheet, which
carries the CSV's provenance.

Two specific traps that will bite:
- **"Across the range" and "at x = 0.01" are different counts and both are correct**
  (`DISSERTATION_NUMBERS.md` §1). Label which one, every time. Never "fix" one to match the other.
- **Filter to `principal` before quoting any aggregate.** Several figures in the framework were
  originally means over both line definitions; they have been corrected, but the habit matters.

## State as of 2026-09-10

- **Build complete.** 21 production runs, **304 tests** green, **28** CSVs in `Sim\Aggregated\`,
  **6** figures in `Sim\Figures\`. `python run_analysis.py` regenerates every derived output;
  `python -m figures.make_all` renders all six figures. Hash `Aggregated\` before any full
  regeneration.
- **Verdict reached** (2026-08-22) — `VERDICT_BRIEF.md`, `PRESENTATION_SCRIPT.md` §C.
- **Presentation delivered and closed** — `PENDING_EDITS.md`.
- **Day 0 prep done** (2026-09-10): number sheet and chapter skeletons exist, as above.
- **Six filter discrepancies found and all resolved** by me on 2026-09-10 — see
  `DISSERTATION_NUMBERS.md` §0. Rulings: quote `principal` throughout; Ch5.2 uses the
  `matched_rho_t` block throughout.

## Still to do — all of it is writing

| | |
|---|---|
| **Ch4** | Methodology, 13 pp. Was scheduled Wed 10; **not started.** |
| **Ch2.2–2.4** | The largest unwritten block (~5 pp). Draft with the Walther PDF open. |
| **Ch3** | Theory, 5 pp. |
| **Ch5** | Results, 14 pp — the number sheet is the input. |
| **Ch6, Ch7, Ch1** | Discussion, Conclusions, Introduction. 6.1 and 1.5 are mine. |
| **Front matter, appendices, figure captions** | Abstract written last. |

⚠ **Ch2.1 (LO1) is already drafted** — ~3,400 words in `Lit review draft.pdf`. It needs pasting
in, a hand-off paragraph (mine), and the two corrections listed in `PENDING_EDITS.md`.

## How I work

- Ask rather than decide when a design question isn't settled — but if you can *measure* the
  answer instead of asking, do that and tell me what you found.
- Surface anomalies immediately, and say plainly when something you told me earlier was wrong.
- Your build-time estimates run 6–8× long. My review time and the write-up do not compress.
- I lose the chat history regularly. Keep the repo files current enough that a cold start works.
