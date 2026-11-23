#!/usr/bin/env python3
"""Part II (plan 4.5.1): inventory every protected (locked) file.

For each path in translation/locked-code.sha256 the tool writes ONE record to
translation/part2/code-inventory.jsonl: host language, parser kind, embedded languages
(heredocs, SQL strings, regex families, HTML script blocks), comments, string literals
(with a provisional class), and identifiers with a provisional role.

Parser-backed: Python (tokenize + ast). Everything else uses a lexical scanner driven by a
small per-language spec. The inventory only *describes*; it never decides what to localize
(the protected-token registries and the scope file do that in later tasks). Roles are
therefore provisional: keyword lists for non-Python languages are small hints, not registries.

Usage:
  python3 -I tools/code_inventory.py --write    # regenerate the JSONL and the summary
  python3 -I tools/code_inventory.py --check    # coverage and freshness (exit 1 on problems)
  python3 -I tools/code_inventory.py FILE...    # print records for given files (no write)
"""
from __future__ import annotations

import argparse
import ast
import collections
import hashlib
import io
import json
import keyword
import os
import re
import sys
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MANIFEST = "translation/locked-code.sha256"
OUT_JSONL = "translation/part2/code-inventory.jsonl"
OUT_SUMMARY = "translation/part2/code-inventory-summary.md"
MAX_TEXT = 200
IDENT = re.compile(r"[^\W\d]\w*", re.UNICODE)
IDENT_HYPHEN = re.compile(r"[^\W\d][\w-]*", re.UNICODE)  # COBOL, Lisp, Forth names carry hyphens

# ---------------------------------------------------------------------------
# language table
# ---------------------------------------------------------------------------

C_LIKE = dict(line=["//"], block=[("/*", "*/", False)],
              strings=[('"', '"', "\\", True)], char=True)

SPECS: dict[str, dict] = {
    "python": dict(line=["#"], strings=[('"""', '"""', "\\", True), ("'''", "'''", "\\", True),
                                        ('"', '"', "\\", False), ("'", "'", "\\", False)]),
    "shell": dict(line=["#"], hash_word=True, heredoc=True,
                  strings=[('"', '"', "\\", True), ("'", "'", None, True)]),
    "dockerfile": dict(line=["#"], hash_word=True, strings=[('"', '"', "\\", False)]),
    "makefile": dict(line=["#"], strings=[('"', '"', "\\", False), ("'", "'", None, False)]),
    "cmake": dict(line=["#"], block=[("#[[", "]]", False)], strings=[('"', '"', "\\", True)]),
    "powershell": dict(line=["#"], block=[("<#", "#>", False)],
                       strings=[('"', '"', "`", True), ("'", "'", None, True)]),
    "batch": dict(line_start_words=["REM", "::"], strings=[('"', '"', None, False)]),
    "awk": dict(line=["#"], strings=[('"', '"', "\\", False)]),
    "perl": dict(line=["#"], strings=[('"', '"', "\\", True), ("'", "'", "\\", True)]),
    "sed": dict(line=["#"], hash_word=True),
    "ed": dict(line=["#"], hash_word=True),
    "ex": dict(line_start_words=['"']),
    "tcl": dict(line=["#"], hash_word=True, strings=[('"', '"', "\\", True)]),
    "m4": dict(line=["#"], line_words=["dnl"], strings=[("`", "'", None, True)]),
    "csharp": dict(C_LIKE, strings=[('@"', '"', '"', True), ('$@"', '"', '"', True),
                                    ('$"', '"', "\\", True), ('"""', '"""', None, True),
                                    ('"', '"', "\\", False)]),
    "java": dict(C_LIKE, strings=[('"""', '"""', "\\", True), ('"', '"', "\\", False)]),
    "kotlin": dict(C_LIKE, strings=[('"""', '"""', None, True), ('"', '"', "\\", False)]),
    "go": dict(C_LIKE, strings=[("`", "`", None, True), ('"', '"', "\\", False)]),
    "rust": dict(line=["//"], block=[("/*", "*/", True)], char=True,
                 strings=[('r#"', '"#', None, True), ('r"', '"', None, True),
                          ('b"', '"', "\\", True), ('"', '"', "\\", True)]),
    "c": dict(C_LIKE, strings=[('"', '"', "\\", False)]),
    "javascript": dict(line=["//"], block=[("/*", "*/", False)],
                       strings=[("`", "`", "\\", True), ('"', '"', "\\", False),
                                ("'", "'", "\\", False)]),
    "fsharp": dict(line=["//"], block=[("(*", "*)", True)], char=True,
                   strings=[('"""', '"""', None, True), ('@"', '"', '"', True),
                            ('"', '"', "\\", True)]),
    "haskell": dict(line=["--"], block=[("{-", "-}", True)], char=True,
                    strings=[('"', '"', "\\", True)]),
    "lisp": dict(line=[";"], block=[("#|", "|#", True)], skip=["#\\"],
                 strings=[('"', '"', "\\", True)]),
    "sql": dict(line=["--"], block=[("/*", "*/", False)], strings=[("'", "'", "'", True),
                                                                    ('"', '"', '"', True)]),
    "cobol": dict(line=["*>"], cobol_fixed=True,
                  strings=[('"', '"', '"', False), ("'", "'", "'", False)]),
    "apl": dict(line=["⍝"], strings=[("'", "'", "'", False)]),
    "forth": dict(word_start=True, line=["\\"], block=[("(", ")", False)],
                  strings=[('." ', '"', None, True), ('s" ', '"', None, True),
                           ('S" ', '"', None, True), ('c" ', '"', None, True)]),
    "xml": dict(block=[("<!--", "-->", False)], strings=[('"', '"', None, True)]),
    "json": dict(strings=[('"', '"', "\\", False)]),
    "toml": dict(line=["#"], strings=[('"""', '"""', "\\", True), ('"', '"', "\\", False),
                                      ("'", "'", None, False)]),
    "properties": dict(line=["#", "!"]),
    "gradle": dict(line=["//"], block=[("/*", "*/", False)],
                   strings=[('"""', '"""', "\\", True), ('"', '"', "\\", False),
                            ("'", "'", "\\", False)]),
    "gitconfig": dict(line=["#"]),
    "data": dict(),
}

