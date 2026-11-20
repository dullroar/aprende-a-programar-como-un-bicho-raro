#!/usr/bin/env python3
"""Tests for tools/glossary_check.py. Run: python3 -I tools/test_glossary_check.py"""
import copy
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import glossary_check as gc  # noqa: E402


def good():
    return copy.deepcopy(gc.load(gc.DEFAULT_PATH))


class RealGlossaryTests(unittest.TestCase):
    def test_real_glossary_is_clean(self):
        self.assertEqual(gc.check(good()), [])

    def test_has_about_150_terms_or_more(self):
        self.assertGreaterEqual(len(good()["terms"]), 150)

    def test_assurance_labels_exact(self):
        labels = {l["enum"]: l["es"] for l in good()["frozen"]["assurance_labels"]["labels"]}
        self.assertEqual(labels, gc.REQUIRED_LABELS)

    def test_forty_rule_wording(self):
        rule = good()["frozen"]["timecard_rule"]
        self.assertEqual(rule["stop_phrase"], "pasa de 40")
        self.assertEqual(rule["exact_forty_phrase"], "un total de exactamente 40 continúa")
        text = " ".join(rule["es"].split())
        self.assertIn("pasa de 40", text)
        self.assertIn("Un total de exactamente 40 continúa", text)

    def test_phases_are_macros_not_letters(self):
        for p in good()["phases"]:
            self.assertTrue(p["macro_letter"].startswith("{{phase."))

    def test_core_term_decisions(self):
        by_id = {t["id"]: t for t in good()["terms"]}
        self.assertEqual(by_id["loop"]["es"], "bucle")
        self.assertEqual(by_id["rollback"]["es"], "reversión")
        self.assertEqual(by_id["backtracking"]["es"], "retroceso")
        self.assertEqual(by_id["array"]["es"], "arreglo")


class NegativeTests(unittest.TestCase):
    def test_missing_assurance_label_is_caught(self):
        d = good()
        d["frozen"]["assurance_labels"]["labels"].pop()
        self.assertTrue(any("accidentally-exploited" in p for p in gc.check(d)))

    def test_changed_assurance_label_is_caught(self):
        d = good()
        d["frozen"]["assurance_labels"]["labels"][2]["es"] = "explotado accidentalmente"
        self.assertTrue(any("aprovechado por accidente" in p for p in gc.check(d)))

    def test_changed_stop_phrase_is_caught(self):
        d = good()
        d["frozen"]["timecard_rule"]["stop_phrase"] = "llega a 40"
        self.assertTrue(any("stop_phrase" in p for p in gc.check(d)))

    def test_banned_phrase_in_rule_text_is_caught(self):
        d = good()
        d["frozen"]["timecard_rule"]["es"] += " Detente cuando el total llega a 40."
        self.assertTrue(any("banned phrase" in p for p in gc.check(d)))

    def test_category_without_code_font_is_caught(self):
        d = good()
        d["frozen"]["timecard_rule"]["es"] = d["frozen"]["timecard_rule"]["es"].replace("`Coding`", "Coding")
        self.assertTrue(any("`Coding`" in p for p in gc.check(d)))

    def test_literal_phase_letter_is_caught(self):
        d = good()
        d["phases"][0]["macro_letter"] = "B"
        self.assertTrue(any("macro" in p for p in gc.check(d)))

    def test_duplicate_id_is_caught(self):
        d = good()
        d["terms"].append(copy.deepcopy(d["terms"][0]))
        self.assertTrue(any("duplicate id" in p for p in gc.check(d)))

    def test_approved_term_banned_is_caught(self):
        d = good()
        d["terms"][0]["banned"] = [d["terms"][0]["es"]]
        self.assertTrue(any("also banned" in p for p in gc.check(d)))

    def test_banned_equals_other_concept_is_caught(self):
        d = good()
        by_id = {t["id"]: t for t in d["terms"]}
        by_id["rollback"]["banned"] = ["retroceso"]
        self.assertTrue(any("approved term of" in p for p in gc.check(d)))

    def test_missing_es_is_caught(self):
        d = good()
        del d["terms"][3]["es"]
        self.assertTrue(any("missing or empty 'es'" in p for p in gc.check(d)))

    def test_non_mapping_is_caught(self):
        self.assertEqual(gc.check(["x"]), ["glossary is not a mapping"])


def names(**files):
    return {"dirs": {"lessons/cs": "informatica"}, "files": {"A.md": "x.md", **{k: v for k, v in files.items()}}}


class PathWordTests(unittest.TestCase):
    def test_real_path_names_are_clean(self):
        self.assertEqual(gc.check_path_words(good(), gc.load(gc.PATH_NAMES)), [])

    def test_accents_and_plurals_fold(self):
        d = good()
        n = {"dirs": {}, "files": {"a": "01-guias-de-estudio.md", "b": "indice.md", "c": "maquinas-raras.md"}}
        self.assertEqual(gc.check_path_words(d, n), [])

    def test_word_without_entry_is_caught(self):
        n = {"dirs": {}, "files": {"a": "zapatos.md"}}
        problems = gc.check_path_words(good(), n)
        self.assertEqual(len(problems), 1)
        self.assertIn("zapatos", problems[0])

    def test_banned_word_in_a_path_is_caught(self):
        # "desafio" is banned for the glossary term "reto"; the name DESAFIO.md was exactly this mistake.
        n = {"dirs": {}, "files": {"CHALLENGE.md": "DESAFIO.md"}}
        problems = gc.check_path_words(good(), n)
        self.assertTrue(any("banned" in p and "desafio" in p for p in problems), problems)

    def test_banned_commitment_and_callback_are_caught(self):
        n = {"dirs": {}, "files": {"a": "efectos-errores-y-compromiso.md", "b": "eventos-callbacks.md"}}
        problems = gc.check_path_words(good(), n)
        self.assertTrue(any("compromiso" in p for p in problems), problems)
        self.assertTrue(any("callbacks" in p for p in problems), problems)

    def test_removing_a_path_word_entry_is_caught(self):
        d = good()
        d["path_words"] = [p for p in d["path_words"] if p["es"] != "informática"]
        problems = gc.check_path_words(d, {"dirs": {"lessons/cs": "informatica"}, "files": {}})
        self.assertTrue(any("informatica" in p for p in problems), problems)

    def test_proper_names_and_function_words_pass_but_only_when_listed(self):
        d = good()
        n = {"dirs": {}, "files": {"a": "make-y-cmake.md"}}
        self.assertEqual(gc.check_path_words(d, n), [])
        d["path_proper_names"].remove("cmake")
        self.assertTrue(any("cmake" in p for p in gc.check_path_words(d, n)))

    def test_missing_section_is_caught(self):
        d = good()
        del d["path_words"]
        self.assertEqual(gc.check_path_words(d, {"dirs": {}, "files": {}}), ["path_words: missing"])

    def test_path_words_do_not_reach_the_term_list(self):
        self.assertFalse({p["es"] for p in good()["path_words"]} & {t["es"] for t in good()["terms"]})


if __name__ == "__main__":
    unittest.main()
