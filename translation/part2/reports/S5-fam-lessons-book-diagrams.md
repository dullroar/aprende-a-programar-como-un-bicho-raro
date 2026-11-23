# S5-fam-lessons-book-diagrams batch report: lessons/book/diagrams

Iteration 426. Verdict: **NOT TESTED. Family left English (EXC-544).**

## Why nothing changed

- The family is build tooling for the PDF: `flatten-text.mjs` (the only file with comments, 16 comment lines) plus `mermaid-config.json`, `package.json` and `package-lock.json` (no comments, strings are JSON keys, npm metadata and hashes).
- `tools/oracle.py` proves equivalence by running a `src/` entry English against Spanish in the sandbox and comparing a semantic record. It has no runner for a Node build script, so a changed `flatten-text.mjs` could not be proved equivalent. Hard rule 1: if equivalence cannot be proved, leave the family English.
- `translation/localization-scope.yaml` keeps `lessons/book/diagrams` as `frozen`; no protected file changed, and `translation/localized-code.sha256` is untouched.

## Not a loss for readers

The comments are maintainer notes inside a build script. They do not appear in the book.

## Follow-up

If a build-tool oracle is added later (render a fixed SVG through the script, English vs Spanish, compare bytes), this family can be localized with `tools/loc_apply.py` (16 comment entries, line count unchanged).
