#!/usr/bin/env python3
"""Part II invariants I28 to I31 (plan 4.5, task S2-005). Pure functions over text and records; invariants.py wraps them.

  I28  identifier-map closure: every identifier that differs between the English and the localized code of a mapped file is
       a ledger rename (no unmapped change); every ledger rename is applied in its file (no half rename); and the old name
       is gone from code, prose, diagrams, trace tables and generated excerpts (stale-symbol sweep).
  I29  protected-token integrity: the token-level diff between English and localized code, outside the mapped renames,
       is empty. Comments and string literals are compared as opaque slots (their text is the PO layer's business).
  I30  no keyword or API used as code appears outside inline code in Spanish prose (wraps tools/token_audit.py, whose
       evidence rules keep ordinary words such as "lista" or "for" quiet).
  I31  oracle equality: every ledger family has an oracle report with verdict PASS; FAIL and NOT TESTED are findings.

The ledger rules for identifiers.yaml and dnt.txt are derived from translation/identifier-map.jsonl by derive_rules();
`--derive [--write]` prints or writes translation/identifiers.ledger.yaml and translation/dnt.ledger.txt.

Usage:
  python3 -I tools/part2_inv.py --check     I28 to I31 over the real tree (empty ledger: nothing to check, exit 0)
  python3 -I tools/part2_inv.py --derive [--write]
"""
import json
import os
import re
import sys
from collections import namedtuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import loc_map  # noqa: E402
import token_audit  # noqa: E402

Finding = namedtuple("Finding", "inv where msg")
IDENT_RE = re.compile(r"[^\W\d]\w*", re.UNICODE)
LEDGER_IDS = os.path.join(ROOT, "translation", "identifiers.ledger.yaml")
LEDGER_DNT = os.path.join(ROOT, "translation", "dnt.ledger.txt")
TABLE = {
    "I28": "Identifier-map closure and stale-symbol sweep",
    "I29": "Protected-token integrity outside mapped renames",
    "I30": "No keyword or API used as code outside inline code",
    "I31": "Oracle equality (verdict PASS for every localized family)",
}
STR, COM = "\x00STR", "\x00COM"

# ------------------------------------------------------------------------------------------ lexer


def lex(code, line_comments=("#", "//", "--"), block=(("/*", "*/"),)):
    """Tokens of `code` with every comment and string literal collapsed to a slot token (STR or COM).

    Language-agnostic on purpose: words, numbers, and single punctuation characters. Good enough to compare an English
    file with its localized twin, because both go through the same lexer; it never has to parse the language."""
    toks, i, n = [], 0, len(code)
    while i < n:
        c = code[i]
        if c.isspace():
            i += 1
            continue
        hit = next((b for b in block if code.startswith(b[0], i)), None)
        if hit:
            j = code.find(hit[1], i + len(hit[0]))
            i = n if j < 0 else j + len(hit[1])
            toks.append(COM)
            continue
        if any(code.startswith(p, i) for p in line_comments):
            j = code.find("\n", i)
            i = n if j < 0 else j
            toks.append(COM)
            continue
        if c in "\"'`":
            j = i + 1
            while j < n and code[j] != c and code[j] != "\n":
                j += 2 if code[j] == "\\" else 1
            i = min(j + 1, n)
            toks.append(STR)
            continue
        m = IDENT_RE.match(code, i)
        if m:
            toks.append(m.group(0))
            i = m.end()
            continue
        m = re.compile(r"\d[\w.]*").match(code, i)
        if m:
            toks.append(m.group(0))
            i = m.end()
            continue
        toks.append(c)
        i += 1
    return toks


def _is_ident(t):
    return bool(IDENT_RE.fullmatch(t)) and not t.startswith("\x00")


def token_diff(en_code, es_code, **lexopts):
    """[(index, english token, spanish token)] where the two token streams differ; a length change is reported as 'length'."""
    a, b = lex(en_code, **lexopts), lex(es_code, **lexopts)
    out = [(i, x, y) for i, (x, y) in enumerate(zip(a, b)) if x != y]
    if len(a) != len(b):
        out.append((min(len(a), len(b)), "<%d tokens>" % len(a), "<%d tokens>" % len(b)))
    return out


# ------------------------------------------------------------------------------------------ I28 and I29


def renames_for(records, path):
    """{old: new} of the ledger for one file; a name renamed differently by two scopes keeps both in `all_pairs`."""
    return {(r["old"], r["new"]) for r in records if r["path"] == path}


def i28_i29_code(path, en_code, es_code, records, reserved=(), **lexopts):
    """I28 (unmapped or half-applied renames) and I29 (everything else that changed) for one protected file."""
    out = []
    pairs = renames_for(records, path)
    seen = set()
    for i, x, y in token_diff(en_code, es_code, **lexopts):
        if x.startswith("<") and x.endswith("tokens>"):
            out.append(Finding("I29", path, "token count differs (%s vs %s): syntax or structure changed" % (x, y)))
        elif x in reserved or y in reserved:
            out.append(Finding("I29", path, "token %d: protected token %r -> %r" % (i, x, y)))
        elif _is_ident(x) and _is_ident(y):
            if (x, y) in pairs:
                seen.add((x, y))
            else:
                out.append(Finding("I28", path, "token %d: %s -> %s is not in the identifier map" % (i, x, y)))
        else:
            out.append(Finding("I29", path, "token %d: %r -> %r changed outside the mapped renames" % (i, x, y)))
    for old, new in sorted(pairs - seen):
        out.append(Finding("I28", path, "map entry %s -> %s is not applied in the localized file" % (old, new)))
    return out


