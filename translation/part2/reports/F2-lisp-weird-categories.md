# F2-007-lisp-weird batch report: card categories in src/lisp-weird (decision 11)

Iteration 523. Verdict: **oracle PASS in Spanish; categories localized in code, check script and README of src/lisp-weird.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.lisp`: the circular `*week*` list (C45) and the docstring line that quotes `"Meetings"` (C47), so one form per file.
- `check.sh`: the two row filters of the PROGN/OR run (C29, C35), the expected-order array (C42) and the row filter of the consistency loop (C51).
- `README.md`: output rows and the copied `*week*` list in fences; the inline span in prose. Added to `category-localized-md.txt` and `category-localized-prose.txt`.
- `tools/apply.py`: `localize_category_rows` also rewrites a copied Lisp list of the four quoted words in order, inside fences (new `QUOTED_LIST_RE`; 2 tests in `tools/test_apply.py`, one negative: other order and prose stay).

## Proof

- `python3 -I tools/oracle.py --entry src/lisp-weird --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `verify --fast` OK; `part2_inv --check` clean; `lock_code --verify` OK; localized-code hashes rewritten.
