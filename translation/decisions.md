# Decisions log (glossary, style and tier decisions)

One dated entry per deliberate change to `glossary.es.yaml`, `house-style.es.md` or the prompts. Provisional choices the loop made on its own also go to `loop/decisions-provisional.md`. Never rephrase an unchanged term over a new synonym: change it here first.

## 2026-11-20 First external editorial review (task P3C-001)

Source: `review-decisions-2026-11-20.md` (Parts B, C, F). Applied in this commit:

**Style.** `house-style.es.md` section 2.1 adds rules B1 to B8 (units and ranges, literal identifiers in every field, no added guarantees, voice and address, per-file first-use glosses, typography, diagram rendering at translation time, headings and anchors). Section 2.2 lists the vocabulary changes. The two broken links to the English guide are fixed (pinned English file and the local `guia-de-estilo.md`).

**Glossary (Part C).**

| Change | Before | After |
| --- | --- | --- |
| callback | retrollamada | función de devolución de llamada (*callback*); `retrollamada` is now banned |
| listener | oyente | escuchador de eventos |
| eager evaluation | evaluación ansiosa, "calcular al escribir" | evaluación inmediata; both retired |
| scope | ámbito, alcance banned | ámbito (binding); new term `scope-coverage` = alcance (what a guide covers) |
| transaction commit | confirmación | confirmación de la transacción |
| Git commit | confirmación (*commit*) de Git | *commit* de Git |
| port (of a program) | `path_words` entry "adaptaciones" | prose term `port` = adaptación |
| new terms | none | sentencia, sentencia de expresión, instrucción, función auxiliar, intérprete de comandos (*shell*), interfaz local, error de desfase en una posición, JAR, despachador de WPF, etapas diferidas, cómo viaja el dato (plumbing), in situ, suma acumulada, revisión |
| sandbox, flag, debugging | unchanged terms | notes updated (gloss once per file; boolean or bit mask; Depuración for table dimensions) |

Not captured as separate terms because the glossary maps one English word to one rendering: Forth `>in` (two renderings, by referent: *posición de lectura del intérprete* for the concept, *desplazamiento en el búfer de entrada* for the stored quantity) and the guideline that `Debugging` stays literal where it designates a card category. Both live in the glossary notes and in the translate prompt.

**Prompts and schema.** `translate.md` and `review.md` move to version 2. The translator gets rules for units, added guarantees, literal identifiers, Mermaid labels, voice and typography. The reviewer gets attack items 11 to 15. `segment.schema.json` gains the optional input field `file_first_use` (rule B5). Populating it from `tools/translate.py` is part of the B5 lints (P3C-002).

**Source issues (Part F).** Ten issues logged in `source-issues.md` (SI-001 to SI-010).

**Effect on the 12 translated files.** The new I7 terms and bans flag the 12 files translated so far (for example `statement` needs `sentencia`, `loopback` needs `interfaz local`). `verify --fast` checks only touched files, so this commit passes. Each file is corrected by its own task P3C-004 to P3C-015, and the P3C-017 gate runs `verify --release` over them.

**Path names.** Two student-facing paths contain `retrollamadas` (`eventos-retrollamadas-...`). The word stays valid as a legacy `path_words` entry (it is not an I7 term). Renaming the two files is deferred to Phase 5, because it needs a pure `git mv` plus a reference rewrite as in P3B-005.
