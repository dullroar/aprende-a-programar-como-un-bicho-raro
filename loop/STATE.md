# loop/STATE.md (keep to 60 lines; refreshed by every iteration)

- **Edition:** v4-es.0-rc1 (working)    **English SHA:** 48a4429c0a22b2aac628b256a50c07d1816bcb80
- **Iteration:** 299    **Stage:** 4 (bulk translation)    **Last result:** P4-lessons-languages-3 partial (JavaScript positions 0 to 69 complete; resume at 70).
- **Tasks:** todo 72 | doing 0 | done 142 | blocked 0 | skipped 0 (recount with the queue files)
- **Next task:** run python3 tools/next_task.py (see loop/queue/generated/translate.jsonl).
- **Budget:** driver-reported $112.6405 of $150 through iteration 274, with Codex session cost unavailable
- **Translate progress:** at least 7415 / total 8827 segments accepted (7394 prose + 1433 Mermaid labels); at least 189 / 212 files done. Answer key, Forth and Haskell complete with no pending segments. Counts based on the previous snapshot plus this task.
- **Last audit:** P4-audit-6 (iter 176, translation/reviews/p4-audit-6.md)    **Next audit due:** the next P4-audit task in the queue
- **Gates:** P0 passed (iter 17)  P1 passed (iter 23)  P2 passed (iter 47)  P3 passed (iter 58)  P3B passed (iter 85)  P3C passed (iter 105)  P4 -  P5 -  P6 -  P7A -
- **Open provisional decisions:** 6 (includes corrected task acceptance command)    **Blockers:** 0    **Source issues:** 26 (translation/source-issues.md)

## Traps to remember (details live in SIGNS.md)

- Never import with `tar --exclude=.gitignore`: it drops nested .gitignore files (fixed in iter 8).
- translation/work/ is git-ignored: regenerate inventory.json with `python3 tools/inventory.py` before reading it.
- lock_code: .bat files check out as CRLF (.gitattributes); the lock accepts CRLF->LF only where git reports eol=crlf. In a fresh clone run `python3 tools/lock_code.py --install-hook`.

## If you are a new agent picking this up

1. Read `loop/HANDOFF.md` if present, then `loop/SIGNS.md`.
2. Run `loop/ralph.sh`. It restarts the loop with a fresh context each iteration.
3. Do not edit `loop/queue/*.jsonl` by hand except to unblock a task (set `status` to `todo` and note why).
