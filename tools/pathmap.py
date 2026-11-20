#!/usr/bin/env python3
"""tools/pathmap.py: Spanish names for student-facing paths (plan 5.6, task P3B-001).

The English path is the canonical key. translation/path-map.yaml maps every English path
of the imported tree (every non-owned file) to its Spanish path, or to itself when the path
must stay. translation/path-map-report.md lists every path as renamed or kept with the reason.

Inputs: the tracked file set and its classes (tools/inventory.py), the naming table
translation/path-names.es.yaml, and the text of every frozen file and workflow.

Rules, in order, for each English file:
  1. frozen (any non-Markdown file the byte lock covers)            -> kept
  2. keep-list names: README.md, LICENSE, CONTRIBUTING.md, SECURITY.md, CODE_OF_CONDUCT.md,
     CODEOWNERS, anything under .github/                              -> kept
  3. keep-list trees: src/, sandbox/, gradle/, lessons/solutions/, lessons/tools/,
     lessons/book/ (build tree), lessons/cs-source/ (generator source) -> kept
  4. reference closure: a path that a frozen file mentions (or, for a Markdown document, a
     workflow mentions) stays English; so does every ancestor directory of such a path
  5. other non-Markdown files (tooling, archival)                    -> name kept (the file
     moves only when its directory is renamed)
  6. Markdown documents                                              -> renamed through
     translation/path-names.es.yaml; a missing row is an error (a human names the file)
Directories are renamed through the same table, unless a pinned path (rules 1 to 4) lies below
them or a frozen file mentions the directory itself.

Usage:
  python3 tools/pathmap.py --write    write translation/path-map.yaml and path-map-report.md
  python3 tools/pathmap.py --check    recompute; exit 1 on a problem or a stale committed file
  python3 tools/pathmap.py            print the summary only
"""
from __future__ import annotations

import os
import re
import sys
import unicodedata
from pathlib import PurePosixPath

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import inventory  # noqa: E402

ROOT = os.path.dirname(HERE)
NAMES_PATH = "translation/path-names.es.yaml"
MAP_PATH = "translation/path-map.yaml"
REPORT_PATH = "translation/path-map-report.md"
GLOSSARY_PATH = "translation/glossary.es.yaml"

# Exact names GitHub or tooling recognizes. README.md may sit in a renamed folder; the rest stay put.
README = "README.md"
HARD_KEEP_NAMES = {"README.md", "LICENSE", "CONTRIBUTING.md", "SECURITY.md", "CODE_OF_CONDUCT.md",
                   "CODEOWNERS"}
HARD_KEEP_PREFIXES = (".github/",)
KEEP_TREES = {
    "src/": "frozen code: entry folders and every code file",
    "sandbox/": "frozen sandbox scripts",
    "gradle/": "frozen build wrapper",
    "lessons/solutions/": "frozen solutions named by verify-exercises.sh and verify-windows.ps1",
    "lessons/tools/": "frozen scripts named by other frozen scripts",
    "lessons/book/": "build tree (frozen package files and tooling); maintainer docs only",
    "lessons/cs-source/": "generator source tree; sandbox/scope-check.sh names concepts/, roles/ and languages.txt",
}
# Paths the Phase 3B survey found named by frozen files (plan 5.6). --check fails if the scan loses one.
EXPECTED_PINNED = (
    "lessons", "lessons/exercises.md", "lessons/cs-source/concepts", "lessons/cs-source/languages.txt",
    "SANDBOX-SETUP.md", "CONTRIBUTING.md", "docs/running-with-gradle.md",
)
FUNCTION_WORDS = {"de", "del", "y", "la", "el", "los", "las", "en", "un", "una", "mas", "a", "por",
                  "para", "con", "que", "o", "como"}

PROPER_WORDS = {"cmake", "make", "ed", "ex", "sed", "csharp", "linq", "xaml", "regex"}

