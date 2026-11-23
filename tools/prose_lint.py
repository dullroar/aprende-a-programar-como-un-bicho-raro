#!/usr/bin/env python3
"""prose_lint: the editorial lints of the first external review (translation/review-decisions-2026-11-20.md, Part E).

Pure functions over text. tools/invariants.py wires them in (segment checks in check_segment, file checks in
check_files); each returns Hit(inv, msg) pairs and the invariants module turns them into Findings.

  I21  identifiers   a name that exists in the code stays literal in Mermaid labels, accDescr, table cells and prose (B2);
                     the rules are translation/identifiers.yaml (also, step, where, from persisted in, over-40?, ...)
  I22  units         a range keeps the unit of the English: "de 10 a 19 horas", never "10 a 19 tarjetas" (B1)
  I23  diagrams      an unquoted parenthesis in an edge label, and (with a renderer) parse, render and the 8.4 pt floor (B7)
  I24  glosses       one first-use gloss per file (B5) and no absolute guarantee the English does not make (B3);
                     the phrase list is translation/style-lint.yaml
  I25  typography    non-breaking space before "%", no comma before a simple "o" or "y" (B6)
  I26  layout        table dimensions equal the English table's, every fence is closed, fence kinds equal (Part E item 11)

Usage:
  python3 -I tools/prose_lint.py --list      print the lint table
  python3 -I tools/prose_lint.py EN.md ES.md the file-level lints (I23 static, I24 glosses, I26) on a finished pair
Exit 0 = no findings.
"""
import fnmatch
import os
import re
import sys
from collections import Counter, namedtuple

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import mask  # noqa: E402

Hit = namedtuple("Hit", "inv msg")

TABLE = {
    "I21": "Code identifiers stay literal in labels, accDescr, table cells and prose",
    "I22": "Numeric ranges keep the English unit (10 a 19 horas, not tarjetas)",
    "I23": "Diagrams: quoted special characters in edge labels, render, 8.4 pt",
    "I24": "One gloss per file; no added absolute guarantee",
    "I25": "Typography: nbsp before %, no comma before a simple o or y",
    "I26": "Layout: table dimensions, fences, fence kinds",
}

MIN_POINTS = 8.4            # printed size of a diagram label; below this it is unreadable on paper (diagrams.MIN_SCALE)
NBSP = chr(0xA0)
MACRO_RE = re.compile(r"\{\{[^}\n]+\}\}|\[\[[^\]\n]+\]\]")


def plain(text, filler=" "):
    """What a reader reads as words: inline code, placeholders and macros are replaced by `filler` (a space, or "X"
    where a removed item must still count as an item, as in the list "`a`, `b` y `c`")."""
    return MACRO_RE.sub(filler, mask.PH_RE.sub(filler, re.sub(r"`[^`\n]*`", filler, text)))


# ------------------------------------------------------------------------------------------ configuration

class Rule:
    __slots__ = ("literal", "en", "kinds", "roles", "files")

    def __init__(self, d):
        self.literal = d["literal"]
        pat = d.get("en") or r"(?<![\w])%s(?![\w])" % re.escape(self.literal)
        self.en = re.compile(pat)
        self.kinds = tuple(d.get("kinds") or ())
        self.roles = tuple(d.get("roles") or ())
        self.files = tuple(d.get("files") or ())

    def applies(self, kind, role, rel):
        return ((not self.kinds or kind in self.kinds) and (not self.roles or role in self.roles)
                and (not self.files or any(fnmatch.fnmatch(rel, p) for p in self.files)))


class Config:
    def __init__(self, identifiers=(), claims=(), gloss_pattern=r"\(\*[^*\n]{2,40}\*\)", render=False, renderer=None):
        self.rules = [Rule(d) for d in identifiers]
        self.claims = [(c["es"].lower(), re.compile(c["en"], re.I) if c.get("en") else None) for c in claims]
        self.gloss_re = re.compile(gloss_pattern)
        self.render = render            # I23 renders the diagrams of a finished file (needs Mermaid CLI and Chromium)
        self.renderer = renderer        # a callable (sources: {text: where}) -> ({text: points}, [error]); default: the book's


