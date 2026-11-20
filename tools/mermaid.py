#!/usr/bin/env python3
"""Mermaid label extraction (plan 7.1 R6, 8.1; invariants I5 and I10).

A Mermaid fence is a diagram in a tiny language. Only prose inside it may be translated: accTitle, accDescr,
node labels, edge labels, subgraph labels, participant aliases, message and note text, block titles (loop,
alt, ...), state labels and transition labels. Everything else (the diagram type, node IDs, arrows, shapes,
directives, classDef, class, style) is the SKELETON and must stay byte-identical.

extract(body_lines) returns the label Spans of one diagram: for each, the line index and column range of the
text that may change. apply_spans() puts new text into those ranges and touches nothing else. The skeleton is
the body with every label emptied; two diagrams with equal skeletons differ only in label text (I5).

Supported diagram types: flowchart/graph, sequenceDiagram, stateDiagram-v2. Anything else, and any construct
the extractor does not understand (an unquoted node label, click, multi-line accDescr), raises MermaidError:
the segmenter fails closed rather than guess.

Usage: python3 -I tools/mermaid.py FILE.md   (lists the labels of every Mermaid fence)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)


class MermaidError(ValueError):
    """The diagram has a construct the extractor does not handle."""


class Span:
    __slots__ = ("line", "start", "end", "text", "role", "quoted")

    def __init__(self, line, start, end, text, role, quoted):
        self.line, self.start, self.end = line, start, end   # columns: text == lines[line][start:end]
        self.text, self.role, self.quoted = text, role, quoted

    def __repr__(self):
        return "Span(%d:%d-%d %s %r)" % (self.line, self.start, self.end, self.role, self.text)


ACC_RE = re.compile(r"^(?P<pre>\s*(?P<key>accTitle|accDescr)\s*:\s*)(?P<txt>.*?)\s*$")
ACC_BLOCK_RE = re.compile(r"^\s*accDescr\s*\{")
HEADER_RE = re.compile(r"^\s*(flowchart|graph|sequenceDiagram|stateDiagram-v2|stateDiagram)\b")
QUOTED_RE = re.compile(r'"([^"\n]*)"')
PIPE_RE = re.compile(r"(?<=[-=.~xo>])\|(?P<t>[^|\"\n\x00]+)\|")
FLOW_SKIP_RE = re.compile(r"^\s*(?:flowchart|graph|direction|classDef|class|style|linkStyle|end)\b")
FLOW_CLICK_RE = re.compile(r"^\s*click\b")
UNQUOTED_SHAPE_RE = re.compile(r"[A-Za-z0-9_]\s*(?:\(\(|\(\[|\[\[|\[/|\[\\|\{\{|\[|\(|\{|>)\s*[^\"\s\[\(\{\x00>]")
UNQUOTED_EDGE_RE = re.compile(r"(?:--|==|-\.)\s+[^\"\s>\-.=][^\x00>]*?\s+(?:-->|---|==>|===|-\.->|-\.-)")

SEQ_ARROW = r"(?:-->>|->>|-->|->|--x|-x|--\)|-\))[+-]?"
SEQ_MSG_RE = re.compile(r"^(?P<pre>\s*[^\s:]+\s*" + SEQ_ARROW + r"\s*[^\s:]+\s*:\s*)(?P<txt>.*?)\s*$")
SEQ_NOTE_RE = re.compile(r"^(?P<pre>\s*Note\s+(?:over|left of|right of)\s+[^:]+:\s*)(?P<txt>.*?)\s*$", re.I)
SEQ_ALIAS_RE = re.compile(r"^(?P<pre>\s*(?:participant|actor)\s+\S+\s+as\s+)(?P<txt>.*?)\s*$")
SEQ_BLOCK_RE = re.compile(r"^(?P<pre>\s*(?:loop|alt|else|opt|par|and|critical|option|break)\s+)(?P<txt>\S.*?)\s*$")
SEQ_PLAIN_RE = re.compile(r"^\s*(?:sequenceDiagram|participant\s+\S+|actor\s+\S+|autonumber|activate\s+\S+|"
                          r"deactivate\s+\S+|end|else|and|option|opt|loop|alt|par|critical|break|rect\b.*)\s*$")
SEQ_TITLE_RE = re.compile(r"^\s*title\b")

STATE_DECL_RE = re.compile(r'^(?P<pre>\s*state\s+")(?P<txt>[^"\n]*)(?P<post>"\s+as\s+\S+\s*\{?\s*)$')
STATE_EDGE_RE = re.compile(r"^(?P<pre>\s*\S+\s*-->\s*\S+\s+:\s*)(?P<txt>.*?)\s*$")
STATE_PLAIN_RE = re.compile(r"^\s*(?:stateDiagram(?:-v2)?|direction\s+\w+|\}|\S+\s*-->\s*\S+|--)\s*$")
STATE_PLAIN_ID_RE = re.compile(r"^\s*(?:class|classDef|style)\b|^\s*state\s+\S+\s*(?:\{|<<.*>>)?\s*$")

ENTITY_RE = re.compile(r"#(?:[A-Za-z]+|\d+);")


def diagram_type(lines):
    for ln in lines:
        s = ln.strip()
        if not s or s.startswith("%%"):
            continue
        m = HEADER_RE.match(s)
        if not m:
            raise MermaidError("unsupported or unrecognised diagram type: %r" % s[:40])
        t = m.group(1)
        return "flow" if t in ("flowchart", "graph") else "seq" if t == "sequenceDiagram" else "state"
    raise MermaidError("empty Mermaid diagram")


def _acc(i, line):
    m = ACC_RE.match(line)
    if not m:
        return None
    if not m.group("txt"):
        raise MermaidError("line %d: empty %s" % (i + 1, m.group("key")))
    s = len(m.group("pre"))
    return Span(i, s, s + len(m.group("txt")), m.group("txt"), m.group("key"), False)


def _group_span(i, m, role):
    s = len(m.group("pre"))
    return Span(i, s, s + len(m.group("txt")), m.group("txt"), role, False)


def _flow_line(i, line, out):
    blanked = []
    last = 0
    spans = []
    for m in QUOTED_RE.finditer(line):
        spans.append(Span(i, m.start(1), m.end(1), m.group(1), "label", True))
        blanked.append(line[last:m.start(1)])
        blanked.append("\x00" * len(m.group(1)))
        last = m.end(1)
    blanked.append(line[last:])
    blank = "".join(blanked)
    for m in PIPE_RE.finditer(blank):
        t = m.group("t")
        lead = len(t) - len(t.lstrip())
        stripped = t.strip()
        if stripped:
            spans.append(Span(i, m.start("t") + lead, m.start("t") + lead + len(stripped), stripped, "edge", False))
    if UNQUOTED_EDGE_RE.search(blank):
        raise MermaidError("line %d: unquoted '-- text -->' edge label is not supported" % (i + 1))
    probe = PIPE_RE.sub(lambda m: "|" + "\x00" * len(m.group("t")) + "|", blank)
    if UNQUOTED_SHAPE_RE.search(probe):
        raise MermaidError("line %d: unquoted node label is not supported: %r" % (i + 1, line.strip()[:60]))
    spans.sort(key=lambda s: s.start)
    out.extend(spans)


def extract(lines):
    """Label spans of one diagram body (the lines between the fences), in document order."""
    kind = diagram_type(lines)
    out = []
    for i, line in enumerate(lines):
        s = line.strip()
        if not s or s.startswith("%%"):
            continue
        if ACC_BLOCK_RE.match(line):
            raise MermaidError("line %d: multi-line accDescr is not supported" % (i + 1))
        acc = _acc(i, line)
        if acc:
            out.append(acc)
            continue
        if HEADER_RE.match(s):
            continue
        if kind == "flow":
            if FLOW_CLICK_RE.match(line):
                raise MermaidError("line %d: click is not supported" % (i + 1))
            if line.lstrip().startswith(("%%{", "---")):
                raise MermaidError("line %d: directive or front matter is not supported" % (i + 1))
            if FLOW_SKIP_RE.match(line) and not s.startswith("subgraph"):
                continue
            _flow_line(i, line, out)
        elif kind == "seq":
            if SEQ_TITLE_RE.match(line):
                raise MermaidError("line %d: sequence title is not supported (use accTitle)" % (i + 1))
            m = SEQ_ALIAS_RE.match(line) or SEQ_NOTE_RE.match(line) or SEQ_MSG_RE.match(line) \
                or SEQ_BLOCK_RE.match(line)
            if m:
                role = ("participant" if SEQ_ALIAS_RE.match(line) else "note" if SEQ_NOTE_RE.match(line)
                        else "message" if SEQ_MSG_RE.match(line) else "block")
                out.append(_group_span(i, m, role))
            elif not SEQ_PLAIN_RE.match(line):
                raise MermaidError("line %d: unrecognised sequence-diagram line: %r" % (i + 1, s[:60]))
        else:
            m = STATE_DECL_RE.match(line)
            if m:
                out.append(_group_span(i, m, "state"))
                continue
            m = STATE_EDGE_RE.match(line)
            if m:
                out.append(_group_span(i, m, "transition"))
                continue
            if not (STATE_PLAIN_RE.match(line) or STATE_PLAIN_ID_RE.match(line)):
                raise MermaidError("line %d: unrecognised state-diagram line: %r" % (i + 1, s[:60]))
    return out


def apply_spans(lines, spans, texts):
    """Lines with each span's text replaced by the matching entry of `texts`. Nothing else changes."""
    if len(spans) != len(texts):
        raise ValueError("%d labels but %d replacements" % (len(spans), len(texts)))
    new = list(lines)
    for sp, tx in sorted(zip(spans, texts), key=lambda p: (p[0].line, -p[0].start)):
        new[sp.line] = new[sp.line][:sp.start] + tx + new[sp.line][sp.end:]
    return new


