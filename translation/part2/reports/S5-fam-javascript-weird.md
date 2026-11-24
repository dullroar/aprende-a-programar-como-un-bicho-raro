# S5-fam-javascript-weird batch report: src/javascript-weird

Iteration 463. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/javascript-weird/`)

- `core.mjs`: 8 comment lines. `timecards.mjs`: 7. `check.mjs`: 6. `check-static.mjs`: 4. `Dockerfile`: 4. `check.sh`: 12 full-line comments (shebang kept).
- Trailing comments and all code, strings and the `DEMO ONLY` text are untouched.
- `translation/localization-scope.yaml`: `src/javascript-weird` is now `localizing`; `translation/localized-code.sha256` records 70 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/javascript-weird --english ~/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-576)

- Card categories (decision 11): printed rows matched by `check.sh` and the README trace.
- Display strings: `DEMO ONLY`, the `# committed ...` line, SQL text, the result summary.
- Identifiers: none renamed (`identifier-map.jsonl` untouched). The README copies no comment text, so it needs no change.
