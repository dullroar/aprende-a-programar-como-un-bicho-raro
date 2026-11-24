# G1-007 batch report: card categories in src/tar-gnu (decision 11)

Iteration 542. Verdict: **oracle PASS in Spanish; categories localized and the `[A-Za-z]` class in check.sh made accent-safe. Resolves EXC-593.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `build-archive.sh`: C30 (the category list written into the archive).
- `dispatch.sh`: C44 (SQL CHECK list), C53 (strict `case` pattern).
- `inspect.sh`: C37 (the `grep -Eqx` record grammar).
- `check.sh`: C25, C26, C36 (lists), C92 (the `sed` decode class widened to `[A-Za-zÁÉÍÓÚáéíóúñ]+`, the G1-001 class), C112, C113, C131, C132, C147 to C149, C151 to C153, C155 (hand-made archives), C165, C166 (SQL inserts).
- `README.md`: output rows, table cell, spans and the fenced archive record lines; added to both category-localized lists.
- Tooling: `apply.py` localizes `category=Word` in fences (`KEYVAL_RE`); test `test_archive_record_category_in_fence` with a negative (`CodingX` stays).
- `translation/localized-code.sha256` rewritten; EXC-593 marked resolved.
- Left alone: the member-name classes `tr -cd 'A-Za-z0-9._-'` (dispatch.sh, inspect.sh) act on file names, not categories.

## Proof

- `python3 -I tools/oracle.py --entry src/tar-gnu --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- `lock_code --write-localized`, `part2_inv --check` 0 findings, `verify --fast` OK, `test_apply` OK.
- Nothing was run on the host (hard rule 1).
