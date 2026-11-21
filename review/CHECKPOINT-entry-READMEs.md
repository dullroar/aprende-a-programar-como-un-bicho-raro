# Editorial checkpoint for the Spanish entry READMEs

Iteration 123 · `P4-chk-1` · 2026-11-21

The 40 entry READMEs are ready for external editorial review. Compare the Spanish files below with the same paths at pinned English commit `48a4429c0a22b2aac628b256a50c07d1816bcb80`. The previous review is [in the inbox](inbox/chatgpt-editorial-2026-11-20.md).

## Files for review

| | | |
| --- | --- | --- |
| [GoChallenge1](../src/GoChallenge1/README.md) | [JavaChallenge1](../src/JavaChallenge1/README.md) | [KotlinChallenge1](../src/KotlinChallenge1/README.md) |
| [LinqChallenge1](../src/LinqChallenge1/README.md) | [LinqChallenge2](../src/LinqChallenge2/README.md) | [ModernChallenge1](../src/ModernChallenge1/README.md) |
| [PythonChallenge1](../src/PythonChallenge1/README.md) | [RustChallenge1](../src/RustChallenge1/README.md) | [apl-weird](../src/apl-weird/README.md) |
| [apl](../src/apl/README.md) | [awk-weird](../src/awk-weird/README.md) | [awk](../src/awk/README.md) |
| [cmake](../src/cmake/README.md) | [cobol-weird](../src/cobol-weird/README.md) | [cobol](../src/cobol/README.md) |
| [ed-weird](../src/ed-weird/README.md) | [ex-weird](../src/ex-weird/README.md) | [find-gnu](../src/find-gnu/README.md) |
| [find-posix](../src/find-posix/README.md) | [forth-weird](../src/forth-weird/README.md) | [forth](../src/forth/README.md) |
| [haskell-weird](../src/haskell-weird/README.md) | [haskell](../src/haskell/README.md) | [javascript-events](../src/javascript-events/README.md) |
| [javascript-weird](../src/javascript-weird/README.md) | [javascript](../src/javascript/README.md) | [lisp-weird](../src/lisp-weird/README.md) |
| [lisp](../src/lisp/README.md) | [m4](../src/m4/README.md) | [make-gnu](../src/make-gnu/README.md) |
| [regex-dotnet](../src/regex-dotnet/README.md) | [regex-pcre2](../src/regex-pcre2/README.md) | [regex-pcre2grep](../src/regex-pcre2grep/README.md) |
| [regex-perl](../src/regex-perl/README.md) | [regex-sed](../src/regex-sed/README.md) | [tar-gnu-weird](../src/tar-gnu-weird/README.md) |
| [tar-gnu](../src/tar-gnu/README.md) | [tcl-weird](../src/tcl-weird/README.md) | [tcl](../src/tcl/README.md) |
| [xaml](../src/xaml/README.md) | | |

## Verification

The per-file checks used by `verify --release` passed for all 46 translated files. This covers the 40 READMEs, two pilot language guides, two front-matter files, the curriculum overview and the pilot recursion concept. The frozen-file check against the pinned clone also passed, for 47 checks total. The CLI applies `--release` to the full corpus, so this checkpoint called the same `Env.file_problems(path, release=True)` checks over the translated scope. Whole-edition coverage, publication builds and reproducibility are later gates.

The [first Stage 4 audit](../translation/reviews/p4-audit-1.md) sampled five segments. It found two minor issues, both corrected, and one phrasing nit. The fixes align the `awk` teaching statement and preserve the distinction between joining and adding in the `awk-weird` run ID.

## Rules adopted since the first review

- The timecard still runs at exactly 40 and stops only above 40. Keep the card that crosses the threshold. The range `de 10 a 19 horas` describes each card's hours. Card counts and literal output keep their own units and forms.
- Preserve identifiers in all prose-bearing fields, including diagram labels, accessible descriptions, table cells and front matter. Only translate the surrounding prose.
- Use *tú*, reader-action imperatives and clear subjects for program behavior. Gloss a difficult term once per file. Preserve the sandbox warning and `DEMO ONLY` marker while keeping the English scope of the guarantee.
- Use sentence-case headings, straight quotes, a nonbreaking space before `%` and Spanish list punctuation. Render diagrams at a minimum of 8.4 pt and check that visible labels and `accDescr` agree. Regenerate heading anchors and relink references when headings change.
- Use the binding glossary distinctions for callbacks and listeners, evaluation order, shell and terminal, statements and instructions, and Git and SQL commits. Check that the `teaches:` metadata and the **Te enseña:** line convey the same learning outcome.

See [rules B1–B8 and glossary decisions](../translation/review-decisions-2026-11-20.md), the [house style](../translation/house-style.es.md) and the [glossary](../translation/glossary.es.yaml).

## Open English source issues

All 18 issues in the [source-issue register](../translation/source-issues.md) are open. The curriculum and APL guide have three (`SI-001`, `SI-002`, `SI-011`). The README issues cover Java and Modern `IsNaN` explanations and Modern's anonymous container (`SI-003`, `SI-004`, `SI-015`, `SI-016`), C# and LINQ grammar and execution (`SI-005`, `SI-006`, `SI-013`, `SI-014`), Python statement counts (`SI-007`, `SI-017`), Kotlin `for` terminology (`SI-008`), and Forth wording and accessibility (`SI-009`, `SI-010`, `SI-012`). `SI-018` records the Tcl diagram's `INSERT` trigger wording.

## Questions for the reviewer

1. Do the prose, tables and diagrams agree on the timecard boundary, card count, units and the crossing card? Check at least one recursive example and one filtering example against the source.
2. Do diagram labels and `accDescr` preserve the exact identifiers and describe the same control flow as the code? Check especially LINQ filtering, Tcl trigger order and Forth flags.
3. Do the Spanish summaries, `teaches:` and **Te enseña:** agree with the English learning outcomes? Flag any stronger guarantee, missing warning or connective that changes an operation.
4. Is the Spanish clear and idiomatic across the recently completed READMEs? Sample first-use glosses, the playful headings in the [humor register](../translation/humor-register.jsonl), and links to translated headings.

For each finding, give the file, Spanish line or section, severity, the relevant English and a suggested correction. Cite the frozen code when it resolves a technical question. Identify English source issues so they can be logged upstream separately. Record a disposition for each item and apply confirmed systemic rules before removing `loop/STOP`.
