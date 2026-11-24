---
id: f03-lens-faults
status: pending
depends_on: [a02-jury-prompts, t02-jury-requests]
touches:
  - tools/lens_faults.py
  - tools/lens_routing.py
  - tools/test_lens_faults.py
  - tools/test_lens_routing.py
  - tools/fixtures/lens-faults/**
  - plans/v4-es-1b/steps/f03-lens-faults.md
lane: none
gate: python3 plans/v4-es-1/gatelib.py tests tools/test_lens_faults.py tools/test_lens_routing.py && python3 plans/v4-es-1/gatelib.py tests && python3 plans/v4-es-1/gatelib.py verify && python3 plans/v4-es-1/gatelib.py guard && git diff --check
agent: claude
claimed_by: ""
claimed_at: ""
evidence: ""
---
# Build the calibration set with a seeded fault for each lens, and the routing rule

Anomaly A10. Canaries test only L1, L2, L5, L6 and L8. The pilot needs a known fault for every lens.

## Change

- `tools/lens_faults.py build --seed 3 --out translation/work/calibration/`: pick 6 packets (2 critical prose, 1 high, 1 normal, 2 code) from a rebuilt packet set. Plant faults with fixed mutators, at least 3 for each lens, and write the key to `translation/work/calibration/key.json` (untracked). Use the mutators of `tools/jury_packet.py` and `tools/recall_test.py` for L1, L2, L5, L6 and L8. Add new mutators:
  - L3: replace a transcreated joke with a literal calque of the English.
  - L4: join two sentences into one over the sentence-length limit of `review/EDITION-FACTS.md`.
  - L7: change a number in a sample output so that the prose and the output disagree.
  - L9: weaken a sandbox warning ("debe" to "puede", or drop "solo en el sandbox").
  - L10: break an internal link target or a heading anchor.
  - L11: flip a comparison operator in Spanish code (`>` to `>=`) in a localized family.
  - L12: change a `#Lnn` source-line link to point at another line.
  - L13: rename an identifier in prose but not in code.
- `tools/lens_routing.py`:
  - `candidates --prices translation/batch-prices.yaml --budget plans/v4-es-1b/records/f02-operator-budget.md --out FILE`: a pilot routing that assigns every lens to every candidate juror model: `claude-haiku-5-5`, `claude-opus-5-5`, and the two OpenAI jurors of the budget record. Add `claude-fable-5-2` on L1 and L11 for one packet each, as a quality ceiling.
  - `score --results DIR --key FILE --prices translation/batch-prices.yaml --out review/calibration-<date>.md`: for each `(lens, model)`: recall of the seeded faults of that lens (a fault is caught only by an exact-quote finding at the changed place, as in `jury_ingest.py`), quote validity (exact-substring rate), format validity, findings per packet, cost per packet (exact, from usage), cache-read share.
  - `route --score FILE --out translation/review-routing.yaml`: for each lens pick the cheapest model with recall at or above 0.75 (`RELIABLE_RECALL` of `jury_ingest.py`), quote validity at or above 0.90 and format validity 1.0. If no model passes, assign the two best models from two vendors and mark the lens `weak: true`. Also write: `second_vendor_model` (the best OpenAI juror), `adjudicator: claude-opus-5-5`, `audit_model` (the best OpenAI juror), `fix_drafter` (the Opus model unless the score shows another that passes L1 and L5), `backtranslation_model`, `humor_panel_models` (two, from two vendors), `editorial_model`, `pdf_reviewer: claude-fable-5-2` and `pdf_fallback: claude-opus-5-5` (for the pages that Fable refused in the W0 probe: list them as `pdf_fallback_pages`).
  - `--check FILE`: every lens has a route, every role key is there, and no model is `excluded`. Never pick an `excluded` model.
- Tests for the mutators (each fault appears once, at the right place) and for the rule (a tie, no model passes, an excluded model).

## Do not change

- Files outside `touches`. The `gate`. `tools/jury_packet.py`, `tools/recall_test.py`, `tools/jury_ingest.py` (import from them).

## Record

Set `status: done`. Fill `evidence` with the gate command, the result and the date.
If you cannot finish, write "Resume notes" below. Keep the status `in_progress`.

## Resume notes

(none)
