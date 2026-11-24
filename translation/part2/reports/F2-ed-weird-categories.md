# F2-007-ed-weird batch report: card categories in src/ed-weird (decision 11)

Iteration 513. Verdict: **NOT TESTED / left English. The oracle fails in Spanish, so nothing was kept.**

## What was tried

C entries for the category words in `timecards.ed` (lines 7-11), `timecards.sh` (SQL CHECK list, line 18) and `check.sh` (lines 12, 26, 34, 78, 79, 107, 116, 117), plus the two comment spans that quote the rows (`timecards.ed` L34, `timecards.sh` L4). `loc_apply.py` accepted them.

## Why it fails

- `python3 -I tools/oracle.py --entry src/ed-weird --english ~/english-source`: **FAIL** in Spanish ("stopped at 19, which is not strictly greater than 40"; "the first card over 40 was not kept as the last card").
- Cause: the ed program recognizes card lines with `^[A-Za-z]* [0-9][0-9] x*$` and `^\([A-Za-z]* [0-9]*\)...`. `Programación` and `Depuración` contain `ó`, which those classes do not match, so those cards are never added and the total stops early.
- A C entry may change only category words and PIC widths. Rewriting the regex classes is a syntax change, which the rules forbid. So no safe edit exists.

## State

- All edits reverted (`git checkout` of `src/ed-weird` and its code PO files); the family stays as it was after S5 (comments localized, categories English).
- `translation/exception-register.jsonl`: EXC-588.
- README and `lessons/` text for this family keep the English category words.
