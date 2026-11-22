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
# Pass --agent=claude, --agent=copilot, or --agent=codex for your runner.
# Provider-specific CLI and output handling branch on this value. Loop tasks
# can read RALPH_AGENT for provider-specific steps. See loop/RUN.md.
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
    --agent=*) agent="${1#*=}"; shift ;;
    --agent|--on-limit)
      [ "$#" -ge 2 ] || { echo "ralph: $1 needs a value." >&2; exit 2; }
      if [ "$1" = --agent ]; then agent="$2"; else on_limit="$2"; fi
      shift 2 ;;
    --pause) touch "$LOOP_DIR/PAUSE"; exit $? ;;
    --resume) resume=1; shift ;;
    --help)
      echo "Usage: loop/ralph.sh [--agent=claude|copilot|codex] [--on-limit wait|handoff] [--resume]"
      echo "       loop/ralph.sh --pause"
      exit 0 ;;
    *) echo "ralph: unknown option $1." >&2; exit 2 ;;
  esac
done
case "$agent" in claude|copilot|codex) ;; *) echo "ralph: unknown agent $agent." >&2; exit 2 ;; esac
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
# AGENT_CMD can override the selected provider command, for example in tests. It must read the
# prompt on stdin, run shell commands in the current directory, and print its result to stdout.
# Verified on Claude Code 2.1.319: no --max-turns flag exists; --max-budget-usd caps each iteration.
# NOTE: the allowlist is a guard rail, not a sandbox (python3 can do anything). Real protection:
# no credentials in the environment, no pushable remote, and a pre-push hook that refuses.
CLAUDE_AGENT_CMD='claude -p --output-format json ${RALPH_MODEL:+--model "$RALPH_MODEL"} --max-budget-usd 6 --permission-mode dontAsk --allowedTools "Read,Edit,Write,Glob,Grep,Bash(git:*),Bash(python3:*),Bash(python:*),Bash(pandoc:*),Bash(node:*),Bash(npx:*),Bash(tools/*:*),Bash(ls:*),Bash(cat:*),Bash(head:*),Bash(tail:*),Bash(wc:*),Bash(grep:*),Bash(find:*),Bash(sed:*),Bash(sort:*),Bash(diff:*),Bash(cp:*),Bash(mv:*),Bash(mkdir:*),Bash(touch:*),Bash(chmod:*),Bash(date:*),Bash(sha256sum:*),Bash(zip:*),Bash(unzip:*),Bash(echo:*),Bash(printf:*),Bash(test:*),Bash(pip:*),Bash(pip3:*),Bash(npm:*),Bash(.venv/bin/*:*),Bash(pytest:*),Bash(tar:*),Bash(rsync:*),Bash(rm:*),Bash(cd:*),Bash(awk:*),Bash(tr:*),Bash(cut:*),Bash(xargs:*),Bash(pwd:*),Bash(which:*),Bash(basename:*),Bash(dirname:*),Bash(stat:*),Bash(file:*),Bash(du:*),Bash(tee:*),Bash(uniq:*),Bash(comm:*),Bash(env:*),Bash(true:*),Bash(sleep:*),Bash(time:*)" --disallowedTools "Bash(git push:*)" "Bash(gh:*)" "Bash(curl:*)" "Bash(wget:*)" "Bash(ssh:*)"'
case "$agent" in
  claude)
    DEFAULT_AGENT_CMD="$CLAUDE_AGENT_CMD"
    # Claude needs explicit access to the pinned English source.
    ENGLISH_DIR="$(cfg english_clone_path "")"
    if [ -n "$ENGLISH_DIR" ] && [ -d "$ENGLISH_DIR" ]; then
      printf -v english_arg '%q' "$ENGLISH_DIR"
      DEFAULT_AGENT_CMD+=" --add-dir $english_arg"
    fi
    ;;
  copilot)
    DEFAULT_AGENT_CMD='copilot --no-auto-update --no-ask-user --assisted-approval --disable-builtin-mcps --output-format json ${RALPH_MODEL:+--model "$RALPH_MODEL"} ${RALPH_EFFORT:+--reasoning-effort "$RALPH_EFFORT"} --allow-tool="shell(python3)" --allow-tool="shell(python)" --allow-tool="shell(tools/*)" --allow-tool="shell(git)" --allow-tool="write" --deny-tool="shell(git push)" --deny-tool="shell(gh)" --deny-tool="shell(curl)" --deny-tool="shell(wget)" --deny-tool="shell(ssh)" --prompt "$(cat)"'
    ;;
  codex)
    DEFAULT_AGENT_CMD='codex exec ${RALPH_MODEL:+-m "$RALPH_MODEL"} ${RALPH_EFFORT_CFG:+-c "$RALPH_EFFORT_CFG"} --approve-for-me --color never --json -'
    ;;
