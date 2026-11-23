# S8 full gates (Part II), iteration 485

## RUN

- `python3 tools/verify.py --release` (with English gates): **OK, 86 checks, 386.6 s**, exit 0. Includes gates A to F, release-book / study-guides / curriculum built twice (release-a, release-b), and "double build: identical hashes".
- `python3 tools/scratch_proof.py`: **PASS** (pre-1 86 s, pre-2 49 s, post-1 49 s, post-2 48 s); `translation/scratch-proof.md` updated (timings only).
- `python3 tools/link_audit.py --json translation/work/link-audit.json --md translation/part2/link-audit.md`: **FAIL, broken 33, unverified 578, not executed 0** (Markdown source only). Report: `translation/part2/link-audit.md`.

## Link audit findings (not fixed in this task)

- 29 in `lessons/cs-source/**` (links to Spanish-named paths and anchors that do not exist from that location; already listed at S3-003 as awaiting a repair task).
- 1 in the plan (`TRANSLATING.md`, `TRADUCTORIO.md`), 1 in `loop/SIGNS.md:121` (the literal text `DEST`), 2 `tests/fixtures/mixed.md` (fixture, intentional), 2 wrong-repository URLs (`review/inbox/...`, `translation/house-style.es.md`; both cite the pinned English repository on purpose).
- Several of these are by design (fixture, plan, loop notes, pinned English URLs). The `cs-source` group is real and goes to S8-002 as review-fix candidates.

## NOT EXECUTED

- Link audit over built HTML, PDF and EPUB (`--html/--pdf/--epub`): not run in this task; no artifact paths were produced for it.
- Oracle container runs for the 15 NOT TESTED families: unchanged (docker denied or no runner).

## Result

Deterministic gates green; double build hashes equal; link audit current but **not clean** (33 broken, triaged above).
