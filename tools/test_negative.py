#!/usr/bin/env python3
"""Tests for tools/negative.py. Run: python3 -I tools/test_negative.py

The catalog proves that the gates can fail; these tests prove that the catalog itself can fail: a disarmed gate, a wrong
check id, a stale fixture and a dirty control must each be reported. Nothing here starts the English repo gates."""
import contextlib
import io
import os
import sys
import unittest
from unittest import mock

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lessons", "book", "locale"))
import negative  # noqa: E402
import verify  # noqa: E402

CATALOG = negative.catalog()


def fixture(run, expect="I13", ident="x", item=1):
    return negative.Fixture(ident, item, "a test fixture", "file", expect, run)


class Catalog(unittest.TestCase):
    def test_every_item_of_plan_10_2_has_a_fixture(self):
        self.assertEqual(sorted({f.item for f in CATALOG}), list(range(1, 14)))   # 12 = plan 5.6 (I17 to I20), 13 = editorial review Part E (I21 to I26)

    def test_ids_are_unique_and_every_fixture_names_its_check(self):
        ids = [f.id for f in CATALOG]
        self.assertEqual(len(ids), len(set(ids)))
        for f in CATALOG:
            self.assertTrue(f.expect and f.title and f.kind in ("file", "lock", "tool", "path"), f)

    def test_the_named_cases_of_the_plan_are_present(self):
        ids = {f.id for f in CATALOG}
        for wanted in ("40-code-span-ge", "40-exact-sentence-dropped", "frozen-byte-flipped", "enum-translated", "entry-id-changed",
                       "accdescr-removed", "accdescr-english", "branch-edge-swapped", "diagram-copy-drifted",
                       "guide-evidence-question-missing", "guide-assurance-label-wrong", "guide-section-missing",
                       "curriculum-week-missing", "curriculum-exercise-id-wrong", "curriculum-week-under-wrong-phase",
                       "curriculum-phase-letter-duplicated", "curriculum-es-english-letter-survives",
                       "paragraph-deleted-after-po", "fragment-not-remapped", "link-to-english-repo",
                       "pdf-apl-glyph-missing", "pdf-caption-beyond-page-edge", "pdf-code-beyond-margin", "card-category-translated"):
            self.assertIn(wanted, ids)


class RealFixtures(unittest.TestCase):
    def test_the_control_is_clean(self):
        self.assertEqual(negative.control_problems(), [])

    def test_every_fixture_fails_with_the_expected_check(self):
        for f in CATALOG:
            with self.subTest(fixture=f.id):
                problems, err = negative.run_fixture(f)
                self.assertIsNone(err)
                self.assertTrue(problems, "the gate did not fail")
                self.assertTrue(any(f.expect in p for p in problems), (f.expect, problems[:3]))

    def test_run_all_is_clean(self):
        self.assertEqual(negative.run_all(), [])

    def test_the_lock_fixture_leaves_nothing_behind(self):
        negative.lock_problems(negative.flip_byte)
        self.assertFalse(os.path.exists(os.path.join(negative.WORK, "lock")))

    def test_a_fixture_changes_only_its_own_copy(self):
        path = os.path.join(negative.ROOT, "src", "forth", "timecards.fs")
        with open(path, "rb") as f:
            before = f.read()
        negative.lock_problems(negative.flip_byte)
        with open(path, "rb") as f:
            self.assertEqual(f.read(), before)