esac
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

# ---- model tiers: which model runs the next task (plan section 11.7) ----
# The agent picks its own task inside the iteration, so the driver previews the same pick
# (tools/next_task.py is deterministic) to choose a tier. Tier "light" is used only when the
# task says so ("tier": "light"), or its kind is in tier_light_kinds, and it has not failed
# before (attempts 0). Anything unknown, or TIER_OVERRIDE=standard|light, falls back safely.
TIER_LIGHT_KINDS="$(cfg tier_light_kinds "packet")"
preview_task() {  # prints: id<TAB>kind<TAB>tier<TAB>attempts   (empty fields when nothing is eligible)
  python3 tools/next_task.py 2>/dev/null | python3 -I -c '
import json, sys
line = sys.stdin.readline()
if not line.startswith("TASK "):
    print("-\t-\t-\t0\t0"); raise SystemExit
t = json.loads(line[5:])
print("\t".join([str(t.get("id") or "-"), str(t.get("kind") or "-"), str(t.get("tier") or "-"), str(t.get("attempts") or 0), str(t.get("words") or 0)]))
'
}
choose_tier() {  # choose_tier kind explicit_tier attempts
  local kind="$1" explicit="$2" attempts="$3" tier=standard k
  if [ "$explicit" = light ]; then tier=light; fi
  for k in $TIER_LIGHT_KINDS; do [ "$k" = "$kind" ] && [ -z "$explicit" ] && tier=light; done
  [ "$explicit" = standard ] && tier=standard
  [ "${attempts:-0}" -ge 1 ] 2>/dev/null && tier=standard   # a retried task always gets the standard model
  [ -n "${TIER_OVERRIDE:-}" ] && tier="$TIER_OVERRIDE"
  printf '%s' "$tier"
}

