#!/usr/bin/env python3
"""Masking core (plan R3, R4, R8, I2): typed, numbered placeholders for tokens a translator must not touch.

This is the Phase 1 contract proof. The full line-preserving segmenter (P2-002) builds on it.

Model
  * A file is split on "\\n" into lines. Each line has a kind:
      withheld  front matter, fenced blocks (code, output, Mermaid), whole-line HTML comments.
                Never sent to a translator and never changed (R8).
      prose     everything else. Masked before translation and unmasked after.
  * mask_line() replaces inline code, autolinks, link destinations, bare URLs, HTML tags, comments,
    [[...]] and {{...}} macros, DNT phrases and literal look-alike placeholders with
    typed placeholders such as the code one written CODE_0001 between the brackets.
  * Table rows: unescaped "|" separators also become SEP placeholders, so "\\|" survives (R4).
  * unmask() restores from the mapping in ONE pass over the target text (never recursive), so a
    placeholder-looking string that was in the English source cannot be mistaken for a mask.
  * check_placeholders() is invariant I2: the multiset of placeholders in the target equals the source's.

Usage: python3 -I tools/mask.py FILE.md   (prints OK or the problems; exit 0 = round trip identical)
"""
import os
import re
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DNT_PATH = os.path.join(ROOT, "translation", "dnt.txt")

OPEN, CLOSE = chr(0x27E6), chr(0x27E7)  # mathematical white square brackets
PH_RE = re.compile(OPEN + r"([A-Z]+)_(\d{4})" + CLOSE)
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")
TABLE_RE = re.compile(r"^\s*\|.*\|\s*$")


def load_dnt(path=DNT_PATH):
    """Read the DNT phrases (one per line; no comments; a phrase may start with '#')."""
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [ln.rstrip("\n") for ln in f if ln.strip()]


def build_regex(dnt):
    """Return (compiled regex, [(group name, placeholder type)]). Named groups avoid index bugs."""
    parts = [
        ("LIT", re.escape(OPEN) + r"[^\n]*?" + re.escape(CLOSE), "LIT"),
        ("COMMENT", r"<!--.*?-->", "COMMENT"),
        ("CODE", r"(?<!`)(?P<tick>`+)(?!`).+?(?<!`)(?P=tick)(?!`)", "CODE"),
        ("AUTOLINK", r"<https?://[^>\s]+>", "URL"),
        ("HTML", r"</?[A-Za-z][^>\n]*>", "HTML"),
        ("MACRO", r"\[\[[^\]\n]+\]\]|\{\{[^}\n]+\}\}", "MACRO"),
        ("DEST", r"(?<=\]\()[^)\n]+(?=\))", "DEST"),
        ("BAREURL", r"https?://[^\s)>\]]+", "URL"),
    ]
    if dnt:
        phrases = sorted(set(dnt), key=lambda s: (-len(s), s))
        parts.append(("DNT", "(?<!\\w)(?:" + "|".join(re.escape(p) for p in phrases) + ")(?!\\w)", "DNT"))
    pattern = "|".join("(?P<%s>%s)" % (g, rx) for g, rx, _t in parts)
    return re.compile(pattern, re.S), [(g, t) for g, _rx, t in parts]


class Masker:
    def __init__(self, dnt=None):
        self.dnt = load_dnt() if dnt is None else dnt
        self.rx, self.groups = build_regex(self.dnt)
        self.counter = 0
        self.mapping = {}

    def _new(self, kind, original):
        self.counter += 1
        ph = "%s%s_%04d%s" % (OPEN, kind, self.counter, CLOSE)
        self.mapping[ph] = original
        return ph

    def mask_line(self, line, table=False):
        def repl(m):
            for group, kind in self.groups:
                if m.group(group) is not None:
                    return self._new(kind, m.group(group))
            raise AssertionError("no group matched")  # pragma: no cover
        out = self.rx.sub(repl, line)
        if table:
            out = self._mask_separators(out)
        return out

    def _mask_separators(self, masked):
        # Escaped pipes outside code spans are cell text; unescaped pipes are separators.
        parts, i, buf = [], 0, []
        while i < len(masked):
            c = masked[i]
            if c == "\\" and i + 1 < len(masked) and masked[i + 1] == "|":
                buf.append("\\|")
                i += 2
            elif c == "|":
                buf.append(self._new("SEP", "|"))
                i += 1
            else:
                buf.append(c)
                i += 1
        parts.append("".join(buf))
        return "".join(parts)

    def unmask(self, text):
        """Restore placeholders in one pass. Unknown placeholders are errors, not silently kept."""
        missing = []

        def repl(m):
            if m.group(0) in self.mapping:
                return self.mapping[m.group(0)]
            missing.append(m.group(0))
            return m.group(0)
        out = PH_RE.sub(repl, text)
        if missing:
            raise ValueError("unknown placeholder(s): %s" % ", ".join(sorted(set(missing))))
        return out


