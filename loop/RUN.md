# Run and hand off the translation loop

Start from the Spanish repository. Both runners use the same checkout, queue,
PO files, review registers, and Git history.

```bash
loop/ralph.sh --agent claude --on-limit handoff
loop/ralph.sh --agent codex --on-limit handoff
```

Run one command at a time. The driver releases its lock when it exits. On a
recognized provider usage limit it exits with status 75 in handoff mode. Start
the other command in the same checkout and the next iteration picks up the
saved work, including a task whose prior claim is still fresh. The default
limit action is `wait`, which retries the same provider.

To request a pause while the loop is running, issue `loop/ralph.sh --pause`
from a second terminal. Wait for the iteration to finish and the driver to
exit. Restart either runner with `--resume` to clear that pause. An editorial
`loop/STOP` is a separate checkpoint. Complete the review before removing it
using the checkpoint instructions. Check `loop/STATE.md`,
`python3 tools/next_task.py --counts`, and the latest driver output for status.

Both CLIs use their existing sign-ins. Codex runs with workspace-write
sandboxing and approval policy `never`. If local policy blocks a required
operation, keep the partial work and report the specific operation. The usage
ledger records the agent and tokens reported by the CLI. The shared USD cap
uses only costs the CLIs report. Codex token entries have no dollar amount.

## Drafts from a Codex iteration or an interactive session

Export masked inputs from the pinned English source, including pending fuzzy
entries. Use `--limit` and `--from` to work in smaller batches.

```bash
python3 -I tools/translate.py --export-pending FILE.md --limit 40 > /tmp/spanish-input.jsonl
```

Draft the replies in the current session using `translation/prompts/translate.md`
and the house style. Use one JSON object per input with the
`translator_output` fields from `translation/schemas/segment.schema.json`.
Import a contiguous pending batch with the same start and limit, its actual
provider/model identifier when available, and the queue task ID.

```bash
python3 -I tools/translate.py FILE.md --drafts /tmp/spanish-replies.jsonl \
  --draft-model openai/codex-agent --task-id TASK-ID --redo-fuzzy --limit 40
```

The import validates the reply schema, English segment IDs and placeholders,
and the same invariants as the Claude backend. It writes checkpointable PO
entries and provenance. Resolve fuzzy entries, regenerate the file and
anchors, and run the task's normal gates before committing.
