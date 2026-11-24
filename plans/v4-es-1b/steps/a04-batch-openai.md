---
id: a04-batch-openai
status: pending
depends_on: [a03-batch-review-kind]
touches:
  - tools/batch_openai.py
  - tools/test_batch_openai.py
  - tools/fixtures/batch-openai/**
  - plans/v4-es-1b/steps/a04-batch-openai.md
lane: none
gate: python3 plans/v4-es-1/gatelib.py tests tools/test_batch_openai.py && python3 plans/v4-es-1/gatelib.py tests && python3 plans/v4-es-1/gatelib.py verify && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Add the OpenAI Batch API with the same contract as tools/batch.py

The OpenAI Batch API is the second vendor and the overflow. Keep the same files and the same contract as `tools/batch.py --kind review`, so that the submitter treats both alike.

## Change

- `tools/batch_openai.py` (standard library only, import the helpers of `tools/batch.py`, do not copy them):
  - `build --kind review`: the same input rows. Output JSONL lines `{"custom_id", "method": "POST", "url": <endpoint>, "body": {...}}`. Put the master prompt first and the packet second, so that the shared prefix is the same across the lenses of one packet. Read the endpoint and the body shape from the OpenAI Batch API reference and write the source URL in the docstring.
  - `submit`: upload the file, create the batch with a 24-hour window. Needs `OPENAI_API_KEY` and `--max-usd`. Same cost file, with `"provider": "openai"`.
  - `status`, `collect` (download the output and the error files), and the same `{"request_id", "custom_id", "model", "text", "usage"}` rows. Read `cached_tokens` from the usage block when it is there.
  - The key is read only from the environment. Never write it, a request header or a full response envelope.
- `tools/test_batch_openai.py`: injected HTTP only. Good build; bad ID; a collected output with an error line; cost with and without cached tokens.

## Do not change

- Files outside `touches`. The `gate`. `tools/batch.py`.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
