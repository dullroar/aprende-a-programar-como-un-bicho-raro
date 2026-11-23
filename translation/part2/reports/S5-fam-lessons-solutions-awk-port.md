# S5-fam-lessons-solutions-awk-port batch report: lessons/solutions/awk-port

Iteration 439. Verdict: **NOT TESTED. Family left English (EXC-556).**

## Why nothing changed

- The family holds `timecards.awk`, `check.sh` and a `Dockerfile` (3 files, 14 comments). It is a reference solution under `lessons/solutions`, not a `src/` entry.
- `tools/oracle.py` only runs `src/` entries. It has no runner for `lessons/solutions/awk-port`, so a changed file could not be proved equivalent (same finding as EXC-545 and EXC-555).
- Hard rule 1: if equivalence cannot be proved, leave the family English. `translation/localization-scope.yaml` keeps it `frozen`; no protected file changed.

## Follow-up

If an oracle runner for `lessons/solutions` is added, the comments can be localized with `tools/loc_apply.py`.
