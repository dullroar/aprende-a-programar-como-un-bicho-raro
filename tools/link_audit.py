#!/usr/bin/env python3
"""tools/link_audit.py: the link audit, gate category G (plan section 10.1, task S3-001).

One scanner over four surfaces, with one rule: a target that could not be checked is reported `unverified` or
`not executed`, never green. Findings have a status:

  broken        the target is provably wrong (missing file, missing fragment, line past the end, wrong repository,
                dangling PDF destination, EPUB item missing from the manifest or the zip)
  unverified    could not be checked here (external URL: no network calls are made), with a reason
  not-executed  a check that needs a tool that is absent (EPUBCheck, PyMuPDF), with a reason

Surfaces:
  markdown   tracked Markdown parsed with markdown-it-py (never a regex over lines); heading ids as GitHub makes them
             (NFC, lower case, accents kept, punctuation dropped, duplicates -1, -2 ...); relative paths; fragments;
             semantic line anchors (#L12, #L12-L20) against the real line count of the target file; wrong-repository
             links; GitHub-relative rewrites ({{REPOSITORY_WEB_URL}}-style macros are skipped as unverified-free)
  html       built HTML: every id, every href/src and fragment (html.parser)
  pdf        link annotations and named destinations (PyMuPDF)
  epub       container, manifest, spine, navigation document, fragments in content; EPUBCheck when installed

Every function is pure (it takes file contents as data) so tools/test_link_audit.py can plant a defect of each type.

Usage:
  python3 -I tools/link_audit.py                      audit tracked Markdown of this checkout (exit 1 on any broken)
  python3 -I tools/link_audit.py --html FILE... --pdf FILE... --epub FILE...
  python3 -I tools/link_audit.py --json OUT.json --md OUT.md
"""
from __future__ import annotations

import html.parser
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from urllib.parse import unquote, urlsplit

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)

BROKEN, UNVERIFIED, NOT_EXECUTED = "broken", "unverified", "not-executed"
LINE_RE = re.compile(r"^L(\d+)(?:-L(\d+))?$")
SCHEME_RE = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
MACRO_RE = re.compile(r"\{\{[^}]*\}\}|\[\[[^\]]*\]\]")
REPO_RE = re.compile(r"^https?://(?:www\.)?github\.com/([^/]+)/([^/#?]+)", re.I)
HTML_ATTR_RE = re.compile(r"""\b(?:href|src)\s*=\s*["']([^"']+)["']""", re.I)


def finding(status, kind, where, target, reason):
    return {"status": status, "kind": kind, "where": where, "target": target, "reason": reason}


# ---------------------------------------------------------------------------------------- heading ids

def github_slug(text):
    """github-slugger: lower case, keep letters, marks, digits, '-', '_', spaces become '-'. Input is NFC first."""
    t = unicodedata.normalize("NFC", text).lower()
    keep = "".join(c for c in t if c in "-_ " or unicodedata.category(c)[0] in "LMN" or unicodedata.category(c) == "Pc")
    return keep.replace(" ", "-")


def _md():
    from markdown_it import MarkdownIt
    return MarkdownIt("commonmark").enable("table")


def _inline_text(tok):
    """The text a reader sees in an inline token (code spans keep their content, images their alt text)."""
    out = []
    for c in tok.children or []:
        if c.type in ("text", "code_inline"):
            out.append(c.content)
        elif c.type == "image":
            out.append(c.content)
        elif c.type in ("softbreak", "hardbreak"):
            out.append(" ")
    return "".join(out).strip()


def heading_ids(text):
    """Ids GitHub gives the headings of `text`, in order, with duplicates numbered."""
    toks = _md().parse(text)
    seen, ids = {}, []
    for i, t in enumerate(toks):
        if t.type == "heading_open":
            base = github_slug(_inline_text(toks[i + 1]))
            n = seen.get(base, 0)
            seen[base] = n + 1
            ids.append(base if n == 0 else "%s-%d" % (base, n))
    return ids


