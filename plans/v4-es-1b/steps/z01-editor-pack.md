---
id: z01-editor-pack
status: pending
depends_on: [p08-final-build]
touches:
  - review/editors/**
  - plans/v4-es-1b/steps/z01-editor-pack.md
lane: none
gate: for f in LEEME README pendientes open-items como-se-reviso how-it-was-reviewed; do test -s review/editors/$f.md || exit 1; done && for h in $(grep '^asset: .*\.pdf ' plans/v4-es-1b/records/p08-final-build.md | awk '{print $3}'); do grep -q "$h" review/editors/README.md && grep -q "$h" review/editors/LEEME.md || exit 1; done && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
tier: light
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Write the hand-off package for the human editors

The editors are Spanish-speaking programmers. Jim does not read Spanish. Write each file in Spanish and in English (two files, same content), so that Jim can check what was sent.

## Change

- `review/editors/LEEME.md` and `review/editors/README.md`: what the edition is (one paragraph), what to read (the three PDFs, with the SHA-256 of each from `plans/v4-es-1b/records/p08-final-build.md`), the time it takes (estimate by page count), what kind of feedback helps most, and the feedback format: one line for each item, `<PDF> p.<page> | <quote> | <problem> | <suggestion>`, or a source file and line if they prefer the repository.
- `review/editors/pendientes.md` and `review/editors/open-items.md`: the items that need a native reader: humor items with `needs-native: true` (`translation/humor-decisions.jsonl`), `needs-human` items that Jim sent to the editors in j06 (`reason: editors - ...`), Fable findings routed to `editors` in p05 (minor findings, suggestions, unverified findings), and any lens marked `weak: true` in `translation/review-routing.yaml`. Give PDF page and source file and line for each.
- `review/editors/como-se-reviso.md` and `review/editors/how-it-was-reviewed.md`: one page: which models reviewed what (from the routing file and the reports), the canary recall, the counts of findings and fixes. No canary data.

## Do not change

- Files outside `touches`. The `gate`. Never write a canary, a key, a path or a personal name.

## Done when

- The six files exist. Each PDF hash in the README equals the hash in the p08 record.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