TOKEN_RE = re.compile(r"[\w.$@{}\-]+(?:/[\w.$@{}\-]+)*")
COMP_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*(?:\.[a-z0-9]+)*$")
CAPS_RE = re.compile(r"^[A-Z0-9]+(?:-[A-Z0-9]+)*(?:\.[a-z0-9]+)*$")
NUM_PREFIX_RE = re.compile(r"^(\d+)-")


# ------------------------------------------------------------------ mentions

def tokens(text: str) -> list[tuple[str, bool]]:
    """Path-like tokens of a text (backslashes read as slashes, leading ./ dropped). The flag is
    True for an open reference: the token is followed by a slash ('lessons/cs/', 'lessons/cs/*.md')
    or continues with a shell variable ('lessons/cs-source/concepts/$t.md'), so anything below it
    may be named at run time."""
    text = text.replace("\\", "/")
    out = []
    for m in TOKEN_RE.finditer(text):
        t = m.group(0)
        is_open = text[m.end():m.end() + 1] == "/"
        t = t.strip(".").lstrip("/")
        while t.startswith("./"):
            t = t[2:]
        if not t:
            continue
        parts = t.split("/")
        for i, c in enumerate(parts):
            if c.startswith(("$", "{")) and i > 0:
                t, is_open = "/".join(parts[:i]), True
                break
        out.append((t, is_open))
    return out


def mention_index(sources: list[tuple[str, str]], open_refs: dict[str, str] | None = None) -> dict[str, str]:
    """Every path prefix (at component boundaries) of every token -> first source naming it.
    open_refs, when given, collects the folders referenced openly (see tokens())."""
    idx: dict[str, str] = {}
    for src, text in sources:
        for tok, is_open in tokens(text):
            parts = tok.split("/")
            for i in range(1, len(parts) + 1):
                idx.setdefault("/".join(parts[:i]), src)
            if is_open and open_refs is not None and "/" in tok:
                open_refs.setdefault(tok, src)
    return idx


def is_text(data: bytes) -> bool:
    return b"\0" not in data[:8192]


# ------------------------------------------------------------------ names table

def load_names(text: str) -> dict:
    import yaml
    d = yaml.safe_load(text) or {}
    return {"dirs": dict(d.get("dirs") or {}), "files": dict(d.get("files") or {}),
            "proper": list(d.get("proper") or [])}