class TheCatalogCanFail(unittest.TestCase):
    def run_all_with(self, *fixtures, control=()):
        with mock.patch.object(negative, "catalog", return_value=list(fixtures)), \
                mock.patch.object(negative, "control_problems", return_value=list(control)):
            return negative.run_all()

    def test_a_good_fixture_passes(self):
        self.assertEqual(self.run_all_with(fixture(lambda: ["I13 changed"])), [])

    def test_a_gate_that_does_not_fail_is_reported_as_disarmed(self):
        out = self.run_all_with(fixture(lambda: []))
        self.assertEqual(len(out), 1)
        self.assertIn("disarmed", out[0])
        self.assertIn("plan 10.2 item 1", out[0])

    def test_a_failure_with_the_wrong_check_is_reported(self):
        out = self.run_all_with(fixture(lambda: ["I7 something else"], expect="I13"))
        self.assertEqual(len(out), 1)
        self.assertIn("not with I13", out[0])

    def test_a_stale_fixture_is_reported_not_passed(self):
        out = self.run_all_with(fixture(lambda: negative.swap("not in the text", "x")("the control text")))
        self.assertEqual(len(out), 1)
        self.assertIn("is broken", out[0])
        self.assertIn("stale", out[0])

    def test_a_dirty_control_is_reported(self):
        out = self.run_all_with(fixture(lambda: ["I13 x"]), control=["I7 the good input fails"])
        self.assertEqual(out, ["control: I7 the good input fails"])

    def test_a_disarmed_per_file_gate_fails_most_of_the_catalog(self):
        # verify.check_file is the per-file check of --release. If it stopped finding anything, every file fixture would say so.
        with mock.patch.object(verify, "check_file", return_value=[]):
            out = negative.run_all()
        files = [f for f in CATALOG if f.kind == "file"]
        self.assertGreaterEqual(len([p for p in out if "disarmed" in p]), len(files) - 6)

    def test_a_disarmed_lock_gate_is_reported(self):
        with mock.patch.object(verify, "check_lock", return_value=[]):
            out = negative.run_all()
        self.assertTrue(any("frozen-byte-flipped" in p and "disarmed" in p for p in out), out)

    def test_a_disarmed_foreign_link_gate_is_reported(self):
        import repo_links
        with mock.patch.object(repo_links, "foreign_repo_links", return_value=[]):
            out = negative.run_all()
        self.assertTrue(any("link-to-english-repo" in p and "disarmed" in p for p in out), out)

    def test_swap_refuses_a_missing_old_text(self):
        with self.assertRaises(AssertionError):
            negative.swap("absent", "x")("present")
        with self.assertRaises(AssertionError):
            negative.subst(r"absent", "x")("present")


class ReleaseWiring(unittest.TestCase):
    def test_verify_release_runs_the_catalog(self):
        # the wiring only: the pilot breakage control runs on the real pilot files, which carry findings until P3C-004 to 015
        import breakage_pilot
        import resume_test
        with mock.patch.object(negative, "run_all", return_value=["fixture x did not fail"]), \
                mock.patch.object(breakage_pilot, "run_all", return_value=[]), mock.patch.object(resume_test, "run_all", return_value=[]):
            self.assertEqual(verify.negative_problems(), ["fixture x did not fail"])

    def test_verify_release_source_calls_it(self):
        with open(os.path.join(HERE, "verify.py"), encoding="utf-8") as f:
            self.assertIn('timed("negative fixtures (plan 10.2)", negative_problems)', f.read())


class Cli(unittest.TestCase):
    def call(self, *args):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            status = negative.main(["negative.py", *args])
        return status, out.getvalue()

    def test_default_run_is_ok(self):
        status, text = self.call()
        self.assertEqual(status, 0)
        self.assertIn("all fail as expected", text)

    def test_list_names_every_fixture(self):
        status, text = self.call("--list")
        self.assertEqual(status, 0)
        self.assertEqual(len(text.strip().splitlines()), len(CATALOG))

    def test_show_prints_the_problems_of_one_fixture(self):
        status, text = self.call("--show", "frozen-byte-flipped")
        self.assertEqual(status, 0)
        self.assertIn("I13", text)

    def test_unknown_fixture_and_unknown_option_are_usage_errors(self):
        self.assertEqual(self.call("--show", "no-such-fixture")[0], 2)
        self.assertEqual(self.call("--bogus")[0], 2)

    def test_a_disarmed_gate_makes_the_command_exit_1(self):
        with mock.patch.object(negative, "catalog", return_value=[fixture(lambda: [])]), \
                mock.patch.object(negative, "control_problems", return_value=[]):
            status, text = self.call()
        self.assertEqual(status, 1)
        self.assertIn("disarmed", text)


if __name__ == "__main__":
    unittest.main()
