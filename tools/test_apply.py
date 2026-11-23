#!/usr/bin/env python3
"""Tests for tools/apply.py (plan 7.1, gate T0 through the PO layer). Run: python3 -I tools/test_apply.py"""
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stderr, redirect_stdout

import polib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lessons", "book", "locale"))
import apply as ap
import enpath  # noqa: E402
import catalog  # noqa: E402
import segment  # noqa: E402

ROOT = os.path.dirname(HERE)
FIXDIR = os.path.join(ROOT, "tests", "fixtures")

DOC = (
    "---\n"
    'title: "The weird way"\n'
    "slug: weird\n"
    "---\n"
    "\n"
    "# Phase one\n"
    "\n"
    "Run `make all` and see https://example.com now.\n"
    "Second line of the same paragraph.\n"
    "\n"
    "- First item\n"
    "- Second item with [[xref:foo]] inside\n"
    "\n"
    "```text\n"
    "keep this output\n"
    "```\n"
)


def po_for(text, identity=True, path="t.md"):
    return ap.new_po(segment.Segmentation(text, path), path, identity)


def seg_of(text):
    return segment.Segmentation(text, "t.md")


def set_msgstr(po, english_part, spanish):
    hits = [e for e in po if english_part in e.msgid]
    assert len(hits) == 1, (english_part, [e.msgid for e in po])
    hits[0].msgstr = spanish
    return hits[0]


class Identity(unittest.TestCase):
    def test_every_authored_file(self):
        files = segment.authored_files()
        self.assertGreaterEqual(len(files), 200)
        bad = {}
        for p in files:
            probs = ap.identity_check(segment.read_raw(enpath.load(ROOT).full(p)), p)      # `p` is the English key
            if probs:
                bad[p] = probs
        self.assertEqual(bad, {})

    def test_fixtures(self):
        for name in ("mixed.md", "mermaid.md", "hostile.md"):
            text = segment.read_raw(os.path.join(FIXDIR, name))
            self.assertEqual(ap.identity_check(text, name), [], name)

    def test_empty_po_and_identity_po_both_reproduce(self):
        for identity in (True, False):
            out, st = ap.apply_text(DOC, po_for(DOC, identity), "t.md")
            self.assertEqual(out, DOC)
            self.assertEqual(st["applied"], 5 if identity else 0)

    def test_crlf_file(self):
        crlf = DOC.replace("\n", "\r\n")
        out, _ = ap.apply_text(crlf, po_for(crlf), "t.md")
        self.assertEqual(out, crlf)

    def test_survives_po_serialization(self):
        po = polib.pofile(po_for(DOC).__unicode__(), wrapwidth=0)
        self.assertEqual(ap.apply_text(DOC, po, "t.md")[0], DOC)


class Replacement(unittest.TestCase):
    def test_only_translated_lines_change(self):
        po = po_for(DOC, identity=False)
        set_msgstr(po, "Phase one", "Fase uno")
        out, st = ap.apply_text(DOC, po, "t.md")
        a, b = DOC.split("\n"), out.split("\n")
        self.assertEqual(len(a), len(b))
        changed = [i for i in range(len(a)) if a[i] != b[i]]
        self.assertEqual(changed, [5])
        self.assertEqual(b[5], "# Fase uno")
        self.assertEqual(st["applied"], 1)

    def test_placeholders_restored_and_prefixes_kept(self):
        po = po_for(DOC, identity=False)
        e = [x for x in po if "Run" in x.msgid][0]
        self.assertIn("⟦", e.msgid)
        e.msgstr = e.msgid.replace("Run", "Ejecuta").replace("and see", "y mira").replace("now", "ahora")
        e.msgstr = e.msgstr.replace("Second line of the same paragraph.", "Segunda línea del mismo párrafo.")
        out, _ = ap.apply_text(DOC, po, "t.md")
        self.assertIn("Ejecuta `make all` y mira https://example.com ahora.", out)
        self.assertIn("Segunda línea del mismo párrafo.", out)

    def test_front_matter_and_list_item(self):
        po = po_for(DOC, identity=False)
        set_msgstr(po, "The weird way", "A la manera rara")
        set_msgstr(po, "First item", "Primer elemento")
        out, _ = ap.apply_text(DOC, po, "t.md")
        self.assertIn('title: "A la manera rara"\n', out)
        self.assertIn("- Primer elemento\n", out)
        self.assertIn("slug: weird\n", out)

    def test_fence_untouched_even_if_text_edited_elsewhere(self):
        po = po_for(DOC, identity=False)
        set_msgstr(po, "Phase one", "Fase uno")
        out, _ = ap.apply_text(DOC, po, "t.md")
        self.assertTrue(out.endswith("```text\nkeep this output\n```\n"))

    def test_fuzzy_entry_is_not_applied(self):
        po = po_for(DOC, identity=False)
        e = set_msgstr(po, "Phase one", "Fase uno")
        e.flags.append("fuzzy")
        out, st = ap.apply_text(DOC, po, "t.md")
        self.assertEqual(out, DOC)
        self.assertEqual(st["fuzzy"], 1)


