#!/usr/bin/env python3
"""tools/dnt.py: generate translation/dnt.txt, the do-not-translate list (plan I8).

The list is derived from the frozen program sources (the files named in
translation/locked-code.sha256), never typed by hand. A phrase is DNT when the programs
print it, store it or read it, so the prose must quote it exactly. Four kinds:

  category    the four card categories; a whole string literal in at least MIN_ENTRIES
              different entries (src/<entry>, lessons/solutions/<entry>)
  marker      DEMO ONLY and the output markers the programs print ("# DEMO ONLY run",
              "# committed total=", "entries="): literals in at least MIN_ENTRIES entries
              that contain DEMO ONLY, start with "# ", or end with "="
  identifier  SQL schema names (demo_timecards, run_id, running_total ...) found inside
              SQL literals; ALL_CAPS environment variable names (XDG_DATA_HOME, NO_COLOR)
  path        file names such as demo-timecards.db

Only program sources are scanned (not check.sh, Dockerfiles or build files): their strings
are test plumbing, not the output contract. Output: one phrase per line, sorted, unique,
no comments (a phrase may start with "#").

Usage:
  python3 tools/dnt.py --write     write translation/dnt.txt
  python3 tools/dnt.py --check     exit 1 if translation/dnt.txt differs from a fresh build
  python3 tools/dnt.py --explain   print each phrase with its kind and entry count

Exit codes: 0 ok, 1 drift or a required phrase missing, 2 usage or environment error.
"""
from __future__ import annotations

import argparse
import os
import re
import sys

MANIFEST = "translation/locked-code.sha256"
OUTPUT = "translation/dnt.txt"
MIN_ENTRIES = 3

# Program source extensions. Shell, PowerShell, Dockerfiles and build files are excluded.
PROGRAM_EXTS = (
    ".awk", ".hs", ".java", ".kt", ".py", ".rs", ".go", ".apl", ".cob", ".fs", ".lisp",
    ".sql", ".tcl", ".cmake", ".ed", ".ex", ".m4", ".c", ".pl", ".sed", ".cs", ".mjs",
)

# Phrases the book depends on. Each must be found by the rules below; if one is not, the
# frozen sources changed or a rule broke, and the tool fails instead of writing a short list.
REQUIRED = ("Meetings", "Coding", "Debugging", "Learning", "DEMO ONLY")
CATEGORIES = ("Meetings", "Coding", "Debugging", "Learning")

LITERAL_RX = re.compile(r'"((?:[^"\\\n]|\\.)*)"|\'((?:[^\'\\\n]|\\.)*)\'')
ENV_RX = re.compile(r"^[A-Z][A-Z0-9]*(?:_[A-Z0-9]+)*$")
PATH_RX = re.compile(r"^[A-Za-z0-9][\w.-]*\.(?:db|sqlite|sqlite3)$")
SQL_RX = re.compile(r"\b(?:CREATE TABLE|INSERT INTO|SELECT|UPDATE|FROM|VALUES)\b", re.I)
SNAKE_RX = re.compile(r"\b[a-z][a-z0-9]*(?:_[a-z0-9]+)+\b")
SQL_KEYWORD_PAIRS = {"not_null", "primary_key", "foreign_key", "default_value"}


class DntError(Exception):
    pass


