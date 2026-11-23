#!/usr/bin/env python3
"""tools/impact.py: release-impact map for the cookbook (plan 12, step 5; task S8-003).

Given the English tree of the old release and of the new one, it says which English units changed,
which Spanish units answer to them, what depends on them, and which gates the change reaches. It
never assumes that paths or hashes are equal across the two repos: translation/source-map.jsonl
joins them.

A *unit* is a Markdown section (`path#heading-slug`, `path#` for the text before the first
heading) or a whole non-Markdown file (`path`). Records:

  translation/source-map.jsonl   one row per unit:
      {en_path, en_unit, en_hash, es_path, es_unit, es_hash, note?}
      es_path comes from translation/path-map.yaml, so a renamed path is recorded both ways.
  translation/manifest.json      {"schema": 1, "files": {en_path: {class, sha256, es_path}}}
  translation/reports/impact-<release>.json   the impact map (see `impact`).

Rules worth knowing:
  * A change that only touches a GENERATED English file (lessons/cs/*.md) is traced back to its
    authored source (lessons/cs-source/...). It is regenerated, never translated.
  * Localized code is never overlaid. A changed code file (or a vanished mapped identifier) asks for a
    three-way reconcile and an oracle re-run for its family.
  * Unchanged units reuse the Spanish text with no model call; only changed prose is scheduled.

Usage:
  python3 tools/impact.py --build --en DIR --es DIR     write source-map.jsonl and manifest.json
  python3 tools/impact.py --old DIR --new DIR --release NAME [--write]
                                                          print (or write) the impact map
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from collections import deque
from posixpath import dirname, normpath

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import inventory  # noqa: E402

ROOT = os.path.dirname(HERE)
SCHEMA = 1
HEADING = re.compile(r"^(#{1,6})\s+(.*?)\s*#*\s*$")
FENCE = re.compile(r"^\s*(```+|~~~+)")
LINK = re.compile(r"\]\(([^)\s#]+\.md)(?:#[^)]*)?\)")
SKIP_DIRS = {".git"}


# ---------------------------------------------------------------- units

def slug(text: str) -> str:
    s = re.sub(r"[`*_\[\]()]", "", text.lower())
    s = re.sub(r"[^\w\s-]", "", s, flags=re.UNICODE)
    return re.sub(r"\s+", "-", s.strip())


def sha(data) -> str:
    if isinstance(data, str):
        data = data.encode("utf-8")
    return hashlib.sha256(data).hexdigest()


def norm_text(text: str) -> str:
    return "\n".join(l.rstrip() for l in text.replace("\r\n", "\n").strip("\n").split("\n"))


def md_sections(text: str) -> list[tuple[str, str]]:
    """[(slug, section text)]: slug '' for the preamble; duplicate slugs get -2, -3..."""
    sections: list[list] = [["", []]]
    fence = None
    for line in text.replace("\r\n", "\n").split("\n"):
        m = FENCE.match(line)
        if m:
            tok = m.group(1)[0]
            fence = None if fence == tok else (fence or tok)
        h = None if fence else HEADING.match(line)
        if h:
            sections.append([slug(h.group(2)), [line]])
        else:
            sections[-1][1].append(line)
    seen: dict[str, int] = {}
    out = []
    for s, lines in sections:
        n = seen.get(s, 0) + 1
        seen[s] = n
        out.append((s if n == 1 else "%s-%d" % (s, n), "\n".join(lines)))
    if out and out[0][0] == "" and not out[0][1].strip() and len(out) > 1:
        pass  # keep the empty preamble: it keeps positions aligned across languages
    return out


def units(path: str, data: bytes) -> list[dict]:
    """Units of one file: {unit, hash, text?}. Markdown splits by section; anything else is one unit."""
    if path.endswith(".md"):
        text = data.decode("utf-8", "replace")
        return [{"unit": "%s#%s" % (path, s), "hash": sha(norm_text(t)), "text": t}
                for s, t in md_sections(text)]
    return [{"unit": path, "hash": sha(data)}]


# ---------------------------------------------------------------- reading trees

def read_tree(root: str) -> dict[str, bytes]:
    files = {}
    for dp, dn, fn in os.walk(root):
        dn[:] = [d for d in dn if d not in SKIP_DIRS]
        for f in fn:
            p = os.path.join(dp, f)
            if os.path.isfile(p):
                files[os.path.relpath(p, root).replace(os.sep, "/")] = open(p, "rb").read()
    return files


def read_path_map(path: str) -> dict[str, str]:
    out = {}
    if os.path.exists(path):
        for l in open(path, encoding="utf-8"):
            m = re.match(r'^\s+"(.+?)":\s*"(.+?)"\s*$', l)
            if m:
                out[m.group(1)] = m.group(2)
    return out


def read_jsonl(path: str) -> list[dict]:
    if not os.path.exists(path):
        return []
    return [json.loads(l) for l in open(path, encoding="utf-8") if l.strip()]


# ---------------------------------------------------------------- source map and manifest

def build_source_map(en: dict[str, bytes], es: dict[str, bytes], path_map: dict[str, str]) -> list[dict]:
    """Join English units to Spanish units. Sections pair by position (headings differ in language);
    if the section counts differ the file pairs as one unit and says so."""
    rows = []
    for p in sorted(en):
        esp = path_map.get(p, p)
        eu = units(p, en[p])
        if esp not in es:
            rows += [{"en_path": p, "en_unit": u["unit"], "en_hash": u["hash"], "es_path": esp,
                      "es_unit": None, "es_hash": None, "note": "missing-in-spanish"} for u in eu]
            continue
        su = units(esp, es[esp])
        if len(eu) == len(su):
            for a, b in zip(eu, su):
                rows.append({"en_path": p, "en_unit": a["unit"], "en_hash": a["hash"], "es_path": esp,
                             "es_unit": b["unit"], "es_hash": b["hash"]})
        else:
            rows.append({"en_path": p, "en_unit": p + "#*", "en_hash": sha(en[p]), "es_path": esp,
                         "es_unit": esp + "#*", "es_hash": sha(es[esp]), "note": "sections-differ"})
    return rows


def build_manifest(en: dict[str, bytes], path_map: dict[str, str]) -> dict:
    files = {}
    for p in sorted(en):
        cls = inventory.classify(p)[0]
        files[p] = {"class": cls, "sha256": sha(en[p]), "es_path": path_map.get(p, p)}
    return {"schema": SCHEMA, "files": files}


def dump_jsonl(rows: list[dict]) -> str:
    return "".join(json.dumps(r, sort_keys=True, ensure_ascii=False) + "\n" for r in rows)


# ---------------------------------------------------------------- delta

def family_of(path: str) -> str | None:
    m = re.match(r"^(src/[^/]+)/", path) or re.match(r"^(lessons/solutions/[^/]+)/", path)
    return m.group(1) if m else None


def is_generated(path: str) -> bool:
    return inventory.classify(path)[0] == "generated"


def link_graph(files: dict[str, bytes]) -> dict[str, set[str]]:
    """Reverse links: target path -> set of Markdown files that link to it."""
    rev: dict[str, set[str]] = {}
    for p, data in files.items():
        if not p.endswith(".md"):
            continue
        for t in LINK.findall(data.decode("utf-8", "replace")):
            if "://" in t:
                continue
            tgt = normpath(dirname(p) + "/" + t) if not t.startswith("/") else t.lstrip("/")
            rev.setdefault(tgt, set()).add(p)
    return rev


def has_mermaid(text: str) -> bool:
    return "```mermaid" in text


def diff_trees(old: dict[str, bytes], new: dict[str, bytes]) -> dict:
    """Changed units between two English trees. A deleted file whose bytes equal an added file's is a rename."""
    added = sorted(set(new) - set(old))
    deleted = sorted(set(old) - set(new))
    by_hash = {sha(old[d]): d for d in deleted}
    renames = {}
    for a in list(added):
        h = sha(new[a])
        if h in by_hash:
            renames[by_hash[h]] = a
    r_new = set(renames.values())
    added = [a for a in added if a not in r_new]
    deleted = [d for d in deleted if d not in renames]
    changed = []
    for p in sorted(set(old) & set(new)):
        if old[p] == new[p]:
            continue
        ou = {u["unit"]: u for u in units(p, old[p])}
        nu = {u["unit"]: u for u in units(p, new[p])}
        for k in sorted(set(ou) | set(nu)):
            if k not in nu:
                changed.append({"path": p, "unit": k, "kind": "removed", "text": ou[k].get("text", "")})
            elif k not in ou:
                changed.append({"path": p, "unit": k, "kind": "added", "text": nu[k].get("text", "")})
            elif ou[k]["hash"] != nu[k]["hash"]:
                changed.append({"path": p, "unit": k, "kind": "changed", "text": nu[k].get("text", ""),
                                "old_text": ou[k].get("text", "")})
    return {"added": added, "deleted": deleted, "renamed": renames, "changed": changed}


