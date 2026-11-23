#!/usr/bin/env python3
"""Scoped, line-preserving, fail-closed editor for protected files (Part II, plan 4.5.3, task S2-002).

The only sanctioned way to change a protected (locked) file. Edits come from three sources and
nothing else:
  * comments   : PO entries in translation/po/code/<path>.po, msgctxt "L<line>", msgid = the exact
                 English comment span (marker included), msgstr = the Spanish span (marker included);
  * strings    : PO entries with msgctxt "S<line>", msgid = exact string body; only strings the
                 inventory classes as display-candidate may change, and format placeholders must match;
  * identifiers: records of translation/identifier-map.jsonl for that path (validated by loc_map).
Every edit is a span (start, end, replacement) applied to the original text, so bytes outside
mapped spans are untouched by construction. Then the result is re-checked:
  1. the family is `localizing` and not `never`, and the path is in the inventory (else refuse);
  2. every comment/string replacement must scan as exactly one comment/string of its own kind
     (no early terminator, no injected code);
  3. the new text must scan to the same sequence of span kinds as the old one;
  4. line count may not change unless translation/line-anchors.jsonl has a record
     {"path", "old_lines", "new_lines"} for it (COBOL columns, APL layout, Make tabs);
  5. a renamed identifier may not be a protected token or built-in (old or new), the new name may not
     already occur in the file as code, and every record must match at least one occurrence;
  6. Python results must still parse.
Re-running on an already applied file is a no-op (an entry whose span already holds the msgstr is skipped).

Usage:
  python3 -I tools/loc_apply.py PATH [--write]      # dry run by default; prints what would change
"""
from __future__ import annotations

import ast
import io
import json
import os
import re
import sys
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import code_inventory as ci  # noqa: E402
import loc_map as lm  # noqa: E402
import categories as cat  # noqa: E402

PO_DIR = os.path.join("translation", "po", "code")
ANCHORS = os.path.join("translation", "line-anchors.jsonl")
PLACEHOLDER = re.compile(r"%[-+ #0]*\d*(?:\.\d+)?[sdifxXeEgGrc%]|\{[^{}]*\}|\$\{?\w+\}?|\\[nrt]")


class Refused(Exception):
    """A change was refused; nothing is written."""


# ---------------------------------------------------------------------------
# PO reader (msgctxt / msgid / msgstr, quoted, continued lines)
# ---------------------------------------------------------------------------

def _unq(s: str) -> str:
    s = s.strip()
    if len(s) < 2 or s[0] != '"' or s[-1] != '"':
        raise Refused("bad PO string: %r" % s)
    out, i, body = [], 0, s[1:-1]
    while i < len(body):
        c = body[i]
        if c == "\\" and i + 1 < len(body):
            nxt = body[i + 1]
            out.append({"n": "\n", "t": "\t", "r": "\r", '"': '"', "\\": "\\"}.get(nxt, "\\" + nxt))
            i += 2
        else:
            out.append(c)
            i += 1
    return "".join(out)


def parse_po(text: str) -> list[dict]:
    entries, cur, key = [], {}, None
    for raw in text.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            if not line and cur.get("msgid") is not None and "msgstr" in cur:
                entries.append(cur)
                cur, key = {}, None
            continue
        m = re.match(r"(msgctxt|msgid|msgstr)\s+(\".*)$", line)
        if m:
            key = m.group(1)
            if key == "msgctxt" and "msgstr" in cur:
                entries.append(cur)
                cur = {}
            cur[key] = _unq(m.group(2))
        elif line.startswith('"') and key:
            cur[key] += _unq(line)
        else:
            raise Refused("unreadable PO line: %r" % raw)
    if cur.get("msgid") is not None and "msgstr" in cur:
        entries.append(cur)
    out = []
    for e in entries:
        if e.get("msgid") == "":
            continue  # header
        ctx = e.get("msgctxt", "")
        m = re.fullmatch(r"([LSC])(\d+)", ctx)
        if not m:
            raise Refused("PO entry needs msgctxt L<line>, S<line> or C<line>, got %r" % ctx)
        out.append({"kind": m.group(1), "line": int(m.group(2)), "msgid": e["msgid"], "msgstr": e["msgstr"]})
    return out


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def kinds(text: str, spec: dict) -> list[str]:
    return [s[0] for s in ci.scan(text, spec) if s[0] in ("comment", "string", "char", "heredoc")]


