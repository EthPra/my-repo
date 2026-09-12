# MC X-Ray wrapper — blueprint & status block

*Successor to the MC X-Ray hand-off block. That document froze the tool interface; this one defines the wrapper built on top of it. Interface facts are summarised, not repeated — the hand-off block remains the reference for file-format detail.*

**Open items at a glance:**
- **Three pre-sweep spikes** (unchanged, still pending): (i) windowless settable? — reshapes Set A; (ii) `Electrons per time slice` → native pile-up? — decides sum-peak route; (iii) `.sim` path resolution + seed — gates parallelism only.
- **Two author questions** (Lα2 inclusion; Bi M-lines beyond Mα) and **one supervisor question** (secondary fluorescence) — out or to be sent; gate comparison to Walther's numbers, not the build.
- **Two decisions with Ethan:** Set B statistical floor policy (fixed dose vs fixed statistics); acceptability of the analytic windowless fallback if spike (i) fails.
- **In build:** Stage 1 (input generator) + Stage 2 (parser), via Claude Code, gated on golden regression tests.

---

## 1 — Scope and stop-line

- **McXray-only.** Casino cross-check stays a manual step, outside the wrapper.
- The wrapper terminates at a **clean raw-intensities table + the three diagnostic ratios**, with every number traceable to its generating run. It does **not** perform ratio-to-x inversion, k*-calibration choices, or the hypothesis verdict — those are Ethan's (governance).
- Sum-peak handling is **in scope** (Stage 6), route pending spike (ii).

## 2 — Architecture

Two halves, deliberately decoupled:

**Run + store (freezes early):**

| Stage | Function | Status |
|---|---|---|
| 1. Input generator | RunSpec → six input files (templated off golden files; computes weight fractions, ρ(x)=5.32+0.20x, nm→Å; enforces CRLF + verbatim quirks) | **In build.** Gate: byte-accountable golden diff. Window param ATW-only pending spike (i). |
| 2. Output parser | `_XrayIntensities.csv` → tidy DataFrame (trailing-comma fix, stripped labels, keyed on Z, all intensity columns preserved, run_id attached) | **In build.** Gate: reproduces the 18-line golden table. |
| 3. Executor | Invoke exe per run, cwd=Sim, capture exit/stderr, distinguish sim-failure from crash. Inputs written flat in `Sim\` (required at run time), **copied** into `Results\` after completion; all ~19 outputs per run retained, `Results\` flat | Buildable now (single-run). Parallel variant gated on spike (iii); optional — 24 runs ≈ 80 min serial at 10⁶. |
| 4. Matrix generator | Set A/B specs → run list | Trivial; final count gated on spike (i): 24 runs, or 14 + analytic windowless. |
| 5. Aggregator | Concatenate parsed tables → one raw-intensity table + provenance manifest (spec → input files → outputs) | Draftable; testable only once multi-run data exists. |

**Derive (stays live while open questions resolve):**

| Stage | Function | Status |
|---|---|---|
| 6. Derivations | Three diagnostic ratios (Ga K/L, As K/L, Bi L/M vs thickness — reproduces Walther Fig. 1); sum-peak synthesis onto Bi Mα; sensitivity levels 0.1% / 1% / 10% (never 15% default) | After sweep. Reads the stored table ONLY — never triggers re-runs. |
| 7. Inversion + verdict | k* calibration, x recovery, hypothesis assessment | **Ethan's. Not automated.** |

**The load-bearing rule joining the halves:** the run loop stores raw, unprocessed intensities and nothing derived. Every open question (Lα2, Bi M-band, pile-up level, windowless) then costs a re-derivation from the stored table, never a re-simulation.

## 3 — Build sequencing and rationale

1. **Stages 1–2 first** (current step, via Claude Code) — the only stages with a golden regression target today. The validation run doubles as two acceptance tests: regenerate its inputs and diff (catches the silent unit/fraction killers); reparse its output and match the verified 18-line table. Nothing sweeps until both pass.
2. **Stages 3 (single-run) + 4 alongside** — command interface is fully resolved; matrix logic is trivial with window left as a free parameter.
3. **Spikes in parallel** — none blocks stages 1–4; spike (i) must land before the matrix is *finalised* and any window logic is written.
4. **Stage 5 after first multi-run data**, Stage 6 after the sweep.

## 4 — Known risks and their mitigations

| Risk | Standing mitigation |
|---|---|
| Silent input corruption (nm-in-Å, atomic-in-weight, density=0) — runs fine, wrong physics | Structural golden diff (strict) + value accountability: every delta enumerated and classified (intended / formatting-only / documented deviation / unexplained→FAIL). **Note this risk already materialised — the validation run ran at density=0.** |
| Golden files treated as physics ground truth when they are only format ground truth | Explicit in CLAUDE.md and the build prompt. Physics values come from cited sources; golden authorises syntax and field semantics only |
| Docs written from intent rather than from the artifact (the hand-off block states the run used ρ=5.34; the file says 0) | Assert from files, never from prose. Applies to row counts and line energies too ("18" is a Table-1 cross-check count, not the CSV's 21 rows) |
| Windowless hard-coded → Set A halves, Assumption-2 window arm dies | Spike (i) before matrix freeze. Fallback: analytic windowless via per-line `Detector efficiency` factorisation + Henke/NIST window transmission — testable on the validation run; methodological downgrade (computed, not simulated) requiring Ethan's sign-off |
| Parser drift on unseen output variants | Strict numeric parsing (non-numeric = error, never coerced NaN); anomalies stop the run |
| Derived numbers invalidated by atomic-data answers (Lα2, M-band) | Raw-only storage rule; constant scale error on Bi L cancels in the calibrate-then-invert round trip regardless |
| Bi Mα statistics at low x (Set B floor) | Pending Ethan's policy decision (§5); affects whether `n_electrons` is per-run |

## 5 — Decisions pending with Ethan

1. **Set B floor policy.** "Line vanishes" at fixed dose (10⁶ everywhere — a statement about this measurement) vs fixed statistics (raise trajectories at low x until noise isn't the limiter — a statement about the physics). Decides whether trajectory count varies per run.
2. **Analytic windowless fallback** — pre-authorised, or revisit only if spike (i) actually fails?
3. *(Settled: McXray-only; stop-line at intensities/ratios table; sum peak in scope; DetectorNoise=50; per-line table not spectrum; no 15% pile-up default.)*

## 6 — Deliverables ledger

| Artifact | Produced by | Status |
|---|---|---|
| Golden input set (6 files) + golden `_XrayIntensities.csv` | Validation run (T2.2) | **Done, with caveats** — format ground truth only; carries `UserDefinedMassDensity=0`. Copy into `golden/`, read-only |
| **Corrected-density baseline run** (x=0.1, 100 nm, ρ=5.34) | Generator's first real job, then Ethan runs it (~20 s) | **New.** Restores a physically-valid baseline and yields a free density-sensitivity data point. Does not gate the build |
| `claude_code_prompt.md` (stages 1–2 build prompt) | This session | Done |
| `CLAUDE.md` (repo-level context) | This session | Done |
| Stage 1+2 code + passing golden tests + `REPORT.md` | Claude Code session | Next |
| Spike results (i)–(iii) | Ethan, hands-on | Pending |
| Author / supervisor answers | External | Pending |
| Final matrix (24 or 14+fallback) | After spike (i) | Blocked |
| Raw-intensity table + provenance manifest | Stage 5 | Future |
| Ratios + sum-peak sensitivity | Stage 6 | Future |