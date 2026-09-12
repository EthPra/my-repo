# Appendices A–H

**Unmarked and uncounted. ⚠ Nothing essential may live here** — the handbook is explicit. If a
marker needs it to follow the argument, it belongs in the main body.

**Drafted Sat 13 PM. A–D and G are generated mechanically; E, F, H are first to cut (cut 1).**

---

| App. | Content | Generate from | Priority |
|---|---|---|---|
| **A** | **Run matrix** — all 21 run_ids with thickness, x, ρ, trajectories, wall time | `Aggregated\provenance_manifest.json` | keep |
| **B** | **Annotated input-file templates** (`.sim/.sam/.mic/.par`) showing the load-bearing fields and the trap list | `Golden\` (read-only), `../CLAUDE.md` trap list | keep |
| **C** | **Physical constants with sources** — densities, atomic weights, line energies, ε, F | `spec.py` source comments; REPORT §10, §12.1 | keep |
| **D** | **Output schema** — the 21-row intensity CSV format; `Aggregated\` file inventory, one line each | `../ORIENTATION_MAP.md` §3; REPORT §16.1 | keep |
| **E** | Full 27-scenario measurability table + 16-combination switch table | `measurability_limit.csv`, `route_ranking.csv`, `sumpeak_switch_influence.csv` | **cut 1** |
| **F** | Fault-injection record — the five faults and how each surfaced | REPORT §5 | **cut 1** |
| **G** | **Repository structure, module list, test count; how to regenerate everything** (`run_analysis.py`) | REPORT §32.1 | keep |
| **H** | Supplementary figures: k\* vs thickness, k\* vs K/L ratio | `../artifact\` | **cut 1** |

---

## Notes for generation

- **App. A:** 21 runs. Cross-check the count against `provenance_manifest.json` itself, not
  against prose.
- **App. B:** ⚠ `Golden/` is **read-only**. Copy from it; never regenerate, edit or clean it.
  The templates must reproduce the traps verbatim, including the `DetectorDiffusionLenght`
  misspelling and the CRLF-with-trailing-CRLF convention on the four authored files.
  **Say in the appendix text that golden files are format truth only, never physics.**
- **App. D:** the intensity CSV is **21 rows** (Ga 6, As 6, Bi 9) — *not* 18. "18 lines" is the
  count cross-checked against Walther's Table 1. Assert counts from the file.
  `Aggregated\` holds **28** CSVs as of 2026-09-10 (23 is the stale 17 Aug figure).
- **App. G:** **304 tests** (verified `pytest --collect-only`, 2026-09-10).
