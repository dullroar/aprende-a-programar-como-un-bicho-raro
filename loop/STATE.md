# loop/STATE.md (keep to 60 lines; refreshed by every iteration)

- **Edition:** v4-es.0-rc1 (working)    **English SHA:** 48a4429c0a22b2aac628b256a50c07d1816bcb80
- **Iteration:** 18    **Stage:** 1    **Last result:** P1-001 done (glossary.es.yaml, 206 terms; tools/glossary_check.py)
- **Tasks:** todo 125 (48 seed + 77 generated) | doing 0 | done 13 | blocked 0 | skipped 0
- **Next task:** run `python3 tools/next_task.py` (P1-002 house style is next)
- **Budget:** spent $0.00 of $100; iterations 0 of 300
- **Translate progress:** segments accepted 0 / total ? ; files done 0 / ?
- **Last audit:** none    **Next audit due after:** 8 translate tasks
- **Gates:** P0 passed (iter 17)  P1 -  P2 -  P3 -  P4 -  P5 -  P6 -  P7A -
- **Open provisional decisions:** 1 (acronym BICHO; no Spanish word list on machine)    **Blockers:** 0    **Source issues:** 0

## Traps to remember (details live in SIGNS.md)

- Never import with `tar --exclude=.gitignore`: it drops nested .gitignore files (fixed in iter 8).
- translation/work/ is git-ignored: regenerate inventory.json with `python3 tools/inventory.py` before reading it.
- lock_code: .bat files check out as CRLF (.gitattributes); the lock accepts CRLF->LF only where git reports eol=crlf. In a fresh clone run `python3 tools/lock_code.py --install-hook`.

## If you are a new agent picking this up

1. Read `loop/HANDOFF.md` if present, then `loop/SIGNS.md`.
2. Run `loop/ralph.sh`. It restarts the loop with a fresh context each iteration.
3. Do not edit `loop/queue/*.jsonl` by hand except to unblock a task (set `status` to `todo` and note why).
