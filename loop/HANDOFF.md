# HANDOFF (iteration 83): DONE-WITH-BLOCKERS

`python3 tools/next_task.py` returns NONE-BLOCKED: 0 tasks doing, 1 blocked (P3B-007), 80 todo but all waiting on it (directly or through the stage 3B gate).

## What is blocked

P3B-007 (stage 3B gate, after the Spanish path rename). Cause and evidence: `loop/blockers.md` (section "P3B-007 (iteration 82)") and `translation/reviews/p3b-gate.md`.

In short: the rename itself is done and verified (lock, I17 to I20, English-neutrality proof, curriculum build, verify --fast). What still fails are the English test modules and a few `lessons/book/*.py` files that hard-code renamed paths (`lessons/study-guides/metadata.yaml`, `lessons/front-matter.md`, `lessons/goals.md`, `docs/curriculum.md`, ...): test_repo_links, test_pdf_lint, test_cs, test_study_guides, test_editorial, test_curriculum.

## What a human (or the planner) must do to unblock

1. Add a build-tool task to `loop/queue/` (suggested id P3B-006b, size L, deps P3B-006): route those literals through the catalog `paths:` block (Catalog.path / enpath), and widen `tools/tooling_paths.py` to scan them with a negative case so it fails on a regression.
2. Make P3B-007 depend on P3B-006b, then set P3B-007 to `todo` (`python3 tools/seedtask.py P3B-007 todo "<note>"`).
3. Remove `loop/DONE`, then restart with `loop/ralph.sh`.

Constraint to keep in mind: the `lessons/book/*.py` and test files are English tooling, not frozen under `translation/locked-code.sha256` as code under `src/`, but check with `python3 tools/lock_code.py --verify` before editing; if any of them is in the lock, the fix must go through the catalog and enpath layer, never a byte change.

## State of the translation

836 of 8827 segments accepted, 12 of 212 files done (see `loop/STATE.md`). Bulk translation (stage 4 tasks, 68 translate + 9 audit) starts after P3B-007 passes. No provisional decision is open that blocks anything.
