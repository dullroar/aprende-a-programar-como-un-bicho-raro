#!/usr/bin/env python3
"""resume_test: plan stage 3 resume test (task P3-009), run against the REAL loop/ralph.sh, tools/next_task.py and
tools/seedtask.py in a throwaway git repo under translation/work/resume-test/ (git-ignored).

The scenario (no model is called; the agents are small scripts that obey the PROMPT.md procedure):

  run 1  AGENT_CMD = "python3 agents/agent.py --name A --mode partial-stop"
         Agent A claims T-1, finishes segments 1 and 2 of 4, leaves T-1 `todo` with the note "resume at segment 3",
         writes loop/HANDOFF.md, commits, and creates loop/STOP (the human pressing stop mid-task).
         ralph.sh must print "STOP sentinel found" and exit without starting a second iteration.
  gap    the human removes STOP. The repository must be consistent and mid-task (check_stopped).
  run 2  AGENT_CMD = "python3 agents/agent.py --name B --mode resume"   (a different invocation)
         Agent B must read HANDOFF.md and the queue, continue T-1 at segment 3 (not restart it), finish T-2, and write
         DONE. ralph.sh must continue the iteration numbering from the ledger.
  check  check_resume(): the part file has segments 1 to 4 once each, the log shows the resume, the queue is done.

Negative cases: an agent that restarts instead of resuming (--mode restart) must fail check_resume; STOP present at
the start must run no agent; a stalled agent must trip the circuit breaker; a held lock must refuse a second loop.

  python3 -I tools/resume_test.py            run the scenario and the negative cases, write the report
  python3 -I tools/resume_test.py --report   also write translation/reviews/resume-test.md

verify.run_release runs run_all() as part of "negative fixtures". Exit codes: 0 good, 1 problems.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
WORK = os.path.join(ROOT, "translation", "work", "resume-test")
REPORT = os.path.join(ROOT, "translation", "reviews", "resume-test.md")
SEGMENTS = 4

AGENT = r'''
import argparse, json, os, re, subprocess, sys

ap = argparse.ArgumentParser()
ap.add_argument("--name", required=True)
ap.add_argument("--mode", required=True, choices=["partial-stop", "resume", "restart", "idle"])
a = ap.parse_args()
sys.stdin.read()
it = int(open("loop/.iteration").read().strip())
with open("loop/logs/calls.log", "a") as f:
    f.write("%d %s %s\n" % (it, a.name, a.mode))


def run(*argv):
    return subprocess.run(list(argv), capture_output=True, text=True)


def finish(text):
    print(json.dumps({"total_cost_usd": 0, "result": text}))
    sys.exit(0)


def commit(tid, msg):
    run("git", "add", "-A")
    run("git", "commit", "-q", "-m", "loop(%s): %s" % (tid, msg))


def log(line):
    with open("loop/log.md", "a") as f:
        f.write(line + "\n")


if a.mode == "idle":
    finish("did nothing")
r = run(sys.executable, "tools/next_task.py")
if not r.stdout.startswith("TASK "):
    if r.stdout.startswith("NONE-COMPLETE"):
        with open("loop/DONE", "w") as f:
            f.write("DONE\n")
        commit("final", "queue complete")
    finish(r.stdout.strip())
task = json.loads(r.stdout[5:])
tid = task["id"]
start = 1
m = re.search(r"resume at segment (\d+)", task.get("notes") or "")
handoff = os.path.exists("loop/HANDOFF.md")
if a.mode == "resume" and m:
    start = int(m.group(1))
run(sys.executable, "tools/seedtask.py", tid, "doing", str(it))
last = 2 if a.mode == "partial-stop" else 4
os.makedirs("work", exist_ok=True)
with open("work/%s.part" % tid, "a") as f:
    for n in range(start, last + 1):
        f.write("%s segment %d\n" % (tid, n))
if a.mode == "partial-stop":
    run(sys.executable, "tools/seedtask.py", tid, "todo", "segments 1 to 2 done; resume at segment 3")
    with open("loop/HANDOFF.md", "w") as f:
        f.write("# HANDOFF\n\nStopped mid-task. %s: segments 1 to 2 done; resume at segment 3.\n" % tid)
    log("%d %s partial segments 1 to 2 done; stopped by STOP" % (it, tid))
    commit(tid, "partial")
    with open("loop/STOP", "w") as f:
        f.write("stop\n")
    finish("partial")
run(sys.executable, "tools/seedtask.py", tid, "done", "finished")
if start > 1 and handoff:
    os.remove("loop/HANDOFF.md")
    log("%d %s done resumed from HANDOFF.md and the queue at segment %d" % (it, tid, start))
else:
    log("%d %s done all segments" % (it, tid))
commit(tid, "done")
finish("done")
'''

CONFIG = """# scratch CONFIG for the resume test
max_iterations: 10
max_usd: 100
iteration_timeout_minutes: 1
max_stalled_iterations: 2
sleep_seconds_between_iterations: 0
"""

SEED = [
    {"id": "T-1", "stage": 1, "kind": "translate", "title": "first task", "deps": [], "status": "todo", "attempts": 0},
    {"id": "T-2", "stage": 1, "kind": "translate", "title": "second task", "deps": ["T-1"], "status": "todo", "attempts": 0},
]

IGNORE = "loop/logs/\nloop/.lock\nloop/.iteration\nloop/ledger/\nloop/STOP\n__pycache__/\n"


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)


def read(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError:
        return ""


def git(dest, *argv):
    return subprocess.run(["git", *argv], cwd=dest, capture_output=True, text=True)


def build_scratch(name):
    """A fresh repo with the real driver and queue tools, a two-task queue and an agent script."""
    dest = os.path.join(WORK, name)
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    for rel in ("loop/ralph.sh", "tools/next_task.py", "tools/seedtask.py"):
        os.makedirs(os.path.dirname(os.path.join(dest, rel)), exist_ok=True)
        shutil.copyfile(os.path.join(ROOT, rel), os.path.join(dest, rel))
    write(os.path.join(dest, "loop", "PROMPT.md"), "One iteration. Do one task.\n")
    write(os.path.join(dest, "loop", "CONFIG.yaml"), CONFIG)
    write(os.path.join(dest, "loop", "log.md"), "")
    write(os.path.join(dest, "loop", "queue", "seed.jsonl"), "".join(json.dumps(t) + "\n" for t in SEED))
    write(os.path.join(dest, "agents", "agent.py"), AGENT)
    write(os.path.join(dest, ".gitignore"), IGNORE)
    git(dest, "init", "-q")
    git(dest, "config", "user.name", "resume-test")
    git(dest, "config", "user.email", "resume-test@example.invalid")
    git(dest, "add", "-A")
    git(dest, "commit", "-q", "-m", "scratch start")
    return dest


def agent_cmd(name, mode):
    return "%s agents/agent.py --name %s --mode %s" % (sys.executable, name, mode)


def run_ralph(dest, cmd, timeout=120, options=()):
    """Run the real ralph.sh in the scratch repo with AGENT_CMD=cmd; return (returncode, output)."""
    env = dict(os.environ)
    env["AGENT_CMD"] = cmd
    env["SLEEP_SECS"] = "0"
    for k in ("MAX_ITER", "MAX_USD", "MAX_STALL", "ITER_TIMEOUT_MIN"):
        env.pop(k, None)
    r = subprocess.run(["bash", os.path.join(dest, "loop", "ralph.sh"), *options], cwd=dest, env=env,
                       capture_output=True, text=True, timeout=timeout)
    return r.returncode, r.stdout + r.stderr


def calls(dest):
    out = []
    for ln in read(os.path.join(dest, "loop", "logs", "calls.log")).splitlines():
        parts = ln.split()
        if len(parts) == 3:
            out.append((int(parts[0]), parts[1], parts[2]))
    return out


def queue(dest):
    return {t["id"]: t for t in (json.loads(l) for l in read(os.path.join(dest, "loop", "queue", "seed.jsonl")).splitlines() if l.strip())}


def part_lines(dest, tid):
    return read(os.path.join(dest, "work", tid + ".part")).splitlines()


def check_stopped(dest, out):
    """The state between the runs: stopped mid-task and consistent."""
    p = []
    if "STOP sentinel found" not in out:
        p.append("run 1: ralph.sh did not report the STOP sentinel")
    if not os.path.exists(os.path.join(dest, "loop", "STOP")):
        p.append("run 1: loop/STOP is missing")
    if [c[1] for c in calls(dest)] != ["A"]:
        p.append("run 1: expected exactly one agent call (A), got %s" % calls(dest))
    t1 = queue(dest).get("T-1", {})
    if t1.get("status") != "todo" or "resume at segment 3" not in (t1.get("notes") or ""):
        p.append("run 1: T-1 must be todo with a precise resume note, got %s/%r" % (t1.get("status"), t1.get("notes")))
    if queue(dest).get("T-2", {}).get("status") != "todo":
        p.append("run 1: T-2 must be untouched")
    if not os.path.exists(os.path.join(dest, "loop", "HANDOFF.md")):
        p.append("run 1: loop/HANDOFF.md is missing")
    if part_lines(dest, "T-1") != ["T-1 segment 1", "T-1 segment 2"]:
        p.append("run 1: partial work is not segments 1 and 2: %s" % part_lines(dest, "T-1"))
    if git(dest, "status", "--short").stdout.strip():
        p.append("run 1: working tree is dirty after the stop: %r" % git(dest, "status", "--short").stdout)
    return p


def check_resume(dest, out1, out2):
    """After run 2: the second invocation resumed from HANDOFF.md and the queue instead of starting over."""
    p = []
    if "DONE sentinel found" not in out2:
        p.append("run 2: ralph.sh did not end on the DONE sentinel")
    cs = calls(dest)
    names = [c[1] for c in cs]
    if not names or names[0] != "A" or len(set(names[1:])) != 1 or names[1:2] != ["B"]:
        p.append("agent invocations are not A then B only: %s" % cs)
    if [c[0] for c in cs] != list(range(1, len(cs) + 1)):
        p.append("iteration numbers did not continue across the restart: %s" % [c[0] for c in cs])
    want = ["T-1 segment %d" % n for n in range(1, SEGMENTS + 1)]
    if part_lines(dest, "T-1") != want:
        p.append("T-1 was not resumed at segment 3 (segments seen: %s)" % part_lines(dest, "T-1"))
    q = queue(dest)
    for tid in ("T-1", "T-2"):
        if q.get(tid, {}).get("status") != "done":
            p.append("%s is not done" % tid)
    lines = read(os.path.join(dest, "loop", "log.md")).splitlines()
    partial = [i for i, l in enumerate(lines) if l.startswith("1 T-1 partial")]
    resumed = [i for i, l in enumerate(lines) if l.startswith("2 T-1 done") and "resumed from HANDOFF.md" in l and "segment 3" in l]
    if not partial:
        p.append("loop/log.md has no partial line for T-1 from iteration 1")
    if not resumed:
        p.append("loop/log.md does not show the resume of T-1 in iteration 2")
    if partial and resumed and partial[0] > resumed[0]:
        p.append("loop/log.md lists the resume before the stop")
    if os.path.exists(os.path.join(dest, "loop", "HANDOFF.md")):
        p.append("loop/HANDOFF.md was not consumed")
    if os.path.exists(os.path.join(dest, "loop", "STOP")):
        p.append("loop/STOP is still there")
    if not os.path.exists(os.path.join(dest, "loop", "DONE")):
        p.append("loop/DONE is missing")
    subjects = git(dest, "log", "--format=%s").stdout.splitlines()
    if sum(1 for s in subjects if s.startswith("loop(T-1)")) != 2:
        p.append("expected two T-1 commits (partial, done), got %s" % subjects)
    ledger = [l for l in read(os.path.join(dest, "loop", "ledger", "usage.jsonl")).splitlines() if l.strip()]
    if len(ledger) != len(cs):
        p.append("ledger has %d rows for %d agent calls" % (len(ledger), len(cs)))
    return p


def scenario(name="main", mode_b="resume"):
    """Run the two-run scenario; return (dest, out1, out2, problems)."""
    dest = build_scratch(name)
    rc1, out1 = run_ralph(dest, agent_cmd("A", "partial-stop"))
    problems = check_stopped(dest, out1)
    if rc1 != 0:
        problems.append("run 1: ralph.sh exited %d" % rc1)
    os.remove(os.path.join(dest, "loop", "STOP"))  # the human lets it run again
    rc2, out2 = run_ralph(dest, agent_cmd("B", mode_b))
    if rc2 != 0:
        problems.append("run 2: ralph.sh exited %d" % rc2)
    return dest, out1, out2, problems + check_resume(dest, out1, out2)


def negative_stop_first():
    """STOP present at the start: the driver must not call any agent."""
    dest = build_scratch("neg-stop")
    write(os.path.join(dest, "loop", "STOP"), "stop\n")
    rc, out = run_ralph(dest, agent_cmd("A", "resume"))
    p = []
    if "STOP sentinel found" not in out:
        p.append("STOP at the start was not reported")
    if calls(dest):
        p.append("an agent ran although STOP existed: %s" % calls(dest))
    return p


def negative_stall():
    """An agent that makes no progress trips the circuit breaker (2 stalls) and says so in blockers.md."""
    dest = build_scratch("neg-stall")
    rc, out = run_ralph(dest, agent_cmd("I", "idle"))
    p = []
    if "circuit breaker" not in out:
        p.append("no circuit breaker message: %r" % out[-300:])
    if "stall breaker" not in read(os.path.join(dest, "loop", "blockers.md")):
        p.append("blockers.md has no stall breaker line")
    if len(calls(dest)) != 2:
        p.append("expected 2 calls before the breaker, got %d" % len(calls(dest)))
    return p


def negative_lock():
    """A second loop while the lock is held must refuse (exit 3) and call no agent."""
    dest = build_scratch("neg-lock")
    os.makedirs(os.path.join(dest, "loop"), exist_ok=True)
    holder = subprocess.Popen(["flock", "-n", os.path.join(dest, "loop", ".lock"), "sleep", "20"])
    try:
        import time
        time.sleep(0.5)
        rc, out = run_ralph(dest, agent_cmd("A", "resume"))
    finally:
        holder.kill()
        holder.wait()
    p = []
    if rc != 3 or "another loop is running" not in out:
        p.append("second loop was not refused (rc=%s)" % rc)
    if calls(dest):
        p.append("an agent ran while the lock was held")
    return p


def provider_handoff():
    """Both quota formats release the lock, and a fresh claim survives the switch."""
    dest = build_scratch("provider-handoff")
    write(os.path.join(dest, "agents", "quota.py"), """import json, os, subprocess, sys

