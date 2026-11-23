#!/usr/bin/env python3
"""Tests for tools/part2_negative.py. Run: python3 -I tools/test_part2_negative.py

The catalog must pass; a disarmed detector, a wrong reason, a dirty control and a broken fixture must each be reported as a failure."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import part2_negative as pn  # noqa: E402


def row(control, run, expect="X"):
    return pn.Row("t", 1, "t", "d", expect, control, run)


class Catalog(unittest.TestCase):
    def test_all_planned_fixtures_pass(self):
        results, passed, planned = pn.run_all()
        self.assertEqual(passed, planned, [(r.id, d) for r, ok, d in results if not ok])
        self.assertGreaterEqual(planned, 15)

    def test_every_appendix_row_is_covered_or_deferred(self):
        rows = {r.row for r in pn.catalog()} | {d.row for d in pn.DEFERRED}
        self.assertEqual(rows, set(range(1, 15)))


class Judge(unittest.TestCase):
    def test_good(self):
        self.assertTrue(pn.judge(row(lambda: [], lambda: ["X found"]))[0])

    def test_disarmed_detector_fails(self):
        ok, why = pn.judge(row(lambda: [], lambda: []))
        self.assertFalse(ok)
        self.assertIn("disarmed", why)

    def test_wrong_reason_fails(self):
        ok, why = pn.judge(row(lambda: [], lambda: ["Y found"]))
        self.assertFalse(ok)
        self.assertIn("stated reason", why)

    def test_prefix_of_another_id_is_not_the_reason(self):
        self.assertFalse(pn.judge(row(lambda: [], lambda: ["I16 found"], expect="I6"))[0])

    def test_dirty_control_fails(self):
        self.assertFalse(pn.judge(row(lambda: ["noise"], lambda: ["X"]))[0])

    def test_crashing_fixture_fails(self):
        def boom():
            raise ImportError("missing dependency")
        ok, why = pn.judge(row(lambda: [], boom))
        self.assertFalse(ok)
        self.assertIn("broken", why)


if __name__ == "__main__":
    unittest.main()