def whole_file_units(path: str, data: bytes) -> list[str]:
    """Unit ids of an added or deleted file; an empty Markdown preamble carries no text, so it is skipped."""
    us = units(path, data)
    return [u["unit"] for u in us if not (path.endswith(".md") and u["unit"].endswith("#") and not u["text"].strip())] or [path]


def classify_change(path: str, ch: dict | None = None) -> str:
    cls = inventory.classify(path)[0]
    if cls == "generated":
        return "generated"
    if cls == "frozen":
        return "code"
    if cls == "tooling":
        return "tooling"
    if cls == "archival":
        return "archival"
    if ch and (has_mermaid(ch.get("text", "")) or has_mermaid(ch.get("old_text", ""))):
        return "diagram"
    return "prose"


GATES = {
    "prose": ["invariants", "review"],
    "diagram": ["invariants", "mermaid", "review"],
    "code": ["lock", "oracle", "part2_inv"],
    "tooling": ["locale_check", "book"],
    "generated": ["generate", "invariants"],
    "archival": ["book"],
}


def trace_generated(path: str, new: dict[str, bytes], old: dict[str, bytes], changed_paths: set[str]) -> list[str]:
    """The authored sources of a generated lessons/cs/X.md: the cs-source file of the same stem if it exists,
    else every cs-source file (the generator reads them all)."""
    stem = os.path.basename(path)
    sources = sorted(p for p in set(new) | set(old) if p.startswith("lessons/cs-source/"))
    same = [p for p in sources if p.endswith("/" + stem)]
    return same or sources


