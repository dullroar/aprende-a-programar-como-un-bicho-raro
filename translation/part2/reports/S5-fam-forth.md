# S5-fam-forth batch report: src/forth

Iteration 425. Verdict: **oracle PASS (docker available). Comments localized; strings, categories and identifiers kept English (EXC-543).**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/forth/`)

- `timecards.fs`: 38 `\` comment lines translated line for line (line count unchanged). `DEMO ONLY` stays in line 1 because `check.sh` greps for it.
- `check.sh`: 4 comment lines. `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/forth` is now `localizing`; `translation/localized-code.sha256` records the 3 files.

## Proof

- `python3 -I tools/oracle.py --entry src/forth --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as for the baseline).
- `check.sh` was not run on the host (hard rule 1); code lines unchanged.

## Kept English, on purpose (EXC-543)

- Card categories (decision 11): the words are printed, checked by `check.sh` and shown in the README trace; localizing them needs its own oracle step. Comments still name the English categories, so no mixed forms.
- Display strings: `DEMO ONLY`, `# committed ...`, `# DEMO ONLY run` are contract; SQL text is contract.
- Trailing `\` comments on lines 40 to 42 share a line with a stack comment `( ... )`; `loc_apply` needs exactly one span per line, so they stay English. Stack comments are notation, unchanged.
- Identifiers: none renamed.
