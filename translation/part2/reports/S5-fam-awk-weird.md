# S5-fam-awk-weird batch report: src/awk-weird

Iteration 461. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/awk-weird/`)

- `timecards.awk`: 28 comment lines. The shebang, the empty `#` lines, the `Run:` lines and the header one-liner (lines 17 and 18, which `check.sh` runs) are kept. Code, SQL, `DEMO ONLY` and the `# committed ...` strings are untouched.
- `check.sh`: 20 comments (shebang stays), including five trailing comments. `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/awk-weird` is now `localizing`; `translation/localized-code.sha256` records 61 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/awk-weird --english /home/lehmer/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-574)

- Card categories (decision 11): the `C` array, printed rows, matched by `check.sh` and the README trace.
- Display strings: `DEMO ONLY`, the `# committed ...` line, SQL text, the `OK:` summary.
- Identifiers: none renamed (`identifier-map.jsonl` untouched). The README copies no comment text, so it needs no change.
