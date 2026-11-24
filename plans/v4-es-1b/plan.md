---
gist: "Read me when: you run or change the batch-first plan that finishes the review of the Spanish edition: anomaly fixes, model calibration, the batch Jury, adjudication, fixes, the Fable PDF review and the hand-off to human editors. It supersedes v4-es-1."
---

# Plan `v4-es-1b`: batch-first review of the Spanish edition

This file is the high-level plan. The detail is in `steps/`. Every step is self-contained. Read this file for the shared facts.

## Why a new plan

`v4-es-1` has 28 steps. All are `pending`. Its review lanes have three problems:

1. The batch tool cannot send review requests (see A1 to A3 below). Step `j02` of `v4-es-1` cannot pass as written.
2. Three operator steps need people that the project does not have: a native-speaker humor reader (`h01`), outside jurors that Jim runs by hand (`j04`), and Jim's decisions on Spanish text that he cannot read (`j07`).
3. The interactive agent work hits the five-hour usage windows of the subscription. Batch work does not.

This plan keeps the goals of `v4-es-1`. It moves every review pass that a model can do to batch jobs, and it keeps Claude Code agents for judgment in the repository. It ends with a hand-off package for human editors. Publication moves to a later plan.

## Approach

- **Three executors.** `script` steps build requests and import results. Batch jobs do the reading. Claude Code agents (`agent: claude`) write tools and do the fixes that need judgment. No step uses Codex, Copilot or a local model.
- **Waves.** Batch work runs in waves W0 to W6. A wave is: a `script` step writes tickets to the outbox, the submitter sends them, a wait step (`w*`) passes when every result is collected and reconciled, and a `script` step imports the results. Each wave has a 24-hour completion window on both APIs. Most batches finish much sooner.
- **The submitter holds the keys.** `tools/batch_submitter.py` (step s01) is the only program that reads `ANTHROPIC_API_KEY` or `OPENAI_API_KEY`. Jim runs it from the operator shell on a timer (`--once` every 10 minutes). It submits only a ticket whose estimate fits the approved cap of its wave in `records/f02-operator-budget.md`, and it refuses to go over the program cap. Agents never see a key. Do not start the Ralph driver with a key in its environment: Claude Code uses `ANTHROPIC_API_KEY` when it is set, so agent steps would bill the API account instead of the subscription (check this on the installed Claude Code version).
- **Laptop sleep does not stop a wave.** The batch runs on the vendor side. Results stay available for days. The submitter collects them when the laptop wakes.
- **Model separation.** The translator and the in-loop reviewer were `claude-sonnet-5-5`. Sonnet 5.5 is never a juror, an adjudicator or a fix drafter in this plan. A juror never adjudicates its own findings. Round-two verification of a fix uses a model other than the one that drafted the fix.
- **Calibration before spend.** Wave W0 is a pilot on a small calibration set with seeded faults for each lens. A deterministic rule picks, for each lens, the cheapest model that meets the bar. The full matrix (W1) then uses that routing.
- **Full matrix.** Every prose packet gets every prose lens (L1 to L10). Every code packet gets L11 to L13. Every critical packet gets a second juror from the other vendor on L1, L2 and L9.
- **Cache layout.** One request is: system block (master prompt, cached) → packet block (cached) → lens block (not cached). All lenses of one packet share the first two blocks, and they go in the same batch, next to each other. Use the 1-hour cache lifetime for batches. Cache hits in a batch are best-effort, so every estimate and cap uses the uncached price.
- **Humans at the end.** Where `v4-es-1` needed a native speaker, an AI panel decides now and the result is marked `provisional`. The human editors see every provisional item in the hand-off package.

## Anomalies found (2026-11-24) and the step that fixes each

