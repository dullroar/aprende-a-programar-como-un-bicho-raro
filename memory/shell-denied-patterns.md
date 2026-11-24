---
gist: "Read me when: a Bash call is denied in a non-interactive agent session (dontAsk mode), or you plan a shell command that is not a single simple command."
---

# Shell patterns that the sandbox denies

## Fact

In dontAsk mode (for example `claude -p`) the sandbox denies many shell forms. A denied call can end an iteration with no progress.

Denied forms:

- Compound commands: `&&`, `;`, and redirects mixed with other commands.
- Heredocs, also `python3 - <<EOF`, and `cat >> file <<EOF`.
- Output redirects (`>`, `>>`), `echo >> file`, and `sed -i` in some sessions.
- Shell variables and substitutions: `$?`, `$(...)`, backticks, `$PIPESTATUS`, `$RALPH_AGENT`.
- A leading `VAR=value command`, `for` loops, and brace expansion such as `src/*/*.{a,b}`.
- Writes outside the repository and the English clone (for example `/tmp`).
- Toolchain probes such as `rustc --version` or `dotnet`.

## Cause

The sandbox allows only simple commands that it can check before it runs them.

## What to do

- Run one simple command in each Bash call. Read its output. Do not use `echo $?`.
- Write and change files with the Write and Edit tools, never with redirects or heredocs.
- Write a script with Write, then run it as one command. Put scratch files in `translation/work/` (git-ignored).
- To set an environment variable, use a small Python wrapper (`os.environ` plus `runpy`). Do not use a shell prefix.
- To capture an exit code, use a tool that records it (see `tools/baseline.py`).
- To wait for a long job, start it in the background and read its output file. Do not use `until` or `sleep` loops.
- Use Grep with a `glob` instead of brace expansion.
- Run each tool as a plain `python3 -I tools/...` or `git ...` command.
- Do not plan work that needs a toolchain. Record "not extracted" with that reason.
- Never run `translate.py --dry-run` to preview. It still calls the model and spends tokens.
