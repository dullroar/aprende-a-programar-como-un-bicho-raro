# Run and hand off the translation loop

Start from the Spanish repository. All runners use the same checkout, queue,
PO files, review registers, and Git history.

```bash
loop/ralph.sh --agent=claude --on-limit handoff
loop/ralph.sh --agent=copilot --on-limit handoff
loop/ralph.sh --agent=codex --on-limit handoff
```

Pass your provider explicitly. The driver exports it as `RALPH_AGENT` for
provider-specific steps in the iteration. The default is Claude, and the
space-separated form `--agent NAME` also works. Run one command at a time.
The driver releases its lock when it exits. On a recognized provider usage
limit it exits with status 75 in handoff mode. Start another provider's command
in the same checkout and the next iteration picks up the saved work, including
a task whose prior claim is still fresh. The default limit action is `wait`,
which retries the same provider.

To request a pause while the loop is running, issue `loop/ralph.sh --pause`
from a second terminal. Wait for the iteration to finish and the driver to
exit. Restart a runner with `--resume` to clear that pause. An editorial
`loop/STOP` is a separate checkpoint. Complete the review before removing it
using the checkpoint instructions. Check `loop/STATE.md`,
`python3 tools/next_task.py --counts`, and the latest driver output for status.

The CLIs use their existing sign-ins. Codex runs with workspace-write
sandboxing and automatic approval review. Copilot runs with assisted approval, plus allow rules for `python3`,
`python`, `tools/*`, `git` and file writes (the judge kept denying
`tools/translate.py` exports and imports); `git push`, `gh`, `curl`, `wget`
and `ssh` stay denied.
Request review for a scoped Git operation or the unchanged verifier if the
sandbox blocks it. If review denies a required operation, keep the partial
work and report the specific operation. The usage ledger records the agent and
tokens reported by the CLI. The shared USD cap uses only reported dollar costs.
Codex and Copilot token entries have no dollar amount.

## Drafts from Codex, Copilot, or an interactive session

Export masked inputs from the pinned English source, including pending fuzzy
entries. Use `--limit` and `--from` to work in smaller batches.

```bash
python3 -I tools/translate.py --export-pending FILE.md --limit 40 > /tmp/spanish-input.jsonl
```

Draft the replies in the current session using `translation/prompts/translate.md`
and the house style. Use one JSON object per input with the
`translator_output` fields from `translation/schemas/segment.schema.json`.
Import a contiguous pending batch with the same start and limit, its actual
provider/model identifier when available, and the queue task ID. The example
uses the Codex session label. For Copilot, use `github-copilot/MODEL` with the
model reported by its CLI, or `github-copilot/agent` if it is unavailable.

```bash
python3 -I tools/translate.py FILE.md --drafts /tmp/spanish-replies.jsonl \
  --draft-model openai/codex-agent --task-id TASK-ID --redo-fuzzy --limit 40
```

The import validates the reply schema, English segment IDs and placeholders,
and the same invariants as the Claude backend. It writes checkpointable PO
entries and provenance. Resolve fuzzy entries, regenerate the file and
anchors, and run the task's normal gates before committing.

## Models and tiers

The model is chosen per iteration, not hard-coded. `loop/CONFIG.yaml` lists, for each agent, a
`standard` and a `light` model (and a reasoning effort for Codex and Copilot). Before each iteration
the driver previews the task `tools/next_task.py` will hand out and picks the tier: `light` only when
the task says `"tier": "light"` (queue amendment `{"amend": ID, "set": {"tier": "light"}}`) or its
kind is in `tier_light_kinds`, and only on its first attempt. `TIER_OVERRIDE=standard|light` in the
environment forces a tier. The driver prints a `starting:` line with the task, tier and requested
model, and after the run a `model evidence:` line with the model the CLI **reported** (Claude
`modelUsage`, Copilot model-call events, Codex's session file), flagging a `MISMATCH`. Claude Code
also uses a small helper model for side calls, so a second Claude model in that line is normal.
Both are stored in `loop/ledger/usage.jsonl`; `python3 tools/model_report.py` summarizes them.
Edit CONFIG.yaml only while the driver is stopped (it reads the file at start-up).
