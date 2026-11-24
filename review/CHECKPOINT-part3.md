# Checkpoint: Part III (tasks H3-001 to H3-004)

Written by iteration 549 (task H3-005). `loop/STOP` exists. Jim: read this, then remove `loop/STOP` when you want the loop to continue. Nothing has been pushed, no pull request opened, nobody contacted.

## What changed

### Both guides (H3-001, H3-002)
- `TRANSLATING.md` (English) and `TRADUCTORIO.md` (Spanish) were checked against `loop/ralph.sh`, `loop/CONFIG.yaml`, `tools/model_report.py`, the usage ledger and `translation/reviews/part2-recall.md`. Three fixes per language: light-tier kinds (only `packet` is configured), the recall result, and a mismatch note. Report: `translation/part3/guide-review.md`.
- Both guides are now tracked (`git add -f`, because the exclude lines in `.git/info/exclude` could not be edited in dontAsk mode; harmless once tracked).
- `CONTRIBUTING.md` intro points to `TRADUCTORIO.md` through the PO `msgstr`.

### Upstream package for the English repo (H3-003)
- Two files: new `TRANSLATING.md` and one sentence in `CONTRIBUTING.md`. Base `48a4429c0a22b2aac628b256a50c07d1816bcb80`. Patch: `translation/part3/upstream-package.patch`; notes: `translation/part3/upstream-package.md`.
- Prepared in a scratch clone. `~/english-source` was not touched.
- Evidence: `build.py --check` passes; 20 link/identity tests pass.
- The 27 source issues (SI-001 to SI-027) are all `open`; none is approved, so none is in the package.

### Draft Spanish adoption plan (H3-004)
- `translation/part3/spanish-adoption-plan-draft.md`: pinned to the base revision plus the local patch; inventory shows 2 files touched, no code, diagram or generated change; scoped tasks A1 to A7 with verification and review. Status DRAFT until the package is accepted upstream.

## What was and was not run

- Run: the English checks above; `verify --release --no-gates` at the H3-002 commit.
- Not run: Docker `sandbox/` gates (Docker denied); Mermaid rendering in the English clone (CLI not installed; 79 diagrams unrendered, unchanged by the package); `scope-check.sh` (governs entry pull requests only).
- Not done: the outside adversarial review, the native-speaker humor check, any publication.
- English-repo quirk, not part of the package: a `.pyc` is tracked (`lessons/book/__pycache__/build.cpython-312.pyc`).

## What Jim must still do

1. **Approve both guides.** The "maintainer sign-off" the guide mentions has not happened. Read `TRANSLATING.md` and `TRADUCTORIO.md` before anything goes upstream.
2. **Decide on source issues.** Mark the SI rows you want sent as `approved` in `translation/source-issues.md`; a later task can add them as separate commits (strongest: SI-019, 021, 022, 023, verified by running software or the manuals).
3. **Run the outside adversarial review** with `review/ADVERSARIAL-REVIEW-PROMPT.md` and the local packets. Keep `review/packets/`, `review/repo-bundle.zip`, `review/canaries.key.json` and `review/units.index.jsonl` uncommitted.
4. **Get the native-speaker humor check** (`translation/humor-register.jsonl`).
5. **Publish through the maintainer process.** Open the upstream package with the English maintainer. The Spanish-edition links in the package (`https://github.com/dullroar/aprende-a-programar-como-un-bicho-raro`) resolve only after you publish that repository; check them then.
6. **After acceptance,** record the real accepted SHA in `translation/source.json`, re-run adoption step A1, and mark the plan `final`.
7. Remove `loop/STOP` to resume the loop.
