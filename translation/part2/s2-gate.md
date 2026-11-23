# S2 gate (iteration 412, task S2-007)

Scope: Part II checks and tools built in S2-001 to S2-006.

## Evidence

- `tools/part2_negative.py`: 16 of 16 planned A.2 fixtures fail for their stated reason, each with a clean control. Rows 10, 12 and 14 are DEFERRED (no detector yet), not counted.
- `tools/part2_inv.py` (I28 to I31) has a failing fixture per check (S2-005 tests).
- `tools/lock_code.py --verify`: 230 frozen files match the manifest and the English clone. The scope file and localized hashes are in force; the unscoped, unmapped and unrecorded negatives passed in S2-003.
- No existing check was weakened. One repair was needed at the gate: `lessons/book/book.es.css` (added in S2-003) was classified as both tooling and owned, so `inventory.py --check`, the path map and two path tests failed in `verify --release`. Fix: `tools/inventory.py` now treats it as owned only (excluded from the tooling pattern), and `tools/pathmap.py --write` regenerated the map. No test or expected value was edited.
- Tooling allowlist: new tooling files carry their task ids from S2-001 to S2-006; no new tooling file was added in this task.

## Not proved

- The Docker self-test and real container oracle runs stay NOT TESTED (docker denied in dontAsk mode).
- A.2 rows 10, 12 and 14 stay deferred.
