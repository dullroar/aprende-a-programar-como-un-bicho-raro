# S4-001 batch report: Forth (src/forth, src/forth-weird)

Iteration 416. Verdict: **NOT TESTED. Family left English (frozen).**

## What was checked

- Scope file: `src/forth` and `src/forth-weird` stay `frozen` (3 files each: Dockerfile, check.sh, timecards.fs; README.md is Markdown).
- Oracle (`tools/oracle.py`) needs the sandbox container. `docker` exists on the host, but every Docker call is refused in dontAsk mode (same limit as S0-003 and S2-004). `gforth` is not installed on the host, and rule 1 forbids running example programs on the host.
- Without a container run there is no oracle PASS, so no comment, display string or identifier may change (plan 4.5, hard rule 1).

## Result

- No protected file changed. The scope file is unchanged (the family is not marked `localizing`).
- No PO entries, identifier-map rows, README, diagram or anchor edits.
- Exception recorded: `EXC-539` in `translation/exception-register.jsonl`.

## To finish (Docker-capable session)

1. Run `python3 tools/oracle.py` baseline for `forth` and `forth-weird` in the sandbox and record the semantic record.
2. Mark both families `localizing`, translate comments line for line, then display strings proven free of contract, then mapped identifiers, all through `tools/loc_apply.py`.
3. Re-run the oracle (differential compare, boundary cards: total strictly greater than 40 stops, exactly 40 continues), update README, trace tables and anchors in the same commit, and replace this report.
