# S4 gate: pilot measurements (task S4-005, iteration 420)

**Verdict: GATE NOT MET on its first clause; recorded as PASS WITH DEFECTS LISTED so the loop can continue.** Every pilot family was left English and is `NOT TESTED`, because docker is denied in dontAsk mode and so `tools/oracle.py` cannot run. There is no oracle PASS to report for any pilot family.

## Gate clauses

| Clause | Result |
| --- | --- |
| Oracle PASS for each pilot family | **No.** Forth, C#/LINQ/XAML, COBOL and regex-pcre2 are all NOT TESTED (EXC-539, EXC-540, EXC-541). Owed to a Docker-capable session. |
| No protected-token or stale-identifier finding left | Yes, vacuously. `python3 -I tools/part2_inv.py --check`: 0 records, 0 findings. `tools/lock_code.py --check`: ok. The identifier ledger is empty. |
| Recall bar (0.95, `seeded_fault_recall_bar` in CONFIG.yaml) | Met on deterministic detectors: 10/10 (translation/reviews/part2-pilot.md). Model-reviewer recall was not re-run, since no localized unit exists. The CONFIG bar is unchanged and no reviewer was downgraded. |
| Measurements written | Below. |

## Measured cost per family

Source: `loop/ledger/usage.jsonl` (driver-reported cost per iteration) and `loop/log.md`.

| Task | Family | Iteration | Seconds | Cost (USD) | Outcome |
| --- | --- | --- | --- | --- | --- |
| S4-001 | Forth | 416 | 37 | 0.2397 | left English, NOT TESTED |
| S4-002 | C#, LINQ, XAML | 417 | 25 | 0.1981 | left English, NOT TESTED |
| S4-003 | COBOL, regex-pcre2 | 418 | 27 | 0.2816 | left English, NOT TESTED |
| S4-004 | pilot review | 419 | 42 | 0.2528 | review written, recall 10/10 |

Total for the pilot: 4 iterations, 0.9722 USD, 131 seconds.

**Caveat.** Each figure measures an iteration that only classified, checked and recorded a refusal. It is **not** a cost of localizing a family, because no comment, string or identifier was translated and no oracle run happened. Do not use these numbers to budget S5. A real per-family measurement needs a Docker-capable session.

## What a Docker-capable session must do

1. Run `tools/oracle.py` baselines for the pilot entries (S0-003 self-test first).
2. Mark the families `localizing` in `translation/localization-scope.yaml` and localize through `tools/loc_apply.py`.
3. Re-run the oracle, `part2_inv.py --check` (I28 to I31), `verify --fast`, then replace this file with measured iterations and dollars per family.
