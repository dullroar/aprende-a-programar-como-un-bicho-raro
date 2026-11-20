#!/usr/bin/env python3
"""Tests for tools/recall_test.py (task P3-007). Run: python3 -I tools/test_recall_test.py

Covers: the changed-span helper, fault selection (deterministic, never mutates units, one fault per unit, the
40-flip first), the two pilot mutators, reply parsing, the exact-substring filter, location scoring (a finding
elsewhere earns nothing), the verdict (bar, every 40-flip), resume and budget of ask_all, and the negative cases:
a reviewer that finds nothing fails, a reviewer that invents excerpts fails, a reviewer that flags the wrong
place fails.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
import catalog  # noqa: E402
import jury_packet as jp  # noqa: E402
import recall_test as rt  # noqa: E402

CAT = catalog.load("es")
CTX = jp.canary_context(CAT)
ENUMS = rt.finding_enums()


def unit(n, en, es, kind="paragraph"):
    return {"file": "README.md", "id": "s-%012x-%04d" % (n * 7919, n), "line": n, "kind": kind,
            "english": en, "spanish": es}


FORTY = unit(1, "The chain stops when the total is strictly greater than 40.",
             "La cadena se detiene cuando el total es más de 40. Un total de 40 continúa.")
NEG = unit(2, "The loop does not stop early.", "El bucle no se detiene antes de tiempo.")
NUM = unit(3, "Pick 3 cards and 12 hours.", "Elige 3 tarjetas y 12 horas.")
CAT_U = unit(4, "The run printed `Meetings 15 15`.", "La ejecución imprimió `Meetings 15 15`.")
PH = unit(5, "The phase pointer starts at W.", "Empieza con el puntero de fase en B.")
UNITS = [FORTY, NEG, NUM, CAT_U, PH]


def fake_finding(fault, **kw):
    s = fault["mutated_spanish"]
    a, b = fault["span"]
    f = {"id": "F001", "segment_id": "s-000000000000-0001", "severity": "critical", "category": "number-operator",
         "english_excerpt": None, "spanish_excerpt": s[max(0, a - 3):max(b, a) + 3], "problem": "p", "evidence": "e",
         "proposed_fix": "f", "reviewer_model": "m", "confidence": "high", "type": "defect", "status": "open"}
    f.update(kw)
    return f


class Span(unittest.TestCase):
    def test_replacement(self):
        a, b = rt.changed_span("el total es más de 40.", "el total es al menos 40.")
        self.assertEqual("el total es al menos 40."[a:b], "al menos")

    def test_pure_deletion_is_empty_span(self):
        a, b = rt.changed_span("el bucle no se detiene", "el bucle se detiene")
        self.assertEqual(a, b)

    def test_identical(self):
        a, b = rt.changed_span("igual", "igual")
        self.assertEqual(a, b)


class Mutators(unittest.TestCase):
    def test_category_in_span(self):
        r = rt.m_category_in_span(CAT_U, CTX)
        self.assertIn("`Reuniones 15 15`", r[0])
        self.assertEqual(r[2:], ("dnt-violation", "major"))

    def test_category_declines_outside_code(self):
        self.assertIsNone(rt.m_category_in_span(unit(9, "Meetings.", "Meetings son largas."), CTX))

    def test_phase_letter_after_fase(self):
        r = rt.m_phase_letter_after_fase(PH, CTX)
        letters = CTX["phase_letters"]
        self.assertIn("fase en " + letters[(letters.index("B") + 1) % len(letters)], r[0])
        self.assertEqual(r[3], "critical")

    def test_phase_letter_declines_inside_code(self):
        self.assertIsNone(rt.m_phase_letter_after_fase(unit(9, "x", "Escribe `fase B` aquí."), CTX))


class Select(unittest.TestCase):
    def test_deterministic_and_pure(self):
        before = json.dumps(UNITS)
        a = rt.select_faults(UNITS, CTX, 10, 3)
        b = rt.select_faults(UNITS, CTX, 10, 3)
        self.assertEqual(a, b)
        self.assertEqual(before, json.dumps(UNITS))

    def test_one_fault_per_unit_and_mutated(self):
        faults = rt.select_faults(UNITS, CTX, 50, 3)
        self.assertEqual(len({f["unit"] for f in faults}), len(faults))
        for f in faults:
            self.assertNotEqual(f["original_spanish"], f["mutated_spanish"])
            a, b = f["span"]
            self.assertLessEqual(a, b)

    def test_forty_flip_is_seeded_first(self):
        faults = rt.select_faults(UNITS, CTX, 50, 3)
        self.assertEqual(faults[0]["mutator"], "flip_forty")
        self.assertIn("al menos 40", faults[0]["mutated_spanish"])

    def test_controls_are_clean_and_disjoint(self):
        faults = rt.select_faults(UNITS, CTX, 2, 3)
        ctl = rt.select_controls(UNITS, faults, 10, 3)
        self.assertFalse({jp.unit_key(u) for u in ctl} & {f["unit"] for f in faults})


class Parse(unittest.TestCase):
    def test_empty_forms(self):
        self.assertEqual(rt.parse_findings("[]"), ([], []))
        self.assertEqual(rt.parse_findings(""), ([], []))

    def test_jsonl_and_fence(self):
        txt = '```json\n{"a": 1}\n{"b": 2}\n```'
        out, errs = rt.parse_findings(txt)
        self.assertEqual(len(out), 2)
        self.assertEqual(errs, [])

    def test_garbage_line_is_an_error(self):
        out, errs = rt.parse_findings('{"a": 1}\nnot json')
        self.assertEqual(len(out), 1)
        self.assertEqual(len(errs), 1)


class Scoring(unittest.TestCase):
    def setUp(self):
        self.fault = rt.select_faults([FORTY], CTX, 1, 1)[0]

    def test_exact_finding_at_the_change_is_caught(self):
        f = fake_finding(self.fault)
        s = rt.score_fault(self.fault, [f], FORTY["english"], ENUMS)
        self.assertTrue(s["caught"])
        self.assertTrue(s["caught_at_major"])

    def test_finding_elsewhere_earns_nothing(self):
        f = fake_finding(self.fault, spanish_excerpt="La cadena se detiene")
        s = rt.score_fault(self.fault, [f], FORTY["english"], ENUMS)
        self.assertFalse(s["caught"])
        self.assertEqual(s["elsewhere"], 1)

    def test_invented_excerpt_is_rejected_not_credited(self):
        f = fake_finding(self.fault, spanish_excerpt="al menos 41 horas")
        s = rt.score_fault(self.fault, [f], FORTY["english"], ENUMS)
        self.assertFalse(s["caught"])
        self.assertEqual(s["rejected"], 1)

    def test_english_excerpt_must_be_exact(self):
        f = fake_finding(self.fault, english_excerpt="invented English")
        self.assertFalse(rt.score_fault(self.fault, [f], FORTY["english"], ENUMS)["caught"])

    def test_bad_category_is_rejected(self):
        f = fake_finding(self.fault, category="vibes")
        self.assertFalse(rt.score_fault(self.fault, [f], FORTY["english"], ENUMS)["caught"])

    def test_minor_report_catches_but_not_at_major(self):
        f = fake_finding(self.fault, severity="minor")
        s = rt.score_fault(self.fault, [f], FORTY["english"], ENUMS)
        self.assertTrue(s["caught"])
        self.assertFalse(s["caught_at_major"])

    def test_deletion_is_caught_by_a_nearby_excerpt(self):
        fault = [f for f in rt.select_faults([NEG], CTX, 5, 1) if f["mutator"] == "negation"][0]
        self.assertEqual(fault["span"][0], fault["span"][1])
        f = fake_finding(fault, spanish_excerpt=fault["mutated_spanish"][:20])
        self.assertTrue(rt.score_fault(fault, [f], NEG["english"], ENUMS)["caught"])

    def test_omission_without_spanish_excerpt(self):
        two = unit(7, "One thing. Two things.", "Una cosa. Dos cosas.")
        fault = [f for f in rt.select_faults([two], CTX, 5, 1) if f["mutator"] == "drop_clause"][0]
        f = fake_finding(fault, spanish_excerpt=None, english_excerpt="Two things.", category="omission")
        self.assertTrue(rt.score_fault(fault, [f], two["english"], ENUMS)["caught"])
        f2 = fake_finding(fault, spanish_excerpt=None, english_excerpt="Two things.", category="grammar-agreement")
        self.assertFalse(rt.score_fault(fault, [f2], two["english"], ENUMS)["caught"])

    def test_control_counts_major_findings(self):
        f = fake_finding(self.fault, spanish_excerpt="La cadena")
        s = rt.score_control([f], FORTY["english"], FORTY["spanish"], ENUMS)
        self.assertEqual(len(s["major_plus"]), 1)


class Verdict(unittest.TestCase):
    def setUp(self):
        self.faults = rt.select_faults(UNITS, CTX, 50, 3)

    def scores(self, caught):
        return {f["fault_id"]: {"caught": caught(f), "caught_at_major": caught(f)} for f in self.faults}

    def test_perfect_reviewer_passes(self):
        v = rt.verdict(self.faults, self.scores(lambda f: True), 0.95)
        self.assertTrue(v["pass"], v)

    def test_reviewer_that_finds_nothing_fails(self):
        v = rt.verdict(self.faults, self.scores(lambda f: False), 0.95)
        self.assertFalse(v["pass"])
        self.assertEqual(v["recall_major"], 0.0)

    def test_one_missed_forty_flip_fails_even_with_high_recall(self):
        first = [f for f in self.faults if f["mutator"] == "flip_forty"][0]["fault_id"]
        v = rt.verdict(self.faults, self.scores(lambda f: f["fault_id"] != first), 0.5)
        self.assertFalse(v["pass"])
        self.assertEqual(v["flips_missed"], [first])

    def test_below_bar_fails_and_minor_misses_do_not_count(self):
        v = rt.verdict(self.faults, self.scores(lambda f: f["severity"] in rt.MAJOR_PLUS), 0.95)
        self.assertTrue(v["pass"])
        v = rt.verdict(self.faults, self.scores(lambda f: f["mutator"] == "flip_forty"), 0.95)
        self.assertFalse(v["pass"])

    def test_no_flip_seeded_fails(self):
        faults = [f for f in self.faults if f["mutator"] != "flip_forty"]
        sc = {f["fault_id"]: {"caught": True, "caught_at_major": True} for f in faults}
        self.assertFalse(rt.verdict(faults, sc, 0.95)["pass"])


class Asking(unittest.TestCase):
    class Fake:
        def __init__(self):
            self.calls = 0

        def ask(self, system, inp):
            self.calls += 1
            return {"text": "[]", "cost": 1.0, "models": ["m"]}

    def test_resume_skips_answered_inputs(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "r.jsonl")
            jobs = [("a", {"x": 1}), ("b", {"x": 2})]
            fake, replies = self.Fake(), {}
            rt.ask_all(fake, "sys", jobs, replies, path=path, workers=1, max_usd=10, log=lambda *_: None)
            self.assertEqual(fake.calls, 2)
            again = self.Fake()
            rt.ask_all(again, "sys", jobs, rt.load_replies(path), path=path, workers=1, max_usd=10, log=lambda *_: None)
            self.assertEqual(again.calls, 0)

    def test_budget_stops_new_calls(self):
        with tempfile.TemporaryDirectory() as d:
            fake = self.Fake()
            failed = rt.ask_all(fake, "sys", [("a", {"x": 1}), ("b", {"x": 2}), ("c", {"x": 3})], {},
                                path=os.path.join(d, "r.jsonl"), workers=1, max_usd=1.5, log=lambda *_: None)
            self.assertEqual(fake.calls, 2)
            self.assertEqual([j for j, _ in failed], ["c"])


class EndToEnd(unittest.TestCase):
    """A scripted reviewer over `evaluate`: perfect, silent and wrong-place reviewers."""

    def run_with(self, make_text):
        faults = rt.select_faults(UNITS, CTX, 50, 3)
        controls = []
        jobs = rt.build_jobs(faults, controls, jp.load_glossary(), CAT, {jp.unit_key(u): u for u in UNITS}, "test")
        by_id = {f["fault_id"]: f for f in faults}
        replies = {}
        for job_id, inp in jobs:
            replies[rt.key_of(inp)] = {"key": rt.key_of(inp), "job": job_id, "text": make_text(by_id[job_id], inp)}
        scores, _, missing = rt.evaluate(faults, controls, jobs, replies, ENUMS)
        return rt.verdict(faults, scores, 0.95), missing

    def test_perfect_reviewer(self):
        v, missing = self.run_with(lambda f, inp: json.dumps(fake_finding(f)))
        self.assertTrue(v["pass"], v)
        self.assertEqual(missing, [])

    def test_silent_reviewer_fails(self):
        v, _ = self.run_with(lambda f, inp: "[]")
        self.assertFalse(v["pass"])

    def test_hallucinating_reviewer_fails(self):
        v, _ = self.run_with(lambda f, inp: json.dumps(fake_finding(f, spanish_excerpt="texto que no existe")))
        self.assertFalse(v["pass"])

    def test_wrong_place_reviewer_fails(self):
        v, _ = self.run_with(lambda f, inp: json.dumps(
            fake_finding(f, spanish_excerpt=f["mutated_spanish"][-4:] if f["span"][1] < len(f["mutated_spanish"]) - 20
                         else f["mutated_spanish"][:3])))
        self.assertFalse(v["pass"])

    def test_missing_replies_are_reported(self):
        faults = rt.select_faults(UNITS, CTX, 5, 3)
        jobs = rt.build_jobs(faults, [], jp.load_glossary(), CAT, {jp.unit_key(u): u for u in UNITS}, "test")
        _, _, missing = rt.evaluate(faults, [], jobs, {}, ENUMS)
        self.assertEqual(len(missing), len(faults))


class Report(unittest.TestCase):
    def test_report_names_verdict_and_limits(self):
        faults = rt.select_faults(UNITS, CTX, 5, 3)
        sc = {f["fault_id"]: {"fault_id": f["fault_id"], "caught": False, "caught_at_major": False,
                              "reported_severity": None, "valid": 0, "rejected": 0, "elsewhere": 0} for f in faults}
        v = rt.verdict(faults, sc, 0.95)
        txt = rt.render_report({"reviewer": "r", "translator": "t", "seed": 1, "models": ["m"], "spent": 0.5},
                               faults, sc, [], [], v, 0.95)
        self.assertIn("**Verdict: FAIL.**", txt)
        self.assertIn("Limits of this test", txt)
        self.assertIn("**NO**", txt)


if __name__ == "__main__":
    unittest.main()
