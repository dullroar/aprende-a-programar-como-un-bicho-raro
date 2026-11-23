# F2-007-apl batch report: card categories in src/apl (decision 11)

Iteration 507. Verdict: **oracle PASS in English and in Spanish; categories localized in code, output, check script, README and study guide of src/apl.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.apl`: `Categories` is `'Reuniones' 'Programación' 'Depuración' 'Aprendizaje'` (C21); the recycle comment on line 39 names them (L39). APL strings are Unicode text, so no width change was needed. The variable name `Categories` is a project identifier and stays.
- `check.sh`: the `cats=(...)` list and the `grep -E` row pattern use the Spanish words (C15, C24).
- `README.md`: sample output rows and the "Deduce el resto" prose and spans (`src/apl/README.md` added to `category-localized-md.txt` and `category-localized-prose.txt`).
- `lessons/study-guides/languages/apl.md` (rendered `lessons/guias-de-estudio/lenguajes/apl.md`): inline spans, output sentence and trace table (added to `category-localized-prose.txt`).
- `translation/localized-code.sha256` rewritten (109 files).

## Proof

- `python3 -I tools/oracle.py --entry src/apl --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- `check.sh` and the program were not run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK.

## Left English, on purpose

- The "(Debugging)" gloss in the study-guide category table and the generic phrase "Debugging y seguridad" in `lessons/lenguajes/apl.md`: they name the concept, not the card category.