def repo_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def read_manifest_paths(root: str) -> list[str]:
    path = os.path.join(root, MANIFEST)
    try:
        with open(path, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
    except OSError as exc:
        raise DntError(f"cannot read {MANIFEST}: {exc}") from exc
    paths = []
    for line in lines:
        if not line.strip():
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2:
            raise DntError(f"bad manifest line: {line!r}")
        paths.append(parts[1].strip())
    return paths


def entry_of(path: str) -> str:
    """The entry a file belongs to: its first two path components."""
    return "/".join(path.split("/")[:2])


def is_program(path: str) -> bool:
    return path.endswith(PROGRAM_EXTS)


def literals(text: str):
    for m in LITERAL_RX.finditer(text):
        s = m.group(1) if m.group(1) is not None else m.group(2)
        if s:
            yield s


def collect(files: dict[str, str]) -> dict[str, set[str]]:
    """Map each string literal to the set of entries that contain it.

    files maps a repo path to its text. Non-program files are ignored.
    """
    seen: dict[str, set[str]] = {}
    for path, text in files.items():
        if not is_program(path):
            continue
        ent = entry_of(path)
        for s in literals(text):
            seen.setdefault(s, set()).add(ent)
    return seen


def classify_literal(s: str, n_entries: int) -> list[tuple[str, str]]:
    """Return (kind, phrase) pairs this literal contributes. Pure; used by build and tests."""
    out: list[tuple[str, str]] = []
    phrase = s.strip()
    if not phrase or "\n" in phrase or "\t" in phrase or "\\" in phrase:
        return out
    if n_entries >= MIN_ENTRIES:
        if phrase in CATEGORIES:
            out.append(("category", phrase))
        elif "DEMO ONLY" in phrase or phrase.startswith("# ") or phrase.endswith("="):
            if "$" not in phrase and "%" not in phrase and "'" not in phrase:
                out.append(("marker", phrase))
        if ENV_RX.match(phrase) and len(phrase) >= 4 and phrase not in ("NULL", "TRUE", "FALSE"):
            out.append(("identifier", phrase))
        if PATH_RX.match(phrase):
            out.append(("path", phrase))
    if SQL_RX.search(s) and n_entries >= 2:
        for tok in SNAKE_RX.findall(s):
            if tok not in SQL_KEYWORD_PAIRS:
                out.append(("identifier", tok))
    return out


def build(files: dict[str, str]) -> dict[str, tuple[str, int]]:
    """Return {phrase: (kind, entry_count)}. Raises DntError if a REQUIRED phrase is missing."""
    seen = collect(files)
    found: dict[str, tuple[str, int]] = {}
    for lit, ents in seen.items():
        for kind, phrase in classify_literal(lit, len(ents)):
            count = len(seen.get(phrase, ents))
            prev = found.get(phrase)
            if prev is None or count > prev[1]:
                found[phrase] = (kind, count)
    # "DEMO ONLY" is usually printed inside a longer literal; count entries that contain it.
    if "DEMO ONLY" not in found:
        ents = {e for lit, es in seen.items() if "DEMO ONLY" in lit for e in es}
        if len(ents) >= MIN_ENTRIES:
            found["DEMO ONLY"] = ("marker", len(ents))
    missing = [p for p in REQUIRED if p not in found]
    if missing:
        raise DntError("required DNT phrases not found in the frozen sources: " + ", ".join(missing))
    return found


def render(found: dict[str, tuple[str, int]]) -> str:
    return "".join(p + "\n" for p in sorted(found))


def load_files(root: str) -> dict[str, str]:
    files: dict[str, str] = {}
    for rel in read_manifest_paths(root):
        if not is_program(rel):
            continue
        full = os.path.join(root, rel)
        try:
            with open(full, encoding="utf-8", errors="replace", newline="") as fh:
                files[rel] = fh.read().replace("\r\n", "\n")
        except OSError as exc:
            raise DntError(f"cannot read frozen file {rel}: {exc}") from exc
    if not files:
        raise DntError("no program sources found in the manifest")
    return files


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--write", action="store_true")
    g.add_argument("--check", action="store_true")
    g.add_argument("--explain", action="store_true")
    ap.add_argument("--root", default=repo_root())
    args = ap.parse_args(argv)
    try:
        found = build(load_files(args.root))
    except DntError as exc:
        print(f"dnt: {exc}", file=sys.stderr)
        return 1 if "required DNT" in str(exc) else 2
    text = render(found)
    out = os.path.join(args.root, OUTPUT)
    if args.explain:
        for p in sorted(found):
            kind, n = found[p]
            print(f"{kind:10} {n:3}  {p}")
        return 0
    if args.write:
        with open(out, "w", encoding="utf-8", newline="\n") as fh:
            fh.write(text)
        print(f"dnt: wrote {OUTPUT} ({len(found)} phrases)")
        return 0
    try:
        with open(out, encoding="utf-8", newline="") as fh:
            current = fh.read()
    except OSError:
        print(f"dnt: {OUTPUT} is missing", file=sys.stderr)
        return 1
    if current != text:
        print(f"dnt: {OUTPUT} differs from a fresh build; run --write", file=sys.stderr)
        return 1
    print(f"dnt: {OUTPUT} is current ({len(found)} phrases)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
