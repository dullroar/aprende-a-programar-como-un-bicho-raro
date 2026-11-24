# Part II baseline (S0-001)

Recorded by iteration 394 before any Part II change. This is the state that Part II must leave untouched unless a task says otherwise.

## Release candidate

- Local annotated tag: `v4-es.0-rc1` (exists locally; not pushed).
- Tag object points at commit `a901b7238fcc739c51763623cdafeee821f3e3d4` (P6-003 release report).
- Tree of that commit: `e037c3b2af02ef2d3852363f8517f0e615d78c02`.
- Commit at start of this iteration: `d57a37a` (P6-004 tag record). Its diff against the tagged tree touches only `loop/` bookkeeping files (`loop/STATE.md`, `loop/log.md`, `loop/queue/seed.jsonl`). No translated or protected file differs from the tag.

## English source

- Pinned English commit: `48a4429c0a22b2aac628b256a50c07d1816bcb80`.
- The English clone at `~/english-source` is at that commit.

## Frozen-file lock

- `python3 -I tools/lock_code.py --verify`: ok, 230 frozen files match the manifest and the English clone agree.
- SHA-256 of `translation/locked-code.sha256`: `fb6f8960b231c8abafa32665d36196768af4c768bf5daa95bf74ef4e25048259`.

## Release gate

- `python3 tools/verify.py --release` on the working tree: OK, 75 checks, 410.8 s. Includes the double-build check (identical hashes) and the release-a and release-b gates.

## Scope of this baseline

- Part II has not started. No protected file has changed since the tag.
- Gate for any later `S` task: the tree must still pass `lock_code --verify` and `verify --release` after its change, except where the Part II rules in plan section 4.5 allow a protected file to change through `tools/loc_apply.py` with oracle proof.
