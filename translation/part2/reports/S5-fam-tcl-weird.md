# S5-fam-tcl-weird batch report: src/tcl-weird

Iteration 469. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/tcl-weird/`)

- `timecards.tcl`: 27 Tcl comment lines (shebang stays). The `--` SQL comments inside the Tcl string are not comment spans and stay English.
- `check.sh`: 14 comment lines (shebang stays). Its static scans strip comment lines first, and the Spanish text avoids the words the scans forbid. `Dockerfile`: 4 comment lines.
- `translation/localization-scope.yaml`: `src/tcl-weird` is now `localizing`; `translation/localized-code.sha256` records 82 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/tcl-weird --english ~/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-581)

- Card categories (decision 11): they sit in the `category` proc text and `check.sh` matches the printed rows.
- Display strings: `DEMO ONLY`, `# committed ...`, the `# every proc that ran...` lines (matched by `check.sh`), SQL text.
- Identifiers: none renamed (`identifier-map.jsonl` untouched). The README copies no comment text, so it needs no change.
