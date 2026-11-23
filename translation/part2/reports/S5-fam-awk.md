# S5-fam-awk batch report: src/awk

Iteration 433. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/awk/`)

- `timecards.awk`: 19 comment lines translated line for line (line count unchanged). `DEMO ONLY` stays in the first comment, because `check.sh` greps for it.
- `check.sh`: 8 comment lines. `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/awk` is now `localizing`; `translation/localized-code.sha256` records the 9 localized files of the three families.

## Proof

- `python3 -I tools/oracle.py --entry src/awk --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as for the baseline).
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- `check.sh` was not run on the host (hard rule 1); its code lines are unchanged.

## Kept English, on purpose (EXC-550)

- Card categories (decision 11): `CATEGORY` is filled by `split("Meetings Coding Debugging Learning", ...)` and `check.sh`, the SQL rows and the README trace all name them. Localizing them is a separate step with its own oracle run. Comments still name the English categories because the code prints them; no mixed forms exist in the files.
- Display strings: `DEMO ONLY`, the `# committed ...` summary (parsed by `check.sh`), SQL text, shell commands and the `sqlite3 reported an error` message were left as they are.
- Identifiers: none renamed (`identifier-map.jsonl` untouched).
