# S5-fam-ed-weird batch report: src/ed-weird

Iteration 471. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/ed-weird/`)

- `timecards.ed`: 18 comment lines (the bare `#` separators and the `Run:` command line stay). The ed commands are code and stay untouched.
- `timecards.sh`: 5 comment lines (shebang stays). `check.sh`: 14 comment lines (shebang stays). `Dockerfile`: 3 comment lines.
- `check.sh` strips `#` lines before its static scans (`timecards.sh` and `timecards.ed`), so the Spanish text cannot trip the loop-keyword or shell-escape checks.
- `translation/localization-scope.yaml`: `src/ed-weird` is now `localizing`; `translation/localized-code.sha256` records 86 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/ed-weird --english /home/lehmer/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-582)

- Card categories (decision 11): ed writes them into the buffer and `check.sh` matches the printed rows.
- Display strings: `DEMO ONLY`, the `# committed ...` line, SQL text and error messages (matched by `check.sh`). The quoted example `"Coding 15 ... Meetings 12|..."` inside a comment keeps the English categories to match what ed prints.
- Identifiers: none renamed (`identifier-map.jsonl` untouched). The README copies no comment text, so it needs no change.
