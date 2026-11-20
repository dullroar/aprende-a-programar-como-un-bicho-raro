#!/usr/bin/env python3
"""tools/inventory.py: classify every file of the imported English tree and measure it.

Classes (every non-owned tracked file gets exactly one):
  frozen    non-Markdown content that must stay byte-identical (src/, lessons/solutions/,
            sandbox/, scripts, gradle files, LICENSE, ...). Default for any non-Markdown file.
  authored  hand-written Markdown (translated in place).
  generated Markdown produced by generators (lessons/cs/*.md). Never translated by hand.
  tooling   build code and metadata adapted through the locale layer (allowlist candidates).
  archival  built publications, images and PDFs/EPUBs kept or rebuilt, never hand-translated.
  owned     files this Spanish repo owns (loop/, translation/, tools/, ralph-kit-es/, the plan,
            .gitignore). They are not part of the English inventory and are skipped.

Usage:
  python3 tools/inventory.py            write translation/work/inventory.json
  python3 tools/inventory.py --check    recompute, verify invariants, compare with plan 5.1

--check exits 1 when: a file is unclassified or double-classified, the inventory file is
missing or stale, or the non-owned file set differs from the pinned English tree (when the
clone is reachable). Differences from the plan's section 5.1 numbers are printed as DIFF but
are informational: the plan says "re-measure in Phase 0".
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from pathlib import PurePosixPath

CLASSES = ("frozen", "authored", "generated", "tooling", "archival", "owned")

OWNED_PREFIXES = ("loop/", "translation/", "tools/", "ralph-kit-es/", ".claude/",
                  "tests/fixtures/", "lessons/book/locale/")
OWNED_FILES = {".gitignore", "requirements-es.txt"}
OWNED_GLOBS = (re.compile(r"^SYNTHESIZED-TRANSLATION-PLAN-.*\.md$"),)

# Tooling: adapted through the locale layer. Everything else non-Markdown is frozen.
TOOLING_PATTERNS = (
    re.compile(r"^lessons/book/[^/]+\.(py|yaml|yml|css|lua|txt|json)$"),
    re.compile(r"^lessons/curriculum/[^/]+\.(py|yaml|yml|txt)$"),
    re.compile(r"^lessons/study-guides/[^/]+\.(py|yaml|yml|txt)$"),
    re.compile(r"^\.github/workflows/[^/]+\.ya?ml$"),
)
ARCHIVAL_EXT = {".pdf", ".epub", ".png", ".jpg", ".jpeg", ".gif", ".svg"}

PROSE_FM_KEYS = {"title", "name", "teaches", "machine", "state", "applies-because",
                 "analogies", "counterexamples"}

FENCE_RE = re.compile(r"^\s*(`{3,}|~{3,})(.*)$")
BEGIN_GEN_RE = re.compile(r"<!--\s*BEGIN GENERATED\b")
END_GEN_RE = re.compile(r"<!--\s*END GENERATED\b")
HEADING_RE = re.compile(r"^ {0,3}(#{1,6})\s+\S")
CODE_SPAN_RE = re.compile(r"(`+)(.+?)\1")
LINK_RE = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
WORD_RE = re.compile(r"[^\W_]+(?:['’\-][^\W_]+)*", re.UNICODE)
URL_RE = re.compile(r"https?://\S+")
HTML_COMMENT_RE = re.compile(r"<!--.*?-->")
HTML_TAG_RE = re.compile(r"</?[A-Za-z][^>]*>")

# Plan section 5.1 numbers: (label, key, planned value, exact?)
PLAN = (
    ("Markdown files (tracked)", "md_files", 223, True),
    ("  generated (lessons/cs)", "md_generated", 11, True),
    ("  hand-written", "md_authored", 212, True),
    ("Hand-written prose words", "words_authored", 197000, False),
    ("Translatable segments", "segments", 12136, False),
    ("Entry READMEs under src/", "entry_readmes", 40, True),
    ("CS sources (lessons/cs-source)", "cs_sources", 108, True),
    ("Study guide files", "study_guides", 23, True),
    ("Mermaid blocks", "mermaid_total", 191, True),
    ("  unique Mermaid blocks", "mermaid_unique", 84, True),
    ("Headings", "headings", 1299, True),
    ("Links with .md#anchor", "md_anchor_links", 1159, True),
    ("  unique .md#anchor links", "md_anchor_links_unique", 195, True),
    ("Inline code spans", "inline_code_spans", 12000, False),
    ("Publications (PDF+EPUB at root)", "publications", 6, True),
)
APPROX_TOLERANCE = 0.10

# Why a measured value may legitimately differ from the plan (shown next to DIFF rows).
DIFF_NOTES = {
    "mermaid_total": "plan counted fence openers with grep; CONTRIBUTING.md has one example "
                     "nested inside a ````markdown fence, which is not a diagram",
    "mermaid_unique": "same nested CONTRIBUTING.md example",
    "headings": "plan's counting method is unrecorded; this counts ATX headings outside fences "
                "(61 of them sit inside generated blocks)",
    "md_anchor_links": "a naive all-lines scan finds 1,159; the extra link is an example inside a "
                       "code fence in lessons/book/README.md, which is not a live link",
    "md_anchor_links_unique": "distinct anchor fragments; same fenced example plus method differences",
    "segments": "line-based proxy (non-blank prose line); the P1 segmenter's count supersedes it",
    "inline_code_spans": "this counts front matter and generated blocks; plan said approximate",
}


# ---------------------------------------------------------------- classification

def is_owned(path: str) -> bool:
    return (path in OWNED_FILES
            or path.startswith(OWNED_PREFIXES)
            or any(g.match(path) for g in OWNED_GLOBS))


def classify(path: str) -> list[str]:
    """Return every class whose rule matches `path` (should be exactly one)."""
    hits = []
    ext = PurePosixPath(path).suffix.lower()
    if is_owned(path):
        hits.append("owned")
    if ext == ".md" and not is_owned(path):
        hits.append("generated" if re.match(r"^lessons/cs/[^/]+\.md$", path) else "authored")
    if any(p.match(path) for p in TOOLING_PATTERNS):
        hits.append("tooling")
    if ext in ARCHIVAL_EXT:
        hits.append("archival")
    # frozen is the default for anything else, including LICENSE.
    if not hits:
        hits.append("frozen")
    return hits


# ---------------------------------------------------------------- Markdown measuring

def clean_prose(line: str) -> str:
    line = HTML_COMMENT_RE.sub(" ", line)
    line = CODE_SPAN_RE.sub(" ", line)
    line = LINK_RE.sub("]", line)
    line = URL_RE.sub(" ", line)
    line = HTML_TAG_RE.sub(" ", line)
    return line


def count_words(line: str) -> int:
    return len(WORD_RE.findall(clean_prose(line)))


def split_front_matter(lines: list[str]) -> tuple[list[str], list[str]]:
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return lines[1:i], lines[i + 1:]
    return [], lines


def normalize_mermaid(block: list[str]) -> str:
    return "\n".join(" ".join(l.split()) for l in block if l.strip())


def resolve_link(src: str, target: str) -> str:
    base, _, anchor = target.partition("#")
    if not base:
        return f"{src}#{anchor}"
    resolved = os.path.normpath(os.path.join(os.path.dirname(src), base)).replace(os.sep, "/")
    return f"{resolved}#{anchor}"


def scan_inline(path: str, line: str, m: dict) -> None:
    """Count inline code spans and anchor links on one line (front matter or body)."""
    m["inline_code_spans"] += len(CODE_SPAN_RE.findall(line))
    for t in LINK_RE.findall(line):
        if ".md#" in t:
            m["md_anchor_links"].append(resolve_link(path, t))
        elif t.startswith("#"):
            m["same_file_anchor_links"] += 1


def measure_markdown(path: str, text: str) -> dict:
    lines = text.split("\n")
    fm, body = split_front_matter(lines)
    m = {
        "front_matter": bool(fm) or (lines[:1] == ["---"]),
        "words": 0, "segments": 0, "headings": 0, "inline_code_spans": 0,
        "mermaid_blocks": [], "code_fences": 0, "generated_blocks": 0,
        "md_anchor_links": [], "same_file_anchor_links": 0,
    }
    # front matter: prose keys count as segments and words; links and code spans count too
    in_prose_key = False
    for l in fm:
        scan_inline(path, l, m)
        mk = re.match(r"^([A-Za-z_-]+):\s*(.*)$", l)
        if mk:
            in_prose_key = mk.group(1) in PROSE_FM_KEYS
            if in_prose_key and mk.group(2).strip() not in ("", "[]"):
                m["segments"] += 1
                m["words"] += count_words(mk.group(2))
        elif in_prose_key and l.strip().startswith("-"):
            m["segments"] += 1
            m["words"] += count_words(l.strip()[1:])

    fence = None          # (char, length, is_mermaid)
    mermaid_buf: list[str] = []
    in_generated = False
    for line in body:
        fm_ = FENCE_RE.match(line)
        if fence:
            if fm_ and fm_.group(1)[0] == fence[0] and len(fm_.group(1)) >= fence[1] \
                    and not fm_.group(2).strip():
                if fence[2]:
                    m["mermaid_blocks"].append(normalize_mermaid(mermaid_buf))
                fence = None
                mermaid_buf = []
            elif fence[2]:
                mermaid_buf.append(line)
            continue
        if fm_:
            info = fm_.group(2).strip().lower()
            fence = (fm_.group(1)[0], len(fm_.group(1)), info.startswith("mermaid"))
            m["code_fences"] += 1
            mermaid_buf = []
            continue
        if BEGIN_GEN_RE.search(line):
            m["generated_blocks"] += 1
            in_generated = True
            continue
        if END_GEN_RE.search(line):
            in_generated = False
            continue
        # links and code spans count everywhere outside fences (including generated blocks)
        scan_inline(path, line, m)
        if HEADING_RE.match(line):
            m["headings"] += 1
        if in_generated:
            continue
        w = count_words(line)
        if w:
            m["words"] += w
            m["segments"] += 1
    return m


# ---------------------------------------------------------------- file listing

def list_files(root: str) -> list[str]:
    if os.path.isdir(os.path.join(root, ".git")):
        out = subprocess.run(["git", "-C", root, "ls-files", "-z"], check=True,
                             capture_output=True).stdout.decode("utf-8")
        files = [f for f in out.split("\0") if f]
    else:
        files = []
        for dp, dn, fn in os.walk(root):
            dn[:] = [d for d in dn if d != ".git"]
            for f in fn:
                files.append(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/"))
    return sorted(f for f in files if os.path.isfile(os.path.join(root, f)))


def read_text(path: str) -> str:
    with open(path, encoding="utf-8") as fh:
        return fh.read()


def read_config(root: str) -> dict:
    cfg = {}
    p = os.path.join(root, "loop", "CONFIG.yaml")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as fh:
            for l in fh:
                m = re.match(r"^([a-z_]+):\s*([^#\n]*?)\s*(?:#.*)?$", l)
                if m:
                    cfg[m.group(1)] = m.group(2).strip().strip('"')
    return cfg


def english_file_set(cfg: dict) -> set[str] | None:
    clone, sha = cfg.get("english_clone_path"), cfg.get("english_commit")
    if not clone or not sha or not os.path.isdir(clone):
        return None
    r = subprocess.run(["git", "-C", clone, "ls-tree", "-r", "-z", "--name-only", sha],
                       capture_output=True)
    if r.returncode != 0:
        return None
    return {f for f in r.stdout.decode("utf-8").split("\0") if f}


# ---------------------------------------------------------------- build

def build_inventory(root: str) -> dict:
    files = list_files(root)
    records, problems = [], []
    for f in files:
        classes = classify(f)
        if len(classes) != 1:
            problems.append(f"{f}: matches classes {classes}")
        cls = classes[0]
        rec = {"path": f, "class": cls}
        if cls in ("authored", "generated"):
            with open(os.path.join(root, f), encoding="utf-8") as fh:
                data = fh.read()
            mm = measure_markdown(f, data)
            rec.update({
                "front_matter": mm["front_matter"], "words": mm["words"],
                "segments": mm["segments"], "headings": mm["headings"],
                "inline_code_spans": mm["inline_code_spans"],
                "code_fences": mm["code_fences"],
                "generated_blocks": mm["generated_blocks"],
                "mermaid_blocks": len(mm["mermaid_blocks"]),
                "md_anchor_links": len(mm["md_anchor_links"]),
                "same_file_anchor_links": mm["same_file_anchor_links"],
                "_mermaid": mm["mermaid_blocks"], "_links": mm["md_anchor_links"],
            })
        records.append(rec)

    live = [r for r in records if r["class"] != "owned"]
    md = [r for r in live if r["class"] in ("authored", "generated")]
    auth = [r for r in md if r["class"] == "authored"]
    all_mermaid = [b for r in md for b in r["_mermaid"]]
    all_links = [l for r in md for l in r["_links"]]
    t = {
        "files": len(live),
        "by_class": {c: sum(1 for r in live if r["class"] == c) for c in CLASSES if c != "owned"},
        "md_files": len(md),
        "md_generated": sum(1 for r in md if r["class"] == "generated"),
        "md_authored": len(auth),
        "words_authored": sum(r["words"] for r in auth),
        "words_generated": sum(r["words"] for r in md if r["class"] == "generated"),
        "segments": sum(r["segments"] for r in auth),
        "headings": sum(r["headings"] for r in md),
        "headings_authored": sum(r["headings"] for r in auth),
        "inline_code_spans": sum(r["inline_code_spans"] for r in md),
        "mermaid_total": len(all_mermaid),
        "mermaid_unique": len(set(all_mermaid)),
        "md_anchor_links": len(all_links),
        # distinct anchor fragments (the plan's definition) and distinct resolved file#anchor
        # targets (what the anchor-remap task must handle)
        "md_anchor_links_unique": len({l.split("#", 1)[1] for l in all_links}),
        "md_anchor_targets_unique": len(set(all_links)),
        "same_file_anchor_links": sum(r["same_file_anchor_links"] for r in md),
        "generated_blocks": sum(r["generated_blocks"] for r in md),
        "front_matter_files": sum(1 for r in md if r["front_matter"]),
        "entry_readmes": sum(1 for r in auth if re.match(r"^src/[^/]+/README\.md$", r["path"])),
        "cs_sources": sum(1 for r in auth if r["path"].startswith("lessons/cs-source/")),
        "study_guides": sum(1 for r in auth if r["path"].startswith("lessons/study-guides/")),
        "publications": sum(1 for r in live if r["class"] == "archival"
                            and "/" not in r["path"] and r["path"].endswith((".pdf", ".epub"))),
    }
    for r in records:
        r.pop("_mermaid", None)
        r.pop("_links", None)
    return {"schema": 1, "totals": t, "files": live, "problems": problems,
            "owned_skipped": sorted(r["path"] for r in records if r["class"] == "owned")}


def comparison_rows(totals: dict) -> list[dict]:
    rows = []
    for label, key, planned, exact in PLAN:
        got = totals[key]
        if exact:
            ok = got == planned
        else:
            ok = abs(got - planned) <= APPROX_TOLERANCE * planned
        rows.append({"item": label.strip(), "key": key, "plan": planned,
                     "measured": got, "exact": exact, "status": "ok" if ok else "DIFF"})
    return rows


def dumps(inv: dict) -> str:
    # owned files are left out on purpose: the inventory file itself is owned, so listing
    # owned files would make the file stale the moment it is tracked.
    body = {k: v for k, v in inv.items() if k != "owned_skipped"}
    return json.dumps(body, ensure_ascii=False, indent=1, sort_keys=True) + "\n"


# ---------------------------------------------------------------- CLI

def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--out", default=None, help="inventory path (default translation/work/inventory.json)")
    ap.add_argument("--no-english", action="store_true", help="skip the English tree comparison")
    a = ap.parse_args(argv)

    root = os.path.abspath(a.root)
    out = a.out or os.path.join(root, "translation", "work", "inventory.json")
    inv = build_inventory(root)
    cfg = read_config(root)
    rows = comparison_rows(inv["totals"])
    failures = list(inv["problems"])

    english = None if a.no_english else english_file_set(cfg)
    if english is not None:
        expected = {f for f in english if not is_owned(f)}
        actual = {r["path"] for r in inv["files"]}
        for f in sorted(expected - actual):
            failures.append(f"missing from Spanish repo but in English tree: {f}")
        for f in sorted(actual - expected):
            failures.append(f"not in English tree and not owned: {f}")

    if not a.check:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        with open(out, "w", encoding="utf-8") as fh:
            fh.write(dumps(inv))
        print(f"wrote {os.path.relpath(out, root)}: {inv['totals']['files']} files")
    else:
        if not os.path.exists(out):
            failures.append(f"{os.path.relpath(out, root)} does not exist (run without --check)")
        elif read_text(out) != dumps(inv):
            failures.append(f"{os.path.relpath(out, root)} is stale (run without --check)")

    t = inv["totals"]
    print(f"{'Item':36} {'Plan 5.1':>10} {'Measured':>10}  Status")
    for r in rows:
        mark = "" if r["exact"] else " (~)"
        print(f"{r['item']:36} {r['plan']:>10} {r['measured']:>10}  {r['status']}{mark}")
        if r["status"] == "DIFF" and r["key"] in DIFF_NOTES:
            print(f"    note: {DIFF_NOTES[r['key']]}")
    print(f"{'Distinct file#anchor link targets':36} {'':>10} {t['md_anchor_targets_unique']:>10}")
    print("By class: " + ", ".join(f"{k}={v}" for k, v in t["by_class"].items()))
    print(f"Also: generated words={t['words_generated']}, same-file anchor links="
          f"{t['same_file_anchor_links']}, generated blocks={t['generated_blocks']}, "
          f"front matter files={t['front_matter_files']}")
    diffs = [r for r in rows if r["status"] == "DIFF"]
    if diffs:
        print(f"NOTE: {len(diffs)} item(s) differ from plan 5.1 (informational, re-measured values stand).")
    if english is None and not a.no_english:
        print("NOTE: English clone not reachable; file-set comparison skipped.")
    if failures:
        print("FAIL:")
        for f in failures:
            print("  " + f)
        return 1
    print("OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
