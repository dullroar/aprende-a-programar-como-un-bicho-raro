# S5-fam-tar-gnu-weird batch report: src/tar-gnu-weird

Iteration 475. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/tar-gnu-weird/`)

- `check.sh`: 21 comment lines (shebang stays). `layout.sh`: 4 comment lines. `run-clock.sh`: 6 comment lines. `tick.sh`: 3 comment lines. `timecards.sh`: 1 comment line. `Dockerfile`: 3 comment lines.
- `machine.sql`: 12 comment lines. `tick.sql`: 3 comment lines (still start with `--`, so `check.sh` filtering of comment lines is unaffected).
- `translation/localization-scope.yaml`: `src/tar-gnu-weird` is now `localizing`; `translation/localized-code.sha256` records 109 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/tar-gnu-weird --english ~/english-source`: PASS, no findings.
- `python3 -I tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-586)

- Card categories (decision 11): written into the machine's tables and matched by `check.sh`.
- Display strings: `DEMO ONLY`, usage and error messages (matched by `check.sh`).
- Identifiers: none renamed. Copied comment text in the README was not changed by this task.
