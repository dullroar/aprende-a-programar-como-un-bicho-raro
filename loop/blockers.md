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
