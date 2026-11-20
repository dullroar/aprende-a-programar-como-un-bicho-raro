# Blockers

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
