# Phase 3B gate (P3B-007): PASSED (iteration 85; iteration 82 was blocked)

Recorded here, not in translation/path-map-report.md: that file is generated and `pathmap.py --check` requires it to equal the computed report, so a hand-written result section would fail I20.

Gate rule (task notes): failures that are demonstrably due to untranslated content may be listed here as expected, but every path-related failure must be zero, and the content-only failures must re-run and clear at P5-004. No test was weakened, skipped or edited in this iteration.

## Path-related failures: zero

| Check | Result (iteration 85, `verify --release`, BOOK_LANG=es) |
| --- | --- |
| Frozen byte lock (`lock_code.py --verify`) | ok, 230 frozen files match the manifest and the English clone; `git status` shows no frozen file touched |
| I17 to I20 (`pathcheck.py`) | ok: every link destination resolves, no frozen file mentions a renamed path, map is one-to-one, every file sits at its work path |
| English-neutrality proof (`scratch_proof.py`) | PASS: six publications built twice, hashes identical, English layer |
| Release curriculum build, twice | ok, identical hashes ("double build: identical hashes" ok) |
| `test_repo_links`, `test_repo_identity`, `test_pdf_lint`, `test_curriculum`, `test_catalog`, `test_pathcheck`, `test_enpath`, `test_pathmap`, tooling_paths (33 files) | ok |
| Every other `tools/test_*.py`, negative fixtures, glossary, locale, DNT, humor register | ok |

61 of 73 checks pass. The six publications are not all built in the Spanish layout yet: the book and study-guide release builds are stopped by the untranslated-content checks below. The plan's "all six build twice with identical hashes" is met on the English layer by the neutrality proof; the Spanish-layout builds are exercised at P5-003.

## Expected failures (12 checks), all untranslated content

| Check | Why it fails | Clears when |
| --- | --- | --- |
| authored files (212) with PO (I16) | 200 of 212 files have no complete PO | P4 |
| `build.py --check`, `--check-diagrams`, `release-book` a and b | 40 metadata problems: 'teaches' still English in untranslated READMEs, missing `## Flujo del programa` | P4 |
| `guias-de-estudio/build.py --check`, `release-study-guides` a and b | 315 problems: untranslated guides lack the Spanish labels | P4 |
| `test_anchors` (2 cases) | 17 links to translated READMEs whose heading ids changed | P5-002 applies `anchors.json` |
| `test_cs` (2) | untranslated READMEs lack `## Flujo del programa`; the cross-cutting test hard-codes the English heading `## How the stunt works` (see below) | P4, and a P5 fix for the second |
| `test_study_guides` (1) | real guides untranslated | P4 |
| `test_editorial` (5) | untranslated text | P4 |
| `test_diagrams` (1) | untranslated entries | P4 |

### Not a content failure: it will not clear by itself

`lessons/book/test_cs.py:108` (`test_the_two_cross_cutting_claims_are_true`) asserts the English headings `## How the stunt works` and `## Run it in Windows Sandbox`. It will still fail after every README is translated (H008 is already Spanish in translated READMEs). It is a test-side text literal, not a path. Fix at P5 by reading the heading from the catalog (add a catalog key), not by editing the expected value to match. Also `test_study_guides.test_the_english_guides_are_refused_in_spanish` reads the real cobol guide and will fail once that guide is translated: use a synthetic English guide at P5. Both are recorded in decisions-provisional.md (iter 84, item 5).

Also: the tracked, frozen `lessons/book/__pycache__/build.cpython-312.pyc` is rewritten when a lessons/book script runs without `PYTHONDONTWRITEBYTECODE=1`; run gates with it set.
