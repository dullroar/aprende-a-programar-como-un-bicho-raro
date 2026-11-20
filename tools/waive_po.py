#!/usr/bin/env python3
"""waive_po: clear needs-revision flags on PO entries a human or agent has judged, with a record.

Usage: python3 -I tools/waive_po.py PO_FILE TASK_ID RULES.json [--register FILE]

RULES.json: {"set": {segment_id: msgstr}, "waive": {segment_id: [invariant, reason]}}
  set    replace the msgstr (the msgid never changes), clear the fuzzy flag and the finding comment;
         use it only for text the register or glossary already fixes (a recorded heading);
  waive  keep the translator's msgstr, clear the fuzzy flag and append an exception-register row
         (id EXC-nnn, segment, invariant, reason, task). The reason must say why the check is wrong
         for this segment (product name, verb vs noun, identifier), never "to get green".
Every id must exist in the PO; an unknown id changes nothing and exits 1.
"""
import json
import os
import sys

import polib

HERE = os.path.dirname(os.path.abspath(__file__))
REGISTER = os.path.join(os.path.dirname(HERE), "translation", "exception-register.jsonl")


def waive(po_path, task, rules, register=REGISTER):
    sets, waives = rules.get("set", {}), rules.get("waive", {})
    po = polib.pofile(po_path, wrapwidth=0)
    seen = set()
    for e in po:
        sid = e.msgctxt
        if sid in sets or sid in waives:
            if sid in sets:
                e.msgstr = sets[sid]
            if "fuzzy" in e.flags:
                e.flags.remove("fuzzy")
            e.comment = ""
            seen.add(sid)
    missing = (set(sets) | set(waives)) - seen
    if missing:
        raise KeyError("segment ids not in the PO: %s" % ", ".join(sorted(missing)))
    for sid, (inv, reason) in waives.items():
        if not reason.strip():
            raise ValueError("waiver for %s has no reason" % sid)
    po.save(po_path)
    n = 0
    if os.path.isfile(register):
        with open(register, encoding="utf-8") as f:
            n = sum(1 for line in f if line.strip())
    with open(register, "a", encoding="utf-8") as f:
        for sid, (inv, reason) in waives.items():
            n += 1
            f.write(json.dumps({"id": "EXC-%03d" % n, "segment": sid, "invariant": inv, "reason": reason,
                                "task": task}, ensure_ascii=False, separators=(",", ":")) + "\n")
    return len(sets), len(waives)


def main(argv):
    args = list(argv)
    register = REGISTER
    if "--register" in args:
        i = args.index("--register")
        register = args[i + 1]
        del args[i:i + 2]
    if len(args) != 3:
        print(__doc__)
        return 2
    with open(args[2], encoding="utf-8") as f:
        rules = json.load(f)
    try:
        s, w = waive(args[0], args[1], rules, register)
    except (KeyError, ValueError) as e:
        print("waive_po: %s" % e)
        return 1
    print("set %d, waived %d" % (s, w))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
