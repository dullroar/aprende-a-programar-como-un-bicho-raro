"""Set the status of one task in the loop queue without touching other lines.

Looks in loop/queue/seed.jsonl first, then in loop/queue/generated/*.jsonl.

Usage: python3 tools/seedtask.py TASK_ID doing ITERATION
       python3 tools/seedtask.py TASK_ID done|blocked|todo [NOTES]
"""
import datetime
import glob
import json
import sys

QUEUE = "loop/queue"


def queue_files(queue=QUEUE):
    return [queue + "/seed.jsonl"] + sorted(glob.glob(queue + "/generated/*.jsonl"))


def update_file(path, task_id, status, extra):
    """Rewrite one queue file if it holds task_id. Return True when the task was found."""
    out = []
    found = False
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                t = json.loads(line)
                if t.get("id") == task_id and "amend" not in t:
                    found = True
                    t["status"] = status
                    if status == "doing":
                        t["claimed_by"] = int(extra) if extra else None
                        t["claimed_at"] = datetime.datetime.now(
                            datetime.timezone.utc).isoformat(timespec="seconds")
                    else:
                        t["attempts"] = t.get("attempts", 0) + 1
                        if extra:
                            t["notes"] = extra
                    line = json.dumps(t, ensure_ascii=False, separators=(",", ":")) + "\n"
            out.append(line)
    if found:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write("".join(out))
    return found


def main(argv):
    task_id, status = argv[1], argv[2]
    extra = argv[3] if len(argv) > 3 else None
    for path in queue_files():
        try:
            if update_file(path, task_id, status, extra):
                return 0
        except FileNotFoundError:
            continue
    print("no such task: " + task_id)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
