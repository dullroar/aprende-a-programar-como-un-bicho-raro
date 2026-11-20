#!/usr/bin/env python3
"""Tests for tools/anchors.py (plan 8.2, I4). Run: python3 -I tools/test_anchors.py"""
import importlib.util
import io
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
import anchors as an  # noqa: E402
import invariants  # noqa: E402

EN = (
    "# The weird way\n\n"
    "## What is a bug?\n\n"
    "Text with [a link](#what-is-a-bug) and [other](other.md#run-it).\n\n"
    "## Run it\n\n"
    "```bash\n## Run it\n[x](#run-it)\n```\n\n"
    "## Run it\n"
)
ES = (
    "# El camino raro\n\n"
    "## ¿Qué es un bug?\n\n"
    "Texto con [un enlace](#what-is-a-bug) y [otro](other.md#run-it).\n\n"
    "## Ejecútalo\n\n"
    "```bash\n## Run it\n[x](#run-it)\n```\n\n"
    "## Ejecútalo\n"
)
OTHER_EN = "# Other\n\n## Run it\n"
OTHER_ES = "# Otro\n\n## ¡Ejecútalo ya!\n"


def doc_for():
    return an.build_map({"lessons/a.md": (EN, ES), "lessons/other.md": (OTHER_EN, OTHER_ES)})


def pandoc_ids(md):
    out = subprocess.run(["pandoc", "-f", "gfm+gfm_auto_identifiers", "-t", "html"], input=md, capture_output=True, text=True, check=True).stdout
    return re.findall(r'<h\d id="([^"]*)"', out)


class SlugTests(unittest.TestCase):
    def test_plain_english(self):
        self.assertEqual(an.github_slug("What is a bug?"), "what-is-a-bug")

    def test_inverted_punctuation_vanishes(self):
        self.assertEqual(an.github_slug("¿Qué es un bug?"), "qué-es-un-bug")
        self.assertEqual(an.github_slug("¡Hola, mundo!"), "hola-mundo")

    def test_accents_and_enye_stay(self):
        self.assertEqual(an.github_slug("Año nuevo, niño"), "año-nuevo-niño")
        self.assertEqual(an.github_slug("Ejecútalo"), "ejecútalo")

    def test_uppercase_accents_lowered(self):
        self.assertEqual(an.github_slug("ÉSTE: SÍ"), "éste-sí")

    def test_punctuation_and_quotes_dropped_hyphen_and_underscore_kept(self):
        self.assertEqual(an.github_slug('Un "bug" (raro): sí/no; ¿vale? -- x_y'), "un-bug-raro-síno-vale----x_y")

    def test_backticks_and_emphasis_removed(self):
        self.assertEqual(an.github_slug("Ejecuta `make all` **ahora**"), "ejecuta-make-all-ahora")
        self.assertEqual(an.github_slug("Un _gran_ día"), "un-gran-día")

    def test_underscore_inside_word_is_kept(self):
        self.assertEqual(an.github_slug("snake_case name"), "snake_case-name")

    def test_link_text_only(self):
        self.assertEqual(an.github_slug("Ver [la guía](guia.md) ya"), "ver-la-guía-ya")

    def test_digits_leading_kept(self):
        self.assertEqual(an.github_slug("1. Año nuevo"), "1-año-nuevo")

    def test_build_slug_is_the_repo_function(self):
        for name in ("build.py", "study_guides.py", "cs.py"):
            with open(os.path.join(ROOT, "lessons", "book", name), encoding="utf-8") as f:
                src = f.read()
            m = re.search(r"^def slug\(heading\):\n(?:    .*\n)+", src, re.M)
            self.assertIsNotNone(m, name)
            ns = {"re": re}
            exec(m.group(0), ns)
            for h in ("What is a bug?", "¿Qué es `un` bug?", "Año nuevo", "A  b", "x_y-z"):
                self.assertEqual(an.build_slug(h), ns["slug"](h), (name, h))

    def test_build_and_github_agree_on_spanish_nfc(self):
        for h in ("¿Qué es un bug?", "¡Hola, `mundo`!", "Éste: sí", "Año nuevo", "Cómo funciona (y por qué)"):
            self.assertEqual(an.build_slug(h), an.github_slug(h), h)

    def test_nfd_text_differs_and_is_reported(self):
        nfd = unicodedata.normalize("NFD", "Ejecútalo")
        self.assertNotEqual(an.build_slug(nfd), an.github_slug(nfd))
        self.assertEqual(unicodedata.normalize("NFC", an.github_slug(nfd)), "ejecútalo")
        problems = an.slug_problems("a.md", "## %s\n" % nfd)
        self.assertEqual(len(problems), 1)
        self.assertIn("differs", problems[0])

    def test_no_problem_for_nfc(self):
        self.assertEqual(an.slug_problems("a.md", "## Ejecútalo\n## ¿Qué?\n"), [])

    @unittest.skipUnless(shutil.which("pandoc"), "pandoc not installed")
    def test_matches_real_pandoc_ids(self):
        heads = ["¿Qué es un \"bug\"?", "Éste: sí", "Éste: sí", "¡Hola, `mundo`!", "¡Hola, mundo!", "1. Año nuevo",
                 "Un **gran** día", "snake_case (x)", "Ver [la guía](guia.md)"]
        md = "".join("## %s\n\n" % h for h in heads)
        got = an.numbered_ids([an.github_slug(h) for h in heads])
        self.assertEqual(got, pandoc_ids(md))


