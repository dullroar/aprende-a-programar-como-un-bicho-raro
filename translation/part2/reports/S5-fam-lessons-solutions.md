# S5-fam-lessons-solutions batch report: lessons/solutions

Iteration 438. Verdict: **NOT TESTED. Family left English (EXC-555).**

## Why nothing changed

- The family holds two reference solutions: `c2-forth-rule-check.sh` (a bash rule check) and `f-takewhile.hs` (Haskell). Together they have 10 comment lines and printed strings that `lessons/respuestas.md` quotes.
- `tools/oracle.py` only runs `src/` entries. It has no runner for `lessons/solutions`, so a changed file could not be proved equivalent (same finding as EXC-545 for the b7-linq subfamily).
- Hard rule 1: if equivalence cannot be proved, leave the family English. `translation/localization-scope.yaml` keeps it `frozen`; no protected file changed.

## Follow-up

If an oracle runner for `lessons/solutions` is added, the comments can be localized with `tools/loc_apply.py` together with the answer key.
