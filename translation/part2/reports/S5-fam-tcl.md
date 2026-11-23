# S5-fam-tcl batch report: src/tcl

Iteration 450. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/tcl/`)

- `timecards.tcl`: 28 full-line `#` comment lines. Procs, SQL, `DEMO ONLY` and the `# committed ...` / `# one while loop ...` output strings are untouched.
- `check.sh`: 10 full-line comments (the shebang stays; the `${#rows[@]}` hit is not a comment). `Dockerfile`: 4 comment lines.
- `translation/localization-scope.yaml`: `src/tcl` is now `localizing`; `translation/localized-code.sha256` records 41 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/tcl --english /home/lehmer/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-565)

- Card categories (decision 11): `categories` in `timecards.tcl`, printed rows, matched by `check.sh` and the README trace.
- Display strings: `DEMO ONLY`, the `# committed ...` and `# one while loop ...` lines, SQL text, the `OK:` summary, the usage message.
- Identifiers: none renamed (`identifier-map.jsonl` untouched).
