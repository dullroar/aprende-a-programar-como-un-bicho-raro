# S5-fam-m4 batch report: src/m4

Iteration 456. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English (EXC-570).**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/m4/`)

- `timecards.m4`: 44 `dnl` comment lines translated line for line (line count unchanged). Line 1 keeps `DEMO ONLY` because `check.sh` greps for it. No Spanish comment contains `http`, `socket`, `curl` or `wget`. Lines 86, 88 and 89 (`# DEMO ONLY run`, `# committed ...`, `# no loop statement ...`) are printed output, not comments, and stay English.
- `check.sh`: 15 comment lines (shebang and the `${#rows[@]}` false positive untouched). `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/m4` is now `localizing`; `translation/localized-code.sha256` records the localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/m4 --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as for the baseline).
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: clean.

## Kept English, on purpose (EXC-570)

- Card categories (decision 11): `Meetings`, `Coding`, `Debugging`, `Learning` are macro text printed in rows, stored in SQL and matched by `check.sh` and the README trace. Comments still name the English categories, so no mixed forms.
- Display strings: `DEMO ONLY`, `# committed ...`, `# no loop statement ...` are contract; SQL text is contract. Identifiers (`tc_*`): none renamed.
