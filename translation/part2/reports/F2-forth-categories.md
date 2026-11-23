# F2-004 batch report: card categories in src/forth (decision 11)

Iteration 501. Verdict: **oracle PASS in English and in Spanish; categories localized in code, output, check script and README of src/forth.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.fs`: the four `s" ..."` strings are `Reuniones`, `Programación`, `Depuración`, `Aprendizaje` (C29 to C32). Word names (`meetings`, `coding`, ...) are project identifiers outside this task and stay. Forth strings carry their length, so no width change was needed. Comment line 6 names the Spanish categories.
- `check.sh`: the `cats=(...)` list and the `grep -E` row pattern use the Spanish words (C15, C24).
- `README.md`: the sample output rows print the Spanish words (`src/forth/README.md` added to `translation/part2/category-localized-md.txt`).
- `translation/localized-code.sha256` rewritten (109 files).

## Proof

- `python3 -I tools/oracle.py --entry src/forth --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- `check.sh` and the program were not run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK.

## Left English, on purpose

- `lessons/guias-de-estudio/lenguajes/forth.md` lines 44, 103, 105 and 108 name the categories inside inline code spans (`Meetings`, `Coding`, `Debugging`). Code spans are masked in the PO and restored from the English, and no tool rewrites inline spans (only fence rows, see F2-003). Handling them needs a tool change; deferred to a follow-up task (file in `loop/decisions-provisional.md`). Until then that guide shows the English words for the Forth output.
- `DEMO ONLY`, the `# committed ...` summary, SQL text, the `# begin ... until` line: contract or untouched.
