# G1-006 batch report: card categories in src/regex-sed (decision 11)

Iteration 541. Verdict: **oracle PASS in Spanish; categories localized and the four `[A-Za-z]` classes made accent-safe. Resolves EXC-592.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.sed`: C5 (the tape `cats:` list), C16, C55, C60, C62 (the `[A-Za-z]+` captures widened to `[A-Za-zÁÉÍÓÚáéíóúñ]+`, the G1-001 class).
- `check.sh`: C39, C40, C54 (category alternations and the expected five-row string) and the comment on line 35.
- `README.md`: output rows, prose and spans, the fenced tape (`cats:`, ` c:`, `ret:row`, the SQL value) and the widened classes in the fenced `s///` commands; added to both category-localized lists.
- `tools/loc_apply.py`: a `#` inside a sed `s///` command (the tally class `(#+)`, line 55) is regex text, not a comment; the whole line is compared. Negative test included (`test_widen_sed_hash_inside_s_command_is_not_a_comment`).
- `tools/apply.py`: fenced sed tape and `s///` lines follow the code (`test_sed_tape_and_class_in_fence`).
- `translation/localized-code.sha256` rewritten; EXC-592 marked resolved.

## Proof

- `python3 -I tools/oracle.py --entry src/regex-sed --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
