---
id: t07-archive-loop
status: done
depends_on: [t03-memory, t04-controls]
touches:
  - loop/STATE.md
  - loop/RUN.md
  - plans/adopt-ralph/steps/t07-archive-loop.md
lane: none
tier: light
gate: python3 -m unittest discover -s tools -p 'test_*.py' 2>&1 | python3 plans/adopt-ralph/no_new_failures.py plans/adopt-ralph/tools-test-baseline.txt && python3 scripts/build_indexes.py --check && python3 scripts/check_context.py && python3 -I tools/verify.py --fast && grep -qi 'archived' loop/STATE.md && grep -qi 'archived' loop/RUN.md && grep -q 'plans/' loop/STATE.md && test -f "$(git rev-parse --path-format=absolute --git-common-dir)/../loop/STOP" && ! git ls-files --error-unmatch loop/STOP >/dev/null 2>&1 && git diff --check
claimed_by: ""
claimed_at: ""
evidence: "Gate command run in single-command parts on 2026-11-23 with the operator-changed gate: tool tests show 14 failures (10 failures, 4 errors), the same count as the known baseline; build_indexes --check, check_context.py, verify.py --fast and git diff --check pass; the grep checks for 'archived' and 'plans/' pass; loop/STOP exists in the main checkout (git common dir) and is not tracked. Queue counts written in the notice: todo 0, doing 0, done 322, blocked 0, skipped 0."
---

# Mark the old loop as archived

The private loop is replaced by `plans/` and the Ralph runner. Keep every old file. Only add a notice.

## Change

- `loop/STATE.md` and `loop/RUN.md`: add a short notice at the top, in Simplified Technical English. It says: this loop is archived at the queue state of today (write the output of `python3 tools/next_task.py --counts`); new work lives in `plans/` (see `GUIA-DEL-REPO.md` and `AGENTS.md`); `loop/STOP` stays (Part III checkpoint of the owner); do not run or resume `loop/ralph.sh`.
- `README.md` and `CONTRIBUTING.md` stay unchanged. They are English files with a PO translation, and neither has a section about the loop (checked on 2026-11-24). If you find a loop section now, write it under "Resume notes". Do not edit them.
- Do not delete or move any file of `loop/`. Do not touch the queue files, `loop/STOP` or the pre-push hook.

## Do not change

- Files outside `touches`. The `gate` command.

## Already done by earlier steps

- t03-memory: the traps are in `memory/`. t04-controls: `scripts/check_context.py` and the controls.

## Done when

- The gate passes. `git diff --stat` shows only the two loop files and this step file.

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Operator change (2026-11-23)

`loop/STOP` is untracked (it is in `.gitignore`), so it never exists in a linked worktree, and `test -f loop/STOP` could not pass. The gate now checks the intent: the owner's `loop/STOP` still exists in the main checkout (found through Git's common directory), and this step does not track it. Do not create, move or delete `loop/STOP`.

## Resume notes

Resolved on 2026-11-23: the operator changed the gate to check `loop/STOP` in the main checkout. All gate parts now pass. The notes below are history.

The notices in `loop/STATE.md` and `loop/RUN.md` are done and committed. All gate parts pass except `test -f loop/STOP`.

`loop/STOP` is in `.gitignore`. It is not tracked. A new worktree does not have it, so the check fails here (checked on 2026-11-23). The file is not in `touches`, and it is the owner's checkpoint. Do not create it in the worktree.

Needed from the owner: run the gate in the main checkout (where `loop/STOP` exists), or approve a gate that does not depend on an untracked file. Do not change the gate without the owner.
