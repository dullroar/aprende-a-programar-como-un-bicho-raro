# Goal: finish the review of the Spanish edition `v4-es.1` with batch jobs, then hand it to human editors

## Ralph loop prompt

Use this prompt for each loop iteration. It has no chat history, so keep it complete.

> You work on plan `v4-es-1b` in this repository. Read `AGENTS.md`, then `plans/v4-es-1b/goal.md` and `plan.md`.
> Open the step file you were given. Work only in the worktree you were given, on its branch.
> Do only that step. Change only the files in `touches`.
> Run the `gate` command. If it fails, find the cause and fix it. Do not weaken or delete the gate. Before you commit, run the full tool suite as the gate does: `python3 plans/v4-es-1/gatelib.py tests`.
> When the gate passes, set `status: done` and write `evidence` (command, result, date). Commit.
> If you cannot finish, keep `status: in_progress`, write what remains under "Resume notes" in the step file, and commit.
> If you are blocked, set `status: blocked` and write the reason. Do not guess. If one command is denied three times, stop and write it under "Resume notes". Do not retry a fourth time.
> Never push, publish, tag, change a remote or change a GitHub setting. Never run `ralph-pusher`. Never run `loop/ralph.sh`. Never remove `loop/STOP`. Never install packages, create a virtual environment or use the network.
> Never read, write or print an API key. Never submit, cancel or fetch a batch. Only the submitter (`tools/batch_submitter.py`, run by the operator) does that. A step writes tickets to the outbox and reads results from the inbox.
> Packets, units and the canary key are not in a worktree. Rebuild them in `.probe/` with `python3 plans/v4-es-1/gatelib.py packets rebuild`. Make scratch copies only in `.probe/` inside the worktree, and delete `.probe/` before the gate.
> Never write secrets or personal data in any file. Write in Simplified Technical English.

## Goal

The Spanish edition `v4-es.1` gets a full adversarial review by models that were not in the translation loop. The review runs as batch jobs on the Anthropic Message Batches API (first choice) and the OpenAI Batch API (second vendor and overflow). Claude Code agents do the work that needs judgment in the repository: tools, fixes of code, and fixes that fail the automatic checks. Each wave of batch work has a 24-hour completion window. Before the hand-off, Claude Fable 5.2 reads the built PDFs (book, study guides, study plan) and writes feedback with PDF page, source file and line. Fable changes nothing. The plan ends when the hand-off package for the human editors is ready and Jim sends it.

This plan supersedes `v4-es-1`. It keeps the goals of that plan, except publication, and it keeps `plans/v4-es-1/gatelib.py` as the shared gate helper. Steps u01 to u05, c01 to c05 and x01 are copied from `v4-es-1` with the record paths moved to this plan.

Library for the controls: `deterministic-controls` `v0.2.0`. Install line (for the operator and for CI, never for an agent step):

`python3 -m pip install "deterministic-controls @ git+https://github.com/dullroar/deterministic-controls@d9a1a604fddb5b268a8dadeb693bcbe7fecbf6e5"`

## Done when

- Every step of this plan is `done` with evidence.
- Gate 7 passes (`tools/jury_gate.py --stage final`): no open critical or major finding, canary recall reported for every juror, the humor register has a decision for each item (provisional where only the AI panel decided), every `needs-human` item has a `human_decision`.
- The Fable report `review/fable/report-<date>.md` exists. Each finding has a PDF page and a verified source file and line, or it is in the "unverified" section. Each critical and major Fable finding is fixed, rejected with a reason, or sent to the editors.
- The final build is deterministic (two builds, same hashes) and `verify.py --release --no-gates` passes.
- `review/editors/` holds the hand-off package, and Jim records that he sent it.
- Total batch spend is at or below the caps in `plans/v4-es-1b/records/f02-operator-budget.md`.

## Out of scope

- Publication, the release tag and the release assets (old steps r02 and r03). A later plan does them after the human editors reply.
- The old loop: `loop/ralph.sh` and `loop/STOP` stay as they are.
- Pushing, remotes, GitHub settings, required checks and branch protection.
- Contact with the editors and with the English maintainer. Jim does that in operator steps.
- Codex and GitHub Copilot as executors. Their budgets are reserved or spent.
- A local model (owner decision 2026-11-23).
