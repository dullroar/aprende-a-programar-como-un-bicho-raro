# S5-fam-regex-pcre2 batch report: src/regex-pcre2

Iteration 430. Verdict: **NOT TESTED. Family left English (EXC-548).**

## What was tried

- Translated 8 comment spans in `timecards.c`, 5 in `check.sh` and 3 in `Dockerfile` through `tools/loc_apply.py` (all applied, line counts unchanged, `check.sh` loop-keyword filter unaffected because the C comment lines it excludes keep their markers).
- `python3 -I tools/oracle.py --entry src/regex-pcre2 --english /home/lehmer/english-source` returned **FAIL**, with findings on the English run as well as the Spanish one (for example "english: card 3: running total 15, expected 61"). Findings are identical in kind in both runs, so the cause is the oracle's reading of this entry's output (the entry appends to a data file, and the "latest run below" section appears to include earlier runs), not the comment edits.
- Hard rule 1: equivalence is not proved, so the edits were reverted and the PO files deleted. `translation/localization-scope.yaml` keeps the family `frozen`; no protected file changed.

## Follow-up

Fix the oracle's card parser for this entry (use only the records after the last `# DEMO ONLY` header, or a fresh data dir per run), then re-apply. The 16 comment translations are easy to redo.
