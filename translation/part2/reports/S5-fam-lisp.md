# S5-fam-lisp batch report: src/lisp

Iteration 448. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/lisp/`)

- `timecards.lisp`: 11 full-line `;;;;` and `;;; ---` comment lines. Docstrings (Lisp strings) and the trailing `; T: seed from the OS` comment are untouched. `DEMO ONLY` stays English.
- `check.sh`: 8 full-line comments. `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/lisp` is now `localizing`; `translation/localized-code.sha256` records 35 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/lisp --english ~/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-563)

- Card categories (decision 11): `*categories*` vector, printed rows, matched by `check.sh` and the README trace.
- Display strings: `DEMO ONLY`, the `# committed ...` lines, SQL text, docstrings.
- Identifiers: none renamed (`identifier-map.jsonl` untouched).
