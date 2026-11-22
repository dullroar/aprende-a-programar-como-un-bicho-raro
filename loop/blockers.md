# Blockers

## P4-999 (iter 362): Phase 4 gate fails
`verify.py --release`: 21 of 75 checks fail (7 of 57 with `--no-gates`). Failing: CONTRIBUTING.md and SANDBOX-SETUP.md not equal to PO applied (I2/I4/I16); humor-register H001 (2 in register, 3 in source); test_anchors; test_breakage_pilot; test_humor_register; negative fixtures; inventory --check counts; study-guide build (164 links to English heading slugs); curriculum build (30). Fix narrowly via review-fix tasks, then reset P4-999 to todo.

Both tasks below were requeued after iteration 231. The draft guides are locally excluded. The unchanged fast verifier, scoped fast checks for both tasks, and the anchor check passed. The curriculum task now uses the supported `--files` acceptance command.

## P4-lessons-curriculum-1 (iteration 193): working-tree verification blocked

- `python3 -I tools/verify.py --fast` failed twice: `I1 TRANSLATING.md: no English source at the pinned commit (stale PO or wrong path)`. The unrelated untracked file is preserved.
- The recorded acceptance command also exits 2 because `--task` is unsupported. The documented `--fast --files lessons/plan-de-estudios/preliminares.md translation/po/lessons/curriculum/front-matter.md.po` passed; the existing PO has 1 translated entry, with no untranslated or fuzzy entries. Resolve the working-tree issue and rerun the gates before unblocking.

## P4-lessons-3 (iteration 192): working-tree verification blocked

- `python3 -I tools/verify.py --fast` failed twice: `I1 TRANSLATING.md: no English source at the pinned commit (stale PO or wrong path)`. The unrelated, untracked `TRANSLATING.md` appeared during this iteration and is preserved.
- The task-specific `python3 tools/verify.py --fast --files lessons/answers-key.md` and `python3 -I tools/anchors.py --check` passed. Segments 88 to 91 were accepted and applied; resume at 92 after the working-tree issue is resolved and the task is unblocked.

(none open; P0-002 resolved in iteration 7 by running the import as a single pipeline command)

## P0-002 (iteration 6): blocked, English import denied again
- Command: one compound Bash call, `cp .gitignore <scratchpad>/gitignore.es && git -C /home/lehmer/english-source archive 48a4429c... | tar -x -C .`
- Result: Bash permission denied ("don't ask mode"); nothing extracted; tree unchanged. Later plain Bash calls (sed, cat >>) were also denied, so only file tools could record this.
- The "fix 2" allowlist widening (tar, rsync, cp, rm, cd) is evidently not effective in this session's permissions. Check the driver's allowed-tools string against what the agent actually runs.
- Per SIGNS.md, no variants were tried.
- Note: the English tree has its own `.gitignore`; the import must merge it with ours (driver-owned entries: loop/logs/, loop/.lock, loop/.iteration, translation/work/, __pycache__/, *.pyc, .venv/, loop/driver.out, loop/ledger/, loop/STOP).
- To unblock: allow `Bash(tar:*)`, `Bash(git archive:*)`, `Bash(cp:*)`, or run by hand: `git -C /home/lehmer/english-source archive 48a4429c0a22b2aac628b256a50c07d1816bcb80 | tar -x -C .`, restore our .gitignore entries, then set P0-002 to `todo`.

Iterations 27 to 30 stalled on P2-004 (stall breaker at 30; usage-limit replies were the likely cause, fixed in loop fix 4). Their uncommitted work was complete enough to finish in iteration 31.

## P3B-007 (iteration 82): blocked, English test tooling still hard-codes renamed paths (RESOLVED iter 85: P3B-006b done, gate passed)
- Evidence: `python3 -I tools/verify.py --release` (second run, after the BOOK_LANG=es fix). Failing gates caused by paths: test_repo_links (`lessons/study-guides/metadata.yaml`), test_pdf_lint (`lessons/front-matter.md`), test_cs, test_study_guides, test_editorial, test_curriculum (`lessons/goals.md`, `docs/curriculum.md`, ...). Full write-up and the passed checks: translation/reviews/p3b-gate.md.
- Already fixed here: gates now run with BOOK_LANG=es (baseline.gate_env, verify.run_release, test in test_verify).
- Not fixed: the test files and lessons/book/*.py literals (about ten files, wider than one retry). tools/tooling_paths.py misses them and must be widened.
- To unblock: add a build-tool task (suggested P3B-006b, size L, dep P3B-006, and make P3B-007 depend on it) that routes those literals through the catalog `paths:` block with a tooling_paths negative case, then set P3B-007 to `todo`. Remaining gate failures after that are only the untranslated-content ones listed in the report, which the gate may document as expected.

## P4-src-14 (iteration 121): staging blocked in Codex CLI (resolved on the host)

- `git add -- translation/po/src/tar-gnu-weird/README.md.po translation/po/src/tar-gnu/README.md.po` failed twice with `Unable to create .../.git/index.lock: Read-only file system`. The Codex CLI left the working files ready to commit. Host-side verification and staging completed the task.
- Targeted and full fast verification passed. See `translation/work/121-target-final.log` and `translation/work/121-fast.log` for output. Both Mermaid figures passed the print check using the renderer cache after initial Chromium launch failures.

## P4-lessons-languages-3 (iteration 243): invalid acceptance command

- The configured `python3 tools/verify.py --fast --task P4-lessons-languages-3` exited 2 twice and printed the verifier usage: `--task` is unsupported. The usage is reproducible with that command; `python3 tools/verify.py --help` describes supported options.
- Corrected the task's acceptance command to `python3 tools/verify.py --fast --files lessons/languages/forth.md lessons/languages/haskell.md lessons/languages/javascript.md`; it passed, as did the working-tree fast verifier. The task remains blocked under the two-failure rule. Unblock by setting it to `todo` and resume Forth at position 25.

## P4-lessons-languages-5 (iteration 273): invalid acceptance command

- `python3 tools/verify.py --fast --task P4-lessons-languages-5` exited 2 twice and printed usage because `--task` is unsupported; rerun that command for the failure output.
- Corrected the task gate to `python3 tools/verify.py --fast --files lessons/languages/regex.md lessons/languages/tar.md lessons/languages/tcl.md`; it passed, as did the working-tree fast verifier. The task remains blocked under the two-failure rule. Unblock by setting it to `todo` and resume regex at position 5.

Both language batches were requeued after iteration 274. Their corrected scoped checks, the working-tree fast check, and the anchor check passed before restart.
