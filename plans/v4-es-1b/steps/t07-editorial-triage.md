---
id: t07-editorial-triage
status: pending
depends_on: [a03-batch-review-kind, a05-editorial-move]
touches:
  - tools/editorial_triage.py
  - tools/test_editorial_triage.py
  - tools/fixtures/editorial/**
  - translation/prompts/editorial-triage.md
  - plans/v4-es-1b/steps/t07-editorial-triage.md
lane: none
gate: python3 plans/v4-es-1/gatelib.py tests tools/test_editorial_triage.py && python3 plans/v4-es-1/gatelib.py tests && python3 plans/v4-es-1/gatelib.py verify && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
tier: light
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Write editorial_triage.py: turn the ChatGPT review into findings against the current text

Anomaly A5. The review names lines of commit `22e3a5f`. The text has changed since then.

## Change

- `tools/editorial_triage.py`:
  - `items --review review/editorial/chatgpt-editorial-2026-11-20.md`: parse the review into items: `file`, `lines` (as written), `text` of the item. Each bullet under a file heading is one item. Print the count.
  - `rows --review FILE --out-dir D`: one row for each reviewed file. The cached block holds the file at the reviewed commit (`git show 22e3a5f:<file>`) with line numbers and the file now with line numbers. The tail holds the items of that file. Output for each item, in the Jury reply format (header with `juror_model` and `lens: editorial`, then JSONL findings with exact Spanish quotes from the current file), plus `triage`: `still-applies|already-fixed|stale|source-issue`.
  - `tickets` as in `tools/jury_requests.py`. The model is the Opus juror of the routing file.
- `translation/prompts/editorial-triage.md`: that prompt.
- Tests: the item count of the real review (write the number you find in the test), a review with no file heading, a good item.

## Do not change

- Files outside `touches`. The `gate`. The review file.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