sys.stdin.read()
agent = os.environ["RALPH_AGENT"]
if agent == "claude":
    subprocess.run([sys.executable, "tools/seedtask.py", "T-1", "doing", "1"], check=True)
    print(json.dumps({"is_error": True, "result": "You've hit your 5-hour limit"}))
else:
    result = subprocess.run([sys.executable, "tools/next_task.py", "--id"],
                            capture_output=True, text=True, check=True)
    if result.stdout.strip() != "TASK T-1":
        sys.exit("Codex did not reclaim the fresh claim")
    print(json.dumps({"type": "turn.failed", "error": {"message": "usage_limit_reached"}}))
sys.exit(1)
""")
    cmd = "%s agents/quota.py" % sys.executable
    problems = []
    for provider in ("claude", "codex"):
        rc, out = run_ralph(dest, cmd, options=("--agent", provider, "--on-limit", "handoff"))
        if rc != 75 or provider + " usage limit" not in out:
            problems.append("%s did not hand off (rc=%d): %s" % (provider, rc, out))
    rc, out = run_ralph(dest, agent_cmd("A", "resume"), options=("--agent", "claude"))
    if rc or "DONE sentinel found" not in out or calls(dest)[0][0] != 3:
        problems.append("Claude did not continue after Codex handed back the queue")
    ledger = [json.loads(l) for l in read(os.path.join(dest, "loop", "ledger", "usage.jsonl")).splitlines()]
    if [(r["agent"], r["usage_limited"]) for r in ledger[:2]] != [("claude", True), ("codex", True)]:
        problems.append("quota handoff was not recorded for both providers")
    return problems


def run_all():
    """Problems for verify --release: the real scenario must pass, every negative case must show its gate armed."""
    problems = []
    _, _, _, p = scenario("main")
    problems += ["resume test: " + x for x in p]
    _, _, _, bad = scenario("neg-restart", mode_b="restart")
    if not any("not resumed" in x for x in bad):
        problems.append("resume test: an agent that restarts instead of resuming was not caught")
    for fn in (negative_stop_first, negative_stall, negative_lock, provider_handoff):
        problems += ["resume test (%s): %s" % (fn.__name__, x) for x in fn()]
    return problems


def render(dest, out1, out2, problems):
    lines = ["# Resume test (P3-009)", "",
             "Scratch repo `translation/work/resume-test/main`, real `loop/ralph.sh`, `tools/next_task.py`, `tools/seedtask.py`.",
             "Two driver runs with two different `AGENT_CMD` invocations; STOP between them.", "",
             "## Driver output", "", "Run 1 (agent A, `--mode partial-stop`):", "", "```"]
    lines += out1.replace(dest, "<scratch>").strip().splitlines()
    lines += ["```", "", "Run 2 (agent B, `--mode resume`):", "", "```"] + out2.replace(dest, "<scratch>").strip().splitlines() + ["```", "",
              "## Agent calls (iteration, name, mode)", "", "```"]
    lines += read(os.path.join(dest, "loop", "logs", "calls.log")).strip().splitlines()
    lines += ["```", "", "## loop/log.md in the scratch repo", "", "```"]
    lines += read(os.path.join(dest, "loop", "log.md")).strip().splitlines()
    lines += ["```", "", "## Part file work/T-1.part", "", "```"] + part_lines(dest, "T-1") + ["```", "",
              "## Verdict", "", "PASS" if not problems else "FAIL: " + "; ".join(problems), "",
              "Negative cases (all must be caught): restart instead of resume, STOP at the start, stalled agent, held lock.", ""]
    return "\n".join(lines)


def main(argv):
    dest, out1, out2, problems = scenario("main")
    bad = run_all() if not problems else problems
    if "--report" in argv:
        write(REPORT, render(dest, out1, out2, problems))
    for x in bad:
        print("PROBLEM: " + x)
    if not bad:
        print("resume test ok: stopped mid-task, resumed by a different AGENT_CMD, negative cases caught")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
