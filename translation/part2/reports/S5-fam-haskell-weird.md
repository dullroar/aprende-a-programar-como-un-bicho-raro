# S5-fam-haskell-weird batch report: src/haskell-weird

Iteration 462. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/haskell-weird/`)

- `timecards.hs`: 38 comment lines (the `-- ` markers stay, so the `grep -Ev '^\s*--'` filter in `check.sh` still strips them). The `Run:` line and empty `--` lines are kept. `DEMO ONLY` stays in the header comment. Code and strings are untouched.
- `check.sh`: 6 comment lines (shebang stays). `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/haskell-weird` is now `localizing`; `translation/localized-code.sha256` records 64 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/haskell-weird --english /home/lehmer/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-575)

- Card categories (decision 11): printed rows matched by `check.sh` and the README trace.
- Display strings: `DEMO ONLY`, the `# committed ...` and stunt-note lines, SQL text, the `OK:` summary.
- Identifiers: none renamed (`identifier-map.jsonl` untouched). The README copies no comment text, so it needs no change.
