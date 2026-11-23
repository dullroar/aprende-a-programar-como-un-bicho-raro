# F2-007-cobol-weird batch report: card categories in src/cobol-weird (decision 11)

Iteration 512. Verdict: **oracle PASS in English and in Spanish; categories localized in code, check script and README of src/cobol-weird.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.cob`: the four `MOVE "<category>" TO WS-CATEGORY` lines (C156, C161, C166, C171) use `Reuniones`, `Programación`, `Depuración`, `Aprendizaje`; `WS-CATEGORY` is `PIC X(13)` (C48), because `Programación` is 13 bytes in UTF-8. Paragraph names such as `MEETINGS-CARD` are identifiers and stay. No line passes column 72.
- `check.sh`: the `cats=(...)` list (C28) and the `grep -E` row pattern (C39).
- `README.md`: output rows, the prose line that names the rotation, and the Mermaid `accDescr` and `state "..."` labels (node IDs `M C D L` unchanged). Added to `category-localized-md.txt` and `category-localized-prose.txt`.
- `tools/apply.py`: `localize_category_words` now also rewrites the display text of Mermaid `accDescr:` and `state "..."` lines (nothing else in a fence). 2 new tests, one negative.
- `translation/localized-code.sha256` rewritten (109 files).

## Proof

- `python3 -I tools/oracle.py --entry src/cobol-weird --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK, `test_apply.py` 36 tests OK.

## Left English, on purpose

- `lessons/guias-de-estudio/lenguajes/cobol.md` and `lessons/lenguajes/cobol.md` (generated) still show the English words in their copy of the diagram and in trace tables. They also cover the `cobol` family, which already prints Spanish, so the guide needs its own task; `verify --fast` passes on both today.
