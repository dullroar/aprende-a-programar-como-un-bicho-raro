# F2-007-javascript batch report: card categories in src/javascript (decision 11)

Iteration 520. Verdict: **oracle PASS in Spanish; categories localized in code, check script and README of src/javascript.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.mjs`: the SQLite `CHECK (category IN (...))` list (C24) and the `categories` array (C33) now hold `Reuniones`, `Programación`, `Depuración`, `Aprendizaje`. The report rows print them.
- `check.sh`: the row filter (C13), both expected-order lists (C18, C66) and the two schema-negative inserts (C117, C118). The inserts use `Programación` so they are still refused for the reason they test (`demo_only` and the hours range), not for an unknown category. The `Banking` insert stays English: it must be refused as a fifth category.
- `README.md`: output rows and the table cell naming `Meetings` (inline spans); added to `category-localized-md.txt` and `category-localized-prose.txt`.

## Proof

- `python3 -I tools/oracle.py --entry src/javascript --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `verify --fast` OK; `lock_code --verify` OK; `part2_inv --check` clean.
