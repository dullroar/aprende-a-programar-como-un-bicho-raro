#!/usr/bin/env python3
"""tools/pathcheck.py: invariants I17 to I20 of the Spanish file names (plan 5.6, task P3B-006).

  I17  every relative link destination of every Markdown file resolves in this checkout (a link that still names the
       old English path of a renamed file is reported with the Spanish path it should name)
  I18  a student-facing path that was renamed carries only Spanish words (glossary terms, path words, function words,
       proper names, digits); a Markdown document that kept its English name must be on the keep list
       (pinned by a frozen file, a workflow, a keep-list tree, or a proper name)
  I19  no frozen file or workflow mentions a renamed path, and no frozen file is renamed (the byte lock itself is
       check_lock in verify.py, I13)
  I20  the path map is one-to-one: every file has exactly one row, no two files share a name, README.md and the other
       keep-list names are not renamed, a renamed name is ASCII kebab-case, and the committed map is the one the
       rules compute

Every problem starts with its check id ("I17 ..."). The functions are pure (they take the tree as data) so that
tools/negative.py can feed them a mutated copy; run(root) reads the real checkout.

Usage:
  python3 -I tools/pathcheck.py          check this checkout; exit 1 on any problem
"""
from __future__ import annotations

import os
import posixpath
import re
import sys
from urllib.parse import unquote

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import enpath  # noqa: E402
import pathmap  # noqa: E402

ROOT = os.path.dirname(HERE)

FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
CODE_SPAN_RE = re.compile(r"(`+)(?:(?!\1).)+?\1")
INLINE_LINK_RE = re.compile(r"!?\[(?:[^\[\]]|\[[^\]]*\])*\]\(\s*<?([^)\s>]+)>?(?:\s+(?:\"[^\"]*\"|'[^']*'))?\s*\)")
REF_DEF_RE = re.compile(r"^\s{0,3}\[[^\]]+\]:\s*<?(\S+?)>?(?:\s+.*)?$")
HTML_REF_RE = re.compile(r"""(?:href|src)=["']([^"']+)["']""")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")


def link_destinations(text: str) -> list[tuple[int, str]]:
    """(line number, destination) of every Markdown link, image, reference definition and href/src outside code."""
    out: list[tuple[int, str]] = []
    fence = None
    for n, line in enumerate(text.splitlines(), 1):
        m = FENCE_RE.match(line)
        if m:
            if fence is None:
                fence = m.group(1)[0] * 3
            elif line.strip().startswith(fence):
                fence = None
            continue
        if fence is not None:
            continue
        bare = CODE_SPAN_RE.sub("", line)
        for rx in (INLINE_LINK_RE, HTML_REF_RE):
            out += [(n, d) for d in rx.findall(bare)]
        m = REF_DEF_RE.match(bare)
        if m:
            out.append((n, m.group(1)))
    return out


def local_target(dest: str) -> str | None:
    """The path part of a destination, or None when it is not a local file reference (URL, mailto, bare anchor)."""
    dest = dest.strip()
    if not dest or dest.startswith(("#", "//", "{{")) or SCHEME_RE.match(dest):
        return None
    return unquote(re.split(r"[#?]", dest, 1)[0]) or None


# ------------------------------------------------------------------------------------------------------- I17

def i17_problems(docs: dict[str, tuple[str, str]], exists, old_to_new: dict[str, str] | None = None) -> list[str]:
    """docs: working path -> (text, directory the links are written against). exists(path) -> bool.
    old_to_new: English path -> Spanish path of every renamed file (to name the fix)."""
    old_to_new = old_to_new or {}
    problems = []
    for rel, (text, base) in sorted(docs.items()):
        for line, dest in link_destinations(text):
            target = local_target(dest)
            if target is None:
                continue
            path = posixpath.normpath(posixpath.join(base, target)) if not target.startswith("/") else target.lstrip("/")
            if path.startswith("../") or path == "..":
                problems.append("I17 %s:%d: link %s leaves the repository" % (rel, line, dest))
            elif not exists(path):
                hint = ""
                if path in old_to_new:
                    hint = " (old English name; the file is now %s)" % old_to_new[path]
                problems.append("I17 %s:%d: link destination %s does not resolve%s" % (rel, line, dest, hint))
    return problems


# ------------------------------------------------------------------------------------------------------- I18

