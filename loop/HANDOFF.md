# HANDOFF (iteration 377)

The queue has no eligible task. One task is blocked: **P5-001** (regenerate and refresh canonical copies). Everything after it depends on it.

## Blocker (details in loop/blockers.md, "P5-001 (iteration 377)")
Running `build.py --generate` with `BOOK_LANG=es` is idempotent (a second run leaves the tree unchanged), but it writes Spanish text into the generated blocks of the lesson pages. Invariant I13 (`tools/invariants.py`, `i13_text`) requires those blocks to equal the English source. `verify --fast` then fails 19 of 22 checks. The generated files were reverted to HEAD, so the tree is green.

Plan section 10.1 B expects generated blocks to equal the generator's output, which is the Spanish one. I13 expects English. Both cannot hold for the same file.

## Decision needed (a human)
1. Make I13 skip generated blocks, because `build.py --check` already compares them with the generator in the Spanish edition. Add a narrow negative test for that. This matches the plan.
2. Or keep generated blocks English in the Spanish files and make the generator emit English in that case.

After the decision: set P5-001 to `todo`, regenerate with `BOOK_LANG=es`, run `verify --fast`, then continue with P5-002.

## Also open
- `build.py --check` in Spanish reports 8 broken internal links (anchors into generated chapters, P5-002's job) and a root README note ("update it to 40 challenges in 29 languages").
- The JavaScript study guide diagram labels (`tools/sync_guide_diagrams.py`, 25 labels) fail I7 and I9. The change was reverted. Re-run after the glossary and README PO are checked.

## Working tree
Committed in iteration 377: the Forth study guide diagram labels (verified), `loop/queue/seed.jsonl`, `loop/STATE.md`, `loop/log.md`, `loop/blockers.md`, `loop/SIGNS.md`. Untracked and left alone: `loop/driver.out.claude`, this file.
