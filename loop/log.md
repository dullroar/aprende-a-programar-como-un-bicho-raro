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
