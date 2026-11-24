---
id: f01-price-table
status: pending
depends_on: []
touches:
  - translation/batch-prices.yaml
  - tools/batch_prices.py
  - tools/test_batch_prices.py
  - tools/fixtures/batch-prices/**
  - plans/v4-es-1b/steps/f01-price-table.md
lane: none
gate: python3 -I tools/batch_prices.py --check --allow-placeholder && python3 plans/v4-es-1/gatelib.py tests tools/test_batch_prices.py && python3 plans/v4-es-1/gatelib.py tests && python3 plans/v4-es-1/gatelib.py verify && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
tier: light
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Write the batch price table and its checker

## Change

- `translation/batch-prices.yaml`: one entry for each model, with `provider`, `model`, `batch_input`, `batch_output`, `cache_write_5m`, `cache_write_1h`, `cache_read` (USD per million tokens, batch prices), `prompt_limit_tokens` (if a price tier changes at a size), `source` (URL) and `read_on` (date). Fill the Anthropic rows from the table "Models and prices" of `plans/v4-es-1b/plan.md`: batch input and output as given; cache writes = the listed write price × 0.5; cache read = batch input × the cache-hit multiplier (Haiku 5.5: 0.1; Opus 5.5: 0.05; Fable 5.2: 0.025) and mark them `derived: true`. Add `claude-sonnet-5-5` with `excluded: translator model`. Add two OpenAI rows with every value `SET-BY-JIM`.
- `tools/batch_prices.py --check [--allow-placeholder]`: fail on a missing field, a negative value, a placeholder (unless the flag is given), a duplicate model, or a model that is `excluded` but used in `translation/review-routing.yaml` (when that file exists).
- `tools/test_batch_prices.py`: one fixture for each rule.

## Do not change

- Files outside `touches`. The `gate`. Never use the network: the OpenAI rows wait for Jim (step f02).

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