def fold(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", s) if not unicodedata.combining(c)).lower()


def glossary_words(text: str) -> set[str]:
    """Accent-folded words of every `es` value of the glossary."""
    import yaml
    words: set[str] = set()

    def walk(node):
        if isinstance(node, dict):
            for k, v in node.items():
                if k == "es" and isinstance(v, str):
                    words.update(re.findall(r"[a-z0-9]+", fold(v)))
                else:
                    walk(v)
        elif isinstance(node, list):
            for v in node:
                walk(v)

    walk(yaml.safe_load(text) or {})
    return words


# ------------------------------------------------------------------ core

def ancestors(path: str) -> list[str]:
    parts = path.split("/")
    return ["/".join(parts[:i]) for i in range(1, len(parts))]


def build(files: dict[str, str], read, names: dict, glossary: set[str] | None = None) -> dict:
    """Compute the map. files: English path -> inventory class (owned files already removed).
    read(path) -> text of a file or None (binary or unreadable). Returns a dict with
    'map' (en -> es), 'reasons', 'dir_map', 'dir_reasons', 'problems', 'notes', 'warnings'."""
    problems: list[str] = []
    notes: list[str] = []
    warnings: list[str] = []

    frozen_src, workflow_src = [], []
    for p, cls in sorted(files.items()):
        if cls == "frozen":
            t = read(p)
            if t is not None:
                frozen_src.append((p, t))
        elif p.startswith(".github/workflows/"):
            t = read(p)
            if t is not None:
                workflow_src.append((p, t))
    open_frozen: dict[str, str] = {}
    m_frozen = mention_index(frozen_src, open_frozen)
    m_workflow = mention_index(workflow_src)

    def open_ref(path: str):
        """(folder, source) when a frozen file names a folder openly and `path` lies below it."""
        for d, src in open_frozen.items():
            if path.startswith(d + "/"):
                return d, src
        return None

    is_md = {p: p.endswith(".md") and files[p] in ("authored", "generated") for p in files}
    table_files, table_dirs = names["files"], names["dirs"]
    proper = set(names["proper"])

    # ---- table sanity
    for p in list(table_files) + list(proper):
        if p not in files:
            problems.append(f"names table: file {p} does not exist (stale row)")
    all_dirs = {d for p in files for d in ancestors(p)}
    for d in table_dirs:
        if d not in all_dirs:
            problems.append(f"names table: directory {d} does not exist (stale row)")

    # ---- per-file decision: (kind, reason); kinds: pinned, movable
    kind: dict[str, str] = {}
    reason: dict[str, str] = {}
    for p in sorted(files):
        base = PurePosixPath(p).name
        in_table = p in table_files
        if files[p] == "frozen":
            kind[p], reason[p] = "pinned", "frozen: byte lock covers it"
        elif base in HARD_KEEP_NAMES and base != README or p.startswith(HARD_KEEP_PREFIXES):
            kind[p], reason[p] = "pinned", "keep-list: GitHub or tooling recognizes this exact name"
        elif any(p.startswith(t) for t in KEEP_TREES):
            t = next(t for t in KEEP_TREES if p.startswith(t))
            kind[p], reason[p] = "pinned", f"keep-list tree {t}: {KEEP_TREES[t]}"
        elif p in m_frozen:
            kind[p], reason[p] = "pinned", f"reference closure: {m_frozen[p]} (frozen) mentions it"
        elif open_ref(p):
            d, src = open_ref(p)
            kind[p], reason[p] = "pinned", f"reference closure: {src} (frozen) names the folder {d}/ openly"
        elif is_md[p] and p in m_workflow:
            kind[p], reason[p] = "pinned", f"reference closure: {m_workflow[p]} (workflow) mentions it"
        elif base == README:
            kind[p], reason[p] = "movable", "keep-list: README.md is the folder landing page (the folder may move)"
        elif not is_md[p]:
            kind[p], reason[p] = "movable", "tooling or archival file: name kept (moves only with a renamed folder)"
        elif p in proper:
            kind[p], reason[p] = "movable", "language, command or product name stays"
        elif in_table:
            kind[p], reason[p] = "movable", "renamed"
        else:
            kind[p], reason[p] = "movable", "NEEDS NAME"
            problems.append(f"{p}: Markdown document has no row in {NAMES_PATH} (a human names it)")
        if in_table:
            if kind[p] == "pinned" and "reference closure" in reason[p]:
                notes.append(f"{p}: names-table row ignored ({reason[p]})")
            elif kind[p] == "pinned" or base == README:
                problems.append(f"{p}: names-table row for a keep-list path ({reason[p]})")
        if p in proper and in_table:
            problems.append(f"{p}: listed both as proper name and as renamed")

    # ---- directories
    pinned_dirs: dict[str, str] = {}
    for p, k in kind.items():
        if k == "pinned":
            for a in ancestors(p):
                pinned_dirs.setdefault(a, f"holds pinned file {p}")
    for d in all_dirs:
        if any(d.startswith(t) for t in KEEP_TREES) or d + "/" in KEEP_TREES:
            pinned_dirs[d] = "keep-list tree " + next(t for t in KEEP_TREES if d.startswith(t) or d + "/" == t)
    for d in sorted(all_dirs):
        if d in m_frozen:
            pinned_dirs.setdefault(d, f"reference closure: {m_frozen[d]} (frozen) mentions it")
        elif open_ref(d + "/x"):
            pinned_dirs.setdefault(d, f"reference closure: {open_ref(d + '/x')[1]} (frozen) names a folder above it openly")
    dir_map: dict[str, str] = {}
    dir_reason: dict[str, str] = {}
    for d in sorted(all_dirs):
        if d in table_dirs:
            if d in pinned_dirs:
                notes.append(f"{d}/: names-table row ignored ({pinned_dirs[d]})")
                dir_map[d], dir_reason[d] = PurePosixPath(d).name, f"kept: {pinned_dirs[d]}"
            else:
                dir_map[d], dir_reason[d] = table_dirs[d], "renamed"
        else:
            dir_map[d] = PurePosixPath(d).name
            dir_reason[d] = f"kept: {pinned_dirs[d]}" if d in pinned_dirs else "kept: not student-facing or no Spanish name chosen"

    def map_dir(d: str) -> str:
        parts = d.split("/")
        return "/".join(dir_map["/".join(parts[:i + 1])] for i in range(len(parts)))

    result: dict[str, str] = {}
    for p in sorted(files):
        parent = str(PurePosixPath(p).parent)
        base = PurePosixPath(p).name
        if p in table_files and reason[p] == "renamed":
            base = table_files[p]
        new_parent = "" if parent == "." else map_dir(parent)
        result[p] = f"{new_parent}/{base}" if new_parent else base
        if result[p] != p and kind[p] == "movable" and reason[p] != "renamed":
            reason[p] += "; folder renamed"
        if result[p] != p and kind[p] == "pinned":
            problems.append(f"{p}: pinned path would move to {result[p]}")

    # ---- warnings: basenames a frozen file mentions, workflow references to rewrite
    base_mentions: dict[str, str] = {}
    for src, text in frozen_src:
        for tok, _ in tokens(text):
            base_mentions.setdefault(tok.split("/")[-1], src)
    for p in sorted(files):
        base = PurePosixPath(p).name
        if result[p] != p and base != README and base in base_mentions and "/" in p:
            warnings.append(f"{p}: file name {base} appears in frozen {base_mentions[base]} (check it is not a path)")
    rewrites = sorted({(src, tok) for src, text in workflow_src for tok, _ in tokens(text)
                       if tok in result and result[tok] != tok})
    if glossary is not None:
        unknown: dict[str, list[str]] = {}
        for p in sorted(files):
            if reason[p] != "renamed":
                continue
            comps = [PurePosixPath(result[p]).stem]
            for d in ancestors(p):
                if d in table_dirs and dir_reason[d] == "renamed":
                    comps.append(table_dirs[d])
            for c in comps:
                for w in re.split(r"[-.]", c.lower()):
                    if w and not w.isdigit() and w not in FUNCTION_WORDS | PROPER_WORDS and w not in glossary:
                        unknown.setdefault(w, []).append(p)
        for w in sorted(unknown):
            warnings.append(f"word '{w}' in a Spanish path is not in the glossary (P3B-002 adds it): {unknown[w][0]}")

    problems += validate(files, result, (frozen_src, workflow_src))
    return {"map": result, "reasons": reason, "dir_map": dir_map, "dir_reasons": dir_reason,
            "problems": problems, "notes": notes, "warnings": warnings, "kinds": kind,
            "workflow_rewrites": rewrites, "pinned_mentions": m_frozen}


def validate(files: dict[str, str], result: dict[str, str], read_sources) -> list[str]:
    """Checks that hold for ANY map (also a hand-made one): one-to-one, no collisions, keep-list names
    untouched, frozen files untouched, no frozen file mentions a renamed path, name syntax."""
    problems: list[str] = []
    frozen_src, workflow_src = read_sources
    for p in files:
        if p not in result:
            problems.append(f"{p}: missing from the map")
    for p in result:
        if p not in files:
            problems.append(f"{p}: map entry for a path that is not in the tree")
    seen: dict[str, str] = {}
    for p, q in sorted(result.items()):
        key = q.casefold()
        if key in seen:
            problems.append(f"collision: {seen[key]} and {p} both map to {q}")
        seen.setdefault(key, p)
    # a folder and a file may not share a name either
    dirs_out = {d.casefold() for q in result.values() for d in ancestors(q)}
    for q in result.values():
        if q.casefold() in dirs_out:
            problems.append(f"collision: {q} is both a file and a folder")
    renamed = {p: q for p, q in result.items() if p in files and p != q}
    for p, q in sorted(renamed.items()):
        base, qbase = PurePosixPath(p).name, PurePosixPath(q).name
        if files[p] == "frozen":
            problems.append(f"{p}: frozen file renamed to {q}")
        if base in HARD_KEEP_NAMES and base != README:
            problems.append(f"{p}: keep-list name renamed to {q}")
        if base == README and qbase != README:
            problems.append(f"{p}: README.md renamed to {q}")
        if p.startswith(HARD_KEEP_PREFIXES) or any(p.startswith(t) for t in KEEP_TREES):
            problems.append(f"{p}: path inside a keep-list tree renamed to {q}")
        old_parts, new_parts = p.split("/"), q.split("/")
        if len(old_parts) != len(new_parts):
            problems.append(f"{p}: depth changes ({q})")
            continue
        for o, n in zip(old_parts, new_parts):
            if o == n:
                continue
            if not (COMP_RE.match(n) or CAPS_RE.match(n)):
                problems.append(f"{q}: component '{n}' is not ASCII lowercase kebab-case (or ALL-CAPS name)")
            if "." in o and o.rsplit(".", 1)[-1] != n.rsplit(".", 1)[-1] and o == old_parts[-1]:
                problems.append(f"{p}: extension changes ({q})")
            mo, mn = NUM_PREFIX_RE.match(o), NUM_PREFIX_RE.match(n)
            if (mo.group(1) if mo else None) != (mn.group(1) if mn else None):
                problems.append(f"{p}: numeric prefix changes ({q})")
    # I19: no frozen file mentions a renamed path (file or folder)
    open_frozen: dict[str, str] = {}
    m = mention_index(frozen_src, open_frozen)
    for p in sorted(renamed):
        for d, src in open_frozen.items():
            if p.startswith(d + "/") and p not in m:
                problems.append(f"{p}: renamed, but frozen file {src} names the folder {d}/ openly")
    renamed_dirs = {d for p, q in renamed.items() for d, nd in
                    zip(ancestors(p), ancestors(q)) if d.split("/")[-1] != nd.split("/")[-1]}
    for p in sorted(renamed):
        if p in m:
            problems.append(f"{p}: renamed, but frozen file {m[p]} mentions it")
    for d in sorted(renamed_dirs):
        if d in m:
            problems.append(f"{d}/: renamed, but frozen file {m[d]} mentions it")
    mw = mention_index(workflow_src)
    for p in sorted(renamed):
        if p.endswith(".md") and files.get(p) in ("authored", "generated") and p in mw and p not in m:
            problems.append(f"{p}: renamed, but workflow {mw[p]} mentions it")
    return problems


# ------------------------------------------------------------------ files

def load_tree(root: str) -> tuple[dict[str, str], object]:
    files = {}
    for f in inventory.list_files(root):
        cls = inventory.classify(f)[0]
        if cls != "owned":
            files[f] = cls

    def read(p: str):
        try:
            with open(os.path.join(root, p), "rb") as fh:
                data = fh.read()
        except OSError:
            return None
        return data.decode("utf-8", "replace") if is_text(data) else None

    return files, read


def dump_map(result: dict[str, str]) -> str:
    import json
    lines = ["# translation/path-map.yaml: English path -> Spanish path (generated by tools/pathmap.py; do not edit).",
             "# The English path is the canonical key everywhere (PO files, ledger, locked-code.sha256, anchors.json).",
             "# A path that maps to itself must stay (see translation/path-map-report.md for the reason).",
             "schema: 1", "paths:"]
    for p in sorted(result):
        lines.append(f"  {json.dumps(p, ensure_ascii=False)}: {json.dumps(result[p], ensure_ascii=False)}")
    return "\n".join(lines) + "\n"


def dump_report(files: dict[str, str], res: dict) -> str:
    out = ["# translation/path-map-report.md: renamed and kept paths (generated by tools/pathmap.py; do not edit)", ""]
    result, reasons = res["map"], res["reasons"]
    renamed = [p for p in sorted(files) if result[p] != p]
    kept = [p for p in sorted(files) if result[p] == p]
    out += ["## Summary", "",
            f"- English paths in the map: {len(files)}",
            f"- Renamed (file or folder): {len(renamed)}",
            f"- Kept: {len(kept)}",
            f"- Folders renamed: {sum(1 for d, n in res['dir_map'].items() if n != d.split('/')[-1])}",
            f"- Problems: {len(res['problems'])}", ""]
    out += ["## Folders", "", "| English folder | Spanish name | Reason |", "| --- | --- | --- |"]
    for d in sorted(res["dir_map"]):
        if d.startswith(("src/", "sandbox/", "gradle/")):
            continue
        out.append(f"| `{d}` | `{res['dir_map'][d]}` | {res['dir_reasons'][d]} |")
    out.append("")
    out.append("Folders below `src/`, `sandbox/` and `gradle/` are kept (frozen trees) and are not listed one by one.")
    out += ["", "## Every English path", "", "| English path | Spanish path | Status | Reason |", "| --- | --- | --- | --- |"]
    for p in sorted(files):
        st = "renamed" if result[p] != p else "kept"
        sp = f"`{result[p]}`" if result[p] != p else "(same)"
        out.append(f"| `{p}` | {sp} | {st} | {reasons[p]} |")
    out += [""]
    if res["notes"]:
        out += ["## Notes", ""] + [f"- {n}" for n in res["notes"]] + [""]
    if res["warnings"]:
        out += ["## Warnings", ""] + [f"- {w}" for w in res["warnings"]] + [""]
    if res["workflow_rewrites"]:
        out += ["## Workflow references to rewrite in P3B-005", ""]
        out += [f"- `{s}` mentions `{p}`" for s, p in res["workflow_rewrites"]] + [""]
    if res["problems"]:
        out += ["## Problems", ""] + [f"- {p}" for p in res["problems"]] + [""]
    return "\n".join(out)


CATALOG_FILES = {"en": "lessons/book/locale/en.yaml", "es": "lessons/book/locale/es.yaml"}
CATALOG_BEGIN = "# BEGIN GENERATED paths (tools/pathmap.py --write; do not edit by hand)"
CATALOG_END = "# END GENERATED paths"
CATALOG_LAYOUT = "layout"


def catalog_tables(result: dict[str, str]) -> tuple[dict[str, str], dict[str, str]]:
    """(dirs, files): the renamed entries only, English path -> Spanish path. A folder is renamed when the
    ancestor at the same depth differs; every file of the folder must agree (else a ValueError)."""
    files = {p: n for p, n in sorted(result.items()) if p != n}
    dirs: dict[str, str] = {}
    for p, n in files.items():
        pp, np_ = p.split("/"), n.split("/")
        if len(pp) != len(np_):
            raise ValueError(f"{p} -> {n}: a rename may not change the folder depth")
        for i in range(1, len(pp)):
            a, b = "/".join(pp[:i]), "/".join(np_[:i])
            if a != b and dirs.setdefault(a, b) != b:
                raise ValueError(f"folder {a} maps to both {dirs[a]} and {b}")
    return dict(sorted(dirs.items())), files


def catalog_block(result: dict[str, str], lang: str, layout: str) -> str:
    """The generated `paths:` block of a locale catalog. English is the identity map (same keys, same values)."""
    import json
    dirs, files = catalog_tables(result)
    q = lambda v: json.dumps(v, ensure_ascii=False)
    lines = [CATALOG_BEGIN, "paths:", f'  {CATALOG_LAYOUT}: {q(layout)}', "  dirs:"]
    lines += [f"    {q(k)}: {q(k if lang == 'en' else v)}" for k, v in dirs.items()]
    lines.append("  files:")
    lines += [f"    {q(k)}: {q(k if lang == 'en' else v)}" for k, v in files.items()]
    lines.append(CATALOG_END)
    return "\n".join(lines) + "\n"


def catalog_text(root: str, lang: str, result: dict[str, str]) -> str:
    """The catalog file with its generated paths block (re)built. The layout value is kept as it is in the file."""
    text = read_own(root, CATALOG_FILES[lang])
    m = re.search(re.escape(CATALOG_BEGIN) + r".*?" + re.escape(CATALOG_END) + r"\n", text, re.S)
    layout = "english"
    if m:
        lm = re.search(r'^  layout: "(\w+)"', m.group(0), re.M)
        layout = lm.group(1) if lm else layout
    block = catalog_block(result, lang, layout)
    if m:
        return text[:m.start()] + block + text[m.end():]
    return text.rstrip("\n") + "\n\n" + block


def read_own(root: str, rel: str) -> str:
    with open(os.path.join(root, rel), encoding="utf-8") as fh:
        return fh.read()


def compute(root: str) -> tuple[dict[str, str], dict]:
    files, read = load_tree(root)
    names = load_names(read_own(root, NAMES_PATH))
    gloss = glossary_words(read_own(root, GLOSSARY_PATH))
    res = build(files, read, names, gloss)
    for must in EXPECTED_PINNED:
        if must not in res["pinned_mentions"] and not (must in res["map"] and res["map"][must] == must):
            res["problems"].append(f"expected pinned path {must} is not kept: the closure scan lost a reference")
        elif must in res["map"] and res["map"][must] != must:
            res["problems"].append(f"expected pinned path {must} would be renamed")
    for must in ("lessons", "lessons/cs-source/concepts"):
        for d, n in res["dir_map"].items():
            if d == must and n != must.split("/")[-1]:
                res["problems"].append(f"expected pinned folder {must} would be renamed")
    return files, res


def main(argv: list[str] | None = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    files, res = compute(ROOT)
    n_ren = sum(1 for p in files if res["map"][p] != p)
    print(f"pathmap: {len(files)} paths, {n_ren} renamed, {len(files) - n_ren} kept, "
          f"{len(res['problems'])} problem(s), {len(res['warnings'])} warning(s)")
    for p in res["problems"]:
        print(f"PROBLEM {p}")
    if "--write" in argv:
        with open(os.path.join(ROOT, MAP_PATH), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dump_map(res["map"]))
        with open(os.path.join(ROOT, REPORT_PATH), "w", encoding="utf-8", newline="\n") as fh:
            fh.write(dump_report(files, res))
        for lang, rel in CATALOG_FILES.items():
            text = catalog_text(ROOT, lang, res["map"])      # read before the file is opened for writing
            with open(os.path.join(ROOT, rel), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(text)
        print(f"wrote {MAP_PATH}, {REPORT_PATH} and the paths block of both locale catalogs")
        return 1 if res["problems"] else 0
    if "--check" in argv:
        bad = bool(res["problems"])
        for rel, want in ((MAP_PATH, dump_map(res["map"])), (REPORT_PATH, dump_report(files, res)),
                          *((c, catalog_text(ROOT, l, res["map"])) for l, c in CATALOG_FILES.items())):
            try:
                have = read_own(ROOT, rel)
            except OSError:
                have = None
            if have != want:
                print(f"STALE {rel}: run python3 tools/pathmap.py --write")
                bad = True
        report = read_own(ROOT, REPORT_PATH) if os.path.exists(os.path.join(ROOT, REPORT_PATH)) else ""
        for p in files:
            if f"| `{p}` |" not in report:
                print(f"MISSING from report: {p}")
                bad = True
        print("pathmap --check:", "FAIL" if bad else "ok")
        return 1 if bad else 0
    return 1 if res["problems"] else 0


if __name__ == "__main__":
    sys.exit(main())
