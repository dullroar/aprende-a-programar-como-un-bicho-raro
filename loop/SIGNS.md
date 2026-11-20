# SIGNS.md: lessons learned (one imperative line each)

- Never run compound shell commands that touch paths outside the repo except via the English clone path in CONFIG.yaml; keep Bash calls simple (one command each).
- If the sandbox denies `tar -x` of the English tree into the repo, block P0-002 at once; do not retry variants or hand-copy files.
- Compound Bash (&&, ;, redirects mixed with other commands) is denied; a single pipeline `git -C <english_clone_path> archive <sha> | tar -x -C <repo> --exclude=.gitignore` is allowed. Edit files with Edit/Write, not shell.
- Import the English tree with: git -C <english_clone_path> archive <sha> | tar -x -C . ; keep this repo's own .gitignore entries and loop/, translation/, ralph-kit-es/ and the plan file intact.
- Never extract the English tree with `--exclude=.gitignore` (it drops nested ones); `tools/inventory.py --check` compares the file set to the pinned SHA and catches this.
- Run `python3 -I tools/test_*.py` for tool tests; keep Bash calls single-command when possible, tools in tools/ read files with `with open`.
- Do not write to paths outside this repo or the English clone (for example /tmp): such writes are denied in dontAsk mode. Use translation/work/ (git-ignored) for scratch files.
- Do not use $?, $(...) or backticks in Bash calls; they are denied. Run one simple command per call and read its output instead.
- Use the project virtualenv (.venv; already first on PATH). pip and npm installs are allowed (Jim approved installs in chat); install into .venv only, never globally, and record each new dependency in requirements-es.txt.
- Never use $PIPESTATUS, `echo` or pipes with `tail` in Bash calls to capture exit codes; write a small tool in tools/ that records them (see tools/baseline.py) and run it as one command.
- Compare frozen files by git blob content: .bat files check out as CRLF here (.gitattributes), so raw working-tree hashes of gradlew.bat differ by design; use tools/lock_code.py --verify, never plain sha256sum -c.
