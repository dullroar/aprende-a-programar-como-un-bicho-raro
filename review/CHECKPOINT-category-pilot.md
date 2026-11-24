# Checkpoint: category localization pilot (decision 11, tasks F2-003 to F2-005)

Written by iteration 503 (task F2-006). `loop/STOP` exists. Jim: read this, edit the words if you want, then remove `loop/STOP`.

## The four Spanish words as printed

| English | Spanish (as printed by the programs) | UTF-8 bytes |
|---|---|---|
| `Meetings` | `Reuniones` | 9 |
| `Coding` | `Programación` | 13 |
| `Debugging` | `Depuración` | 11 |
| `Learning` | `Aprendizaje` | 11 |

`Programación` and `Depuración` carry an accented letter (2 bytes), so fixed-width fields had to grow (see COBOL).

## Results per family

| Family | Commit | Oracle (English and Spanish) | Files changed | Lines +/- | Driver cost |
|---|---|---|---|---|---|
| src/cobol | 96564f4 | PASS | 18 | +225 / -29 | $1.13 (97 API calls) |
| src/forth | 5e6276b | PASS | 12 | +64 / -15 | $0.49 (40 API calls) |
| src/lisp | cb5d4ab | PASS | 11 | +49 / -14 | $0.49 (34 API calls) |

The COBOL commit includes the shared tool work (`loc_apply.py` entry kind `C<line>`, `apply.py` fence-row rewrite, `invariants.py` I13 category-aware comparison, 11 new tests), so it costs more. Forth and Lisp reused it: about $0.49 each. Remaining cost estimate for the other families is therefore near $0.5 per family, plus any family with its own quirks.

Oracle was `python3 -I tools/oracle.py --entry <family> --english ~/english-source`. All three report `deterministic: false`, the same as the English baseline. `lock_code --verify`, `part2_inv --check` (0 findings) and `verify --fast` were OK at each commit. No example program or `check.sh` ran on the host.

## What changed in each family

- **COBOL** (`timecards.cob`, `check.sh`, `README.md`): the four FILLER values; `PIC X(9)` became `PIC X(13)` in four FILLER lines and in `CATEGORY`, so the REDEFINES table is 52 bytes (was 36). Comments, the `cats=(...)` list and `grep -E` pattern in `check.sh`, and the README sample rows and byte counts follow. Line count is unchanged and no line passes column 72. An I3 waiver was recorded because the digits changed on purpose.
- **Forth** (`timecards.fs`, `check.sh`, `README.md`): the four `s" ..."` strings and `check.sh`. No width change (Forth strings carry their length). Word names `meetings`, `coding`, ... stay as project identifiers.
- **Lisp** (`timecards.lisp`, `check.sh`, `README.md`): `*categories*` vector and `check.sh`. The ISO-week `sed` keeps `[A-Za-z]+` because it only reads row 2, always `Reuniones`.

Reports: `translation/part2/reports/F2-cobol-categories.md`, `F2-forth-categories.md`, `F2-lisp-categories.md`.

## Known gaps (for you to judge)

1. **Inline spans and masked tokens stay English.** `lessons/guias-de-estudio/lenguajes/forth.md` (lines 44, 103, 105, 108) and `src/lisp/README.md` line 48 still say `Meetings`, `Coding`, `Debugging` in prose or code spans, next to sample rows that print the Spanish words. No tool rewrites inline spans. Fixing it needs a tool change, then a follow-up task. See `loop/decisions-provisional.md`.
2. **COBOL width growth** changes the data layout (36 to 52 bytes). The oracle proves the output is the same apart from the four words, and the README trace was updated. Check that you accept this for the other COBOL-style fixed-width families.
3. **Cross-family text:** `lessons/lenguajes/cobol.md` lines 126 to 130 belong to `cobol-weird` and stay English until that family is done.
4. The oracle is deterministic-false in both languages, so PASS means "same output on the sandbox runs", not a byte-for-byte replay of a fixed clock.

## What happens next

Removing `loop/STOP` lets the loop continue with the remaining follow-up tasks in `loop/queue/generated/part2-followup.jsonl`. If you change a word, edit the PO entries (`translation/po/code/src/{cobol,forth,lisp}/`), the allowed list in `tools/categories.py`, and tell the next iteration; rerun the three oracles afterwards. Do not edit the frozen or localized code by hand.
