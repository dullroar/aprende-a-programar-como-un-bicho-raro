# F2-003 batch report: card categories in src/cobol (decision 11)

Iteration 500. Verdict: **oracle PASS in English and in Spanish; categories localized in code, output, check script and README.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.cob`: the four `FILLER` values are `Reuniones`, `Programación`, `Depuración`, `Aprendizaje`. `Programación` is 13 bytes in UTF-8, so `PIC X(9)` became `PIC X(13)` in the four FILLER lines and in `CATEGORY`; the REDEFINES area is 52 bytes. Comment lines 7 to 9 and 48 name the Spanish categories and 52 bytes. No line passes column 72 and the line count is unchanged.
- `check.sh`: the `cats=(...)` list and the `grep -E` row pattern use the Spanish words.
- `README.md`: the sample output rows print the Spanish words; step 3 says 13 bytes and 52 bytes. I3 waiver recorded in the exception register (the digits changed on purpose).
- `translation/localized-code.sha256` rewritten (109 files).

## New tool support (tested)

- `loc_apply.py`: PO entry kind `C<line>`, a whole-line edit. The only differences allowed between the English and Spanish line are the four category words (mapped one to one, approved forms only) and the width inside `PIC X(n)`. Anything else is refused. 6 new tests, 3 of them negative.
- `apply.py`: for Markdown files listed in `translation/part2/category-localized-md.txt`, an output row inside a fence (English category word then TAB) gets the Spanish word. 2 new tests.
- `invariants.py` I13: fence lines compare equal when they differ only by the approved category words.

## Proof

- `python3 -I tools/oracle.py --entry src/cobol --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- `check.sh` and the container run were not executed on the host (hard rule 1); the oracle ran the program in the sandbox.
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK.

## Left English, on purpose

- `DEMO ONLY`, the `# committed ...` summary, SQL text and the `# PERFORM UNTIL ...` line: contract or untouched in this task.
- `lessons/lenguajes/cobol.md` lines 126 to 130 belong to `cobol-weird` (another family), so they stay English.
