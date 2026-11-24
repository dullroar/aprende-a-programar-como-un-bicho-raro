# F2-007-tar-gnu-weird batch report: card categories in src/tar-gnu-weird (decision 11)

Iteration 531. Verdict: **oracle PASS in Spanish; categories localized in code, check script and README of src/tar-gnu-weird.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `tick.sql`: the `CASE card` line (C11) now yields `'Reuniones'`, `'Programación'`, `'Depuración'`, `'Aprendizaje'`.
- `machine.sql`: the `CHECK (category IN (...))` list (C16) uses the same four words.
- `check.sh`: the `rows()` grep (C13), the two awk `split(...)` lists (C31, C45), and the two schema-negative inserts (C145, C146). The inserts now use `'Programación'`, so they still fail for the stated reason (non-demo row, 9 hours) and not because of the category.
- `README.md`: output rows and the `card` table cell; added to `category-localized-md.txt` and `category-localized-prose.txt`.
- `translation/localized-code.sha256` rewritten.

## Proof

- Unlike tar-gnu (EXC-593), this family has no `[A-Za-z]` class around category names: grep found none.
- `python3 -I tools/oracle.py --entry src/tar-gnu-weird --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK.

## Left English, on purpose

- `lessons/lenguajes/tar.md` line 31 (`category=Meetings`) describes the `src/tar-gnu` archive, which stays English (EXC-593).
