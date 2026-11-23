# HANDOFF (iteration 494)

The queue is complete. Local release candidate `v4-es.0-rc2` exists (tag on 23e837a, not pushed). Nothing has been published. Read `loop/END-REVIEW.md` for the full picture.

## What a human does next

1. Read `loop/END-REVIEW.md` (decisions, exceptions, recall, items for a native speaker).
2. Answer the open provisional decision: the iteration 387 "Alive"/"Vivo" question.
3. Send the review packets to jurors: `review/MANIFEST.md`, prompt in `review/ADVERSARIAL-REVIEW-PROMPT.md`, packets in `review/packets/` (critical packets go to two jurors with different lenses).
4. Ingest the answers with `python3 tools/jury_ingest.py`. It adds `review-fix` tasks and removes `loop/DONE`; then run `loop/ralph.sh` again.
5. Run the docker self-test and the 15 NOT TESTED Part II families in a Docker-capable session (`translation/part2/runtime-matrix.md`).
6. Publishing (push, remote, visibility) is yours; the loop never does it.

## Local-only files (untracked on purpose)

`review/packets/`, `review/repo-bundle.zip`, `review/canaries.key.json`, `review/units.index.jsonl`, `review/ADVERSARIAL-REVIEW-PROMPT.md`, `loop/driver.out.claude`. The packets carry planted canaries; do not commit them. Rebuild with `tools/jury_packet.py` (seed 1) if lost.

## Blockers

None.