KEYWORDS = {
    "shell": "if then else elif fi for while until do done case esac in function select time local "
             "export readonly declare return exit break continue set unset shift trap eval exec source",
    "csharp": "using namespace class struct enum interface public private protected internal static "
              "void int long double string bool var new return if else for foreach while do switch case "
              "break continue try catch finally throw null true false async await in out ref readonly const",
    "java": "package import class interface enum public private protected static final void int long "
            "double boolean new return if else for while do switch case break continue try catch "
            "finally throw throws null true false var this extends implements",
    "kotlin": "package import class object interface fun val var if else for while when return in is as "
              "null true false try catch finally throw private public internal override data",
    "go": "package import func var const type struct interface map chan if else for range switch case "
          "default return go defer select break continue nil true false",
    "rust": "use mod fn let mut const static struct enum impl trait pub if else for while loop match "
            "return break continue as in ref self Self crate true false where move unsafe",
    "javascript": "const let var function class return if else for while do switch case break continue "
                  "new this import export from default async await try catch finally throw typeof "
                  "null true false undefined of in",
    "haskell": "module import where let in case of if then else data type newtype class instance do "
               "deriving qualified as hiding",
    "fsharp": "module open let rec mutable if then else for while do match with fun function type "
              "member true false in yield",
    "sql": "select from where insert into values update set delete create table drop alter index view "
           "join left right inner outer on group by order having limit as and or not null primary key "
           "integer text real begin commit rollback pragma with union all distinct case when then else end",
    "tcl": "proc set puts if else elseif for foreach while switch return incr expr list lappend "
           "string format array dict upvar global namespace",
    "awk": "BEGIN END function if else for while do return printf print getline next exit delete in",
    "lisp": "defun defvar defparameter defmacro let let* lambda if cond when unless loop do dolist "
            "dotimes setf setq progn format",
    "cobol": "IDENTIFICATION DIVISION PROGRAM-ID ENVIRONMENT DATA WORKING-STORAGE SECTION PROCEDURE "
             "PIC PICTURE VALUE PERFORM UNTIL TIMES IF ELSE END-IF COMPUTE ADD MOVE DISPLAY STOP RUN "
             "OPEN CLOSE READ WRITE SELECT ASSIGN FILE",
    "forth": "do loop if else then begin until while repeat variable constant create does> ;",
    "powershell": "function param if else elseif foreach for while switch return begin process end "
                  "try catch finally throw",
    "python": " ".join(keyword.kwlist),
}
KEYWORDS = {k: set(v.split()) for k, v in KEYWORDS.items()}
DECL_WORDS = {"def", "class", "fn", "func", "fun", "function", "let", "var", "val", "const", "proc",
              "defun", "defvar", "defparameter", "defmacro", "variable", "constant", "package",
              "namespace", "module", "type", "struct", "enum", "interface", "local", "mut",
              "int", "long", "double", "string", "bool", "boolean", "void", "static", "readonly"}