class Macros(unittest.TestCase):
    cat = None

    @classmethod
    def setUpClass(cls):
        cls.cat = catalog.load("es")

    def test_phase_macros_expand_from_the_catalog(self):
        po = po_for(DOC, identity=False)
        set_msgstr(po, "Phase one", "Fase {{phase.1.letter}}: {{phase.1.name}}")
        out, _ = ap.apply_text(DOC, po, "t.md", self.cat)
        letter, name = self.cat.get("phases.1.letter"), self.cat.get("phases.1.name")
        self.assertIn("# Fase %s: %s\n" % (letter, name), out)
        self.assertNotIn("{{", out)

    def test_english_side_macros_are_left_alone(self):
        doc = "Texto con {{phase.1.letter}} en inglés.\n"
        seg = seg_of(doc)
        self.assertEqual(len(seg.segments()), 1)
        po = po_for(doc, identity=True)
        out, _ = ap.apply_text(doc, po, "t.md", self.cat)
        self.assertEqual(out, doc)  # masked in the source, so never expanded

    def test_unknown_macro_fails_closed(self):
        po = po_for(DOC, identity=False)
        set_msgstr(po, "Phase one", "Fase {{phase.99.letter}}")
        with self.assertRaises(ap.ApplyError):
            ap.apply_text(DOC, po, "t.md", self.cat)

    def test_macro_to_missing_key_fails_closed(self):
        po = po_for(DOC, identity=False)
        set_msgstr(po, "Phase one", "Fase {{nonsense}}")
        with self.assertRaises(ap.ApplyError):
            ap.apply_text(DOC, po, "t.md", self.cat)


class FailClosed(unittest.TestCase):
    """Negative cases: each must raise, never write a partly wrong file."""

    def test_dropped_placeholder(self):
        po = po_for(DOC, identity=False)
        set_msgstr(po, "Run", "Ejecuta y mira ahora.\nSegunda línea.")
        with self.assertRaises(ap.ApplyError):
            ap.apply_text(DOC, po, "t.md")

    def test_invented_placeholder(self):
        po = po_for(DOC, identity=False)
        e = set_msgstr(po, "Phase one", "Fase uno ⟦CODE_0099⟧")
        self.assertTrue(e.msgstr)
        with self.assertRaises(ap.ApplyError):
            ap.apply_text(DOC, po, "t.md")

    def test_orphan_entry_strict_vs_lenient(self):
        po = po_for(DOC, identity=False)
        po.append(polib.POEntry(msgctxt="s-000000000000-0099", msgid="Gone", msgstr="Ido"))
        with self.assertRaises(ap.ApplyError):
            ap.apply_text(DOC, po, "t.md")
        out, st = ap.apply_text(DOC, po, "t.md", strict=False)
        self.assertEqual(out, DOC)
        self.assertEqual(st["orphan"], 1)

    def test_stale_msgid(self):
        po = po_for(DOC, identity=False)
        e = set_msgstr(po, "Phase one", "Fase uno")
        e.msgid = "Phase ONE (old English)"
        with self.assertRaises(ap.ApplyError):
            ap.apply_text(DOC, po, "t.md")

    def test_english_changed_after_po_was_made(self):
        po = po_for(DOC, identity=True)
        changed = DOC.replace("Phase one", "Phase two")
        with self.assertRaises(ap.ApplyError):
            ap.apply_text(changed, po, "t.md")

    def test_multiline_target_for_heading(self):
        po = po_for(DOC, identity=False)
        set_msgstr(po, "Phase one", "Fase\nuno")
        with self.assertRaises(ap.ApplyError):
            ap.apply_text(DOC, po, "t.md")

    def test_unsupported_source_is_refused(self):
        bad = "para\n\n    indented code\n"
        with self.assertRaises(ap.ApplyError):
            ap.apply_text(bad, polib.POFile(), "t.md")

    def test_identity_check_detects_a_broken_apply(self):
        original = ap.apply_text

        def broken(text, po, rel_path="", cat=None, strict=True):
            out, st = original(text, po, rel_path, cat, strict)
            return out + "x", st

        ap.apply_text = broken
        try:
            probs = ap.identity_check(DOC, "t.md")
        finally:
            ap.apply_text = original
        self.assertEqual(len(probs), 2)
        self.assertIn("changed the file", probs[0])

    def test_duplicate_and_missing_context_in_po_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "x.po")
            with open(path, "w", encoding="utf-8") as f:
                f.write('msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n'
                        'msgid "A"\nmsgstr "B"\n')
            with self.assertRaises(ap.ApplyError):
                ap.load_po(path)
            with open(path, "w", encoding="utf-8") as f:
                f.write('msgid ""\nmsgstr ""\n"Content-Type: text/plain; charset=UTF-8\\n"\n\n'
                        'msgctxt "s-aaaaaaaaaaaa-0000"\nmsgid "A"\nmsgstr "B"\n\n'
                        'msgctxt "s-aaaaaaaaaaaa-0000"\nmsgid "A"\nmsgstr "C"\n')
            with self.assertRaises(ap.ApplyError):
                ap.load_po(path)