record_usage() {  # record_usage iter jsonfile rc seconds
  python3 -I - "$1" "$2" "$3" "$4" "$LEDGER" "$agent" "${5:-}" "${6:-}" "${7:-}" "${8:-}" "${9:-}" "${10:-0}" "${11:-0}" "${12:-}" <<'PY'
import glob, json, os, pathlib, re, sys, time
it, path, rc, secs, ledger, agent, task_id, tier, want_model, want_effort, kind, attempts, words, head_before = sys.argv[1:]
rec = {"iteration": int(it), "ts": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
       "agent": agent, "exit_code": int(rc), "seconds": int(secs), "cost_usd": None,
       "input_tokens": None, "output_tokens": None, "result_tail": "",
       "task": task_id, "kind": kind, "attempts": int(attempts or 0), "unit_words": int(words or 0),
       "tier": tier, "model_requested": want_model, "effort_requested": want_effort,
       "tok_fresh_in": None, "tok_cache_read": None, "tok_cache_write": None, "tok_out": None,
       "tok_reasoning": None, "api_calls": None, "cost_est_usd": None}
reported = {}      # model name -> output tokens when the CLI says, else call count
thread_id = ""
raw = pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
result = ""
errors = []
usage = {}
quota_error = False
if agent == "claude":
    try:
        data = json.loads(raw)
    except ValueError:
        data = {}
    if isinstance(data, dict):
        rec["cost_usd"] = data.get("total_cost_usd", data.get("cost_usd"))
        usage = data.get("usage") or {}
        for name, u in (data.get("modelUsage") or {}).items():
            reported[name] = int((u or {}).get("outputTokens") or 0)
        rec.update(tok_fresh_in=(usage.get("input_tokens") or 0) + (usage.get("cache_creation_input_tokens") or 0),
                   tok_cache_read=usage.get("cache_read_input_tokens"), tok_cache_write=usage.get("cache_creation_input_tokens"),
                   tok_out=usage.get("output_tokens"), api_calls=data.get("num_turns"))
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
        if agent == "copilot":
            data = event.get("data") or {}
            if event_type in ("model.call_start", "model.call_final_result") and data.get("model"):
                reported[data["model"]] = reported.get(data["model"], 0) + 1
            if event_type == "assistant.message" and not data.get("toolRequests"):
                result = str(data.get("content") or "")
            elif event_type == "assistant.usage":
                # Copilot reports usage per API call and its cost field is not USD.
                for key, field in (("input_tokens", "inputTokens"), ("output_tokens", "outputTokens")):
                    if isinstance(data.get(field), int):
                        usage[key] = usage.get(key, 0) + data[field]
            elif event_type == "session.usage_checkpoint":
                snap = data.get("accountingSnapshot") or {}
                mm = snap.get("modelMetrics") or {}
                if mm:
                    t = {"in": 0, "read": 0, "write": 0, "out": 0, "reason": 0, "calls": 0}
                    reported = {}
                    for name, m in mm.items():
                        u = (m or {}).get("usage") or {}
                        t["in"] += u.get("inputTokens") or 0
                        t["read"] += u.get("cacheReadTokens") or 0
                        t["write"] += u.get("cacheWriteTokens") or 0
                        t["out"] += u.get("outputTokens") or 0
                        t["reason"] += u.get("reasoningTokens") or 0
                        t["calls"] += ((m or {}).get("requests") or {}).get("count") or 0
                        reported[name] = u.get("outputTokens") or 0
                    rec.update(tok_fresh_in=max(t["in"] - t["read"] - t["write"], 0), tok_cache_read=t["read"],
                               tok_cache_write=t["write"], tok_out=t["out"], tok_reasoning=t["reason"], api_calls=t["calls"])
                    nano = snap.get("totalNanoAiu")
                    if isinstance(nano, (int, float)):
                        rec["ai_credits"] = round(nano / 1e9, 4)
                        rec["cost_est_usd"] = round(nano / 1e9 * 0.01, 4)   # 1 AI credit = $0.01; an estimate, not the USD cap
                    for entry in (data.get("promptCacheBreakState") or []):
                        for mdl in (entry.get("models") or {}).values():
                            if mdl.get("reasoning_effort"):
                                rec["effort_reported"] = mdl["reasoning_effort"]
            elif event_type == "session.error":
                errors.append(str(data.get("message") or ""))
                quota_error |= data.get("errorType") == "quota"
        elif event_type == "thread.started":
            thread_id = str(event.get("thread_id") or "")
        elif event_type == "turn.completed":
            usage = event.get("usage") or {}
            cached = usage.get("cached_input_tokens") or 0
            rec.update(tok_fresh_in=max((usage.get("input_tokens") or 0) - cached, 0), tok_cache_read=cached,
                       tok_cache_write=usage.get("cache_write_input_tokens"), tok_out=usage.get("output_tokens"),
                       tok_reasoning=usage.get("reasoning_output_tokens"))
        elif event_type == "item.completed":
            item = event.get("item") or {}
            if item.get("type") == "agent_message":
                result = str(item.get("text") or "")
        elif event_type in ("error", "turn.failed"):
            errors.append(str(event.get("error") or event.get("message") or ""))
if agent == "codex" and thread_id:
    # codex exec --json never names the model; its session file does (turn_context).
    home = os.environ.get("CODEX_HOME") or os.path.expanduser("~/.codex")
    for f in glob.glob(os.path.join(home, "sessions", "**", f"rollout-*{thread_id}.jsonl"), recursive=True):
        text = pathlib.Path(f).read_text(encoding="utf-8", errors="replace")
        for m in re.finditer(r'"model":"([^"]+)"', text):
            reported[m.group(1)] = reported.get(m.group(1), 0) + 1
        eff = re.findall(r'"effort":"([^"]+)"', text)
        if eff:
            rec["effort_reported"] = eff[-1]
primary = max(reported, key=reported.get) if reported else ""
norm = lambda s: re.sub(r"[^a-z0-9]", "", s.lower())
rec["model_reported"] = primary
rec["models_all"] = sorted(reported)
rec["model_mismatch"] = bool(want_model) and (not primary or norm(want_model) not in norm(primary))
print(f"ralph: iteration {it} model evidence: agent={agent} requested={want_model or 'cli-default'} "
      f"reported={primary or 'NOT-REPORTED'}"
      + (f" (also: {', '.join(m for m in sorted(reported) if m != primary)})" if len(reported) > 1 else "")
      + (f" effort={rec.get('effort_reported') or want_effort}" if (want_effort or rec.get('effort_reported')) else "")
      + ("  MISMATCH" if rec["model_mismatch"] else ""), file=sys.stderr)
if int(rc):
    errors.append(pathlib.Path(path + ".err").read_text(encoding="utf-8", errors="replace").strip())
error_text = "\n".join(filter(None, errors))
rec["result_tail"] = ((error_text if int(rc) or quota_error else "") or result)[-300:]
rec["input_tokens"] = usage.get("input_tokens")
rec["output_tokens"] = usage.get("output_tokens")
m = re.search(r"LOOP-RESULT:\s*(\S+)\s+(done|blocked|partial)", result or "")
rec["loop_result"] = m.group(2) if m else None
try:
    import subprocess
    head_after = subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    if head_after and head_before and head_after != head_before and head_before != "none":
        rec["commit"] = head_after[:12]
        stat = subprocess.run(["git", "diff", "--shortstat", head_before, head_after], capture_output=True, text=True).stdout
        for key, pat in (("files_changed", r"(\d+) files? changed"), ("lines_added", r"(\d+) insertions?"), ("lines_deleted", r"(\d+) deletions?")):
            mm_ = re.search(pat, stat)
            rec[key] = int(mm_.group(1)) if mm_ else 0
        subject = subprocess.run(["git", "log", "-1", "--format=%s", head_after], capture_output=True, text=True).stdout
        sm = re.search(r"(\d+) segments?", subject)
        if sm:
            rec["unit_segments"] = int(sm.group(1))
except Exception:
    pass
rec["usage_limited"] = quota_error or (int(rc) != 0 and bool(re.search(
    r"\bhit your\b[^\n]{0,100}\blimit\b|\busage[_ ]limit[_ ]reached\b", error_text, re.I
)))
with open(ledger, "a", encoding="utf-8") as f:
    f.write(json.dumps(rec, ensure_ascii=False) + "\n")
print("limit" if rec["usage_limited"] else "recorded")
PY
}

