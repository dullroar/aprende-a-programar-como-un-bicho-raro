# English baseline gates

Run by `python3 tools/baseline.py` against the pinned English tree (see `translation/source.json`).
Nothing here was loosened or skipped. A non-zero exit code is recorded as a failure, not hidden.

## Toolchain

- python3: Python 3.12.3
- pandoc: pandoc 3.1.3
- node: v24.15.0
- npm: 12.2.2
- java: NOT INSTALLED
- git: git version 2.43.0
- pip: jsonschema==4.26.0
- pip: markdown-it-py==4.3.0
- pip: pillow==12.2.0
- pip: polib==1.2.0
- pip: PyMuPDF==1.27.2.3
- pip: pytest==9.2.0
- pip: PyYAML==6.0.3
- pip: weasyprint==70.0
- env MERMAID_CHROME: (unset)
- env MERMAID_NO_SANDBOX: (unset)

## Results

| # | gate | command | exit | seconds |
|---|------|---------|------|---------|
| 0 | book-check | `python3 lessons/book/build.py --check` | 0 | 36.7 |
| 1 | study-guides-check | `python3 lessons/study-guides/build.py --check` | 0 | 12.2 |
| 2 | curriculum-check | `python3 lessons/curriculum/build.py --check` | 0 | 2.2 |
| 3 | test_cs | `python3 lessons/book/test_cs.py` | 0 | 0.9 |
| 4 | test_study_guides | `python3 lessons/book/test_study_guides.py` | 0 | 1.1 |
| 5 | test_curriculum | `python3 lessons/book/test_curriculum.py` | 0 | 0.2 |
| 6 | test_editorial | `python3 lessons/book/test_editorial.py` | 0 | 1.1 |
| 7 | test_repo_links | `python3 lessons/book/test_repo_links.py` | 0 | 0.1 |
| 8 | test_repo_identity | `python3 lessons/book/test_repo_identity.py` | 0 | 0.4 |
| 9 | check-diagrams | `python3 lessons/book/build.py --check-diagrams` | 0 | 0.3 |
| 10 | test_pdf_lint | `python3 lessons/book/test_pdf_lint.py` | 0 | 3.6 |
| 11 | release-book | `python3 lessons/book/build.py --release --artifacts-dir translation/work/baseline/release` | 0 | 31.8 |
| 12 | release-study-guides | `python3 lessons/study-guides/build.py --release --artifacts-dir translation/work/baseline/release` | 0 | 18.6 |
| 13 | release-curriculum | `python3 lessons/curriculum/build.py --release --artifacts-dir translation/work/baseline/release` | 0 | 4.2 |

## Summary

14 of 14 gates exit 0; 0 did not.

## Honest notes

- Exit codes are the only pass/fail signal used here; warnings in the output tails are recorded, not judged.
- The diagram gate may answer from the on-disk render cache (`from cache`); the log says how many diagrams were drawn now.
- Not covered: the per-language challenge programs under `src/` and `sandbox-gate.yml` (they need Java and many other runtimes). Java is NOT INSTALLED here if listed so above.
- Full logs are in `translation/work/baseline/` (git-ignored); regenerate with `python3 tools/baseline.py`.
- The release builds write PDFs and EPUBs under `translation/work/baseline/release/`, not into the tree, so frozen files are untouched.

## Output tails

### book-check (exit 0)

```text
book edition: Learn Programming the Weird Way! v4
counts for the root README: 40 challenges in 29 languages
metadata ok; generated files are up to date
diagrams: 79 rendered with mermaid-cli 12.2.0, Google Chrome for Testing 147.0.7727.15 (79 from cache, 0 drawn now)
diagrams: removed 8 stale cached file(s)
wrote /home/lehmer/repos/aprende-a-programar-como-un-bicho-raro/lessons/book/out/weird-way.html
internal links ok
517 headings checked; every repeated title has its own id
```

### study-guides-check (exit 0)

