---
gist: "Read me when: you must change a PO entry by hand, waive a lint finding (I3, I7, I9, I10, I12, I25), or regenerate an applied file from its PO."
---

# PO edits and waivers

## Waivers

- `python3 -I tools/waive_po.py PO TASK RULES.json`. `PO` is the path with the `.md.po` suffix. `set` writes a msgstr by hand. `waive` clears fuzzy and adds an exception row.
- `waive_po` takes one invariant for each segment. A segment flagged I7 and I9 needs two calls.
- A waiver is keyed by the segment id with its position suffix. Repeat the waiver when the same English label recurs at another position.
- A waiver on a README must be repeated on the guide copy of the same segment.
- Write a non-breaking space in a rules JSON as the real character (typed spaces stay plain), or as `chr(0xA0)` in a script.
- Use `set` to remove a sandbox gloss or an invented clause that `translate.py` added.
- Typical false positives: verb "build" or "state", identifier labels (`Card N+1`), "pull request", "Windows Sandbox", an I3 decimal such as `5.7 KB` (localized format), a table row of only an opcode and numbers.
- Fix nouns such as parser, scope, list and statement by rewording. Waive verbs.
- The glossary may want a rendering for a verb that is not right (State, builds). That is a waiver. For a noun, reword.
- Never key anything on the segment-id hash prefix alone. A repeated English text shares a cache key.

## Edit a PO of an applied file

- `apply.py FILE --write` on an already-Spanish file fails with orphan entries. Use a scratch script instead. Models: `translation/work/edit_apl.py`, `translation/work/p3c004_edit.py`, `translation/work/regen_po.py`.
- Steps: set the msgstr by segment number with polib, assert that the old text occurs once, compute the expected text with `verify.english_text`, `apply.apply_text` and `anchors.layout_text`, and write it to the working path from `enpath`.
- To redo a script after a partial run, run `git checkout --` on the PO and the README first.
- Save a PO with polib `wrapwidth` 78, not 0. The diff stays small.
- A msgstr must keep every placeholder once. A DNT "Debugging" cannot become "Depuración". Write "Depuración (⟦DNT⟧)".
- Add no digit that the English lacks (I3). Spell out "three", "five" and "zero" where the English does. Keep "1,000" as the English writes it.
- A first-use gloss such as `bandera` goes in the README prose, never in an accDescr.
- Write the Write and Edit tools' special characters with `chr()` in a script. These tools decode `\uXXXX` and normalize NBSP and combining marks. Run `python3 -I tools/fixture_check.py` after you touch `tests/fixtures/`.
- A PO file of code lives under `translation/po/code/`. `verify.route()` must not treat it as Markdown.
- In a PO msgid, a literal backslash-t in the file is written `\\t`. `\t` alone means a real TAB.
