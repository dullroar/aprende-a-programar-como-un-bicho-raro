#!/usr/bin/env python3
"""Tests for lessons/book/locale/catalog.py. Run: python3 -I tools/test_catalog.py"""
import os
import shutil
import sys
import tempfile
import unittest

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
LOCALE = os.path.join(REPO, "lessons", "book", "locale")
sys.path.insert(0, LOCALE)
import catalog  # noqa: E402


class Scratch(unittest.TestCase):
    """Copy the real catalogs into a scratch directory so tests can damage them."""

    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="catalog-test-", dir=os.path.join(REPO, "translation", "work")
                                    if os.path.isdir(os.path.join(REPO, "translation", "work")) else None)
        for lang in ("en", "es"):
            shutil.copy(os.path.join(LOCALE, lang + ".yaml"), self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def edit(self, lang, fn):
        path = os.path.join(self.tmp, lang + ".yaml")
        with open(path, encoding="utf-8") as f:
            data = yaml.safe_load(f)
        fn(data)
        with open(path, "w", encoding="utf-8") as f:
            yaml.safe_dump(data, f, allow_unicode=True, sort_keys=False)


class RealCatalogs(unittest.TestCase):
    def test_real_catalogs_mirror(self):
        self.assertEqual(catalog.check(["es"]), [])

    def test_english_catalog_checks_against_itself(self):
        self.assertEqual(catalog.check(["en"]), [])

    def test_section_heading(self):
        self.assertEqual(catalog.load("en").get("diagrams.section"), "Program Flow")
        self.assertEqual(catalog.load("es").get("diagrams.section"), "Flujo del programa")

    def test_phase_letters(self):
        self.assertEqual("".join(catalog.load("en").phase_letters()), "WEIRD")
        self.assertEqual("".join(catalog.load("es").phase_letters()), "BICHO")

    def test_expand_macros(self):
        es = catalog.load("es")
        self.assertEqual(es.expand("Fase {{phase.1.letter}}: {{phase.1.name}} ({{acronym.word}})"),
                         "Fase B: Bicho raro (BICHO)")
        self.assertIn("**BICHO** significa", es.text("acronym.gloss"))
        self.assertIn("La B es recursiva.", es.text("acronym.gloss"))
        self.assertIn("The W is recursive.", catalog.load("en").text("acronym.gloss"))

    def test_list_keys_are_one_based(self):
        self.assertEqual(catalog.load("es").get("phases.5.mermaid_node_id"), "D")

    def test_mermaid_node_ids_same_in_both(self):
        en, es = catalog.load("en"), catalog.load("es")
        for n in range(1, 6):
            k = "phases.%d.mermaid_node_id" % n
            self.assertEqual(en.get(k), es.get(k))


class Loader(unittest.TestCase):
    def test_missing_key_raises(self):
        with self.assertRaises(catalog.MissingKeyError):
            catalog.load("es").get("diagrams.no_such_key")

    def test_missing_key_is_a_keyerror_and_names_the_key(self):
        try:
            catalog.load("es").get("study_guides.title_suffix")
        except KeyError as e:
            self.assertIn("study_guides.title_suffix", str(e))
        else:
            self.fail("no exception")

    def test_require_lists_all_missing(self):
        es = catalog.load("es")
        es.require(["diagrams.section", "acronym.word"])
        with self.assertRaises(catalog.MissingKeyError) as cm:
            es.require(["diagrams.section", "x.one", "x.two"])
        self.assertIn("x.one", str(cm.exception))
        self.assertIn("x.two", str(cm.exception))

    def test_unknown_language_fails(self):
        with self.assertRaises(catalog.CatalogError):
            catalog.load("fr")

    def test_unknown_macro_fails(self):
        with self.assertRaises(catalog.CatalogError):
            catalog.load("es").expand("{{phase.9.letter}}")
        with self.assertRaises(catalog.CatalogError):
            catalog.load("es").expand("{{whatever}}")

    def test_macro_to_missing_phase_fails(self):
        with self.assertRaises(catalog.MissingKeyError):
            catalog.load("es").expand("{{phase.9.letter}}")

    def test_non_macro_braces_left_alone_by_text_without_macros(self):
        self.assertEqual(catalog.load("es").expand("plain text"), "plain text")

    def test_text_of_non_string_fails(self):
        cat = catalog.Catalog("x", {"a": 3})
        with self.assertRaises(catalog.CatalogError):
            cat.text("a")

    def test_macro_target_with_macro_is_rejected(self):
        cat = catalog.Catalog("x", {"acronym.word": "{{phase.1.letter}}", "phases.1.letter": "B"})
        with self.assertRaises(catalog.CatalogError):
            cat.expand("{{acronym.word}}")


class Negatives(Scratch):
    def problems(self):
        return catalog.check(["es"], self.tmp)

    def test_scratch_copy_is_clean(self):
        self.assertEqual(self.problems(), [])

    def test_spanish_key_missing_fails(self):
        self.edit("es", lambda d: d["diagrams"].pop("section"))
        errs = self.problems()
        self.assertTrue(any("missing key diagrams.section" in e for e in errs), errs)

    def test_new_english_key_without_spanish_fails(self):
        self.edit("en", lambda d: d["diagrams"].update(extra="Extra"))
        self.assertTrue(any("missing key diagrams.extra" in e for e in self.problems()))

    def test_spanish_key_without_english_mirror_fails(self):
        self.edit("es", lambda d: d["diagrams"].update(extra="Extra"))
        self.assertTrue(any("no en mirror" in e for e in self.problems()))

    def test_empty_value_fails(self):
        self.edit("es", lambda d: d["diagrams"].update(section="  "))
        self.assertTrue(any("non-empty" in e for e in self.problems()))

    def test_missing_phase_fails(self):
        self.edit("es", lambda d: d["phases"].pop())
        self.assertTrue(any("phases.5" in e for e in self.problems()))

    def test_format_field_mismatch_fails(self):
        self.edit("en", lambda d: d["diagrams"].update(chapter="Ch {n}"))
        self.edit("es", lambda d: d["diagrams"].update(chapter="Cap. {num}"))
        self.assertTrue(any("format fields" in e for e in self.problems()))

    def test_unsupported_macro_in_value_fails(self):
        self.edit("es", lambda d: d["acronym"].update(trace="Mira {{foo.bar}}"))
        self.assertTrue(any("unsupported macro" in e for e in self.problems()))

    def test_macro_without_value_fails(self):
        self.edit("es", lambda d: d["acronym"].update(trace="Mira {{phase.7.name}}"))
        self.assertTrue(any("no catalog value" in e for e in self.problems()))

    def test_acronym_not_phase_letters_in_mirror_fails(self):
        self.edit("en", lambda d: d["acronym"].update(word="WIERD"))
        self.assertTrue(any("acronym.word" in e for e in self.problems()))

    def test_phase_index_mismatch_fails(self):
        def swap(d):
            d["phases"][0]["n"] = 2
        self.edit("es", swap)
        self.assertTrue(any("phases.1.n" in e for e in self.problems()))

    def test_cli_reports_failure(self):
        self.edit("es", lambda d: d["diagrams"].pop("section"))
        errs = catalog.check(["es"], self.tmp)
        self.assertTrue(errs)


if __name__ == "__main__":
    unittest.main()
