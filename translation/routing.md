# Routing map

This file says which executor does each kind of task. `tools/check_routing_map.py` checks it against `loop/queue/**/*.jsonl`.

## Measurement

The cost history `loop/ledger/usage.jsonl` is not present in this worktree. It is untracked. The measurement is `no history` for every kind, except where a fact from the bootstrap wave of this plan applies. Run `python3 tools/model_report.py` on the operator machine to fill the table with real cost, wall time and retry rate.

Bootstrap fact: three parallel local-model steps on an 8 GB GPU made no file edit in more than 70 minutes. The owner decided on 2026-11-23 not to use the local model for plan steps.

## Routes

- `script` or `ci`: a deterministic program. No model.
- `batch`: the Batch API. The operator submits through `tools/batch.py`. A `script` step imports the result.
- `agent-light`: a cloud agent with `tier: light`. The local model is not used.
- `agent-standard`: a cloud agent with a model different from the one that produced the work under review.
- `operator`: the owner or the operator does the work.

## Table

| kind | route | reason | measurement | expected cost change |
| --- | --- | --- | --- | --- |
| meta | agent-light | Meta tasks are small: read a config, write a pin, move a document. A cloud light agent does them in one pass. | no history | Lower than a standard agent. A local model is not used because of the bootstrap fact. |
| meta | operator | Approvals, publication and upstream actions need the owner. | no history | None. The work does not go to a model. |
| build-tool | agent-standard | A new tool needs design and tests. A fix to a known tool is a bounded task. | no history | None for new tools. A bounded fix moves to `agent-light` when the step file gives the exact change. |
| build-tool | agent-light | A bounded tool fix or a fixture addition has a clear gate. | Bootstrap wave: local model made no edit in more than 70 minutes. | Lower. A light cloud agent replaces a standard agent for bounded work. |
| gate | script | A gate is a command with an exit code. A program runs it. | no history | Large saving. No model tokens. |
| gate | ci | The same gate runs in CI on each pull request. | no history | No model tokens. CI minutes only. |
| translate | batch | Bulk drafts of new and fuzzy segments suit the Batch API. The segments are masked and checked after import. | no history | Lower. Batch pricing is below the interactive price. The history will give the exact figure. |
| translate | agent-standard | A segment that fails the checks twice needs judgment. | no history | Higher for each segment, but the count is small. |
| localize-code | script | Localization of code uses `loc_map.py` and `loc_apply.py`. The rules are fixed. | no history | Large saving. No model tokens. |
| localize-code | agent-standard | A new identifier or an unusual example needs judgment. | no history | None. The count is small. |
| regen | script | A regeneration runs a build, an import or a report. | no history | Large saving. No model tokens. |
| audit | script | Link, anchor, invariant and oracle audits are programs. | no history | Large saving. No model tokens. |
| audit | batch | An automated reviewer pass and back-translation fit the Batch API. | no history | Lower. Batch pricing and no waiting time. |
| audit | operator | A jury with outside vendors and a native-speaker humor review need people. | no history | None. The work does not go to a model. |
| review-fix | agent-standard | A fix after review needs judgment. The agent uses a model different from the one that wrote the work. | no history | None. This is the baseline. |
| review-fix | batch | A minimal-edit delta from a review finding is a bulk task. | no history | Lower. Batch pricing. |
| packet | script | Packet building is a program (`tools/jury_packet.py`). | no history | Large saving. No model tokens. |
