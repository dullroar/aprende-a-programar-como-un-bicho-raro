# loop/STATE.md (keep to 60 lines; refreshed by every iteration)

- **Edition:** v4-es.0-rc1 (working)    **English SHA:** 48a4429c0a22b2aac628b256a50c07d1816bcb80
- **Iteration:** 46    **Stage:** 2    **Last result:** P2-019 done (tools/release_report.py: commands, exit codes, hash manifest result, PO coverage, reviewer model IDs, verdict; 32 tests)
- **Tasks:** todo 101 (24 seed + 77 generated) | doing 0 | done 37 | blocked 0 | skipped 0
- **Next task:** run `python3 tools/next_task.py` (PO files live at translation/po/<path>.po, written by tools/apply.py --init)
- **Budget:** spent $0.00 of $100; iterations 0 of 300
- **Translate progress:** segments accepted 0 / total 8827 (7394 prose + 1433 Mermaid labels) ; files done 0 / ?
- **Last audit:** none    **Next audit due after:** 8 translate tasks
- **Gates:** P0 passed (iter 17)  P1 passed (iter 23)  P2 -  P3 -  P4 -  P5 -  P6 -  P7A -
- **Open provisional decisions:** 4 (acronym BICHO; glossary choices; house style N=28; schema/segment-id formats)    **Blockers:** 0    **Source issues:** 0

## Traps to remember (details live in SIGNS.md)

- Never import with `tar --exclude=.gitignore`: it drops nested .gitignore files (fixed in iter 8).
- translation/work/ is git-ignored: regenerate inventory.json with `python3 tools/inventory.py` before reading it.
- lock_code: .bat files check out as CRLF (.gitattributes); the lock accepts CRLF->LF only where git reports eol=crlf. In a fresh clone run `python3 tools/lock_code.py --install-hook`.

## If you are a new agent picking this up

1. Read `loop/HANDOFF.md` if present, then `loop/SIGNS.md`.
2. Run `loop/ralph.sh`. It restarts the loop with a fresh context each iteration.
3. Do not edit `loop/queue/*.jsonl` by hand except to unblock a task (set `status` to `todo` and note why).
