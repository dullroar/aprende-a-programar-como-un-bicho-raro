# S5-fam-find-gnu batch report: src/find-gnu

Iteration 435. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/find-gnu/`)

- `timecards.sh`: 7 comment lines (`DEMO ONLY` stays in the first one).
- `check.sh`: 13 comment lines. The heredoc body of the fake mktemp (`#!/bin/sh`) is code and was not touched. `check.sh` filters comments with `grep -Ev '^\s*(#|$)'`, so Spanish comments cannot change its static checks.
- `build-line.py`: 14 `#` comments, including trailing ones; the module docstring is a string and stays English.
- `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/find-gnu` is now `localizing`; `translation/localized-code.sha256` records 16 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/find-gnu --english ~/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1); code lines are unchanged.

## Kept English, on purpose (EXC-552)

- Card categories (decision 11): quoted SQL values in the find line, `check.sh` and the README trace. Comments still name the English categories because the code prints them.
- Display strings: `DEMO ONLY`, the `# committed ...` summary (parsed by `check.sh`), SQL text, the build-line docstring.
- Identifiers: none renamed (`identifier-map.jsonl` untouched).
