---
id: a05-editorial-move
status: pending
depends_on: []
touches:
  - review/inbox/chatgpt-editorial-2026-11-20.md
  - review/editorial/**
  - plans/v4-es-1b/steps/a05-editorial-move.md
lane: none
gate: test ! -e review/inbox/chatgpt-editorial-2026-11-20.md && test -s review/editorial/chatgpt-editorial-2026-11-20.md && test -s review/editorial/README.md && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
tier: light
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Move the free-form ChatGPT review out of the Jury inbox

Anomaly A5. `review/inbox/` must hold only machine replies in the reply format. `review/inbox/chatgpt-editorial-2026-11-20.md` is a free-form editorial review of commit `22e3a5f`.

## Change

- `git mv review/inbox/chatgpt-editorial-2026-11-20.md review/editorial/chatgpt-editorial-2026-11-20.md`. Do not change its text.
- `review/editorial/README.md`: three lines in English: what the folder holds, that the items are triaged by step e01 of plan `v4-es-1b`, and that a reviewed commit is named in each file.

## Do not change

- Files outside `touches`. The `gate`. The text of the review.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
