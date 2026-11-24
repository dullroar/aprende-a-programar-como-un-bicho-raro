---
gist: "Read me when: you add a directory or file, localize a tooling file, or verify.py or inventory.py fails before a commit."
---

# Inventory registration and the verify gate

## Fact

- A new directory of Spanish-owned files needs its prefix in `OWNED_PREFIXES` in `tools/inventory.py`. Run `python3 tools/inventory.py --check` before the commit.
- A localized tooling file needs a row in `translation/tooling-allowlist.txt` in the same commit. If not, I13 fails. Also add every changed tooling file under `lessons/book` there.
- Run `python3 -I tools/verify.py --fast` before every commit. It has no `--task` flag (it prints help). The accept command of a translate task is plain `--fast`.
- `verify.py --release` without `--no-gates` takes many minutes. A test must never start the English repository gates.
- Do not run `verify --release` right after `tools/scratch_proof.py --tests`. Stale inventory state makes 4 checks fail once. Run `inventory.py`, then verify again.
- Run `verify --release --no-gates` after you widen classes or localize categories. It finds what `--fast` does not. For scoped files, call `verify.Env.file_problems(path, release=True)` with English keys, because the `--release` CLI checks the whole corpus.
- After you touch a tool, run its test: `python3 -I tools/test_<name>.py`.
- A tool run as `python3 -I` does not see sibling modules. Put its own directory on `sys.path` before `import mask` or `import segment`.
- Part II checks I28 to I31 live in `tools/part2_inv.py`. `invariants.py` only lists them.
