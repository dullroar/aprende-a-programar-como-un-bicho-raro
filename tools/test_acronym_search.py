"""Tests for tools/acronym_search.py. Run: python3 -I tools/test_acronym_search.py"""
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)

import acronym_search as a  # noqa: E402


class FilterTests(unittest.TestCase):
    def test_the_two_finalists_pass(self):
        self.assertTrue(a.is_candidate("BICHO"))
        self.assertTrue(a.is_candidate("torce"))

    def test_repeated_letter_is_rejected(self):
        # RAROS repeats R (plan 2.3: breaks N4)
        self.assertFalse(a.is_candidate("raros"))
        self.assertFalse(a.is_candidate("casas"))

    def test_wrong_length_is_rejected(self):
        self.assertFalse(a.is_candidate("bicho2"))
        self.assertFalse(a.is_candidate("bich"))
        self.assertFalse(a.is_candidate("bichos"))

    def test_non_letters_are_rejected(self):
        self.assertIsNone(a.fold("bi-ch"))
        self.assertFalse(a.is_candidate("b1cho"))
        self.assertFalse(a.is_candidate("bi'ho"))

    def test_accent_is_dropped_before_comparing(self):
        # "ánimo" folds to a,n,i,m,o: distinct. "áreas" folds to a,r,e,a,s: repeats a.
        self.assertTrue(a.is_candidate("ánimo"))
        self.assertFalse(a.is_candidate("áreas"))
        self.assertEqual(a.fold("Árbol"), "arbol")

    def test_enie_is_its_own_letter(self):
        self.assertEqual(a.fold("año"), "año")
        self.assertNotEqual(a.fold("año"), "ano")
        # n and ñ are different letters, so "niños" has five different letters
        self.assertTrue(a.is_candidate("niños"))
        self.assertFalse(a.is_candidate("ñoño"))
        self.assertTrue(a.is_candidate("cañon"))
        self.assertNotEqual(a.fold("cañon"), a.fold("canon"))


class ListTests(unittest.TestCase):
    def test_hunspell_style_lines_and_duplicates(self):
        lines = ["bicho/S\n", "BICHO\n", "torce\tverbo\n", "raros 1\n", "\n", "perro/SM\n"]
        self.assertEqual(a.candidates(lines), ["bicho", "torce"])  # perro repeats r

    def test_empty_list_gives_no_candidates(self):
        self.assertEqual(a.candidates([]), [])
        self.assertEqual(a.candidates(["\n", "   \n"]), [])

    def test_letter_counts(self):
        self.assertEqual(a.letter_counts(["bicho", "brujo", "torce"]), {"b": 2, "t": 1})


class CheckWordTests(unittest.TestCase):
    def test_passing_word(self):
        ok, why = a.check_word("BICHO")
        self.assertTrue(ok)

    def test_repeated_r_reason_names_the_letter(self):
        ok, why = a.check_word("RAROS")
        self.assertFalse(ok)
        self.assertIn("r", why)

    def test_wrong_length_reason(self):
        ok, why = a.check_word("BICHOS")
        self.assertFalse(ok)
        self.assertIn("6", why)


class CliTests(unittest.TestCase):
    def test_check_word_exit_codes(self):
        self.assertEqual(a.main(["--check-word", "BICHO", "--check-word", "TORCE"]), 0)
        self.assertEqual(a.main(["--check-word", "RAROS"]), 1)

    def test_missing_wordlist_exits_2(self):
        self.assertEqual(a.main(["translation/work/no-such-list.txt"]), 2)


if __name__ == "__main__":
    unittest.main()
