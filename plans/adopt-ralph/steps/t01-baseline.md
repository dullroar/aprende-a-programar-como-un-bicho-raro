---
id: t01-baseline
status: done
depends_on: [t00-secret-guard]
touches:
  - plans/adopt-ralph/steps/t01-baseline.md
lane: none
tier: light
gate: grep -Eq '^verify-fast: exit [0-9]+' plans/adopt-ralph/steps/t01-baseline.md && grep -Eq '^verify-release-no-gates: exit [0-9]+' plans/adopt-ralph/steps/t01-baseline.md && grep -Eq '^tool-tests: [0-9]+ tests' plans/adopt-ralph/steps/t01-baseline.md && grep -Eq '^queue-counts: .+' plans/adopt-ralph/steps/t01-baseline.md && grep -Eq '^tracked-files: [0-9]+' plans/adopt-ralph/steps/t01-baseline.md && grep -Eq '^git-status: clean' plans/adopt-ralph/steps/t01-baseline.md && git diff --check
claimed_by: claude cli-default
claimed_at: "2026-11-24T02:15:27Z"
evidence: gate passed 2026-11-24 (driver-verified)
---

# Record the current verification results

Step `t08` must reproduce these numbers. Record them exactly.

## Change

Run each command. Write the result in the section "Baseline" below, one line each, at the start of the line, in the formats `verify-fast: exit N ...`, `verify-release-no-gates: exit N ...`, `tool-tests: N tests, <result>`, `queue-counts: <output>`, `tracked-files: N (<files that t00 added>)` and `git-status: clean`. The keys are:

- `verify-fast:` the exit code and the last summary line of `python3 -I tools/verify.py --fast`.
- `verify-release-no-gates:` the same for `python3 -I tools/verify.py --release --no-gates` (exit `3` means "passed but incomplete", which is the expected result without the gates).
- `tool-tests:` the test count and the result of `python3 -m unittest discover -s tools -p 'test_*.py'`.
- `queue-counts:` the output of `python3 tools/next_task.py --counts`.
- `tracked-files:` the output of `git ls-files | wc -l`, and the list of files that `t00` added (`git diff --name-status <first commit of this plan>^ HEAD --stat` is enough).
- `git-status:` a summary of `git status --short` (it must be clean).

If a command needs the English clone and it is missing, write that under "Resume notes" and stop.

## Do not change

- Files outside `touches`. The `gate` command.

## Already done by earlier steps

- t00-secret-guard: the guard and the registration. The tracked file count already includes its files.

## Done when

- The gate passes. Every key has a value, not a placeholder.

## Baseline

verify-fast: exit 0 (verify --fast: OK (1 checks, 0.0s))
verify-release-no-gates: exit 1 (crash: ModuleNotFoundError: No module named 'polib' in tools/apply.py; not the expected exit 3)
tool-tests: 1441 tests, FAILED (failures=10, errors=5, skipped=1)
queue-counts: todo 0 | doing 0 | done 322 | blocked 0 | skipped 0
tracked-files: 1236 (t00 added: .github/workflows/context.yml, scripts/install_hooks.sh, scripts/secret_guard.py, tools/test_registry.py, tools/test_secret_guard.py; t00 modified: tools/inventory.py, tools/lock_code.py, tools/test_lock_code.py, translation/tooling-allowlist.txt)
git-status: clean

Notes. These numbers come from the worktree environment, where `polib` and the Mermaid CLI are not installed. Causes seen in the test failures: `polib` missing, Mermaid CLI missing, and `.git` (a file in a linked worktree) listed by the path-map tests. Step t08 must run in the same kind of environment to get the same numbers.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
