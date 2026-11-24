---
id: a03-batch-review-kind
status: pending
depends_on: []
touches:
  - tools/batch.py
  - tools/test_batch.py
  - tools/fixtures/batch/**
  - plans/v4-es-1b/steps/a03-batch-review-kind.md
lane: none
gate: python3 plans/v4-es-1/gatelib.py tests tools/test_batch.py && python3 plans/v4-es-1/gatelib.py tests && python3 plans/v4-es-1/gatelib.py verify && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Let tools/batch.py send review requests with a cached packet block and exact cost fields

Anomalies A1, A2 and A3. Keep the `translate` behavior byte for byte: the existing tests must pass unchanged.

## Change

- `tools/batch.py build` gets `--kind translate|review` (default `translate`).
  - `review`: input rows are `{"request_id", "prefix_blocks": [FILE...], "packet_file", "tail_text", "max_tokens"}`. `request_id` matches `^[A-Za-z0-9_-]{1,51}$`, so that `custom_id = request_id + "_" + 12 hex` stays within 64 characters. Check the custom ID rule against the Message Batches API reference and write the source URL in the docstring.
  - System block: the files of `--prompt-manifest FILE` (one path per line), joined in order, with `cache_control` on the last system block. No translator wrapper, no house style, no glossary unless the manifest names them.
  - User content: block 1 = the packet text with `cache_control`, block 2 = `tail_text` without `cache_control`. At most 4 cache breakpoints for each request.
  - `--cache-ttl 5m|1h` (default `1h` for `review`). Write the exact `cache_control` shape that the API reference gives for a 1-hour lifetime.
  - Sort the output so that rows with the same `packet_file` are next to each other.
  - Refuse a request whose estimated prompt is more than 100 000 tokens (4 characters per token, conservative), because Haiku 5.5 changes price above that.
- `collect`: read `usage.input_tokens`, `cache_creation_input_tokens` (and the split by lifetime if present), `cache_read_input_tokens`, `output_tokens`. Write them in the cost record. With `--prices translation/batch-prices.yaml --model M`, compute the exact cost with the batch prices of that model; without it, keep the old upper bound.
- `collect --kind review`: write `{"request_id", "custom_id", "model", "text", "stop_reason", "usage"}` rows. Do not parse the reply.
- `segment_of()` and `load_requests()` accept the review ID shape when `--kind review` is given.
- Tests (inject the HTTP function, as now): a good review build; a bad ID; a 65-character custom ID; a prompt over the limit; the cache blocks are where this step says; `translate` output is byte-equal to the fixture of today; exact cost from a usage block with cache reads.

## Do not change

- Files outside `touches`. The `gate`. The program cap logic. The rule that the key is read only from the environment and never written.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