def load_config(root=ROOT, render=False):
    def load(name):
        path = os.path.join(root, "translation", name)
        if not os.path.isfile(path):
            return {}
        with open(path, encoding="utf-8") as f:
            return yaml.safe_load(f) or {}
    ids, style = load("identifiers.yaml"), load("style-lint.yaml")
    derived = load("identifiers.ledger.yaml")            # derived from the identifier ledger (Part II, tools/part2_inv.py)
    return Config((ids.get("identifiers") or []) + (derived.get("identifiers") or []), style.get("absolute_claims") or [],
                  style.get("gloss_pattern") or r"\(\*[^*\n]{2,40}\*\)", render)


# ------------------------------------------------------------------------------------------ segment lints

def token_present(literal, text):
    """`literal` appears in `text` as a whole token (a letter, digit, underscore, hyphen or dot next to it breaks the token)."""
    left = r"(?<![\w\-.])" if re.match(r"\w", literal) else ""
    right = r"(?![\w\-])" if re.search(r"\w$", literal) else ""
    return re.search(left + re.escape(literal) + right, text) is not None


def applicable_rules(src, rel, cfg):
    """The identifier rules whose context is in the English segment `src` (the names this segment must keep)."""
    kind = getattr(src, "kind", "")
    role = getattr(src, "info", "") if kind == "mermaid_label" else ""
    return [r for r in cfg.rules if r.applies(kind, role, rel) and r.en.search(src.text)]


def without_identifiers(src, rel, cfg, source_text, target_text):
    """`source_text` and `target_text` with the segment's identifier names removed, for the glossary check (I7) and the
    inverted-mark check (I10): a kept name is not a rendering ('step' stays 'step', not 'paso'; the '?' of `over-40?` is not a question)."""
    for r in applicable_rules(src, rel, cfg):
        pat = re.compile(r"(?<![\w\-])%s(?![\w\-])" % re.escape(r.literal))
        source_text, target_text = pat.sub(" ", source_text), pat.sub(" ", target_text)
    return source_text, target_text


def identifier_hits(src, restored, rel, cfg):
    """I21: every rule whose English context is in the source needs its literal in the (restored) target."""
    out = []
    for r in applicable_rules(src, rel, cfg):
        if not token_present(r.literal, restored):
            out.append(Hit("I21", "identifier '%s' must stay literal (the English names it here); describe around it, never translate it"
                           % r.literal))
    return out


RANGE_RE = re.compile(r"(?<![\w.])(?P<a>\d+)\s*(?:a|–|—|-|y|al?|to)\s*(?P<b>\d+)(?!\w)(?!\.\d)(?P<tail>[^.!?\n]*)", re.I)
HOURS_RANGE = ("10", "19")
CARDS_RANGE = ("3", "5")


def unit_hits(restored):
    """I22 (rule B1): the shared challenge's 10 to 19 are hours per card; the 3 to 5 are cards."""
    out = []
    text = plain(restored)
    for m in RANGE_RE.finditer(text):
        pair, tail = (m.group("a"), m.group("b")), m.group("tail").lstrip()
        nxt = re.match(r"([^\W\d_]+)", tail)
        word = nxt.group(1).lower() if nxt else ""
        if pair == HOURS_RANGE:
            if word.startswith("tarjeta"):
                out.append(Hit("I22", "'%s a %s %s': the range is hours per card (horas por tarjeta), never cards" % (pair + (word,))))
            # the sentence that holds the range must name the unit
            start = max(text.rfind(c, 0, m.start()) for c in ".!?\n") + 1
            if word.startswith("tarjeta"):
                pass
            elif "hora" not in text[start:m.end()].lower() and "hora" not in text[m.end():m.end() + 40].lower():
                out.append(Hit("I22", "range '%s a %s' names no unit (write horas por tarjeta)" % pair))
        elif pair == CARDS_RANGE and word.startswith("hora"):
            out.append(Hit("I22", "'%s a %s horas': the 3 to 5 are cards, the hours are 10 to 19 per card" % pair))
    return out


