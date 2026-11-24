# F2-007-apl-weird batch report: card categories in src/apl-weird (decision 11)

Iteration 508. Verdict: **oracle PASS in English and in Spanish; categories localized in code, check script and README output rows of src/apl-weird.**

## Changed (only through `tools/loc_apply.py` and `tools/apply.py`)

- `timecards.apl`: `Categories` is `'Reuniones' 'Programación' 'Depuración' 'Aprendizaje'` (C20). The variable name `Categories` is a project identifier and stays.
- `check.sh`: the `cats=(...)` list (C20) and the `grep -E` row pattern (C31) use the Spanish words.
- `README.md`: the three sample output rows (`src/apl-weird/README.md` added to `category-localized-md.txt`). The README has no prose or inline span naming the categories, so `category-localized-prose.txt` is unchanged. This family has no study guide page.
- `translation/localized-code.sha256` rewritten (109 files).

## Proof

- `python3 -I tools/oracle.py --entry src/apl-weird --english ~/english-source`: PASS, no findings (`deterministic: false`, as in the baseline).
- Program and `check.sh` were not run on the host (hard rule 1).
- `lock_code --verify` ok, `part2_inv --check` 0 findings, `verify --fast` OK.

## Left English, on purpose

- Nothing else in this family names the categories.
