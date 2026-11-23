# F2-007-forth-weird batch report: card categories in src/forth-weird (decision 11)

Iteration 517. Verdict: **oracle PASS in Spanish; categories localized in code, check script and README of src/forth-weird.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.fs`: the four category words `s" Meetings"`, `s" Coding"`, `s" Debugging"`, `s" Learning"` (C24 to C27) now hold `Reuniones`, `Programación`, `Depuración`, `Aprendizaje`. The Forth word names (`meetings`, `coding`, `debugging`, `learning`) and the `( -- c-addr u )` stack comments did not change.
- `check.sh`: `cats=(...)` and the `grep -E` row pattern (C22, C32).
- `README.md`: output rows; added to `category-localized-md.txt`.

## Tool fix

`loc_apply._category_edit` treated any comment span as a trailing comment and cut the line by comment length. A Forth stack comment sits mid-line, so the cut broke the comparison and refused a valid edit. Now only a comment that ends the line counts as trailing; a mid-line comment stays in the compared text and cannot change. Two tests added to `tools/test_loc_apply.py` (one positive, one negative that changes the stack comment).

## Proof

- `python3 -I tools/oracle.py --entry src/forth-weird --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).

## Left English, on purpose

- Nothing found: the README prose and the study guide do not name the categories.