EXT_LANG = {
    ".sh": "shell", ".bash": "shell", ".bat": "batch", ".ps1": "powershell", ".py": "python",
    ".cs": "csharp", ".java": "java", ".kt": "kotlin", ".go": "go", ".rs": "rust", ".c": "c",
    ".mjs": "javascript", ".js": "javascript", ".fs": "fsharp", ".hs": "haskell",
    ".lisp": "lisp", ".sql": "sql", ".cob": "cobol", ".apl": "apl", ".awk": "awk",
    ".tcl": "tcl", ".m4": "m4", ".pl": "perl", ".sed": "sed", ".ed": "ed", ".ex": "ex",
    ".cmake": "cmake", ".xaml": "xml", ".csproj": "xml", ".json": "json", ".toml": "toml",
    ".properties": "properties", ".gradle": "gradle", ".gitignore": "gitconfig",
    ".gitattributes": "gitconfig", ".mod": "data", ".sum": "data", ".lock": "data",
    ".txt": "data", ".fth": "forth",
}
NAME_LANG = {"Dockerfile": "dockerfile", "Makefile": "makefile", "CODEOWNERS": "gitconfig",
             "gradlew": "shell", "LICENSE": "data", ".gitattributes": "gitconfig",
             ".gitignore": "gitconfig"}
BINARY_EXT = {".jar", ".pyc", ".png", ".gif", ".jpg", ".ico", ".pdf", ".zip"}

SQL_START = re.compile(r"^\s*(select|insert|create|update|delete|drop|pragma|with|begin|alter)\b",
                       re.I)
PATH_LIKE = re.compile(r"^(?:[./~]|[A-Za-z]:\\)[\w./\\~-]*$|^[\w.-]+/[\w./-]+$")
FORMAT_LIKE = re.compile(r"%[-+ 0#]*\d*(?:\.\d+)?[sdifxXcgeEu]|\{\d*(?::[^}]*)?\}|\$\{?\w+\}?|\\[nrt]")
WORDS = re.compile(r"[^\W\d_]{2,}[^\n]*\s[^\W\d_]{2,}", re.UNICODE)


def detect_lang(path: str, head: bytes) -> str:
    base = os.path.basename(path)
    if path.startswith("src/forth") and base.endswith((".fs", ".fth", ".4th")):
        return "forth"  # .fs is Forth here, F# elsewhere
    if base in NAME_LANG:
        return NAME_LANG[base]
    ext = os.path.splitext(base)[1].lower()
    if ext in EXT_LANG:
        return EXT_LANG[ext]
    first = head.split(b"\n", 1)[0]
    if first.startswith(b"#!"):
        if b"python" in first:
            return "python"
        if b"awk" in first:
            return "awk"
        return "shell"
    return "data"


def is_binary(path: str, data: bytes) -> bool:
    return os.path.splitext(path)[1].lower() in BINARY_EXT or b"\0" in data[:4096]


# ---------------------------------------------------------------------------
# lexical scanner
# ---------------------------------------------------------------------------

CHARLIT = re.compile(r"'(?:\\(?:u[0-9a-fA-F]{4}|x[0-9a-fA-F]{2}|.)|[^\\'\n])'")
HEREDOC = re.compile(r"<<(-?)\s*(['\"]?)([A-Za-z_][\w]*)\2")


