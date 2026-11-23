# S5-fam-javascript batch report: src/javascript

Iteration 445. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/javascript/`)

- `timecards.mjs`: 19 full-line comment lines. `DEMO ONLY` stays English in the header comment. The ASCII-art `*` lines, the `FIRST/LAST SEMICOLON` banners, the trailing `// Still the only statement.` and `{ /* Intentionally empty. */ }` are untouched (check.sh mutates that exact text).
- `check.sh`: 13 full-line comments. Trailing comments on code lines are kept English.
- `check-structure.mjs`: 4 comment lines. `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/javascript` is now `localizing`; `translation/localized-code.sha256` records 27 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/javascript --english /home/lehmer/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-560)

- Card categories (decision 11): SQL CHECK values and list data printed by the program, used by `check.sh` and the README trace.
- Display strings: `DEMO ONLY`, the `# committed ...` lines (parsed by `check.sh`), SQL text.
- Identifiers: none renamed (`identifier-map.jsonl` untouched).
