#!/usr/bin/env python3
"""Tests for tools/phase_lint.py and its use in invariant I14 (task P2-014). Run: python3 -I tools/test_phase_lint.py

Covers: the exercise-ID prefixes, collisions of BICHO and TORCE with them, the two ambiguity rules, and the
swap test of the task: change the catalog from BICHO to TORCE and re-apply a fixture.
"""
import io
import os
import re
import sys
import unittest
from contextlib import redirect_stdout

import polib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
import apply as ap  # noqa: E402
import catalog  # noqa: E402
import invariants as inv  # noqa: E402
import locale_check  # noqa: E402
import phase_lint as pl  # noqa: E402
import segment  # noqa: E402

TORCE = [("T", "Torcido"), ("O", "Operación"), ("R", "Rodeos"), ("C", "Consecuencias"), ("E", "Estado")]


def torce_catalog():
    flat = dict(catalog.load("es").flat)
    flat["acronym.word"] = "TORCE"
    for n, (letter, name) in enumerate(TORCE, 1):
        flat["phases.%d.letter" % n] = letter
        flat["phases.%d.name" % n] = name
    return catalog.Catalog("es", flat)


BICHO = catalog.load("es")
PREFIXES = pl.load_prefixes()


class Prefixes(unittest.TestCase):
    def test_recorded_prefixes(self):
        self.assertEqual(list("ABCDEFG"), PREFIXES)

    def test_json_matches_the_exercises_file(self):
        with open(pl.EXERCISES_MD, encoding="utf-8") as f:
            self.assertEqual([], pl.check_prefixes(PREFIXES, f.read()))

    def test_extra_prefix_in_the_file_is_reported(self):
        with open(pl.EXERCISES_MD, encoding="utf-8") as f:
            text = f.read() + "\n### H1. A new exercise\n"
        self.assertTrue(any("H" in p for p in pl.check_prefixes(PREFIXES, text)))

    def test_prefix_missing_from_the_file_is_reported(self):
        with open(pl.EXERCISES_MD, encoding="utf-8") as f:
            text = re.sub(r"^(#+ )E\d*\. ", r"\1", f.read(), flags=re.M)
        self.assertEqual(["prefix E is in phase-letters.json but not in lessons/exercises.md"],
                         pl.check_prefixes(PREFIXES, text))

    def test_cli_check_is_clean(self):
        out = io.StringIO()
        with redirect_stdout(out):
            self.assertEqual(0, pl.main(["--check"]))
        self.assertIn("OK", out.getvalue())


class Collisions(unittest.TestCase):
    def test_bicho_collides_on_b_and_c(self):
        self.assertEqual(["B", "C"], pl.collisions(BICHO, PREFIXES))

    def test_torce_collides_on_c_and_e(self):
        self.assertEqual(["C", "E"], pl.collisions(torce_catalog(), PREFIXES))

    def test_english_collides_on_e_and_d(self):
        self.assertEqual(["E", "D"], pl.collisions(catalog.load("en"), PREFIXES))

    def test_no_prefixes_no_collisions(self):
        self.assertEqual([], pl.collisions(BICHO, []))

    def test_report_lists_the_collisions(self):
        self.assertIn("collisions: B C", pl.report(BICHO, PREFIXES))


class Ambiguity(unittest.TestCase):
    def lint(self, text, cat=BICHO):
        return pl.ambiguity(text, cat, PREFIXES)

    def test_letter_with_its_name_passes(self):
        self.assertEqual([], self.lint("La fase B: Bicho raro cubre las semanas 1 y 2."))
        self.assertEqual([], self.lint("La fase C (Camino indirecto) cubre las semanas 7 a 10."))

    def test_bare_colliding_letter_after_phase_fails(self):
        self.assertTrue(self.lint("La fase B cubre las semanas 1 y 2."))

    def test_the_wrong_name_does_not_rescue_the_letter(self):
        self.assertTrue(self.lint("La fase B: Interpreta cubre las semanas 1 y 2."))

    def test_exercise_id_written_as_a_phase_fails(self):
        found = self.lint("Estás en la fase B3 del curso.")
        self.assertTrue(found and "B3" in found[0])

    def test_english_phase_word_is_covered_too(self):
        self.assertTrue(self.lint("The phase B3 is odd."))

    def test_free_letter_is_never_ambiguous(self):
        self.assertEqual([], self.lint("La fase H cubre las semanas 11 a 13."))
        self.assertEqual([], self.lint("La fase O cubre las semanas 14 y 15."))

    def test_a_real_exercise_reference_passes(self):
        self.assertEqual([], self.lint("Haz el ejercicio B3 durante la fase Octetos."))

    def test_code_and_placeholders_are_not_prose(self):
        self.assertEqual([], self.lint("Escribe `fase B` en el archivo."))
        self.assertEqual([], self.lint("La fase ⟦MACRO_0001⟧ sigue."))

    def test_unexpanded_macro_is_not_a_literal_letter(self):
        self.assertEqual([], self.lint("La fase {{phase.1.letter}} cubre las semanas 1 y 2."))

    def test_torce_flags_its_own_collisions_only(self):
        t = torce_catalog()
        self.assertTrue(self.lint("La fase C cubre las semanas 7 a 10.", t))
        self.assertTrue(self.lint("La fase E cubre las semanas 14 y 15.", t))
        self.assertEqual([], self.lint("La fase T cubre las semanas 1 y 2.", t))
        self.assertEqual([], self.lint("La fase B cubre las semanas 1 y 2.", t))
        self.assertEqual([], self.lint("La fase C: Consecuencias cubre las semanas 11 a 13.", t))

    def test_no_catalog_no_findings(self):
        self.assertEqual([], pl.ambiguity("La fase B3", None, PREFIXES))


