# F2-007-haskell batch report: card categories in src/haskell (decision 11)

Iteration 518. Verdict: **oracle PASS in Spanish; categories localized in code, check script and README of src/haskell.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.hs`: the constructors of `data Category` (C25) are now `Reuniones | Programación | Depuración | Aprendizaje`. They occur once in the file; `deriving Show` prints them, so the output rows carry the Spanish words.
- `check.sh`: `cats=(...)` and the `grep -E` row pattern (C16, C26).
- `README.md`: output rows and the inline span naming the four constructors; added to `category-localized-md.txt` and `category-localized-prose.txt`.

## Proof

- `python3 -I tools/oracle.py --entry src/haskell --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `verify --fast` OK; `lock_code --verify` OK; `part2_inv --check` clean.

## Known unrelated failures in `verify --release --no-gates`

Present before this task (checked with the change stashed): two line-anchor records (`lessons/lenguajes/awk.md:34`, `lessons/lenguajes/cobol.md:15`) and `tools/test_anchors.py::test_stored_document_is_current`. They come from earlier category tasks (awk-weird, cobol) and need a follow-up reanchor task.

## Left English, on purpose

- `lessons/lenguajes/haskell.md` mentions `Meetings` only in the haskell-weird war story (another family).
