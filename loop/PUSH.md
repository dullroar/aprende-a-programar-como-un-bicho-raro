# Backup pushes (authorized by Jim, 2026-11-20)

Remote: `origin` = git@github-bicho-raro:dullroar/aprende-a-programar-como-un-bicho-raro.git (private; SSH alias in ~/.ssh/config using a single-repo write deploy key ~/.ssh/id_ed25519_bicho_raro_deploy). Branch pushed: `loop/es-v4` only.

- `loop/pusher.sh` runs in the background and calls `loop/push-backup.sh` every 45 s; it pushes whenever HEAD has moved, so every task commit is backed up within a minute.
- The **agent never pushes**: it has no credentials, `git push` is denied in its tool list, and the repo's pre-push hook refuses any push unless `RALPH_PUSH=1` is set, the remote is origin, and only `refs/heads/loop/es-v4` is pushed.
- Status of the last push: `loop/push.status` (`ok <sha> <time>` or `FAIL <reason>`).
- Start the pusher: `setsid nohup loop/pusher.sh > loop/pusher.out 2>&1 < /dev/null &`. Stop it: `touch loop/PUSHER-STOP`.
- Making the repo public, tagging a release and uploading artifacts still need Jim's explicit "publish".