def claim_hits(src_text, restored, cfg):
    """I24 (rule B3): an absolute claim the translator added. A phrase is a finding unless the English makes that claim."""
    low = plain(restored).lower()
    out, found = [], []
    for phrase, en_rx in sorted(cfg.claims, key=lambda c: -len(c[0])):     # the longest phrase first: report one claim once
        if phrase in low and not (en_rx and en_rx.search(src_text)) and not any(phrase in f for f in found):
            found.append(phrase)
            out.append(Hit("I24", "added guarantee '%s': the English makes no such claim (soften it; see house style B3)" % phrase))
    return out


PERCENT_RE = re.compile(r"(?<![\w.,])(\d+(?:[.,]\d+)?)([ ]?)%")
COMMA_CONJ_RE = re.compile(r",\s+(?P<conj>y|o|u|e)(?=\s)", re.I)
SIMPLE_WORDS = 6            # a clause of at most this many words on each side of the conjunction is a simple coordination
CLAUSE_END_RE = re.compile(r"[,.;:!?¡¿()]")


def _words(text):
    return len(re.findall(r"[^\W_]+", text))


def comma_conj_hits(text):
    """Commas before a simple 'o' or 'y': both clauses next to the conjunction are short (at most SIMPLE_WORDS words), and the
    conjunction does not open a parenthetical ("entorno aislado, o *sandbox*, que..."). A comma between two long clauses is fine."""
    out = []
    for m in COMMA_CONJ_RE.finditer(text):
        left_start = max([text.rfind(c, 0, m.start()) for c in ",.;:!?¡¿()"] + [-1]) + 1
        left = text[left_start:m.start()]
        rest = text[m.end():]
        stop = CLAUSE_END_RE.search(rest)
        right = rest[:stop.start()] if stop else rest
        closes_with_comma = bool(stop) and stop.group(0) == ","
        if closes_with_comma and _words(right) <= 3:
            continue                                      # ", o *sandbox*," is an aside, not a coordination
        if _words(left) <= SIMPLE_WORDS and _words(right) <= SIMPLE_WORDS:
            ctx = text[max(0, left_start):m.end() + len(right)].strip()
            out.append(Hit("I25", "comma before a simple '%s' ('%s'): no comma before a simple o or y" % (m.group("conj"), ctx[:60])))
    return out


def typography_hits(restored, kind=""):
    """I25 (rule B6): '30 %' with a non-breaking space; no comma before a simple 'o' or 'y'."""
    text = plain(restored, "X")
    out = []
    for m in PERCENT_RE.finditer(text):
        out.append(Hit("I25", "'%s%s%%': write a non-breaking space before %% (%s%s%%)" % (m.group(1), m.group(2), m.group(1), NBSP)))
    if kind != "mermaid_label":
        out += comma_conj_hits(text)
    return out


def segment_hits(src, restored, rel, cfg):
    """All the segment-level lints for one translated segment (`restored` is the target with code restored)."""
    kind = getattr(src, "kind", "")
    out = identifier_hits(src, restored, rel, cfg)
    out += unit_hits(restored)
    out += claim_hits(src.text, restored, cfg)
    out += typography_hits(restored, kind)
    return out


# ------------------------------------------------------------------------------------------ file lints

FENCE_RE = re.compile(r"^( {0,3})(`{3,}|~{3,})\s*([^\s`]*)")


def fences(text):
    """[(info, fence mark, closed)] for every fenced block of `text`, in order; a fence nobody closes is closed=False."""
    out, open_ = [], None
    for line in text.replace("\r\n", "\n").split("\n"):
        m = FENCE_RE.match(line)
        if open_ is None:
            if m:
                open_ = [m.group(3), m.group(2), False]
        elif m and m.group(2)[0] == open_[1][0] and len(m.group(2)) >= len(open_[1]) and not m.group(3):
            open_[2] = True
            out.append(tuple(open_))
            open_ = None
    if open_ is not None:
        out.append(tuple(open_))
    return out


