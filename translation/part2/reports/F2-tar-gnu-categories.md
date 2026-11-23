# F2-007-tar-gnu batch report: card categories in src/tar-gnu (decision 11)

Iteration 530. Verdict: **NOT TESTED / left English. No edit was made.**

## Why

- `check.sh` line 92 decodes the archive with `sed -nE 's/...category=([A-Za-z]+) hours=.../'` and compares the result with the database rows (the "state" check).
- `Programación` and `Depuración` contain `ó`, which `[A-Za-z]` does not match, so the decoded list would lose those cards and the check would fail.
- A C entry may change only category words. Changing the character class is a syntax change, and loosening the check is forbidden. So no safe edit exists.
- Decided from the code (same cause as EXC-588, EXC-590, EXC-591 and EXC-592); the oracle was not run, so the family is NOT TESTED for categories.

## State

- `src/tar-gnu`, its README and scripts keep the English category words and the S5 comment localization.
- `translation/exception-register.jsonl`: EXC-593.
