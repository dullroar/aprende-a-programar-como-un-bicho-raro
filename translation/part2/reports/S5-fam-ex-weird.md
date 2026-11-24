# S5-fam-ex-weird batch report: src/ex-weird

Iteration 472. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/ex-weird/`)

- `timecards.ex`: 19 comment lines (the bare `"` separators and the `Run:` command line stay). The Ex commands are code and stay untouched; the `"` comment marker is kept, so Ex still reads each line as a comment.
- `timecards.sh`: 10 comment lines (shebang and the shellcheck directive stay). `check.sh`: 15 comment lines, including four trailing comments (shebang stays). `Dockerfile`: 3 comment lines.
- `check.sh` removes `"` lines from the program before its static scans and ignores `#` lines in the launcher, so the Spanish text cannot trip the loop-keyword, global-command or shell-escape checks.
- `translation/localization-scope.yaml`: `src/ex-weird` is now `localizing`; `translation/localized-code.sha256` records 90 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/ex-weird --english ~/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-583)

- Card categories (decision 11): Ex writes them into the buffer and `check.sh` matches the printed rows.
- Display strings: `DEMO ONLY`, the `# committed ...` line, SQL text and error messages (matched by `check.sh`). The quoted examples `"Meetings 7"` and `"Meetings 17 17"` inside comments keep the English categories to match what Ex prints.
- Identifiers: none renamed (`identifier-map.jsonl` untouched). The README copies no comment text, so it needs no change.
