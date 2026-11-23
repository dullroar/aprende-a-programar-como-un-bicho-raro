# S5-fam-linqchallenge2 batch report: src/LinqChallenge2

Iteration 429. Verdict: **NOT TESTED. Family left English (EXC-547).**

## Why nothing changed

- The entry is a WPF and EF Core program (Windows only). It has no Dockerfile, so `python3 -I tools/oracle.py --entry src/LinqChallenge2 --english /home/lehmer/english-source` reports NOT TESTED: "LinqChallenge2 has no Dockerfile (no entry image)".
- The 78 comments (Program.cs, TimecardDbContext.cs, TimecardEntry.cs, check.ps1) could be translated, but without a run no equivalence proof exists. Hard rule 1: leave the family English.
- `translation/localization-scope.yaml` keeps the family `frozen`; no protected file changed.

## Follow-up

Run the oracle under Windows Sandbox (`sandbox/windows/run.ps1`) once a runner exists, then localize comments with `tools/loc_apply.py`.
