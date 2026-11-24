---
id: t01-lane-tools
status: pending
depends_on: [a05-editorial-move]
touches:
  - tools/fix_steps.py
  - tools/inbox_check.py
  - tools/jury_gate.py
  - tools/test_fix_steps.py
  - tools/test_inbox_check.py
  - tools/test_jury_gate.py
  - tools/fixtures/fix-steps/**
  - tools/fixtures/inbox-check/**
  - tools/fixtures/jury-gate/**
  - plans/v4-es-1b/steps/t01-lane-tools.md
lane: none
gate: python3 plans/v4-es-1/gatelib.py tests tools/test_fix_steps.py tools/test_inbox_check.py tools/test_jury_gate.py && python3 plans/v4-es-1/gatelib.py tests && python3 plans/v4-es-1/gatelib.py verify && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Write fix_steps.py, inbox_check.py and jury_gate.py for this plan

This is step `g01` of `v4-es-1`, adapted: the plan folder is a parameter, the inbox holds only machine replies, and a juror name tells the vendor.

## Change

- `tools/fix_steps.py`:
  - `--findings GLOB --plan-dir DIR --prefix P [--only accepted]`: write one step file `DIR/steps/<P>-po-<po-file-stem>.md` for each PO file with accepted findings that the batch import did not fix (read the list `--unfixed FILE` when given), one `DIR/steps/<P>-code-<family>.md` for each code family with accepted findings, and one `DIR/steps/<P>-other-<source-file-stem>.md` for each source file with accepted findings that have neither a PO entry nor a code family (layout, figure or build findings from the Fable report). Each step file has the front matter of `plans/for-each-plan/steps/00-step-template.md`, `agent: claude`, `depends_on: [<the generator step>]`, `touches` = the PO file and its generated Markdown (or the code family), and a gate that runs `python3 -I tools/fix_steps.py --verify-fixed --step <id>`, the tool tests, `verify --fast` and `guard`. The body lists each finding: id, severity, file, the exact quotes, the adjudicator reason and (for prose) the English source.
  - `--check --findings GLOB --plan-dir DIR --prefix P`: every accepted finding is in exactly one generated step; no two generated steps touch the same file.
  - `--all-done DIR --prefix P`: exit 0 when every step `DIR/steps/<P>-*.md` is `done`.
  - `--verify-fixed --step ID`: each finding of the step no longer matches its Spanish quote in the file, or the step file records a reason under "Not changed".
- `tools/inbox_check.py`: every file in `review/inbox/` matches `^(batch|outside)-[a-z0-9]+-[a-z0-9.-]+-L(0[1-9]|1[0-3])-[0-9]{4}-[0-9]{2}-[0-9]{2}\.md$` (`batch-<provider>-<model>-<lens>-<date>`) or the editorial juror name `batch-<provider>-<model>-editorial-<date>.md`, has a header line with `juror_model` and `lens`, and is not empty. It fails on any other file and names it.
- `tools/jury_gate.py --stage adjudicated|human|final [--findings GLOB]`:
  - `adjudicated`: no finding has status `open`.
  - `human`: every `needs-human` row has `human_decision` and `human_reason`.
  - `final`: `human` plus no unresolved `critical` or `major` (accepted and not fixed by a done fix step), a canary recall line for each juror in the report, `translation/humor-decisions.jsonl` has one row for each register item, and each critical packet had two jurors from two vendors.
- Tests with known-bad and known-good fixtures for each rule.

## Do not change

- Files outside `touches`. The `gate`. `tools/jury_ingest.py`.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