class NumberingTests(unittest.TestCase):
    def test_repeats_numbered_in_order(self):
        self.assertEqual(an.numbered_ids(["a", "b", "a", "a"]), ["a", "b", "a-1", "a-2"])

    def test_duplicate_headings_in_one_file(self):
        ids = [i for _, i in an.file_ids("## Ejecútalo\n\n## Otro\n\n## Ejecútalo\n")]
        self.assertEqual(ids, ["ejecútalo", "otro", "ejecútalo-1"])

    def test_numbering_resets_per_file_but_not_across_the_book(self):
        texts = {"a.md": "## Run it\n## Run it\n", "b.md": "## Run it\n"}
        self.assertEqual(an.file_ids(texts["b.md"])[0][1], "run-it")
        self.assertEqual(an.book_ids(texts), {"a.md": ["run-it", "run-it-1"], "b.md": ["run-it-2"]})

    def test_new_duplicate_created_by_translation_is_numbered(self):
        # two different English headings that translate to the same Spanish words
        en, es = "## Run it\n\n## Execute\n", "## Ejecútalo\n\n## Ejecútalo\n"
        e = an.pair_file(en, es)
        self.assertEqual(e["map"], {"run-it": "ejecútalo", "execute": "ejecútalo-1"})


class HeadingScanTests(unittest.TestCase):
    def test_fenced_headings_and_front_matter_skipped(self):
        text = '---\ntitle: "# not"\n---\n\n# Real\n\n```text\n# fake\n```\n\n~~~\n## fake2\n~~~\n\n## Two ##\n'
        self.assertEqual([h.text for h in an.headings(text)], ["Real", "Two"])

    def test_line_numbers_and_levels(self):
        hs = an.headings("a\n\n## B\n\n### C\n")
        self.assertEqual([(h.line, h.level) for h in hs], [(3, 2), (5, 3)])

    def test_setext_fails_closed(self):
        with self.assertRaises(an.AnchorError):
            an.headings("Title\n=====\n")

    def test_quoted_heading_fails_closed(self):
        with self.assertRaises(an.AnchorError):
            an.headings("> ## Quoted\n")

    def test_same_headings_as_the_build_scanner_on_every_english_file(self):
        spec = importlib.util.spec_from_file_location("diagrams_for_test", os.path.join(ROOT, "lessons", "book", "diagrams.py"))
        diagrams = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(diagrams)
        checked = 0
        for rel in an.markdown_files():
            text = an.read_es(rel)
            body = text
            if text.startswith("---\n"):   # the build scans bodies; keep only files where it makes no difference
                if re.search(r"^#", text.split("\n---\n", 1)[0], re.M):
                    continue
            theirs = [it[2] for it in diagrams.scan(text) if it[0] == "heading"]
            mine = [h.text for h in an.headings(body)]
            self.assertEqual(mine, theirs, rel)
            checked += 1
        self.assertGreater(checked, 100)


