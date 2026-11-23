# S5-fam-cmake batch report: src/cmake

Iteration 434. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/cmake/`)

- `timecards.cmake`: comment spans translated line for line (line count unchanged), including the trailing comments on the register lines. `DEMO ONLY` stays in the first comment.
- `check.sh`: 13 comment lines. `Dockerfile`: 2 comment lines. `check.sh` filters comment lines with `grep -Ev '^\s*#'`, so Spanish comments cannot change its static checks.
- `translation/localization-scope.yaml`: `src/cmake` is now `localizing`; `translation/localized-code.sha256` records the localized files (12 in total).

## Proof

- `python3 -I tools/oracle.py --entry src/cmake --english /home/lehmer/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- `check.sh` was not run on the host (hard rule 1); its code lines are unchanged.

## Kept English, on purpose (EXC-551)

- Card categories (decision 11): the `categories` list, `check.sh`, the SQL rows and the README trace all name them. Comments still name the English categories because the code prints them.
- Display strings: `DEMO ONLY`, the `# committed ...` summary (parsed by `check.sh`), SQL text and shell commands were left as they are.
- Identifiers: none renamed (`identifier-map.jsonl` untouched).