| ID | Anomaly | Fix |
| --- | --- | --- |
| A1 | `tools/batch.py build` accepts only segment IDs of the form `s-<12 hex>-<4 digits>` (`SEG_RE`). Jury rows use `P-critical-01.L1`. `build`, `submit` and `collect` reject them. Step `g02` of `v4-es-1` forbids a change to `batch.py`. | a03 |
| A2 | `build_system()` always puts the translator batch wrapper (`translation/prompts/batch-translate.md`: "answer with a translator_output"), the house style and the glossary in front of the prompt. A juror request would get translator instructions. | a03 |
| A3 | Only the system block has `cache_control`. The packet (about 19 000 tokens, shared by up to 10 lenses) is in the user message and is not cached. Cost records count all input at the input price, with no cache-read or cache-write fields. | a03 |
| A4 | `v4-es-1` reads the lenses from `review/ADVERSARIAL-REVIEW-PROMPT.md`. That file is an untracked copy (loop task P7-002), so a linked worktree does not have it, and every tool or gate that reads it fails there. The tracked source is `ralph-kit-es/ADVERSARIAL-REVIEW-PROMPT.md`. Its "For Jim" section is not part of the prompt. `ralph-kit-es/README.md` says "ten lens modules"; the file has 13. | a02 |
| A5 | `review/inbox/chatgpt-editorial-2026-11-20.md` is a free-form review (no `juror_model` header, no `batch-` or `outside-` prefix). `jury_ingest.py` reports "no header line" for it. It reviews commit `22e3a5f`, which is 505 commits before `55ab941`. Its items are not triaged. | a05, t07, e01 |
| A6 | The Anthropic models that are not loop models are Haiku 5.5, Opus 5.5 and Fable 5.2. The cheap middle model (Sonnet 5.5) is excluded. The ladder is therefore Haiku 5.5, then Opus 5.5 (40 times the batch input price), then Fable 5.2. | f05 (routing rule) |
| A7 | `v4-es-1` step `j04` needs at least five jurors from at least three vendors. The project has credits on two vendors. | f02 (decision D1) |
| A8 | The Windows checkout (the folder that was shared for this plan) has no `loop/STOP`, no packets, no `translation/work/` and no canary key. A Linux `git` sees 457 tracked files as changed there: CRLF in the working files, because `.gitattributes` forces LF only for `src/**`. If the driver runs on this checkout from WSL, `git diff --check`, the `touches` check and the `untracked` gate see every one of those files. The plan assumes that the operator checkout is a different, clean clone. | a01 |
| A9 | `translation/source.json` still holds a home path in `english_clone_path`, after the merge that scrubbed home paths. Rule 1 of `AGENTS.md` forbids personal paths in tracked files. Rule 7 forbids a change to the pin. | a01 (Jim decides) |
| A10 | Canary mutators (`recall_test.py`, `jury_packet.py`) cover the 40-rule, negation, numbers, dropped clauses, card categories, assurance labels, phase letters and the `usted` slip. They cover L1, L2, L5, L6 and L8. They do not test L3, L4, L7, L9, L10, L11 or L13. Canary recall alone cannot pick a model for those lenses. | f03 |
| A11 | Fable 5.2 has extra safety measures for cybersecurity. The book is about adversarial programs, weird machines and arbitrary code execution. Fable can refuse some pages. | W0 probe in f04 |
| A12 | `batch.py` has a program cap of USD 100 for all submissions. It does not know OpenAI. | a04, s01, f02 |

## Models and prices (facts from the Anthropic pricing page, read 2026-11-24)

Batch prices in USD per million tokens. The Batch API discount (50 %) and the prompt-cache multipliers stack. The cache-read price in a batch below is derived (batch input × the cache-hit multiplier of the model). Check it against the first cost records.

| Model | Role in this plan | Batch input | Batch output | Cache read (derived) |
| --- | --- | --- | --- | --- |
| `claude-haiku-5-5` | Default juror, back-translation, humor panel | 0.05 (prompt up to 100K tokens) | 0.25 | 0.005 |
| `claude-opus-5-5` | Juror where Haiku fails the bar, adjudicator, fix drafter | 2 | 10 | 0.10 |
| `claude-fable-5-2` | PDF review only (and a W0 probe) | 4 | 20 | 0.10 |
| `claude-sonnet-5-5` | Excluded: the translator's model | — | — | — |

Haiku 5.5 costs five times more above 100K prompt tokens. Every request in this plan stays under 100K tokens (packets are about 17 000 to 24 000 tokens).

OpenAI: f02 fills model IDs and prices in `translation/batch-prices.yaml` from the OpenAI pricing page. Sources disagree on whether OpenAI applies the cache discount to batch requests. W0 measures it (`cached_tokens` in the usage block).

## Cost estimate (inference, not a quote)

W1 has about 630 requests: 55 prose packets × 10 lenses, 14 code packets × 3 lenses, and 13 critical packets × 3 lenses from the second vendor. At about 26 000 input and 4 000 output tokens each, that is about 16 million input and 2.5 million output tokens.

| W1 routing | Uncached upper bound | With cache hits |
| --- | --- | --- |
| All Haiku 5.5 | about USD 1.5 | about USD 0.8 |
| All Opus 5.5 | about USD 58 | about USD 35 |
| Mixed (expected after W0) | USD 10 to 30 | lower |