def i18_problems(files: dict[str, str], res: dict, glossary: dict) -> list[str]:
    """files: English path -> class. res: pathmap.build() result. glossary: the parsed glossary.es.yaml.
    Words of every renamed component are judged by glossary_check.check_path_words (terms, path_words, function and
    proper words; a banned word fails), applied to the map itself and not to the names table that produced it."""
    import glossary_check
    problems = []
    result, reasons, kinds, dir_map = res["map"], res["reasons"], res["kinds"], res["dir_map"]
    names: dict = {"dirs": {}, "files": {}}
    for d, n in dir_map.items():
        if n != d.split("/")[-1]:
            names["dirs"][d] = n
    for p, q in result.items():
        if q != p and files.get(p) in ("authored", "generated") and p.endswith(".md"):
            o, n = posixpath.basename(p), posixpath.basename(q)
            if o != n:
                names["files"][p] = n
    problems += ["I18 " + m for m in glossary_check.check_path_words(glossary, names)]
    for p in sorted(files):
        if files[p] in ("authored", "generated") and p.endswith(".md") and result.get(p) == p:
            if kinds.get(p) == "movable" and posixpath.basename(p) != pathmap.README \
                    and "stays" not in reasons.get(p, ""):
                problems.append("I18 %s: Markdown document kept its English name and is not on the keep list (%s)"
                                % (p, reasons.get(p, "no reason")))
    return problems


# ------------------------------------------------------------------------------------------------ I19 and I20

def classify_map_problem(msg: str) -> str:
    """I19 for a frozen file or workflow that mentions a renamed path (or is renamed itself); I20 for the rest."""
    return "I19" if ("frozen file" in msg or "workflow" in msg) else "I20"


def map_problems(files: dict[str, str], result: dict[str, str], sources) -> list[str]:
    """pathmap.validate on any map, each problem tagged I19 or I20."""
    return ["%s %s" % (classify_map_problem(m), m) for m in pathmap.validate(files, result, sources)]


# ------------------------------------------------------------------------------------------------------- run

def collect_docs(root: str, files: dict[str, str], layer) -> dict[str, tuple[str, str]]:
    docs = {}
    for en, cls in sorted(files.items()):
        if cls not in ("authored", "generated") or not en.endswith(".md"):
            continue
        full = layer.full(en)
        if not os.path.isfile(full):
            continue
        with open(full, encoding="utf-8") as fh:
            text = fh.read()
        work = layer.work(en)
        # cs-source bodies are written for the pages the generator puts in lessons/cs (enpath._virtual_dirs)
        base = enpath._virtual_dirs(layer, en)[1] if layer.moved else enpath._virtual_dirs(layer, en)[0]
        docs[work] = (text, base)
    return docs


def run(root: str = ROOT) -> list[str]:
    layer = enpath.load(root)
    files, read = pathmap.load_tree(root)
    names = pathmap.load_names(pathmap.read_own(root, pathmap.NAMES_PATH))
    known = pathmap.glossary_words(pathmap.read_own(root, pathmap.GLOSSARY_PATH))
    res = pathmap.build(files, read, names, known)
    import yaml
    glossary = yaml.safe_load(pathmap.read_own(root, pathmap.GLOSSARY_PATH))
    problems: list[str] = []
    committed = enpath.read_map(root)

    # I20: the committed map is the computed one, and every file of the tree has a row
    if committed != res["map"]:
        diff = sorted(p for p in set(committed) | set(res["map"]) if committed.get(p) != res["map"].get(p))
        problems.append("I20 translation/path-map.yaml is stale or hand-edited (differs from the rules at %d path(s), "
                        "first %s): run python3 tools/pathmap.py --write" % (len(diff), diff[0]))
    frozen_src = [(p, t) for p, c in sorted(files.items()) if c == "frozen" for t in [read(p)] if t is not None]
    workflow_src = [(p, t) for p in sorted(files) if p.startswith(".github/workflows/") for t in [read(p)]
                    if t is not None]
    problems += map_problems(files, committed or res["map"], (frozen_src, workflow_src))
    # the tree on disk follows the layout: every file sits at its work path
    for en in sorted(files):
        if not os.path.isfile(layer.full(en)):
            problems.append("I20 %s: not found at its %s path %s" % (en, layer.layout, layer.work(en)))

    # I18
    problems += i18_problems(files, res, glossary)

    # I17
    docs = collect_docs(root, files, layer)
    old_to_new = {en: es for en, es in layer.renamed().items()} if layer.moved else {}
    problems += i17_problems(docs, lambda p: os.path.exists(os.path.join(root, *p.split("/"))), old_to_new)
    return problems


def main(argv: list[str]) -> int:
    problems = run(ROOT)
    for p in problems:
        print(p)
    print("pathcheck (I17 to I20): %s" % ("FAIL (%d problem(s))" % len(problems) if problems else "ok"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