```text
study guides: template, diagrams, links and index ok
diagrams: 36 rendered with mermaid-cli 12.2.0, Google Chrome for Testing 147.0.7727.15 (33 from cache, 3 drawn now)
wrote /home/lehmer/repos/aprende-a-programar-como-un-bicho-raro/lessons/book/out/study-guides.html
internal links ok
265 headings checked; every repeated title has its own id
```

### curriculum-check (exit 0)

```text
curriculum: plan, diagram, links and house style ok
diagrams: 1 rendered with mermaid-cli 12.2.0, Google Chrome for Testing 147.0.7727.15 (0 from cache, 1 drawn now)
wrote /home/lehmer/repos/aprende-a-programar-como-un-bicho-raro/lessons/book/out/curriculum.html
internal links ok
14 headings checked; every repeated title has its own id
```

### test_cs (exit 0)

```text
test_an_ungrounded_concept (__main__.TestTheLintersRefuse.test_an_ungrounded_concept) ... ok
test_an_unknown_concept_in_analogies (__main__.TestTheLintersRefuse.test_an_unknown_concept_in_analogies) ... ok
test_an_unknown_tag (__main__.TestTheLintersRefuse.test_an_unknown_tag) ... ok
test_every_entry_must_name_its_machine_and_its_state (__main__.TestTheLintersRefuse.test_every_entry_must_name_its_machine_and_its_state)
The comparative tables must never show a blank cell. An ordinary entry says so in words ("Ordinary: ..."). ... ok
test_removing_the_last_demonstration_leaves_only_an_analogy_which_is_still_allowed_but_visible (__main__.TestTheLintersRefuse.test_removing_the_last_demonstration_leaves_only_an_analogy_which_is_still_allowed_but_visible)
continuation has analogies and counterexamples only: the report must say so, and not call it demonstrated. ... ok
test_stale_wording_cannot_come_back (__main__.TestTheLintersRefuse.test_stale_wording_cannot_come_back) ... ok
test_teaches_needs_a_that_clause (__main__.TestTheLintersRefuse.test_teaches_needs_a_that_clause) ... ok
----------------------------------------------------------------------
Ran 18 tests in 0.873s
OK
```

### test_study_guides (exit 0)

```text
........................................
----------------------------------------------------------------------
Ran 40 tests in 1.055s
OK
```

### test_curriculum (exit 0)

```text
..............
----------------------------------------------------------------------
Ran 14 tests in 0.124s
OK
```

### test_editorial (exit 0)

```text
......
----------------------------------------------------------------------
Ran 6 tests in 1.012s
OK
```

### test_repo_links (exit 0)

```text
............
----------------------------------------------------------------------
Ran 12 tests in 0.001s
OK
```

### test_repo_identity (exit 0)

```text
....
----------------------------------------------------------------------
Ran 4 tests in 0.391s
OK
```

### check-diagrams (exit 0)

```text
flowchart            729x582     640x511   0.88     10.5  src/regex-dotnet/README.md, section '## Program Flow' (copied into lessons/languages/regex.md)
sequenceDiagram      477x836     399x700   0.84     10.0  src/regex-pcre2/README.md, section '## Program Flow' (copied into lessons/languages/regex.md)
flowchart            689x777     620x700   0.90     10.8  src/regex-pcre2grep/README.md, section '## Program Flow' (copied into lessons/languages/regex.md)
flowchart            725x706     640x623   0.88     10.6  src/regex-perl/README.md, section '## Program Flow' (copied into lessons/languages/regex.md)
flowchart            656x600     640x585   0.98     11.7  src/regex-sed/README.md, section '## Program Flow' (copied into lessons/languages/regex.md)
sequenceDiagram      654x690     640x675   0.98     11.7  src/tar-gnu-weird/README.md, section '## Program Flow' (copied into lessons/languages/tar.md)
sequenceDiagram      798x724     640x581   0.80      9.6  src/tar-gnu/README.md, section '## Program Flow' (copied into lessons/languages/tar.md)
sequenceDiagram      634x851     522x700   0.82      9.9  src/tcl-weird/README.md, section '## Program Flow' (copied into lessons/languages/tcl.md)
flowchart            651x370     640x364   0.98     11.8  src/tcl/README.md, section '## Program Flow' (copied into lessons/languages/tcl.md)
sequenceDiagram      808x753     640x597   0.79      9.5  src/xaml/README.md, section '## Program Flow' (copied into lessons/languages/csharp-linq-xaml.md)
note: 8 cached file(s) belong to no current diagram (an older text or style); a normal build deletes them
FULL RENDER GATE PASSED: 79 diagram(s) rendered in 3 families (flowchart, sequenceDiagram, stateDiagram-v2); every one fits a printed page at >= 70% scale; a second pass came entirely from the cache
```

