#!/usr/bin/env bash
# ralph.sh: driver for the Spanish-edition Ralph loop.
# Place this file at <repo>/loop/ralph.sh. Run it from anywhere.
#
# What it does, per iteration:
#   1. checks sentinels and budgets
#   2. starts a FRESH agent session fed with loop/PROMPT.md
#   3. records usage in loop/ledger/usage.jsonl
#   4. checks that progress happened (new commit or queue change)
# It never pushes, never touches remotes, and never needs credentials.
#
# Handoff to another agent: set AGENT_CMD (see below) and run this script again.
# VERIFY every agent-CLI flag against the installed version's --help before the first run.

set -u

LOOP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$LOOP_DIR/.." && pwd)"
cd "$ROOT" || exit 2

PROMPT="$LOOP_DIR/PROMPT.md"
CONFIG="$LOOP_DIR/CONFIG.yaml"
LOGDIR="$LOOP_DIR/logs"
LEDGER="$LOOP_DIR/ledger/usage.jsonl"
STATE="$LOOP_DIR/STATE.md"
mkdir -p "$LOGDIR" "$LOOP_DIR/ledger"

# ---- config: flat "key: value" lines in CONFIG.yaml; environment variables override ----
cfg() {  # cfg key default
  local v
  v="$(grep -E "^$1:" "$CONFIG" 2>/dev/null | head -n1 | sed -E "s/^$1:[[:space:]]*//; s/[[:space:]]*#.*$//; s/^[\"']//; s/[\"']$//")"
  printf '%s' "${v:-$2}"
}
MAX_ITER="${MAX_ITER:-$(cfg max_iterations 300)}"
MAX_USD="${MAX_USD:-$(cfg max_usd 150)}"
ITER_TIMEOUT_MIN="${ITER_TIMEOUT_MIN:-$(cfg iteration_timeout_minutes 45)}"
MAX_STALL="${MAX_STALL:-$(cfg max_stalled_iterations 3)}"
SLEEP_SECS="${SLEEP_SECS:-$(cfg sleep_seconds_between_iterations 5)}"

# Default agent: Claude Code in print mode with an explicit tool allowlist.
# Replace via AGENT_CMD to hand the loop to a different agent. The command must read the
# prompt on stdin, run shell commands in the current directory, and print its result to stdout.
# Verified on Claude Code 2.1.319: no --max-turns flag exists; --max-budget-usd caps each iteration.
# NOTE: the allowlist is a guard rail, not a sandbox (python3 can do anything). Real protection:
# no credentials in the environment, no pushable remote, and a pre-push hook that refuses.
DEFAULT_AGENT_CMD='claude -p --output-format json --model sonnet --max-budget-usd 6 --permission-mode dontAsk --allowedTools "Read,Edit,Write,Glob,Grep,Bash(git:*),Bash(python3:*),Bash(python:*),Bash(pandoc:*),Bash(node:*),Bash(npx:*),Bash(tools/*:*),Bash(ls:*),Bash(cat:*),Bash(head:*),Bash(tail:*),Bash(wc:*),Bash(grep:*),Bash(find:*),Bash(sed:*),Bash(sort:*),Bash(diff:*),Bash(cp:*),Bash(mv:*),Bash(mkdir:*),Bash(touch:*),Bash(chmod:*),Bash(date:*),Bash(sha256sum:*),Bash(zip:*),Bash(unzip:*),Bash(echo:*),Bash(printf:*),Bash(test:*),Bash(pip:*),Bash(pip3:*),Bash(npm:*),Bash(.venv/bin/*:*),Bash(pytest:*),Bash(tar:*),Bash(rsync:*),Bash(rm:*),Bash(cd:*),Bash(awk:*),Bash(tr:*),Bash(cut:*),Bash(xargs:*),Bash(pwd:*),Bash(which:*),Bash(basename:*),Bash(dirname:*),Bash(stat:*),Bash(file:*),Bash(du:*),Bash(tee:*),Bash(uniq:*),Bash(comm:*),Bash(env:*),Bash(true:*),Bash(sleep:*),Bash(time:*)" --disallowedTools "Bash(git push:*)" "Bash(gh:*)" "Bash(curl:*)" "Bash(wget:*)" "Bash(ssh:*)"'
# The agent must be able to read the pinned English clone (outside the repo). --add-dir grants that.
ENGLISH_DIR="$(cfg english_clone_path "")"
[ -n "$ENGLISH_DIR" ] && [ -d "$ENGLISH_DIR" ] && DEFAULT_AGENT_CMD="$DEFAULT_AGENT_CMD --add-dir \"$ENGLISH_DIR\""
AGENT_CMD="${AGENT_CMD:-$DEFAULT_AGENT_CMD}"

# ---- project virtualenv first on PATH (never install into another project's venv) ----
if [ -x "$ROOT/.venv/bin/python" ]; then export PATH="$ROOT/.venv/bin:$PATH"; export VIRTUAL_ENV="$ROOT/.venv"; fi

# ---- safety: no credentials for the agent, no interactive git prompts ----
unset GH_TOKEN GITHUB_TOKEN GITLAB_TOKEN
export GIT_TERMINAL_PROMPT=0
export GIT_ASKPASS=/bin/false

