# END-REVIEW (regenerated iteration 544, task G1-009)

Local release candidate: `v4-es.0-rc3` (local tag, not pushed; earlier candidates `v4-es.0-rc1`, `v4-es.0-rc2`). Branch `loop/es-v4`. English source pinned at `48a4429c0a22b2aac628b256a50c07d1816bcb80`. Nothing is published. This file points to the evidence; it does not repeat it.

## Where things stand

- Queue: all tasks done through G1-009 (196 done, 0 blocked). Earlier blocks (`P5-001`, `P4-999`, `P4-lessons-languages-5`) were resolved; see `loop/blockers.md`.
- Gates passed: P0 to P5, S0 to S8, F2 and G1 follow-ups (Part II gate files under `translation/part2/`). P6 and P7A are not marked in `STATE.md` as gates; the rc reports and the 7A packet build cover them in practice. A human should confirm.
- Last full checks (G1-009): `verify --release --no-gates` OK; `lock_code --verify` OK (230 frozen files); `part2_inv --check` 0 findings; no file mixes English and Spanish category forms (I13).

## 1. Provisional decisions

`loop/decisions-provisional.md` holds every default the loop took (each with alternatives and cost to reverse). Review these first:

- Iteration 387 "Alive"/"Vivo": answered by Jim on 2026-11-23 (keep Vivo).
- Iterations 373 (Phase 4 gate scope) and 378 (generated blocks in Spanish files): approved by Jim.
- Decision 11 (the four card categories as `Reuniones`, `Programación`, `Depuración`, `Aprendizaje`), applied by S4-007, F2 and G1.
- S7-002: finding F6 (minor) deferred.
- P7-001: packets and canary key kept untracked (see section 9).

## 2. Blocked tasks

None.

## 3. Exceptions (`translation/exception-register.jsonl`, 593 rows)

- Part II families left English and marked **NOT TESTED**: Docker denied in unattended mode, image builds need network, no oracle runner for `lessons/solutions` and book tooling, WPF entries without an entry image, `regex-dotnet` and `regex-pcre2` oracles fail on the English baseline itself (EXC-541, 547 to 549, 555 to 559, 562, 571, 573, 578).
- Comments: families that could be tested are `localizing`, comments only, oracle PASS.
- Categories: localized in every family that passes the oracle in Spanish. G1 widened the `[A-Za-z]` classes (`A-Za-zÁÉÍÓÚáéíóúñ`) in ed-weird, regex-pcre2grep, regex-perl, regex-sed and tar-gnu (EXC-588, 590 to 593 resolved). **ex-weird stays English** (EXC-589): nvi fails the oracle on accented categories and the locale is frozen.
- No identifier was renamed (`translation/identifier-map.jsonl` is empty).
- A native-voice pass (S7-001/002) changed 36 "desafío" to "reto" in 27 files.
- The docker self-test is still owed to a Docker-capable session (`translation/part2/runtime-matrix.md`).

## 4. Humor register

`translation/humor-register.jsonl`: 175 playful segments translated by effect. A native speaker should spot-check a sample for tone.

## 5. Glossary changes

`translation/glossary.es.yaml`: assurance labels, the timecard rule and phase macros are frozen. `git log -p translation/glossary.es.yaml` shows the changes.

## 6. Recall numbers

- English-side pilot: `translation/reviews/pilot-recall.md`, `pilot-breakage.md`.
- Part II deterministic detectors: 10/10 seeded-fault recall, 16/16 negative fixtures fail for their stated reason (`translation/reviews/part2-pilot.md`).
- Model reviewer on localized code (G1-008, `translation/reviews/part2-recall.md`): 21/24 = 87.5%, below the 95% bar; all 3 misses are regex classes narrowed back to ASCII, so rely on the Spanish oracle for those. 1 of 4 clean controls was flagged.

## 7. Ledger

- Cost ledger: `loop/ledger/usage.jsonl`; `python3 tools/model_report.py`. Last driver-reported figure: $112.64 of $150 through iteration 274; Codex session cost unavailable, so the true total is higher and unknown.
- Identifier ledger: empty by design (no renames).

## 8. Tooling changes worth knowing

Part II: `tools/loc_map.py`, `loc_apply.py` (now accent-safe class widening), `oracle.py`, `part2_inv.py`, `part2_negative.py`, `token_registry.py`, `token_audit.py`, `link_audit.py`, `impact.py`, `categories.py`, `code_inventory.py`, `recall_test.py --code`; `lock_code.py` has a second (localized) lock. `fit_tier` in `tools/jury_packet.py` measures render overhead.

## 9. Review packets (stage 7A)

69 packets, 540 canaries across 8998 units (built at P7-001/002, before the F2 and G1 changes; rebuild them before sending). **Untracked on purpose:** `review/packets/`, `review/repo-bundle.zip`, `review/canaries.key.json`, `review/units.index.jsonl`, `review/ADVERSARIAL-REVIEW-PROMPT.md`. Public: `review/MANIFEST.md`, `review/EDITION-FACTS.md`. Ingest feedback with `tools/jury_ingest.py` (adds `review-fix` tasks, removes `loop/DONE`).

## 10. For a native speaker

- Tone of the 175 humor segments; whether "reto" reads naturally throughout.
- Link audit: 33 broken (29 in `cs-source`, resolved after generation; the rest triaged in `translation/part2/s8-gate.md`), 578 unverified; HTML/PDF/EPUB audit not executed.
- 26 source issues in `translation/source-issues.md`, including SI-027.
- Part II comments in the localized families (sentence length, register) and the accented category words in code output.
- The Spanish editorial feedback in `review/inbox/chatgpt-editorial-2026-11-20.md`.
- The English gates were not run after the F2 and G1 changes.
