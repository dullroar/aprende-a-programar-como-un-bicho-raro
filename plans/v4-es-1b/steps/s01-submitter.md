---
id: s01-submitter
status: pending
depends_on: [a03-batch-review-kind, a04-batch-openai, f01-price-table]
touches:
  - tools/batch_submitter.py
  - tools/test_batch_submitter.py
  - tools/fixtures/batch-submitter/**
  - plans/v4-es-1b/steps/s01-submitter.md
lane: none
gate: python3 plans/v4-es-1/gatelib.py tests tools/test_batch_submitter.py && python3 plans/v4-es-1/gatelib.py tests && python3 plans/v4-es-1/gatelib.py verify && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Write the submitter: the only program that holds a key and spends money

The submitter replaces the manual `submit` and `collect` operator steps of `v4-es-1`. Jim runs it from the operator shell, for example every 10 minutes with `python3 tools/batch_submitter.py run --once`. Agents never run `run`.

## Change

- `tools/batch_submitter.py` (standard library only; call `tools/batch.py` and `tools/batch_openai.py` functions):
  - Work folder: `$RALPH_WORK/aprende-a-programar-como-un-bicho-raro/v4-es-1b/batch/` (`--work` overrides). Sub-folders `outbox/`, `submitted/`, `inbox/`, `ledger/`. Cost file `costs.jsonl`.
  - `run --once`: for each ticket in `outbox/` (oldest first): check the sha256 of the request file against the ticket; check the budget (below); submit; move the ticket to `submitted/` with the batch ID. For each submitted batch: poll; when it ends, collect to `inbox/<ticket>.results.jsonl`, write the cost record, then resubmit errored and expired requests once as a new ticket `<ticket>.retry1`. After a second failure write the request in `inbox/<ticket>.failed.jsonl`. Hold a lock file so that two runs never overlap.
  - `budget --wave W --record FILE`: read `estimate-usd:` from FILE and the caps of `plans/v4-es-1b/records/f02-operator-budget.md` (`cap-W0-usd:` to `cap-W6-usd:`, `cap-C-usd:`, `cap-anthropic-total-usd:`, `cap-openai-total-usd:`). Exit 1 if the estimate plus the spend of that wave so far is over the wave cap, or if the vendor total would go over its cap. The Anthropic total cap can never be over `PROGRAM_CAP_USD` of `tools/batch.py`, unless that constant was changed by Jim.
  - `check --wave W`: exit 0 when every ticket of the wave is collected (including its retry) and every request has a result or a line in a `failed` file. Print the counts. Read only; no key needed.
  - `status`: one line for each ticket. No key needed.
  - `failed-share --wave W (--write FILE | --max X --record FILE)`: the share of requests of the wave that ended in a `failed` file. `--write` appends `failed-share: <value>` to FILE. `--max` exits 1 if the share is over X, unless FILE has a line `failed-accepted: <reason>`.
  - Never write a key, a header or a full response envelope. Refuse to run `run` when stdin is not a terminal and `BATCH_SUBMITTER_UNATTENDED=1` is not set (so that an agent cannot start it by accident from a step).
- `tools/test_batch_submitter.py`: injected HTTP for both vendors. Over the wave cap; over the vendor cap; changed request file; retry once then fail; two runs and the lock; `check` before and after collection.
- Write the timer example (cron line and a systemd user timer) in the tool docstring, with placeholders for paths.

## Do not change

- Files outside `touches`. The `gate`. `tools/batch.py` and `tools/batch_openai.py` (use them).

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
