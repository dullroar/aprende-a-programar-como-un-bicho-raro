# S5-fam-tar-gnu batch report: src/tar-gnu

Iteration 474. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English.**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/tar-gnu/`)

- `check.sh`: 25 comment lines (shebang stays). `build-archive.sh`: 9 comment lines (shebang, usage line, member-list line and the `shellcheck` directive stay).
- `dispatch.sh`: 10 comment lines (shebang and the `format=`/`category=` record-shape comments stay). `inspect.sh`: 9 comment lines. `interpret.sh`: 4 comment lines. `timecards.sh`: 2 comment lines. `Dockerfile`: 3 comment lines.
- `translation/localization-scope.yaml`: `src/tar-gnu` is now `localizing`; `translation/localized-code.sha256` records 101 localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/tar-gnu --english ~/english-source`: PASS, no findings.
- `python3 -I tools/lock_code.py --verify`: ok.
- No script was run on the host (hard rule 1).

## Kept English, on purpose (EXC-585)

- Card categories (decision 11): `dispatch.sh` accepts them with a strict pattern and `build-archive.sh` writes them into the archive, so the archive format is contract.
- Display strings: `DEMO ONLY`, `# committed ...`, error and usage messages (matched by `check.sh`).
- Identifiers: none renamed. Copied comment text in the README was not changed by this task.
