# S5-audit-1: Part II audit of eight S5 families (iteration 432)

Scope: S5-fam-cobol, S5-fam-forth, S5-fam-regex-pcre2, S5-fam-xaml, S5-fam-linqchallenge1, S5-fam-linqchallenge2, S5-fam-lessons-solutions-b7-linq, S5-fam-lessons-book-diagrams.

## Checks run

- `python3 tools/lock_code.py --verify`: ok, 230 frozen files match the manifest.
- `python3 -I tools/part2_inv.py --check`: 0 records, 0 findings (the identifier ledger is still empty, so I28 to I31 had nothing to check).
- `python3 -I tools/oracle.py --entry src/cobol` and `--entry src/forth` against `/home/lehmer/english-source`: PASS, no findings.
- `diff -rq` of `src/` against the English clone, ignoring Markdown: only `src/cobol` and `src/forth` differ (Dockerfile, check.sh and the program file in each). The other six families are byte-identical to English, as their reports say.
- No Spanish card category appears in `src/cobol` or `src/forth` (grep), so no mixed forms.
- Exception register has EXC-544 to EXC-549 for the six families left English, each with a stated reason.

## Findings

1. **Localized families are comments-only, oracle PASS.** cobol (60 comment lines) and forth (38 + 7 lines) match their reports. No finding.
2. **Oracle reports `deterministic: false` for both** and also did for the English baseline. This weakens the PASS: a nondeterministic run is not proof of equal output. Not a regression; needs a decision on whether the oracle should compare after normalizing the nondeterministic fields. Recorded as an observation, no task opened.
3. **Five families (xaml, linqchallenge1, linqchallenge2, lessons-solutions-b7-linq, lessons-book-diagrams) are NOT TESTED** because no oracle runner or entry image exists for WPF/EF Core entries, lessons/solutions or the diagram build script. Left English is correct under hard rule 1; the cost is that their comments stay untranslated. A future task could add runners; this is a capability gap, not a defect.
4. **regex-pcre2 oracle fails on the English baseline** (card-sum mismatch, EXC-548). This suggests a bug in the oracle comparison, the fixture, or the English example. It should be triaged before any later attempt at this family. Suggested follow-up: a review-fix task to find out which of the three is wrong.
5. **Forth lines 40 to 42** keep English trailing comments because `loc_apply` supports one span per line. Documented in EXC-543. Consistent, but it leaves a mixed-language file; a `loc_apply` extension for two spans per line would close it.
6. **Card categories stay English in cobol and forth** (decision 11) because code still prints them. Consistent with the "one form per file" rule; localizing them needs data-layout changes in COBOL and its own oracle step.

## Verdict

No violation of the hard rules. No protected file changed outside a family marked `localizing`. Follow-ups suggested (not queued by this audit): triage item 4; decide on item 2; optional tool work for items 3 and 5.