def scan(text: str, spec: dict):
    """Yield (kind, start, end) with kind in comment|string|code|heredoc|char."""
    n = len(text)
    i = 0
    code_start = 0
    pending: list[tuple[str, bool]] = []
    word_start = spec.get("word_start", False)

    def at_word_start(k: int) -> bool:
        return k == 0 or text[k - 1].isspace()

    line_words = spec.get("line_start_words", [])
    out = []
    while i < n:
        c = text[i]
        # newline with pending heredocs
        if c == "\n" and pending:
            j = i + 1
            for tag, strip in pending:
                body_start = j
                while j < n:
                    e = text.find("\n", j)
                    e = n if e < 0 else e
                    line = text[j:e]
                    if (line.strip() if strip else line) == tag:
                        break
                    j = e + 1
                out.append(("heredoc", body_start, j, tag))
                j = (text.find("\n", j) + 1) or n
            pending = []
            out.append(("code_flush", i + 1, i + 1))
            i = j
            continue
        # cobol fixed-format comment lines
        if spec.get("cobol_fixed") and (i == 0 or text[i - 1] == "\n"):
            e = text.find("\n", i)
            e = n if e < 0 else e
            ln = text[i:e]
            if len(ln) > 6 and ln[6] in "*/":
                out.append(("comment", i, e))
                i = e
                continue
        # line-start words (REM, ::, ex ")
        if line_words is not None and line_words and (i == 0 or text[i - 1] == "\n" or
                                                      text[i - 1] in " \t" and text[:i].rsplit("\n", 1)[-1].strip() == ""):
            hit = None
            for w in line_words:
                if text[i:i + len(w)].upper() == w.upper() and (
                        not w[0].isalpha() or text[i + len(w):i + len(w) + 1] in ("", " ", "\t", "\n", "\r")):
                    hit = w
                    break
            if hit:
                e = text.find("\n", i)
                e = n if e < 0 else e
                out.append(("comment", i, e))
                i = e
                continue
        # skip prefixes (lisp #\x)
        sk = next((s for s in spec.get("skip", []) if text.startswith(s, i)), None)
        if sk:
            i += len(sk) + 1
            continue
        # block comments
        blk = None
        for o, cl, nest in spec.get("block", []):
            if text.startswith(o, i) and (not word_start or (at_word_start(i) and text[i + len(o):i + len(o) + 1] in (" ", "\n", ""))
                                          or o != "("):
                blk = (o, cl, nest)
                break
        if blk:
            o, cl, nest = blk
            j, depth = i + len(o), 1
            while j < n and depth:
                if nest and text.startswith(o, j):
                    depth += 1
                    j += len(o)
                elif text.startswith(cl, j):
                    depth -= 1
                    j += len(cl)
                else:
                    j += 1
            out.append(("comment", i, j))
            i = j
            continue
        # line comments
        lc = None
        for p in spec.get("line", []):
            if text.startswith(p, i):
                if spec.get("hash_word") and p == "#" and not (i == 0 or text[i - 1] in " \t\n;&|(){"):
                    continue
                if word_start and not (at_word_start(i) and text[i + len(p):i + len(p) + 1] in (" ", "\n", "\t", "")):
                    continue
                lc = p
                break
        if not lc:
            for w in spec.get("line_words", []):
                if text.startswith(w, i) and (i == 0 or not (text[i - 1].isalnum() or text[i - 1] == "_")) \
                        and not (text[i + len(w):i + len(w) + 1].isalnum()):
                    lc = w
                    break
        if lc:
            e = text.find("\n", i)
            e = n if e < 0 else e
            out.append(("comment", i, e))
            i = e
            continue
        # heredoc marker (shell)
        if spec.get("heredoc") and text.startswith("<<", i) and not text.startswith("<<<", i):
            m = HEREDOC.match(text, i)
            if m:
                pending.append((m.group(3), m.group(1) == "-"))
                i = m.end()
                continue
        # char literals
        if spec.get("char") and c == "'" and (i == 0 or not (text[i - 1].isalnum() or text[i - 1] == "_")):
            m = CHARLIT.match(text, i)
            if m:
                out.append(("char", i, m.end()))
                i = m.end()
                continue
            i += 1
            continue
        # strings
        st = None
        for o, cl, esc, ml in sorted(spec.get("strings", []), key=lambda s: -len(s[0])):
            if text.startswith(o, i):
                if o in ("'", '"', "`") and spec.get("hash_word") is None and False:
                    pass
                st = (o, cl, esc, ml)
                break
        if st:
            o, cl, esc, ml = st
            if word_start and not at_word_start(i):
                i += 1
                continue
            j = i + len(o)
            while j < n:
                if esc and text[j] == esc and esc != cl[:1] and j + 1 < n:
                    j += 2
                    continue
                if esc and esc == cl[:1] and text.startswith(cl + cl, j):
                    j += 2 * len(cl)
                    continue
                if text.startswith(cl, j):
                    j += len(cl)
                    break
                if text[j] == "\n" and not ml:
                    break
                j += 1
            out.append(("string", i, j))
            i = j
            continue
        i += 1
    return out


