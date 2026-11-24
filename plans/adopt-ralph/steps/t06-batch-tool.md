---
id: t06-batch-tool
status: done
depends_on: [t02-layout]
touches:
  - tools/batch.py
  - tools/test_batch.py
  - tools/fixtures/batch/**
  - translation/prompts/batch-*.md
  - plans/adopt-ralph/steps/t06-batch-tool.md
lane: none
gate: python3 -m unittest tools/test_batch.py && python3 scripts/build_indexes.py --check && python3 -I tools/verify.py --fast && git diff --check
claimed_by: claude cli-default
claimed_at: "2026-11-24T02:32:58Z"
evidence: gate passed 2026-11-24 (driver-verified)
---

# Write `tools/batch.py` for the Message Batches API

The operator submits bulk drafts and reviews through the Message Batches API. The tool never runs in CI and never runs in an agent step. Tests use recorded fixtures only, with no network. Use the standard library only (`urllib`), no SDK.

## Change

- Reuse `tools/translate.py`: `--export-pending` writes the masked pending segments. `--drafts ... --draft-model ... --task-id ...` imports drafts with all checks. The batch tool uses these two paths. It does not copy their logic.
- `build`: read `--export-pending` JSONL or reviewer input JSONL. Write a request file. `custom_id` is the segment ID plus the first 12 hex digits of the source hash. The stable style guide and glossary go in one `system` block with `cache_control` `{"type": "ephemeral"}`. The model ID is a required argument. Prompts that the tool needs go to `translation/prompts/batch-*.md`.
- `submit`: needs `ANTHROPIC_API_KEY` in the environment and `--max-usd`. It refuses without both. It prints the batch ID. It reads the running total from the cost records and refuses a submission whose cap would take the total over USD 100 (program cap, owner decision of 2026-11-23). Each submission records its own cap and the running total.
- `status`; `collect` (write a drafts JSONL that `translate.py --drafts` accepts, and a cost record); `reconcile` (reject results whose `custom_id` does not match a current pending segment or whose source hash changed; never apply a result twice). `--dry-run` writes nothing.
- Secrets. The tool reads the key only from `ANTHROPIC_API_KEY`. It never writes the key, the request headers or a full response envelope to a file or a log. A test builds a synthetic key at run time and proves that it does not appear in any file that `build`, `submit --dry-run` or `collect` writes.
- Fixtures in `tools/fixtures/batch/` (recorded responses, JSONL): success, partial errors (`errored`), expired requests, a duplicate result and a stale source hash. A batch result line has `custom_id` and `result.type` (`succeeded`, `errored`, `canceled` or `expired`). Test each case. A case that the tool must refuse is a known-bad fixture. Write a fixture that holds a secret at run time. Never store it.
- A test that submits for real is not allowed. Inject the HTTP function in tests.

## Do not change

- Files outside `touches`. The `gate` command. `tools/translate.py` (use it, do not edit it).
- Never call the network. Never run `submit` without `--dry-run`.

## Already done by earlier steps

- t02-layout: the registration (`tools/` and `translation/` are owned) and `build_indexes.py`.

## Done when

- The gate passes. Run the full tool test suite before you commit.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

Work is written: `tools/batch.py`, `tools/test_batch.py`, `tools/fixtures/batch/*` and `translation/prompts/batch-translate.md`.

Gate result in this session (2026-11-24):

- `python3 -m unittest tools/test_batch.py`: pass (27 tests).
- `python3 scripts/build_indexes.py --check`: pass.
- `git diff --check`: pass.
- `python3 -I tools/verify.py --fast`: 8 of 9 checks pass. The `prompts` check fails with `ModuleNotFoundError: No module named 'referencing'`. The module exists only in the repository venv. The `-I` flag hides it from this shell. The error comes before any prompt is read, so it is not caused by this step. I could not use the venv interpreter (Bash denied it).
- Full tool suite: 15 failures and errors in `test_breakage_pilot`, `test_anchors`, `test_pathcheck`, `test_pathmap` and `test_negative`. None of them touch the files of this step. Compare them with the t01 baseline.

What remains: run the gate with an interpreter that has `referencing`, then set `status: done` and fill `evidence`.

Design notes:

- `custom_id` = segment ID + "-" + 12 hex of the sha256 of `english_masked`.
- Cost file and applied ledger must live outside the repository (`$RALPH_WORK`). `submit` refuses a cost file inside the repository.
- `collect` prices need `--price-in` and `--price-out` (USD per million tokens). All input tokens count at the input price, so the cost is an upper bound.