def placeholders(text):
    return Counter(m.group(0) for m in PH_RE.finditer(text))


def check_placeholders(source_masked, target):
    """Invariant I2. Return problem strings: dropped, duplicated or invented placeholders."""
    src, tgt = placeholders(source_masked), placeholders(target)
    problems = []
    for ph in sorted(set(src) | set(tgt)):
        if src[ph] > tgt[ph]:
            problems.append("dropped %s (%d -> %d)" % (ph, src[ph], tgt[ph]))
        elif src[ph] < tgt[ph]:
            problems.append("%s %s (%d -> %d)" % ("invented" if src[ph] == 0 else "duplicated", ph, src[ph], tgt[ph]))
    return problems


def classify(text):
    """Return a list of (kind, line) for every line: 'withheld', 'table' or 'prose'."""
    kinds, lines = [], text.split("\n")
    i = 0
    if lines and lines[0] == "---":
        j = 1
        while j < len(lines) and lines[j] != "---":
            j += 1
        if j < len(lines):
            kinds += [("withheld", ln) for ln in lines[:j + 1]]
            i = j + 1
    fence = None
    while i < len(lines):
        ln = lines[i]
        m = FENCE_RE.match(ln)
        if fence is None and m:
            fence = m.group(1)
            kinds.append(("withheld", ln))
        elif fence is not None:
            kinds.append(("withheld", ln))
            if ln.strip().startswith(fence[0] * len(fence)) and ln.strip().strip(fence[0]) == "":
                fence = None
        elif ln.strip().startswith("<!--") and ln.strip().endswith("-->"):
            kinds.append(("withheld", ln))
        elif TABLE_RE.match(ln):
            kinds.append(("table", ln))
        else:
            kinds.append(("prose", ln))
        i += 1
    return kinds


def mask_text(text, dnt=None):
    """Return (list of (kind, original, masked) per line, Masker)."""
    mk = Masker(dnt)
    rows = []
    for kind, ln in classify(text):
        if kind == "withheld":
            rows.append((kind, ln, ln))
        else:
            rows.append((kind, ln, mk.mask_line(ln, table=(kind == "table"))))
    return rows, mk


def translatable_payload(rows):
    """What a translation prompt may see: masked prose and table lines only (R8)."""
    return [m for kind, _o, m in rows if kind != "withheld"]


def reassemble(rows, mk, translate=None):
    """Join the lines back. `translate` maps masked line -> translated masked line (default identity)."""
    out = []
    for kind, orig, masked in rows:
        if kind == "withheld":
            out.append(orig)
            continue
        tgt = masked if translate is None else translate(masked)
        problems = check_placeholders(masked, tgt)
        if problems:
            raise ValueError("I2 failed for %r: %s" % (orig[:50], "; ".join(problems)))
        out.append(mk.unmask(tgt))
    return "\n".join(out)


def roundtrip(text, dnt=None):
    rows, mk = mask_text(text, dnt)
    return reassemble(rows, mk)


def main(argv):
    if len(argv) != 2:
        print("usage: mask.py FILE.md")
        return 2
    with open(argv[1], encoding="utf-8", newline="") as f:
        text = f.read()
    try:
        back = roundtrip(text)
    except ValueError as e:
        print("FAIL " + str(e))
        return 1
    if back != text:
        print("FAIL round trip changed %s" % argv[1])
        return 1
    print("OK masked round trip identical: %s" % argv[1])
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
