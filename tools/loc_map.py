#!/usr/bin/env python3
"""Identifier ledger validator (Part II, plan 4.5.5, task S2-001).

The ledger is translation/identifier-map.jsonl: one JSON object per renamed symbol.

Schema (all fields required, no extras):
  language   str   a language with an `extracted` record in translation/protected-tokens/tokens.jsonl
  entry      str   entry (book chapter or program) the symbol belongs to
  path       str   protected file the rename touches; must be in code-inventory.jsonl
  old, new   str   identifier spellings; must differ
  role       str   one of ROLES
  scope      str   binding scope: "file", "module", or "<kind>:<name>" with kind in SCOPE_KINDS
  evidence   list  non-empty; each item is a path under translation/part2/reports/ (oracle report)
  approver   str   non-empty

Rules (fail closed):
  1. The file's family must be `localizing` in translation/localization-scope.yaml and not `never`.
  2. The language must be extracted; a not-extracted language cannot prove collision-freedom.
  3. `new` must not be a registry token for that language, nor a Python builtin (python), compared
     case-folded for case-insensitive languages.
  4. Within one (path, scope), `old` is renamed once and `new` is not used twice, and `new` is not
     the `old` of another entry in the same (path, scope) (a swap hides a collision).
  5. `new` must look like an identifier (letters, digits, underscore; not starting with a digit).

Usage:
  python3 -I tools/loc_map.py --check [--map FILE]
"""
import builtins
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MAP = os.path.join(ROOT, "translation", "identifier-map.jsonl")
TOKENS = os.path.join(ROOT, "translation", "protected-tokens", "tokens.jsonl")
SCOPE = os.path.join(ROOT, "translation", "localization-scope.yaml")
INVENTORY = os.path.join(ROOT, "translation", "part2", "code-inventory.jsonl")
REPORTS = "translation/part2/reports/"

FIELDS = ("language", "entry", "path", "old", "new", "role", "scope", "evidence", "approver")
ROLES = ("variable", "function", "type", "constant", "parameter", "field", "label", "macro", "module")
SCOPE_KINDS = ("function", "class", "block", "paragraph", "section", "rule", "target", "namespace")
CASE_INSENSITIVE = {"cobol", "batch", "basic", "sql", "ed", "ex", "makefile"}
IDENT = re.compile(r"^[^\W\d]\w*$", re.UNICODE)
SCOPE_RE = re.compile(r"^(file|module|(%s):[^\s:][^\s]*)$" % "|".join(SCOPE_KINDS))


def load_jsonl(path):
    out = []
    if not os.path.exists(path):
        return out
    with open(path, encoding="utf-8") as fh:
        for n, line in enumerate(fh, 1):
            if line.strip():
                try:
                    out.append(json.loads(line))
                except ValueError as exc:
                    out.append({"__bad__": "line %d: %s" % (n, exc)})
    return out


def load_scope(path=SCOPE):
    """family -> {'status': str, 'never': bool}, parsed without a YAML dependency."""
    fams = {}
    row = re.compile(r'^\s+"([^"]+)":\s*\{(.*)\}\s*$')
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            m = row.match(line)
            if not m:
                continue
            body = m.group(2)
            st = re.search(r"status:\s*(\w+)", body)
            fams[m.group(1)] = {"status": st.group(1) if st else "frozen",
                                "never": "never: true" in body}
    return fams


def load_families(path=INVENTORY):
    return {r["path"]: r["family"] for r in load_jsonl(path) if "path" in r}


def load_tokens(path=TOKENS):
    reg = {}
    for r in load_jsonl(path):
        if "language" in r:
            reg[r["language"]] = r
    return reg


def reserved_names(language, reg):
    rec = reg.get(language)
    names = {t["token"] for t in rec["tokens"]} if rec else set()
    if language == "python":
        names |= set(dir(builtins))
    return names


def validate(records, scope=None, families=None, reg=None):
    """Return a list of error strings; empty means the ledger is valid."""
    scope = load_scope() if scope is None else scope
    families = load_families() if families is None else families
    reg = load_tokens() if reg is None else reg
    errs = []
    seen_new = {}
    seen_old = {}
    for i, r in enumerate(records, 1):
        tag = "record %d" % i
        if "__bad__" in r:
            errs.append("%s: invalid JSON (%s)" % (tag, r["__bad__"]))
            continue
        missing = [f for f in FIELDS if f not in r]
        extra = [k for k in r if k not in FIELDS]
        if missing or extra:
            errs.append("%s: missing %s extra %s" % (tag, missing, extra))
            continue
        bad = [f for f in FIELDS if f != "evidence" and not (isinstance(r[f], str) and r[f].strip())]
        if bad:
            errs.append("%s: empty or non-string field(s) %s" % (tag, bad))
            continue
        lang, path, old, new = r["language"], r["path"], r["old"], r["new"]
        if old == new:
            errs.append("%s: old and new are identical (%s)" % (tag, old))
        if not IDENT.match(new):
            errs.append("%s: new name %r is not an identifier" % (tag, new))
        if r["role"] not in ROLES:
            errs.append("%s: unknown role %r" % (tag, r["role"]))
        if not SCOPE_RE.match(r["scope"]):
            errs.append("%s: unscoped or malformed binding scope %r" % (tag, r["scope"]))
        ev = r["evidence"]
        if not (isinstance(ev, list) and ev and all(isinstance(e, str) and e.startswith(REPORTS)
                                                    and e.endswith(".md") for e in ev)):
            errs.append("%s: evidence must be a non-empty list of %s*.md reports" % (tag, REPORTS))
        fam = families.get(path)
        if fam is None:
            errs.append("%s: path %s is not a protected file in the inventory" % (tag, path))
        else:
            row = scope.get(fam)
            if row is None or row["status"] != "localizing" or row["never"]:
                errs.append("%s: family %s of %s is not localizing in the scope file" % (tag, fam, path))
        rec = reg.get(lang)
        if rec is None or rec.get("status") != "extracted":
            errs.append("%s: language %s has no extracted token registry; collision cannot be checked"
                        % (tag, lang))
        else:
            fold = lang in CASE_INSENSITIVE
            names = reserved_names(lang, reg)
            probe = new.casefold() if fold else new
            pool = {n.casefold() for n in names} if fold else names
            if probe in pool:
                errs.append("%s: new name %r collides with a protected token or built-in of %s"
                            % (tag, new, lang))
        key = (path, r["scope"])
        k_new = new.casefold() if lang in CASE_INSENSITIVE else new
        if (key, k_new) in seen_new:
            errs.append("%s: new name %r already used in %s %s (record %d)"
                        % (tag, new, path, r["scope"], seen_new[(key, k_new)]))
        seen_new.setdefault((key, k_new), i)
        if (key, old) in seen_old:
            errs.append("%s: old name %r renamed twice in %s %s" % (tag, old, path, r["scope"]))
        seen_old.setdefault((key, old), i)
    for (key, k_new), i in seen_new.items():
        if (key, k_new) in seen_old and seen_old[(key, k_new)] != i:
            errs.append("record %d: new name %r is the old name of record %d in the same scope"
                        % (i, k_new, seen_old[(key, k_new)]))
    return errs


def main(argv):
    path = MAP
    if "--map" in argv:
        path = argv[argv.index("--map") + 1]
    if "--check" not in argv:
        print(__doc__)
        return 2
    records = load_jsonl(path)
    errs = validate(records)
    for e in errs:
        print("loc_map: " + e)
    print("loc_map: %d record(s), %d error(s)" % (len(records), len(errs)))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
