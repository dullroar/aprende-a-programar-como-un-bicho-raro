---
gist: "Read me when: you edit a queue task, pick the next task, test the driver, or you need the project virtualenv and dependency rules of the old loop."
---

# Old loop: queue, driver and environment

The old loop is archived. Do not run or resume `loop/ralph.sh`. These facts matter only when you read or test its tools.

## Queue

- `python3 tools/next_task.py` picks a task. Exit 0 = TASK, 1 = NONE-BLOCKED, 2 = NONE-WAITING, 3 = NONE-COMPLETE.
- Change a seed-queue status with `python3 tools/seedtask.py <id> <status> [notes]`. `seedtask.py ID doing` takes the iteration number (an integer) as its last argument, not free text.
- After `seedtask.py ID done`, run `git diff --stat`. Check that the changed queue line is the task's own ID (once, S5-fam-regex-perl was marked done instead of javascript-weird).
- Write queue records with the Write tool (one JSON per line). Validate with `python3 tools/next_task.py --check`.
- Do not edit `loop/queue/*.jsonl` by hand, except to unblock a task (set `status` to `todo` and note why).
- Append to `loop/*.md` with Edit, anchored on the last line.

## Driver and environment

- Never start the real `loop/ralph.sh` from inside an iteration (lock, nested agent). Test the driver with `python3 -I tools/resume_test.py`. It runs a copy in a scratch repo under `translation/work/` with scripted agents.
- Use the project virtualenv (`.venv`). Install into `.venv` only, never globally. Record each new dependency in `requirements-es.txt`. In this plan, an agent step never installs anything.
- Tools in `tools/` read files with `with open`. Run tool tests as `python3 -I tools/test_<name>.py`.
- Build masking regexes with named groups (never numbered backreferences). Unmask in one non-recursive pass. Run `python3 -I tools/test_mask.py` after you touch `tools/mask.py`.
- After you touch `tools/segment.py`, run `python3 -I tools/test_segment.py` and `python3 -I tools/segment.py --t0`.
- After you touch `tools/apply.py` or the PO layout, run `python3 -I tools/test_apply.py` and `python3 -I tools/apply.py --identity`. PO entries are keyed by msgctxt = segment id. Macros must expand in msgstr before unmask.
- After you touch `translation/prompts/` or `translation/schemas/`, run `python3 -I tools/prompt_check.py`. Update the prompt examples and the sample rows together.
- After you touch `tools/verify.py`, run `python3 -I tools/test_verify.py`.
