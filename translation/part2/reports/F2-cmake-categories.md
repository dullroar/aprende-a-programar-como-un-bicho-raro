# F2-007-cmake batch report: card categories in src/cmake (decision 11)

Iteration 511. Verdict: **oracle PASS in English and in Spanish; categories localized in code, check script and README of src/cmake.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.cmake`: `set(categories Reuniones Programación Depuración Aprendizaje Reuniones)` (C59). The line's trailing comment moved from an L entry into the same C entry (a line cannot carry both: overlapping edits are refused) and now ends in `Reuniones`.
- `check.sh`: the eight lines that match, order-check or filter on the category words (C37, C40 to C44, C51, C63).
- `README.md`: output rows and the prose line that names the wrap-around category. Added to `category-localized-md.txt` and `category-localized-prose.txt`.
- `tools/loc_apply.py`: a C entry may now also translate a trailing comment on the same line (code part still limited to category words; the comment must scan as one comment; adding or dropping a comment is refused). 3 new tests, two negative.
- `translation/localized-code.sha256` rewritten (109 files).

## Proof

- `python3 -I tools/oracle.py --entry src/cmake --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK.

## Left English, on purpose

- `lessons/guias-de-estudio/lenguajes/make-y-cmake.md` names `Meetings` in prose and spans, but the guide also covers make-gnu, whose family still prints the English words. Revisit after F2-007-make-gnu.
