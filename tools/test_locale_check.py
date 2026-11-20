#!/usr/bin/env python3
"""Tests for tools/locale_check.py. Run: python3 -I tools/test_locale_check.py"""
import copy
import os
import sys
import unittest

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import locale_check as lc  # noqa: E402


def load():
    with open(lc.DEFAULT, encoding="utf-8") as f:
        return yaml.safe_load(f)


class LocaleCheck(unittest.TestCase):
    def test_real_catalog_passes(self):
        self.assertEqual(lc.check(load()), [])

    def test_five_phases_and_bicho(self):
        d = load()
        self.assertEqual("".join(p["letter"] for p in d["phases"]), "BICHO")
        self.assertEqual(d["acronym"]["word"], "BICHO")

    def test_torce_swap_works(self):
        d = load()
        for p, (l, n) in zip(d["phases"], [("T", "Torcido"), ("O", "Operación"), ("R", "Rodeos"),
                                          ("C", "Consecuencias"), ("E", "Estado")]):
            p["letter"], p["name"] = l, n
        d["acronym"]["word"] = "TORCE"
        d["acronym"]["expansion"] = "Torcido, Operación, Rodeos, Consecuencias y Estado"
        d["acronym"]["gloss"] = "**{{acronym.word}}** significa **" + d["acronym"]["expansion"] + "**."
        d["acronym"]["aside"] = "{{acronym.word}} significa **" + d["acronym"]["expansion"] + "**. Claro que no."
        self.assertEqual(lc.check(d), [])

    def test_missing_phase_fails(self):
        d = load()
        del d["phases"][4]
        self.assertTrue(lc.check(d))

    def test_duplicated_letter_fails(self):
        d = load()
        d["phases"][1]["letter"] = "B"
        self.assertTrue(any("duplicate" in e for e in lc.check(d)))

    def test_changed_order_fails(self):
        d = load()
        d["phases"][0], d["phases"][1] = d["phases"][1], d["phases"][0]
        self.assertTrue(lc.check(d))

    def test_surviving_english_letter_fails(self):
        d = load()
        d["phases"][0]["letter"] = "W"
        d["phases"][0]["name"] = "Weird"
        self.assertTrue(lc.check(d))

    def test_name_must_start_with_letter(self):
        d = load()
        d["phases"][2]["name"] = "Indirecto"
        self.assertTrue(any("does not start" in e for e in lc.check(d)))

    def test_node_id_change_fails(self):
        d = load()
        d["phases"][0]["mermaid_node_id"] = "B"
        self.assertTrue(any("mermaid_node_id" in e for e in lc.check(d)))

    def test_unpaired_question_fails(self):
        d = load()
        d["phases"][0]["question"] = "Qué puede causarlo?"
        self.assertTrue(any("¿?" in e for e in lc.check(d)))

    def test_expansion_must_list_names(self):
        d = load()
        d["acronym"]["expansion"] = "Bicho raro, Interpreta, Hallazgos"
        self.assertTrue(lc.check(d))

    def test_unknown_macro_fails(self):
        d = copy.deepcopy(load())
        d["acronym"]["recursive_note"] = "La {{phase.9.letter}} es recursiva."
        self.assertTrue(any("unknown macro" in e for e in lc.check(d)))

    def test_weeks_must_stay(self):
        d = load()
        d["phases"][1]["weeks"] = "3 a 5"
        self.assertTrue(any("weeks" in e for e in lc.check(d)))


if __name__ == "__main__":
    unittest.main()
