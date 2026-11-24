# F2-007-tcl-weird batch report: card categories in src/tcl-weird (decision 11)

Iteration 533. Verdict: **oracle PASS in Spanish; categories localized in code, check script and README of src/tcl-weird.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.tcl`: the SQL string with `lindex {Meetings Coding Debugging Learning}` (C75).
- `check.sh`: `cards()` grep (C12), the hours-row grep (C37), `cats=(...)` (C73) and the `mapfile` grep (C82).
- `README.md`: output rows and the copied SQL excerpt (fence); added to `category-localized-md.txt` and `category-localized-prose.txt`.
- `tools/apply.py`: `LIST_RE` also follows a braced Tcl list `{Meetings Coding Debugging Learning}` inside a fence (2 tests: positive, other order stays).
- `translation/localized-code.sha256` rewritten.

## Proof

- No `[A-Za-z]` class touches category names in this family, so nothing blocks accents (unlike EXC-590 to EXC-593).
- `python3 -I tools/oracle.py --entry src/tcl-weird --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK.