# Interactive checkpoints can advance STATE.md without a driver usage entry.
iter=$(python3 -I - "$LEDGER" "$STATE" <<'PY'
import json, pathlib, re, sys
ledger, state = map(pathlib.Path, sys.argv[1:])
last_usage = max((json.loads(line)["iteration"] for line in ledger.read_text().splitlines()
                  if line.strip()), default=0) if ledger.exists() else 0
checkpoint = re.search(r"^- \*\*Iteration:\*\*\s+(\d+)\b", state.read_text(), re.M) if state.exists() else None
print(max(last_usage, int(checkpoint[1]) if checkpoint else 0))
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

  IFS=$'\t' read -r p_id p_kind p_tier p_attempts p_words <<< "$(preview_task)"
  [ "$p_id" = - ] && p_id=""; [ "$p_kind" = - ] && p_kind=""; [ "$p_tier" = - ] && p_tier=""
  tier="$(choose_tier "$p_kind" "$p_tier" "$p_attempts")"
  model="$(cfg "${agent}_model_${tier}" "")"
  effort="$(cfg "${agent}_effort_${tier}" "")"
  export RALPH_MODEL="$model" RALPH_EFFORT="$effort" RALPH_TIER="$tier" RALPH_TASK_PREVIEW="$p_id"
  export RALPH_EFFORT_CFG=""
  [ "$agent" = codex ] && [ -n "$effort" ] && RALPH_EFFORT_CFG="model_reasoning_effort=\"$effort\""
  echo "ralph: iteration $iter starting: task=${p_id:-none} kind=${p_kind:-none} tier=$tier agent=$agent model=${model:-cli-default} effort=${effort:-default}"

  start=$(date +%s)
  timeout "${ITER_TIMEOUT_MIN}m" bash -c "$AGENT_CMD" < "$PROMPT" > "$out" 2> "$out.err"
  rc=$?
  secs=$(( $(date +%s) - start ))
  outcome=$(record_usage "$iter" "$out" "$rc" "$secs" "$p_id" "$tier" "$model" "$effort" "$p_kind" "$p_attempts" "$p_words" "$head_before") || exit 2

  if [ "$outcome" = limit ]; then
    if [ "$on_limit" = handoff ]; then
      echo "ralph: $agent usage limit at iteration $iter. Resume with --agent=claude, --agent=copilot, or --agent=codex."
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
