#!/usr/bin/env python3
"""breakage_pilot: plan Appendix A step 7 on the REAL pilot files (task P3-008).

tools/negative.py breaks a small synthetic file. This tool breaks the translated pilot files themselves, in throwaway
copies that live only in memory or under translation/work/negative/ (git-ignored), and asks the same functions that
`verify.py --release` calls whether they notice:

  a  the stop rule is weakened (exactly 40 would stop, or the `40≥` code span changes)
  b  one byte of a frozen file changes (a mini repo with the real file and its manifest row)
  c  an accDescr is deleted (hand edit of the finished file, and a PO that leaves it in English)
  d  a Spanish heading anchor is broken (a link fragment, and a renamed heading that the book links to)
  e  an English phase letter survives (the step-7 repeat with `W`: a bare letter in prose, a label, a diagram label)

The control (the pilot files as they are) must be clean first: a gate that fails on good input proves nothing.

  python3 -I tools/breakage_pilot.py            run the control and every copy; exit 0 only if all of them fail as expected
  python3 -I tools/breakage_pilot.py --list     print the catalog
  python3 -I tools/breakage_pilot.py --show ID  print the problems one copy produces

verify.run_release runs this as the check "pilot breakage copies". Exit codes: 0 good, 1 a copy did not fail or the
control is dirty, 2 usage.
"""
import os
import re
import sys
from collections import namedtuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
sys.path.insert(0, os.path.join(ROOT, "lessons", "book"))
sys.path.insert(0, os.path.join(ROOT, "lessons", "curriculum"))

PILOT = ("src/forth/README.md", "lessons/cs-source/concepts/recursion.md", "lessons/study-guides/languages/forth.md",
         "docs/curriculum.md", "lessons/study-guides/languages/apl.md")
README, RECURSION, FORTH, CURRICULUM, APL = PILOT

Copy = namedtuple("Copy", "id step title kind rel expect edit")
# kind "po"      edit the msgstr of the PO, apply it, check the finished file (a consistent but wrong translation)
# kind "hand"    edit the finished file only (a hand edit after the PO)
# kind "lock"    flip a byte of a frozen file in a mini repo; `rel` is the frozen file
# kind "anchors" a hand edit judged by the file check AND by anchors.check_links


