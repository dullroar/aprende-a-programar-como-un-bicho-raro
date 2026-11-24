---
gist: "Read me when: you touch the review jury, packets, canaries, the recall test, or you commit anything under review/."
---

# Review jury, packets and canaries

## Fact

- Never commit `review/packets/`, `review/repo-bundle.zip`, `review/canaries.key.json` or `review/units.index.jsonl`. They carry canaries or the key. Commit only the public `MANIFEST.md` and `EDITION-FACTS.md`.
- Keep canary data (rate, ids, fragments) out of every public review file (packets, `manifest.json`, `EDITION-FACTS.md`, bundle).
- After you touch `tools/jury_packet.py`, run `python3 -I tools/test_jury_packet.py` and `python3 -I tools/test_jury_ingest.py`. Check quotes in ingest against the text as shown (`units.index.jsonl`), never the original Spanish.
- Code jury units use ids `c-<hash>-NNNN`. Canary quotas are per group (code and prose). A test that needs an uncanaried code unit must give the file two differing 60-line chunks.
- Check packet sizes on the rendered text (manifest tokens), never on chunk estimates. The chunker ignores facts, glossary and Part II context. So `fit_tier` lowers the cap by the measured overhead.
- Recall test: `python3 -I tools/recall_test.py --run` (about 60 `claude -p` calls, about 2 USD). It resumes from `translation/work/recall/replies.jsonl`. `--rescore` makes no call. Run it in the background without shell redirects. Enforce a spend cap inside the worker, not in the consumer of `executor.map`.
