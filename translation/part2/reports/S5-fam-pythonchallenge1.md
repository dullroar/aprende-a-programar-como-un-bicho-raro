# S5-fam-pythonchallenge1 batch report: src/PythonChallenge1

Iteration 458. Verdict: **oracle PASS. Comments localized; strings, categories and identifiers kept English (EXC-572).**

## Changed (only through `tools/loc_apply.py`, PO in `translation/po/code/src/PythonChallenge1/`)

- `program.py`: 11 `#` comment lines translated line for line (line count unchanged). The module docstring is a string, not a comment, and stays English.
- `Dockerfile`: 4 comment lines.
- `translation/localization-scope.yaml`: `src/PythonChallenge1` is now `localizing`; `translation/localized-code.sha256` records the localized files.

## Proof

- `python3 -I tools/oracle.py --entry src/PythonChallenge1 --english /home/lehmer/english-source`: PASS, no findings (`deterministic: false`, as for the baseline).
- `python3 tools/lock_code.py --verify`: ok. `python3 tools/part2_inv.py --check`: clean.

## Kept English, on purpose (EXC-572)

- Card categories (decision 11): `Meetings`, `Coding`, `Debugging`, `Learning` are stored in the `categories` deque and written to SQLite; comments do not name them, so no mixed forms.
- Display strings: the window title, `DEMO ONLY` banner and labels are built in an XML string and shown in the screenshot; left English in this pass, comments only. Identifiers: none renamed.
