# S1 gate (S1-007)

Written by iteration 405. Checked with `translation/work/s1_gate_check.py`, `tools/token_registry.py --check`, `tools/test_token_registry.py` and `tools/test_token_audit.py`.

## Result

- **Coverage:** `translation/protected-tokens/tokens.jsonl` holds 37 language records and 37 generated pages, one for each. Every language named in `runtime-matrix.md` (and the shell, SQL, batch, PowerShell and C hosts found by the inventory) has a record. No record lacks a page and no page lacks a record.
- **Extracted:** 2 (python: CPython 3.12.3; javascript). **Not extracted:** 35, each with a stated reason (no runtime or no pinned specification; toolchains denied under dontAsk mode). Those families stay English and any report on them says NOT TESTED (policy H-05).
- **APIs separate from keywords:** the extracted pages list Reserved words, Contextual words and Standard API names in separate sections (python: 35, 4 and 149).
- **Drift gate:** `token_registry.py --check` reports OK (JSONL and Markdown agree).
- **Tests:** `test_token_registry.py` 19 tests OK (5 drift negatives); `test_token_audit.py` 24 tests OK (false-positive guards and failing fixtures).

## Caveats

- The registry is thin: 35 of 37 languages have zero tokens. Phase S2 and later must not localize any family whose language is not-extracted.
- A Docker- or toolchain-capable session could extract more languages with `token_registry.py --write` and promote them from NOT TESTED.
- Nothing was pushed.
