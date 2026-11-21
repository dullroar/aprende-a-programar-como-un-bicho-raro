# Phase 3C gate (P3C-017): PASSED (iteration 105, 2026-11-20)

Gate rule (task text): the new checks pass on the 12 files; a disposition exists for every review item; `source-issues.md` is up to date; `verify --release` shows no path or new-rule failure on translated files. Failures that come only from untranslated content are listed as expected and must clear at P4 or P5. No test was weakened, skipped or edited in this iteration.

## 1. New checks pass on the 12 files

| Check | Result |
| --- | --- |
| `verify --fast` (lock, queue) | OK |
| `verify --fast --files` on the 12 (P3C-016, iteration 104) | OK, 13 checks |
| `anchors.py --check` | `anchors OK` |
| Lints I21 to I26 and the path checks I17 to I20 in `verify --release` | no finding on any translated file; I17 to I20 pass |
| `build.py --check` (book) and `guias-de-estudio/build.py --check`, filtered to the 8 translated READMEs, the Forth README and the translated guides | no finding on a translated file (see section 4 for three links into English READMEs) |
| `test_anchors`, `test_diagrams`, `test_pathcheck`, `test_enpath`, `test_pathmap`, `test_repo_links`, `test_repo_identity`, `test_pdf_lint`, `test_curriculum`, `test_catalog`, negative fixtures | pass (both were red at the P3B gate for untranslated content, `test_anchors` and `test_diagrams`; now green) |

## 2. Dispositions complete

`translation/reviews/chatgpt-editorial-2026-11-20-dispositions.jsonl` has 174 rows: 66 accept, 87 modify, 19 reject, 2 no_change_needed, each with a reason, across all 12 files. Its `review_lines` are the line numbers **in the reviewed Spanish file**, as the review cites them (not lines of the review document).

Coverage check against `review/inbox/chatgpt-editorial-2026-11-20.md` lines 13 to 141: 89 bold-numbered items; every item has at least one row citing its line numbers (0 items with none). Nine items are cited by a sub-range of their numbers (rows split a long range, such as `82–95, 99–108`), which is how the rows were written; no item is without a disposition.

## 3. Source issues up to date

The ten items of review-decisions Part F are logged as SI-001 to SI-010. SI-011 to SI-017 were found while correcting the files. 17 rows in all; each Spanish passage stays faithful to the English.

## 4. `verify --release` (BOOK_LANG=es)

First run: 12 of 74 checks failed, 182 s. One was `inventory --check` ("translation/work/inventory.json is stale"): the git-ignored cache. Regenerated with `python3 tools/inventory.py`; `--check` is now OK. After that, **11 of 74 fail, all from untranslated content**, none from a path or a new rule:

| Failing check | Cause | Clears when |
| --- | --- | --- |
| authored files (212) with PO (I16) | 200 files have no PO yet (only `I16 ... no PO file` lines) | P4 |
| `book-check`, `check-diagrams`, `release-book` a and b | 64 metadata problems, all `'teaches' must start with a lowercase 'que' clause` or a missing `## Flujo del programa` in untranslated READMEs | P4 (`src/*` tasks) |
| `study-guides-check`, `release-study-guides` a and b | 313 problems in untranslated guides (labels, challenge paragraph) | P4 (guide tasks) |
| `test_cs` | untranslated READMEs lack `## Flujo del programa`; `test_the_two_cross_cutting_claims_are_true` hard-codes `## How the stunt works` (test-side literal, known since P3B-007) | P4, plus a P5 fix reading the heading from the catalog |
| `test_study_guides` | the real guides are still English | P4 |
| `test_editorial` (5) | the intro, the first guide and the root README (the aside) are untranslated | P4 |

Also reported by the study-guide check, and caused by untranslated content: three links from translated guides into English READMEs (`forth.md:78` to `src/forth-weird/README.md#program-flow`, `apl.md:62` and `:78` to `src/apl/README.md` and `src/apl-weird/README.md`). The targets still have the English `## Program Flow` heading. `anchors.py --generate` and `apply.py --relink --write` re-aim them when those READMEs are translated.

Passing: lock (230 frozen files), I17 to I20, path map, curriculum build twice with identical hashes, `test_cs` partial run aside, and every `tools/test_*.py`.

## 5. Decision

Phase 3C passes. Next task is the first stage 4 task in the queue.
