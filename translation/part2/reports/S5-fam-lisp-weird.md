# S5-fam-lisp-weird batch report: src/lisp-weird

Iteration 465. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/lisp-weird/`)

- `timecards.lisp`: 18 comment lines (the `;;;; ` and `;;; ` markers stay). The `Run:` line, empty `;;;;` lines, the card-chain diagram line and the `RUN TIME` section marker are kept, because `check.sh` finds the marker with `^;;; -+ RUN TIME` and strips `;.*` before its static scan. Docstrings are strings, so they stay English. `DEMO ONLY` stays in the header.
- `check.sh`: 8 comment lines (shebang stays). `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/lisp-weird` is now `localizing`; `translation/localized-code.sha256` records 73 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/lisp-weird --english ~/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-577)

- Card categories (decision 11): printed rows matched by `check.sh` and the README trace.
- Display strings and docstrings: `DEMO ONLY`, the `# committed ...` and `# PUNCH had ...` lines, SQL text, the `OK:` summary.
- Identifiers: none renamed (`identifier-map.jsonl` untouched). The README copies no comment text, so it needs no change.
