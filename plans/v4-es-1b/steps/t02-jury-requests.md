---
id: t02-jury-requests
status: pending
depends_on: [a02-jury-prompts, a03-batch-review-kind]
touches:
  - tools/jury_requests.py
  - tools/test_jury_requests.py
  - tools/fixtures/jury-requests/**
  - translation/prompts/jury-verify.md
  - plans/v4-es-1b/steps/t02-jury-requests.md
lane: none
gate: python3 plans/v4-es-1/gatelib.py tests tools/test_jury_requests.py && python3 plans/v4-es-1/gatelib.py tests && python3 plans/v4-es-1/gatelib.py verify && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Write jury_requests.py: matrix tickets from the routing file and the inbox writer

This replaces the jury part of step `g02` of `v4-es-1`. It uses `tools/batch.py --kind review` (step a03) and the split prompts (step a02).

## Change

- `tools/jury_requests.py`:
  - `rows --packets DIR --routing FILE --wave W --out-dir D`: for each packet and each lens that `FILE` assigns, write one input row for `batch.py build --kind review` (step a03 gives the shape). Lens rule: prose packets get L1 to L10, code packets get L11 to L13. L7 gets a Spanish-only rendering of the packet (use the packet builder's Spanish-only mode if it has one; if it has none, set `status: blocked` and write it under "Resume notes"). L3 gets the humor register rows of the packet's units in `tail_text`. The prefix is `translation/prompts/jury-master.md` plus `review/EDITION-FACTS.md`; the tail is the lens file and the line `Your lens: L<n>`. Each critical packet also gets L1, L2 and L9 from the second-vendor model of the routing file. Write one row file for each `(provider, model)`.
  - `tickets --rows-dir D --wave W --lane L --outbox DIR --record FILE`: call `batch.py build --kind review` (or `batch_openai.py build`) for each row file, write the ticket JSON (see "Shared facts" in `plans/v4-es-1b/plan.md`), and write `FILE` with `tickets:`, `requests:`, `estimate-usd:` (uncached upper bound from `translation/batch-prices.yaml`), `input-sha256:` and `lenses:`.
  - `inbox --results-dir DIR --out-dir review/inbox --date D`: for each collected result, write `review/inbox/batch-<provider>-<model>-<lens>-<date>.md`, one file for each `(model, lens)`, with the header line and the JSONL lines of the reply, exactly as the model wrote them. A reply that is not in the format goes to `<file>.rejects.md` next to it, with the reason, and counts as a failed request.
  - `verify-rows --since-record plans/v4-es-1b/records/j03-ingest.md --findings GLOB --units FILE --routing FILE --out-dir D`: for each unit that changed since the `base-commit:` of that record, one row with the English, the old Spanish (from the base commit), the new Spanish and the findings that the change must resolve. Prompt `translation/prompts/jury-verify.md` (write it): for each finding, `resolved: yes|no` with a reason, then any new finding in the reply format. The model is a juror of the routing file that is not the fix drafter of that unit.
  - `verify-ingest --wave W --findings GLOB --out review/round-two-<date>.md`: write the report and `review/round-two-<date>.jsonl` (new findings and unresolved old ones, in the finding schema, exact quotes checked).
  - Every command that reads results takes `--wave W` and reads the submitter inbox (`$RALPH_WORK/aprende-a-programar-como-un-bicho-raro/v4-es-1b/batch/inbox/`) unless `--results-dir` is given.
- `tools/test_jury_requests.py`: an unresolved finding and a new finding in a verify reply; a packet with no lens in the routing; a code packet that would get L4; a request over 100 000 tokens; a reply with no header; a good matrix of two packets gives 10 + 3 rows in the right order (same packet next to each other).

## Do not change

- Files outside `touches`. The `gate`. `tools/batch.py`, `tools/jury_ingest.py`, `tools/jury_packet.py`. Never call the network.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
