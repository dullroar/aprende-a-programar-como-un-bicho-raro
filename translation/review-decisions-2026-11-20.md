# Decisions from the first external editorial review (2026-11-20)

**Source:** `review/inbox/chatgpt-editorial-2026-11-20.md`, an external review by ChatGPT of the 12 files translated so far (commit `22e3a5f`). It is the first "Jury"-style review, run early on purpose: fixing rules now is cheaper than reworking 200 files later.

**How to use this file.** It is the binding contract for tasks P3C-001 to P3C-017 and for every later translation task. Part A lists claims that were verified against the files. Part B lists the new rules. Part C lists glossary decisions. Part D says how to treat the review's per-line suggestions. Part E covers tooling work. Part F is the source-issue policy.

## A. Claims verified before adopting the review

| Claim | Check | Result |
| --- | --- | --- |
| Forth README says 10 to 19 **cards**, not hours | English `src/forth/README.md:21` says "add 10 to 19 hour cards"; Spanish line 21 says "agrega de 10 a 19 tarjetas de horas" | **Confirmed. Critical meaning error** in the shared challenge sentence |
| LINQ variant A diagram has an unrenderable edge label | `src/LinqChallenge1/README.md:66` has `\|demanda (pull)\|`, with unquoted parentheses | **Confirmed** |
| Code identifiers translated inside diagrams | `donde`, `de persistido en`, `también encadena`, `paso` found in Mermaid labels in LinqChallenge2, KotlinChallenge1 and PythonChallenge1 | **Confirmed** |
| `cs.py` hard-codes English | `lessons/book/cs.py:312, 345, 347` match English `that` and `**Teaches you:**` | **Confirmed** |
| Stale anchors | `#what-the-challenge-does` in Spanish study guides and `#side-by-side` and `#gotchas-worth-knowing` in READMEs | **Confirmed** |

The reviewer's other items are treated as credible leads. Each is decided in its file task (Part D), never applied blindly.

## B. New rules (add to `house-style.es.md`, the prompts and the lints)

**B1. Units and ranges.** A numeric range keeps the unit of the English. The shared challenge says each card has "de 10 a 19 horas" (hours per card). It never says "de 10 a 19 tarjetas". Add a lint: a Spanish sentence containing `de 10 a 19` must name the unit hours, and the count of cards (3 to 5) must never take that range. Negative fixtures: "10 a 19 tarjetas" fails; "10 a 19 horas por tarjeta" passes.

**B2. Code identifiers are literal in every prose-bearing field.** In Mermaid node and edge labels, `accTitle`, `accDescr`, table cells, front matter and ordinary prose, a name that exists in the code stays as it is, in code font where the field allows it. Examples: `also`, `step`, `where`, `from persisted in`, `let`, `over-40?` (with its `?`), `.let { false }`, `Double.IsNaN`, `SaveChanges`, `Aggregate`, `Seq`, `After`, `ShowDialog`, `/closed`, `WaitForSaves`, `⎕CR`, `⎕FX`, `⍎`. The Spanish describes around them ("`where`: la suma acumulada hasta este día es como máximo 40"). Extend masking and invariants beyond diagram skeleton equality (see Part E).

**B3. No added guarantees.** The translator must not add absolute claims that the English does not make. Examples to remove or soften: "no puede dañar nada", "el código no afecta a tu sistema", "donde un error no daña tu equipo", "nunca se publica nada". Define the sandbox **once per file**: "un entorno aislado (*sandbox*) que limita el acceso al sistema anfitrión", then use "entorno aislado". Keep "Ejecútalo solo en el entorno aislado" and the `DEMO ONLY` marker with a plain gloss ("datos ficticios marcados con `DEMO ONLY`").

**B4. Voice and address.** Keep *tú*, usually implicit. Use the imperative for an action the reader performs (*Lee*, *traza*, *ejecuta*). Use infinitives after outcome lead-ins ("deberías poder", "podrás"), coordinated in the infinitive. Describe what a program does in the indicative with an explicit subject ("El programa abre…"). In headings, use an imperative for an action ("Traza una ejecución") and a question or indirect question for an explanation ("Cómo funciona el truco"). Never switch to *usted* or *vos*. Program output and literal labels stay as they are.

