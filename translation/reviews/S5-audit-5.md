# S5-audit-5: Part II audit of eight S5 families (iteration 470)

Scope: S5-fam-awk-weird, S5-fam-haskell-weird, S5-fam-javascript-weird, S5-fam-lisp-weird, S5-fam-tcl-weird, S5-fam-regex-dotnet, S5-fam-regex-pcre2grep, S5-fam-regex-perl.

## Checks run

- `python3 tools/lock_code.py --verify`: ok, 230 frozen files match the manifest.
- `python3 -I tools/part2_inv.py --check`: 0 records, 0 findings (identifier ledger still empty).
- `python3 -I tools/oracle.py --entry <family> --english /home/lehmer/english-source` for src/awk-weird, haskell-weird, javascript-weird, lisp-weird, tcl-weird, regex-pcre2grep, regex-perl: PASS, no findings, each.
- `diff -rq` of `src/` against the English clone, ignoring Markdown: no differing file outside a family marked localizing in this audit's scope or in earlier audits. regex-dotnet shows no non-Markdown difference.
- No Spanish card category (`Reuniones`, `Programación`, `Depuración`, `Aprendizaje`) appears in the seven localized families, so no mixed forms.
- Exception register has rows EXC-574 to EXC-581, each with a stated reason.

## Findings

1. **Seven families are comments-only, oracle PASS.** No finding.
2. **Oracle reports `deterministic: false` for all seven**, as in earlier audits. Same open observation; no task opened.
3. **regex-dotnet left English, NOT TESTED** (EXC-578): the oracle fails on the unmodified English baseline too. Correct under hard rule 1; a capability gap, not a defect.
4. **Categories and display strings stay English** in the localized families, consistent with decision 11 (one form per file).

## Verdict

No violation of the hard rules. No protected file changed outside a family marked `localizing`. No review-fix tasks needed from this audit.
