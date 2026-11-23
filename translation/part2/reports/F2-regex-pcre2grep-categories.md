# F2-007-regex-pcre2grep batch report: card categories in src/regex-pcre2grep (decision 11)

Iteration 527. Verdict: **NOT TESTED / left English. No edit was made.**

## Why

- `timecards.sh` line 20 reads the one-line tape `MeetingsCodingDebuggingLearning...` and skips the remaining names with `[A-Za-z]*` before the gray-level digits.
- `Programación` and `Depuración` contain `ó`, which `[A-Za-z]` does not match, so the match would fail after the category alternation. The pattern is not UTF-aware either.
- A C entry may change only category words. Changing the regex class is a syntax change, which the rules forbid. So no safe edit exists.
- This was decided from the code (same cause as EXC-588, ed-weird); the oracle was not run, so the family is NOT TESTED for categories.

## State

- `src/regex-pcre2grep`, its README and lessons text keep the English category words and the S5 comment localization.
- `translation/exception-register.jsonl`: EXC-590.