def explicit_ids(text):
    """id= and name= attributes of raw HTML in a Markdown file (GitHub keeps them, prefixed `user-content-` internally)."""
    return set(re.findall(r"""\b(?:id|name)\s*=\s*["']([^"']+)["']""", text))


def md_links(text):
    """(line, destination) for every link, image and HTML href/src that is not inside code. Real parser."""
    out = []
    for t in _md().parse(text):
        if t.type == "inline":
            line = (t.map or [0])[0] + 1
            for c in t.children or []:
                if c.type == "link_open":
                    out.append((line, c.attrGet("href") or ""))
                elif c.type == "image":
                    out.append((line, c.attrGet("src") or ""))
                elif c.type == "html_inline":
                    out += [(line, d) for d in HTML_ATTR_RE.findall(c.content)]
        elif t.type == "html_block":
            line = (t.map or [0])[0] + 1
            out += [(line, d) for d in HTML_ATTR_RE.findall(t.content)]
    return out


# ---------------------------------------------------------------------------------------- repository

def _wrong_repo(dest, repo_url, wrong_repos):
    m = REPO_RE.match(dest)
    if not m:
        return None
    own = REPO_RE.match(repo_url)
    owner, name = m.group(1), m.group(2)
    if own and name.lower().removesuffix(".git") in {w.lower() for w in wrong_repos if w}:
        return "links to repository %s/%s, not %s/%s" % (owner, name, own.group(1), own.group(2))
    return None


def line_anchor_problem(frag, nlines):
    m = LINE_RE.match(frag)
    if not m:
        return None
    a = int(m.group(1))
    b = int(m.group(2)) if m.group(2) else a
    if a < 1 or b < a:
        return "line anchor #%s is not a valid range" % frag
    if b > nlines:
        return "line anchor #%s is past the end (target has %d lines)" % (frag, nlines)
    return None


def _count_lines(data):
    if isinstance(data, bytes):
        data = data.decode("utf-8", "replace")
    return len(data.splitlines())


# ---------------------------------------------------------------------------------------- markdown

def audit_markdown(files, tree, repo_url, wrong_repos=()):
    """files: {rel path: Markdown text} to scan. tree: {rel path: bytes or str} of every file a link may name
    (the Markdown files must be in it too). Returns findings."""
    out = []
    ids_cache = {}

    def ids_of(rel):
        if rel not in ids_cache:
            t = tree[rel]
            t = t.decode("utf-8", "replace") if isinstance(t, bytes) else t
            ids_cache[rel] = set(heading_ids(t)) | explicit_ids(t)
        return ids_cache[rel]

    dirs = {posixpath.dirname(p) for p in tree}
    for rel, text in sorted(files.items()):
        for line, dest in md_links(text):
            where = "%s:%d" % (rel, line)
            if not dest or MACRO_RE.search(unquote(dest)):
                continue
            wr = _wrong_repo(dest, repo_url, wrong_repos)
            if wr:
                out.append(finding(BROKEN, "wrong-repository", where, dest, wr))
                continue
            if dest.startswith("//") or SCHEME_RE.match(dest):
                if dest.lower().startswith(("http://", "https://")):
                    out.append(finding(UNVERIFIED, "external", where, dest, "external URL: no network calls are made"))
                continue
            parts = urlsplit(dest)
            path, frag = unquote(parts.path), unquote(parts.fragment)
            if path:
                target = posixpath.normpath(path.lstrip("/") if path.startswith("/") else posixpath.join(posixpath.dirname(rel), path))
                if target.startswith("../") or target == "..":
                    out.append(finding(BROKEN, "path", where, dest, "path leaves the repository"))
                    continue
                if target not in tree and target not in dirs:
                    out.append(finding(BROKEN, "path", where, dest, "no such file in this checkout"))
                    continue
            else:
                target = rel
            if not frag:
                continue
            if LINE_RE.match(frag):
                if target in tree:
                    why = line_anchor_problem(frag, _count_lines(tree[target]))
                    if why:
                        out.append(finding(BROKEN, "line-anchor", where, dest, why))
                continue
            if target.lower().endswith((".md", ".markdown")) and target in tree:
                if frag not in ids_of(target):
                    out.append(finding(BROKEN, "fragment", where, dest, "no heading or id %r in %s" % (frag, target)))
            elif target in tree and target.lower().endswith((".html", ".xhtml")):
                got = html_ids(tree[target])
                if frag not in got:
                    out.append(finding(BROKEN, "fragment", where, dest, "no id %r in %s" % (frag, target)))
            elif target in tree:
                out.append(finding(UNVERIFIED, "fragment", where, dest, "fragment into a non-Markdown file is not checked"))
    return out


