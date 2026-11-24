---
id: t04-fix-requests
status: pending
depends_on: [a03-batch-review-kind, t01-lane-tools]
touches:
  - tools/fix_requests.py
  - tools/test_fix_requests.py
  - tools/fixtures/fix-requests/**
  - translation/prompts/review-fix.md
  - tools/translate.py
  - tools/test_translate.py
  - plans/v4-es-1b/steps/t04-fix-requests.md
lane: none
gate: python3 plans/v4-es-1/gatelib.py tests tools/test_fix_requests.py tools/test_translate.py && python3 plans/v4-es-1/gatelib.py tests && python3 plans/v4-es-1/gatelib.py verify && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Write fix_requests.py: minimal-edit fix drafts in batch, imported through the translate.py checks

A prose fix is a minimal edit of one PO entry. That is a bulk task (route `review-fix: batch` in `translation/routing.md`). A draft that fails the checks goes to a Claude Code fix step.

## Change

- `translation/prompts/review-fix.md`: the fix prompt. Input: the English segment (masked), the current Spanish, the findings for that segment with the adjudicator reason, the house style and glossary (in the cached prefix). Output: a `translator_output` for the same `segment_id`, with the smallest change that resolves every finding, and a `fix_note` in English (one sentence for each finding). Do not change text that no finding names.
- `tools/fix_requests.py`:
  - `rows --findings GLOB --status accepted --units FILE --out-dir D [--humor review/humor-findings.jsonl]`: map each accepted prose finding to its PO segment IDs (`s-<hash>-NNNN`) through the units index. One row for each segment, with all its findings. Humor items with a `better_option` become rows too. A finding that carries `po_file` and `po_line` (from `tools/pdf_review.py`) maps to its segment directly. Code findings and findings with no PO entry are not rows: list them in `D/code-findings.jsonl` for `fix_steps.py`.
  - `tickets ...` as in `tools/jury_requests.py` (same ticket and record shape), with the fix-drafter model of the routing file. The fix drafter is never `claude-sonnet-5-5`.
  - `import --results FILE --applied LEDGER --out-unfixed FILE`: reconcile with `batch.py reconcile`, then call `python3 -I tools/translate.py <file> --drafts <drafts> --draft-model <provider>/<model> --task-id <wave>` for each PO file. Check first whether `translate.py --drafts` accepts a draft for an entry that is already translated. If it does not, add the smallest option to `translate.py` that does, with all its current checks, and a test. Write every segment that a check refused to `--out-unfixed`.
- Tests: a finding with no segment; a code finding goes to the code list; a fix draft that changes another placeholder is refused and listed as unfixed; a good draft imports.

## Do not change

- Files outside `touches`. The `gate`. The checks of `translate.py`.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
