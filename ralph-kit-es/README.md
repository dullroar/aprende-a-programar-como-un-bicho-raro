# ralph-kit-es: starter kit for the long-haul Spanish-edition loop

Companion to `SYNTHESIZED-TRANSLATION-PLAN-es-bicho-raro.md` (section 11). Nothing here has been run.

| File | Goes to | Purpose |
| --- | --- | --- |
| `PROMPT.md` | `<spanish-repo>/loop/PROMPT.md` | The single prompt every loop iteration receives |
| `ralph.sh` | `<spanish-repo>/loop/ralph.sh` | Driver: fresh session per iteration, budgets, stall breaker, ledger, sentinels |
| `CONFIG.template.yaml` | `<spanish-repo>/loop/CONFIG.yaml` | Pinned English SHA, edition defaults, budgets, model roles |
| `STATE.template.md` | `<spanish-repo>/loop/STATE.md` | The 60-line state file |
| `seed-queue.jsonl` | `<spanish-repo>/loop/queue/seed.jsonl` | 61 hand-authored tooling and stage tasks, Phases 0 to 7A |
| `ADVERSARIAL-REVIEW-PROMPT.md` | `<spanish-repo>/review/` | Master prompt and ten lens modules for the uninvolved AIs (Phase 7B) |

## Bootstrap (one time)

1. Make an empty directory for the Spanish repo and run `git init`. Do not add a remote.
2. Create `loop/` and `loop/queue/`; copy the kit files to the destinations above (rename as shown).
3. Edit `loop/CONFIG.yaml`: pin the **full** English SHA, set budgets, record exact model IDs.
4. Copy the plan document into the repo root (its path is in `plan_path`).
5. Create empty `loop/log.md`, `loop/SIGNS.md`, `loop/decisions-provisional.md`, `loop/blockers.md`; commit.
6. Check the agent CLI's flags with `--help`; adjust `AGENT_CMD` if needed.
7. Run `loop/ralph.sh`. To stop: `touch loop/STOP`. To hand off: run it again, with a different `AGENT_CMD` if you like.

The loop commits locally only and never pushes. It creates `loop/DONE` when the release candidate and review packets are ready.