class PairingTests(unittest.TestCase):
    def test_map(self):
        e = an.pair_file(EN, ES)
        self.assertEqual(e["map"], {"the-weird-way": "el-camino-raro", "what-is-a-bug": "qué-es-un-bug",
                                    "run-it": "ejecútalo", "run-it-1": "ejecútalo-1"})
        self.assertEqual(e["headings"][1]["en"], "What is a bug?")
        self.assertEqual(e["headings"][1]["line"], 3)

    def test_heading_count_mismatch_fails(self):
        with self.assertRaises(an.AnchorError):
            an.pair_file(EN, ES + "\n## Extra\n")

    def test_heading_level_mismatch_fails(self):
        with self.assertRaises(an.AnchorError):
            an.pair_file("## A\n", "### A\n")

    def test_identity_pair_is_identity_map(self):
        e = an.pair_file(EN, EN)
        self.assertTrue(all(k == v for k, v in e["map"].items()))

    def test_dumps_is_deterministic_and_utf8(self):
        d = doc_for()
        self.assertEqual(an.dumps(d), an.dumps(json.loads(an.dumps(d))))
        self.assertIn("¿Qué es un bug?", an.dumps(d))


class LinkTests(unittest.TestCase):
    def test_resolve(self):
        self.assertEqual(an.resolve("lessons/a.md", "#x"), ("lessons/a.md", "x"))
        self.assertEqual(an.resolve("lessons/a/b.md", "../c.md#y"), ("lessons/c.md", "y"))
        self.assertEqual(an.resolve("lessons/a.md", "my%20file.md#z"), ("lessons/my file.md", "z"))
        self.assertIsNone(an.resolve("lessons/a.md", "https://example.com/x#y"))
        self.assertIsNone(an.resolve("lessons/a.md", "mailto:a@b.c"))
        self.assertIsNone(an.resolve("lessons/a.md", "/abs.md#x"))
        self.assertIsNone(an.resolve("lessons/a.md", "../../../out.md#x"))
        self.assertIsNone(an.resolve("lessons/a.md", ""))

    def test_cs_source_chapter_reads_on_the_generated_page(self):
        rel = "lessons/cs-source/chapters/05-x.md"
        self.assertEqual(an.resolve(rel, "#weird-machines"), ("lessons/cs/05-x.md", "weird-machines"))
        self.assertEqual(an.resolve("lessons/cs-source/concepts/a.md", "#w"), ("lessons/cs-source/concepts/a.md", "w"))

    def test_remap_same_file_and_cross_file(self):
        out = an.remap_text(EN, "lessons/a.md", doc_for())
        self.assertIn("[a link](#qué-es-un-bug)", out)
        self.assertIn("[other](other.md#ejecútalo-ya)", out)

    def test_remap_leaves_fenced_code_alone(self):
        out = an.remap_text(EN, "lessons/a.md", doc_for())
        self.assertIn("```bash\n## Run it\n[x](#run-it)\n```", out)

    def test_remap_is_idempotent_on_spanish_ids_that_differ_and_keeps_eol(self):
        text = EN.replace("\n", "\r\n")
        out = an.remap_text(text, "lessons/a.md", doc_for())
        self.assertIn("\r\n", out)
        self.assertNotIn("\n\n", out.replace("\r\n", ""))

    def test_remap_external_and_plain_links_untouched(self):
        text = "[w](https://en.wikipedia.org/wiki/A#b) [f](../src/x.py) [d](other.md)\n"
        self.assertEqual(an.remap_text(text, "lessons/a.md", doc_for()), text)

    def test_remap_reference_definition(self):
        text = "[r]: other.md#run-it \"title\"\n"
        out = an.remap_text(text, "lessons/a.md", doc_for())
        self.assertEqual(out, "[r]: other.md#ejecútalo-ya \"title\"\n")

    def test_remap_unknown_anchor_is_reported_and_left(self):
        missing = []
        text = "[x](#no-such-heading)\n"
        self.assertEqual(an.remap_text(text, "lessons/a.md", doc_for(), missing), text)
        self.assertEqual(len(missing), 1)

    def test_remap_file_without_headings_in_map_is_left(self):
        text = "[x](../src/Main.java#L10)\n"
        self.assertEqual(an.remap_text(text, "lessons/a.md", doc_for()), text)

    def test_check_links_accepts_remapped_text_and_rejects_english_fragment(self):
        d = doc_for()
        good = an.remap_text(EN, "lessons/a.md", d)
        self.assertEqual(an.check_links("lessons/a.md", good, d), [])
        bad = an.check_links("lessons/a.md", ES, d)       # ES still carries the English fragments
        self.assertEqual(len(bad), 2)
        self.assertIn("what-is-a-bug", bad[0])

    def test_check_links_ignores_links_in_fences(self):
        d = doc_for()
        self.assertEqual(an.check_links("lessons/a.md", "```\n[x](#nope)\n```\n", d), [])

    def test_broken_spanish_anchor_is_caught(self):
        d = doc_for()
        text = an.remap_text(EN, "lessons/a.md", d).replace("#qué-es-un-bug", "#que-es-un-bug")   # lost the accent
        self.assertEqual(len(an.check_links("lessons/a.md", text, d)), 1)

    def test_I4_with_dest_map(self):
        d = doc_for()
        m = an.dest_map(EN, "lessons/a.md", d)
        ctx = invariants.Context(anchor_map=m)
        good = an.remap_text(EN, "lessons/a.md", d)
        self.assertEqual([f for f in invariants.check_files(EN, good, "lessons/a.md", ctx) if f.inv == "I4"], [])
        bad = invariants.check_files(EN, EN, "lessons/a.md", ctx)      # fragments not remapped
        self.assertTrue([f for f in bad if f.inv == "I4"])


