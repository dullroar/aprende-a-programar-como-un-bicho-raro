#!/usr/bin/env python3
"""Tests for tools/link_audit.py (S3-001). Run: python3 -I tools/test_link_audit.py
Every link type has a clean control and a planted broken case; unverified and not-executed are never green."""
import io
import os
import sys
import tempfile
import unittest
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import link_audit as la  # noqa: E402

REPO = "https://github.com/dullroar/aprende-a-programar-como-un-bicho-raro"
WRONG = ["learn-programming-the-weird-way"]


def md(files, tree_extra=None):
    tree = dict(files)
    tree.update(tree_extra or {})
    return la.audit_markdown(files, tree, REPO, WRONG)


def kinds(fs, status=la.BROKEN):
    return sorted(f["kind"] for f in fs if f["status"] == status)


class Slugs(unittest.TestCase):
    def test_accents_kept_punctuation_dropped(self):
        self.assertEqual(la.heading_ids("# ¿Qué hace el reto?\n"), ["qué-hace-el-reto"])

    def test_duplicates_are_numbered(self):
        self.assertEqual(la.heading_ids("# A\n\n## A\n\n### A\n"), ["a", "a-1", "a-2"])

    def test_code_span_and_link_text_and_nfc(self):
        ids = la.heading_ids("# Usa `let` y [enlaces](x.md)\n\n# Café\n")
        self.assertEqual(ids, ["usa-let-y-enlaces", "café"])

    def test_heading_inside_fence_is_not_a_heading(self):
        self.assertEqual(la.heading_ids("```\n# no\n```\n\n# si\n"), ["si"])


class Markdown(unittest.TestCase):
    def test_clean_controls(self):
        files = {"a.md": "[b](b.md#hola-mundo) [c](sub/c.txt#L2-L3) [s](#top) [e](https://en.wikipedia.org/wiki/X)\n\n# Top\n",
                 "b.md": "# Hola mundo\n"}
        fs = md(files, {"sub/c.txt": "1\n2\n3\n"})
        self.assertEqual(kinds(fs), [])
        self.assertEqual(kinds(fs, la.UNVERIFIED), ["external"])

    def test_broken_path(self):
        self.assertEqual(kinds(md({"a.md": "[x](nada.md)\n"})), ["path"])

    def test_path_leaves_repository(self):
        self.assertEqual(kinds(md({"a.md": "[x](../fuera.md)\n"})), ["path"])

    def test_broken_fragment_and_accent_mismatch(self):
        files = {"a.md": "[x](b.md#ola)\n[y](b.md#que-hace)\n", "b.md": "# Qué hace\n"}
        self.assertEqual(kinds(md(files)), ["fragment", "fragment"])

    def test_duplicate_heading_fragment(self):
        files = {"a.md": "[ok](b.md#x-1) [bad](b.md#x-2)\n", "b.md": "# X\n\n# X\n"}
        self.assertEqual(kinds(md(files)), ["fragment"])

    def test_line_anchor_past_end_and_reversed(self):
        files = {"a.md": "[ok](c.py#L3) [far](c.py#L9) [rev](c.py#L3-L2)\n"}
        fs = md(files, {"c.py": "a\nb\nc\n"})
        self.assertEqual(kinds(fs), ["line-anchor", "line-anchor"])

    def test_wrong_repository(self):
        files = {"a.md": "[x](https://github.com/dullroar/learn-programming-the-weird-way/blob/main/README.md)\n"
                         "[y](https://github.com/dullroar/aprende-a-programar-como-un-bicho-raro/blob/main/README.md)\n"}
        fs = md(files)
        self.assertEqual(kinds(fs), ["wrong-repository"])
        self.assertEqual(kinds(fs, la.UNVERIFIED), ["external"])

    def test_code_is_not_scanned_but_html_is(self):
        files = {"a.md": "`[x](no.md)`\n\n```\n[y](no2.md)\n```\n\n<a href=\"no3.md\">z</a>\n![i](no4.png)\n"}
        got = sorted(f["target"] for f in md(files))
        self.assertEqual(got, ["no3.md", "no4.png"])

    def test_percent_encoded_and_macros(self):
        files = {"a.md": "[x](b.md#qu%C3%A9) [m]({{REPOSITORY_WEB_URL}}/x)\n", "b.md": "# Qué\n"}
        self.assertEqual(kinds(md(files)), [])

    def test_root_absolute_path(self):
        files = {"d/a.md": "[x](/docs/f.pdf) [y](/docs/g.pdf)\n"}
        self.assertEqual(kinds(md(files, {"docs/f.pdf": b""})), ["path"])


class Html(unittest.TestCase):
    def test_clean_and_broken(self):
        pages = {"o/a.html": '<h1 id="t">T</h1><a href="b.html#u">b</a><a href="#t">t</a><img src="i.png">',
                 "o/b.html": '<p id="u">u</p>'}
        self.assertEqual(la.audit_html(pages, REPO, WRONG, assets={"o/i.png"}), [])
        bad = {"o/a.html": '<a href="b.html#zz">b</a><a href="#nope">t</a><a href="gone.html">g</a><img src="x.png">'
                           '<a href="https://github.com/dullroar/learn-programming-the-weird-way">w</a>',
               "o/b.html": ""}
        fs = la.audit_html(bad, REPO, WRONG, assets=set())
        self.assertEqual(kinds(fs), ["fragment", "fragment", "path", "path", "wrong-repository"])


def make_pdf(path, links):
    import fitz
    doc = fitz.open()
    for _ in range(2):
        doc.new_page()
    page = doc[0]
    for i, ln in enumerate(links):
        ln = dict(ln)
        ln["from"] = fitz.Rect(10, 10 + 20 * i, 100, 25 + 20 * i)
        page.insert_link(ln)
    doc.save(path)


