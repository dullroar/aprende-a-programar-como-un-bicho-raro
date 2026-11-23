# Decision 11: places that assume the four card categories stay English (S4-006 listing)

Source: `translation/decisions.md` decision 11. Task S4-007 applies each row and marks it done here. No S5 family task may start before every row is done. Each S5 family task changes its own fixtures in its own commit.

Proposed Spanish words (glossary candidates, provisional, see `loop/decisions-provisional.md`): `Meetings` = Reuniones, `Coding` = Programación, `Debugging` = Depuración, `Learning` = Aprendizaje. The Python tools `recall_test.py` and `jury_packet.py` already use this same set for their seeded faults.

| # | Place | What assumes English | Status |
| --- | --- | --- | --- |
| 1 | `loop/PROMPT.md` hard rule 8 and the rule 1 Part II sentence | lists the four categories as never translated | todo |
| 2 | plan section 4.1 rule 13 and section 16 (plan document named by `plan_path` in CONFIG.yaml) | "never translate card categories" | todo |
| 3 | `translation/part2/policy.md` and `translation/localization-scope.yaml` header | "by default the four card categories never change" | todo |
| 4 | `translation/glossary.es.yaml` (`card_categories`, `tools/glossary_check.py` REQUIRED_CATEGORIES) | values are the English words as do-not-translate | todo |
| 5 | `tools/dnt.py` (REQUIRED, CATEGORIES) and the derived `dnt.txt` | categories are protected phrases | todo |
| 6 | `tools/invariants.py` I2, I8, I13 (card-category code-span handling, line 713 area) | category word must survive as code in prose | todo |
| 7 | `tools/negative.py` fixture row 11 (`card-category-translated`) and `tools/fixture_check.py` | a translated category is the fault | todo |
| 8 | `tools/oracle.py` CATEGORIES and CARD_RE | the oracle matches English category names only; must accept the mapped Spanish word per family | todo |
| 9 | `tools/mask.py` and `tools/test_mask.py` | masks the four words | todo |
| 10 | `tools/recall_test.py`, `tools/jury_packet.py` | seeded fault "translated card category" becomes "inconsistent or mixed category word" | todo |
| 11 | `translation/humor-register.jsonl` and the approved PO entries | segments that gloss the English names once per chapter | todo |
| 12 | Spanish prose that glosses the English categories (about 20 study guides, the book text, the curriculum) | find with `grep -rn "Meetings\|Coding\|Debugging\|Learning"` over the Spanish Markdown | todo |
| 13 | tests that encode the old rule: `test_invariants.py`, `test_dnt.py`, `test_mask.py`, `test_recall_test.py`, `test_jury_packet.py`, `test_prose_lint.py`, `test_oracle.py` | expectations | todo |

Order for S4-007: glossary (4), then tools (5 to 10), then tests (13), then prose (11, 12), then the rule texts (1 to 3). Run `verify --fast` after each group. Do not weaken a check: replace the English-only expectation with the mapped-word expectation and keep a failing fixture for a mixed or wrong word.
