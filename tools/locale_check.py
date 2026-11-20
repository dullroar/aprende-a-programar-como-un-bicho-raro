#!/usr/bin/env python3
"""Validate the acronym and phase catalog in lessons/book/locale/es.yaml.

Usage: python3 -I tools/locale_check.py [path]
Exit 0 = OK, 1 = problems (listed on stdout).

Checks (plan 2.5): five phases in order 1..5; five different single letters;
each name starts with its letter; the acronym word is exactly the five letters in
order; the expansion lists the five names; mermaid node IDs stay W E I R D;
every definition/question is non-empty, questions are paired with the opening mark.
"""
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
DEFAULT = os.path.join(REPO, "lessons", "book", "locale", "es.yaml")
NODE_IDS = ["W", "E", "I", "R", "D"]
WEEKS = ["1 a 2", "3 a 6", "7 a 10", "11 a 13", "14 a 15"]
MACRO = re.compile(r"\{\{([a-z0-9_.]+)\}\}")


def check(data):
    errs = []
    if not isinstance(data, dict):
        return ["catalog is not a mapping"]
    acr = data.get("acronym")
    phases = data.get("phases")
    if not isinstance(acr, dict):
        errs.append("missing 'acronym' mapping")
        acr = {}
    if not isinstance(phases, list):
        return errs + ["missing 'phases' list"]
    if len(phases) != 5:
        errs.append("expected 5 phases, found %d" % len(phases))
    ns = [p.get("n") for p in phases if isinstance(p, dict)]
    if ns != list(range(1, len(phases) + 1)):
        errs.append("phases not numbered 1..N in order: %r" % ns)
    letters = []
    for i, p in enumerate(phases):
        if not isinstance(p, dict):
            errs.append("phase %d is not a mapping" % (i + 1))
            continue
        n = p.get("n", i + 1)
        for key in ("letter", "name", "weeks", "question", "definition", "mermaid_node_id"):
            if not isinstance(p.get(key), str) or not p[key].strip():
                errs.append("phase %s: missing or empty '%s'" % (n, key))
        letter, name = p.get("letter"), p.get("name")
        letters.append(letter)
        if isinstance(letter, str) and (len(letter) != 1 or not letter.isalpha() or not letter.isupper()):
            errs.append("phase %s: letter %r is not one capital letter" % (n, letter))
        if isinstance(letter, str) and isinstance(name, str) and not name.startswith(letter):
            errs.append("phase %s: name %r does not start with letter %r" % (n, name, letter))
        if isinstance(p.get("question"), str) and not (p["question"].startswith("¿") and p["question"].endswith("?")):
            errs.append("phase %s: question lacks paired ¿?" % n)
        if i < len(NODE_IDS) and p.get("mermaid_node_id") != NODE_IDS[i]:
            errs.append("phase %s: mermaid_node_id must stay %s" % (n, NODE_IDS[i]))
        if i < len(WEEKS) and p.get("weeks") != WEEKS[i]:
            errs.append("phase %s: weeks must stay %r" % (n, WEEKS[i]))
        for key in ("name", "definition", "question"):
            if isinstance(p.get(key), str) and re.search(r"\b[WEIRD]\b:?\s", p[key]) and key == "name":
                errs.append("phase %s: English phase letter survives in name" % n)
    if len(set(letters)) != len(letters):
        errs.append("duplicate phase letters: %r" % letters)
    word = acr.get("word")
    if not isinstance(word, str) or word != "".join(l for l in letters if isinstance(l, str)):
        errs.append("acronym.word %r is not the phase letters in order %r" % (word, "".join(str(l) for l in letters)))
    exp = acr.get("expansion")
    names = [p.get("name") for p in phases if isinstance(p, dict)]
    if isinstance(exp, str) and all(isinstance(x, str) for x in names):
        pos = 0
        for nm in names:
            k = exp.find(nm, pos)
            if k < 0:
                errs.append("acronym.expansion does not list %r in order" % nm)
                break
            pos = k + len(nm)
    else:
        errs.append("acronym.expansion missing")
    for key in ("gloss", "aside", "recursive_note"):
        txt = acr.get(key)
        if not isinstance(txt, str) or not txt.strip():
            errs.append("acronym.%s missing" % key)
        elif key != "recursive_note" and isinstance(exp, str) and exp not in txt:
            errs.append("acronym.%s does not contain the expansion" % key)
    # every macro used inside the catalog must resolve
    for key, txt in acr.items():
        if isinstance(txt, str):
            for m in MACRO.findall(txt):
                parts = m.split(".")
                if parts[0] == "acronym" and parts[1:] == ["word"]:
                    continue
                if parts[0] == "phase" and len(parts) == 3 and parts[1].isdigit() \
                        and 1 <= int(parts[1]) <= len(phases) and parts[2] in ("letter", "name"):
                    continue
                errs.append("acronym.%s uses unknown macro {{%s}}" % (key, m))
    return errs


def main(argv):
    path = argv[1] if len(argv) > 1 else DEFAULT
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    errs = check(data)
    for e in errs:
        print("FAIL " + e)
    if not errs:
        print("OK locale phases 1 to 5 (%s)" % os.path.relpath(path, REPO))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