class Pdf(unittest.TestCase):
    def setUp(self):
        try:
            import fitz  # noqa: F401
        except ImportError:
            self.skipTest("PyMuPDF missing")

    def test_clean_and_planted(self):
        import fitz
        with tempfile.TemporaryDirectory() as d:
            good = os.path.join(d, "g.pdf")
            make_pdf(good, [{"kind": fitz.LINK_GOTO, "page": 1, "to": fitz.Point(0, 0)},
                            {"kind": fitz.LINK_URI, "uri": REPO + "/blob/main/README.md"}])
            fs = la.audit_pdf(good, REPO, WRONG)
            self.assertEqual(kinds(fs), [])
            self.assertEqual(kinds(fs, la.UNVERIFIED), ["external"])
            bad = os.path.join(d, "b.pdf")
            make_pdf(bad, [{"kind": fitz.LINK_NAMED, "name": "no-such-dest"},
                           {"kind": fitz.LINK_URI, "uri": "https://github.com/dullroar/learn-programming-the-weird-way/x"}])
            fs = la.audit_pdf(bad, REPO, WRONG)
            self.assertEqual(kinds(fs), ["pdf-destination", "wrong-repository"])


def make_epub(files):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as z:
        for n, data in files.items():
            z.writestr(n, data)
    return buf.getvalue()


CONTAINER = ('<?xml version="1.0"?><container xmlns="urn:oasis:names:tc:opendocument:xmlns:container" version="1.0">'
             '<rootfiles><rootfile full-path="OEBPS/c.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')


def opf(items, spine):
    its = "".join('<item id="%s" href="%s" media-type="application/xhtml+xml"%s/>' % (i, h, (' properties="%s"' % p) if p else "")
                  for i, h, p in items)
    sp = "".join('<itemref idref="%s"/>' % s for s in spine)
    return '<package xmlns="http://www.idpf.org/2007/opf" version="3.0"><manifest>%s</manifest><spine>%s</spine></package>' % (its, sp)


GOOD = {"META-INF/container.xml": CONTAINER,
        "OEBPS/c.opf": opf([("nav", "nav.xhtml", "nav"), ("c1", "c1.xhtml", "")], ["c1"]),
        "OEBPS/nav.xhtml": '<nav><a href="c1.xhtml#s">uno</a></nav>',
        "OEBPS/c1.xhtml": '<h1 id="s">Uno</h1><a href="#s">yo</a>'}


class Epub(unittest.TestCase):
    def run_epub(self, files):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "t.epub")
            with open(p, "wb") as f:
                f.write(make_epub(files))
            return la.audit_epub(p)

    def test_clean_reports_epubcheck_not_executed_when_absent(self):
        fs = self.run_epub(GOOD)
        self.assertEqual(kinds(fs), [])
        if la.shutil.which("epubcheck") is None:
            self.assertEqual(kinds(fs, la.NOT_EXECUTED), ["epubcheck"])

    def test_missing_manifest_item(self):
        f = dict(GOOD)
        f["OEBPS/c.opf"] = opf([("nav", "nav.xhtml", "nav"), ("c1", "c1.xhtml", ""), ("c2", "c2.xhtml", "")], ["c1"])
        self.assertIn("epub-manifest", kinds(self.run_epub(f)))

    def test_spine_item_not_in_manifest(self):
        f = dict(GOOD)
        f["OEBPS/c.opf"] = opf([("nav", "nav.xhtml", "nav"), ("c1", "c1.xhtml", "")], ["c1", "zz"])
        self.assertIn("epub-spine", kinds(self.run_epub(f)))

    def test_no_navigation_document(self):
        f = dict(GOOD)
        f["OEBPS/c.opf"] = opf([("nav", "nav.xhtml", ""), ("c1", "c1.xhtml", "")], ["c1"])
        self.assertIn("epub-nav", kinds(self.run_epub(f)))

    def test_nav_entry_matching_no_spine_document(self):
        f = dict(GOOD)
        f["OEBPS/nav.xhtml"] = '<nav><a href="nav.xhtml">x</a></nav>'
        self.assertIn("epub-nav", kinds(self.run_epub(f)))

    def test_broken_fragment_and_missing_target(self):
        f = dict(GOOD)
        f["OEBPS/c1.xhtml"] = '<h1 id="s">Uno</h1><a href="#zz">a</a><a href="gone.xhtml">b</a>'
        self.assertEqual(sorted(k for k in kinds(self.run_epub(f)) if k.startswith("epub-")), ["epub-fragment", "epub-link"])

    def test_not_a_zip(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.epub")
            with open(p, "wb") as f:
                f.write(b"nope")
            self.assertEqual(kinds(la.audit_epub(p)), ["epub"])


class Reports(unittest.TestCase):
    def test_separates_broken_from_unverified(self):
        fs = [la.finding(la.BROKEN, "path", "a.md:1", "x", "r"), la.finding(la.UNVERIFIED, "external", "a.md:2", "https://x", "r"),
              la.finding(la.NOT_EXECUTED, "epubcheck", "e", "", "absent")]
        self.assertEqual(la.summarize(fs), {"broken": 1, "unverified": 1, "not-executed": 1})
        text = la.report_markdown(fs)
        self.assertIn("Verdict: FAIL", text)
        self.assertIn("## not-executed (1)", text)
        self.assertNotIn("Verdict: FAIL", la.report_markdown(fs[1:]))
        self.assertIn('"broken": 1', la.report_json(fs))


if __name__ == "__main__":
    unittest.main()
