"""Set the status of one task in loop/queue/seed.jsonl without touching other lines.

Usage: python3 tools/seedtask.py TASK_ID doing ITERATION
       python3 tools/seedtask.py TASK_ID done|blocked|todo [NOTES]
"""
import datetime
import json
import sys

PATH = "loop/queue/seed.jsonl"


def main(argv):
    task_id, status = argv[1], argv[2]
    extra = argv[3] if len(argv) > 3 else None
    out = []
    found = False
    with open(PATH, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                t = json.loads(line)
                if t["id"] == task_id:
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
    if not found:
        print("no such task: " + task_id)
        return 1
    with open(PATH, "w", encoding="utf-8") as f:
        f.write("".join(out))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
