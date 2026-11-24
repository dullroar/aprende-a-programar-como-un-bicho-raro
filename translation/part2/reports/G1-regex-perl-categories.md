# G1-005 batch report: card categories in src/regex-perl (decision 11)

Iteration 540. Verdict: **oracle PASS in Spanish; categories localized and the tape-skip class made accent-safe. Resolves EXC-591.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.pl`: C7 (the tape of category names, the `qw(...)` list, and the `[A-Za-z]*` tape skip widened to `[A-Za-zÁÉÍÓÚáéíóúñ]*`, the G1-001 class).
- `check.sh`: C27, C32, C48, C50 (category alternations, order test and message) and the comment on line 43.
- `README.md`: output rows, the category spans, and the widened class in the pulse row; added to both category-localized lists.
- `translation/localized-code.sha256` rewritten; EXC-591 marked resolved.

## Proof

- `python3 -I tools/oracle.py --entry src/regex-perl --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