# ---------------------------------------------------------------------------------------- html

class _Scan(html.parser.HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.ids, self.refs = set(), []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        for k in ("id", "name"):
            if a.get(k):
                self.ids.add(a[k])
        for k in ("href", "src"):
            if a.get(k):
                self.refs.append((self.getpos()[0], a[k]))


def _scan_html(data):
    s = _Scan()
    s.feed(data.decode("utf-8", "replace") if isinstance(data, bytes) else data)
    return s


def html_ids(data):
    return _scan_html(data).ids


def audit_html(pages, repo_url="", wrong_repos=(), assets=None):
    """pages: {path: html}. assets: set of other paths (images, css) a page may reference; None skips asset checks."""
    out = []
    scans = {p: _scan_html(d) for p, d in pages.items()}
    known = set(pages) | set(assets or ())
    for p, s in sorted(scans.items()):
        for line, dest in s.refs:
            where = "%s:%d" % (p, line)
            wr = _wrong_repo(dest, repo_url, wrong_repos) if repo_url else None
            if wr:
                out.append(finding(BROKEN, "wrong-repository", where, dest, wr))
                continue
            if dest.startswith("//") or SCHEME_RE.match(dest):
                if dest.lower().startswith(("http://", "https://")):
                    out.append(finding(UNVERIFIED, "external", where, dest, "external URL: no network calls are made"))
                continue
            parts = urlsplit(dest)
            path, frag = unquote(parts.path), unquote(parts.fragment)
            target = posixpath.normpath(posixpath.join(posixpath.dirname(p), path)) if path else p
            if path and target not in known and (assets is not None or target in pages):
                out.append(finding(BROKEN, "path", where, dest, "no such page or asset"))
                continue
            if frag and target in scans and frag not in scans[target].ids:
                out.append(finding(BROKEN, "fragment", where, dest, "no id %r in %s" % (frag, target)))
    return out


# ---------------------------------------------------------------------------------------- pdf

def audit_pdf(path, repo_url="", wrong_repos=()):
    try:
        import fitz
    except ImportError:
        return [finding(NOT_EXECUTED, "pdf", path, "", "PyMuPDF is not installed")]
    out = []
    doc = fitz.open(path)
    try:
        names = doc.resolve_names()
    except Exception:
        names = {}
    for pno, page in enumerate(doc, 1):
        for ln in page.get_links():
            where = "%s:page %d" % (path, pno)
            kind = ln.get("kind")
            if kind == fitz.LINK_URI:
                uri = ln.get("uri", "")
                wr = _wrong_repo(uri, repo_url, wrong_repos) if repo_url else None
                if wr:
                    out.append(finding(BROKEN, "wrong-repository", where, uri, wr))
                else:
                    out.append(finding(UNVERIFIED, "external", where, uri, "external URL: no network calls are made"))
            elif kind == fitz.LINK_GOTO:
                dest = ln.get("page", -1)
                if not (0 <= dest < doc.page_count):
                    out.append(finding(BROKEN, "pdf-destination", where, str(dest), "internal link goes to a page that does not exist"))
            elif kind == fitz.LINK_NAMED:
                nm = ln.get("name", "")
                if nm not in names:
                    out.append(finding(BROKEN, "pdf-destination", where, nm, "named destination is not defined"))
            elif kind == fitz.LINK_NONE:
                out.append(finding(BROKEN, "pdf-destination", where, "", "link annotation has no action"))
    return out


# ---------------------------------------------------------------------------------------- epub

def audit_epub(path, run_epubcheck=True):
    out = []
    try:
        z = zipfile.ZipFile(path)
    except (OSError, zipfile.BadZipFile) as e:
        return [finding(BROKEN, "epub", path, "", "not a readable zip: %s" % e)]
    names = set(z.namelist())
    from xml.etree import ElementTree as ET

    def parse(n):
        return ET.fromstring(z.read(n))

    if "META-INF/container.xml" not in names:
        return [finding(BROKEN, "epub", path, "META-INF/container.xml", "missing container")]
    rf = [e.get("full-path") for e in parse("META-INF/container.xml").iter() if e.tag.endswith("rootfile")]
    if not rf or rf[0] not in names:
        return [finding(BROKEN, "epub", path, "container.xml", "rootfile missing from the zip")]
    opf = rf[0]
    base = posixpath.dirname(opf)
    root = parse(opf)
    items = {}
    for e in root.iter():
        if e.tag.endswith("}item") or e.tag == "item":
            items[e.get("id")] = (e.get("href", ""), e.get("media-type", ""), e.get("properties", ""))
    for iid, (href, _mt, _pr) in items.items():
        full = posixpath.normpath(posixpath.join(base, unquote(href)))
        if full not in names:
            out.append(finding(BROKEN, "epub-manifest", opf, href, "manifest item %r is not in the zip" % iid))
    spine = [e.get("idref") for e in root.iter() if e.tag.endswith("itemref")]
    if not spine:
        out.append(finding(BROKEN, "epub-spine", opf, "", "spine is empty"))
    for idref in spine:
        if idref not in items:
            out.append(finding(BROKEN, "epub-spine", opf, idref, "spine item is not in the manifest"))
    navs = [h for h, _m, pr in items.values() if "nav" in pr.split()]
    if not navs:
        out.append(finding(BROKEN, "epub-nav", opf, "", "no navigation document (properties=nav) in the manifest"))
    content = {}
    for h, mt, _pr in items.values():
        full = posixpath.normpath(posixpath.join(base, unquote(h)))
        if full in names and ("html" in mt):
            content[full] = z.read(full)
    scans = {p: _scan_html(d) for p, d in content.items()}
    for p, s in sorted(scans.items()):
        for line, dest in s.refs:
            if SCHEME_RE.match(dest) or dest.startswith("//"):
                continue
            parts = urlsplit(dest)
            tp = posixpath.normpath(posixpath.join(posixpath.dirname(p), unquote(parts.path))) if parts.path else p
            where = "%s:%d" % (p, line)
            if tp not in names:
                out.append(finding(BROKEN, "epub-link", where, dest, "target is not in the zip"))
            elif parts.fragment and tp in scans and unquote(parts.fragment) not in scans[tp].ids:
                out.append(finding(BROKEN, "epub-fragment", where, dest, "no id %r in %s" % (parts.fragment, tp)))
    for nav in navs:
        full = posixpath.normpath(posixpath.join(base, unquote(nav)))
        listed = set()
        for _l, dest in scans.get(full, _Scan()).refs:
            if not SCHEME_RE.match(dest):
                listed.add(posixpath.normpath(posixpath.join(posixpath.dirname(full), unquote(urlsplit(dest).path))) if urlsplit(dest).path else full)
        spine_paths = {posixpath.normpath(posixpath.join(base, unquote(items[i][0]))) for i in spine if i in items}
        if not listed:
            out.append(finding(BROKEN, "epub-nav", full, "", "navigation document links to nothing"))
        elif not listed & spine_paths:
            out.append(finding(BROKEN, "epub-nav", full, "", "navigation entries match no spine document"))
    z.close()
    if run_epubcheck:
        out += _epubcheck(path)
    return out


def _epubcheck(path):
    exe = shutil.which("epubcheck")
    if not exe:
        return [finding(NOT_EXECUTED, "epubcheck", path, "", "EPUBCheck is not installed")]
    try:
        r = subprocess.run([exe, path], capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as e:
        return [finding(NOT_EXECUTED, "epubcheck", path, "", "EPUBCheck could not run: %s" % e)]
    if r.returncode != 0:
        return [finding(BROKEN, "epubcheck", path, "", (r.stdout + r.stderr).strip()[-400:])]
    return []


# ---------------------------------------------------------------------------------------- reports

def summarize(findings):
    s = {BROKEN: 0, UNVERIFIED: 0, NOT_EXECUTED: 0}
    for f in findings:
        s[f["status"]] += 1
    return s


def report_json(findings):
    return json.dumps({"summary": summarize(findings), "findings": findings}, indent=1, ensure_ascii=False) + "\n"


def report_markdown(findings):
    s = summarize(findings)
    lines = ["# Link audit", "",
             "broken: %d | unverified: %d | not executed: %d" % (s[BROKEN], s[UNVERIFIED], s[NOT_EXECUTED]), "",
             "Verdict: %s" % ("FAIL" if s[BROKEN] else "no broken link (unverified and not-executed items are not green)"), ""]
    for st in (BROKEN, UNVERIFIED, NOT_EXECUTED):
        rows = [f for f in findings if f["status"] == st]
        if not rows:
            continue
        lines += ["## %s (%d)" % (st, len(rows)), "", "| kind | where | target | reason |", "|---|---|---|---|"]
        for f in rows:
            lines.append("| %s | %s | %s | %s |" % (f["kind"], f["where"], f["target"].replace("|", "\\|"), f["reason"].replace("|", "\\|")))
        lines.append("")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------------------- checkout

def read_repo_url(root=ROOT):
    with open(os.path.join(root, "lessons/book/locale/es.yaml"), encoding="utf-8") as f:
        m = re.search(r'^\s*repo_url:\s*"([^"]+)"', f.read(), re.M)
    return m.group(1) if m else ""


def read_english_repo_name(root=ROOT):
    with open(os.path.join(root, "lessons/book/locale/en.yaml"), encoding="utf-8") as f:
        m = re.search(r'^\s*repo_url:\s*"[^"]*/([^"/]+)"', f.read(), re.M)
    return m.group(1) if m else ""


def tracked(root=ROOT):
    r = subprocess.run(["git", "-C", root, "ls-files"], capture_output=True, text=True, check=True)
    return [p for p in r.stdout.splitlines() if p]


def audit_checkout(root=ROOT):
    names = tracked(root)
    tree, files = {}, {}
    for p in names:
        fp = os.path.join(root, p)
        if not os.path.isfile(fp):
            continue
        with open(fp, "rb") as f:
            data = f.read()
        tree[p] = data
        if p.lower().endswith(".md"):
            files[p] = data.decode("utf-8", "replace")
    repo = read_repo_url(root)
    wrong = [read_english_repo_name(root)]
    return audit_markdown(files, tree, repo, wrong)


def main(argv):
    import argparse
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--html", nargs="*", default=[])
    ap.add_argument("--pdf", nargs="*", default=[])
    ap.add_argument("--epub", nargs="*", default=[])
    ap.add_argument("--json")
    ap.add_argument("--md")
    a = ap.parse_args(argv)
    findings = audit_checkout()
    repo, wrong = read_repo_url(), [read_english_repo_name()]
    if a.html:
        pages = {p: open(p, "rb").read() for p in a.html}
        findings += audit_html(pages, repo, wrong)
    for p in a.pdf:
        findings += audit_pdf(p, repo, wrong)
    for p in a.epub:
        findings += audit_epub(p)
    if a.json:
        with open(a.json, "w", encoding="utf-8") as f:
            f.write(report_json(findings))
    if a.md:
        with open(a.md, "w", encoding="utf-8") as f:
            f.write(report_markdown(findings))
    s = summarize(findings)
    print("link audit: broken %d, unverified %d, not executed %d" % (s[BROKEN], s[UNVERIFIED], s[NOT_EXECUTED]))
    for f in findings:
        if f["status"] == BROKEN:
            print("  BROKEN %s %s -> %s: %s" % (f["kind"], f["where"], f["target"], f["reason"]))
    return 1 if s[BROKEN] else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
