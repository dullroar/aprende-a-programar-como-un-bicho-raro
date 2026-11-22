#!/usr/bin/env python3
"""anchors: heading slugs, translation/anchors.json, link remap and link check (plan 8.2, invariant I4).

A Spanish heading changes its GitHub anchor ("## Run it" -> "## Ejecútalo", "## What is a bug?" ->
"## ¿Qué es un bug?"), so every `file.md#anchor` and `#anchor` link written for the English heading must be
re-aimed. The links themselves are protected tokens in the segmenter, so the Spanish file keeps the English
fragments until this tool remaps them.

Three slug rules live here, kept apart on purpose:

  build_slug    a copy of slug() in lessons/book/build.py, study_guides.py and cs.py (Python \\w and no more).
                The book build resolves links with it, so the Spanish ids must be right under this rule.
  github_slug   what GitHub renders: lower-case, keep letters, marks, digits, "_" and "-", drop the rest
                (so "¿" "¡" and quotes vanish, accents and "ñ" stay), spaces become "-". It differs from
                build_slug only for combining marks (NFD text) and other connector punctuation.
  pandoc ids    the EPUB and PDF ids come from `pandoc -f gfm+gfm_auto_identifiers`, i.e. the GitHub rule, but
                a repeated heading is numbered across the whole BOOK, not per file (build.py id_maps). Both
                numberings are produced by numbered_ids().

A repeated slug inside one file gets -1, -2, ... in heading order. Headings are paired English-to-Spanish by
position, so a file whose heading count differs from the English file is an error (the translators may not add
or drop a heading).

Usage:
  python3 -I tools/anchors.py --generate       write translation/anchors.json (English clone vs working tree)
  python3 -I tools/anchors.py --check          anchors.json is current, headings pair up, slugs agree, every
                                               internal link in the Spanish files resolves; exit 0 = clean
  python3 -I tools/anchors.py --remap FILE...  rewrite the fragments of the internal links in FILE (in place)
  python3 -I tools/anchors.py --slug TEXT      print the slugs of one heading text
Exit 0 = ok, 1 = problems, 2 = usage.
"""
import json
import os
import re
import subprocess
import sys
import unicodedata
from collections import namedtuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import enpath  # noqa: E402

ANCHORS_PATH = os.path.join(ROOT, "translation", "anchors.json")
FORMAT = 1

# The same two expressions as lessons/book/diagrams.py (scan), so the ids agree with the build.
FENCE_OPEN = re.compile(r"^ {0,3}(`{3,}|~{3,})[ \t]*([^\s`]*)[^`]*$")
HEADING = re.compile(r"^ {0,3}(#{1,6})[ \t]+(.+?)[ \t]*#*[ \t]*$")
QUOTED_HEADING = re.compile(r"^(?: {0,3}>[ ]?)+ {0,3}#{1,6}[ \t]")
SETEXT = re.compile(r"^ {0,3}=+[ \t]*$")
LINK_RE = re.compile(r"(\]\(\s*<?)([^)\s>]+)(>?(?:\s+\"[^\"]*\")?\s*\))")
REFDEF_RE = re.compile(r"^( {0,3}\[[^\]\n]+\]:[ \t]*<?)([^\s>]+)(>?[ \t]*(?:\S.*)?)$")
IMAGE_RE = re.compile(r"!\[([^\]]*)\]\([^)]*\)")
INLINE_LINK_RE = re.compile(r"\[([^\]]*)\]\([^)]*\)")
REF_LINK_RE = re.compile(r"\[([^\]]*)\]\[[^\]]*\]")
HTML_TAG_RE = re.compile(r"</?[A-Za-z][^>\n]*>")
EMPH_RE = re.compile(r"(?<!\w)(_{1,3})(?=\S)(.+?)(?<=\S)\1(?!\w)")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")

Heading = namedtuple("Heading", "line level text")


class AnchorError(ValueError):
    """A construct the tool does not handle, or files that do not pair up. Fails closed."""


def _fence_close(mark):
    return re.compile(r"^ {0,3}" + re.escape(mark[0]) + "{" + str(len(mark)) + r",}[ \t]*$")