def outside_fences(text):
    """The lines of `text` that are not inside a fenced block (a fence line is dropped)."""
    keep, open_ = [], None
    for line in text.replace("\r\n", "\n").split("\n"):
        m = FENCE_RE.match(line)
        if open_ is None:
            if m:
                open_ = m.group(2)
            else:
                keep.append(line)
        elif m and m.group(2)[0] == open_[0] and len(m.group(2)) >= len(open_) and not m.group(3):
            open_ = None
    return keep


def split_cells(line):
    """Cells of one table row: `|` inside a code span or escaped as `\\|` is not a separator."""
    body = re.sub(r"`[^`\n]*`", lambda m: m.group(0).replace("|", "\0"), line.strip())
    body = body.replace("\\|", "\0")
    if body.startswith("|"):
        body = body[1:]
    if body.endswith("|") :
        body = body[:-1]
    return [c.replace("\0", "|").strip() for c in body.split("|")]


SEP_CELL_RE = re.compile(r"^:?-{1,}:?$")


def tables(text):
    """[(first line number, header cells, [row cells])]: GitHub tables outside fences (header row, separator row, body rows)."""
    lines = outside_fences(text)
    out, i = [], 0
    while i + 1 < len(lines):
        head, sep = lines[i], lines[i + 1]
        if "|" in head and "|" in sep and all(SEP_CELL_RE.match(c) for c in split_cells(sep) if c != "") and split_cells(sep):
            rows, j = [], i + 2
            while j < len(lines) and "|" in lines[j] and lines[j].strip():
                rows.append(split_cells(lines[j]))
                j += 1
            out.append((i + 1, split_cells(head), rows, split_cells(sep)))
            i = j
        else:
            i += 1
    return out


def layout_hits(en_text, es_text):
    """I26: table dimensions and fences of a finished file against its English source."""
    out = []
    fa, fb = fences(en_text), fences(es_text)
    for info, mark, closed in fb:
        if not closed:
            out.append(Hit("I26", "fenced block (%s) is never closed" % (info or mark)))
    if [f[0] for f in fa] != [f[0] for f in fb]:
        out.append(Hit("I26", "fenced block kinds differ: %s in the source, %s in the target"
                       % ([f[0] or "-" for f in fa], [f[0] or "-" for f in fb])))
    ta, tb = tables(en_text), tables(es_text)
    if len(ta) != len(tb):
        out.append(Hit("I26", "%d table(s) in the source, %d in the target" % (len(ta), len(tb))))
        return out
    for (la, ha, ra, sa), (lb, hb, rb, sb) in zip(ta, tb):
        where = "table at line %d" % lb
        if len(ha) != len(hb):
            out.append(Hit("I26", "%s: %d column(s) in the header, %d in the source" % (where, len(hb), len(ha))))
        if len(ra) != len(rb):
            out.append(Hit("I26", "%s: %d body row(s), %d in the source" % (where, len(rb), len(ra))))
        for n, row in enumerate(rb):
            if len(row) != len(hb):
                out.append(Hit("I26", "%s, row %d: %d cell(s), the header has %d" % (where, n + 1, len(row), len(hb))))
        if [c for c in sa] != [c for c in sb]:
            out.append(Hit("I26", "%s: the alignment row differs from the source" % where))
    return out


def gloss_hits(es_text, cfg):
    """I24 (rule B5): the same first-use gloss written twice in one file."""
    text = "\n".join(outside_fences(es_text))
    count = Counter(m.group(0).lower() for m in cfg.gloss_re.finditer(text))
    return [Hit("I24", "gloss %s appears %d times in this file; define a term once per file (house style B5), then use the plain term" % (g, n))
            for g, n in sorted(count.items()) if n > 1]


