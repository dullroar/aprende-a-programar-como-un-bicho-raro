# S5 gate (iteration 477, task S5-999)

Scope: the 45 S5 family tasks and the 6 audits (S5-audit-1 to 6).

## Evidence

- Queue: every S5-fam-* and S5-audit-* task is `done`; none blocked. `python3 tools/next_task.py --check`: 272 tasks ok.
- Oracle matrix: 45 family reports in `translation/part2/reports/`, each with a verdict. 30 families localized (comments only, oracle PASS; EXC-542 to EXC-586). 15 left English with an exception row and `NOT TESTED` and the reason: 5 `lessons/` build-tooling families (no oracle runner), 8 `src/` families with no entry image or needing network (Go, Java, Kotlin, Modern, Rust, Linq1, Linq2, xaml), and regex-dotnet and regex-pcre2 (oracle fails on the unmodified English baseline).
- `python3 tools/lock_code.py --verify`: ok, 230 frozen files match the manifest; `translation/localized-code.sha256` holds 109 rows for the localized files.
- `python3 -I tools/part2_inv.py --check`: 0 findings (the identifier ledger is empty: no identifier was renamed, categories and strings kept English).
- `python3 -I tools/verify.py --fast`: OK.
- `python3 -I tools/verify.py --release --no-gates`: all checks pass (the English gates are skipped by design).

## Defects found by the gate and fixed narrowly

1. Line-anchor meaning (16 records): the seeded `expect` text held the English comment that S5 translated; the lines did not move. Trimmed each `expect` in `translation/line-anchors.jsonl` to the code part of the same lines (script `translation/work/reanchor.py`; the check still fails when the statement changes). `src/tcl/timecards.tcl` 32-34 has only comment text, so its record now expects the Spanish comment.
2. `tools/negative.py` lock fixtures copied the working `src/forth` files, which are now localized, against the English manifest hash. They now use the pinned English bytes (fallback: working file). `test_negative.py` and `test_breakage_pilot.py` pass.

No check was weakened: the negative fixtures still fail as expected (68 of 68).

## Result

S5 gate **PASS**.