Other waves (estimates): W0 pilot USD 5 to 10, W2 adjudication USD 5 to 15, W3 and W6 fix drafts USD 2 to 10, W4 verification USD 2 to 5, W5 Fable on 667 PDF pages (410 + 246 + 11) USD 15 to 30. The submitter enforces the real caps. f04 and each wave build step record a dry-run estimate.

## Waves and the 24-hour SLA

| Wave | Content | Build step | Wait step | Import step |
| --- | --- | --- | --- | --- |
| W0 | Pilot: lens × candidate models on the calibration set, plus a Fable probe | f04 | w0 | f05 |
| W1 | Full Jury matrix, editorial triage, humor panel, back-translation of the critical tier | j02, e01, h01, b01 | w1 | j03, h02 |
| W2 | Adjudication of all findings (Opus 5.5) and a cross-vendor audit sample | j04 | w2 | j05 |
| W3 | Minimal-edit fix drafts for accepted prose findings and humor transcreations | j07 | w3 | j08 |
| W4 | Round-two verification of every changed unit | j09 | w4 | j10 |
| W5 | Fable review of the three PDFs | p03 | w5 | p04 |
| W6 | Fix drafts for accepted Fable findings | p06 | w6 | p07 |

W1 is the bulk of the review: all lenses for all segments in one 24-hour window. Agent-heavy work (lanes a, t, s, f03, p01 and the generated `fix-*` steps) is the part that meets the five-hour windows. Start those lanes right after a window resets. The batch waves run in the rest periods.

## Steps