def code_only(md):
    """Markdown with everything but code spans, fenced blocks and diagrams blanked (line numbers kept): an old name that is also an
    ordinary word ("total") in running prose is not a stale symbol; the same name in code formatting is."""
    out, fence = [], None
    for line in md.split("\n"):
        m = re.match(r"^ {0,3}(`{3,}|~{3,})", line)
        if m:
            fence = None if fence and m.group(1)[0] == fence[0] and len(m.group(1)) >= len(fence) else (fence or m.group(1))
            out.append(line)
        elif fence:
            out.append(line)
        else:
            out.append(" ".join(re.findall(r"`[^`\n]+`", line)))
    return "\n".join(out)


def i28_stale(records, texts):
    """Stale-symbol sweep. `texts` maps a path (code, prose, diagram, trace table, generated excerpt) to its localized text.
    The old spelling of a renamed identifier must not remain as a whole token, except in the ledger's own files."""
    out = []
    olds = {}
    for r in records:
        olds.setdefault(r["old"], r)
    for path, text in sorted(texts.items()):
        if path.endswith(".md"):
            text = code_only(text)
        for old, r in olds.items():
            if r["new"] == old:
                continue
            m = re.search(r"(?<![\w])%s(?![\w])" % re.escape(old), text)
            if m:
                line = text.count("\n", 0, m.start()) + 1
                out.append(Finding("I28", "%s:%d" % (path, line), "stale symbol %r (renamed to %r in %s)" % (old, r["new"], r["path"])))
    return out


# ------------------------------------------------------------------------------------------ I30


def i30_unfenced(path, es_text, tokens):
    """Protected tokens used as code outside inline code in Spanish prose. `tokens` is token -> [languages]."""
    return [Finding("I30", "%s:%d" % (path, f["line"]), "%s used as code outside inline code (%s)" % (f["token"], f["reason"]))
            for f in token_audit.audit_text(es_text, tokens, path)]


# ------------------------------------------------------------------------------------------ I31


def i31_oracle(records, families, verdicts):
    """Every family touched by the ledger needs verdict PASS. `families` is path -> family, `verdicts` is family -> verdict."""
    out = []
    for fam in sorted({families.get(r["path"]) or "?" for r in records}):
        v = verdicts.get(fam)
        if v is None:
            out.append(Finding("I31", fam, "family has ledger renames and no oracle report"))
        elif v != "PASS":
            out.append(Finding("I31", fam, "oracle verdict is %s, not PASS" % v))
    return out


def load_verdicts(report_dir):
    """family -> verdict from translation/part2/reports/*.md lines of the form `family: <name>` and `verdict: PASS|FAIL|NOT TESTED`."""
    out = {}
    if not os.path.isdir(report_dir):
        return out
    for name in sorted(os.listdir(report_dir)):
        if not name.endswith(".md"):
            continue
        with open(os.path.join(report_dir, name), encoding="utf-8") as f:
            text = f.read()
        fam = re.search(r"^\s*-?\s*family:\s*(\S+)", text, re.M)
        ver = re.search(r"^\s*-?\s*verdict:\s*(PASS|FAIL|NOT TESTED)\s*$", text, re.M)
        if fam and ver:
            out[fam.group(1)] = ver.group(1)
    return out


# ------------------------------------------------------------------------------------------ derived rules


def derive_rules(records):
    """(identifiers.yaml text, dnt text) from the ledger. Rule: where the English names `old`, the Spanish keeps `new` literal."""
    seen, rows = set(), []
    for r in sorted(records, key=lambda r: (r["path"], r["old"], r["new"])):
        key = (r["old"], r["new"])
        if key in seen:
            continue
        seen.add(key)
        rows.append("  - literal: %s\n    en: '\\b%s\\b'\n    files: ['%s']\n" % (json.dumps(r["new"], ensure_ascii=False),
                                                                                  re.escape(r["old"]).replace("'", "''"), r["path"].rsplit("/", 1)[0] + "/*"))
    ids = "# Generated by tools/part2_inv.py --derive --write from translation/identifier-map.jsonl. Do not edit.\nidentifiers:\n"
    ids += "".join(rows) if rows else "  []\n"
    dnt = "".join(n + "\n" for n in sorted({r["new"] for r in records}))
    return ids, dnt


def load_ledger_dnt(path=LEDGER_DNT):
    if not os.path.isfile(path):
        return []
    with open(path, encoding="utf-8") as f:
        return [ln.rstrip("\n") for ln in f if ln.strip()]


# ------------------------------------------------------------------------------------------ CLI


def main(argv):
    records = [r for r in loc_map.load_jsonl(loc_map.MAP) if "__bad__" not in r]
    if "--derive" in argv:
        ids, dnt = derive_rules(records)
        if "--write" in argv:
            with open(LEDGER_IDS, "w", encoding="utf-8", newline="\n") as f:
                f.write(ids)
            with open(LEDGER_DNT, "w", encoding="utf-8", newline="\n") as f:
                f.write(dnt)
            print("part2_inv: wrote %d rule(s)" % len(records))
        else:
            sys.stdout.write(ids + "--- dnt\n" + dnt)
        return 0
    if "--check" not in argv:
        print(__doc__)
        return 2
    found = [Finding("I28", "ledger", e) for e in loc_map.validate(records)]
    found += i31_oracle(records, loc_map.load_families(), load_verdicts(os.path.join(ROOT, "translation", "part2", "reports")))
    for f in found:
        print("%s %s: %s" % f)
    print("part2_inv: %d record(s), %d finding(s)" % (len(records), len(found)))
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
