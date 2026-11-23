# S5-audit-6: Part II audit of five S5 families (iteration 476)

Scope: S5-fam-regex-sed, S5-fam-tar-gnu, S5-fam-tar-gnu-weird, S5-fam-ed-weird, S5-fam-ex-weird.

## Checks run

- `python3 tools/lock_code.py --verify`: ok, 230 frozen files match the manifest and the English clone agree.
- `python3 -I tools/part2_inv.py --check`: 0 records, 0 findings (identifier ledger still empty).
- `python3 -I tools/oracle.py --entry src/<family> --english /home/lehmer/english-source` for src/regex-sed, tar-gnu, tar-gnu-weird, ed-weird, ex-weird: PASS, no findings, each.
- `diff -rq` of `src/` against the English clone, ignoring Markdown: the five families differ only in files of families marked localizing; no other unexpected difference.
- No Spanish card category (`Reuniones`, `Programación`, `Depuración`, `Aprendizaje`) appears in any non-Markdown file of the five families, so no mixed forms.
- Exception register has rows EXC-582 to EXC-586.

## Findings

1. **All five families are comments-only, oracle PASS.** No finding.
2. **Oracle reports `deterministic: false` for all five**, as in earlier audits. Same open observation; no task opened.
3. **Categories and display strings stay English**, consistent with decision 11 (one form per file).

## Verdict

No violation of the hard rules. No protected file changed outside a family marked `localizing`. No review-fix tasks needed from this audit.