def check_standalone(kind: str, new: str, spec: dict) -> None:
    spans = [s for s in ci.scan(new, spec) if s[0] != "code_flush"]
    if len(spans) != 1 or spans[0][0] != kind or spans[0][1] != 0 or spans[0][2] != len(new):
        raise Refused("replacement is not exactly one %s span (terminator or code smuggled in): %r"
                      % (kind, new[:60]))


def load_anchors(root: str) -> list[dict]:
    return lm.load_jsonl(os.path.join(root, ANCHORS))


def identifier_spans(text: str, lang: str, rec: dict, spec: dict) -> list[tuple[int, int]]:
    """Offsets of code occurrences of rec['old'] inside rec['scope']."""
    old, scope = rec["old"], rec["scope"]
    fold = lang in lm.CASE_INSENSITIVE
    starts = ci.line_starts(text)
    spans: list[tuple[int, int]] = []
    if lang == "python":
        lo, hi = 1, 10 ** 9
        if scope not in ("file", "module"):
            kind, _, name = scope.partition(":")
            if kind not in ("function", "class"):
                raise Refused("python scope %r not supported" % scope)
            tree = ast.parse(text)
            nodes = [n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
                     and n.name == name]
            if len(nodes) != 1:
                raise Refused("scope %r matches %d definitions" % (scope, len(nodes)))
            lo, hi = nodes[0].lineno, nodes[0].end_lineno
        prev = None
        for tok in tokenize.generate_tokens(io.StringIO(text).readline):
            if tok.type == tokenize.NAME and tok.string == old and lo <= tok.start[0] <= hi:
                dotted = prev is not None and prev.string == "." and prev.type == tokenize.OP
                if not dotted or rec["role"] == "field":
                    a = starts[tok.start[0] - 1] + tok.start[1]
                    spans.append((a, a + len(old)))
            if tok.type not in (tokenize.NL, tokenize.COMMENT):
                prev = tok
        return spans
    if scope not in ("file", "module"):
        raise Refused("scope %r needs a language-aware parser; %s is lexical (file/module only)" % (scope, lang))
    mask = bytearray(len(text))
    for s in ci.scan(text, spec):
        if s[0] != "code_flush":
            for k in range(s[1], min(s[2], len(text))):
                mask[k] = 1
    rx = ci.IDENT_HYPHEN if lang in ("cobol", "lisp", "forth") else ci.IDENT
    for m in rx.finditer(text):
        if mask[m.start()]:
            continue
        same = m.group(0).casefold() == old.casefold() if fold else m.group(0) == old
        if same:
            spans.append((m.start(), m.end()))
    return spans


def code_names(text: str, lang: str, spec: dict) -> set[str]:
    mask = bytearray(len(text))
    for s in ci.scan(text, spec):
        if s[0] != "code_flush":
            for k in range(s[1], min(s[2], len(text))):
                mask[k] = 1
    rx = ci.IDENT_HYPHEN if lang in ("cobol", "lisp", "forth") else ci.IDENT
    names = {m.group(0) for m in rx.finditer(text) if not mask[m.start()]}
    return {n.casefold() for n in names} if lang in lm.CASE_INSENSITIVE else names


# ---------------------------------------------------------------------------
# core
# ---------------------------------------------------------------------------

PIC_WIDTH = re.compile(r"(?i)(PIC(?:TURE)?\s+X\()\d+(\))")


