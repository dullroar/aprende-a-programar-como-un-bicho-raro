# loop/STATE.md (keep to 60 lines; refreshed by every iteration)

- **Edition:** v4-es.0-rc1 (working)    **English SHA:** 48a4429c0a22b2aac628b256a50c07d1816bcb80
- **Iteration:** 121    **Stage:** 4 (bulk translation)    **Last result:** iter 121 P4-src-14 done (GNU tar READMEs, Codex CLI drafts and host-side Git commit).
- **Tasks:** todo 75 | doing 0 | done 91 | blocked 0 | skipped 0 (recount with the queue files)
- **Next task:** P4-src-15 (Tcl and XAML READMEs), then P4-chk-1 (entry README editorial checkpoint).
- **Budget:** driver-reported $89.4099 of $100 through the Claude run, with Codex session cost unavailable
- **Translate progress:** segments accepted 2790 / total 8827 (7394 prose + 1433 Mermaid labels) ; files done 43 / 212 (src/tar-gnu and src/tar-gnu-weird READMEs, src/regex-perl and src/regex-sed READMEs, src/regex-dotnet, src/regex-pcre2, src/regex-pcre2grep READMEs, src/lisp, src/m4, src/make-gnu READMEs, src/javascript, src/lisp-weird READMEs, src/javascript-weird README, src/haskell-weird, src/haskell, src/javascript-events READMEs, src/find-posix, src/forth-weird READMEs, src/ex-weird, src/find-gnu, src/cobol-weird, src/cobol, src/ed-weird READMEs, src/awk-weird, src/awk, src/cmake READMEs, src/RustChallenge1, src/apl-weird, src/apl READMEs, curriculum and study-guide title pages, src/GoChallenge1, JavaChallenge1, KotlinChallenge1, LinqChallenge1, LinqChallenge2, ModernChallenge1, PythonChallenge1 READMEs, src/forth/README.md, lessons/cs-source/concepts/recursion.md, lessons/study-guides/languages/forth.md, docs/curriculum.md, lessons/study-guides/languages/apl.md)
- **Last audit:** P4-audit-1 (iter 112, translation/reviews/p4-audit-1.md)    **Next audit due after:** P4-lessons-cs-source-1
- **Gates:** P0 passed (iter 17)  P1 passed (iter 23)  P2 passed (iter 47)  P3 passed (iter 58)  P3B passed (iter 85)  P3C passed (iter 105)  P4 -  P5 -  P6 -  P7A -
- **Open provisional decisions:** 5 (acronym BICHO; glossary choices; house style N=29 calibrated; schema/segment-id formats; same-tier reviewer kept after recall test)    **Blockers:** 0    **Source issues:** 16 (translation/source-issues.md)

## Traps to remember (details live in SIGNS.md)

- Never import with `tar --exclude=.gitignore`: it drops nested .gitignore files (fixed in iter 8).
- translation/work/ is git-ignored: regenerate inventory.json with `python3 tools/inventory.py` before reading it.
- lock_code: .bat files check out as CRLF (.gitattributes); the lock accepts CRLF->LF only where git reports eol=crlf. In a fresh clone run `python3 tools/lock_code.py --install-hook`.

## If you are a new agent picking this up

1. Read `loop/HANDOFF.md` if present, then `loop/SIGNS.md`.
2. Run `loop/ralph.sh`. It restarts the loop with a fresh context each iteration.
3. Do not edit `loop/queue/*.jsonl` by hand except to unblock a task (set `status` to `todo` and note why).
