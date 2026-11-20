# loop/log.md

1 P0-001 done English clone at pinned SHA verified (HEAD file read; Bash denied mid-iteration); translation/source.json written
4 P0-002 blocked Bash permission denied for extracting the English tree into the repo; nothing imported
5 - done-with-blockers no eligible task (all remaining depend on blocked P0-002); wrote HANDOFF.md and DONE
6 P0-002 blocked Bash denied again for English tree import (tar); nothing imported
7 P0-002 done English tree imported (git archive | tar, single command); .gitignore merged; upstream remote fetch-only

8 P0-003 done tools/inventory.py + 17 tests; file set matches English tree; repaired P0-002 import (9 nested .gitignore + tracked .pyc)
9 P0-004 done tools/lock_code.py + 22 tests; 230 frozen files locked; pre-commit hook installed; inventory --check repaired (requirements-es.txt owned)
10 P0-005 done tools/baseline.py + 6 tests; 14/14 English CI gates exit 0; translation/baseline.md written (caveats: diagrams from cache, 2 PDF-009 warnings, no Java)
11 P0-006 done LICENSE confirmed MIT, sha256 matches lock and English SHA; EXC-001 added to translation/exception-register.jsonl
12 P0-007 done tools/dnt.py + 14 tests; translation/dnt.txt (19 phrases) derived from frozen program sources
13 P0-008 done translation/phase-letters.json: 20 phase-letter locations, exercise prefixes A-G; BICHO collides on B and C (plan expected B only)
14 P0-009 done tools/humor_register.py + 12 tests; translation/humor-register.jsonl seeded with 33 entries (31 headings, 2 prose lines), all status pending
15 P0-010 done tools/acronym_search.py + 14 tests; BICHO adopted with TORCE runner-up logged; no Spanish word list on machine, so the candidate search itself was not run
16 P0-011 done tools/next_task.py (+19 tests) and tools/plan_tasks.py (+22 tests); 68 translate + 9 audit tasks generated (max 3986 words/task); rerun is byte-identical; seedtask.py now handles generated files
17 P0-012 done Phase 0 gate passed: inventory --check OK, lock_code --verify OK (230 frozen files), all deps done, LICENSE exception/phase-letters/dnt/humor-register/queue present
18 P1-001 done translation/glossary.es.yaml (206 terms, frozen 40-rule wording, assurance labels, card categories, phase macros); tools/glossary_check.py + 17 tests
19 P1-002 done translation/house-style.es.md (ETS profile: tiers T1 to T3, rules 1 to 13 with lint IDs, English-to-Spanish convention table, N=28 provisional)
20 P1-003 done translation/prompts/ (translate, review, backtranslate, adjudicate, v1) and translation/schemas/ (segment, finding, ledger-row + samples); tools/prompt_check.py with 42 tests incl. exact-substring finding check
21 P1-004 done lessons/book/locale/es.yaml with BICHO acronym text and phases 1 to 5 (letter, name, question, definition, weeks, node ID); tools/locale_check.py + 13 tests incl. TORCE swap and 7 negative cases
22 P1-005 done tests/fixtures/ (mixed.md, mermaid.md, hostile.md, data.yaml: front matter, macros, tables with \|, Mermaid entities, APL/NFD/NBSP/astral Unicode, injection text); tools/fixture_check.py + 11 tests; inventory owns tests/fixtures/ and locale/ (repaired failing --check)
23 P1-006 done Phase 1 gate passed: tools/mask.py + 26 tests; masked round trip identical on 4 fixtures (also CRLF), code spans/URLs/macros/DNT never reach the translator, fenced output and front matter withheld, I2 negatives (drop, duplicate, invent, edit) fail closed
24 P2-001 done lessons/book/locale/catalog.py loader (dotted keys, 1-based lists, macros, MissingKeyError) + en.yaml mirror + diagrams.section key; tools/test_catalog.py 28 tests incl. 11 negatives
25 P2-002 done tools/segment.py + 37 tests (escaped pipes, spaces in code, COBOL column 1, list continuation, 14 negatives); T0 identity on all 212 authored files; 7394 translatable segments; mermaid withheld whole until P2-004
26 P2-003 done tools/apply.py + 26 tests: PO layer (msgctxt=segment id, msgid=English masked), fuzzy/empty keep English, phase macros expand before unmask, orphan/stale/I2 fail closed; identity and empty PO reproduce all 212 files
31 P2-004 done tools/mermaid.py + tools/test_mermaid.py (37 tests); segment.py emits mermaid_label segments (+1433, total 8827); I2/I5/I10 fail closed; T0 and apply identity pass on 212 files (finished uncommitted work left by stalled iterations 27 to 30)
32 P2-005 done tools/invariants.py (I1 to I16: check_segment, check_po, check_files, protected_files) + 100 tests, each invariant with passing and failing cases; I13 tooling-allowlist report goes to P2-006, I14 exercise-ID ambiguity to P2-014
33 P2-006 done tools/verify.py (--fast touched files, --release everything incl. tooling allowlist report, counts, gates, double build) + 35 tests; fast run 1.3s; release --no-gates fails only on I16 no-PO for 212 files (expected)
34 P2-007 done tools/anchors.py + 47 tests; translation/anchors.json (223 files, 1314 headings); github/build/pandoc slug rules (pandoc parity tested), per-file map, link remap and check; --check is clean
35 P2-008 done lessons/book/diagrams.py takes section heading, near-miss word, I11 lead-ins, figure word and default title from the locale catalog (diagrams.*, BOOK_LANG default en, atomic set_language); 11 new tests incl. Spanish contract, negatives and a real accented render; allowlist rows added
36 P2-009 done lessons/book/study_guides.py: title pattern, 11 headings, SHARED_CHALLENGE (single source), 5+4 lead-ins, assurance labels, sandbox/predict/placeholder words from catalog study_guides.*; 69 tests (Spanish contract on a synthetic guide, English literal guard, atomic language switch)
37 P2-010 done lessons/book/cs.py: banner, table headers, lead-ins, relation words, program-flow block, openers, index and study-guides section from catalog cs.* (34+ keys, en/es); English output byte-identical (hash checked), accent-aware index order (fold/letter); test_cs.py 38 tests incl. Spanish over English sources, atomic switch, English literal guard
38 P2-011 done lessons/curriculum/build.py: chapter label (Cap.), sentence limit 28, register rule (usted/vos), acronym sentences, phase letters in table rows and diagram labels, weeks per phase from the catalog (curriculum.*); test_curriculum.py 35 tests incl. synthetic Spanish curriculum and surviving-English-letter negatives; English --check unchanged
39 P2-012 done test_editorial.py (checks as functions; words from catalog editorial.*) and pdf_sentinels.py (label sentinels from catalog sentinels.*, set_language, PROFILES updated in place); 39 tests, English and Spanish mutation fixtures; real-source tests in es fail until stage 4 (expected)
40 P2-013 done identity.* catalog block; repo_links.py, build.py, lint_pdf.py, study-guides and curriculum stems read it (set_language, publication_uuid); Spanish metadata YAMLs (es-419, titles, companion-to, new UUIDv5); 10 new tests in test_repo_links.py (25 with test_repo_identity, unchanged; sandbox tag untouched)
41 P2-014 done tools/phase_lint.py: collisions with exercise-ID prefixes (BICHO: B C; TORCE: C E), ambiguity rules in I14; I14 literal checks read the pre-expansion msgstr (expanded macros were flagged as literals); test_phase_lint.py 30 tests incl. BICHO to TORCE swap and re-apply
42 P2-015 done tools/negative.py: 45 fixtures for plan 10.2 items 1 to 11 (control clean, each fixture fails with its expected check id), wired into verify --release as "negative fixtures"; two missing gates found and added (foreign repo link check in build.check, curriculum exercise-ID check); test_negative.py 24 tests incl. disarmed-gate, wrong-id, stale-fixture and dirty-control cases
