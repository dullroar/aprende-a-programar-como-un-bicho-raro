"""Tests for tools/humor_register.py. Run: python3 -I tools/test_humor_register.py"""
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
os.chdir(ROOT)

import humor_register as hr  # noqa: E402


class RegisterTests(unittest.TestCase):
    def test_committed_register_passes_check(self):
        self.assertEqual(hr.check(), [])

    def test_every_planned_entry_is_in_the_register(self):
        ids = set(hr.load())
        self.assertEqual(ids, {e[0] for e in hr.ENTRIES})

    def test_all_five_recurring_section_headings_are_covered(self):
        english = {r["english"] for r in hr.load().values()}
        for h in ("Behold the monstrosity", "How the hell does that work?",
                  "Do this in production and you're fired", "Now break it yourself",
                  "Under what circumstances would this terrible idea become reasonable?"):
            self.assertIn(h, english)

    def test_heading_in_code_fence_is_not_counted(self):
        # lessons/languages/lisp.md has "# PUNCH had 5 OR methods..." inside a fence.
        self.assertEqual(hr.find_headings("PUNCH had 5 OR methods and 3 ran",
                                          hr.markdown_files()), [])

    def test_fabricated_heading_is_not_found(self):
        self.assertEqual(hr.find_headings("This heading does not exist anywhere",
                                          hr.markdown_files()), [])


class NegativeCheckTests(unittest.TestCase):
    def setUp(self):
        self.rows = hr.load()
        self.orig_load = hr.load

    def tearDown(self):
        hr.load = self.orig_load

    def run_with(self, mutate):
        rows = json.loads(json.dumps(self.rows))
        mutate(rows)
        hr.load = lambda: rows
        return hr.check()

    def test_fabricated_english_is_reported(self):
        def m(rows):
            rows["H002"]["english"] = "Behold the fabricated monstrosity"
        self.assertTrue(any("not found" in p for p in self.run_with(m)))

    def test_wrong_occurrence_count_is_reported(self):
        def m(rows):
            rows["H002"]["occurrences"] += 1
        self.assertTrue(any("occurrences" in p for p in self.run_with(m)))

    def test_bad_status_is_reported(self):
        def m(rows):
            rows["H003"]["status"] = "maybe"
        self.assertTrue(any("bad status" in p for p in self.run_with(m)))

    def test_transcreated_without_spanish_is_reported(self):
        def m(rows):
            rows["H003"]["status"] = "transcreated"
        self.assertTrue(any("needs a Spanish" in p for p in self.run_with(m)))

    def test_flattened_without_reason_is_reported(self):
        def m(rows):
            rows["H003"]["status"] = "deliberately-flattened"
        self.assertTrue(any("without a reason" in p for p in self.run_with(m)))

    def test_missing_description_is_reported(self):
        def m(rows):
            rows["H004"]["english_does"] = ""
        self.assertTrue(any("english_does" in p for p in self.run_with(m)))

    def test_empty_register_is_reported(self):
        hr.load = lambda: {}
        self.assertTrue(hr.check())


if __name__ == "__main__":
    unittest.main()