### test_pdf_lint (exit 0)

```text
MuPDF error: syntax error: cannot find XObject resource 'Missing'
MuPDF error: syntax error: cannot find XObject resource 'Missing'
MuPDF error: syntax error: cannot find XObject resource 'Missing'
......................
----------------------------------------------------------------------
Ran 22 tests in 3.524s
OK
```

### release-book (exit 0)

```text
  Selectable content sentinels: 10/10 passed
  WARNING PDF-009 page 245: sparse page; may be an intentional section ending
    "effects, Integrity constraints, Undefined, unspecified and implementation-def\u2026"
    box [64.5, 63.866, 498.983, 91.167] pt, allowed [62.362, 62.362, 549.638, 721.134] pt
    preview learn-programming-the-weird-way-p0245.png
  WARNING PDF-009 page 374: sparse page; may be an intentional section ending
    "34.32 G. Open challenges"
    box [64.5, 65.159, 384.361, 106.392] pt, allowed [62.362, 62.362, 549.638, 721.134] pt
    preview learn-programming-the-weird-way-p0374.png
0 errors, 2 warnings; exit 0
WARNING: Ignored `overflow-x: auto` at 5:28, unknown property.
WARNING: Ignored `user-select: none` at 42:32, unknown property.
```

### release-study-guides (exit 0)

```text
study guides: template, diagrams, links and index ok
diagrams: 36 rendered with mermaid-cli 12.2.0, Google Chrome for Testing 147.0.7727.15 (33 from cache, 3 drawn now)
wrote /home/lehmer/repos/aprende-a-programar-como-un-bicho-raro/lessons/book/out/study-guides.html
wrote /home/lehmer/repos/aprende-a-programar-como-un-bicho-raro/translation/work/baseline/release/learn-programming-the-weird-way-study-guides.epub
wrote /home/lehmer/repos/aprende-a-programar-como-un-bicho-raro/translation/work/baseline/release/learn-programming-the-weird-way-study-guides.pdf
learn-programming-the-weird-way-study-guides.pdf: scanned 222/222 pages
  Selectable content sentinels: 6/6 passed
0 errors, 0 warnings; exit 0
WARNING: Ignored `overflow-x: auto` at 5:28, unknown property.
WARNING: Ignored `user-select: none` at 42:32, unknown property.
```

### release-curriculum (exit 0)

```text
curriculum: plan, diagram, links and house style ok
diagrams: 1 rendered with mermaid-cli 12.2.0, Google Chrome for Testing 147.0.7727.15 (0 from cache, 1 drawn now)
wrote /home/lehmer/repos/aprende-a-programar-como-un-bicho-raro/lessons/book/out/curriculum.html
wrote /home/lehmer/repos/aprende-a-programar-como-un-bicho-raro/translation/work/baseline/release/curriculum.epub
wrote /home/lehmer/repos/aprende-a-programar-como-un-bicho-raro/translation/work/baseline/release/curriculum.pdf
curriculum.pdf: scanned 10/10 pages
0 errors, 0 warnings; exit 0
curriculum.pdf: 10 pages (title page and contents included; the plan is about 8 in all and at most 12)
WARNING: Ignored `overflow-x: auto` at 5:28, unknown property.
```
