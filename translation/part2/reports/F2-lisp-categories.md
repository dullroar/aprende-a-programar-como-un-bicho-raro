# F2-005 batch report: card categories in src/lisp (decision 11)

Iteration 502. Verdict: **oracle PASS in English and in Spanish; categories localized in code, output, check script and README rows of src/lisp.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.lisp`: `*categories*` is `#("Reuniones" "Programación" "Depuración" "Aprendizaje")` (C20). Header comment lines 6 and 7 name the Spanish categories (L6, L7).
- `check.sh`: the `cats=(...)` list and the `grep -E` row pattern use the Spanish words (C32, C41). The ISO-week sed on line 27 keeps `[A-Za-z]+`: it reads output row 2, which is always the first card (`Reuniones`), so no non-ASCII letter reaches it.
- `README.md`: the sample output rows print the Spanish words (`src/lisp/README.md` added to `translation/part2/category-localized-md.txt`).
- `translation/localized-code.sha256` rewritten (109 files).

## Proof

- `python3 -I tools/oracle.py --entry src/lisp --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- `check.sh` and the program were not run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv` 0 findings, `verify --fast` OK.

## Left English, on purpose

- `src/lisp/README.md` line 48 ("Qué hace") names the categories as masked tokens restored from the English; no tool rewrites them (same limit as the F2-004 inline spans). The prose still says `Meetings, Coding, Debugging y Learning`, while the sample rows above print the Spanish words. Follow-up with the span tool.
- Docstrings and comments that do not name the categories, `DEMO ONLY`, SQL text: contract or untouched.
