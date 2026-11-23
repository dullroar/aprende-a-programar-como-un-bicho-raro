# S5-fam-regex-perl batch report: src/regex-perl

Iteration 468. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/regex-perl/`)

- `timecards.pl`: 3 comment lines (shebang stays). The one-statement match is code and stays untouched.
- `check.sh`: 8 comment lines (shebang stays). `check.sh` strips comment lines before its static scans, so the Spanish text cannot trip the loop-keyword check. `Dockerfile`: 2 comment lines.
- `translation/localization-scope.yaml`: `src/regex-perl` is now `localizing`; `translation/localized-code.sha256` records 79 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/regex-perl --english /home/lehmer/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-580)

- Card categories (decision 11): they sit in the tape and the pattern, and `check.sh` matches the printed rows.
- Display strings: `DEMO ONLY`, the `# committed ...` and `# the match now returns false, on purpose` lines (matched by `check.sh`), SQL text.
- Identifiers: none renamed (`identifier-map.jsonl` untouched). The README copies no comment text, so it needs no change.
