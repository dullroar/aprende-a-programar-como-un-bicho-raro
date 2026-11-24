---
id: t08-verify
status: in_progress
depends_on: [t05-routing-map, t06-batch-tool, t07-archive-loop]
touches:
  - plans/adopt-ralph/steps/t08-verify.md
lane: none
tier: light
gate: python3 -m unittest discover -s tools -p 'test_*.py' 2>&1 | python3 plans/adopt-ralph/no_new_failures.py plans/adopt-ralph/tools-test-baseline.txt && python3 scripts/build_indexes.py --check && python3 scripts/check_context.py && python3 tools/check_routing_map.py && python3 scripts/secret_guard.py --tracked && python3 -I tools/verify.py --fast && grep -Eq '^verify-fast-same: (yes|no)' plans/adopt-ralph/steps/t08-verify.md && grep -Eq '^tool-tests-same: (yes|no)' plans/adopt-ralph/steps/t08-verify.md && grep -Eq '^queue-counts-same: (yes|no)' plans/adopt-ralph/steps/t08-verify.md && grep -Eq '^secret-history-count: [0-9]+' plans/adopt-ralph/steps/t08-verify.md && git diff --check
claimed_by: ""
claimed_at: ""
evidence: ""
---

# Prove that the new layout and the old results agree

## Change

- Run the commands of the baseline again (see "Baseline" in the step file `t01-baseline.md`): `verify.py --fast`, `verify.py --release --no-gates`, the tool tests, `next_task.py --counts`, the tracked file count and `git status`. Compare each result with the baseline.
- Write the comparison in "Comparison" below, one line each, at the start of the line: `verify-fast-same: yes|no`, `tool-tests-same: yes|no` (the count may be higher only by the tests that this plan added: list them), `queue-counts-same: yes|no`, and `file-count-delta: N (<list of added paths>)`. A `no` needs a reason on the same line. A `no` without a reason that is one of this plan's added files means failure: write "Resume notes".
- Runner view. Make a scratch clone of this branch outside the repository (use `RALPH_WORK`, not `/tmp`). Run the runner's status view there: `ralph-looper --repo <scratch clone> --plan adopt-ralph --status` (the runner is in the `ralph-looper` checkout under `REPOS_ROOT`; read its `--help` first). Write `runner-status: ok` if it prints the step table without an error, and the first line of its output.
- Run `python3 scripts/secret_guard.py --history`. Write `secret-history-count: N`. Any count above 0 is blocking: set the status `blocked` and say so.
- List each exception in `.secret-guard-allow` that this plan added (it must be none), under "Exceptions".

## Do not change

- Files outside `touches`. The `gate` command. Do not push. Do not delete the scratch clone's source branch.

## Already done by earlier steps

- t01-baseline: the numbers. t00 to t07: all the work.

## Done when

- The gate passes. The comparison is complete.

## Comparison

verify-fast-same: yes (exit 0, "verify --fast: OK (1 checks)", as in the baseline)
verify-release-no-gates: exit 1, same crash as the baseline (`polib` missing in `tools/apply.py`)
tool-tests-same: yes (1477 tests, failures=10, errors=5, skipped=1. The baseline had 1441 tests with the same failures, errors and skips. The 36 extra tests come from `tools/test_batch.py`, `tools/test_check_routing_map.py` and `tools/test_controls.py`, added by this plan)
queue-counts-same: yes (todo 0 | doing 0 | done 322 | blocked 0 | skipped 0)
file-count-delta: 47 (1283 tracked now, 1236 in the baseline. Added: AGENTS.md, CLAUDE.md, GUIA-DEL-REPO.md, controls.toml, 15 files in memory/, memory/AGENTS.md, plans/AGENTS.md, plans/adopt-ralph/no_new_failures.py, plans/adopt-ralph/tools-test-baseline.txt, 3 files in plans/for-each-plan/, scripts/AGENTS.md, scripts/build_indexes.py, scripts/check_context.py, scripts/controls-requirements.txt, scripts/ctx_common.py, scripts/verify_fast.sh, tools/batch.py, tools/check_routing_map.py, 6 fixtures in tools/fixtures/batch/, tools/test_batch.py, tools/test_check_routing_map.py, tools/test_controls.py, translation/controls-adoption.md, translation/prompts/batch-translate.md, translation/routing.md)
secret-history-count: 0 (108 binary blobs unscanned; this is only a note)

## Exceptions

(none)

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Operator change (2026-11-23)

Agent sessions cannot write outside the worktree or run `mktemp`. Make the scratch clone inside the worktree instead: `git clone -q . .probe/copy`. The operator excluded `/.probe/` in this clone's `.git/info/exclude`, so it is never tracked and the scope check ignores it. Run the runner view in that copy. Delete it with `rm -rf .probe` before you run the gate.

## Operator change (2026-11-23, runner view)

The runner view is dropped. The agent session cannot reach the runner checkout, and `ralph-looper --status` can create branches and worktrees (see the runner's `docs/fanout.md`). Its purpose was to show that `plans/` is valid for Ralph. The gate already runs `python3 scripts/check_context.py`, whose library checks `plans.schema` and `plans.graph` apply the same rules as the runner's picker. The parent plan's `fanout.py verify` checks the finished steps with Git plumbing. Do not write `runner-status`.

## Resume notes

Status: partial. The comparison above is complete. The runner view is NOT done.

- The scratch clone worked (`git clone -q . .probe/copy`). I removed `.probe` afterwards.
- Bash denied every call to `/home/lehmer/repos/ralph-looper/ralph-looper` (`--help` and `--repo .probe/copy --plan adopt-ralph --status`). So I could not write `runner-status: ok`. I did not guess it.
- To finish: run `ralph-looper --repo <scratch clone in .probe/copy> --plan adopt-ralph --status` (allow that command for the agent, or run it as the operator). If it prints the step table without an error, add the line `runner-status: ok (<first output line>)`. The line must start with `runner-status: ok`. Then remove `.probe`, run the gate, set `status: done` and fill `evidence`.
- Second attempt: the scratch clone worked again. The call to the runner (`ralph-looper --repo .probe/copy --plan adopt-ralph --status`, path from `REPOS_ROOT`) was denied again ("don't ask mode"). I did not work around the denial. I removed `.probe`. The operator must allow this one command or run it by hand.
- No exceptions were added to `.secret-guard-allow` by this plan (not changed in the diff since the baseline).
