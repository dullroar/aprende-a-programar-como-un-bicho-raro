# S5-audit-2: Part II audit of eight S5 families (iteration 441)

Scope: S5-fam-lessons-solutions, S5-fam-lessons-solutions-awk-port, S5-fam-lessons-tools, S5-fam-awk, S5-fam-cmake, S5-fam-find-gnu, S5-fam-find-posix, S5-fam-haskell.

## Checks run

- `python3 tools/lock_code.py --verify`: ok, 230 frozen files match the manifest.
- `python3 -I tools/part2_inv.py --check`: 0 records, 0 findings (identifier ledger still empty).
- `python3 -I tools/oracle.py --entry <family> --english /home/lehmer/english-source` for src/awk, src/cmake, src/find-gnu, src/find-posix, src/haskell: PASS, no findings, each.
- `diff -rq` of `src/` against the English clone, ignoring Markdown: only cobol, forth (audit 1) and the five families above differ (Dockerfile, check.sh, program file; build-line.py for the two find families). Nothing else under `src/` differs.
- `diff -rq` of `lessons/solutions` (non-Markdown) and `lessons/tools` against English: no code difference. The only difference is `lessons/tools/README.md`, which is translated prose.
- No Spanish card category (`Reuniones`, `Programación`, `Depuración`, `Aprendizaje`) appears in the five localized families, so no mixed forms.
- Exception register has EXC-550 to EXC-557, each with a stated reason.

## Findings

1. **Five localized families are comments-only, oracle PASS.** Line counts match the commit stats (awk 38, cmake 62, find-gnu, find-posix, haskell 36 changed lines). No finding.
2. **Oracle reports `deterministic: false` for all five**, as in audit 1. The PASS is weaker than it looks; same open observation as S5-audit-1 item 2. No task opened.
3. **Three families left English, NOT TESTED** (lessons/solutions, awk-port, lessons/tools): no oracle runner for reference solutions or sandbox scripts. Correct under hard rule 1; a capability gap, not a defect.
4. **Categories and display strings stay English** in all five localized families (EXC-550 to EXC-554) because the code prints them as data. Consistent with decision 11 (one form per file).

## Verdict

No violation of the hard rules. No protected file changed outside a family marked `localizing`. No review-fix tasks needed from this audit.
