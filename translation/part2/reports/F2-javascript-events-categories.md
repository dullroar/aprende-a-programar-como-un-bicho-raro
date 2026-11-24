# F2-007-javascript-events batch report: card categories in src/javascript-events (decision 11)

Iteration 521. Verdict: **oracle PASS in Spanish; categories localized in code, check scripts and README of src/javascript-events.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.mjs`: the `CATEGORIES` array (C27) and the SQLite `CHECK (category IN (...))` list (C32).
- `check.sh`: the row filter (C13), both expected-order lists (C18, C87) and the two schema-negative inserts (C147, C148). The inserts use `Programación` so they are still refused for the reason they test.
- `check.mjs`: expected rows (C44), expected DEMO ONLY lines (C48) and the `CATEGORIES` assertion (C187).
- `README.md`: output rows (fence); added to `category-localized-md.txt`. No prose or spans name the categories.

## Proof

- `python3 -I tools/oracle.py --entry src/javascript-events --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `verify --fast` OK; `part2_inv --check` clean; localized-code hashes rewritten.
