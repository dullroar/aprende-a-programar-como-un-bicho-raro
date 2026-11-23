# END-REVIEW (iteration 494, task P7-003)

Local release candidate: `v4-es.0-rc2` (tag on 23e837a, not pushed). Branch `loop/es-v4`. English source pinned at `48a4429c0a22b2aac628b256a50c07d1816bcb80`. Nothing is published. This file points to the evidence; it does not repeat it.

## Where things stand

- Queue: 190 tasks done, 0 blocked, 0 skipped. P7-003 (this task) is the last one. `P5-001`, once blocked by the I13 conflict, was resolved by P5-000 (generator-owned lines skipped by verification).
- Gates passed: P0 to P5, S0 to S8 (Part II gate files under `translation/part2/`, final one `s8-final-gate.md`). P6 and P7A are not marked in `STATE.md`; the rc2 report and the 7A packet build cover them in practice. A human should confirm.
- Last full checks (S8-007): `verify --release` OK (88 checks, double build identical); `lock_code --verify` OK (230 frozen files); `part2_inv --check` 0 findings.

## 1. Provisional decisions

`loop/decisions-provisional.md` holds every default the loop took (about 25 entries, each with alternatives and cost to reverse). Review these first:

- Iteration 387 "Alive"/"Vivo" question (open, for Jim).
- Iteration 373 (Phase 4 gate scope) and 378 (generated blocks in Spanish files): both approved by Jim.
- S4-006 / S4-007 (Part II planning; decision 11, the four card categories as `Reuniones`, `Programación`, `Depuración`, `Aprendizaje`).
- S7-002: finding F6 (minor) deferred.
- P7-001: packets and canary key kept untracked (see section 9).

## 2. Blocked tasks

None at the end. Historic blocks (P4-lessons-languages-5 acceptance command, P4-999 gate scope, P5-001) are recorded in `loop/blockers.md` and were all resolved.

## 3. Exceptions (`translation/exception-register.jsonl`, 586 rows)

- 15 of 45 Part II families were left English and marked **NOT TESTED** (EXC-541, 547 to 549, 555 to 559, 562, 571, 573, 578 and others). Causes: Docker denied in unattended mode, image builds need network, no oracle runner for `lessons/solutions` and book tooling, WPF entries without an entry image, `regex-dotnet` and `regex-pcre2` oracles fail on the English baseline itself.
- 30 families are `localizing`, comments only, oracle PASS. No identifier was renamed (`translation/identifier-map.jsonl` is empty); category words and display strings stayed English everywhere (so no file mixes forms).
- A native-voice pass (S7-001/002) changed 36 "desafío" to "reto" in 27 files.
- The docker self-test is still owed to a Docker-capable session (`translation/part2/runtime-matrix.md`).

## 4. Humor register

`translation/humor-register.jsonl`: 175 playful segments translated by effect. A native speaker should spot-check a sample for tone.

## 5. Glossary changes

`translation/glossary.es.yaml` has 7 commits of history. Assurance labels, the timecard rule and phase macros are frozen. `git log -p translation/glossary.es.yaml` shows the changes.

## 6. Recall numbers

- English-side pilot: `translation/reviews/pilot-recall.md`, `pilot-breakage.md`.
- Part II deterministic detectors: 10/10 seeded-fault recall on four classes, 16/16 negative fixtures fail for their stated reason (`translation/reviews/part2-pilot.md`).
- **Not re-run:** the model-reviewer recall test (`tools/recall_test.py`) for Part II, because it needs localized units and costs spend. Re-run it before trusting a jury on code comments.

## 7. Ledger

- Cost ledger: `loop/ledger/usage.jsonl`; `python3 tools/model_report.py`. Last driver-reported figure: $112.64 of $150 through iteration 274; Codex session cost unavailable, so the true total is higher and unknown.
- Identifier ledger: empty by design (no renames).

## 8. Tooling changes worth knowing

New in Part II: `tools/loc_map.py`, `loc_apply.py`, `oracle.py`, `part2_inv.py`, `part2_negative.py`, `token_registry.py`, `token_audit.py`, `link_audit.py`, `impact.py`, `categories.py`, `code_inventory.py`; `lock_code.py` gained a second (localized) lock. P7-001 changed `fit_tier` in `tools/jury_packet.py` to measure render overhead (2 new tests).

## 9. Review packets (stage 7A)

69 packets, largest 23793 tokens, 540 canaries across 8998 units (6.0%). Rebuilt deterministically (seed 1). **Untracked on purpose:** `review/packets/`, `review/repo-bundle.zip`, `review/canaries.key.json`, `review/units.index.jsonl`. Copy of the prompt: `review/ADVERSARIAL-REVIEW-PROMPT.md` (untracked). Public: `review/MANIFEST.md`, `review/EDITION-FACTS.md`. Ingest feedback with `tools/jury_ingest.py` (adds `review-fix` tasks, removes `loop/DONE`).

## 10. For a native speaker

- Tone of the 175 humor segments; whether "reto" reads naturally throughout.
- Unresolved link audit: 33 broken (29 in `cs-source`, which resolve after generation; the rest triaged in `translation/part2/s8-gate.md`), 578 unverified; HTML/PDF/EPUB audit not executed.
- 26 source issues in `translation/source-issues.md`, including SI-027 (two unfenced tokens kept as in English).
- Part II comments in the 30 localized families (sentence length, register).
- The Spanish editorial feedback already in `review/inbox/chatgpt-editorial-2026-11-20.md`.
