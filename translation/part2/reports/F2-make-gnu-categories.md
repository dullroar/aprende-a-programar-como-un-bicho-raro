# F2-007-make-gnu batch report: card categories in src/make-gnu (decision 11)

Iteration 525. Verdict: **oracle PASS in Spanish; categories localized in code, check script, README and both make/cmake guides.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `Makefile`: `cat_names := Reuniones Programación Depuración Aprendizaje` (C92).
- `check.sh`: C entries for lines 31, 35, 37, 38, 39, 41, 49 and 62 (row filters, the category-order list and the first-row lookup).
- `README.md`: output rows (fence), the `$(word n,...)` span (row 73) and the prose span on the fifth card.
- `lessons/guias-de-estudio/lenguajes/make-y-cmake.md` (prose, spans, trace table rows and the fenced hand-trace line) and `lessons/lenguajes/make-cmake.md` (one bullet). This also closes the item left open by F2-007-cmake. The bold concept label `**Debugging**` stays English, as in the other guides.
- `tools/apply.py`: `_WORD_RE` also follows the last word of the four-word list when `)` closes it (`Debugging Learning)`); new `TRACE_RE` rewrites `Word N N / Word N N` summary lines inside fences of files in `category-localized-md.txt` (2 tests, each with a negative case).
- Lists: `category-localized-md.txt` (README, guide) and `category-localized-prose.txt` (README, guide, make-cmake.md).

## Proof

- `python3 -I tools/oracle.py --entry src/make-gnu --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `verify --fast` OK; `part2_inv --check` clean; `lock_code --verify` OK; localized-code hashes rewritten.

## Not fixed here

- `verify --release --no-gates` still fails the same 4 line-anchor records (awk.md:34, cobol.md:15, lisp.md:52, patrones.md:41) and `test_anchors`. They predate this task; a re-anchor task is still owed.
- `regen_po.py` on `lessons/languages/make-cmake.md` reverts its generated Program Flow blocks to English, so that file was edited by one line instead.
