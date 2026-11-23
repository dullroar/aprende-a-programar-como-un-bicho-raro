# F2-007-regex-sed batch report: card categories in src/regex-sed (decision 11)

Iteration 529. Verdict: **NOT TESTED / left English. No edit was made.**

## Why

- `timecards.sed` carries the category through the pipeline as `c:NAME` and matches it with `[A-Za-z]+` at lines 16, 55, 60 and 62 (also quoted in the README at lines 183, 312, 356 and 375).
- `Programación` and `Depuración` contain `ó`, which `[A-Za-z]` does not match, so those cards would not match the captures, the rewrites would not fire and the output would differ.
- A C entry may change only category words. Changing the character class is a syntax change, which the rules forbid. So no safe edit exists.
- Decided from the code (same cause as EXC-588, EXC-590 and EXC-591); the oracle was not run, so the family is NOT TESTED for categories.

## State

- `src/regex-sed`, its README and `check.sh` keep the English category words and the S5 comment localization.
- `translation/exception-register.jsonl`: EXC-592.