def line_of(starts: list[int], pos: int) -> int:
    lo, hi = 0, len(starts)
    while lo < hi:
        mid = (lo + hi) // 2
        if starts[mid] <= pos:
            lo = mid + 1
        else:
            hi = mid
    return lo


def line_starts(text: str) -> list[int]:
    s = [0]
    for m in re.finditer("\n", text):
        s.append(m.end())
    return s


def clip(s: str) -> str:
    s = s.replace("\r", "")
    return s if len(s) <= MAX_TEXT else s[:MAX_TEXT] + "…"


def classify_string(body: str, lang: str) -> str:
    if SQL_START.match(body):
        return "sql"
    if PATH_LIKE.match(body.strip()):
        return "path-or-contract"
    if FORMAT_LIKE.search(body):
        return "format-or-template"
    if WORDS.search(body):
        return "display-candidate"
    return "literal"


def strip_delims(raw: str, spec: dict) -> str:
    for o, cl, _e, _m in sorted(spec.get("strings", []), key=lambda s: -len(s[0])):
        if raw.startswith(o) and len(raw) >= len(o):
            body = raw[len(o):]
            return body[:-len(cl)] if cl and body.endswith(cl) else body
    return raw


def guess_heredoc_lang(tag: str, body: str) -> str:
    t = tag.upper()
    if "SQL" in t or SQL_START.match(body):
        return "sql"
    if "PY" in t or body.lstrip().startswith(("import ", "def ", "#!/usr/bin/env python")):
        return "python"
    if t in ("EOF", "EOT", "END", "HEREDOC"):
        if body.lstrip().startswith("#!"):
            return "shell"
        return "text"
    return "text"


def lexical_record(text: str, lang: str, path: str) -> dict:
    spec = SPECS.get(lang, SPECS["data"])
    starts = line_starts(text)
    spans = scan(text, spec)
    comments, strings, embedded = [], [], []
    mask = bytearray(len(text))  # 1 = not code
    for sp in spans:
        kind, a, b = sp[0], sp[1], sp[2]
        if kind == "code_flush":
            continue
        for k in range(a, min(b, len(text))):
            mask[k] = 1
        la, lb = line_of(starts, a), line_of(starts, max(a, b - 1))
        raw = text[a:b]
        if kind == "comment":
            comments.append({"line": la, "end_line": lb, "text": clip(raw)})
        elif kind == "heredoc":
            embedded.append({"lang": guess_heredoc_lang(sp[3], raw), "kind": "heredoc",
                             "tag": sp[3], "line": la, "end_line": lb})
        elif kind == "char":
            strings.append({"line": la, "end_line": lb, "text": clip(raw), "class": "char"})
        else:
            body = strip_delims(raw, spec)
            cls = classify_string(body, lang)
            strings.append({"line": la, "end_line": lb, "text": clip(body), "class": cls})
            if cls == "sql":
                embedded.append({"lang": "sql", "kind": "string", "line": la, "end_line": lb})
    kws = KEYWORDS.get(lang, set())
    ids = collections.OrderedDict()
    for m in (IDENT_HYPHEN if lang in ("cobol", "lisp", "forth") else IDENT).finditer(text):
        a = m.start()
        if mask[a]:
            continue
        name = m.group(0)
        ln = line_of(starts, a)
        before = text[max(0, a - 2):a]
        prev_word = re.search(r"([\w-]+)\s+$", text[max(0, a - 30):a])
        after = text[m.end():m.end() + 2].lstrip()
        if lang == "forth" or lang == "cobol":
            key = name.upper() if lang == "cobol" else name
        else:
            key = name
        if key in kws or name in kws or name.lower() in kws and lang in ("sql", "cobol"):
            role = "keyword"
        elif before.endswith(".") or before.endswith("::") or before.endswith("->"):
            role = "member"
        elif prev_word and prev_word.group(1) in DECL_WORDS:
            role = "declaration"
        elif after.startswith("=") and not after.startswith("==") and \
                (text[:a].rsplit("\n", 1)[-1].strip() == "" or lang in ("shell", "awk", "tcl")):
            role = "declaration"
        else:
            role = "reference"
        rec = ids.setdefault(name, {"name": name, "roles": set(), "count": 0, "first_line": ln})
        rec["roles"].add(role)
        rec["count"] += 1
    # families that are code only by embedding
    fam_embed = family_embedded(path, lang)
    embedded = fam_embed + embedded
    idl = [{"name": r["name"], "roles": sorted(r["roles"]), "count": r["count"],
            "first_line": r["first_line"]} for r in ids.values()]
    return dict(parser="lexical", comments=comments, strings=strings, embedded=embedded,
                identifiers=idl)