class WholeTreeTests(unittest.TestCase):
    def test_check_passes_on_the_working_tree(self):
        self.assertEqual(an.check_all(), [])

    def test_every_english_link_with_a_fragment_resolves(self):
        d = an.load()
        for rel in an.markdown_files():
            self.assertEqual(an.check_links(rel, an.read_es(rel), d), [], rel)

    def test_stored_document_is_current(self):
        doc, _ = an.current_document()
        self.assertEqual(an.load(), doc)

    def test_cli_slug(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = an.main(["anchors.py", "--slug", "¿Qué es?"])
        self.assertEqual(rc, 0)
        self.assertIn("github: qué-es", buf.getvalue())

    def test_cli_usage_exit_2(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(an.main(["anchors.py"]), 2)

    def test_cli_remap_rewrites_in_place_and_fails_on_unknown(self):
        d = doc_for()
        with tempfile.TemporaryDirectory(dir=os.path.join(ROOT, "translation", "work")) as tmp:
            old = an.ANCHORS_PATH
            an.ANCHORS_PATH = os.path.join(tmp, "anchors.json")
            try:
                # the CLI resolves the rel path against the repo root, so build a file with a matching rel path
                path = os.path.join(ROOT, "lessons", "zz-anchors-test.md")
                d["files"]["lessons/zz-anchors-test.md"] = an.pair_file(EN, ES)
                with open(an.ANCHORS_PATH, "w", encoding="utf-8") as f:
                    f.write(an.dumps(d))
                try:
                    with open(path, "w", encoding="utf-8", newline="") as f:
                        f.write("[x](#what-is-a-bug)\n")
                    with redirect_stdout(io.StringIO()):
                        self.assertEqual(an.main(["anchors.py", "--remap", path]), 0)
                    with open(path, encoding="utf-8") as f:
                        self.assertEqual(f.read(), "[x](#qué-es-un-bug)\n")
                    with open(path, "w", encoding="utf-8", newline="") as f:
                        f.write("[x](#nope)\n")
                    buf = io.StringIO()
                    with redirect_stdout(buf):
                        self.assertEqual(an.main(["anchors.py", "--remap", path]), 1)
                    self.assertIn("unknown anchor", buf.getvalue())
                    with open(path, encoding="utf-8") as f:
                        self.assertEqual(f.read(), "[x](#nope)\n")
                finally:
                    if os.path.exists(path):
                        os.remove(path)
            finally:
                an.ANCHORS_PATH = old


if __name__ == "__main__":
    unittest.main()
