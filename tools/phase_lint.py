#!/usr/bin/env python3
"""phase_lint: phase letters against exercise-ID prefixes (plan 2.5 N5, invariant I14, task P2-014).

The Spanish phase letters come from the locale catalog (BICHO by default, TORCE as the runner-up). Exercise IDs
such as B3 or C1 also start with a letter, so a letter that is both a phase letter and an ID prefix is a collision.
Collisions are allowed (the English edition has two: E and D); what is refused is a phase reference a reader could
mistake for an exercise, and an exercise ID written where a phase belongs.

Rules, applied to PROSE (code spans, placeholders and macros removed), for every colliding letter L:
  A1  "fase L3"            a phase word followed by an exercise-ID-shaped token (letter and digits).
  A2  "fase L" with no name  the phase word and the bare letter; the phase name must follow ("fase B: Bicho raro").
A letter that is a phase letter but not an ID prefix is never reported by these rules. The prefixes come from
translation/phase-letters.json (checked against lessons/exercises.md by --check).

Usage:
  python3 -I tools/phase_lint.py --report [LANG]   collisions of the catalog letters with the exercise-ID prefixes
  python3 -I tools/phase_lint.py --check           the JSON prefixes equal the headings of lessons/exercises.md
  python3 -I tools/phase_lint.py --text FILE       lint one Markdown file against the Spanish catalog
Exit 0 = clean.
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
import catalog  # noqa: E402
import mask  # noqa: E402

PHASE_LETTERS_JSON = os.path.join(ROOT, "translation", "phase-letters.json")
EXERCISES_MD = os.path.join(ROOT, "lessons", "exercises.md")
PHASE_WORDS = r"(?:fases?|phases?)"
MACRO_RE = re.compile(r"\{\{[^}\n]+\}\}|\[\[[^\]\n]+\]\]")
HEADING_ID_RE = re.compile(r"^#{2,4}\s+([A-Z])(\d*)\.\s", re.M)
SECTION_RE = re.compile(r"^#{2,3}\s+(?:Section\s+)?([A-Z])\.\s", re.M)


def load_prefixes(path=PHASE_LETTERS_JSON):
    """The exercise-ID prefixes recorded by Phase 0, as a sorted list of capital letters."""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return sorted(data["exercise_id_prefixes"]["prefixes"])


def scan_prefixes(text):
    """Prefixes found in the headings of an exercises file: numbered IDs (B3.) and lettered sections (D.)."""
    found = {m.group(1) for m in HEADING_ID_RE.finditer(text)}
    found |= {m.group(1) for m in SECTION_RE.finditer(text)}
    return sorted(found)


def phase_letters(cat):
    letters = []
    n = 1
    while "phases.%d.letter" % n in cat.flat:
        letters.append(cat.flat["phases.%d.letter" % n])
        n += 1
    return letters


def collisions(cat, prefixes):
    """Phase letters of `cat` that are also exercise-ID prefixes, in phase order."""
    pre = set(prefixes)
    return [l for l in phase_letters(cat) if l in pre]


def _prose(text):
    text = mask.PH_RE.sub(" ", re.sub(r"`[^`\n]*`", " ", text))
    return MACRO_RE.sub(" ", text)


def ambiguity(text, cat, prefixes):
    """Findings (list of strings) for phase references that collide with exercise IDs. Empty when none."""
    if cat is None or not prefixes:
        return []
    clash = collisions(cat, prefixes)
    if not clash:
        return []
    names = {}
    n = 1
    while "phases.%d.letter" % n in cat.flat:
        names[cat.flat["phases.%d.letter" % n]] = cat.flat.get("phases.%d.name" % n, "")
        n += 1
    out = []
    prose = _prose(text)
    letters = "".join(sorted(clash))
    for m in re.finditer(r"\b%s\s+([%s])(\d+)\b" % (PHASE_WORDS, letters), prose, re.I):
        out.append("exercise ID %s%s written as a phase: '%s'" % (m.group(1), m.group(2), m.group(0)))
    for m in re.finditer(r"\b%s\s+([%s])\b(?!\d)" % (PHASE_WORDS, letters), prose, re.I):
        letter = m.group(1)
        tail = prose[m.end():]
        name = names.get(letter, "")
        if name and re.match(r"\s*[:(,–—-]?\s*%s\b" % re.escape(name), tail):
            continue
        out.append("phase letter %s collides with exercise IDs %s1...; follow it with its name '%s' (%s)"
                   % (letter, letter, name, m.group(0)))
    return out


def report(cat, prefixes):
    clash = collisions(cat, prefixes)
    lines = ["acronym %s: letters %s" % (cat.get("acronym.word"), " ".join(phase_letters(cat))),
             "exercise-ID prefixes: %s" % " ".join(prefixes),
             "collisions: %s" % (" ".join(clash) if clash else "none")]
    return lines


def check_prefixes(json_prefixes, exercises_text):
    """Problems when the recorded prefixes differ from the exercises file."""
    scanned = scan_prefixes(exercises_text)
    out = []
    for p in sorted(set(scanned) - set(json_prefixes)):
        out.append("prefix %s is in lessons/exercises.md but not in phase-letters.json" % p)
    for p in sorted(set(json_prefixes) - set(scanned)):
        out.append("prefix %s is in phase-letters.json but not in lessons/exercises.md" % p)
    return out


def main(argv):
    if not argv or argv[0] in ("-h", "--help"):
        print(__doc__)
        return 0
    if argv[0] == "--report":
        lang = argv[1] if len(argv) > 1 else "es"
        for ln in report(catalog.load(lang), load_prefixes()):
            print(ln)
        return 0
    if argv[0] == "--check":
        with open(EXERCISES_MD, encoding="utf-8") as f:
            problems = check_prefixes(load_prefixes(), f.read())
        for p in problems:
            print(p)
        print("OK" if not problems else "%d problem(s)" % len(problems))
        return 1 if problems else 0
    if argv[0] == "--text" and len(argv) > 1:
        with open(argv[1], encoding="utf-8") as f:
            found = ambiguity(f.read(), catalog.load("es"), load_prefixes())
        for p in found:
            print("%s: %s" % (argv[1], p))
        return 1 if found else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
