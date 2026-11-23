# loop/STATE.md (keep to 60 lines; refreshed by every iteration)

- **Edition:** v4-es.0-rc1 (working)    **English SHA:** 48a4429c0a22b2aac628b256a50c07d1816bcb80
- **Iteration:** 402    **Stage:** 6    **Last result:** S1-004 done (batch B rows and pages for 8 languages incl. new m4; all NOT TESTED, toolchains absent or denied). Before: S1-003 done (batch A rows exist; 7 of 9 languages NOT TESTED, toolchains denied). Before: S1-002 done (tools/token_registry.py, translation/protected-tokens/ for python and javascript; 21 languages not-extracted). Before: S1-001 done (translation/part2/policy.md, translation/localization-scope.yaml, 53 families all frozen). Before: S0-004 done (translation/part2/s0-gate.md; 230/230 classified once; self-test still NOT RUN). Before: S0-003 done (runtime-matrix.md static; self-test and versions NOT TESTED, docker denied in dontAsk). Before: S0-002 done (tools/code_inventory.py, translation/part2/code-inventory.jsonl for all 230 locked paths; not pushed).
- **Tasks:** todo 45 | doing 0 | done 169 | blocked 1 | skipped 0 (recount with the queue files)
- **Next task:** S1-005 (docker self-test still owed to a Docker-capable session).
- **Budget:** driver-reported $112.6405 of $150 through iteration 274, with Codex session cost unavailable
- **Translate progress:** at least 7751 / total 8827 segments accepted; at least 196 / 212 files done. P4-lessons-languages-5 complete. Counts based on the previous snapshot plus this task.
- **Last audit:** P4-audit-9 (iter 361, translation/reviews/p4-audit-9.md)    **Next audit due:** the next P4-audit task in the queue
- **Gates:** P0 passed (iter 17)  P1 passed (iter 23)  P2 passed (iter 47)  P3 passed (iter 58)  P3B passed (iter 85)  P3C passed (iter 105)  P4 passed (iter 376)  P5 passed (iter 387)  P6 -  P7A -
- **Open provisional decisions:** 7 (includes corrected task acceptance command and the iter 387 "Alive"/"Vivo" question for Jim)    **Blockers:** 0 (P5-001 unblocked)    **Source issues:** 26 (translation/source-issues.md)

## Traps to remember (details live in SIGNS.md)

- Never import with `tar --exclude=.gitignore`: it drops nested .gitignore files (fixed in iter 8).
- translation/work/ is git-ignored: regenerate inventory.json with `python3 tools/inventory.py` before reading it.
- lock_code: .bat files check out as CRLF (.gitattributes); the lock accepts CRLF->LF only where git reports eol=crlf. In a fresh clone run `python3 tools/lock_code.py --install-hook`.

## If you are a new agent picking this up

1. Read `loop/HANDOFF.md` if present, then `loop/SIGNS.md`.
2. Run `loop/ralph.sh`. It restarts the loop with a fresh context each iteration.
3. Do not edit `loop/queue/*.jsonl` by hand except to unblock a task (set `status` to `todo` and note why).
