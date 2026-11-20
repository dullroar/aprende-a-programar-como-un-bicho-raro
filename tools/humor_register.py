"""Seed and check translation/humor-register.jsonl (plan section 6, invariant I15).

The register lists every playful heading or joke in the T2 (book) tier, with what the
joke does in English. The Spanish side starts as status "pending"; translate tasks fill
it in (kept | transcreated | deliberately-flattened) and a human reviews it.

Usage:
  python3 tools/humor_register.py --seed    # (re)build entries, keeping any filled-in status
  python3 tools/humor_register.py --check   # verify every entry against the source files
"""
import glob
import json
import os
import re
import sys

REGISTER = "translation/humor-register.jsonl"
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*$")
FENCE = re.compile(r"^\s*(```|~~~)")

# kind: heading = a Markdown heading, line = a sentence in prose, title = the book title.
# "does" says what the English does, so the translator can match the effect.
ENTRIES = [
    ("H001", "title", "Learn Programming the Weird Way!",
     "The book title. Wordplay on 'learn programming the hard way' with 'weird'; the same "
     "word is the W of the recursive acronym WEIRD. Tied to the acronym decision (P0-010).",
     ["README.md", "lessons/README.md"]),
    ("H002", "heading", "Behold the monstrosity",
     "Mock-grand showman's announcement before the strange program appears. Recurs as a fixed "
     "section name in every language page.", None),
    ("H003", "heading", "How the hell does that work?",
     "The reader's exasperated question in mild profanity. Promises the real mechanism, not the "
     "trick. Recurs as a fixed section name.", None),
    ("H004", "heading", "Do this in production and you're fired",
     "Comic threat. Hyperbole that introduces the serious failure modes. Contraction is kept "
     "in English as a fixed humor heading.", None),
    ("H005", "heading", "Now break it yourself",
     "A playful dare. Invites the reader to change the program and watch it fail.", None),
    ("H006", "heading", "Under what circumstances would this terrible idea become reasonable?",
     "Ironic: calls the program a terrible idea, then asks for the honest engineering case.", None),
    ("H007", "heading", "Weird next to boring",
     "Sets the strange program beside its ordinary equivalent. 'Boring' is affectionate teasing; "
     "echoes 'weird' in the title.", None),
    ("H008", "heading", "How the stunt works",
     "Frames each entry as a circus stunt. Recurs in every entry README.", None),
    ("H009", "heading", "Why this is weird",
     "Plain-spoken use of the book's key word as a heading in entry READMEs.", None),
    ("H010", "heading", "Gotchas worth knowing",
     "Casual 'gotchas' for the known traps; colloquial register.", None),
    ("H011", "heading", "APL was meant for the whiteboard",
     "Wry claim about APL's origin as notation, setting up why running it feels odd.", None),
    ("H012", "heading", "Honest fine print",
     "Mock-legal tone for the caveats about XAML evidence.", None),
    ("H013", "heading", "How is that even possible?",
     "Incredulous reader voice, a milder sibling of 'How the hell does that work?'.", None),
    ("H014", "heading", "Learn and break",
     "Short imperative pair that merges 'what did we learn' with 'now break it'.", None),
    ("H015", "heading", "The buffer is the machine",
     "Slogan-style identity claim ('X is the Y'), a pattern repeated in other headings.", None),
    ("H016", "heading", "The archive is the clock",
     "Same slogan pattern; the archive order plays the role of a clock.", None),
    ("H017", "heading", "A program that is an archive",
     "Paradox heading: a tar file is the program.", None),
    ("H018", "heading", "A tree walk that digs its own tree",
     "Image of find digging the tree it walks; playful self-reference.", None),
    ("H019", "heading", "A loop made of rescanning",
     "Plain metaphor for m4 recursion; mild wit by understatement.", None),
    ("H020", "heading", "Closures all the way down",
     "Allusion to the 'turtles all the way down' idiom.", None),
    ("H021", "heading", "Listeners all the way down",
     "Same turtles idiom, reused for event listeners.", None),
    ("H022", "heading", "SQLite as the program",
     "Surprise framing: a database holds the code.", None),
    ("H023", "heading", "The bodiless for in Node",
     "Wry description of a for loop with no body.", None),
    ("H024", "heading", "No variables? Find somewhere else to keep state",
     "Question-and-answer challenge heading with a shrug of a solution.", None),
    ("H025", "heading", "No loop? Build control flow out of something else",
     "Same challenge-and-answer pattern as H024.", None),
    ("H026", "heading", "Squeezing the program into one statement",
     "Physical image of squeezing; the one-statement constraint.", None),
    ("H027", "heading", "When does it actually run? Order of evaluation",
     "Conversational question heading with a technical label after it.", None),
    ("H028", "heading", "Different ways to solve problems, limited only by imagination",
     "Upbeat goal slogan.", None),
    ("H029", "heading", "Teach computation, not just computational tricks",
     "Contrast of computation versus tricks, with the word-echo carrying the point.", None),
    ("H030", "heading", "A word of caution",
     "Mock-solemn warning heading in the intro.", None),
    ("H031", "heading", "Three ways in",
     "Casual doorway metaphor for the three reading paths.", None),
    ("H032", "line",
     "You know the right way. Now find out what the language actually lets you do. Then ask why, "
     "although it is perfectly legal, it might be a terrible idea.",
     "Three-beat dare that sums up the book's method. Deadpan, ends on 'terrible idea'.",
     ["lessons/intro.md"]),
    ("H033", "line", "how far can a language's own machinery be pushed before it starts acting like a "
     "general-purpose program?",
     "Central question of the intro, wrapped in the 'many accents' image (one question asked in "
     "many languages).", ["lessons/intro.md"]),
]


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


