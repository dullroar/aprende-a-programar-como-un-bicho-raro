#!/usr/bin/env python3
"""Tests for tools/baseline.py. Run: python3 -I tools/test_baseline.py"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import baseline  # noqa: E402


class BaselineTests(unittest.TestCase):
    def test_run_gate_records_exit_zero(self):
        code, out, _ = baseline.run_gate("ok", [sys.executable, "-c", "print('hi')"], 30)
        self.assertEqual(code, 0)
        self.assertIn("hi", out)

    def test_run_gate_records_failure_not_hidden(self):
        code, out, _ = baseline.run_gate("bad", [sys.executable, "-c", "import sys; print('boom'); sys.exit(3)"], 30)
        self.assertEqual(code, 3)
        self.assertIn("boom", out)

    def test_run_gate_records_timeout(self):
        code, _, _ = baseline.run_gate("slow", [sys.executable, "-c", "import time; time.sleep(5)"], 1)
        self.assertEqual(code, "timeout")

    def test_render_lists_every_command_and_counts_failures(self):
        results = [
            ("a", ["cmd", "one"], 0, "fine", 1.0),
            ("b", ["cmd", "two"], 2, "broken", 2.0),
        ]
        text = baseline.render(results)
        self.assertIn("`cmd one`", text)
        self.assertIn("`cmd two`", text)
        self.assertIn("1 of 2 gates exit 0; 1 did not.", text)
        self.assertIn("b (exit 2)", text)

    def test_render_all_green_has_no_failing_line(self):
        text = baseline.render([("a", ["x"], 0, "ok", 0.1)])
        self.assertNotIn("Failing gates", text)

    def test_gate_list_covers_ci_workflow_commands(self):
        cmds = [" ".join(c) for _, c, _ in baseline.GATES]
        for needle in ("lessons/book/build.py --check", "--check-diagrams", "test_pdf_lint.py",
                       "lessons/curriculum/build.py --release", "test_repo_identity.py"):
            self.assertTrue(any(needle in c for c in cmds), needle)


if __name__ == "__main__":
    unittest.main()