class Swap(unittest.TestCase):
    """The task's accept test: swap the catalog from BICHO to TORCE and re-apply a fixture."""
    EN = (
        "Phase one is the first stop.\n\n"
        "The first letter of the acronym is recursive.\n"
    )
    ES = "La fase {{phase.1.letter}}: {{phase.1.name}} es la primera parada."
    ES2 = "La {{phase.1.letter}} de {{acronym.word}} es recursiva."

    def po(self, first=None, second=None):
        seg = segment.Segmentation(self.EN, "t.md")
        po = ap.new_po(seg, "t.md", identity=False)
        entries = list(po)
        entries[0].msgstr = first if first is not None else self.ES
        entries[1].msgstr = second if second is not None else self.ES2
        return po

    def ctx(self, cat):
        return inv.Context(cat=cat, lang_cat=catalog.load("en"), exercise_prefixes=PREFIXES, sentence_limit=40,
                           phase_names=["Weird", "Execution", "Indirect", "Results", "Data"])

    def test_both_catalogs_pass_the_locale_check(self):
        import yaml
        with open(locale_check.DEFAULT, encoding="utf-8") as f:
            d = yaml.safe_load(f)
        self.assertEqual([], locale_check.check(d))

    def test_reapply_with_bicho(self):
        text, stats = ap.apply_text(self.EN, self.po(), "t.md", BICHO)
        self.assertIn("La fase B: Bicho raro es la primera parada.", text)
        self.assertIn("La B de BICHO es recursiva.", text)
        self.assertEqual(2, stats["applied"])

    def test_reapply_with_torce(self):
        text, stats = ap.apply_text(self.EN, self.po(), "t.md", torce_catalog())
        self.assertIn("La fase T: Torcido es la primera parada.", text)
        self.assertIn("La T de TORCE es recursiva.", text)
        self.assertNotIn("BICHO", text)
        self.assertNotIn("Bicho", text)

    def test_same_po_gives_different_files(self):
        a, _ = ap.apply_text(self.EN, self.po(), "t.md", BICHO)
        b, _ = ap.apply_text(self.EN, self.po(), "t.md", torce_catalog())
        self.assertNotEqual(a, b)

    def test_i14_is_clean_for_both_alphabets(self):
        for cat in (BICHO, torce_catalog()):
            found = inv.check_po(self.EN, self.po(), "t.md", self.ctx(cat))
            self.assertEqual([], [f for f in found if f.inv == "I14"], cat.get("acronym.word"))

    def test_literal_letters_fail_under_their_own_catalog(self):
        # A literal never reaches a PO file under any alphabet, so a swap cannot leave old letters behind.
        po = self.po(first="La fase B: Bicho raro es la primera parada.", second="La B de BICHO es recursiva.")
        found = inv.check_po(self.EN, po, "t.md", self.ctx(BICHO))
        self.assertEqual(2, len([f for f in found if f.inv == "I14"]))
        po = self.po(first="La fase T: Torcido es la primera parada.", second="La T de TORCE es recursiva.")
        found = inv.check_po(self.EN, po, "t.md", self.ctx(torce_catalog()))
        self.assertEqual(2, len([f for f in found if f.inv == "I14"]))

    def test_macro_without_the_name_is_ambiguous_after_expansion(self):
        po = self.po(first="La fase {{phase.1.letter}} es la primera parada.")
        found = inv.check_po(self.EN, po, "t.md", self.ctx(BICHO))
        self.assertTrue([f for f in found if f.inv == "I14" and "collides" in f.msg])
        # the same text is fine under TORCE, where the first letter does not collide
        found = inv.check_po(self.EN, po, "t.md", self.ctx(torce_catalog()))
        self.assertEqual([], [f for f in found if f.inv == "I14" and "collides" in f.msg])

    def test_ambiguity_is_waivable_only_through_the_register(self):
        po = self.po(first="La fase {{phase.1.letter}} es la primera parada.")
        sid = list(po)[0].msgctxt
        ctx = self.ctx(BICHO)
        ctx.exceptions = {(sid, "I14")}
        found = inv.check_po(self.EN, po, "t.md", ctx)
        self.assertEqual([], [f for f in found if f.inv == "I14"])


class Real(unittest.TestCase):
    def test_load_context_carries_the_prefixes(self):
        ctx = inv.load_context("es")
        self.assertEqual(PREFIXES, ctx.exercise_prefixes)


if __name__ == "__main__":
    unittest.main()