class Cli(unittest.TestCase):
    def run_cli(self, *argv):
        out, err = io.StringIO(), io.StringIO()
        with redirect_stdout(out), redirect_stderr(err):
            rc = ap.main(["apply.py"] + list(argv))
        return rc, out.getvalue() + err.getvalue()

    def test_identity_cli_on_fixture(self):
        rc, text = self.run_cli("--identity", os.path.join(FIXDIR, "mixed.md"))
        self.assertEqual(rc, 0)
        self.assertIn("apply identity OK", text)

    def test_init_then_apply_then_write(self):
        with tempfile.TemporaryDirectory() as d:
            src, po = os.path.join(d, "doc.md"), os.path.join(d, "doc.md.po")
            with open(src, "w", encoding="utf-8", newline="") as f:
                f.write(DOC)
            rc, _ = self.run_cli("--init", src, "--po", po)
            self.assertEqual(rc, 0)
            rc, _ = self.run_cli("--init", src, "--po", po)
            self.assertEqual(rc, 1)  # never overwrites a PO file
            pf = polib.pofile(po, wrapwidth=0)
            set_msgstr(pf, "Phase one", "Fase {{phase.1.letter}}")
            pf.save(po)
            rc, _ = self.run_cli(src, "--po", po)  # dry run
            self.assertEqual(rc, 0)
            with open(src, encoding="utf-8", newline="") as f:
                self.assertEqual(f.read(), DOC)
            rc, _ = self.run_cli(src, "--po", po, "--write")
            self.assertEqual(rc, 0)
            with open(src, encoding="utf-8", newline="") as f:
                new = f.read()
            letter = catalog.load("es").get("phases.1.letter")
            self.assertIn("# Fase %s\n" % letter, new)

    def test_bad_po_exits_1_and_leaves_file(self):
        with tempfile.TemporaryDirectory() as d:
            src, po = os.path.join(d, "doc.md"), os.path.join(d, "doc.md.po")
            with open(src, "w", encoding="utf-8", newline="") as f:
                f.write(DOC)
            self.run_cli("--init", src, "--po", po)
            pf = polib.pofile(po, wrapwidth=0)
            set_msgstr(pf, "Phase one", "Fase ⟦CODE_0042⟧")
            pf.save(po)
            rc, text = self.run_cli(src, "--po", po, "--write")
            self.assertEqual(rc, 1)
            self.assertIn("FAIL", text)
            with open(src, encoding="utf-8", newline="") as f:
                self.assertEqual(f.read(), DOC)


class CategoryRows(unittest.TestCase):
    """Decision 11: only an output row inside a fence (category word, then TAB) is rewritten."""

    def test_row_in_fence_only(self):
        text = "Meetings\tprose row\n```text\nMeetings\t11\nCoding in prose\nDebugging\t12\n```\nLearning\tafter\n"
        out = ap.localize_category_rows(text)
        self.assertEqual(out, "Meetings\tprose row\n```text\nReuniones\t11\nCoding in prose\nDepuración\t12\n```\nLearning\tafter\n")

    def test_idempotent_and_no_other_word(self):
        text = "```\nReuniones\t1\nMeetingsX\t2\nXCoding\t3\n```\n"
        self.assertEqual(ap.localize_category_rows(text), text)