**B5. First-use glosses are scoped per file.** The translate prompt receives the file's first-use decisions with each segment, so the same gloss is not repeated in every segment. Add an assembled-file check for duplicate glosses, label drift, subject switches and missing literal values.

**B6. Typography and punctuation.**
- Non-breaking space before `%` (`30 %`).
- No serial comma in simple lists, and no comma before a simple "o" or "y".
- Titles of works are italicized; link text is translated; headings use sentence case ("mayúscula inicial y minúsculas en el resto, salvo nombres propios, siglas y literales").
- Distinguish decimal notation and units in prose ("40 horas", "8 horas") from exact program output (`40.0h`), which is preserved.
- Straight quotation marks remain the rule; keep quotation punctuation outside the delimiters where appropriate.

**B7. Diagram rendering is checked at translation time, not only in Phase 5.** Every translated diagram must render with the project's Mermaid CLI and meet the 8.4 pt print threshold. Edge labels containing parentheses or other Mermaid-special characters must be quoted or reworded. If a label is too long, shorten it (labels are not sentences) and keep the detail in `accDescr` and the prose. Never loosen the threshold. Edit the visible labels and `accDescr` together.

**B8. Headings and anchors.** When a heading is translated, every incoming link to it is migrated in the same change (see Part E). Prefer a stable explicit anchor when a heading is linked from the shared common paragraph.

## C. Glossary decisions (apply in `translation/glossary.es.yaml`; add each Spanish word used in a path or label)

| English | Spanish decision | Note |
| --- | --- | --- |
| callback | **función de devolución de llamada** (*callback*) on first use per file, then repeat where the referent could be unclear | Retire "retrollamada". A callback can be synchronous; do not define it by an event or a delay. Keep API names such as `addEventListener` |
| listener | **escuchador de eventos** | Not "oyente" |
| eager evaluation | **evaluación inmediata** | Already used in LINQ and WPF material. Retire "calcular al escribir". Keep "evaluación perezosa", "ejecución diferida" (LINQ) and memoization as separate concepts |
| scope | **ámbito** for lexical or dynamic binding; **alcance** for what a guide covers | Use "ámbito dinámico" consistently |
| Forth `>in` | **posición de lectura del intérprete** (the concept) and **desplazamiento en el búfer de entrada** (the stored quantity) | Distinct from "análisis sintáctico" |
| flag | **bandera**, introduced as a boolean or bit mask in context | |
| transaction commit | **confirmación de la transacción** | SQL |
| Git commit | ***commit* de Git**; the action is "registrar … con un *commit*" | Keep `git commit` literal |
| sandbox | **entorno aislado** (*sandbox*), glossed once per file (rule B3) | |
| port (of a program) | **adaptación** | Promote from `path_words` into the prose glossary |
| statement / expression statement / instruction | **sentencia** / **sentencia de expresión** / **instrucción** | |
| helper function | **función auxiliar** | |
| shell / terminal | **intérprete de comandos** (*shell*) / **terminal** | A terminal hosts the session; the shell interprets |
| loopback | **interfaz local** (`127.0.0.1`) | Avoid "puerto de retorno local" |
| Debugging (as a table dimension or heading) | **Depuración** | The four card category strings stay `Debugging`, `Meetings`, `Coding`, `Learning` wherever they designate values |
| off-by-one error | **error de desfase en una posición** | "error de una línea" for the source-copy boundary |
| JAR | **JAR** | Not "jar" |
| dispatcher | **despachador de WPF** or **bucle de mensajes**, by referent | |
| lazy queue | **etapas diferidas** | Avoid "cola perezosa" |
| plumbing (figurative) | avoid "plomería" | Say "cómo viaja el dato" or "la mecánica de la salida" |
| in place | **in situ** or "se modifica directamente" | |
| prefix sum | **suma acumulada** (glossed once) | |
| review (curriculum) | **revisión** | |

## D. Treating the review's per-line suggestions

For each file task: read the review section for that file, then for **every** item decide **accept**, **modify** or **reject**, checking the English source, the glossary and these rules. Do not apply an item you cannot justify against the English. Record each decision in `translation/reviews/chatgpt-editorial-2026-11-20-dispositions.jsonl` as `{"file","review_lines","decision","reason"}`.

