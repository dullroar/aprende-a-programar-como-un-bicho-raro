# S5-fam-forth-weird batch report: src/forth-weird

Iteration 455. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English (EXC-569).**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/forth-weird/`)

- `timecards.fs`: 27 `\` comment lines translated line for line (line count unchanged). `DEMO ONLY` stays in line 1 because `check.sh` greps for it; the `<== THE LOOP` marker stays literal because the header comment names it. No Spanish comment contains `http`, `socket`, `curl` or `wget`.
- `check.sh`: 5 comment lines. `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/forth-weird` is now `localizing`; `translation/localized-code.sha256` records the localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/forth-weird --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as for the baseline).
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: clean.

## Kept English, on purpose (EXC-569)

- Card categories (decision 11): `s"` strings are printed, stored in SQL and checked by `check.sh` and the README trace; localizing them needs its own step. Comments still name the English categories, so no mixed forms.
- Display strings: `DEMO ONLY`, `# committed ...`, `# no loop word anywhere ...` are contract; SQL text is contract.
- Stack comments `( n h t )` are notation, unchanged. The `( n total anchor )` after `<== THE LOOP` sits inside the backslash comment and stays English. Identifiers: none renamed.