class CategoryList(unittest.TestCase):
    """F2-007-awk-weird: the quoted four-word list in a fenced one-liner follows the code; other text stays."""

    def test_quoted_list_in_fence(self):
        text = '```sh\nsplit("Meetings Coding Debugging Learning",C)\n```\n'
        self.assertEqual(ap.localize_category_rows(text),
                         '```sh\nsplit("Reuniones Programación Depuración Aprendizaje",C)\n```\n')

    def test_other_orders_and_prose_stay(self):
        text = '"Coding Meetings Debugging Learning"\n```\nsplit("Coding Meetings Debugging Learning")\nMeetings Coding Debugging Learning\n```\n'
        self.assertEqual(ap.localize_category_rows(text), text)


class CategoryQuotedList(unittest.TestCase):
    """F2-007-lisp-weird: a copied Lisp list literal of the four quoted words follows the code; other text stays."""

    def test_quoted_words_in_fence(self):
        text = "```lisp\n'#1=(\"Meetings\" \"Coding\" \"Debugging\" \"Learning\" . #1#)\n```\n"
        self.assertEqual(ap.localize_category_rows(text),
                         "```lisp\n'#1=(\"Reuniones\" \"Programación\" \"Depuración\" \"Aprendizaje\" . #1#)\n```\n")

    def test_other_order_and_prose_stay(self):
        text = "\"Meetings\" \"Coding\" \"Debugging\" \"Learning\"\n```lisp\n(\"Coding\" \"Meetings\" \"Debugging\" \"Learning\")\n```\n"
        self.assertEqual(ap.localize_category_rows(text), text)


class CategoryWords(unittest.TestCase):
    """F2-006b: prose and inline spans of a localized family follow the code; fences, glosses and links stay."""

    def test_spans_and_prose(self):
        text = "Ciclo: `Meetings`, `Coding` y Learning. | Debugging, 12 horas |\n"
        self.assertEqual(ap.localize_category_words(text), "Ciclo: `Reuniones`, `Programación` y Aprendizaje. | Depuración, 12 horas |\n")

    def test_gloss_link_fence_and_partial_words_stay(self):
        text = "**Depuración** (Debugging) [x](a/Coding.md)\n```\nMeetings\n```\nMeetingsX XCoding\n"
        self.assertEqual(ap.localize_category_words(text), text)

    def test_bold_only_concept_row_label_stays(self):
        """Negative case: a '| **Debugging** |' concept-table label is not a card category."""
        text = "| **Debugging** | Un fallo. | Otra fila con Debugging y `Coding`. |\n"
        want = "| **Debugging** | Un fallo. | Otra fila con Depuración y `Programación`. |\n"
        self.assertEqual(ap.localize_category_words(text), want)

    def test_glued_macro_example_follows_and_other_glue_stays(self):
        text = "`Meetingstc_tab` y `MeetingsX`\n"
        self.assertEqual(ap.localize_category_words(text), "`Reunionestc_tab` y `MeetingsX`\n")

    def test_mermaid_labels_and_accdescr(self):
        text = '```mermaid\nstateDiagram-v2\n    accDescr: Empieza como Meetings y sigue con Coding.\n    state "Meetings" as M\n```\n'
        want = '```mermaid\nstateDiagram-v2\n    accDescr: Empieza como Reuniones y sigue con Programación.\n    state "Reuniones" as M\n```\n'
        self.assertEqual(ap.localize_category_words(text), want)

    def test_mermaid_other_lines_and_plain_fences_stay(self):
        """Negative case: only accDescr and state labels change; edges, comments and non-mermaid fences stay."""
        text = '```mermaid\nflowchart TD\n    Meetings --> Coding\n    %% Debugging\n```\n```text\naccDescr: Meetings\nstate "Coding"\n```\n'
        self.assertEqual(ap.localize_category_words(text), text)

    def test_idempotent(self):
        once = ap.localize_category_words("`Meetings`")
        self.assertEqual(ap.localize_category_words(once), once)

    def test_non_listed_file_stays_english(self):
        """Negative case: a span in a family that is not localized is not touched by apply_text."""
        import polib
        text = "Usa `Meetings` aqui.\n"
        po = polib.POFile()
        out, _ = ap.apply_text(text, po, "src/python/README.md")
        self.assertEqual(out, text)
        self.assertNotIn("src/python/README.md", ap.category_prose_files())
        self.assertIn("src/lisp/README.md", ap.category_prose_files())


if __name__ == "__main__":
    unittest.main()
