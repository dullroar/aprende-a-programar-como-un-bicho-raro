# S5-fam-lessons-tools batch report: lessons/tools

Iteration 440. Verdict: **NOT TESTED. Family left English (EXC-557).**

## Why nothing changed

- The family holds sandbox and verification scripts (4 files, 47 comments). It is build and exercise tooling under `lessons/`, not a `src/` entry.
- `tools/oracle.py` only runs `src/` entries. It has no runner for `lessons/tools`, so a changed file could not be proved equivalent (same finding as EXC-544, EXC-545, EXC-555, EXC-556).
- Hard rule 1: if equivalence cannot be proved, leave the family English. `translation/localization-scope.yaml` keeps it `frozen`; no protected file changed.

## Follow-up

If an oracle runner for `lessons/tools` is added, the comments can be localized with `tools/loc_apply.py`.
