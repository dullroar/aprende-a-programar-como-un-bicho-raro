# F2-007-awk-weird batch report: card categories in src/awk-weird (decision 11)

Iteration 510. Verdict: **oracle PASS in English and in Spanish; categories localized in code, check script and README of src/awk-weird, and in the quoted one-liner of the awk lesson.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.awk`: `split("Reuniones Programación Depuración Aprendizaje", C, " ")` (C36) and the header comment one-liner (L17). The array name `C` stays.
- `check.sh`: `rows()` grep pattern (C11), the `cats=(...)` list (C28) and the `mapfile` grep pattern (C87).
- `README.md`: output row, prose, and the fenced one-liner; `lessons/lenguajes/awk.md` quotes the same one-liner. Both added to `category-localized-md.txt`, the README also to `category-localized-prose.txt`.
- `tools/apply.py`: `localize_category_rows` also rewrites the quoted four-word list `"Meetings Coding Debugging Learning"` inside fences (needed for the one-liner; 2 new tests, one negative).
- `translation/localized-code.sha256` rewritten (109 files).

## Proof

- `python3 -I tools/oracle.py --entry src/awk-weird --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK.

## Left English, on purpose

- `lessons/solutions/awk-port/timecards.awk` (family lessons/solutions-awk-port, left English, NOT TESTED, EXC-556).
