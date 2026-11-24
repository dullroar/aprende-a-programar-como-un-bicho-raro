---
gist: "Read me when: locked code, a CRLF file, a .pyc file or the lock check (I13 CHANGED) fails, or you set up a fresh clone."
---

# Locked code, CRLF and `.pyc` files

## Fact

- `.bat` files check out as CRLF (`.gitattributes`). A raw hash of `gradlew.bat` differs by design. The lock accepts CRLF to LF only where Git reports `eol=crlf`.
- Compare frozen files by Git blob content. Use `tools/lock_code.py --verify`. Never use plain `sha256sum -c`.
- A tracked, locked `.pyc` file in `lessons/book/__pycache__/` is rewritten when `build.py` is imported. The lock then fails with I13 CHANGED.
- In Part II, a `.fs` file is Forth under `src/forth*` and F# elsewhere. Use `detect_lang` and the hash code in `tools/code_inventory.py`. Do not guess from the extension.

## What to do

- In a fresh clone, run `python3 tools/lock_code.py --install-hook` first. Then run `scripts/install_hooks.sh`. Never use the other order.
- Run book scripts as `env PYTHONDONTWRITEBYTECODE=1 BOOK_LANG=es python3 -B ...`.
- After a book test, run `git status --short`. Restore a changed `.pyc` with `git checkout -- <file>`.
- Never edit locked code to pass a task. Never bypass the pre-commit hook.