# ------------------------------------------------------------------------------------------ diagrams (I23)

MERMAID_FENCE_RE = re.compile(r"^```mermaid[ \t]*\n(.*?)^```[ \t]*$", re.M | re.S)
SPECIAL_EDGE = re.compile(r"[()\[\]{}<>]")
EDGE_TEXT_RE = re.compile(r"(?<=[-=.~xo>])\|(?P<t>[^|\"\n]+)\|")
EDGE_DASH_RE = re.compile(r"(?:--|==|-\.)\s+(?P<t>[^\"\s>\-.=][^>\n]*?)\s+(?:-->|---|==>|===|-\.->|-\.-)")


def diagram_sources(text):
    return [m.group(1) for m in MERMAID_FENCE_RE.finditer(text.replace("\r\n", "\n"))]


def edge_label_hits(source):
    """An edge label with a parenthesis, bracket, brace or angle bracket must be quoted (`|"text (x)"|`) or reworded."""
    out = []
    for line in source.split("\n"):
        for rx in (EDGE_TEXT_RE, EDGE_DASH_RE):
            for m in rx.finditer(line):
                if SPECIAL_EDGE.search(m.group("t")):
                    out.append(Hit("I23", "edge label '%s' has a parenthesis or bracket and is not quoted (quote it or reword it)"
                                   % m.group("t").strip()[:50]))
    return out


def book_renderer(sources):
    """Render with the book's Mermaid CLI. Returns ({source: printed label points}, [error text])."""
    sys.path.insert(0, os.path.join(ROOT, "lessons", "book"))
    sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
    import diagrams  # noqa: E402
    renderer, why = diagrams.find_renderer()
    if renderer is None:
        return {}, ["cannot render: " + why]
    figs, errors = diagrams.render_all(renderer, sources)
    return {src: f.points for src, f in figs.items() if hasattr(f, "points")}, errors


def render_hits(sources, cfg):
    """Parse and render every diagram in `sources` ({text: where}); fail closed when nothing can render."""
    if not sources:
        return []
    points, errors = (cfg.renderer or book_renderer)(sources)
    out = [Hit("I23", e.strip().replace("\n", " ")[:300]) for e in errors]
    for src, where in sources.items():
        pts = points.get(src)
        if pts is not None and pts < MIN_POINTS:
            out.append(Hit("I23", "%s prints its labels at %.1f pt (the floor is %.1f pt): shorten the labels, never loosen the gate"
                           % (where, pts, MIN_POINTS)))
    return out


def diagram_hits(en_text, es_text, cfg):
    """I23 for a finished file: the static edge-label rule on every Spanish diagram, then render the ones that differ from the
    English (a copied diagram is the English file's business)."""
    out, en_src = [], set(diagram_sources(en_text))
    wanted = {}
    for n, src in enumerate(diagram_sources(es_text), 1):
        out += [Hit(h.inv, "diagram %d: %s" % (n, h.msg)) for h in edge_label_hits(src)]
        if src not in en_src:
            wanted[src] = "diagram %d" % n
    if cfg.render:
        out += render_hits(wanted, cfg)
    return out


def file_hits(en_text, es_text, cfg):
    """Every file-level lint for a finished Spanish file against its English source."""
    return diagram_hits(en_text, es_text, cfg) + gloss_hits(es_text, cfg) + layout_hits(en_text, es_text)


# ------------------------------------------------------------------------------------------ CLI

def read_raw(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def main(argv):
    args = argv[1:]
    if args == ["--list"]:
        for k, v in TABLE.items():
            print("%-4s %s" % (k, v))
        return 0
    if len(args) == 2:
        hits = file_hits(read_raw(args[0]), read_raw(args[1]), load_config(render=False))
        for h in hits:
            print("%s %s: %s" % (h.inv, args[1], h.msg))
        print("prose_lint: %s" % ("FAIL (%d finding(s))" % len(hits) if hits else "OK"))
        return 1 if hits else 0
    print(__doc__.split("Usage:")[1].rstrip())
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