- Apply by editing the PO targets through the tools, never by editing a file that bypasses the segmenter, and keep the byte lock.
- Treat items marked **Technical** and **Link** first, then the rest.
- Items marked **Source issue** are logged only (Part F); the Spanish stays faithful to the English meaning.
- Where the review suggests rewording for taste, prefer the wording that matches these rules and the glossary. Reject changes that add content.
- Re-review every changed passage that touches a critical or major category with a fresh-context reviewer.

## E. Tooling work (P3C-002 and P3C-003)

1. **Identifier protection beyond skeleton equality.** Extend masking and the invariants to named symbols in Mermaid labels, `accDescr`, table cells, metadata and prose. Allowlist per entry from the code and from `dnt.txt`. Negative fixtures: `also` to "también", `step` to "paso", `where` to "donde", `from persisted in` to "de persistido en", `over-40?` without the `?`.
2. **Unit-sensitive check** for rule B1.
3. **Render check in `verify --fast`** for every translated Mermaid diagram (parse, render, 8.4 pt), with a fixture for an unquoted parenthesis in an edge label.
4. **Duplicate-gloss and added-guarantee lints** (rules B3 and B5). The absolute-claim phrase list lives in the locale or style config.
5. **Typography lints** (rule B6).
6. **`cs.py` teaches contract through the locale:** the prefix ("que") and the printed label ("Te enseña:") come from the catalog. Add positive and negative Spanish tests, using the LinqChallenge1 mismatch between line 3 and line 19 as a regression fixture.
7. **Common-paragraph anchor** in the study guides: the shared challenge paragraph links to a heading that the Spanish catalog computes differently. Migrate the target heading and every source together, or use a stable explicit anchor, and adapt the catalog and checker.
8. **Stale-anchor migration** across all translated files using `anchors.json`: `#what-the-challenge-does`, `#side-by-side`, `#gotchas-worth-knowing`, `#program-flow` in generated chapters. Check both standalone GitHub Markdown and assembled publications. Run `tools/sync_guide_diagrams.py` whenever a canonical diagram changes.
9. **Broken links in `house-style.es.md`:** `../house-style.md` has no target at the current path. Link to the pinned English source for the English reference and to the path-mapped local guide where it exists. Create `translation/decisions.md` and `translation/source-issues.md`, which the policy already names.
10. **Title-page visible copy:** the title-page Markdown for the curriculum and study guides still has English visible text; translate it through the catalog.
11. **Layout checks:** parse table dimensions, fenced code and raw terminal output before rendering; render long captions and wide table cells (curriculum diagram, the Java markup table) at publication size. Full PDF and EPUB checks stay in Phase 5.

## F. Source-issue policy and the items to log

The Spanish edition translates what the English says. When the English itself looks wrong or imprecise, **log it in `translation/source-issues.md`** for the English repository and do not fix it silently in Spanish. The first batch to log, from the review:

1. Curriculum: the claim that the commit timestamp proves the order of prediction and run. Independent proof needs evidence tying the run to the committed prediction.
2. APL guide: "discards two draws" is an observed trace; the program can use three, four or all five. The test concerns the count of card functions, not "five hours".
3. Java and Modern README: `Double.isNaN(int)` reads like a method signature; the method takes a `double` and the integer is widened.
4. Modern README: "the anonymous object is the only legal container" is a design choice of this implementation, not a language rule.
5. LINQ README: "must end in an invocation" overgeneralizes; the C# grammar allows other expression statements.
6. LINQ B: `where` filters by the cap and does not signal an early stop; clarify the lowering of `where`, `let` and `from`.
7. Python README: `pass` versus `...` and the statement-counting rule.
8. Kotlin README: "no semicolons" is shorthand for the missing three-clause `for` header.
9. Forth README: "a stack language needs a loop and a pipe" overgeneralizes.
10. Forth diagram alternative text drops the `?` of `over-40?`.

## G. Early checkpoints (process change)

Do not wait for the end. After the **entry READMEs** (all `P4-src-*` tasks) the loop writes a checkpoint packet and **stops** (`P4-chk-1`), so an external review can run before the 108 concept files and the rest are translated. Any new rule found there is added here, applied to the finished files, and only then does the next family start.
