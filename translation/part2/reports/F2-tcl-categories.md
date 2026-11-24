# F2-007-tcl batch report: card categories in src/tcl (decision 11)

Iteration 532. Verdict: **oracle PASS in Spanish; categories localized in code, check script and README of src/tcl.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.tcl`: the `variable categories {...}` line (C17) now lists `Reuniones Programación Depuración Aprendizaje`; the header comment (L8, L9) names the same four words. The L8 and L9 entries use the previous Spanish comment as `msgid`, because the file already held it.
- `check.sh`: the Tcl `set cats` list (C29), the bash `cats=(...)` array (C67) and the `mapfile` grep (C76).
- `README.md`: output rows and the inline-span sentence; added to `category-localized-md.txt` and `category-localized-prose.txt`.
- `translation/localized-code.sha256` rewritten.

## Proof

- No `[A-Za-z]` class touches category names in this family (the only one is `[^a-z]` before `expr`), so unlike EXC-590 to EXC-593 nothing blocks accents.
- `python3 -I tools/oracle.py --entry src/tcl --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Nothing was run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK.

## Left as is, on purpose

- README line 51 now reads "`Reuniones` (reuniones)", a redundant gloss: apply.py keeps parenthesized words and does not drop the gloss. A later wording pass may trim it.
