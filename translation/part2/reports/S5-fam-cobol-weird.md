# S5-fam-cobol-weird batch report: src/cobol-weird

Iteration 454. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/cobol-weird/`)

- `timecards.cob`: comment lines translated line for line (fixed format kept; no line over 72 bytes; line count unchanged). `DEMO ONLY` stays in the first comment, because `check.sh` greps for it.
- `check.sh`: 8 comment lines. `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/cobol-weird` is now `localizing`; `translation/localized-code.sha256` records the localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/cobol-weird --english ~/english-source`: PASS, no findings (`deterministic: false`, as for the baseline).
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: clean. `verify --fast`: ok.

## Kept English, on purpose (EXC-568)

- Card categories (decision 11): 9-byte `PIC X` fields, printed rows, SQL data, `check.sh` lists and the README trace all use them; localizing them needs a dedicated step. No mixed forms exist; comments still name the English categories because the code prints them.
- Display strings: `DEMO ONLY`, the `# committed ...` summary, SQL and shell text are contract. Identifiers: none renamed.
