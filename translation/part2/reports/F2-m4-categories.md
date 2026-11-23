# F2-007-m4 batch report: card categories in src/m4 (decision 11)

Iteration 524. Verdict: **oracle PASS in Spanish; categories localized in code, check script, README and study guide of src/m4.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.m4`: `tc_pick` (C54) uses `[Reuniones]`, `[Programación]`, `[Depuración]`, `[Aprendizaje]`; comment lines 6 and 7 name the Spanish words.
- `check.sh`: `cats=(...)` (C23), the row filters (C36, C41, C51, C67), the expected row string of seed 4020 (C42) and the comment on line 40.
- `README.md`: output rows (fence), prose and inline spans. `lessons/guias-de-estudio/lenguajes/m4.md`: prose and inline spans (lines 42, 78, 113). Both added to `category-localized-prose.txt`; the README also to `category-localized-md.txt`.
- `tools/apply.py`: `localize_category_words` leaves a bold-only `| **Debugging** |` concept-table label alone (not a card category; it stays English, as in the other guides) and follows the glued example `Meetingstc_tab` (2 tests, one negative).
- `tools/invariants.py` (`values`, `drop_dnt_spans`): the span `<category>tc_tab` follows the mapped word symmetrically (2 tests, one negative: a different macro still fails I13).
- `translation/line-anchors.jsonl`: the `tc_pick` record (lines 53-54) expects the Spanish words.

## Proof

- `python3 -I tools/oracle.py --entry src/m4 --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `verify --fast` OK; `part2_inv --check` clean; `lock_code --verify` OK; localized-code hashes rewritten.

## Not fixed here

- `verify --release --no-gates` still fails 4 line-anchor records (awk.md:34, cobol.md:15, lisp.md:52, patrones.md:41; awk-weird, cobol, lisp-weird) and `test_anchors`. They predate this task; a re-anchor task is still owed.