def family_embedded(path: str, lang: str) -> list[dict]:
    """Regex engines and similar: the whole file is (or hosts) another language."""
    p = path.lower()
    out = []
    if "/regex-" in p or p.startswith("src/regex-"):
        out.append({"lang": "regex", "kind": "family", "note": "regex-engine family: pattern bytes are the lesson"})
    if lang in ("sed", "awk", "perl") and not out:
        out.append({"lang": "regex", "kind": "inline", "note": "regex literals inside " + lang})
    return out


# ---------------------------------------------------------------------------
# Python: parser-backed
# ---------------------------------------------------------------------------

def python_record(text: str, path: str) -> dict:
    spec = SPECS["python"]
    comments, strings = [], []
    ids: dict[str, dict] = collections.OrderedDict()
    try:
        toks = list(tokenize.generate_tokens(io.StringIO(text).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        rec = lexical_record(text, "python", path)
        rec["parser"] = "lexical (python tokenize failed)"
        return rec
    for t in toks:
        if t.type == tokenize.COMMENT:
            comments.append({"line": t.start[0], "end_line": t.end[0], "text": clip(t.string)})
        elif t.type == tokenize.STRING:
            body = t.string.lstrip("rbfuRBFU")
            for q in ('"""', "'''", '"', "'"):
                if body.startswith(q):
                    body = body[len(q):-len(q)]
                    break
            strings.append({"line": t.start[0], "end_line": t.end[0], "text": clip(body),
                            "class": classify_string(body, "python")})
    roles: dict[tuple[str, int], str] = {}
    try:
        tree = ast.parse(text)
    except SyntaxError:
        tree = None
    if tree is not None:
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                roles[(node.name, node.lineno)] = "declaration"
            elif isinstance(node, ast.arg):
                roles[(node.arg, node.lineno)] = "declaration"
            elif isinstance(node, ast.Name) and isinstance(node.ctx, ast.Store):
                roles[(node.id, node.lineno)] = "declaration"
            elif isinstance(node, ast.Attribute):
                roles[(node.attr, node.lineno)] = "member"
            elif isinstance(node, (ast.Import, ast.ImportFrom)):
                for a in node.names:
                    for part in a.name.split("."):
                        roles[(part, node.lineno)] = "import"
    for t in toks:
        if t.type != tokenize.NAME:
            continue
        name, ln = t.string, t.start[0]
        if keyword.iskeyword(name):
            role = "keyword"
        else:
            role = roles.get((name, ln), "reference")
        rec = ids.setdefault(name, {"name": name, "roles": set(), "count": 0, "first_line": ln})
        rec["roles"].add(role)
        rec["count"] += 1
    idl = [{"name": r["name"], "roles": sorted(r["roles"]), "count": r["count"],
            "first_line": r["first_line"]} for r in ids.values()]
    embedded = [{"lang": "sql", "kind": "string", "line": s["line"], "end_line": s["end_line"]}
                for s in strings if s["class"] == "sql"]
    return dict(parser="python-ast+tokenize" if tree is not None else "python-tokenize",
                comments=comments, strings=strings, embedded=embedded, identifiers=idl)


# ---------------------------------------------------------------------------
# XML-ish hosts: embedded JavaScript, XAML bindings
# ---------------------------------------------------------------------------

def xml_extras(text: str, rec: dict) -> None:
    starts = line_starts(text)
    for m in re.finditer(r"<script\b[^>]*>(.*?)</script>", text, re.S | re.I):
        rec["embedded"].append({"lang": "javascript", "kind": "script",
                                "line": line_of(starts, m.start(1)),
                                "end_line": line_of(starts, m.end(1))})


# ---------------------------------------------------------------------------
# per-file record
# ---------------------------------------------------------------------------

def family_of(path: str) -> str:
    parts = path.split("/")
    if parts[0] in ("src", "lessons") and len(parts) >= 3:
        if parts[0] == "lessons":
            return "/".join(parts[:3]) if len(parts) > 3 else "/".join(parts[:2])
        return "src/" + parts[1]
    return parts[0] if len(parts) > 1 else "(root)"


def inventory_file(root: str, path: str, expected_sha: str | None = None) -> dict:
    full = os.path.join(root, path)
    with open(full, "rb") as f:
        data = f.read()
    sha = hashlib.sha256(data).hexdigest()
    flags0 = []
    if expected_sha is not None and sha != expected_sha:
        lf = hashlib.sha256(data.replace(b"\r\n", b"\n")).hexdigest()
        if lf == expected_sha:  # CRLF checkout; the lock accepts CRLF->LF (see lock_code.py)
            sha = lf
            flags0 = ["crlf-checkout"]
        else:
            flags0 = ["sha-differs-from-lock"]
    base = {"path": path, "family": family_of(path), "sha256": sha, "bytes": len(data)}
    if flags0:
        base["flags"] = flags0
    if is_binary(path, data):
        base.update(host="binary", parser="none", lines=0, comments=[], strings=[],
                    embedded=[], identifiers=[])
        return base
    try:
        text = data.decode("utf-8")
        flags = []
    except UnicodeDecodeError:
        text = data.decode("latin-1")
        flags = ["not-utf8"]
    if text.startswith("﻿"):
        text = text[1:]
        flags.append("bom")
    if "\r\n" in text:
        flags.append("crlf")
        text = text.replace("\r\n", "\n")
    lang = detect_lang(path, data[:200])
    if lang == "python":
        rec = python_record(text, path)
    else:
        rec = lexical_record(text, lang, path)
        if lang == "xml":
            xml_extras(text, rec)
        if lang == "data":
            rec["parser"] = "none (data file)"
    base["host"] = lang
    base["lines"] = text.count("\n") + (0 if text.endswith("\n") or not text else 1)
    base["flags"] = base.get("flags", []) + flags
    base.update(rec)
    return base


def load_manifest(root: str) -> dict[str, str]:
    out = {}
    with open(os.path.join(root, MANIFEST), encoding="utf-8") as f:
        for ln in f:
            ln = ln.rstrip("\n")
            if not ln.strip() or ln.startswith("#"):
                continue
            sha, _, p = ln.partition("  ")
            out[p.strip()] = sha.strip()
    return out


def build(root: str, manifest: dict[str, str] | None = None) -> list[dict]:
    manifest = manifest if manifest is not None else load_manifest(root)
    return [inventory_file(root, p, manifest[p]) for p in sorted(manifest)]


def dump_jsonl(records: list[dict]) -> str:
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True) + "\n" for r in records)


