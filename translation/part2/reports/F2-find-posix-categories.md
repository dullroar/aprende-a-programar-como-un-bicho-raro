# F2-007-find-posix batch report: card categories in src/find-posix (decision 11)

Iteration 516. Verdict: **oracle PASS in Spanish; categories localized in code, check script and README of src/find-posix.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.sh`: the single `find` line (C21) now prints `'Reuniones'`, `'Aprendizaje'`, `'Depuración'`, `'Programación'`, `'Reuniones'`. No path pattern or primary changed.
- `build-line.py`: the five `ex("printf", q("'...',"))` lines (C62 to C66), so the generator still reproduces `timecards.sh`.
- `check.sh`: `cats=(...)`, the `rows()` grep and the awk `want` list (C61, C65, C88); the comment on line 144 now says Reuniones (L144 msgstr).
- `README.md`: output rows; added to `category-localized-md.txt`.

## Proof

- `python3 -I tools/oracle.py --entry src/find-posix --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK.

## Left English, on purpose

- README line 139 prose: the word is a masked DNT token in the PO (same case as the lisp README line 48).
