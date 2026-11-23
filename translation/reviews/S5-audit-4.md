# S5-audit-4: Part II audit of eight S5 families (iteration 460)

Scope: S5-fam-modernchallenge1, S5-fam-pythonchallenge1, S5-fam-rustchallenge1, S5-fam-cobol-weird, S5-fam-apl, S5-fam-apl-weird, S5-fam-m4, S5-fam-forth-weird.

## Checks run

- `python3 tools/lock_code.py --verify`: ok, 230 frozen files match the manifest.
- `python3 -I tools/part2_inv.py --check`: 0 records, 0 findings (identifier ledger still empty).
- `python3 -I tools/oracle.py --entry <family> --english /home/lehmer/english-source` for src/m4, src/PythonChallenge1, src/apl, src/apl-weird, src/cobol-weird, src/forth-weird: PASS, no findings, each.
- `diff -rq` of `src/` against the English clone, ignoring Markdown: every differing file belongs to a family marked localizing. ModernChallenge1 and RustChallenge1 are byte-identical to English.
- No Spanish card category (`Reuniones`, `Programación`, `Depuración`, `Aprendizaje`) appears in the six localized families, so no mixed forms.
- Exception register has rows EXC-566 to EXC-573, each with a stated reason.

## Findings

1. **Six localized families are comments-only, oracle PASS.** No finding.
2. **Oracle reports `deterministic: false` for all six**, as in audits 1 to 3. Same open observation; no task opened.
3. **Two families left English, NOT TESTED** (ModernChallenge1: no entry image; RustChallenge1: cargo image build needs network, forbidden by hard rule 2). Correct under hard rule 1; a capability gap, not a defect.
4. **Categories and display strings stay English** in the localized families, consistent with decision 11 (one form per file).

## Verdict

No violation of the hard rules. No protected file changed outside a family marked `localizing`. No review-fix tasks needed from this audit.
