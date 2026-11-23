# S4-003 batch report: COBOL (cobol, cobol-weird) plus regex-pcre2

Iteration 418. Verdict: **NOT TESTED. Family left English (frozen).**

## What was checked

- Scope file: `src/cobol`, `src/cobol-weird` and `src/regex-pcre2` stay `frozen`; no family was marked `localizing`.
- Oracle (`tools/oracle.py`) needs the sandbox container. Docker is refused in dontAsk mode (same limit as S0-003, S2-004, S4-001 and S4-002). No COBOL or PCRE2 toolchain is allowed on the host, and rule 1 forbids running example programs on the host.
- Without a container run there is no oracle PASS, so no comment, display string or identifier may change (plan 4.5, hard rule 1).
- COBOL: column positions (fixed-form areas A and B, columns 7 and 72) and byte widths of PIC fields may be part of the lesson. Refuse by default: any comment or string edit needs a column and byte check from the oracle first.
- Regex: patterns, flags and fixtures are contract and never change; only comments could be candidates.

## Result

- No protected file changed. No PO entries, identifier-map rows, README, diagram or anchor edits.
- Exception recorded: `EXC-541` in `translation/exception-register.jsonl`.

## To finish (Docker-capable session)

1. Run the `tools/oracle.py` baseline for the three entries and record the semantic record, including column and byte checks for COBOL.
2. Mark the families `localizing`, translate comments line for line, then display strings proven free of contract, then mapped identifiers, all through `tools/loc_apply.py`.
3. Re-run the oracle (boundary cards: total strictly greater than 40 stops, exactly 40 continues), update README, trace tables and anchors in the same commit, and replace this report.
