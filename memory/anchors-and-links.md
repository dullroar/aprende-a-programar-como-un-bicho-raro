---
gist: "Read me when: you translate or change a heading, a link fails (I16, I4, I2), or you apply a PO to a file."
---

# Anchors, relinks and apply

## Fact

- Commit `translation/anchors.json` with the heading change. Keep headings in NFC, so the build slug equals the GitHub slug.
- Keep `slug()` in `lessons/book/study_guides.py`, `build.py` and `cs.py` as a verbatim copy of each other (`tools/test_anchors.py` executes them). Normalize text at the call site, never inside `slug()`.
- `anchors.py --remap` expects English fragments. It fails on Spanish ones. Never use it by hand on an already-Spanish file. `--remap` must never touch generated pages (`lessons/languages/*.md`, I13).
- A link fragment into a translated heading is written by `anchors.layout_text`. `apply.py` and `verify.py` share it.

## What to do after you translate or re-heading any file

1. `python3 -I tools/anchors.py --generate` (before the final `apply.py --write`).
2. `python3 -I tools/apply.py --relink --write` (or `--relink FILE --write`).
3. `python3 -I tools/anchors.py --check` (a P5-002 gate).
4. `build.py --generate` if generated pages carry the links.

## Apply

- `apply.py FILE` without `--write` only reports.
- Apply the answer key PO to `lessons/respuestas.md`, its mapped Spanish path. Passing `lessons/answers-key.md` creates a separate untracked file and fails I16.
- A tool or test that opens a file named by an English key (PO, ledger, inventory, anchors) must use `enpath.load(ROOT).full(key)`. Never join `ROOT` with a path from a record. A glob over lessons folders must map the folder with `enpath.map_path`. Run tools from the repository root. Run `python3 -I tools/test_enpath.py` after you touch any of them.
- A path that `translation/path-map.yaml` renames is written in tooling only as an English KEY passed to a mapper (`cs.P`, `study_guides.GW/GP/LP`, catalog `.path()`). Run `python3 -I tools/tooling_paths.py`. Mark an English-keyed dict key `# en-key`, or a kept path `# path-ok: why`.
- After you change `translation/path-names.es.yaml` or the English tree, run `python3 tools/pathmap.py --write`, then `--check`, then `python3 -I tools/test_pathmap.py`. A Markdown file with no names row is an error. A row for README.md or a keep-list name is an error.
- After you add or rename a Spanish path name, run `python3 -I tools/glossary_check.py`. Put new name words in `path_words`, not `terms`.
- After the layout is Spanish, do not hand-edit a reference in an untranslated file. `verify` expects `enpath.remap_text(English)`. Change the rule in `tools/enpath.py`. Pass `verify.layout_remap(rel)` as `remap` to `verify.check_file`.
- Add a path or link check to `tools/pathcheck.py` (ids I17 to I20, each message starts with its id), with a `path` fixture in `tools/negative.py` item 12. Classify `pathmap.validate` messages there. Do not change their text.
- Never put a path inside a catalog value without a note for P3B-005. After `pathmap.py --write`, never edit the `paths` block of `en.yaml` and `es.yaml` by hand. Read a file before you open it for writing.
