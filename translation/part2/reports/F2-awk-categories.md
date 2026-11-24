# F2-007-awk batch report: card categories in src/awk (decision 11)

Iteration 509. Verdict: **oracle PASS in English and in Spanish; categories localized in code, check script and README of src/awk.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.awk`: `split("Reuniones Programación Depuración Aprendizaje", CATEGORY, " ")` (C67); header comment lines 7-8 name the same words (L7, L8). The array name `CATEGORY` is a project identifier and stays.
- `check.sh`: the `cats=(...)` list (C42) and the `grep -E` row pattern (C51) use the Spanish words.
- `README.md`: sample output rows and the "Qué hace" and "Arreglos" prose and spans (`src/awk/README.md` added to `category-localized-md.txt` and `category-localized-prose.txt`).
- `translation/localized-code.sha256` rewritten (109 files; awk files were already localized for comments).

## Proof

- `python3 -I tools/oracle.py --entry src/awk --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK.

## Left English, on purpose

- `lessons/lenguajes/awk.md` line 37 quotes the `src/awk-weird` one-liner, which still prints English words; it belongs to the awk-weird task.
