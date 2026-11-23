# S5-audit-3: Part II audit of eight S5 families (iteration 451)

Scope: S5-fam-javascript, S5-fam-javascript-events, S5-fam-lisp, S5-fam-make-gnu, S5-fam-tcl, S5-fam-gochallenge1, S5-fam-javachallenge1, S5-fam-kotlinchallenge1.

## Checks run

- `python3 tools/lock_code.py --verify`: ok, 230 frozen files match the manifest.
- `python3 -I tools/part2_inv.py --check`: 0 records, 0 findings (identifier ledger still empty).
- `python3 -I tools/oracle.py --entry <family> --english /home/lehmer/english-source` for src/javascript, src/javascript-events, src/lisp, src/make-gnu, src/tcl: PASS, no findings, each.
- `diff -rq` of `src/` against the English clone, ignoring Markdown: the only differing files belong to families marked localizing (awk, cmake, cobol, find-gnu, find-posix, forth, haskell, javascript, javascript-events, lisp, make-gnu, tcl). gochallenge1, javachallenge1 and kotlinchallenge1 are byte-identical to English.
- No Spanish card category (`Reuniones`, `Programación`, `Depuración`, `Aprendizaje`) appears in the five localized families, so no mixed forms.
- Exception register has 8 rows for EXC-558 to EXC-565, each with a stated reason.

## Findings

1. **Five localized families are comments-only, oracle PASS.** No finding.
2. **Oracle reports `deterministic: false` for all five**, as in audits 1 and 2. Same open observation; no task opened.
3. **Three families left English, NOT TESTED** (gochallenge1, javachallenge1, kotlinchallenge1): the image build needs network, which hard rule 2 forbids. Correct under hard rule 1; a capability gap, not a defect. A Docker- and network-capable session could retry them.
4. **Categories and display strings stay English** in the five localized families, consistent with decision 11 (one form per file).

## Verdict

No violation of the hard rules. No protected file changed outside a family marked `localizing`. No review-fix tasks needed from this audit.
