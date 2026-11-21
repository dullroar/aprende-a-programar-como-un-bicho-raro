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
# Handoff: loop/ralph.sh --agent claude|codex --on-limit handoff. See loop/RUN.md.
# VERIFY every agent-CLI flag against the installed version's --help before the first run.

set -u

LOOP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$LOOP_DIR/.." && pwd)"
cd "$ROOT" || exit 2

agent=claude
on_limit=wait
resume=0
while [ "$#" -gt 0 ]; do
  case "$1" in
    --agent|--on-limit)
      [ "$#" -ge 2 ] || { echo "ralph: $1 needs a value." >&2; exit 2; }
      if [ "$1" = --agent ]; then agent="$2"; else on_limit="$2"; fi
      shift 2 ;;
    --pause) touch "$LOOP_DIR/PAUSE"; exit $? ;;
    --resume) resume=1; shift ;;
    --help)
      echo "Usage: loop/ralph.sh [--agent claude|codex] [--on-limit wait|handoff] [--resume]"
      echo "       loop/ralph.sh --pause"
      exit 0 ;;
    *) echo "ralph: unknown option $1." >&2; exit 2 ;;
  esac
done
case "$agent" in claude|codex) ;; *) echo "ralph: unknown agent $agent." >&2; exit 2 ;; esac
case "$on_limit" in wait|handoff) ;; *) echo "ralph: unknown limit action $on_limit." >&2; exit 2 ;; esac

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
if [ "$agent" = codex ]; then
  DEFAULT_AGENT_CMD='codex -a never exec --sandbox workspace-write --color never --json -'
fi
AGENT_CMD="${AGENT_CMD:-$DEFAULT_AGENT_CMD}"
export RALPH_AGENT="$agent"

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

# With the driver lock held, a claim from a previous iteration can be resumed immediately.
export RALPH_RECLAIM_CLAIMED=1
if [ "$resume" -eq 1 ]; then rm -f "$LOOP_DIR/PAUSE" || exit 2; fi
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
  python3 -I - "$1" "$2" "$3" "$4" "$LEDGER" "$agent" <<'PY'
import json, pathlib, re, sys, time
it, path, rc, secs, ledger, agent = sys.argv[1:]
rec = {"iteration": int(it), "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "agent": agent, "exit_code": int(rc), "seconds": int(secs), "cost_usd": None,
       "input_tokens": None, "output_tokens": None, "result_tail": ""}
raw = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
result = ""
errors = []
usage = {}
if agent == "claude":
    try:
        data = json.loads(raw)
    except ValueError:
        data = {}
    if isinstance(data, dict):
        rec["cost_usd"] = data.get("total_cost_usd", data.get("cost_usd"))
        usage = data.get("usage") or {}
        result = str(data.get("result") or "")
        errors.append(result)
else:
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        if not isinstance(event, dict):
            continue
        event_type = event.get("type")
        if event_type == "turn.completed":
            usage = event.get("usage") or {}
        elif event_type == "item.completed":
            item = event.get("item") or {}
            if item.get("type") == "agent_message":
                result = str(item.get("text") or "")
        elif event_type in ("error", "turn.failed"):
            errors.append(str(event.get("error") or event.get("message") or ""))
if int(rc):
    errors.append(pathlib.Path(path + ".err").read_text(encoding="utf-8", errors="replace").strip())
error_text = "\n".join(filter(None, errors))
rec["result_tail"] = ((error_text if int(rc) else "") or result)[-300:]
rec["input_tokens"] = usage.get("input_tokens")
rec["output_tokens"] = usage.get("output_tokens")
rec["usage_limited"] = int(rc) != 0 and bool(re.search(
    r"\bhit your\b[^\n]{0,100}\blimit\b|\busage[_ ]limit[_ ]reached\b", error_text, re.I
))
with open(ledger, "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("limit" if rec["usage_limited"] else "recorded")
PY
}

iter=$(python3 -I - "$LEDGER" <<'PY'
import json, pathlib, sys
path = pathlib.Path(sys.argv[1])
print(max((json.loads(line)["iteration"] for line in path.read_text().splitlines() if line.strip()),
          default=0) if path.exists() else 0)
PY
) || exit 2
result=0
stall=0
echo "ralph: start at iteration $((iter+1)); agent=$agent max_iter=$MAX_ITER max_usd=$MAX_USD timeout=${ITER_TIMEOUT_MIN}m"

while :; do
  [ -f "$LOOP_DIR/PAUSE" ] && { echo "ralph: PAUSE sentinel found. Use --resume to continue."; break; }
  [ -f "$LOOP_DIR/STOP" ] && { echo "ralph: STOP sentinel found."; break; }
  [ -f "$LOOP_DIR/DONE" ] && { echo "ralph: DONE sentinel found: $(head -n1 "$LOOP_DIR/DONE")"; break; }
  [ "$iter" -ge "$MAX_ITER" ] && { echo "ralph: iteration budget reached ($MAX_ITER)."; break; }
  over="$(python3 -I -c "print(1 if float('$(spent_usd)') >= float('$MAX_USD') else 0)")"
  [ "$over" = "1" ] && { echo "ralph: cost budget reached (\$$MAX_USD)."; break; }

  iter=$((iter+1))
  stem="$LOGDIR/iter-$(printf '%04d' "$iter")"
  out="$stem.json"
  if [ -e "$out" ]; then out=$(mktemp "$stem.retry-XXXXXX.json") || exit 2; fi
  head_before="$(git rev-parse HEAD 2>/dev/null || echo none)"
  sig_before="$(queue_signature)"
  # tell the agent which iteration it is (STATE.md carries the human-readable copy)
  printf '%s\n' "$iter" > "$LOOP_DIR/.iteration"

  start=$(date +%s)
  timeout "${ITER_TIMEOUT_MIN}m" bash -c "$AGENT_CMD" < "$PROMPT" > "$out" 2> "$out.err"
  rc=$?
  secs=$(( $(date +%s) - start ))
  outcome=$(record_usage "$iter" "$out" "$rc" "$secs") || exit 2

  if [ "$outcome" = limit ]; then
    if [ "$on_limit" = handoff ]; then
      echo "ralph: $agent usage limit at iteration $iter. Resume with --agent claude or --agent codex."
      result=75
      break
    fi
    remaining="${LIMIT_SLEEP_SECS:-900}"
    echo "ralph: usage limit reached at iteration $iter; sleeping ${remaining}s then retrying (not counted as a stall)."
    iter=$((iter-1))
    while [ "$remaining" -gt 0 ] && [ ! -f "$LOOP_DIR/PAUSE" ] && [ ! -f "$LOOP_DIR/STOP" ]; do
      chunk=5
      [ "$remaining" -lt "$chunk" ] && chunk="$remaining"
      sleep "$chunk"
      remaining=$((remaining-chunk))
    done
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

exit "$result"
