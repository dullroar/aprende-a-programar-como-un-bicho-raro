# Release report: v4-es.0-rc1 (local release candidate, nothing published)

Written in iteration 392 (task P6-003), 2026-11-22. Tag is created by P6-004; this report is for the commit `af7734c4aa63b5815486a96f0fdf13108f928c4d` (branch `loop/es-v4`).

## Identity

| Item | Value |
| --- | --- |
| Edition label | v4-es.0-rc1 |
| Spanish title | ¡Aprende a programar como un bicho raro! (es-419, register tú) |
| Pinned English source | `48a4429c0a22b2aac628b256a50c07d1816bcb80` (`dullroar/learn-programming-the-weird-way`) |
| Frozen-file lock | `translation/locked-code.sha256`, 230 entries |

## Tool versions

Python 3.12.3, pandoc 3.1.3, git 2.43.0, WSL2 Ubuntu 24.04 (Linux 6.6.87.2). Example programs run only in the sandbox container.

## Commands and exit codes

| Command | Exit | Result |
| --- | --- | --- |
| `python3 tools/verify.py --release` (iteration 392, re-run for this report) | 0 | OK, 75 checks, 421.3 s; includes "double build: identical hashes" |
| `python3 tools/verify.py --release` (iteration 391, P6-002) | 0 | OK, 75 checks |
| `python3 -I tools/inventory.py` | 0 | OK; classes frozen=230, authored=212, generated=11, tooling=33, archival=16 |
| `python3 tools/next_task.py` | 2 | Normal: exit 2 means "task printed" (P6-003) |

Earlier gates (from `loop/STATE.md`): P0 iter 17, P1 23, P2 47, P3 58, P3B 85, P3C 105, P4 376, P5 387. The P5-004 gate built the six publications twice and got identical sha256 values; the release gate repeated that check (A and B rounds for book, study guides and curriculum).

## Artifact hashes (sha256, repo root)

| File | sha256 |
| --- | --- |
| aprende-a-programar-como-un-bicho-raro.pdf | e75ba85f673e3694a71f9a75b857046b93227fe9de5d478bea98a846626fae8c |
| aprende-a-programar-como-un-bicho-raro.epub | 7aca2f147014dc4aee0f28dee35af276b7a42d80fe72cc515cc10baa0d5ca2d3 |
| aprende-a-programar-como-un-bicho-raro-guias-de-estudio.pdf | 3302ee321c459e19d9605b83dde17c38d38ee8dfd805fd4f51e399c3c3be11b0 |
| aprende-a-programar-como-un-bicho-raro-guias-de-estudio.epub | 077d2038862f6684e6067fbe5d8ceea812803dc2f224ddc03f2ac719a0602693 |
| plan-de-estudios.pdf | cf89659cfea279ff1d80354a58dd6a9a9ea47b95c4e15ee14aace570fb9ccb43 |
| plan-de-estudios.epub | c6346cde3323dc2d5d811fa12fccae8ba7d625c1f494edd0156ac6ecb9307f52 |

Note: the root PDFs and EPUBs are the checked-in artifacts. The English-named `learn-programming-the-weird-way*.{pdf,epub}` and `curriculum.*` files in the root are English-layout outputs and are not part of this edition.

## Coverage

- PO catalogs: 212 files, 9,039 `msgid` entries (212 headers + 8,827 segments). Untranslated: 0. Fuzzy: 0 (counted by script over `translation/po/**/*.po`).
- Files by class (inventory): authored 212 (all translated), generated 11 (rebuilt in Spanish by `build.py --generate`, second run zero diff), frozen 230 (byte-identical to the pin, enforced by the lock and pre-commit hook), tooling 33, archival 16.
- Humor register: 175 rows. Exception register: 538 rows. Source issues logged: 26 (`translation/source-issues.md`).
- Visual inspection: 34 page images with `index.json` (seed 20261122) in `translation/work/visual/` (git-ignored, regenerable; not reviewed by a human yet).

## Review and model IDs

- Translator: `anthropic/claude-sonnet-5-5` (config); drafts for many tasks were also produced by Codex `gpt-6.1-terra` (standard tier, medium effort, 159 iterations) and a few by `claude-haiku-5-5` (light tier, regen/gate work).
- In-loop reviewer (P6-001 and the P4 audits): `claude-sonnet-5-5`. This is the same family as the main translator, so it is **not** an independent vendor review (`cross_vendor_review: false`).
- P6-001: full 40-rule scan of all Markdown clean; 14-segment pre-registered sample (seed 390), 0 findings. Nine P4 audits, no open review-fix tasks.
- Cost ledger: `python3 tools/model_report.py`; driver-reported spend $112.64 of $150 through iteration 274 (Codex cost unavailable; later Claude spend is in `loop/ledger/usage.jsonl`). 150 early Claude iterations carry no model tag (`no evidence`).

## Caveats

1. **Not a full human or independent read.** The whole corpus was not read segment by segment in the loop; stage 7A packets are meant to cover that.
2. **Open question for Jim:** "Alive" / "Vivo" rendering (decisions-provisional.md, iteration 387). Seven provisional decisions are open.
3. **Known failing tests outside the release gate** (noted in decisions-provisional.md, iteration 387): five `lessons/book/test_editorial.py` RealSources tests that assume English-layout paths, and several `test_cs.py` tests, fail when run in the English layer; they pre-date P5-004, and `src/` is unchanged. The release gate and the Spanish-layer tests pass.
4. **Gate scope was re-scoped** at P4-999 (iteration 374/376) to the authored-files criteria; see `loop/blockers.md` and decisions-provisional.md.
5. **Tree-fence translation deferred** (H001 title survives in a verbatim tree fence).
6. **Part II (code localization) is not part of this candidate (no S tasks are in the queue);** frozen code, comments and output remain English.
7. **Nothing is pushed or tagged yet.** P6-004 creates the local tag only.
