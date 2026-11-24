# S5-fam-apl-weird batch report: src/apl-weird

Iteration 453. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/apl-weird/`)

- `timecards.apl`: 25 full-line and trailing `⍝` comments. Rule lines (`⍝ ───` with no words) and the empty `⍝` lines are kept. Code, SQL, `DEMO ONLY` and the `# committed ...` strings are untouched.
- `check.sh`: 6 comments (shebang stays), including one trailing comment. `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/apl-weird` is now `localizing`; `translation/localized-code.sha256` records 47 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/apl-weird --english ~/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-567)

- Card categories (decision 11): the `Categories` vector, printed rows, matched by `check.sh` and the README trace.
- Display strings: `DEMO ONLY`, the `# committed ...` line, SQL text, the `OK:` summary.
- Identifiers: none renamed (`identifier-map.jsonl` untouched). The README copies no comment text, so it needs no change.