def summarize(records: list[dict]) -> str:
    hosts = collections.Counter(r["host"] for r in records)
    parsers = collections.Counter(r["parser"].split(" ")[0] for r in records)
    emb = collections.Counter(e["lang"] for r in records for e in r["embedded"])
    fams = collections.defaultdict(lambda: [0, 0, 0, 0])
    for r in records:
        f = fams[r["family"]]
        f[0] += 1
        f[1] += len(r["comments"])
        f[2] += len(r["strings"])
        f[3] += len(r["identifiers"])
    cls = collections.Counter(s["class"] for r in records for s in r["strings"])
    roles = collections.Counter(ro for r in records for i in r["identifiers"] for ro in i["roles"])
    L = ["# Part II code inventory (generated)", "",
         "Generated by `python3 -I tools/code_inventory.py --write`; do not edit by hand.",
         "Source: `translation/part2/code-inventory.jsonl`, one record per path in "
         "`translation/locked-code.sha256`. Roles and string classes are provisional hints; "
         "the registries and the scope file decide (plan 4.5.1).", "",
         f"- Files inventoried: {len(records)}",
         f"- Comments: {sum(len(r['comments']) for r in records)}; string literals: "
         f"{sum(len(r['strings']) for r in records)}; distinct identifiers (per file): "
         f"{sum(len(r['identifiers']) for r in records)}", "",
         "## Host languages", "", "| Host | Files |", "| --- | ---: |"]
    L += [f"| {h} | {c} |" for h, c in sorted(hosts.items())]
    L += ["", "## Parser kind", "", "| Parser | Files |", "| --- | ---: |"]
    L += [f"| {h} | {c} |" for h, c in sorted(parsers.items())]
    L += ["", "## Embedded languages", "", "| Language | Occurrences |", "| --- | ---: |"]
    L += [f"| {h} | {c} |" for h, c in sorted(emb.items())] or ["| (none) | 0 |"]
    L += ["", "## String classes (provisional)", "", "| Class | Count |", "| --- | ---: |"]
    L += [f"| {h} | {c} |" for h, c in sorted(cls.items())]
    L += ["", "## Identifier roles (provisional)", "", "| Role | Identifier entries |",
          "| --- | ---: |"]
    L += [f"| {h} | {c} |" for h, c in sorted(roles.items())]
    L += ["", "## Families", "", "| Family | Files | Comments | Strings | Identifiers |",
          "| --- | ---: | ---: | ---: | ---: |"]
    L += [f"| {k} | {v[0]} | {v[1]} | {v[2]} | {v[3]} |" for k, v in sorted(fams.items())]
    flagged = [r["path"] for r in records if r.get("flags")]
    L += ["", f"## Flagged files ({len(flagged)})", ""]
    L += [f"- `{p}`" for p in flagged[:60]]
    return "\n".join(L) + "\n"


