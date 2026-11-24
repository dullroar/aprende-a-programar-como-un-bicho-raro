# G1-002 batch report: card categories in src/ed-weird (decision 11)

Iteration 537. Verdict: **oracle PASS in Spanish; categories localized and regex classes made accent-safe. Resolves EXC-588.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.ed`: C7-C11 (the five `Ns/^/Category /` lines); C42, C44, C45 widen every `[A-Za-z]` to `[A-Za-zÁÉÍÓÚáéíóúñ]` (G1-001 class); L34 comment example now uses the Spanish words.
- `timecards.sh`: C18 (SQL CHECK list) and the L4 comment.
- `check.sh`: C12, C26, C34 (category lists), C78, C79 (swap test), C107, C116, C117, and C21, C80 (greps that must follow the widened regex text in `timecards.ed`).
- `README.md`: output rows, table cell and the two inline spans; added to both category-localized lists.
- Tooling: `apply.py` and `categories.WORD_RE` accept a category word glued after three tally marks (`xxxMeetings`), as the joined ed line shows; 2 new tests (negative: `yMeetings` stays).
- `translation/localized-code.sha256` rewritten; EXC-588 marked resolved.

## Proof

- `python3 -I tools/oracle.py --entry src/ed-weird --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK, `test_apply` and `test_categories` OK.

## Left as is

- The Spanish word `Dead` (a marker, not a category) stays English.
