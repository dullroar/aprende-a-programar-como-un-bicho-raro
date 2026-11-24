# G1-004 batch report: card categories in src/regex-pcre2grep (decision 11)

Iteration 539. Verdict: **oracle PASS in Spanish; categories localized and the tape-skip class made accent-safe. Resolves EXC-590.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.sh`: C18 (the one-line tape of category names), C20 (the pattern: the `(Reuniones|Programación|Depuración|Aprendizaje)` alternation, and the `[A-Za-z]*` tape skip widened to `[A-Za-zÁÉÍÓÚáéíóúñ]*`, the G1-001 class).
- `check.sh`: C36, C38, C40, C59, C61 (category lists and expected rows) and the comment on line 54.
- `README.md`: output rows, the tape and alternation spans, and the widened class in the pulse row; added to both category-localized lists.
- Tooling: `categories.WORD_RE` and `apply._WORD_RE` accept the glued tape (`MeetingsCodingDebuggingLearningMeetings247...`); `apply.py` localizes the four-word regex alternation and widens `[A-Za-z]` in README code spans; `invariants._en_cats` maps the widened class back for I13. Tests added in `test_categories.py` (tape, with negatives `Meetings2`, `xMeetings247`) and `test_apply.py`.
- `translation/localized-code.sha256` rewritten; EXC-590 marked resolved.

## Proof

- `python3 -I tools/oracle.py --entry src/regex-pcre2grep --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `lock_code --write-localized`, `part2_inv --check` 0 findings, `verify --fast` OK, `test_apply` and `test_categories` OK.
- Why it works: pcre2grep runs without `-u`, so the widened class matches the UTF-8 bytes of the accented letters one at a time, which is enough for the `*` skip.
