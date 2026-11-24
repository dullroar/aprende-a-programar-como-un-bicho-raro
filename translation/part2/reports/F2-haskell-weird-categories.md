# F2-007-haskell-weird batch report: card categories in src/haskell-weird (decision 11)

Iteration 519. Verdict: **oracle PASS in Spanish; categories localized in code, check script and README of src/haskell-weird.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.hs`: constructors of `data Category` (C40) are now `Reuniones | Programación | Depuración | Aprendizaje`; `deriving Show` prints them.
- `check.sh`: `cats=(...)` (C22) and the `grep -E` row pattern (C32).
- `README.md`: output rows and the inline span in the war story (`# committed total=Reuniones ...`); added to `category-localized-md.txt` and `category-localized-prose.txt`.

## Proof

- `python3 -I tools/oracle.py --entry src/haskell-weird --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `verify --fast` OK; `lock_code --verify` OK; `part2_inv --check` clean.

## Left English, on purpose

- `lessons/guias-de-estudio/lenguajes/haskell.md` (trace fence, lines 132-146) and `lessons/lenguajes/haskell.md` line 48 still show the English category words for haskell-weird output; no tool localizes guide fences or spans. A follow-up task should handle them together with the haskell guide copies.
- `verify --release` still has the 2 pre-existing line-anchor failures noted in the F2-007-haskell report (awk.md:34, cobol.md:15); not run again here.
