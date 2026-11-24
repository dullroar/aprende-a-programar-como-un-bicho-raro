---
gist: "Read me when: you translate or change a Mermaid diagram, label or accDescr, or lint I21, I23 or the 8.4 pt label floor fails."
---

# Mermaid diagrams and labels

## Fact

- Code identifiers stay literal inside Mermaid labels, accDescr, tables and prose. Examples: `also`, `step`, `where`, `let`, `Aggregate`, `SaveChanges`, APL symbols. Describe around them. Never translate them.
- Quote an edge label with parentheses, or reword it.
- Keep each label at 8.4 pt or more (I23). Render every translated diagram. Shorten labels. Never loosen the gate. A label that needs a long glossary term forces the other labels to be shorter.
- Mermaid node text must not gain backticks that the English lacks (I23 render error).
- Lint I21 treats a dot next to an identifier as a break. Write `la llamada a let { false }`, never `.let { false }`. I21 never matches a name that only appears dotted in a code span. Waive that segment.
- A label that restates a code-comment banner keeps that word literal (I21): `Post (cláusula de actualización): ...`.
- When I7 wants a glossary word and I21 wants an identifier, write both: `la máquina (machine)`, `cards (tarjetas)`.
- When you shorten a label, keep every identifier, digit and glossary term of the English label. "hasta 40" is banned. Write "lo que pasa de 40 h". Use "pasa del tope" for a third mention of 40.
- The extractor (`tools/mermaid.py`) fails closed on unquoted labels, click and multi-line accDescr. A new diagram style needs a new rule and a test, never a looser regex. Run `python3 -I tools/test_mermaid.py` after you touch it.
- If I23 reports that the Chromium sandbox start is denied, request automatic review for the exact unchanged verifier command. After it renders, run the working-tree fast check normally so it reuses the render cache.
- Render a file with `translation/work/render_check.py FILE`. `tools/pilot_render.py` is stale after the rename.
