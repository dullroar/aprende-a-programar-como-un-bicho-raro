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

## 2026-11-22 Decision 11 at checkpoint S4-chk-1 (Part II pilot): localize the four card categories

Source: `review/CHECKPOINT-part2-pilot.md`. Recorded by Claude from Jim's answers in the session.

**Decision.** The four card categories `Meetings`, `Coding`, `Debugging` and `Learning` are **localized** in code, program output and fixtures, not left English. This reverses the plan's default (§4.1 and §16, "stay English").

**Oracle.** Docker is allowed in the loop's permissions (`Bash(docker:*)` in the project's untracked `.claude/settings.json`). The oracle (`tools/oracle.py`) runs for each family, so a family is localized only with oracle proof. S0-003's sandbox self-test and the four pilot families (Forth, C#/LINQ/XAML, COBOL, regex-pcre2) are re-run first.

**Consequences to handle (not decided here).**
- The Spanish words for the four categories come from the glossary; S4-006 proposes them in `loop/decisions-provisional.md` and applies them consistently (candidates: reuniones, programación, depuración, aprendizaje).
- Prose in already translated files that glosses the English categories once per chapter, the card-category checks (I2, I13 and the humor register if affected), and `PROMPT.md` hard rule 8 and §4.1 rule 13 ("never translate card categories") need updating so the rules match this decision. S4-006 lists each place and fixes it before any S5 family task starts.
- Cost to reverse after the bulk is high: fixtures that embed the names change per family. Each family's change stays in its own commit so it can be reverted alone.

## 2026-11-23 End-of-run review answers from Jim (after release candidate v4-es.0-rc2)

Recorded by Claude from Jim's answers in the session. The follow-up work is described in the plan section "Part II follow-up" and queued as tasks F2-001 to F2-008.

1. **Card categories in program output: staged pass.** Localize the four category names in the code, printed output and saved test data of three oracle-proven families first (src/cobol, src/forth, src/lisp), then stop at a checkpoint for Jim, then roll out to the other oracle-proven families. The families the oracle could not test stay English. This keeps decision 11 (localize) and adds a staged rollout.
2. **The four Spanish words:** Reuniones, Programación, Depuración, Aprendizaje stand for the pilot; Jim reviews them in the pilot output at the checkpoint, where they are cheap to change.
3. **"Alive" in the weird APL diagram:** keep the approved Spanish label "¿Vivo: total ≤ 40?". The note in the Spanish catalog that says Alive stays English is wrong for this label and is corrected in F2-001's housekeeping pass.
4. **Dashes:** use the Spanish long dash (raya, —) wherever the Spanish text uses a spaced hyphen as a dash. Never in code, URLs, file names, command-line flags or number ranges.
5. **Model-reviewer recall test for code comments:** run it only if an AI jury will review the localized comments. Not queued now.
6. **Docker self-test:** run it and record the result (F2-001).
7. **Native-speaker check of the humor register:** skipped for now. It is a prerequisite for any publication, not for the loop. Listed in the plan.
8. **Phase markers:** the whole-corpus review phase and the review-packet phase are marked passed in loop/STATE.md, with their evidence.

## 2026-11-23 Pilot review of the category localization (checkpoint F2-006)

Recorded by Claude from Jim's answers in the session. Jim approved the four words as printed (Reuniones, Programación, Depuración, Aprendizaje) and the rollout to the other families whose oracle passed. The inline-text gap found by the pilot (English category words left in inline code and prose next to Spanish sample output) is fixed by a tool task, F2-006b, before the rollout. Families the oracle could not test stay English. `loop/STOP` removed.

## 2026-11-23 Answers after the category follow-up (release candidate rc2 plus follow-up)

Recorded by Claude from Jim's answers in the session.

1. **Six families left English:** make their regular expressions accent-safe, then localize their category words (ed-weird, ex-weird, regex-pcre2grep, regex-perl, regex-sed, tar-gnu). Each change is proven by the oracle in English and Spanish.
2. **Native-speaker check of the humor register:** deferred, and handled as part of the final review before any publication.
3. **Model-reviewer recall test for the localized code comments:** run it. An AI jury will be used on the comments.
4. **Part III (translation guide and upstream package):** start it. Note: the plan's entry gate names the outside adversarial review (the Jury) as evidence. That review has not happened yet; Jim waives that part of the gate for starting the drafting work. Nothing is published, pushed or sent to the upstream maintainers by the loop. The approval of both guides stays a separate checkpoint.
5. **Tag a third release candidate** (`v4-es.0-rc3`, local, not pushed) when the six families and the recall test are done and the release check passes.
