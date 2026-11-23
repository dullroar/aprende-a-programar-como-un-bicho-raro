# Guide review (H3-001): TRANSLATING.md and TRADUCTORIO.md

Both guides were read together and checked against `loop/ralph.sh`, `loop/CONFIG.yaml`, `tools/model_report.py`, `loop/ledger/usage.jsonl` and `translation/reviews/part2-recall.md`.

## Verified as accurate (no change)

- Reciprocal links exist at the top of each guide; both files are in the repository root.
- One generic six-step workflow, one sample plan with acceptance evidence, one runner prompt and one adversarial prompt; Spanish mirrors English section by section.
- `--agent=claude|codex|copilot`, `--on-limit handoff` (exit 75 on a recognized limit), `--pause`, `--resume`, the lock and the consecutive-stall limit (`max_stalled_iterations`) all exist in `loop/ralph.sh`.
- Tier policy: light only for opted-in tasks or listed kinds, first attempt only, retries standard (CONFIG.yaml lines 42-48).
- Cross-provider run really happened: 195 codex/copilot iterations in the ledger, so the calibration-as-hypothesis wording stays.
- Ledger fields named in the guides (timing, outcome, token and cache counts, cost evidence, `unit_words`) are present; `cost_est_usd` is the credit estimate, `cost_usd` the provider figure.

## Fixes

| # | Guide text | Problem | Fix (both languages) |
| --- | --- | --- | --- |
| 1 | Light tier "such as packet assembly or routine regeneration" | CONFIG.yaml lists only `tier_light_kinds: packet`; "routine regeneration" was never configured | Name `packet` as this project's configured kind |
| 2 | Seeded-defect paragraph | The run's actual recall was not reported; a clean-looking threshold hid that the code review fell short (21/24 = 87.5% against a 95% bar, 1 of 4 clean controls flagged) | Added the result and the lesson: a check that runs the code in the target language covered the misses |
| 3 | Ledger section | `model_report.py` exit status 1 on mismatch and helper models in `models_all` (haiku inside sonnet iterations) were not mentioned and invite false mismatches | Added one warning sentence: compare the reported model |

## Not changed

- The "Working draft" banner stays until the independent adversarial review and maintainer sign-off.
- No cost ranking is added; costs remain provisional as the guides say.
