# S5-fam-javachallenge1 batch report: src/JavaChallenge1

Iteration 444. Verdict: **NOT TESTED. Family left English (EXC-559).**

## Why nothing changed

- The entry Dockerfile builds with Gradle and downloads the Gradle distribution and Maven dependencies, so it needs `sandbox/container/run-image.sh --online-build`. Hard rule 2 forbids network calls.
- `python3 -I tools/oracle.py --entry src/JavaChallenge1 --english /home/lehmer/english-source` reports NOT TESTED: "sandbox refused to build or run".
- Without a run there is no equivalence proof for the 203 comments (hard rule 1), so the family stays English. `translation/localization-scope.yaml` keeps it `frozen`; no protected file changed.

## Follow-up

Pre-build the image online in a session that may use the network, then localize comments with `tools/loc_apply.py` and rerun the oracle.