# ------------------------------------------------------------------------------------------ slugs

def build_slug(heading):
    """Verbatim copy of the repo's slug(): lessons/book/build.py."""
    h = re.sub(r"`", "", heading.strip().lower())
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


def plain_text(heading):
    """The text a reader sees for a heading: links, images, HTML, backticks and emphasis marks removed."""
    h = IMAGE_RE.sub(r"\1", heading)
    h = INLINE_LINK_RE.sub(r"\1", h)
    h = REF_LINK_RE.sub(r"\1", h)
    h = HTML_TAG_RE.sub("", h)
    h = h.replace("`", "").replace("*", "")
    prev = None
    while prev != h:                     # nested emphasis such as __a _b_ c__
        prev = h
        h = EMPH_RE.sub(r"\2", h)
    return h.strip()


def _keeps(ch):
    cat = unicodedata.category(ch)
    return ch in "-_ " or cat[0] in "LMN" or cat == "Pc"


def github_slug(heading):
    """GitHub's heading id (github-slugger): lower-case; keep letters, marks, digits, "-", "_"; spaces to "-"."""
    h = plain_text(heading).lower()
    return "".join(ch for ch in h if _keeps(ch)).replace(" ", "-")


def numbered_ids(slugs, start=None):
    """Number repeats in order: the first keeps its slug, later ones get -1, -2, ... `start` is a dict of how
    many times each base was already used (pass one dict through several files for book-wide numbering)."""
    seen = {} if start is None else start
    out = []
    for base in slugs:
        n = seen.get(base, 0)
        seen[base] = n + 1
        out.append(base if n == 0 else "%s-%d" % (base, n))
    return out


# ------------------------------------------------------------------------------------------ headings

def headings(text):
    """ATX headings of a Markdown file, in order, skipping fenced code and front matter (the build's rule).
    Fails closed on a Setext heading or a heading inside a block quote: both render with an id but the
    build ignores them, so the two sides would silently disagree."""
    lines = text.replace("\r\n", "\n").split("\n")
    out, i = [], 0
    if lines and lines[0].rstrip() == "---":
        for j in range(1, len(lines)):
            if lines[j].rstrip() in ("---", "..."):
                i = j + 1
                break
    prev_blank = True
    while i < len(lines):
        line = lines[i]
        m = FENCE_OPEN.match(line)
        if m:
            close = _fence_close(m.group(1))
            i += 1
            while i < len(lines) and not close.match(lines[i]):
                i += 1
            i += 1
            prev_blank = False
            continue
        h = HEADING.match(line)
        if h:
            out.append(Heading(i + 1, len(h.group(1)), h.group(2).strip()))
        elif QUOTED_HEADING.match(line):
            raise AnchorError("line %d: heading inside a block quote (not handled)" % (i + 1))
        elif SETEXT.match(line) and not prev_blank:
            raise AnchorError("line %d: Setext heading (not handled)" % (i + 1))
        prev_blank = not line.strip()
        i += 1
    return out


def file_ids(text, slug=github_slug):
    """[(Heading, id)] for one file, ids numbered within the file."""
    hs = headings(text)
    return list(zip(hs, numbered_ids([slug(h.text) for h in hs])))


# ------------------------------------------------------------------------------------------ the map

def pair_file(en_text, es_text, rel=""):
    """The anchors.json entry of one file: headings paired by position."""
    en, es = file_ids(en_text), file_ids(es_text)
    if len(en) != len(es):
        raise AnchorError("%s: %d heading(s) in the English file, %d in the Spanish file" % (rel, len(en), len(es)))
    rows, mapping = [], {}
    for (eh, eid), (sh, sid) in zip(en, es):
        if eh.level != sh.level:
            raise AnchorError("%s:%d: heading level %d in the English file, %d in the Spanish file" % (rel, sh.line, eh.level, sh.level))
        rows.append({"line": eh.line, "level": eh.level, "en": eh.text, "es": sh.text, "en_id": eid, "es_id": sid})
        mapping[eid] = sid
    if len(mapping) != len(rows):
        raise AnchorError("%s: duplicate English anchor after numbering" % rel)
    return {"headings": rows, "map": mapping}


