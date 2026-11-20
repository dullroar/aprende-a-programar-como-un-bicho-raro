#!/usr/bin/env python3
"""Tests for tools/breakage_pilot.py. Run: python3 -I tools/test_breakage_pilot.py

The catalog breaks the real pilot files; these tests prove that the catalog itself can fail: a disarmed gate, a wrong
check id, a stale copy and a dirty control must each be reported, and the plan's step 7 (a to d, then the surviving
phase letter) must all be present."""
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lessons", "book", "locale"))
import breakage_pilot as bp  # noqa: E402
import verify  # noqa: E402

CATALOG = bp.catalog()
PILOT = bp.Pilot()


def copy(run_kind="hand", expect="I13", rel=bp.README, edit=None, cid="x"):
    return bp.Copy(cid, "a", "a test copy", run_kind, rel, expect, edit or (lambda t: t))


class Catalog(unittest.TestCase):
    def test_every_step_of_appendix_a_7_is_present(self):
        self.assertEqual(sorted({c.step for c in CATALOG}), ["a", "b", "c", "d", "e"])

    def test_ids_are_unique_and_every_copy_names_its_check(self):
        ids = [c.id for c in CATALOG]
        self.assertEqual(len(ids), len(set(ids)))
        for c in CATALOG:
            self.assertTrue(c.expect and c.title and c.kind in ("po", "hand", "lock", "anchors"), c)
            self.assertIn(c.rel, bp.PILOT + ("src/forth/timecards.fs", "src/forth/check.sh"))

    def test_the_surviving_phase_letter_is_tested_in_prose_labels_and_acronym(self):
        ids = {c.id for c in CATALOG}
        for wanted in ("phase-bare-letter-prose", "phase-bare-letter-recursive", "phase-label-letter", "phase-start-label",
                       "phase-acronym-english"):
            self.assertIn(wanted, ids)

    def test_every_pilot_file_loses_an_accdescr(self):
        broken = {c.rel for c in CATALOG if c.id.startswith("accdescr-deleted")}
        self.assertEqual(broken, set(bp.PILOT))


class RealCopies(unittest.TestCase):
    def test_the_control_is_clean(self):
        self.assertEqual(bp.control_problems(PILOT), [])

    def test_every_copy_fails_with_the_expected_check(self):
        for c in CATALOG:
            with self.subTest(copy=c.id):
                problems, err = bp.run_one(PILOT, c)
                self.assertIsNone(err)
                self.assertTrue(problems, "the gate did not fail")
                self.assertTrue(any(c.expect in p for p in problems), (c.expect, problems[:3]))

    def test_run_all_is_clean(self):
        self.assertEqual(bp.run_all(), [])

    def test_a_copy_does_not_touch_the_repository_files(self):
        rel = bp.FORTH
        path = os.path.join(bp.ROOT, rel)
        with open(path, "rb") as f:
            before = f.read()
        bp.run_one(PILOT, next(c for c in CATALOG if c.id == "anchor-heading-renamed"))
        with open(path, "rb") as f:
            self.assertEqual(f.read(), before)


class TheCatalogCanFail(unittest.TestCase):
    def run_all_with(self, *copies, control=()):
        with mock.patch.object(bp, "catalog", return_value=list(copies)), \
                mock.patch.object(bp, "control_problems", return_value=list(control)):
            return bp.run_all()

    def test_a_good_copy_passes(self):
        c = copy(edit=bp.text_edit("# Forth", "# Forth!"), expect="I")
        self.assertEqual(self.run_all_with(c), [])

    def test_a_gate_that_does_not_fail_is_reported_as_disarmed(self):
        out = self.run_all_with(copy(edit=lambda t: t))     # no change at all: the file is still good
        self.assertEqual(len(out), 1)
        self.assertIn("disarmed", out[0])

    def test_a_failure_with_the_wrong_check_is_reported(self):
        out = self.run_all_with(copy(edit=bp.text_edit("# Forth", "# Forth!"), expect="I99"))
        self.assertEqual(len(out), 1)
        self.assertIn("not with I99", out[0])

    def test_a_stale_copy_is_reported_not_passed(self):
        out = self.run_all_with(copy(edit=bp.text_edit("text that is not in the file", "x")))
        self.assertEqual(len(out), 1)
        self.assertIn("is broken", out[0])
        self.assertIn("stale", out[0])

    def test_a_dirty_control_is_reported(self):
        out = self.run_all_with(copy(edit=bp.text_edit("# Forth", "# Forth!"), expect="I"), control=["I7 the good file fails"])
        self.assertEqual(out, ["control: I7 the good file fails"])

    def test_a_disarmed_per_file_gate_fails_most_of_the_catalog(self):
        with mock.patch.object(verify, "check_file", return_value=[]):
            problems = [bp.run_one(PILOT, c)[0] for c in CATALOG if c.kind in ("po", "hand", "anchors")]
        self.assertEqual([p for p in problems if p and not any(x.startswith("anchors") for x in p)], [])

    def test_a_disarmed_lock_gate_is_reported(self):
        with mock.patch.object(verify, "check_lock", return_value=[]):
            out = bp.run_all()
        self.assertTrue(any("frozen-byte" in p and "disarmed" in p for p in out), out)

    def test_msgstr_edit_refuses_a_missing_text(self):
        class E:
            msgstr = "uno"
        with self.assertRaises(AssertionError):
            bp.msgstr_edit("dos", "tres")([E()])
        with self.assertRaises(AssertionError):
            bp.drop_first_line("accDescr:")("no such line")


class ReleaseWiring(unittest.TestCase):
    def test_verify_release_runs_the_pilot_copies(self):
        with mock.patch.object(bp, "run_all", return_value=["copy x did not fail"]), \
                mock.patch("negative.run_all", return_value=[]):
            self.assertEqual(verify.negative_problems(), ["copy x did not fail"])


if __name__ == "__main__":
    unittest.main()
