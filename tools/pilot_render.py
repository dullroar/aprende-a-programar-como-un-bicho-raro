#!/usr/bin/env python3
"""Render the translated pilot guides to HTML, PDF and EPUB (plan phase 3, Appendix A step 6).

    env BOOK_LANG=es python3 tools/pilot_render.py [--out DIR] [--only-check]

The study-guide build refuses a Spanish edition while any guide is still English (its set check wants all 22 guides). For the pilot
this tool builds a document of only the translated guides (Forth and APL), after running the guides' own per-guide check
(study_guides.check_guide) on each of them. It calls the book's pipeline (lessons/book/build.py build_documents), so the Pandoc command,
the stylesheet, the Mermaid renderer and the PDF lint are the real ones. Output goes to translation/work/pilot-render/guides by default
(git-ignored). The curriculum has its own build: `env BOOK_LANG=es python3 lessons/curriculum/build.py --artifacts-dir DIR`.

Exit code 0 when the guides pass their checks and every output was written, 1 otherwise.
"""
import importlib.util
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GUIDES = os.path.join(ROOT, "lessons", "study-guides")
BOOKDIR = os.path.join(ROOT, "lessons", "book")
PILOT_GUIDES = ["languages/forth.md", "languages/apl.md"]
DEFAULT_OUT = os.path.join(ROOT, "translation", "work", "pilot-render", "guides")


ENGLISH_ANCHOR = "intro.md#what-the-challenge-does"
NO_SECTION_RE = re.compile(r"line \d+: (\S+?)#program-flow: the file has no '## Program Flow' section")


def source_still_english(path, repo=ROOT):
    """True when `path` still has the English '## Program Flow' heading: its README is not translated yet (stage 4)."""
    try:
        with open(os.path.join(repo, path), encoding="utf-8") as f:
            return any(ln.strip() == "## Program Flow" for ln in f)
    except OSError:
        return False


def intro_still_english(repo=ROOT):
    try:
        with open(os.path.join(repo, "lessons", "intro.md"), encoding="utf-8") as f:
            return any(ln.strip() == "## What the challenge does" for ln in f)
    except OSError:
        return False


def expected_during_pilot(problem, spanish_anchor, repo=ROOT):
    """A guide-check message that only reflects a file the pilot has not translated yet. Nothing else is excused."""
    m = NO_SECTION_RE.search(problem)
    if m:
        return source_still_english(m.group(1), repo)
    return problem.endswith("link to a missing heading: ../../" + spanish_anchor) and intro_still_english(repo)


def guide_problems(study_guides, names, repo=ROOT):
    """The per-guide checks of lessons/book/study_guides.py for each named guide (paths relative to lessons/study-guides/).

    Two things are adjusted because intro.md is still English: the link to its challenge section is checked with the Spanish
    anchor it will have (anchors.py --remap writes it in stage 5), and a diagram whose source README is still English is not an error yet."""
    out = []
    spanish_anchor = "intro.md#" + study_guides.slug(study_guides.CHALLENGE_HEADING)
    for g in names:
        text = study_guides.read(os.path.join(repo, "lessons", "study-guides", g)).replace(ENGLISH_ANCHOR, spanish_anchor)
        out += [p for p in study_guides.check_guide(g, text, repo) if not expected_during_pilot(p, spanish_anchor, repo)]
    return out


def main(argv):
    out = DEFAULT_OUT
    if "--out" in argv:
        out = os.path.abspath(argv[argv.index("--out") + 1])
    if os.environ.get("BOOK_LANG", "en") != "es":
        print("set BOOK_LANG=es")
        return 1
    sys.argv = [sys.argv[0], "--artifacts-dir", out]       # the book pipeline reads --artifacts-dir from argv
    sys.path.insert(0, BOOKDIR)
    sys.dont_write_bytecode = True
    import study_guides
    problems = guide_problems(study_guides, PILOT_GUIDES)
    if problems:
        print("\n".join("PROBLEM " + p for p in problems))
        return 1
    print("pilot guides: template, diagrams and links ok (%d guides)" % len(PILOT_GUIDES))
    if "--only-check" in argv:
        return 0
    spec = importlib.util.spec_from_file_location("book_build", os.path.join(BOOKDIR, "build.py"))
    book = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(book)
    book.release_mode()
    texts = {"study-guides/" + g: study_guides.read(os.path.join(GUIDES, g)) for g in PILOT_GUIDES}
    html = book.build_documents(texts, "guias-piloto", os.path.join(GUIDES, "metadata.yaml"), os.path.join(GUIDES, "front-matter.md"),
                                "pilot-guides.html", "pilot-guides", False, prune_cache=False)
    book.check(html)
    for ext in (".pdf", ".epub"):
        if not os.path.isfile(os.path.join(out, "guias-piloto" + ext)):
            print("missing output guias-piloto" + ext)
            return 1
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
