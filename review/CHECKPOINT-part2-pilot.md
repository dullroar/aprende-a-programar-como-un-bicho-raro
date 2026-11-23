# Checkpoint for the Part II pilot (code localization)

Iteration 421 · `S4-chk-1` · 2026-11-22

The Part II pilot (S4-001 to S4-005) is ready for an external review. **The honest summary: the pilot did not localize anything.** Docker is denied in the unattended `claude -p` (dontAsk) mode, so `tools/oracle.py` could not run, and the rules say a family without oracle proof stays English. All four pilot families are `NOT TESTED`.

## 1. Diffs to review

There are none in protected files. Compare the working tree with pinned English commit `48a4429c0a22b2aac628b256a50c07d1816bcb80`:

- Non-Markdown files under `src/`, `lessons/solutions/`, fixtures and data: byte-identical (`python3 tools/lock_code.py --check`: ok).
- `translation/identifier-map.jsonl` and the identifier ledger: empty. No identifier, comment or display string was changed.
- What the pilot did add (all Markdown or registry files):
  - `translation/part2/reports/S4-001-forth.md`, `S4-002-csharp.md`, `S4-003-cobol.md` (NOT TESTED reports)
  - `translation/exception-register.jsonl`: EXC-539 (Forth), EXC-540 (C#/LINQ/XAML), EXC-541 (COBOL, regex-pcre2)
  - `translation/reviews/part2-pilot.md` (pilot review, recall 10/10 on deterministic detectors; model-reviewer recall not re-run)
  - `translation/part2/pilot-measurements.md` (S4 gate)

## 2. Oracle report

| Family | Oracle verdict | Reason | Record |
| --- | --- | --- | --- |
| Forth | NOT TESTED | docker denied | EXC-539 |
| C#, LINQ, XAML | NOT TESTED | docker denied | EXC-540 |
| COBOL | NOT TESTED | docker denied | EXC-541 |
| regex-pcre2 | NOT TESTED | docker denied | EXC-541 |

The S4 gate clause "oracle PASS for each pilot family" is **not met**. The S0-003 sandbox self-test is also still owed. `part2_inv.py --check` (I28 to I31): 0 records, 0 findings (vacuous).

## 3. Measured cost per family

| Task | Family | USD | Seconds |
| --- | --- | --- | --- |
| S4-001 | Forth | 0.2397 | 37 |
| S4-002 | C#, LINQ, XAML | 0.1981 | 25 |
| S4-003 | COBOL, regex-pcre2 | 0.2816 | 27 |
| S4-004 | pilot review | 0.2528 | 42 |

Total 0.9722 USD. **These measure classify-and-refuse iterations, not localization.** Do not use them to budget S5 (about 40 families). A real measurement needs a Docker-capable session. Details: `translation/part2/pilot-measurements.md`.

## 4. Open decision 11 (plan section 16): the four card categories

Default in force: `Meetings`, `Coding`, `Debugging`, `Learning` **stay English** in code, output and fixtures (about 705 occurrences); prose glosses them once per chapter (*reuniones*, and so on). The pilot produced no evidence on cost, so there is no measured reason to change the default. Options:

1. **Keep English (default, recommended).** Cheapest, reversible, the reader can match prose to program output.
2. **Localize the categories** in code, output and fixtures. High cost to reverse after bulk; needs oracle proof per family including fixtures that embed the names.

Please also decide how to unblock the oracle, since it gates everything in S5:

- (a) Run the oracle steps in a Docker-capable session (S0-003 self-test, then pilot families), or
- (b) Allow docker in the loop's permissions, or
- (c) Accept that Part II ends with comments and identifiers left English, and skip S5.

## What to do next

Record decision 11 (and the oracle choice) in `translation/decisions.md`, then remove `loop/STOP`. The next task, S4-006, generates the S5 family tasks and applies decision 11.
