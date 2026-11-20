# Phase 3B gate (P3B-007), iteration 82: BLOCKED

Recorded here, not in translation/path-map-report.md: that file is generated and `pathmap.py --check` requires it to equal the computed report, so a hand-written result section would fail I20.

## Passed

| Check | Result |
| --- | --- |
| Frozen byte lock (`lock_code.py --verify`) | ok, 230 frozen files match the manifest and the English clone |
| I17 to I20 (`pathcheck.py`, also inside `verify --release`) | ok: every link destination resolves, no frozen file mentions a renamed path, map is one-to-one, every file at its work path |
| English-neutrality proof (`scratch_proof.py`) | PASS: six publications built twice before and twice after the rename on the English layer, hashes identical |
| `verify --release`: lock, inventory, counts, tooling (33), negative fixtures, JSONL, locale, glossary, prompts, fixtures, DNT, humor register, every `tools/test_*.py` except test_anchors | ok |
| Spanish-layout curriculum: `plan-de-estudios/build.py --check`, release build twice, identical hashes, `test_repo_identity` | ok |

## Failed

1. **English repo gates ran without `BOOK_LANG=es`.** `verify --release` and `baseline.py` started them with the English default, so every build looked for `lessons/goals.md` and the other renamed English names. Fixed in this iteration: `baseline.gate_env()` sets `BOOK_LANG=es` when `paths.layout` is spanish, `verify.run_release` passes it to every gate; `test_verify` has a test (36 tests ok).
2. **English test tooling still hard-codes English paths** (found by the gates after fix 1, not fixed: more than one retry of work, about ten files). Each fails with FileNotFoundError on a renamed path:
   - `lessons/book/test_repo_links.py`: `lessons/study-guides/metadata.yaml` (METADATA dict)
   - `lessons/book/test_pdf_lint.py`: `lessons/front-matter.md` (now `lessons/preliminares.md`)
   - `lessons/book/test_cs.py`, `test_study_guides.py`, `test_editorial.py`, `test_curriculum.py` (for example `docs/curriculum.md`, `lessons/goals.md`, `lessons/languages/*.md`, `lessons/study-guides/languages/*.md`), including the copies they build in temp directories under the English layout
   - `lessons/book/study_guides.py`, `cs.py`, `repo_links.py`, `lint_pdf.py`, `pdf_sentinels.py` still carry literal English path fragments (about 40 occurrences by grep); `tools/tooling_paths.py` does not catch them (it reports ok on 11 files), so it needs a wider rule
3. **Gates that fail only because the content is not translated yet (expected until P4 and P5):** `build.py --check`, `--check-diagrams` (40 metadata problems: 'teaches' still English in untranslated READMEs, missing `## Flujo del programa`), `guias-de-estudio/build.py --check` (315 problems), the two release builds of the book and study guides, I16 (212 files, no complete PO), and 2 `test_anchors` cases (17 links to translated READMEs whose heading ids changed; P5-002 applies `anchors.json`; they failed the same way at P3-010).

Also recorded: the tracked, frozen `lessons/book/__pycache__/build.cpython-312.pyc` is rewritten when a lessons/book script runs without `PYTHONDONTWRITEBYTECODE=1`; it was restored with `git checkout --` (SIGNS rule added).

## To unblock

New task before P3B-007 (suggested id P3B-006b, build-tool, size L): make every `lessons/book/*.py` and `lessons/*/build.py` path reference, and the test fixtures they build in temp directories, go through the catalog `paths:` block (`CAT.path`, `CAT.english`); widen `tooling_paths.py` to catch these literals (negative case: a literal `lessons/study-guides/` in a test file must fail); then rerun the gates. After that the only remaining gate failures must be the untranslated-content ones in item 3, and P3B-007 can pass on that documented basis (the plan's "all six publications build twice" is already met by the English-neutrality proof; the Spanish-layout builds are fully exercised at P5-003).
