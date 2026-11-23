# F2-007-regex-perl batch report: card categories in src/regex-perl (decision 11)

Iteration 528. Verdict: **NOT TESTED / left English. No edit was made.**

## Why

- `timecards.pl` is a single regex match against the tape `MeetingsCodingDebuggingLearningMeetings~~~...`. After the category loop and `(*COMMIT)` it skips the remaining names with `[A-Za-z]*` before the `~` pulse.
- `Programación` and `Depuración` contain `ó`, which `[A-Za-z]` does not match, so the tape could not be consumed and the match would not reach the pulse and final `(*FAIL)` as designed. The pattern has no `/u` handling for the tape either.
- A C entry may change only category words. Changing the character class (or the tape and `qw()` list in one line without breaking the single-statement check) is a syntax change, which the rules forbid. So no safe edit exists.
- Decided from the code (same cause as EXC-588 and EXC-590); the oracle was not run, so the family is NOT TESTED for categories.

## State

- `src/regex-perl`, its README and `check.sh` keep the English category words and the S5 comment localization.
- `translation/exception-register.jsonl`: EXC-591.