| Step | Executor | Goal | Depends on |
| --- | --- | --- | --- |
| [a00-retire-v4-es-1](./steps/a00-retire-v4-es-1.md) | agent, light | Mark `v4-es-1` superseded. Remove its step files. Keep its gate helper. | none |
| [a01-operator-checkout](./steps/a01-operator-checkout.md) | operator | Confirm the operator checkout, the English clone, `loop/STOP`, the clean tree. Decide A9. | none |
| [a02-jury-prompts](./steps/a02-jury-prompts.md) | agent, light | Tracked master prompt and 13 lens files from `ralph-kit-es/`, with a checker. | none |
| [a03-batch-review-kind](./steps/a03-batch-review-kind.md) | agent | `batch.py`: a `review` kind, prompt manifests, cache blocks, 1-hour cache, exact cost fields. | none |
| [a04-batch-openai](./steps/a04-batch-openai.md) | agent | `tools/batch_openai.py`: the same contract on the OpenAI Batch API. | a03 |
| [a05-editorial-move](./steps/a05-editorial-move.md) | agent, light | Move the free-form ChatGPT review out of the inbox. | none |
| [f01-price-table](./steps/f01-price-table.md) | agent, light | `translation/batch-prices.yaml` and its checker. | none |
| [s01-submitter](./steps/s01-submitter.md) | agent | `tools/batch_submitter.py`: outbox, caps, submit, poll, collect, reconcile, one retry. | a03, a04, f01 |
| [t01-lane-tools](./steps/t01-lane-tools.md) | agent | `fix_steps.py`, `inbox_check.py`, `jury_gate.py` (old g01, adapted). | a05 |
| [t02-jury-requests](./steps/t02-jury-requests.md) | agent | `jury_requests.py`: matrix tickets from the routing file, and the inbox writer. | a02, a03 |
| [t03-humor-tools](./steps/t03-humor-tools.md) | agent | `humor_panel.py` and `humor_ingest.py`. | a03 |
| [t04-fix-requests](./steps/t04-fix-requests.md) | agent | `fix_requests.py`: fix tickets and the import through `translate.py` checks. | a03, t01 |
| [t05-adjudication](./steps/t05-adjudication.md) | agent | `adjudicate_requests.py`: adjudication tickets, audit sample, apply, English memo. | a03, t01 |
| [t06-backtranslation](./steps/t06-backtranslation.md) | agent, light | `backtranslate_requests.py`: blind back-translation tickets for the critical tier. | a03 |
| [t07-editorial-triage](./steps/t07-editorial-triage.md) | agent, light | `editorial_triage.py`: one ticket for each item of the ChatGPT review. | a03, a05 |
| [t08-pdf-review](./steps/t08-pdf-review.md) | agent | `pdf_review.py`: page chunks, Fable tickets, ingest that finds file and line. | a03 |
| [f02-operator-budget](./steps/f02-operator-budget.md) | operator | Jim fills OpenAI prices, wave caps and decisions D1 to D6. Jim starts the submitter timer. | a01, f01, s01 |
| [f03-lens-faults](./steps/f03-lens-faults.md) | agent | Calibration set with seeded faults for each lens, and the routing rule. | a02, t02 |
| [j01-packets](./steps/j01-packets.md) | script | Build the packets twice, record the digest, check for leaks. | a01 |
| [f04-pilot-build](./steps/f04-pilot-build.md) | script | W0 tickets: lens × candidate models, plus the Fable probe. | f02, f03, t08, j01 |
| [w0-pilot-wait](./steps/w0-pilot-wait.md) | wait | W0 collected and reconciled. | f04 |
| [f05-pilot-score](./steps/f05-pilot-score.md) | script | Score W0. Write `translation/review-routing.yaml`. | w0 |
| [j02-wave1-jury](./steps/j02-wave1-jury.md) | script | W1 tickets: the full Jury matrix. | f05, j01 |
| [e01-wave1-editorial](./steps/e01-wave1-editorial.md) | script | W1 tickets: triage of the ChatGPT review. | f05, t07 |
| [h01-wave1-humor](./steps/h01-wave1-humor.md) | script | W1 tickets: the humor panel (replaces the native reader). | f05, t03 |
| [b01-wave1-backtranslate](./steps/b01-wave1-backtranslate.md) | script | W1 tickets: back-translation of the critical tier. | f05, t06, j01 |
| [w1-wave1-wait](./steps/w1-wave1-wait.md) | wait | W1 collected and reconciled. | j02, e01, h01, b01 |
| [j03-ingest](./steps/j03-ingest.md) | script | Write the inbox replies, ingest, report and findings with canary recall. | w1, t01 |
| [h02-humor-ingest](./steps/h02-humor-ingest.md) | script | Provisional humor decisions from the panel and the L3 findings. | w1, j03 |
| [j04-wave2-adjudicate](./steps/j04-wave2-adjudicate.md) | script | W2 tickets: adjudication and the cross-vendor audit sample. | j03, t05 |
| [w2-wave2-wait](./steps/w2-wave2-wait.md) | wait | W2 collected and reconciled. | j04 |
| [j05-adjudication-apply](./steps/j05-adjudication-apply.md) | script | Apply statuses. Write the English decision memo for Jim. | w2 |
| [j06-human-decisions](./steps/j06-human-decisions.md) | operator | Jim decides the `needs-human` items from the English memo. | j05, h02 |
| [j07-wave3-fixes](./steps/j07-wave3-fixes.md) | script | W3 tickets: fix drafts and humor transcreations. | j06, t04 |
| [w3-wave3-wait](./steps/w3-wave3-wait.md) | wait | W3 collected and reconciled. | j07 |
| [j08-fix-import](./steps/j08-fix-import.md) | script | Import drafts with all checks. Write `fix-*` agent steps for failures and code. | w3 |
| [j09-wave4-verify](./steps/j09-wave4-verify.md) | script | W4 tickets: round-two verification of changed units. | j08 (and all `fix-*` by its gate) |
| [w4-wave4-wait](./steps/w4-wave4-wait.md) | wait | W4 collected and reconciled. | j09 |
| [j10-round-two-ingest](./steps/j10-round-two-ingest.md) | script | Ingest W4. Write `fix-r2-*` steps for any new critical or major finding. | w4 |
| [j11-gate-7](./steps/j11-gate-7.md) | script | Gate 7 and `verify.py --release --no-gates`. | j10 (and all `fix-r2-*` by its gate), h02 |
| [p01-context-pack](./steps/p01-context-pack.md) | agent | The English brief for Fable: purpose, audience, rules, decisions, what not to report. | t08, j05 |
| [p02-candidate-build](./steps/p02-candidate-build.md) | script | Double build of the PDFs and EPUBs. Record the hashes. | j11, u01, x01 |
| [p03-wave5-fable](./steps/p03-wave5-fable.md) | script | W5 tickets: Fable reads the three PDFs. | p01, p02 |
| [w5-wave5-wait](./steps/w5-wave5-wait.md) | wait | W5 collected and reconciled. | p03 |
| [p04-fable-ingest](./steps/p04-fable-ingest.md) | script | Fable report with PDF page and verified file and line. | w5 |
| [p05-fable-decisions](./steps/p05-fable-decisions.md) | operator | Jim confirms the routing of the Fable findings (fix, reject, editors). | p04 |
| [p06-wave6-fixes](./steps/p06-wave6-fixes.md) | script | W6 tickets: fix drafts for the accepted Fable findings. | p05, t04 |
| [w6-wave6-wait](./steps/w6-wave6-wait.md) | wait | W6 collected and reconciled. | p06 |
| [p07-fix-import](./steps/p07-fix-import.md) | script | Import with all checks. Write `fix-p-*` steps for failures. | w6 |
| [p08-final-build](./steps/p08-final-build.md) | script | Final double build, release check, diff against p02. | p07 (and all `fix-p-*` by its gate) |
| [z01-editor-pack](./steps/z01-editor-pack.md) | agent, light | `review/editors/`: brief, PDFs to read, provisional items, Fable suggestions, feedback format. | p08 |
| [z02-send-to-editors](./steps/z02-send-to-editors.md) | operator | Jim sends the package and records it. | z01 |
| [u01-approve-guides](./steps/u01-approve-guides.md) to [u05-adopt-upstream](./steps/u05-adopt-upstream.md) | as in `v4-es-1` | Upstream package lane, unchanged. | as in `v4-es-1` |
| [c01-synthetic-delta](./steps/c01-synthetic-delta.md) to [c05-retrospective](./steps/c05-retrospective.md) | as in `v4-es-1` | Cookbook rehearsal lane. c03 may use the submitter. c05 now waits for j11. | as in `v4-es-1` |
| [x01-translation-pack](./steps/x01-translation-pack.md) | agent | Controls translation pack, unchanged. | none |