# Decision 11 follow-up (G1-001): the one regex edit a C entry may make. An ASCII letter class
# `A-Za-z` (inside brackets) may gain exactly the accented letters of the four Spanish category words,
# directly after `z`, so a check or regex that reads a category still matches "Programación".
ACCENT_EXT = "ÁÉÍÓÚáéíóúñ"
ASCII_CLASS = re.compile(r"\[[^\]\[\n]*A-Za-z(?!" + ACCENT_EXT + r")[^\]\[\n]*\]")
WIDE_SEQ = "A-Za-z" + ACCENT_EXT


def _category_norm(line: str) -> str:
    """Line with every card-category word (either form), every PIC X(n) width and every widened
    letter class abstracted."""
    return PIC_WIDTH.sub(r"\1#\2", cat.WORD_RE.sub("<CAT>", line.replace(WIDE_SEQ, "A-Za-z")))


def _split_comment(line: str, lang: str):
    """(code part, trailing comment or None) of one line, cut at the first comment span."""
    spec = ci.SPECS.get(lang, ci.SPECS["data"])
    for s in ci.scan(line, spec):
        if s[0] == "comment":
            return line[:s[1]], line[s[1]:s[2]]
    return line, None


def _category_edit(text: str, rel: str, starts: list[int], e: dict, lang: str = "data"):
    """Whole-line edit for decision 11 (C<line> entries): the only differences allowed between the
    English line and the Spanish line are the four category words, mapped one to one, and the
    numeric width inside a PIC X(n) clause. Returns an edit tuple, or None when already applied."""
    ln = e["line"]
    if ln < 1 or ln > len(starts):
        raise Refused("%s line %d: no such line" % (rel, ln))
    a = starts[ln - 1]
    b = text.find("\n", a)
    b = len(text) if b < 0 else b
    cr = "\r" if text[a:b].endswith("\r") else ""
    if cr:
        b -= 1
    cur = text[a:b]
    if cur == e["msgstr"] and cur != e["msgid"]:
        return None
    if cur != e["msgid"]:
        raise Refused("%s line %d: msgid does not match the file line %r" % (rel, ln, cur[:60]))
    old, new = e["msgid"], e["msgstr"]
    oc, nc = _split_comment(old, lang)[1], _split_comment(new, lang)[1]
    # only a comment that ends the line is a trailing comment; a mid-line one (Forth "( -- c-addr u )"
    # followed by code) stays part of the compared line and may not change
    if oc is not None and not old.endswith(oc):
        oc = None
    # sed: a `#` inside an s/// command (a tally class such as `(#+)`) is regex text, not a comment; compare the whole line
    if lang == "sed" and re.match(r"\s*s[^#\s\w\\]", old):
        oc = nc = None
    if nc is not None and not new.endswith(nc):
        nc = None
    if oc is not None or nc is not None:
        # a trailing comment may be translated in the same entry (it must still be one comment)
        if oc is None or nc is None:
            raise Refused("%s line %d: a C entry may not add or drop a trailing comment" % (rel, ln))
        check_standalone("comment", nc, ci.SPECS.get(lang, ci.SPECS["data"]))
        old, new = old[:len(old) - len(oc)], new[:len(new) - len(nc)]
    if _category_norm(old) != _category_norm(new):
        raise Refused("%s line %d: a C entry may change only the category words, PIC X(n) widths and A-Za-z letter classes" % (rel, ln))
    olds = [m.group(1) for m in cat.WORD_RE.finditer(old)]
    news = [m.group(1) for m in cat.WORD_RE.finditer(new)]
    widened = new.count(WIDE_SEQ)
    if WIDE_SEQ in old:
        raise Refused("%s line %d: the English line already holds a widened letter class; a C entry may only widen"
                      % (rel, ln))
    if widened and (not ASCII_CLASS.search(old) or old.count("A-Za-z") != widened):
        raise Refused("%s line %d: every letter class widened must be an ASCII A-Za-z class of the English line"
                      % (rel, ln))
    if not olds and not PIC_WIDTH.search(old) and not widened:
        raise Refused("%s line %d: a C entry needs a card-category word, a PIC X(n) clause or an A-Za-z letter "
                      "class in the English line" % (rel, ln))
    if [cat.EN_TO_ES.get(w, w) for w in olds] != news:
        raise Refused("%s line %d: category words must map one to one to the approved Spanish forms" % (rel, ln))
    if "\n" in new or "\r" in new:
        raise Refused("%s line %d: a C entry is one line" % (rel, ln))
    return (a, b, e["msgstr"], "cat")


