# SIGNS.md: lessons learned (one imperative line each)

- Never run compound shell commands that touch paths outside the repo except via the English clone path in CONFIG.yaml; keep Bash calls simple (one command each).
- If the sandbox denies `tar -x` of the English tree into the repo, block P0-002 at once; do not retry variants or hand-copy files.
