---
gist: "Read me when: you draft or fix a study guide, or its diagrams, shared-challenge paragraph or README copy do not match."
---

# Study guides and README diagram copies

## Fact

- A guide diagram copy must equal its source README diagram. `tools/sync_guide_diagrams.py` overwrites guide labels with the README labels. So a README-only I7, I9 or I12 finding must be waived on the guide copy (one `waive_po` call for each invariant).
- If the source README is still English, edit the guide diagram by hand. If the README is already Spanish, change the README PO first, then sync the guide.
- The shared-challenge paragraph is catalog text (`lessons/book/locale/es.yaml`, `study_guides.shared_challenge`, checked by I11). Never edit it in one guide. Reject a review finding against it with evidence. When the English has no backticks around the categories, the msgstr still wraps each `⟦DNT_n⟧` in backticks to match the catalog.
- Translate "What the challenge does" in `lessons/intro.md` as exactly the catalog value `study_guides.challenge_heading`.

## What to do

1. Check if the source README PO is already Spanish (`translation/po/src/<entry>/README.md.po`). Copy its labels, accDescr and term choices verbatim. Run `translation/work/readme_match.py` on the export first.
2. Translate through the tools. Do not write freehand.
3. After a README with a Spanish guide is translated: `python3 -I tools/sync_guide_diagrams.py GUIDE.md --write`, then `python3 translation/work/regen_po.py GUIDE`. After a guide is translated, sync on the restored English file, then `apply.py GUIDE.md --write`. A diagram whose README is still English stays pending.
4. Get linked page titles by grepping `lessons/` for the Spanish `[Title]` before you draft.
5. Gloss `(*shell*)` and `(*sandbox*)` once in the first segment that names it. Later text says `intérprete de comandos` and `entorno aislado`. Scope limits can come before the Safety model.
6. For a table row of only an opcode, a category and numbers, use a TRANSLATE waiver. A label such as "GNU Make" alone is rejected as unchanged English. Set it with `waive_po set`.
7. Write the gloss `(*frontmatter*)` and `(*fold*)` once for each file.
8. Use `translation/work/rx_drafts.py` as a draft template (D dict plus README reuse by identical English).
9. An accDescr synced from a README that breaks I12 is waived on the guide copy. Run `regen_po.py REL` again.
