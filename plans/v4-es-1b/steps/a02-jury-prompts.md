---
id: a02-jury-prompts
status: pending
depends_on: []
touches:
  - tools/jury_prompts.py
  - tools/test_jury_prompts.py
  - tools/fixtures/jury-prompts/**
  - translation/prompts/jury-master.md
  - translation/prompts/jury-lenses/**
  - ralph-kit-es/README.md
  - plans/v4-es-1b/steps/a02-jury-prompts.md
lane: none
gate: python3 -I tools/jury_prompts.py --check && python3 plans/v4-es-1/gatelib.py tests tools/test_jury_prompts.py && python3 plans/v4-es-1/gatelib.py tests && python3 plans/v4-es-1/gatelib.py verify && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
tier: light
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Make the tracked review prompt the single source of the master prompt and the 13 lenses

Anomaly A4. The tools of `v4-es-1` read `review/ADVERSARIAL-REVIEW-PROMPT.md`, an untracked copy. A worktree does not have it. The tracked source is `ralph-kit-es/ADVERSARIAL-REVIEW-PROMPT.md`.

## Change

- `tools/jury_prompts.py`:
  - `split --source ralph-kit-es/ADVERSARIAL-REVIEW-PROMPT.md --out translation/prompts`: write `translation/prompts/jury-master.md` (the text from the line `# Your job` to the line before `# Lens modules`, without the section "For Jim: how to use this file") and `translation/prompts/jury-lenses/L01.md` to `L13.md` (one lens paragraph each, the text as written). Write `translation/prompts/jury-lenses/SOURCE.sha256` with the sha256 of the source file.
  - `--check`: fail if a lens file is missing or empty, if there are not exactly 13, if the sha256 differs from the source, or if a split again gives different bytes. Print one message for each rule.
- Run `split`. Commit the output.
- `ralph-kit-es/README.md`: change "ten lens modules" to "13 lens modules (L1 to L13)". Add one line: the tools read the split files in `translation/prompts/`, not a copy in `review/`.
- `tools/test_jury_prompts.py`: a good fixture passes; a fixture with 12 lenses, a fixture with an empty lens and a changed source each fail with their own message.

## Do not change

- Files outside `touches`. The `gate`. The text of the prompt itself. `loop/` (keep the old handoff notes as history).

## Done when

- `python3 -I tools/jury_prompts.py --check` passes in a worktree that has no `review/ADVERSARIAL-REVIEW-PROMPT.md`.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
