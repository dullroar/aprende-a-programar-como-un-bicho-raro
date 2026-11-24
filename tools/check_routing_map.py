#!/usr/bin/env python3
"""tools/check_routing_map.py: check that the routing map covers every task kind of the queue.

Usage: python3 tools/check_routing_map.py [--queue DIR] [--map FILE]

Rules:
- Every `kind` in `<queue>/**/*.jsonl` has a row in the map with an allowed route.
- Every row has a non-empty reason and a measurement (or the words `no history`).
- A row for a kind that is not in the queue is allowed.

Standard library only. Exit code 0 = pass, 1 = defects.
"""
import argparse
import json
import pathlib
import sys

ROUTES = ("script", "ci", "batch", "agent-light", "agent-standard", "operator")
COLUMNS = ["kind", "route", "reason", "measurement", "expected cost change"]
ROOT = pathlib.Path(__file__).resolve().parent.parent


def queue_kinds(queue_dir):
    """Return the set of `kind` values in the queue files. A row with no `kind` is skipped."""
    kinds = set()
    for path in sorted(pathlib.Path(queue_dir).rglob("*.jsonl")):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    row = json.loads(line)
                except ValueError:
                    continue
                if isinstance(row, dict) and isinstance(row.get("kind"), str):
                    kinds.add(row["kind"])
    return kinds


def _cells(line):
    parts = line.strip().strip("|").split("|")
    return [p.strip().strip("`").strip() if i < 2 else p.strip() for i, p in enumerate(parts)]


def map_rows(map_path):
    """Return (rows, defects). Each row is a dict with the table columns."""
    rows, defects = [], []
    header_seen = False
    with open(map_path, encoding="utf-8") as f:
        for line in f:
            if not line.lstrip().startswith("|"):
                continue
            cells = _cells(line)
            if not header_seen:
                if [c.lower() for c in cells] == COLUMNS:
                    header_seen = True
                continue
            if all(set(c) <= set("-: ") for c in cells):
                continue
            if len(cells) != len(COLUMNS):
                defects.append("bad row (expected %d columns): %s" % (len(COLUMNS), line.strip()))
                continue
            rows.append(dict(zip(COLUMNS, cells)))
    if not header_seen:
        defects.append("no table with the columns: " + " | ".join(COLUMNS))
    return rows, defects


def check(queue_dir, map_path):
    kinds = queue_kinds(queue_dir)
    try:
        rows, defects = map_rows(map_path)
    except FileNotFoundError:
        return ["map file not found: %s" % map_path]
    covered = set()
    for row in rows:
        name = row["kind"]
        if row["route"] not in ROUTES:
            defects.append("kind %s: unknown route %r" % (name, row["route"]))
        elif name in kinds:
            covered.add(name)
        if not row["reason"]:
            defects.append("kind %s (route %s): empty reason" % (name, row["route"]))
        if not row["measurement"]:
            defects.append("kind %s (route %s): empty measurement" % (name, row["route"]))
    for name in sorted(kinds - covered):
        defects.append("kind %s: no row with an allowed route" % name)
    return defects


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--queue", default=str(ROOT / "loop" / "queue"))
    ap.add_argument("--map", default=str(ROOT / "translation" / "routing.md"))
    args = ap.parse_args(argv)
    defects = check(args.queue, args.map)
    for d in defects:
        print("DEFECT: " + d)
    if defects:
        return 1
    print("routing map ok")
    return 0


if __name__ == "__main__":
    sys.exit(main())