def impact(old: dict[str, bytes], new: dict[str, bytes], source_map: list[dict],
           ident_rows: list[dict] | None = None, release: str = "",
           path_map: dict[str, str] | None = None) -> dict:
    ident_rows = ident_rows or []
    d = diff_trees(old, new)
    smap = {r["en_unit"]: r for r in source_map}
    rev = link_graph(new)
    changed_paths = {c["path"] for c in d["changed"]} | set(d["added"]) | set(d["deleted"]) | set(d["renamed"])
    tr_units, items = [], []
    reuse = sum(1 for r in source_map if r.get("es_hash") and r["en_unit"].split("#")[0] not in changed_paths)

    def dependents(path: str) -> list[str]:
        seen, q, out = {path}, deque([path]), []
        while q:
            cur = q.popleft()
            for n in sorted(rev.get(cur, ())):
                if n not in seen:
                    seen.add(n)
                    out.append(n)
                    q.append(n)
        if path.startswith(("lessons/cs-source/", "src/", "lessons/languages/")) and path.endswith(".md"):
            out += [g for g in sorted(new) if is_generated(g) and g not in seen]
        return sorted(set(out))

    def add(path, unit, kind, change, ch=None, extra=None):
        gen_only = change == "generated"
        e = {"en_path": path, "en_unit": unit, "kind": kind, "change": change,
             "es_path": (smap.get(unit) or {}).get("es_path") or path_for(path),
             "es_unit": (smap.get(unit) or {}).get("es_unit"),
             "dependents": dependents(path), "gates": list(GATES[change])}
        if gen_only:
            e["generated_only"] = True
            e["traced_to"] = trace_generated(path, new, old, changed_paths)
            e["action"] = "regenerate; never translate"
        elif change == "prose" or change == "diagram":
            e["action"] = "translate-minimal-edit" if kind == "changed" and e["es_unit"] else "translate-new" \
                if kind == "added" else "remove-or-obsolete"
            if kind not in ("removed", "renamed"):
                tr_units.append(unit)
        elif change == "code":
            e["action"] = "three-way-reconcile; oracle re-run" if family_of(path) else "overlay"
            if family_of(path):
                e["oracle_family"] = family_of(path)
        else:
            e["action"] = "port-tooling-diff"
        if kind in ("added", "removed") or (ch and ch.get("kind") != "changed"):
            if path.endswith(".md"):
                e["gates"] = sorted(set(e["gates"]) | {"link_audit"})  # an anchor appeared or vanished
        if extra:
            e.update(extra)
        items.append(e)

    def path_for(p):
        return (path_map or {}).get(p, p)

    for ch in d["changed"]:
        kind = classify_change(ch["path"], ch)
        add(ch["path"], ch["unit"], ch["kind"], kind, ch)
    for p in d["added"]:
        for u in whole_file_units(p, new[p]):
            add(p, u, "added", classify_change(p, {"text": new[p].decode("utf-8", "replace")}))
    for p in d["deleted"]:
        for u in whole_file_units(p, old[p]):
            add(p, u, "removed", classify_change(p, {"text": old[p].decode("utf-8", "replace")}))
    for o, n in sorted(d["renamed"].items()):
        add(n, n, "renamed", classify_change(n), extra={"renamed_from": o, "action": "rename-spanish-path",
                                                          "gates": ["pathcheck", "link_audit"]})
    # symbols: a mapped English identifier that vanished from a changed file
    symbols = []
    for r in ident_rows:
        p = r.get("path")
        if p in new and p in old and old[p] != new[p]:
            if r["old"] in old[p].decode("utf-8", "replace") and r["old"] not in new[p].decode("utf-8", "replace"):
                symbols.append({"path": p, "english": r["old"], "spanish": r["new"],
                                "action": "re-evaluate identifier; update ledger"})
        elif p in old and p not in new and p not in d["renamed"]:
            symbols.append({"path": p, "english": r["old"], "spanish": r["new"], "action": "file gone; retire ledger row"})
    for s in symbols:
        for e in items:
            if e["en_path"] == s["path"] and "ledger" not in e["gates"]:
                e["gates"].append("ledger")
    gates = sorted({g for e in items for g in e["gates"]} | ({"verify_fast"} if items else set()))
    return {"schema": SCHEMA, "release": release, "units": items, "symbols": symbols,
            "translate_units": sorted(set(tr_units)), "model_calls_needed": len(set(tr_units)),
            "reused_spanish_units": reuse, "gates": gates,
            "oracle_families": sorted({e["oracle_family"] for e in items if "oracle_family" in e})}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--build", action="store_true")
    ap.add_argument("--en")
    ap.add_argument("--es")
    ap.add_argument("--old")
    ap.add_argument("--new")
    ap.add_argument("--release", default="")
    ap.add_argument("--write", action="store_true")
    a = ap.parse_args(argv)
    pm = read_path_map(os.path.join(ROOT, "translation", "path-map.yaml"))
    if a.build:
        if not (a.en and a.es):
            ap.error("--build needs --en and --es")
        en, es = read_tree(a.en), read_tree(a.es)
        rows = build_source_map(en, es, pm)
        open(os.path.join(ROOT, "translation", "source-map.jsonl"), "w", encoding="utf-8").write(dump_jsonl(rows))
        with open(os.path.join(ROOT, "translation", "manifest.json"), "w", encoding="utf-8") as fh:
            json.dump(build_manifest(en, pm), fh, indent=1, sort_keys=True, ensure_ascii=False)
            fh.write("\n")
        print("source-map: %d rows; manifest: %d files" % (len(rows), len(en)))
        return 0
    if not (a.old and a.new):
        ap.error("need --old and --new (or --build)")
    rep = impact(read_tree(a.old), read_tree(a.new),
                 read_jsonl(os.path.join(ROOT, "translation", "source-map.jsonl")),
                 read_jsonl(os.path.join(ROOT, "translation", "identifier-map.jsonl")), a.release, pm)
    text = json.dumps(rep, indent=1, sort_keys=True, ensure_ascii=False) + "\n"
    if a.write:
        out = os.path.join(ROOT, "translation", "reports", "impact-%s.json" % (a.release or "x"))
        open(out, "w", encoding="utf-8").write(text)
        print("wrote", out)
    else:
        print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