def markdown_files():
    files = ["README.md", "CHALLENGE.md"]
    for pattern in ("lessons/*.md", "lessons/languages/*.md", "lessons/cs-source/**/*.md",
                    "src/*/README.md"):
        files += glob.glob(pattern, recursive=True)
    return sorted(set(f for f in files if os.path.isfile(f)))


def find_headings(text, files):
    hits = []
    for path in files:
        in_fence = False
        for no, line in enumerate(read(path), 1):
            if FENCE.match(line):
                in_fence = not in_fence
                continue
            m = None if in_fence else HEADING.match(line)
            if m and m.group(2) == text:
                hits.append((path, no))
    return hits


def find_line(text, paths):
    hits = []
    for path in paths:
        flat = " ".join(read(path))
        if text in flat:
            hits.append((path, 0))
    return hits


def locate(kind, english, paths, files):
    if kind == "heading":
        return find_headings(english, files)
    return find_line(english, paths)


def build(old):
    files = markdown_files()
    rows = []
    for eid, kind, english, does, paths in ENTRIES:
        hits = locate(kind, english, paths or files, files)
        by_file = sorted(set(p for p, _ in hits))
        row = {
            "id": eid, "kind": kind, "tier": "T2", "english": english,
            "english_does": does, "files": by_file, "occurrences": len(hits),
            "status": "pending", "spanish": None, "reviewer_note": None,
        }
        if eid in old:
            for key in ("status", "spanish", "reviewer_note"):
                row[key] = old[eid].get(key, row[key])
        rows.append(row)
    return rows


def load():
    if not os.path.exists(REGISTER):
        return {}
    with open(REGISTER, encoding="utf-8") as f:
        return {r["id"]: r for r in (json.loads(l) for l in f if l.strip())}


def check():
    problems = []
    rows = list(load().values())
    if not rows:
        return ["register is empty or missing"]
    files = markdown_files()
    valid = {"pending", "kept", "transcreated", "deliberately-flattened"}
    seen = set()
    for r in rows:
        if r["english"] in seen:
            problems.append(r["id"] + ": duplicate English text")
        seen.add(r["english"])
        if not r.get("english_does"):
            problems.append(r["id"] + ": missing english_does")
        if r["status"] not in valid:
            problems.append(r["id"] + ": bad status " + repr(r["status"]))
        if r["status"] == "deliberately-flattened" and not r.get("reviewer_note"):
            problems.append(r["id"] + ": flattened without a reason")
        if r["status"] in ("kept", "transcreated") and not r.get("spanish"):
            problems.append(r["id"] + ": status needs a Spanish text")
        hits = locate(r["kind"], r["english"], r["files"] or files, files)
        if not hits:
            problems.append(r["id"] + ": English text not found in source: " + r["english"][:50])
        elif len(hits) != r["occurrences"]:
            problems.append("%s: occurrences %d in register, %d in source"
                            % (r["id"], r["occurrences"], len(hits)))
    return problems


def main(argv):
    if "--seed" in argv:
        rows = build(load())
        with open(REGISTER, "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
        print("wrote %d entries" % len(rows))
        empty = [r["id"] for r in rows if r["occurrences"] == 0]
        if empty:
            print("not found in source: " + ", ".join(empty))
            return 1
        return 0
    if "--check" in argv:
        problems = check()
        for p in problems:
            print("FAIL " + p)
        print("OK" if not problems else "%d problem(s)" % len(problems))
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
