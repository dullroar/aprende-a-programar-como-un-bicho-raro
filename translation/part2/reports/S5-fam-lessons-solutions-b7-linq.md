# S5-fam-lessons-solutions-b7-linq batch report: lessons/solutions/b7-linq

Iteration 427. Verdict: **NOT TESTED. Family left English (EXC-545).**

## Why nothing changed

- `Program.cs` has no comments, so there is nothing to translate line for line. `lq.csproj` is project metadata.
- The only candidates are 8 display strings (`-- (a) declared q`, `effect {i}` and so on). They are the program output that `lessons/respuestas.md` quotes, so changing them would also change the answer key and any trace.
- `tools/oracle.py` only runs `src/` entries. It has no runner for `lessons/solutions`, so a changed file could not be proved equivalent. Hard rule 1: if equivalence cannot be proved, leave the family English.
- `translation/localization-scope.yaml` keeps the family `frozen`; no protected file changed.

## Follow-up

If an oracle runner for `lessons/solutions` is added, the strings can be localized with `tools/loc_apply.py` together with the answer key.