# ---- single instance ----
exec 9>"$LOOP_DIR/.lock"
if ! flock -n 9; then
  echo "ralph: another loop is running (lock held). Exiting." >&2
  exit 3
fi

[ -f "$PROMPT" ] || { echo "ralph: missing $PROMPT" >&2; exit 2; }

spent_usd() {
  python3 -I - "$LEDGER" <<'PY'
import json, sys
total = 0.0
try:
    for line in open(sys.argv[1], encoding="utf-8"):
        line = line.strip()
        if line:
            total += float(json.loads(line).get("cost_usd") or 0)
except FileNotFoundError:
    pass
print(f"{total:.4f}")
PY
}

queue_signature() {  # changes whenever any queue file changes
  cat "$LOOP_DIR"/queue/*.jsonl "$LOOP_DIR"/queue/generated/*.jsonl 2>/dev/null | sha256sum | cut -d' ' -f1
}

record_usage() {  # record_usage iter jsonfile rc seconds
  python3 -I - "$1" "$2" "$3" "$4" "$LEDGER" <<'PY'
import json, sys, time
it, path, rc, secs, ledger = sys.argv[1:6]
rec = {"iteration": int(it), "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "exit_code": int(rc), "seconds": int(secs),
       "cost_usd": 0.0, "input_tokens": None, "output_tokens": None, "result_tail": ""}
try:
    data = json.load(open(path, encoding="utf-8"))
    if isinstance(data, dict):
        rec["cost_usd"] = data.get("total_cost_usd") or data.get("cost_usd") or 0.0
        u = data.get("usage") or {}
        rec["input_tokens"] = u.get("input_tokens")
        rec["output_tokens"] = u.get("output_tokens")
        rec["result_tail"] = str(data.get("result", ""))[-300:]
except Exception as e:  # agent may not emit JSON; keep going
    rec["result_tail"] = f"unparsed output: {e}"
with open(ledger, "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
PY
}

iter=0
if [ -f "$LEDGER" ]; then iter="$(wc -l < "$LEDGER" | tr -d ' ')"; fi
stall=0
echo "ralph: start at iteration $((iter+1)); max_iter=$MAX_ITER max_usd=$MAX_USD timeout=${ITER_TIMEOUT_MIN}m"

while :; do
  [ -f "$LOOP_DIR/STOP" ] && { echo "ralph: STOP sentinel found."; break; }
  [ -f "$LOOP_DIR/DONE" ] && { echo "ralph: DONE sentinel found: $(head -n1 "$LOOP_DIR/DONE")"; break; }
  [ "$iter" -ge "$MAX_ITER" ] && { echo "ralph: iteration budget reached ($MAX_ITER)."; break; }
  over="$(python3 -I -c "print(1 if float('$(spent_usd)') >= float('$MAX_USD') else 0)")"
  [ "$over" = "1" ] && { echo "ralph: cost budget reached (\$$MAX_USD)."; break; }

  iter=$((iter+1))
  out="$LOGDIR/iter-$(printf '%04d' "$iter").json"
  head_before="$(git rev-parse HEAD 2>/dev/null || echo none)"
  sig_before="$(queue_signature)"
  # tell the agent which iteration it is (STATE.md carries the human-readable copy)
  printf '%s\n' "$iter" > "$LOOP_DIR/.iteration"

  start=$(date +%s)
  timeout "${ITER_TIMEOUT_MIN}m" bash -c "$AGENT_CMD" < "$PROMPT" > "$out" 2> "$out.err"
  rc=$?
  secs=$(( $(date +%s) - start ))
  record_usage "$iter" "$out" "$rc" "$secs"

  # Usage-limit replies are not stalls: sleep and retry instead of tripping the breaker.
  if python3 -I - "$LEDGER" <<'PY'
import json, sys
last = ""
for line in open(sys.argv[1], encoding="utf-8"):
    if line.strip():
        last = line
r = json.loads(last) if last else {}
tail = str(r.get("result_tail", "")).lower()
sys.exit(0 if ("hit your" in tail and "limit" in tail) else 1)
PY
  then
    echo "ralph: usage limit reached at iteration $iter; sleeping ${LIMIT_SLEEP_SECS:-900}s then retrying (not counted as a stall)."
    iter=$((iter-1))
    sleep "${LIMIT_SLEEP_SECS:-900}"
    continue
  fi

  head_after="$(git rev-parse HEAD 2>/dev/null || echo none)"
  sig_after="$(queue_signature)"
  if [ "$head_before" = "$head_after" ] && [ "$sig_before" = "$sig_after" ]; then
    stall=$((stall+1))
    echo "ralph: iteration $iter made no progress (stall $stall/$MAX_STALL, rc=$rc)."
  else
    stall=0
    echo "ralph: iteration $iter progressed (rc=$rc, ${secs}s, spent \$$(spent_usd))."
  fi
  if [ "$stall" -ge "$MAX_STALL" ]; then
    echo "ralph: circuit breaker: $MAX_STALL consecutive iterations without progress. See $LOGDIR." >&2
    printf 'ralph stopped by stall breaker at iteration %s\n' "$iter" >> "$LOOP_DIR/blockers.md"
    break
  fi
  sleep "$SLEEP_SECS"
done

echo "ralph: finished. Iterations: $iter. Spent: \$$(spent_usd). See $LOOP_DIR/HANDOFF.md and $STATE."
