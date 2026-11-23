# S5-fam-regex-pcre2grep batch report: src/regex-pcre2grep

Iteration 467. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/regex-pcre2grep/`)

- `timecards.sh`: 4 comment lines (shebang and the empty `#` line stay). The pattern, callouts and SQL are code and stay untouched.
- `check.sh`: 11 comment lines (shebang stays). `check.sh` strips comment lines before its static scans, so the Spanish text cannot trip the loop-keyword or program allow-list checks. `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/regex-pcre2grep` is now `localizing`; `translation/localized-code.sha256` records 76 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/regex-pcre2grep --english /home/lehmer/english-source`: PASS, no findings (the English baseline passed too).
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-579)

- Card categories (decision 11): they sit inside the one-line tape and the pattern, and `check.sh` matches the printed rows.
- Display strings: `DEMO ONLY`, the `# committed ...` and `# the match now returns false, on purpose` lines (matched by `check.sh`), SQL text and the `OK:` summary.
- Identifiers: none renamed (`identifier-map.jsonl` untouched). The README copies no comment text, so it needs no change.
