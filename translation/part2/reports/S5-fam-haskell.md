# S5-fam-haskell batch report: src/haskell

Iteration 437. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/haskell/`)

- `timecards.hs`: 21 comment lines (`DEMO ONLY` stays in the first one, which `check.sh` greps for). Dashed separator lines and bare `--` lines are untouched.
- `check.sh`: 5 full-line comments. The static greps look at code lines, not comments.
- `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/haskell` is now `localizing`; `translation/localized-code.sha256` records 23 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/haskell --english /home/lehmer/english-source`: PASS, no findings.
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: 0 findings. `verify --fast`: OK.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-554)

- Card categories (decision 11): `Category` constructors are printed through `show`, and used by `check.sh` and the README trace.
- Display strings: `DEMO ONLY`, the `# committed ...` and stunt-note lines (parsed by `check.sh`), SQL text.
- Identifiers: none renamed (`identifier-map.jsonl` untouched).
