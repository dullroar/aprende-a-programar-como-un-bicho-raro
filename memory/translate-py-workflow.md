---
gist: "Read me when: you run tools/translate.py on a file, it stops or leaves needs-revision entries, or you import drafts."
---

# Work with translate.py

## Commands

- Translate: `python3 -I tools/translate.py FILE.md --task-id ID [--limit K]`. It saves the PO after each segment. A rerun resumes. `--from N` jumps. `--redo-fuzzy` retries needs-revision entries.
- It always translates the whole file. Check the segment range of the next task for the same file. Mark it done if nothing is pending.
- Run it in the background. When it stops on "reply is not a single JSON object" (transient), rerun with `--from N+1`, then finish with `--redo-fuzzy`.
- The PO entry of the failed segment may exist with an empty msgstr. Set it with `waive_po` `set`. Never insert a duplicate.

## Traps

- Never run `translate.py` on a file after `apply.py --write` made it Spanish. It re-segments the Spanish and adds orphan PO entries. Run `git checkout -- FILE` first, then rerun.
- Never add keys to ledger rows (closed schema). Use `mask.PH_RE.finditer` and `m.group(0)`. `findall` returns tuples.
- `translate.py` glosses a term such as `(*sandbox*)` or `(*closure*)` in many segments. Lint I24 allows one gloss for each file. After each run, grep the README. Keep the first gloss. Edit the later PO entries to plain text (for example `entorno aislado`). Use a polib script, then `apply.py --write`.
- It puts backticks around an identifier in a Mermaid label even when the English has none (I23 lexical error). Grep the diagram lines. Fix with `waive_po set`, then `regen_po.py REL`.
- A heading that repeats a gloss fails I24. Use the plain term there.
- When it leaves needs-revision entries, ask first if the CHECK is wrong (plural, verb or noun, identifier in a label). Narrow the check with a test, or waive one segment in `translation/exception-register.jsonl`. Then run `apply.py FILE --write` and `verify.py --fast`.
- A link title that is an English article name ("Tail call") is translated. Rerun with `--redo-fuzzy` once before a waiver.
- Before you claim a file is complete, export all pending segments without `--from`. Early empty entries can remain.
- `--export-pending` printing nothing means the file is complete. Mark the task done after `verify.py --fast --files MD PO`.
- If `git status` shows a half-done task with untracked PO files, do not revert. Count translated and fuzzy entries with polib. Resume `translate.py`.

## Drafts import

- Write `{segment_id: text}` JSON (or a `.es` file with `N text` lines) in `translation/work/`. Build the JSONL with a script. Fill `placeholders_seen` in TEXT order. Compare it with the export's `placeholders` as sorted lists.
- A script that runs `--export-pending` in a subprocess can key texts by the segment-id suffix. A rerun then exports only the fuzzy leftovers.
- `--redo-fuzzy` needs a reply for EVERY still-pending segment ("replay has no answer"). Merge the old texts with the fixes and rebuild the JSONL.
- Run `waive_po` on known false positives BEFORE the `--redo-fuzzy` import, so the replies cover only the rewrites.
- A segment that is only a `[CODE Lnn-nn](DEST):` line needs a verb (for example "Mira"). If not, `translate.py` rejects it as unchanged English.
- Keep every sentence at 28 words or fewer (lint I12 counts placeholders). Write the first-use gloss in the first segment that names the term.