def plan_edits(text: str, rel: str, lang: str, po: list[dict], idrecs: list[dict], reg: dict) -> list[tuple]:
    spec = ci.SPECS.get(lang, ci.SPECS["data"])
    spans = [s for s in ci.scan(text, spec) if s[0] != "code_flush"]
    starts = ci.line_starts(text)
    edits: list[tuple[int, int, str, str]] = []
    for e in po:
        if e["kind"] == "C":
            edit = _category_edit(text, rel, starts, e, lang)
            if edit:
                edits.append(edit)
            continue
        want = "comment" if e["kind"] == "L" else "string"
        hits = [s for s in spans if s[0] == want and ci.line_of(starts, s[1]) == e["line"]]
        if e["kind"] == "S":
            hits = [(s[0], s[1] + len(_open(text, s, spec)), s[2] - len(_close(text, s, spec))) for s in hits]
        if len(hits) != 1:
            raise Refused("%s line %d: %d %s span(s) start there (need exactly one)" % (rel, e["line"], len(hits), want))
        a, b = hits[0][1], hits[0][2]
        cur = text[a:b]
        cr = "\r" if cur.endswith("\r") else ""
        cur_cmp = cur[:-1] if cr else cur
        if cur_cmp == e["msgstr"] and cur_cmp != e["msgid"]:
            continue  # already applied
        if cur_cmp != e["msgid"]:
            raise Refused("%s line %d: msgid does not match the file text %r" % (rel, e["line"], cur_cmp[:60]))
        new = e["msgstr"]
        if not new.strip():
            raise Refused("%s line %d: empty msgstr" % (rel, e["line"]))
        if want == "comment":
            check_standalone("comment", new, spec)
        else:
            if ci.classify_string(cur_cmp, lang) != "display-candidate":
                raise Refused("%s line %d: string is class %s, only display-candidate strings may change"
                              % (rel, e["line"], ci.classify_string(cur_cmp, lang)))
            if sorted(PLACEHOLDER.findall(cur_cmp)) != sorted(PLACEHOLDER.findall(new)):
                raise Refused("%s line %d: format placeholders differ between msgid and msgstr" % (rel, e["line"]))
            sp = [s for s in spans if s[0] == "string" and ci.line_of(starts, s[1]) == e["line"]][0]
            o, c = _open(text, sp, spec), _close(text, sp, spec)
            check_standalone("string", o + new + c, spec)
        edits.append((a, b, new + cr, "po"))
    for r in idrecs:
        occ = identifier_spans(text, lang, r, spec)
        if not occ:
            if r["new"] in code_names(text, lang, spec):
                continue  # already applied
            raise Refused("%s: no occurrence of %r in scope %s" % (rel, r["old"], r["scope"]))
        if r["new"] in code_names(text, lang, spec) or (lang in lm.CASE_INSENSITIVE and r["new"].casefold() in code_names(text, lang, spec)):
            raise Refused("%s: new name %r already occurs in the file" % (rel, r["new"]))
        for a, b in occ:
            edits.append((a, b, r["new"], "id"))
    edits.sort()
    for x, y in zip(edits, edits[1:]):
        if x[1] > y[0]:
            raise Refused("%s: two mapped edits overlap at offset %d" % (rel, y[0]))
    return edits


def _open(text, sp, spec):
    raw = text[sp[1]:sp[2]]
    for o, cl, _e, _m in sorted(spec.get("strings", []), key=lambda s: -len(s[0])):
        if raw.startswith(o):
            return o
    return ""


def _close(text, sp, spec):
    raw = text[sp[1]:sp[2]]
    for o, cl, _e, _m in sorted(spec.get("strings", []), key=lambda s: -len(s[0])):
        if raw.startswith(o):
            return cl if raw.endswith(cl) and len(raw) >= len(o) + len(cl) else ""
    return ""