def skeleton(lines):
    """The diagram with every label emptied. Equal skeletons mean only label text differs (I5)."""
    spans = extract(lines)
    return apply_spans(lines, spans, [""] * len(spans))


def label_problems(span, text):
    """Problems that would make `text` break the Mermaid syntax of `span` (I10). Entities such as the quote
    and angle ones (#quot; #gt; #lt;) are legal and are ignored by the ';' rule."""
    p = []
    if not text.strip():
        p.append("empty label")
    if "\n" in text or "\r" in text:
        p.append("label spans several lines")
    if span.quoted and '"' in text:
        p.append('label contains a double quote (use the #quot; entity)')
    if span.role == "edge" and ("|" in text or '"' in text):
        p.append("edge label contains | or a double quote")
    if span.role in ("message", "note", "block", "participant", "transition") and ";" in ENTITY_RE.sub("", text):
        p.append("';' would end the statement")
    if span.role == "accDescr" and text.lstrip().startswith("{"):
        p.append("accDescr text must not open a block")
    if span.role == "state" and '"' in text:
        p.append("state label contains a double quote")
    return p


def skeleton_problems(en_lines, es_lines):
    """I5: compare two diagram bodies. Returns problem strings (empty = same skeleton and same label slots)."""
    try:
        a, b = extract(en_lines), extract(es_lines)
    except MermaidError as e:
        return ["cannot read the diagram: %s" % e]
    problems = []
    if [(s.line, s.role) for s in a] != [(s.line, s.role) for s in b]:
        problems.append("label slots differ: %d in the source, %d in the target" % (len(a), len(b)))
    sa, sb = apply_spans(en_lines, a, [""] * len(a)), apply_spans(es_lines, b, [""] * len(b))
    if len(sa) != len(sb):
        problems.append("line count differs: %d -> %d" % (len(sa), len(sb)))
    else:
        for n, (x, y) in enumerate(zip(sa, sb)):
            if x != y:
                problems.append("skeleton line %d differs: %r -> %r" % (n + 1, x.strip()[:50], y.strip()[:50]))
    return problems


def main(argv):
    if len(argv) != 2:
        print(__doc__.split("Usage:")[1].strip())
        return 2
    import segment
    with open(argv[1], encoding="utf-8", newline="") as f:
        seg = segment.Segmentation(f.read(), argv[1])
    n = 0
    for b in seg.blocks:
        if b.kind == "mermaid":
            for lab in b.labels:
                n += 1
                print("%d: %s %r" % (lab.start + 1, lab.info, lab.text))
    print("%d label(s)" % n)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
