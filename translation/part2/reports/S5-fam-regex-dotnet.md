# S5-fam-regex-dotnet batch report: src/regex-dotnet

Iteration 466. Verdict: **NOT TESTED. Family left English (EXC-578).**

## What was tried

- `python3 -I tools/oracle.py --entry src/regex-dotnet --english /home/lehmer/english-source` returns **FAIL** with findings on the English run itself (for example "english: card 0: running total 2026, expected 12"). The oracle reads the year 2026 as the running total, so it fails for the unmodified English baseline; the cause is the oracle's parsing of this entry's output, not any comment edit.
- Hard rule 1: equivalence cannot be proved, so no edit was attempted. `translation/localization-scope.yaml` keeps the family `frozen`; no protected file changed.

## Follow-up

Fix the oracle's card parser for this entry (ignore the date field when reading the running total), then localize the 16 comments with `tools/loc_apply.py` and rerun the oracle.
