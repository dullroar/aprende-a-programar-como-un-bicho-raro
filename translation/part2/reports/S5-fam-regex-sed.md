# S5-fam-regex-sed batch report: src/regex-sed

Iteration 473. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/regex-sed/`)

- `timecards.sed`: 4 comment lines (the sed program itself is untouched; `check.sh` strips `#` lines before its scans).
- `timecards.sh`: 6 comment lines (shebang stays). `check.sh`: 13 comment lines (shebang stays). `Dockerfile`: 2 comment lines.
- `translation/localization-scope.yaml`: `src/regex-sed` is now `localizing`; `translation/localized-code.sha256` records 94 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/regex-sed --english ~/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-584)

- Card categories (decision 11): the sed program writes them into the tape and `check.sh` matches the printed rows. The comment example `Meetings` in `check.sh` keeps the English form to match what is printed.
- Display strings: `DEMO ONLY`, `# committed ...`, `# sed now exits with status 1 ...`, SQL text and error messages (matched by `check.sh`).
- Identifiers: none renamed. The README copies no comment text, so it needs no change.
