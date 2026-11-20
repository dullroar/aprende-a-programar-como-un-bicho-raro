# loop/STATE.md (keep to 60 lines; refreshed by every iteration)

- **Edition:** v4-es.0-rc1 (working)    **English SHA:** 48a4429c0a22b2aac628b256a50c07d1816bcb80
- **Iteration:** 13    **Stage:** 0    **Last result:** P0-008 done (translation/phase-letters.json; BICHO collides with exercise prefixes B and C)
- **Tasks:** todo 53 | doing 0 | done 8 | blocked 0 | skipped 0
- **Next task:** tools/next_task.py not built yet (P0-011); take the first `todo` in loop/queue/seed.jsonl whose deps are done (P0-009)
- **Budget:** spent $0.00 of $100; iterations 0 of 300
- **Translate progress:** segments accepted 0 / total ? ; files done 0 / ?
- **Last audit:** none    **Next audit due after:** 8 translate tasks
- **Gates:** P0 -  P1 -  P2 -  P3 -  P4 -  P5 -  P6 -  P7A -
- **Open provisional decisions:** 0    **Blockers:** 0    **Source issues:** 0

## Traps to remember (details live in SIGNS.md)

- Never import with `tar --exclude=.gitignore`: it drops nested .gitignore files (fixed in iter 8).
- translation/work/ is git-ignored: regenerate inventory.json with `python3 tools/inventory.py` before reading it.
- lock_code: .bat files check out as CRLF (.gitattributes); the lock accepts CRLF->LF only where git reports eol=crlf. In a fresh clone run `python3 tools/lock_code.py --install-hook`.

## If you are a new agent picking this up

1. Read `loop/HANDOFF.md` if present, then `loop/SIGNS.md`.
2. Run `loop/ralph.sh`. It restarts the loop with a fresh context each iteration.
3. Do not edit `loop/queue/*.jsonl` by hand except to unblock a task (set `status` to `todo` and note why).