def check(root: str) -> list[str]:
    problems = []
    manifest = load_manifest(root)
    path = os.path.join(root, OUT_JSONL)
    if not os.path.exists(path):
        return [f"{OUT_JSONL} missing; run --write"]
    seen = collections.Counter()
    recs = {}
    with open(path, encoding="utf-8") as f:
        for n, ln in enumerate(f, 1):
            if not ln.strip():
                continue
            try:
                r = json.loads(ln)
            except json.JSONDecodeError:
                problems.append(f"line {n}: not JSON")
                continue
            seen[r.get("path")] += 1
            recs[r.get("path")] = r
    for p in manifest:
        if seen[p] != 1:
            problems.append(f"{p}: appears {seen[p]} times (want exactly 1)")
    for p in seen:
        if p not in manifest:
            problems.append(f"{p}: not in {MANIFEST}")
    for p, r in recs.items():
        if p in manifest and r.get("sha256") != manifest[p]:
            problems.append(f"{p}: inventory sha differs from lock")
    return problems


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--write", action="store_true")
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("files", nargs="*")
    a = ap.parse_args(argv)
    if a.files:
        for p in a.files:
            print(json.dumps(inventory_file(a.root, p), ensure_ascii=False, indent=1))
        return 0
    if a.write:
        recs = build(a.root)
        os.makedirs(os.path.join(a.root, "translation/part2"), exist_ok=True)
        with open(os.path.join(a.root, OUT_JSONL), "w", encoding="utf-8", newline="\n") as f:
            f.write(dump_jsonl(recs))
        with open(os.path.join(a.root, OUT_SUMMARY), "w", encoding="utf-8", newline="\n") as f:
            f.write(summarize(recs))
        print(f"wrote {len(recs)} records")
        return 0
    if a.check:
        probs = check(a.root)
        for p in probs:
            print("PROBLEM:", p)
        if not probs:
            print("code inventory OK")
        return 1 if probs else 0
    ap.print_help()
    return 2


if __name__ == "__main__":
    sys.exit(main())
