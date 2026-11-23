# Part II pilot review (task S4-004, iteration 419)

**Verdict: PASS for what exists; the pilot proves little about localized code.** All three pilot batches (S4-001 Forth, S4-002 C#/LINQ/XAML, S4-003 COBOL and regex-pcre2) left their families English and `NOT TESTED`, because docker is denied in dontAsk mode and so no oracle run is possible. There is no localized code to review, so the exact-span review covered the absence of change.

## Fresh-context review (exact-span rule)

Checked from the files, not from the batch reports:

- `python3 -I tools/lock_code.py --check`: ok. No protected file differs from the pinned English or from `localized-code.sha256`.
- `git diff --stat a445ba3 HEAD` shows only `loop/`, `translation/exception-register.jsonl` and `translation/part2/reports/S4-00[123]-*.md`. No `src/`, no PO entry, no identifier-map row, no README, diagram or anchor edit.
- EXC-539, EXC-540 and EXC-541 exist, and each report says `NOT TESTED` with the reason and the steps a Docker-capable session must run.
- `python3 -I tools/verify.py --fast`: OK.

Findings: none that need a `review-fix` task. Open item carried forward, not new: the oracle baseline for the pilot families is owed to a Docker-capable session (S0-003, S2-004 and S4-001 to S4-003 all depend on it).

## Seeded-fault recall (Part II fault classes)

No localized unit exists, so no model reviewer could be tested on real Part II translations. Recall was measured on the deterministic detectors, using the planted faults of `tools/part2_negative.py` (16/16 fixtures fail for their stated reason, each with a clean control) and `tools/test_link_audit.py` (10 anchor tests pass).

| Fault class | Fixture and detector | Caught | Reported reason |
| --- | --- | --- | --- |
| Translated keyword | `dotnet-list`, `sql-commit`, `m4-macro` (I29) | 3/3 | `protected token 'COMMIT' -> 'CONFIRMAR'` and similar |
| Stale identifier | `stale-symbol` (I28 sweep), `regex-capture`, `xaml-binding` (I28) | 3/3 | `stale symbol 'total' (renamed to 'suma')`; `not in the identifier map` |
| Flipped `>` | `stop-ge` and `stop-ge-differential` (oracle boundary property) | 2/2 | `stopped at 40, which is not strictly greater than 40` |
| Shifted `#Lnn` | `comment-adds-line` (loc_apply refusal); link_audit planted line shift (S3-002) | 2/2 | `not exactly one comment span`; semantic anchor mismatch |

Recall is 10/10 on the four classes, which meets the plan 9.3 bar of 95% for critical and major faults, and every flipped `>` is caught.

## Limits of this result

- The flipped-`>` fixtures run against the reference model in `tools/oracle.py`, not against a real program in the sandbox container. A container run is still owed.
- The model-reviewer recall test (`tools/recall_test.py`) was not re-run for Part II. It needs localized units and would cost model spend with nothing to review. Re-run it after the first real `localizing` family lands.
- Fixtures are authored by the same tool family as the detectors, so they show the detectors work on the planted shapes, not that no other shape slips through. Rows 10, 12 and 14 of Appendix A.2 stay DEFERRED.
