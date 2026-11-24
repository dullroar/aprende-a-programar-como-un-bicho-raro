---
id: t06-backtranslation
status: pending
depends_on: [a03-batch-review-kind]
touches:
  - tools/backtranslate_requests.py
  - tools/test_backtranslate_requests.py
  - tools/fixtures/backtranslate/**
  - translation/prompts/backtranslate-blind.md
  - plans/v4-es-1b/steps/t06-backtranslation.md
lane: none
gate: python3 plans/v4-es-1/gatelib.py tests tools/test_backtranslate_requests.py && python3 plans/v4-es-1/gatelib.py tests && python3 plans/v4-es-1/gatelib.py verify && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
tier: light
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Write backtranslate_requests.py: blind back-translation of the critical tier

A back-translation lets Jim read the Spanish in English, and it is a second method next to the Jury. The model sees only the Spanish.

## Change

- `translation/prompts/backtranslate.md` exists. Read it. If it lets the model see the English, write `translation/prompts/backtranslate-blind.md` that does not.
- `tools/backtranslate_requests.py rows --units FILE --tier critical --out-dir D`, `tickets` (as in `tools/jury_requests.py`), and `collect --results DIR --out translation/work/backtranslation/` (untracked: it holds canaried units). One request for each Spanish file of the tier, with the file in the cached block. Output: one JSON object for each unit: `unit_id`, `english`.
- Tests: a unit with English in the input is refused; a good file of three units.

## Do not change

- Files outside `touches`. The `gate`.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
