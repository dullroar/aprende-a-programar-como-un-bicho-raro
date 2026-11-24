# S5-fam-make-gnu batch report: src/make-gnu

Iteration 449. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/make-gnu/`)

- `Makefile`: 31 full-line `#` comment lines. Recipes, variables, SQL, `DEMO ONLY` and the `# committed ...` output strings are untouched.
- `check.sh`: 17 full-line comments (the shebang stays). `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/make-gnu` is now `localizing`; `translation/localized-code.sha256` records 38 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/make-gnu --english ~/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-564)

- Card categories (decision 11): `cat_names` in the Makefile, printed rows, matched by `check.sh` and the README trace.
- Display strings: `DEMO ONLY`, the `# committed ...` and `# make re-executed ...` lines, SQL text, the `OK:` summary.
- Identifiers: none renamed (`identifier-map.jsonl` untouched).
