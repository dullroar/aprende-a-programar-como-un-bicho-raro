#!/usr/bin/env python3
"""tools/next_task.py: print the next eligible task of the loop queue.

Queue = loop/queue/seed.jsonl plus loop/queue/generated/*.jsonl. A generated record of the form
{"amend": "<task-id>", "add_deps": [...]} adds dependencies to an existing task (used to make the
Phase 4 gate wait for every generated task); it is not a task itself.

Eligible: status "todo" (or "doing" with a claim older than 60 minutes: stale, may be reclaimed)
and every dep exists and has status "done". Order: stage, then natural task ID.

Output and exit code (first word of stdout says which):
  TASK <json>        exit 0   the first eligible task, one JSON line
  NONE-BLOCKED       exit 1   nothing eligible and at least one task is blocked
  NONE-WAITING       exit 2   nothing eligible, nothing blocked, but tasks remain (e.g. a live claim)
  NONE-COMPLETE      exit 3   every task is done or skipped

Options:
  --id        print only the task ID after TASK
  --counts    print status counts (todo/doing/done/blocked/skipped) and exit 0
  --check     validate the queue: duplicate IDs, unknown deps, unknown amend targets, cycles;
              exit 1 on any problem
  --queue DIR use another loop/queue directory (tests)
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import re
import sys

STALE_MINUTES = 60
DEFAULT_QUEUE = "loop/queue"


def natural(s):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", s)]


def load_queue(queue_dir=DEFAULT_QUEUE):
    """Return (tasks, problems). tasks is a list of dicts with amendments applied."""
    files = [os.path.join(queue_dir, "seed.jsonl")]
    files += sorted(glob.glob(os.path.join(queue_dir, "generated", "*.jsonl")))
    tasks, amends, problems, seen = [], [], [], {}
    for path in files:
        if not os.path.exists(path):
            continue
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                if not line.strip():
                    continue
                try:
                    rec = json.loads(line)
                except ValueError as e:
                    problems.append(f"{path}:{n}: bad JSON ({e})")
                    continue
                if "amend" in rec:
                    amends.append(rec)
                    continue
                tid = rec.get("id")
                if not tid:
                    problems.append(f"{path}:{n}: record without id")
                    continue
                if tid in seen:
                    problems.append(f"duplicate task id {tid} ({seen[tid]} and {path})")
                    continue
                seen[tid] = path
                rec.setdefault("deps", [])
                rec["deps"] = list(rec["deps"])
                tasks.append(rec)
    by_id = {t["id"]: t for t in tasks}
    for a in amends:
        target = by_id.get(a["amend"])
        if target is None:
            problems.append(f"amend targets unknown task {a['amend']}")
            continue
        for d in a.get("add_deps", []):
            if d not in target["deps"]:
                target["deps"].append(d)
    return tasks, problems


def parse_time(s):
    if not s:
        return None
    try:
        dt = datetime.datetime.fromisoformat(s)
    except ValueError:
        return None
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=datetime.timezone.utc)
    return dt


def is_stale(task, now):
    """A doing task is stale when its claim is older than 60 minutes (or has no usable time)."""
    claimed = parse_time(task.get("claimed_at"))
    if claimed is None:
        return True
    return now - claimed > datetime.timedelta(minutes=STALE_MINUTES)


def find_cycles(tasks):
    by_id = {t["id"]: t for t in tasks}
    state, cycles = {}, []

    def visit(tid, path):
        if state.get(tid) == 2:
            return
        if state.get(tid) == 1:
            cycles.append(" -> ".join(path[path.index(tid):] + [tid]))
            return
        state[tid] = 1
        for d in by_id.get(tid, {}).get("deps", []):
            if d in by_id:
                visit(d, path + [tid])
        state[tid] = 2

    for t in tasks:
        visit(t["id"], [])
    return cycles


def check(tasks, problems):
    out = list(problems)
    ids = {t["id"] for t in tasks}
    for t in tasks:
        for d in t["deps"]:
            if d not in ids:
                out.append(f"{t['id']}: unknown dep {d}")
        if t["id"] in t["deps"]:
            out.append(f"{t['id']}: depends on itself")
    out += ["dependency cycle: " + c for c in find_cycles(tasks)]
    return out


def pick(tasks, now=None):
    """Return (verdict, task_or_None) where verdict is TASK/NONE-BLOCKED/NONE-WAITING/NONE-COMPLETE."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    status = {t["id"]: t.get("status", "todo") for t in tasks}
    eligible = []
    for t in tasks:
        st = t.get("status", "todo")
        if st == "doing" and is_stale(t, now):
            st = "todo"
        if st != "todo":
            continue
        if all(status.get(d) == "done" for d in t["deps"]):
            eligible.append(t)
    if eligible:
        eligible.sort(key=lambda t: (t.get("stage", 99), natural(t["id"])))
        return "TASK", eligible[0]
    open_tasks = [t for t in tasks if t.get("status", "todo") not in ("done", "skipped")]
    if not open_tasks:
        return "NONE-COMPLETE", None
    if any(t.get("status") == "blocked" for t in open_tasks):
        return "NONE-BLOCKED", None
    return "NONE-WAITING", None


def counts(tasks):
    c = {s: 0 for s in ("todo", "doing", "done", "blocked", "skipped")}
    for t in tasks:
        s = t.get("status", "todo")
        c[s] = c.get(s, 0) + 1
    return c


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--id", action="store_true")
    ap.add_argument("--counts", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--queue", default=DEFAULT_QUEUE)
    a = ap.parse_args(argv)

    tasks, problems = load_queue(a.queue)
    if a.check:
        bad = check(tasks, problems)
        for b in bad:
            print("PROBLEM: " + b)
        if not bad:
            print("queue ok: %d tasks" % len(tasks))
        return 1 if bad else 0
    if a.counts:
        c = counts(tasks)
        print(" | ".join(f"{k} {v}" for k, v in c.items()))
        return 0
    verdict, task = pick(tasks)
    if task is not None:
        print("TASK " + (task["id"] if a.id else json.dumps(task, ensure_ascii=False)))
        return 0
    print(verdict)
    return {"NONE-BLOCKED": 1, "NONE-WAITING": 2, "NONE-COMPLETE": 3}[verdict]


if __name__ == "__main__":
    sys.exit(main())
