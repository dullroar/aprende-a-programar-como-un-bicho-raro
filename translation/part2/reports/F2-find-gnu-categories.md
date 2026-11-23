# F2-007-find-gnu batch report: card categories in src/find-gnu (decision 11)

Iteration 515. Verdict: **oracle PASS in Spanish; categories localized in code, check script and README of src/find-gnu.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.sh`: the single `find` line (C22) now prints `'Reuniones'`, `'Aprendizaje'`, `'Depuración'`, `'Programación'`, `'Reuniones'`. No regex or primary changed.
- `build-line.py`: the five `out("'...',")` lines (C48 to C52), so the check that `build-line.py` reproduces `timecards.sh` still holds.
- `check.sh`: `cats=(...)`, the `rows()` grep and the awk `want` list (C48, C50, C61).
- `README.md`: output rows; added to `category-localized-md.txt`.
- `translation/localized-code.sha256` rewritten (109 files).

## Proof

- `python3 -I tools/oracle.py --entry src/find-gnu --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK.

## Left English, on purpose

- No study-guide or lesson copy of the rows exists for this family (`lessons/lenguajes/find.md` does not name the categories).
