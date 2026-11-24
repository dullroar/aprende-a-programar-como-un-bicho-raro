---
gist: "Read me when: you import or compare the pinned English tree, or you need a command that touches the English clone."
---

# Import of the English tree

## Fact

- Never import the English tree with `tar --exclude=.gitignore`. It drops nested `.gitignore` files.
- `tools/inventory.py --check` compares the file set with the pinned commit. It catches a bad import.
- `translation/work/` is git-ignored. Run `python3 tools/inventory.py` to rebuild `inventory.json` before you read it.

## What to do

- Import with one pipeline: `git -C <english-clone> archive <sha> | tar -x -C <repo>`. Keep this repository's own `.gitignore` entries, and keep `loop/`, `translation/` and the plan file.
- If the sandbox denies `tar -x` of the English tree, block the task at once. Do not try variants. Do not copy files by hand.
- Do not run compound commands that touch paths outside the repository. The English clone path is in `loop/CONFIG.yaml`.
- To replace a Spanish code file by its English baseline, copy it from `<english-clone>`, then run `loc_apply.py PATH --write`. It applies from the English baseline and refuses text that is already localized.
- The English repository is fetch-only. Never change it.
