---
id: t05-adjudication
status: pending
depends_on: [a03-batch-review-kind, t01-lane-tools]
touches:
  - tools/adjudicate_requests.py
  - tools/test_adjudicate_requests.py
  - tools/fixtures/adjudicate/**
  - translation/prompts/adjudicate-batch.md
  - plans/v4-es-1b/steps/t05-adjudication.md
lane: none
gate: python3 plans/v4-es-1/gatelib.py tests tools/test_adjudicate_requests.py && python3 plans/v4-es-1/gatelib.py tests && python3 plans/v4-es-1/gatelib.py verify && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Write adjudicate_requests.py: batch adjudication, the cross-vendor audit and the English memo

This replaces the agent adjudication of old step `j06`. The adjudicator is Opus 5.5 in batch. It is not the translator's model and not a juror of the finding it decides.

## Change

- `translation/prompts/adjudicate.md` exists. Read it. Write `translation/prompts/adjudicate-batch.md`: the batch wrapper. Input: one Spanish file (all its units), the English units, the back-translation of each unit when there is one, and all findings for that file. Output: one JSON object for each finding: `id`, `status` (`accepted|rejected|duplicate|needs-human|needs-source-issue`), `reason` (one line), `en_gloss` (an English rendering of the Spanish excerpt, for Jim). Rules: never decide by majority vote; check each quote; set `needs-human` for playfulness the panel did not agree on, a guarantee, the 40-rule, safety and the acronym; set `needs-source-issue` for a defect of the English. The adjudicator may add a finding with `origin: adjudicator-backtranslation` when the back-translation shows a meaning change that no juror reported. Such a finding is `needs-human` unless the audit agrees.
- `tools/adjudicate_requests.py`:
  - `rows --findings FILE --units FILE --backtranslations DIR --out-dir D`: one row for each Spanish file that has findings, and one for each critical-tier file without findings (so that the back-translation is checked). Put the master rules in the prefix and the file in the cached packet block.
  - `audit-rows`: a stratified sample for the other vendor: every critical finding, every `needs-source-issue`, and 10 % of the rest (seed 1).
  - `tickets` as in `tools/jury_requests.py`.
  - `apply --results DIR --findings FILE`: write `status`, `reason`, `en_gloss`, `adjudicator_model` into the findings. Where the audit and the adjudicator disagree, set `needs-human` and keep both reasons. Never change another field.
  - `memo --findings FILE --out review/human-decisions-<date>.md`: one section for each `needs-human` row, in English: the English source, the Spanish excerpt, its `en_gloss`, the juror claim, the adjudicator and audit views, and the options `accepted|rejected|source-issue`, with a line `decision: ` and `reason: ` for Jim to fill. Sort by severity.
  - `memo-merge --memo FILE --findings FILE`: copy Jim's `decision` and `reason` into `human_decision` and `human_reason`.
- Tests for each command, with a disagreement, a quote that does not match, and a memo round trip.

## Do not change

- Files outside `touches`. The `gate`. `translation/prompts/adjudicate.md`.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