def read(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


class Pilot:
    """The shared, read-only state: the English text, the PO and the finished Spanish file of each pilot file."""

    def __init__(self):
        import apply as apply_mod
        import inventory
        import verify
        self.apply, self.verify = apply_mod, verify
        self.env = verify.Env(ROOT)
        self.cfg = inventory.read_config(ROOT)

    def files(self, rel):
        en = self.verify.english_text(self.cfg, rel)
        po = self.apply.load_po(self.apply.po_path_for(rel))
        import enpath
        return en, po, read(enpath.load(ROOT).full(rel))        # `rel` is the English key

    def check(self, rel, es, po, en=None):
        en = en if en is not None else self.verify.english_text(self.cfg, rel)
        return self.verify.check_file(rel, en, es, po, self.env.ctx, True, self.env.cat, self.verify.layout_remap(rel, ROOT))


def msgstr_edit(old, new):
    """A change to the Spanish of one PO entry; stale when `old` is in no entry (a stale copy must not pass)."""
    def run(po):
        hits = [e for e in po if old in e.msgstr]
        if not hits:
            raise AssertionError("copy is stale: %r is in no msgstr" % old)
        hits[0].msgstr = hits[0].msgstr.replace(old, new, 1)
    return run


def text_edit(old, new):
    def run(text):
        if old not in text:
            raise AssertionError("copy is stale: %r is not in the finished file" % old)
        return text.replace(old, new, 1)
    return run


def drop_first_line(prefix):
    def run(text):
        lines = text.split("\n")
        for i, ln in enumerate(lines):
            if ln.strip().startswith(prefix):
                return "\n".join(lines[:i] + lines[i + 1:])
        raise AssertionError("copy is stale: no line starts with %r" % prefix)
    return run


def run_copy(pilot, c):
    """The problems the release gate reports for one copy."""
    import negative
    if c.kind == "lock":
        return negative.lock_problems(negative.flip_byte, c.rel)
    en, po, es = pilot.files(c.rel)
    if c.kind == "po":
        c.edit(po)
        es, _ = pilot.apply.apply_text(en, po, c.rel, pilot.env.cat, strict=False)
        return pilot.check(c.rel, es, po, en)
    es = c.edit(es)
    out = pilot.check(c.rel, es, po, en)
    if c.kind == "anchors":
        import anchors
        doc, _ = anchors.current_document()
        out += ["anchors " + p for p in anchors.check_links(c.rel, es, doc)]
    return out


def catalog():
    C = []

    def add(cid, step, title, kind, rel, expect, edit=None):
        C.append(Copy(cid, step, title, kind, rel, expect, edit))

    # a. the stop rule: strictly greater than 40 stops, exactly 40 continues
    add("stop-readme-reaches-40", "a", "the Forth README says the challenge ends when the total reaches 40",
        "po", README, "I7", msgstr_edit("hasta que el total pase de 40", "hasta que el total llegue a 40"))
    add("stop-guide-less-than-40", "a", "the Forth guide says the flag is true while the total is less than 40 (40 stops)",
        "po", FORTH, "I7", msgstr_edit("no pasa de 40", "es menor que 40"))
    add("stop-apl-code-span-gt", "a", "the APL code span 40≥ becomes 40> in the finished file",
        "hand", APL, "I13", text_edit("`40≥`", "`40>`"))
    add("stop-apl-diagram-label", "a", "the APL diagram label says the total is below 40",
        "po", APL, "I3", msgstr_edit("total ≤ 40", "total < 40"))
    # b. one byte of a frozen file
    add("frozen-byte-timecards-fs", "b", "one byte of src/forth/timecards.fs is flipped", "lock", "src/forth/timecards.fs", "I13")
    add("frozen-byte-check-sh", "b", "one byte of src/forth/check.sh is flipped", "lock", "src/forth/check.sh", "I13")
    # c. an accDescr is deleted
    for rel, name in ((README, "readme"), (FORTH, "guide-forth"), (APL, "guide-apl"), (CURRICULUM, "curriculum"),
                      (RECURSION, "recursion")):
        add("accdescr-deleted-" + name, "c", "an accDescr line is deleted from %s" % rel, "hand", rel, "I5",
            drop_first_line("accDescr:"))
    add("accdescr-english-curriculum", "c", "the curriculum accDescr is left in English", "po", CURRICULUM, "I9",
        lambda po: _english_accdescr(po))
    # d. a Spanish heading anchor is broken
    add("anchor-fragment-translated", "d", "a link into exercises.md gets a Spanish fragment that no heading has",
        "anchors", FORTH, "I4", text_edit("exercises.md#ejecutar-con-seguridad", "exercises.md#ejecutar-cosas-de-forma-segura"))
    add("anchor-fragment-dropped", "d", "a link into the English guide loses its fragment", "anchors", APL, "I4",
        text_edit("introduccion.md#qué-hace-el-reto", "introduccion.md#el-reto"))
    add("anchor-heading-renamed", "d", "a heading is renamed in the finished file only", "hand", FORTH, "I16",
        text_edit("## Traza una ejecución", "## Sigue una ejecución"))
    # e. an English phase letter survives (the step-7 repeat with W)
    add("phase-bare-letter-prose", "e", "the curriculum says 'empezar en W' (bare English phase letter)", "po", CURRICULUM, "I14",
        msgstr_edit("vuelve a empezar en {{phase.1.letter}}", "vuelve a empezar en W"))
    add("phase-bare-letter-recursive", "e", "the curriculum says 'La W es recursiva'", "po", CURRICULUM, "I14",
        msgstr_edit("La {{phase.1.letter}} es recursiva. En la primera", "La W es recursiva. En la primera"))
    add("phase-label-letter", "e", "a diagram label keeps 'W: Raro' instead of the phase macros", "po", CURRICULUM, "I14",
        msgstr_edit("{{phase.1.letter}}: {{phase.1.name}}, semanas 1 a 2", "W: {{phase.1.name}}, semanas 1 a 2"))
    add("phase-start-label", "e", "the diagram start label says 'fase = W'", "po", CURRICULUM, "I14",
        msgstr_edit("Inicio: fase = {{phase.1.letter}}", "Inicio: fase = W"))
    add("phase-acronym-english", "e", "the curriculum introduction uses the English acronym", "po", CURRICULUM, "I14",
        msgstr_edit("**{{acronym.word}}** significa", "**WEIRD** significa"))
    return C


def _english_accdescr(po):
    """Leave the accDescr of the curriculum in English: msgstr becomes the msgid."""
    hits = [e for e in po if e.msgid.startswith("A flowchart. The course starts")]
    if not hits:
        raise AssertionError("copy is stale: the curriculum accDescr is not in the PO")
    hits[0].msgstr = hits[0].msgid


def control_problems(pilot):
    """The pilot files as they are must be clean under the same checks."""
    import anchors
    import negative
    out = []
    doc, _ = anchors.current_document()
    for rel in PILOT:
        en, po, es = pilot.files(rel)
        out += ["%s: %s" % (rel, p) for p in pilot.check(rel, es, po, en)]
        out += ["%s: anchors %s" % (rel, p) for p in anchors.check_links(rel, es, doc)]
    for rel in ("src/forth/timecards.fs", "src/forth/check.sh"):
        out += ["%s: %s" % (rel, p) for p in negative.lock_problems(lambda path: None, rel)]
    return out


def run_one(pilot, c):
    try:
        return list(run_copy(pilot, c)), None
    except Exception as e:  # a stale copy must be loud, not a pass
        return [], "%s: %s" % (type(e).__name__, e)


def run_all():
    pilot = Pilot()
    out = ["control: " + p for p in control_problems(pilot)]
    for c in catalog():
        problems, err = run_one(pilot, c)
        if err:
            out.append("copy %s is broken: %s" % (c.id, err))
        elif not problems:
            out.append("copy %s (step 7%s: %s) did not fail: the gate is disarmed" % (c.id, c.step, c.title))
        elif not any(re.search(r"\b%s" % re.escape(c.expect), p) for p in problems):
            out.append("copy %s failed, but not with %s: %s" % (c.id, c.expect, problems[0]))
    return out


def main(argv):
    args = argv[1:]
    if args and args[0] == "--list":
        for c in catalog():
            print("%s  %-30s %-7s %-5s %s" % (c.step, c.id, c.kind, c.expect, c.title))
        return 0
    if args and args[0] == "--show" and len(args) == 2:
        c = next((x for x in catalog() if x.id == args[1]), None)
        if c is None:
            print("no copy %s" % args[1])
            return 2
        problems, err = run_one(Pilot(), c)
        print("\n".join(problems) or "(no problems)")
        if err:
            print("ERROR " + err)
        return 0
    if args:
        print(__doc__.split("Exit codes")[0].rstrip())
        return 2
    problems = run_all()
    if problems:
        print("\n".join(problems))
        print("breakage_pilot: FAIL (%d problem(s))" % len(problems))
        return 1
    print("breakage_pilot: OK (control clean; %d copies of the pilot files, each fails the release check)" % len(catalog()))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
