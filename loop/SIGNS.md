# SIGNS.md: lessons learned (one imperative line each)

- Never run compound shell commands that touch paths outside the repo except via the English clone path in CONFIG.yaml; keep Bash calls simple (one command each).
- If the sandbox denies `tar -x` of the English tree into the repo, block P0-002 at once; do not retry variants or hand-copy files.
- Compound Bash (&&, ;, redirects mixed with other commands) is denied; a single pipeline `git -C <english_clone_path> archive <sha> | tar -x -C <repo> --exclude=.gitignore` is allowed. Edit files with Edit/Write, not shell.
- Import the English tree with: git -C <english_clone_path> archive <sha> | tar -x -C . ; keep this repo's own .gitignore entries and loop/, translation/, ralph-kit-es/ and the plan file intact.
