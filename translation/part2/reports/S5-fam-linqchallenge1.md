# S5-fam-linqchallenge1 batch report: src/LinqChallenge1

Iteration 428. Verdict: **NOT TESTED. Family left English (EXC-546).**

## Why nothing changed

- The entry is a WPF and EF Core program (Windows only). It has no Dockerfile, so `python3 -I tools/oracle.py --entry src/LinqChallenge1 --english /home/lehmer/english-source` reports NOT TESTED: "LinqChallenge1 has no Dockerfile (no entry image)".
- The 45 comments (Program.cs, TimecardDbContext.cs, check.ps1) could be translated, but without a run no equivalence proof exists. Hard rule 1: leave the family English.
- `translation/localization-scope.yaml` keeps the family `frozen`; no protected file changed.

## Follow-up

Run the oracle under Windows Sandbox (`sandbox/windows/run.ps1`) once a runner exists, then localize comments with `tools/loc_apply.py`.
