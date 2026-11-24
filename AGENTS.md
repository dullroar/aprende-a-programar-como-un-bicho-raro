# Agent contract

This repository is the Spanish edition of an English book. The English source is pinned in `translation/source.json`.
The layout follows `repo-template`. The work runs on the Ralph runner.

## Standing rules

1. **No private data in tracked files.** Never put PII, secrets, keys, tokens, passwords, personal paths or private host names in a file that Git tracks. This includes memory, plans, docs, logs and examples. Use placeholders. Keep working files outside the repository (see `~/repo-work` below).
2. **Start all work on a branch.** Never commit to `main` directly. This applies in a Git worktree too. A worktree does not replace a branch: create the branch first, or create the worktree with a new branch (`git worktree add -b <branch> <path>`).
3. **Write documents in Simplified Technical English** (ASD-STE100), or close to it. Use short sentences, one idea in each, active voice, simple words and consistent terms. This rule applies to all new English text. It does not apply to the translated book content.
4. **Do not push, publish or force-push** without authorization from the user.
5. **Secrets are never tracked.** Run `python3 scripts/secret_guard.py` before a commit. Do not add an exception to pass a task. A new exception needs a reason and a fingerprint, and the owner reviews it.
6. **User instructions come first.** If sources conflict, use this order: user, this file, the named plan, `memory/`, code and tests, old notes.
7. **Do not weaken the controls.** Do not change the pin (`scripts/controls-requirements.txt`), `controls.toml` or the workflows to make a task pass. The driver checks the gate and the `touches` of each step. A change to the gate or a file outside `touches` fails the step.
8. **Route work by cost.** Send each piece of work to the cheapest executor that can do it. The gate decides if the work is done.
9. **Read the templates before a structure change.** Before changing this repository's structure, read `repo-template` and `ralph-looper` (https://github.com/dullroar/repo-template and https://github.com/dullroar/ralph-looper) and account for their contracts.

## Authorization limits

These limits come from section 11.8 of `SYNTHESIZED-TRANSLATION-PLAN-es-bicho-raro.md`. The limits are the same.

- You may create local commits and branches at any time.
- Pushing the release candidate to a private remote needs the owner to say "go".
- The continuous private backup of `loop/es-v4` is authorized. Only the trusted `loop/push-backup.sh` does it. An agent cannot push. The pre-push hook allows only that script to push `loop/es-v4`. Do not change the hook.
- Making the repository public, tagging a release and uploading PDF or EPUB files need the owner to say "publish".
- Never change the English repository. It is fetch-only.
- Run unusual example programs only inside the sandbox container, never on the host.
- Do not open an upstream issue or patch for an English defect. Log it in `translation/source-issues.md`. The owner decides.

## Locked code and the pinned source

- Locked code is protected by `tools/lock_code.py`. Never bypass the pre-commit hook. Never edit locked code to make a task pass.
- To install the hooks, run `python3 tools/lock_code.py --install-hook` first. Then run `scripts/install_hooks.sh`. Do not run them in the other order.
- The English source is pinned in `translation/source.json`. Do not change the pin.

## The old loop

- `loop/STOP` stays. It is the Part III checkpoint of the owner. Do not remove it.
- Do not run or resume `loop/ralph.sh`.
- Keep `loop/queue/` history and `loop/STATE.md` unchanged unless a plan step says so.

## Files that stay untracked

Never add these files to Git:

- `review/packets/`
- `review/repo-bundle.zip`
- `review/canaries.key.json`
- `review/units.index.jsonl`
- `loop/driver.out*`
- `translation/work/`

## Directory structure

| Path | Purpose | Index |
| --- | --- | --- |
| `docs/` | Book content (the translated book). It is not a place for repository documents. | none |
| `GUIA-DEL-REPO.md` | Index of repository documents for humans. | edit by hand |
| `memory/` | Facts for agents that cost time to find. One file for each fact. | `memory/AGENTS.md` (generated) |
| `plans/` | Work plans. One folder for each plan. | `plans/AGENTS.md` (generated) |
| `scripts/` | Scripts for agents and CI: run, test, debug, build. | `scripts/AGENTS.md` (generated) |
| `translation/`, `tools/`, `loop/`, `review/` | Edition tooling and records. | none |

**Deviation from the template.** In `repo-template`, `docs/` holds documents for humans, and `docs/README.md` is their index. Here `docs/` is book content. Do not add `docs/README.md`. The index for humans is `GUIA-DEL-REPO.md`.

### How to load context

1. Read this file.
2. Read `memory/AGENTS.md`, `plans/AGENTS.md` and `scripts/AGENTS.md`.
3. Open only the files whose "Read me when" or "Run me when" line matches your task.
4. Stop when you know the decision, the files, the limits and how to verify.

### memory/

- One memory in one file. Edit the file that exists for a topic. Do not add a second file for the same topic.
- Each file starts with front matter that has a `gist` key:

  ```yaml
  ---
  gist: "Read me when: <the situation in which an agent needs this file>"
  ---
  ```

- Never write PII, secrets or personal paths in a memory.
- `memory/AGENTS.md` is generated. Do not edit the part between the markers.

### plans/

- A plan is a folder `plans/<plan-name>/`. Copy `plans/for-each-plan/` to start one.
- `goal.md` holds the goal and the Ralph loop prompt. `plan.md` holds the high-level plan and has a `gist` key. `steps/` holds one file for each step.
- A step file has front matter: `id`, `status`, `depends_on`, `touches`, `lane`, `gate`. A step is done only when its `evidence` is recorded.
- Run each plan in its own Git worktree. Steps that run at the same time must not touch the same files.
- A plan must survive a stop at any time. Record progress in the step files, not in chat.
- Runtime output (logs, usage records, locks) goes outside the repository: `~/repo-work/<repo>/<plan>/`. Never track it.
- `plans/AGENTS.md` is generated.

### scripts/

- Scripts are deterministic. Each script starts with a comment block that has a line `Run me when: <situation>`.
- `scripts/AGENTS.md` is generated from those lines.

### Generated indexes

Run `python3 scripts/build_indexes.py` after any change to a memory, a plan or a script. CI runs the same script with `--check` and fails if an index is stale.

## Validation

Run the smallest check that proves your change.

- Fast check of the edition: `scripts/verify_fast.sh` (it runs `python3 -I tools/verify.py --fast`).
- Tool tests: `python3 -m unittest discover -s tools -p 'test_*.py'`.
- Indexes: `python3 scripts/build_indexes.py --check`.
