#!/bin/sh
# Trusted backup push of the current loop branch to origin. Run by loop/pusher.sh (not by the agent).
# The agent has no credentials and `git push` is denied for it; this script is the only pusher.
cd "$(dirname "$0")/.." || exit 2
BR="$(git branch --show-current)"
if [ "$BR" != "loop/es-v4" ]; then echo "FAIL not on loop/es-v4 (on '$BR') $(date -u +%FT%TZ)" > loop/push.status; exit 1; fi
HEADSHA="$(git rev-parse HEAD)"
if [ "$HEADSHA" = "$(git rev-parse --verify -q "refs/remotes/origin/$BR")" ]; then exit 0; fi
unset GIT_ASKPASS
export GIT_TERMINAL_PROMPT=0
if RALPH_PUSH=1 git push -q -u origin "$BR" 2> loop/push.err; then
  echo "ok $HEADSHA $(date -u +%FT%TZ)" > loop/push.status
else
  echo "FAIL $(tr '\n' ' ' < loop/push.err | cut -c1-220) $(date -u +%FT%TZ)" > loop/push.status
  exit 1
fi