Generated steps: j08 writes `fix-po-*` and `fix-code-*`, j10 writes `fix-r2-*`, p07 writes `fix-p-*`. Each depends on its generator. The next step in the chain does not list them in `depends_on`. Its gate runs `python3 tools/fix_steps.py --all-done plans/v4-es-1b --prefix <prefix>`.

## Operator touchpoints

Jim does six things. Each one is in English. The rest of his time is not needed.

1. a01: confirm the operator checkout and answer A9.
2. f02: fill the OpenAI rows of the price table, set the wave caps, answer D1 to D6, start the submitter timer.
3. j06: decide the `needs-human` items from `review/human-decisions-<date>.md` (English: source, back-translation, claim, adjudicator view, options).
4. p05: confirm or change the routing of the Fable findings.
5. u01 and u03 (upstream lane, as before), and c03 (the small rehearsal batch; the submitter can do the submission).
6. z02: send the package to the editors.

The wait steps `w0` to `w6` need no human action. They pass when the submitter has collected the wave. Look at them only if one waits more than 24 hours.

## Decisions for Jim (answer in f02)

- **D1. Vendors.** Accept two vendors (Anthropic non-loop models and OpenAI) and at least five distinct juror models, in place of three vendors. Proposed: yes.
- **D2. Caps.** Anthropic program cap: keep USD 100 (`PROGRAM_CAP_USD` in `batch.py`) or set a new value. OpenAI cap: proposed USD 40. Caps for each wave.
- **D3. Humor.** The AI panel decides the humor register now, marked `provisional`. The human editors have the last word. Gate 7 accepts provisional decisions. Proposed: yes.
- **D4. Publication.** Publication (old r02, r03) moves to a later plan, after the editors reply. Proposed: yes.
- **D5. Unattended submission.** The submitter submits without a human action, inside the approved caps. Proposed: yes.
- **D6. Fable minor findings.** Minor findings and suggestions from Fable go to the editors and are not fixed automatically. Proposed: yes.

## Shared facts

