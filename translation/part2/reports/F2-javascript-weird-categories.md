# F2-007-javascript-weird batch report: card categories in src/javascript-weird (decision 11)

Iteration 522. Verdict: **oracle PASS in Spanish; categories localized in code, check scripts and README of src/javascript-weird.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `core.mjs`: the `CATEGORIES` array (C5).
- `timecards.mjs`: the SQLite `CHECK (category IN (...))` list (C17).
- `check.sh`: the row filter (C13), the expected-order list (C18), the simulation list (C70) and the two schema-negative inserts (C121, C122). The inserts use `Programación` so they are still refused for the reason they test.
- `check.mjs`: the expected category order (C38).
- `README.md`: output rows (fence); added to `category-localized-md.txt`. No prose or spans name the categories.

## Proof

- `python3 -I tools/oracle.py --entry src/javascript-weird --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `verify --fast` OK; `part2_inv --check` clean; `lock_code --verify` OK; localized-code hashes rewritten.
