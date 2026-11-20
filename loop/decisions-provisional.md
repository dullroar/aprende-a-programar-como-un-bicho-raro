# Provisional decisions (reviewed by Jim at the end)

- 2026-11-19 bootstrap: acronym default BICHO (runner-up TORCE); es-419; tu; straight quotes; English LICENSE authoritative. Model: sonnet alias for all roles, no cross-vendor keys (Jury carries independence).
- 2026-11-19 bootstrap: English source cloned to /home/lehmer/english-source (not ../english-source) so the user's working clone is never touched.
- 2026-11-19 bootstrap: kit AGENT_CMD changed: Claude Code 2.1.319 has no --max-turns; per-iteration cap is --max-budget-usd 6.
- 2026-11-19 loop fix: agent denied access to /home/lehmer/english-source (outside cwd). Driver now passes --add-dir <english_clone_path>. Driver-owned files (driver.out, ledger/, STOP) are git-ignored so the tree is not dirty between iterations; the ledger is therefore not committed (END-REVIEW reads it from disk).