- **Gate helper.** `plans/v4-es-1/gatelib.py` stays the shared gate helper. No step changes it. `gatelib.py packets build` writes its record to `plans/v4-es-1/records/j01-packets.md` (a fixed path in the helper). Step j01 has that path in `touches`.
- **Batch folders.** `$BATCH` means `$RALPH_WORK/aprende-a-programar-como-un-bicho-raro/v4-es-1b/batch/`. It holds `outbox/`, `inbox/`, `ledger/applied.jsonl` and `costs.jsonl`. It is outside the repository. Never track it.
- **Ticket.** A ticket is `outbox/<wave>-<lane>-<provider>-<model>.requests.jsonl` and `<same>.ticket.json` (`wave`, `lane`, `provider`, `model`, `requests`, `estimate_usd`, `input_sha256`). One ticket is one batch.
- **Results by wave.** Every tool that reads batch results takes `--wave W` and reads the submitter inbox unless `--results-dir` is given. Results never go into a worktree or into Git, except the inbox replies that j03 writes and the reports.
- **Build records.** `tickets --record FILE` writes `tickets:`, `requests:`, `estimate-usd:` and `input-sha256:`. Each lane tool also writes the lane keys that the gate of its build step names (for example `lenses:`, `items:`, `files:`, `segments:`, `code-findings:`, `findings:`, `audit-sample:`, `changed-units:`, `pages:`).
- **Packets after a content change.** `gatelib.py packets rebuild` fails when the digest differs from `plans/v4-es-1/records/j01-packets.md`. The first step that needs packets after a fix (j09, p06) runs `gatelib.py packets build` first, which records the new digest.
- **Dead helper commands.** `gatelib.py requests` calls the old `jury_requests.py build` and `translation/prompts/batch-jury.md`. No step of this plan uses it.
- **Custom IDs.** Anthropic requires 1 to 64 characters from `A-Z a-z 0-9 _ -` (check the API reference in a03). Review IDs are `<packet>_<lens>_<12 hex>`, for example `P-critical-01_L1_3fa2c4d9e011`.
- **Known test failures.** `plans/adopt-ralph/tools-test-baseline.txt` records them. `gatelib.py tests` means "no new failure and no fewer tests".
- **Untracked private files.** As in `v4-es-1`: `review/packets/`, `review/repo-bundle.zip`, `review/canaries.key.json`, `review/units.index.jsonl`, `loop/driver.out*`, `translation/work/`. Requests in the outbox hold packets with canaries. That is by design: they go to the vendors.
- **Finding schema.** `translation/schemas/finding.schema.json`. Adjudication statuses: `accepted`, `rejected`, `duplicate`, `needs-human`, `needs-source-issue`. Always `needs-human`: playfulness that the panel did not agree on, a guarantee, the 40-rule, safety, the acronym.
- **Lenses.** L1 to L13 in `translation/prompts/jury-lenses/` (from step a02). L7 (cold reader) gets a Spanish-only packet, so it has its own cache prefix. L3 gets the humor register slice of the packet.
- **English clone.** `translation/source.json` names the clone and the pinned commit `48a4429`. The English repository HEAD is the same commit on 2026-11-24.

## Parallelism

- At the start these run together: a00, a01, a02, a03, a05, f01, x01, u01, c01. Their `touches` do not overlap.
- After a03: a04, t02 (after a02 too), t03, t06, t08 run together. After a05: t01, t07. After t01: t04, t05.
- W1 build steps j02, e01, h01 and b01 write different tickets and different records. They run together.
- p01 (the Fable brief) can run as soon as j05 is done. It does not wait for the fixes.
- Generated fix steps touch one PO file and its generated Markdown, or one code family. The driver runs them with `--jobs 4`.
- No two steps that can run together touch the same file.

## Risks

- **A key reaches an agent.** Only the submitter reads keys. The driver environment has no key. If an agent step finds a key in its environment, it stops and sets `status: blocked`.
- **Cost overrun.** The submitter refuses a ticket over the wave cap or the program cap. It counts a submitted batch at its cap until the real cost is collected. Estimates use the uncached price.
- **Haiku is not good enough for a lens.** The routing rule moves that lens to Opus 5.5. If Opus also fails, the lens goes to two models from both vendors, and the report says so. Nobody lowers the bar.
- **Cache misses in a batch.** Caching in a batch is best-effort. The cost is then higher but stays under the cap. W0 measures the hit rate.
- **Fable refuses pages (A11).** The W0 probe sends two chunks with adversarial-program content. If Fable refuses, p03 sends those pages to Opus 5.5 and the report marks them.
- **Fable invents a line number.** p04 never trusts a line number from the model. It finds the quoted text in the Spanish sources and in the PO files and computes file and line. A quote it cannot find goes to the "unverified" section.
- **The fixes after Fable are not re-reviewed by Fable.** p08 runs the release check and the deterministic gates. The editors read the result. A later plan can run a Fable pass on the changed pages.
- **A wave stalls.** The submitter resubmits errored and expired requests once. After the second failure the request is recorded as failed, and the wait step reports it. Jim decides.
- **Batch results arrive late or twice.** Stable custom IDs and the applied ledger stop a second import. Reconcile before every import.
- **The operator checkout is not clean (A8).** a01 checks it. Do not run the driver on a checkout where `git status --short` is not empty.