def apply_file(root: str, rel: str, scope=None, families=None, reg=None, records=None, po=None,
               anchors=None) -> tuple[str, str]:
    """Return (old_text, new_text) for `rel`, or raise Refused."""
    scope = lm.load_scope(os.path.join(root, "translation", "localization-scope.yaml")) if scope is None else scope
    families = lm.load_families(os.path.join(root, "translation", "part2", "code-inventory.jsonl")) \
        if families is None else families
    reg = lm.load_tokens(os.path.join(root, "translation", "protected-tokens", "tokens.jsonl")) if reg is None else reg
    fam = families.get(rel)
    if fam is None:
        raise Refused("%s is not a protected file in the inventory" % rel)
    row = scope.get(fam)
    if row is None or row["never"]:
        raise Refused("family %s of %s is never localizable (or not in the scope file)" % (fam, rel))
    if row["status"] != "localizing":
        raise Refused("family %s of %s is frozen in the scope file" % (fam, rel))
    path = os.path.join(root, rel)
    with open(path, "rb") as fh:
        data = fh.read()
    if ci.is_binary(rel, data):
        raise Refused("%s is binary; binary files never localize" % rel)
    text = data.decode("utf-8")
    lang = ci.detect_lang(rel, data[:200])
    if po is None:
        pp = os.path.join(root, PO_DIR, rel + ".po")
        po = parse_po(open(pp, encoding="utf-8").read()) if os.path.exists(pp) else []
    if records is None:
        records = lm.load_jsonl(os.path.join(root, "translation", "identifier-map.jsonl"))
    mine = [r for r in records if r.get("path") == rel]
    if mine:
        errs = lm.validate(mine, scope, families, reg)
        if errs:
            raise Refused("identifier map invalid: " + "; ".join(errs))
        fold = lang in lm.CASE_INSENSITIVE
        names = lm.reserved_names(lang, reg)
        pool = {n.casefold() for n in names} if fold else names
        for r in mine:
            if (r["old"].casefold() if fold else r["old"]) in pool:
                raise Refused("%s: %r is a protected token or built-in of %s and cannot be renamed" % (rel, r["old"], lang))
    if not po and not mine:
        raise Refused("%s: no PO entries and no identifier-map records; nothing is mapped" % rel)
    edits = plan_edits(text, rel, lang, po, mine, reg)
    new = text
    for a, b, rep, _k in reversed(edits):
        new = new[:a] + rep + new[b:]
    spec = ci.SPECS.get(lang, ci.SPECS["data"])
    if kinds(text, spec) != kinds(new, spec):
        raise Refused("%s: span structure (comments/strings) changed; refusing" % rel)
    old_n, new_n = text.count("\n"), new.count("\n")
    if old_n != new_n:
        anchors = load_anchors(root) if anchors is None else anchors
        if not any(a.get("path") == rel and a.get("old_lines") == old_n and a.get("new_lines") == new_n
                   for a in anchors):
            raise Refused("%s: change moves line count %d -> %d and line-anchors.jsonl has no matching record"
                          % (rel, old_n, new_n))
    if lang == "python":
        try:
            ast.parse(new)
        except SyntaxError as exc:
            raise Refused("%s: result does not parse: %s" % (rel, exc))
    return text, new


def main(argv: list[str]) -> int:
    args = [a for a in argv if not a.startswith("--")]
    if len(args) != 1:
        print(__doc__)
        return 2
    rel = args[0].replace(os.sep, "/")
    try:
        old, new = apply_file(ROOT, rel)
    except Refused as exc:
        print("loc_apply: REFUSED: %s" % exc)
        return 1
    if old == new:
        print("loc_apply: %s unchanged" % rel)
        return 0
    if "--write" in argv:
        with open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="") as fh:
            fh.write(new)
        print("loc_apply: wrote %s" % rel)
    else:
        print("loc_apply: %s would change (%d -> %d bytes); use --write" % (rel, len(old), len(new)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
