# S5-fam-javascript-events batch report: src/javascript-events

Iteration 446. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/javascript-events/`)

- `timecards.mjs`: 28 full-line comment lines (header prose, numbered listener comments). The ASCII-art arrow lines, the `program(realWorld()).emit('start');` example line and trailing comments are untouched. `DEMO ONLY` stays English.
- `check.sh`: 12 full-line comments; trailing comments kept English.
- `check.mjs`: 5 comment lines. `check-static.mjs`: 6 comment lines. `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/javascript-events` is now `localizing`; `translation/localized-code.sha256` records 32 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/javascript-events --english ~/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-561)

- Card categories (decision 11): SQL CHECK values and list data printed by the program, used by `check.sh` and the README trace.
- Display strings: `DEMO ONLY`, the `# committed ...` lines, SQL text.
- Identifiers: none renamed (`identifier-map.jsonl` untouched).
