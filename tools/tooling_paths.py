#!/usr/bin/env python3
"""Find hard-coded renamed paths in the build and check tooling (plan 5.6, P3B-003).

The publication tooling must not spell a path that translation/path-map.yaml renames: it names the English path as a
KEY and asks the locale catalog for the path in the edition being built (cs.P, study_guides.GW/GP/LP, catalog .path()).
This tool parses each tooling file and reports every string literal that is, or ends in, a renamed English path and is
not one of:
  * a docstring (prose, not a path in use);
  * an argument of a mapper call (P, E, GW, GP, LP, path, english, lessons_path, lessons_english);
  * part of a module-level table of English guide keys (TABLE_NAMES): those are keys, mapped at the point of use.
  * on a line that carries a `# en-key` comment (a key of the English-keyed generated files) or a `# path-ok: reason`
    comment (a path that merely shares a file name with a renamed one, such as lessons/cs-source/index.md).
A bare folder name (os.path.join(LESSONS, "cs")) is reported too when it is an argument of os.path.join / posixpath.join.

Usage:  python3 -I tools/tooling_paths.py            # exit 0 = clean, 1 = hard-coded paths found
        python3 -I tools/tooling_paths.py FILE...    # scan these files instead of the default tooling set
"""
import ast
import glob
import io
import os
import sys
import tokenize

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MAP_PATH = os.path.join(ROOT, "translation", "path-map.yaml")

MARKERS = ("en-key", "path-ok")
MAPPERS = {"P", "E", "GW", "GP", "LP", "path", "english", "lessons_path", "lessons_english"}
TABLE_NAMES = {"LANGUAGE_GUIDES", "CONCEPT_GUIDES", "ALL_GUIDES", "EXPECTED_DIAGRAMS", "BOOK_LINKS"}
JOINERS = {"join"}


def default_files():
    out = []
    if HERE not in sys.path:
        sys.path.insert(0, HERE)
    import enpath
    layer = enpath.load(ROOT)
    for pattern in ("lessons/book/*.py", "lessons/curriculum/build.py", "lessons/study-guides/build.py"):
        out += glob.glob(os.path.join(ROOT, *layer.work(pattern).split("/")))    # the two builders move with their folder
    return sorted(f for f in out if not os.path.basename(f).startswith("test_"))


def load_map(path=MAP_PATH):
    import yaml
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)["paths"]


def candidates(mapping):
    """(literals, folder names): the strings that spell a renamed path. A suffix of an English path counts only when
    the same-length suffix of its Spanish path differs (so `README.md` and `build.py` never count)."""
    literals, folders = set(), set()
    for en, es in mapping.items():
        if en == es:
            continue
        a, b = en.split("/"), es.split("/")
        for i in range(len(a)):
            if a[i:] != b[i:]:
                literals.add("/".join(a[i:]))
                if i < len(a) - 1:
                    folders.add(a[i])
    folders = {f for f in folders if not any(f == x for x in ("lessons", "docs"))}
    return literals, folders


def call_name(node):
    f = node.func
    if isinstance(f, ast.Name):
        return f.id
    if isinstance(f, ast.Attribute):
        return f.attr
    return None


class Scan(ast.NodeVisitor):
    def __init__(self, literals, folders, marked=()):
        self.literals, self.folders, self.marked = literals, folders, set(marked)
        self.found = []
        self.stack = []

    def generic_visit(self, node):
        self.stack.append(node)
        super().generic_visit(node)
        self.stack.pop()

    def exempt(self):
        for node in self.stack:
            if isinstance(node, ast.Call) and call_name(node) in MAPPERS:
                return True
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id in TABLE_NAMES for t in node.targets):
                return True
        return False

    def spells(self, text):
        head = text.partition("#")[0]
        parts = head.split("/")
        if any("/".join(parts[i:]) in self.literals for i in range(len(parts))):
            return True
        return any(head.rstrip("/").endswith("/" + lit) or head.rstrip("/") == lit or ("/" + lit + "/") in head or head.startswith(lit + "/")
                   for lit in self.literals if "/" in lit)

    def visit_Constant(self, node):
        if isinstance(node.value, str) and node.value and node.lineno not in self.marked and not self.exempt():
            if getattr(node, "_doc", False):
                return
            if self.spells(node.value):
                self.found.append((node.lineno, node.value))
            elif node.value in self.folders and any(isinstance(n, ast.Call) and call_name(n) in JOINERS for n in self.stack[-2:]):
                self.found.append((node.lineno, node.value))


def mark_docstrings(tree):
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.ClassDef, ast.AsyncFunctionDef)):
            body = node.body
            if body and isinstance(body[0], ast.Expr) and isinstance(body[0].value, ast.Constant) and isinstance(body[0].value.value, str):
                body[0].value._doc = True


def scan_source(source, literals, folders):
    tree = ast.parse(source)
    mark_docstrings(tree)
    marked = {t.start[0] for t in tokenize.generate_tokens(io.StringIO(source).readline)
              if t.type == tokenize.COMMENT and any(m in t.string for m in MARKERS)}
    scan = Scan(literals, folders, marked)
    scan.visit(tree)
    return scan.found


def main(argv):
    literals, folders = candidates(load_map())
    files = argv[1:] or default_files()
    bad = 0
    for f in files:
        with open(f, encoding="utf-8") as fh:
            hits = scan_source(fh.read(), literals, folders)
        for line, text in hits:
            bad += 1
            print(f"{os.path.relpath(f, ROOT)}:{line}: hard-coded renamed path {text!r}: route it through the locale catalog (paths.*)")
    print("tooling_paths:", "FAIL (%d)" % bad if bad else f"ok ({len(files)} files)")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
