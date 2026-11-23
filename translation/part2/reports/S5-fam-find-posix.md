# S5-fam-find-posix batch report: src/find-posix

Iteration 436. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/find-posix/`)

- `timecards.sh`: 6 comment lines (`DEMO ONLY` stays in the first one); the shebang is untouched.
- `check.sh`: 25 comment lines, full-line and trailing. The heredoc body of the fake mktemp is code and was not touched. `check.sh` filters comments with `grep -Ev '^\s*(#|$)'`, so Spanish comments cannot change its static checks. Comments still name the English card categories because the code prints them.
- `build-line.py`: 16 `#` comments, including trailing ones; the module docstring is a string and stays English.
- `Dockerfile`: 4 comment lines.
- `translation/localization-scope.yaml`: `src/find-posix` is now `localizing`; `translation/localized-code.sha256` records 20 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/find-posix --english /home/lehmer/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1); code lines are unchanged.

## Kept English, on purpose (EXC-553)

- Card categories (decision 11): quoted SQL values in the find line, `check.sh` and the README trace.
- Display strings: `DEMO ONLY`, the `# committed ...` summary (parsed by `check.sh`), SQL text, the build-line docstring.
- Identifiers: none renamed (`identifier-map.jsonl` untouched).
