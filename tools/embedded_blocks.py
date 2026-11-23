#!/usr/bin/env python3
"""Embedded-block table (Part II, task S1-005).

For every embedded block that tools/code_inventory.py found (a string in one language that holds
another, for example SQL inside a shell script), record the host and the embedded language.
Reads translation/part2/code-inventory.jsonl; writes translation/part2/embedded-blocks.jsonl (one
row per block) and translation/part2/embedded-blocks.md (counts by host and language). Both are
generated, so --check fails if either differs from a fresh rendering.

Usage:
  python3 -I tools/embedded_blocks.py --write
  python3 -I tools/embedded_blocks.py --check
"""
import collections
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
INVENTORY = os.path.join(ROOT, "translation", "part2", "code-inventory.jsonl")
OUT_JSONL = os.path.join(ROOT, "translation", "part2", "embedded-blocks.jsonl")
OUT_MD = os.path.join(ROOT, "translation", "part2", "embedded-blocks.md")


def rows_from(records):
    rows = []
    for r in records:
        for e in r.get("embedded", []):
            rows.append({"path": r["path"], "host": r["host"], "embedded": e["lang"], "kind": e.get("kind", ""),
                         "line": e.get("line", 0), "end_line": e.get("end_line", e.get("line", 0))})
    rows.sort(key=lambda x: (x["path"], x["line"], x["embedded"]))
    return rows


def render_jsonl(rows):
    return "".join(json.dumps(r, sort_keys=True, separators=(",", ":")) + "\n" for r in rows)


def render_md(rows):
    counts = collections.Counter((r["host"], r["embedded"]) for r in rows)
    files = collections.defaultdict(set)
    for r in rows:
        files[(r["host"], r["embedded"])].add(r["path"])
    lines = ["<!-- GENERATED from code-inventory.jsonl by tools/embedded_blocks.py; do not edit by hand -->",
             "# Embedded blocks: host and embedded language", "",
             "Each embedded block keeps the protected tokens of its embedded language (see",
             "translation/protected-tokens/) while the host language owns the quoting around it.", "",
             "| Host | Embedded | Blocks | Files |", "| --- | --- | ---: | ---: |"]
    for (host, emb) in sorted(counts):
        lines.append("| %s | %s | %d | %d |" % (host, emb, counts[(host, emb)], len(files[(host, emb)])))
    lines += ["", "Total blocks: %d. Row-level data: embedded-blocks.jsonl." % len(rows)]
    return "\n".join(lines) + "\n"


def load_inventory():
    with open(INVENTORY, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def read(path):
    if not os.path.exists(path):
        return None
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def check(records=None):
    rows = rows_from(load_inventory() if records is None else records)
    problems = []
    if read(OUT_JSONL) != render_jsonl(rows):
        problems.append("embedded-blocks.jsonl differs from the inventory")
    if read(OUT_MD) != render_md(rows):
        problems.append("embedded-blocks.md differs from the inventory")
    return problems


def main(argv):
    mode = argv[1] if len(argv) > 1 else "--check"
    if mode == "--write":
        rows = rows_from(load_inventory())
        with open(OUT_JSONL, "w", encoding="utf-8", newline="\n") as f:
            f.write(render_jsonl(rows))
        with open(OUT_MD, "w", encoding="utf-8", newline="\n") as f:
            f.write(render_md(rows))
        print("wrote %d embedded blocks" % len(rows))
        return 0
    if mode == "--check":
        problems = check()
        print("\n".join(problems) if problems else "embedded blocks OK")
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
