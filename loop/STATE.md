# loop/STATE.md (keep to 60 lines; refreshed by every iteration)

- **Edition:** v4-es.0-rc1 (working)    **English SHA:** 48a4429c0a22b2aac628b256a50c07d1816bcb80
- **Iteration:** 133    **Stage:** 4 (bulk translation)    **Last result:** iter 133 P4-lessons-cs-source-concepts-4 done (18 concept pages verified).
- **Tasks:** todo 65 | doing 0 | done 103 | blocked 0 | skipped 0 (recount with the queue files)
- **Next task:** P4-lessons-cs-source-concepts-5 (Translate lessons/cs-source/concepts/state.md .. lessons/cs-source/concepts/weird-machine.md (12 files), about 2133 words).
- **Budget:** driver-reported $89.4099 of $100 through the Claude run, with Codex session cost unavailable
- **Translate progress:** segments accepted 4118 / total 8827 (7394 prose + 1433 Mermaid labels) ; files done 131 / 212 (nonempty, non-fuzzy PO entries and complete files). Latest: lessons/cs-source/concepts/state-encoding.md.
- **Last audit:** P4-audit-2 (iter 125, translation/reviews/p4-audit-2.md)    **Next audit due:** P4-audit-3
- **Gates:** P0 passed (iter 17)  P1 passed (iter 23)  P2 passed (iter 47)  P3 passed (iter 58)  P3B passed (iter 85)  P3C passed (iter 105)  P4 -  P5 -  P6 -  P7A -
- **Open provisional decisions:** 5 (acronym BICHO; glossary choices; house style N=29 calibrated; schema/segment-id formats; same-tier reviewer kept after recall test)    **Blockers:** 0    **Source issues:** 26 (translation/source-issues.md)

## Traps to remember (details live in SIGNS.md)

- Never import with `tar --exclude=.gitignore`: it drops nested .gitignore files (fixed in iter 8).
- translation/work/ is git-ignored: regenerate inventory.json with `python3 tools/inventory.py` before reading it.
- lock_code: .bat files check out as CRLF (.gitattributes); the lock accepts CRLF->LF only where git reports eol=crlf. In a fresh clone run `python3 tools/lock_code.py --install-hook`.

## If you are a new agent picking this up

1. Read `loop/HANDOFF.md` if present, then `loop/SIGNS.md`.
2. Run `loop/ralph.sh`. It restarts the loop with a fresh context each iteration.
3. Do not edit `loop/queue/*.jsonl` by hand except to unblock a task (set `status` to `todo` and note why).
