# S5-fam-rustchallenge1 batch report: src/RustChallenge1

Iteration 459. Verdict: **NOT TESTED. Family left English (EXC-573).**

## Why nothing changed

- The entry Dockerfile builds with `cargo build --release --locked`, which downloads the locked crates, so it needs `sandbox/container/run-image.sh --online-build`. Hard rule 2 forbids network calls.
- `python3 -I tools/oracle.py --entry src/RustChallenge1 --english ~/english-source` reports NOT TESTED: "sandbox refused to build or run".
- Without a run there is no equivalence proof for the 54 comments (hard rule 1), so the family stays English. `translation/localization-scope.yaml` keeps it `frozen`; no protected file changed.

## Follow-up

Pre-build the image online in a session that may use the network, then localize comments with `tools/loc_apply.py` and rerun the oracle.