def build_map(pairs):
    """pairs: {rel: (en_text, es_text)} -> the anchors.json document."""
    files = {}
    for rel in sorted(pairs):
        files[rel] = pair_file(pairs[rel][0], pairs[rel][1], rel)
    return {"format": FORMAT, "files": files}


def dumps(doc):
    return json.dumps(doc, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


def load(path=None):
    path = path or ANCHORS_PATH
    with open(path, encoding="utf-8") as f:
        doc = json.load(f)
    if doc.get("format") != FORMAT or "files" not in doc:
        raise AnchorError("%s: unknown anchors.json format" % path)
    return doc


# ------------------------------------------------------------------------------------------ links

CS_SOURCE_CHAPTER = re.compile(r"^lessons/cs-source/chapters/([^/]+\.md)$")


def page_of(rel):
    """The page a file's same-file links are read on. A cs-source chapter intro is copied into the generated
    lessons/cs/ chapter page (cs.py), and its #fragment links name headings of THAT page."""
    m = CS_SOURCE_CHAPTER.match(rel)
    return "lessons/cs/" + m.group(1) if m else rel


ENGLISH = enpath.PathLayer()          # identity: the layer of English text, whose links name English paths


def resolve(rel, dest, layer=None):
    """(target file, fragment) of an internal link written in file `rel` (an ENGLISH key), or None for an external
    link, an absolute path, a mail link or an empty destination. The file part is normalised, repo-root relative,
    and is an English key (anchors.json is keyed by English path).

    `layer` says how the text that holds the link is laid out: a Spanish file written after the rename names its
    targets by their Spanish paths, relative to its own Spanish folder, so the link is read from `layer.work(rel)` and
    the target mapped back to its English key. The default is the real layer of this checkout; pass ENGLISH for text
    that still carries English paths."""
    if not dest or SCHEME_RE.match(dest) or dest.startswith("/"):
        return None
    layer = layer or enpath.load(ROOT)
    path, _, frag = dest.partition("#")
    if not path:
        return page_of(rel), frag
    base = layer.work(page_of(rel))
    full = os.path.normpath(os.path.join(os.path.dirname(base), path.replace("%20", " "))).replace(os.sep, "/")
    if full.startswith(".."):
        return None
    return layer.english(full), frag


def _remap_dest(rel, dest, doc, missing, layer=None):
    r = resolve(rel, dest, layer)
    if r is None or not r[1]:
        return dest
    target, frag = r
    entry = doc["files"].get(target)
    if entry is None:
        return dest                      # a file with no hand-written headings (code, data, folders)
    if frag not in entry["map"]:
        missing.append("%s -> %s#%s" % (rel, target, frag))
        return dest
    return dest[:dest.index("#") + 1] + entry["map"][frag]


def _links_in(line):
    """Destinations on one line: [(start, end, dest)] for inline links and a reference definition."""
    spots = [(m.start(2), m.end(2), m.group(2)) for m in LINK_RE.finditer(line)]
    m = REFDEF_RE.match(line)
    if m:
        spots.append((m.start(2), m.end(2), m.group(2)))
    return sorted(spots)


def _outside_fences(lines):
    """Yield (1-based line number, line) for every line that is not a fence line or inside fenced code."""
    close = None
    for n, line in enumerate(lines, 1):
        if close is None:
            m = FENCE_OPEN.match(line)
            if m:
                close = _fence_close(m.group(1))
            else:
                yield n, line
        elif close.match(line):
            close = None


def remap_text(text, rel, doc, missing=None, layer=None):
    """Rewrite the fragment of every internal link in `text` (a Spanish file as applied from its PO: the
    links still carry the English fragments). Fenced code is left alone. Unknown fragments are left
    unchanged and appended to `missing`. `rel` is the English key of the file."""
    missing = [] if missing is None else missing
    eol = "\r\n" if "\r\n" in text else "\n"
    lines = text.replace("\r\n", "\n").split("\n")
    for n, line in _outside_fences(lines):
        for s, e, dest in reversed(_links_in(line)):
            line = line[:s] + _remap_dest(rel, dest, doc, missing, layer) + line[e:]
        lines[n - 1] = line
    return eol.join(lines)


def dest_map(en_text, rel, doc):
    """{English destination as written: remapped destination} for one file; feeds invariants.Context.anchor_map
    (I4 compares the remapped English destinations with the Spanish ones)."""
    out, missing = {}, []
    for _, line in _outside_fences(en_text.replace("\r\n", "\n").split("\n")):
        for _, _, dest in _links_in(line):
            new = _remap_dest(rel, dest, doc, missing, ENGLISH)      # English text: English paths
            if new != dest:
                out[dest] = new
    return out


_DOC_CACHE = {}


def stored_document(root=ROOT):
    """translation/anchors.json of the real checkout, read once per process; None for another root, a missing file or an
    unreadable one (the early phases have none: then fragments are left as they are)."""
    if root != ROOT:
        return None
    if root not in _DOC_CACHE:
        try:
            _DOC_CACHE[root] = load()
        except (OSError, AnchorError, ValueError):
            _DOC_CACHE[root] = None
    return _DOC_CACHE[root]


def layout_text(text, rel, layer=None, root=ROOT):
    """`text` (English layout and English fragments) as it reads in this checkout: references to renamed paths in the Spanish
    layout (enpath.remap_text), then the fragment of every internal link re-aimed at the heading id of the target in this
    edition (anchors.json). Identity when the layer is not moved. The one function apply.py (writing) and verify.py (checking)
    share, so a file is never right for one and wrong for the other."""
    layer = layer or enpath.load(root)
    new = enpath.remap_text(text, rel, layer, root)
    doc = stored_document(root) if layer.moved else None
    if doc is None or not rel.endswith(".md"):
        return new
    return remap_front_matter(remap_text(new, layer.english(rel), doc, None, layer), doc, layer)


FM_LINK_KEYS = ("lesson", "exercise")


def remap_front_matter(text, doc, layer):
    """Re-aim the fragment of the front-matter keys `lesson:` and `exercise:` (values 'path#fragment', the path relative to
    lessons/ and already in this edition's layout) at the heading id of the target in this edition. Unknown targets and
    fragments stay as they are (the book build reports them)."""
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return text
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            break
        m = re.match(r'^(%s): "([^"#]+)#([^"]+)"(.*)$' % "|".join(FM_LINK_KEYS), lines[i])
        if not m:
            continue
        entry = doc["files"].get(layer.english("lessons/" + m.group(2)))
        if entry is None:
            continue
        for h in entry["headings"]:
            if h["en_id"] == m.group(3):
                lines[i] = '%s: "%s#%s"%s' % (m.group(1), m.group(2), h["es_id"], m.group(4))
                break
    return "\n".join(lines)


def check_links(rel, es_text, doc, layer=None):
    """Problems for the internal links of one Spanish file: each fragment must be an id of the target file."""
    problems = []
    for n, line in _outside_fences(es_text.replace("\r\n", "\n").split("\n")):
        for _, _, dest in _links_in(line):
            r = resolve(rel, dest, layer)
            if r is None or not r[1]:
                continue
            entry = doc["files"].get(r[0])
            if entry is None:
                continue
            if r[1] not in {h["es_id"] for h in entry["headings"]}:
                problems.append("%s:%d: link %s points at no heading id of %s" % (rel, n, dest, r[0]))
    return problems


def slug_problems(rel, text):
    """Headings whose GitHub id differs from the build's id (the book would then resolve the link wrongly)."""
    out = []
    for h in headings(text):
        a, b = github_slug(h.text), build_slug(h.text)
        if a != b:
            out.append("%s:%d: GitHub id %r differs from the build's id %r" % (rel, h.line, a, b))
    return out


def book_ids(texts):
    """Pandoc ids across the whole book: {rel: [id, ...]} with repeats numbered across files, in order.
    `texts` is an ordered mapping rel -> text (the chapters.txt order)."""
    seen, out = {}, {}
    for rel, text in texts.items():
        out[rel] = numbered_ids([github_slug(h.text) for h in headings(text)], seen)
    return out


# ------------------------------------------------------------------------------------------ files

def read_config():
    cfg = {}
    with open(os.path.join(ROOT, "loop", "CONFIG.yaml"), encoding="utf-8") as f:
        for l in f:
            m = re.match(r"^([a-z_]+):\s*([^#\n]*?)\s*(?:#.*)?$", l)
            if m:
                cfg[m.group(1)] = m.group(2).strip()
    return cfg


def english_text(cfg, rel):
    clone, sha = cfg.get("english_clone_path"), cfg.get("english_commit")
    if not clone or not sha or not os.path.isdir(clone):
        raise AnchorError("English clone not available (english_clone_path in loop/CONFIG.yaml)")
    r = subprocess.run(["git", "-C", clone, "show", "%s:%s" % (sha, rel)], capture_output=True)
    if r.returncode != 0:
        raise AnchorError("%s: not in the English commit" % rel)
    return r.stdout.decode("utf-8").replace("\r\n", "\n")


def read_es(rel):
    """The working-tree text of the file with English key `rel` (read at its Spanish name after the rename)."""
    with open(enpath.load(ROOT).full(rel), encoding="utf-8", newline="") as f:
        return f.read().replace("\r\n", "\n")


def markdown_files():
    import inventory
    return [p for p in inventory.list_files(ROOT)
            if p.endswith(".md") and set(inventory.classify(p)) & {"authored", "generated"}]


def current_document():
    cfg = read_config()
    pairs = {rel: (english_text(cfg, rel), read_es(rel)) for rel in markdown_files()}
    return build_map(pairs), pairs


def check_all():
    """Every check over the working tree. Returns a list of problem strings."""
    try:
        doc, pairs = current_document()
    except AnchorError as e:
        return [str(e)]
    problems = []
    if not os.path.exists(ANCHORS_PATH):
        problems.append("translation/anchors.json is missing (run --generate)")
    else:
        try:
            stored = load()
        except (AnchorError, ValueError) as e:
            return problems + [str(e)]
        if stored != doc:
            stale = sorted(r for r in set(stored["files"]) | set(doc["files"]) if stored["files"].get(r) != doc["files"].get(r))
            problems.append("translation/anchors.json is stale for %d file(s), first: %s (run --generate)" % (len(stale), stale[0]))
    for rel, (_, es) in sorted(pairs.items()):
        problems += slug_problems(rel, es)
        problems += check_links(rel, es, doc)
    return problems


def main(argv):
    if len(argv) == 3 and argv[1] == "--slug":
        t = argv[2]
        print("build:  %s\ngithub: %s" % (build_slug(t), github_slug(t)))
        return 0
    if len(argv) == 2 and argv[1] == "--generate":
        try:
            doc, _ = current_document()
        except AnchorError as e:
            print("FAIL %s" % e)
            return 1
        with open(ANCHORS_PATH, "w", encoding="utf-8", newline="\n") as f:
            f.write(dumps(doc))
        n = sum(len(v["headings"]) for v in doc["files"].values())
        print("anchors.json: %d file(s), %d heading(s)" % (len(doc["files"]), n))
        return 0
    if len(argv) == 2 and argv[1] == "--check":
        problems = check_all()
        for p in problems:
            print("FAIL " + p)
        print("anchors %s" % ("FAILED (%d problem(s))" % len(problems) if problems else "OK"))
        return 1 if problems else 0
    if len(argv) >= 3 and argv[1] == "--remap":
        try:
            doc = load()
        except (OSError, AnchorError, ValueError) as e:
            print("FAIL %s" % e)
            return 1
        bad = 0
        for path in argv[2:]:
            rel, path = enpath.locate(path, ROOT)
            with open(path, encoding="utf-8", newline="") as f:
                text = f.read()
            missing = []
            new = remap_text(text, rel, doc, missing)
            for m in missing:
                print("FAIL unknown anchor: " + m)
            bad += len(missing)
            if new != text and not missing:
                with open(path, "w", encoding="utf-8", newline="") as f:
                    f.write(new)
        return 1 if bad else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
