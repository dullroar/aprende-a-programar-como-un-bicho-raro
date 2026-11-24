# S5-fam-cobol batch report: src/cobol

Iteration 424. Verdict: **oracle PASS (docker available this session). Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/cobol/`)

- `timecards.cob`: 49 comment lines translated line for line (fixed format kept; no line over 72 bytes; line count unchanged). `DEMO ONLY` stays in the first comment, because `check.sh` greps for it.
- `check.sh`: 8 comment lines. `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/cobol` is now `localizing`; `translation/localized-code.sha256` records the 3 localized files.

## Proof

- `python3 -I tools/oracle.py --selftest`: PASS (planted `total >= 40` mutant rejected).
- `python3 -I tools/oracle.py --entry src/cobol --english ~/english-source`: PASS, no findings. `deterministic: false` is reported by the oracle as it was for the baseline.
- `check.sh` was not run on the host (hard rule 1); its code lines are unchanged.

## Kept English, on purpose (EXC-542)

- Card categories (decision 11): `PIC X(9)` holds four 9-byte names and `REDEFINES` lays a table over 36 bytes. `Programación`, `Depuración` and `Aprendizaje` need wider fields, which changes data layout, the SQL rows, the `check.sh` category list and the README trace. Left for a dedicated step with its own oracle run; no mixed forms exist in the files (comments still name the English categories because the code still prints them).
- Display strings: `DEMO ONLY` (grepped by `check.sh`, written to the database), the `# committed ...` summary (parsed by `check.sh`), SQL text and shell commands are contract. The `sqlite3 failed` message and the `# PERFORM UNTIL an 88-level` line were not translated in this pass.
- Identifiers: none renamed (`identifier-map.jsonl` untouched).

## Also fixed

- `tools/verify.py` `md_rel_of_po` treated `translation/po/code/*.po` as a Markdown PO (I16 false failure). It now ignores the code PO tree; a test was added.
