#!/usr/bin/env python3
"""Unfenced-token audit (Part II, task S1-006).

Finds protected language tokens (from translation/protected-tokens/tokens.jsonl, plus a small
lexical SQL list) that sit in Markdown prose without code formatting. It only REPORTS; it never
edits and never wraps. Output: translation/reports/unfenced-tokens.jsonl, one row per finding.

A finding needs code-shaped evidence, so ordinary words stay quiet:
  * a registry token directly followed by `(`, `()`, `[`, `<` or `.name`, or preceded by `.name.`
    (List<String>, print(x), os.path), or
  * a token containing `_` or a digit, or a mixed-case registry token longer than one capital
    (for example `isinstance`-style API names are lower case, so they need the first rule), or
  * two or more distinct SQL keywords in one line (SELECT name FROM users).
Never flagged: text inside fenced blocks, inline code, link targets, URLs, HTML comments, table
rows (a table is reported only if a cell has the evidence above, still by line, never wrapped),
macros `[[...]]` and `{{...}}`, front matter, and plain words in quotes.
An ordinary Spanish or English word that is also a token (lista, list, return, for) is quiet unless
the evidence above is present.

Usage:
  python3 -I tools/token_audit.py [--write] [paths...]   default: all authored Markdown
"""
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
REGISTRY = os.path.join(ROOT, "translation", "protected-tokens", "tokens.jsonl")
OUT = os.path.join(ROOT, "translation", "reports", "unfenced-tokens.jsonl")

SQL_WORDS = {"SELECT", "FROM", "WHERE", "INSERT", "INTO", "VALUES", "UPDATE", "DELETE", "JOIN",
             "GROUP", "ORDER", "HAVING", "CREATE", "TABLE", "DROP", "LIMIT", "UNION"}

WORD = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
FENCE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
INLINE_CODE = re.compile(r"(`+)(?:(?!\1).)+?\1")
LINK_TARGET = re.compile(r"\]\([^)]*\)")
URL = re.compile(r"https?://\S+|<https?://[^>]+>")
MACRO = re.compile(r"\[\[[^\]]*\]\]|\{\{[^}]*\}\}")
HTML_COMMENT = re.compile(r"<!--.*?-->")
QUOTED_PLAIN = re.compile(r"\"[A-Za-z]+\"|“[A-Za-z]+”|'[A-Za-z]+'(?!\w)")


def load_registry(path=REGISTRY):
    """token -> sorted list of languages. Skips not-extracted records."""
    tokens = {}
    if not os.path.exists(path):
        return tokens
    with open(path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            r = json.loads(line)
            for t in r.get("tokens", []):
                name = t["token"] if isinstance(t, dict) else t
                tokens.setdefault(name, set()).add(r["language"])
    return {k: sorted(v) for k, v in tokens.items()}


def blank(text, pattern):
    """Replace every match with spaces of equal length so columns stay valid."""
    return pattern.sub(lambda m: " " * len(m.group(0)), text)


def prose_lines(text):
    """Yield (line_number, masked_line) for prose lines only."""
    in_fence = None
    in_comment = False
    lines = text.split("\n")
    i = 0
    if lines and lines[0].strip() == "---":  # front matter
        i = 1
        while i < len(lines) and lines[i].strip() != "---":
            i += 1
        i += 1
    for n in range(i, len(lines)):
        line = lines[n]
        m = FENCE.match(line)
        if in_fence:
            if m and m.group(1)[0] == in_fence[0] and len(m.group(1)) >= len(in_fence):
                in_fence = None
            continue
        if m:
            in_fence = m.group(1)
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        if "<!--" in line and "-->" not in line:
            in_comment = True
            continue
        if line.startswith("    ") and not line.strip().startswith(("-", "*", "+")) and not re.match(r"\s*\d+[.)]", line):
            continue  # indented code block
        for pat in (HTML_COMMENT, INLINE_CODE, LINK_TARGET, URL, MACRO, QUOTED_PLAIN):
            line = blank(line, pat)
        yield n + 1, line


def evidence(line, m, name):
    """Return a reason string if the occurrence at m looks like code, else ''."""
    after = line[m.end():m.end() + 2]
    before = line[max(0, m.start() - 1):m.start()]
    if after[:1] in ("(", "[", "<") and after[:2] not in ("< ",):
        return "call-or-type-shape"
    if re.match(r"\.[A-Za-z_]", after):
        return "member-access"
    if before == "." and m.start() >= 2 and re.match(r"[A-Za-z0-9_)\]]", line[m.start() - 2]):
        return "member-access"
    if "_" in name or any(c.isdigit() for c in name):
        return "identifier-shape"
    return ""


def audit_text(text, tokens, path=""):
    findings = []
    for ln, line in prose_lines(text):
        sql_hits = {}
        for m in WORD.finditer(line):
            w = m.group(0)
            if w in SQL_WORDS:
                sql_hits.setdefault(w, m)
        if len(sql_hits) >= 2:
            for w, m in sql_hits.items():
                findings.append({"path": path, "line": ln, "col": m.start() + 1, "token": w,
                                 "languages": ["sql"], "reason": "sql-keywords-together"})
        for m in WORD.finditer(line):
            w = m.group(0)
            if w not in tokens or w in sql_hits and len(sql_hits) >= 2:
                continue
            why = evidence(line, m, w)
            if why:
                findings.append({"path": path, "line": ln, "col": m.start() + 1, "token": w,
                                 "languages": tokens[w], "reason": why})
    findings.sort(key=lambda f: (f["path"], f["line"], f["col"]))
    return findings


def render(findings):
    return "".join(json.dumps(f, sort_keys=True, ensure_ascii=False, separators=(",", ":")) + "\n" for f in findings)


def md_files():
    sys.path.insert(0, HERE)
    import segment
    return [p for p in segment.authored_files() if p.endswith(".md")]


def main(argv):
    write = "--write" in argv
    paths = [a for a in argv if not a.startswith("--")] or md_files()
    tokens = load_registry()
    findings = []
    for p in paths:
        full = p if os.path.isabs(p) else os.path.join(ROOT, p)
        if not os.path.isfile(full):
            continue
        with open(full, encoding="utf-8") as f:
            findings += audit_text(f.read(), tokens, os.path.relpath(full, ROOT))
    out = render(findings)
    if write:
        os.makedirs(os.path.dirname(OUT), exist_ok=True)
        with open(OUT, "w", encoding="utf-8") as f:
            f.write(out)
    print("token_audit: %d finding(s) in %d file(s)%s" % (len(findings), len(paths), " (written)" if write else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
