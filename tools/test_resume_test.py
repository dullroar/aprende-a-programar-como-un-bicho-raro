#!/usr/bin/env python3
"""Tests for tools/resume_test.py. Run: python3 -I tools/test_resume_test.py

Each test runs the real loop/ralph.sh in a scratch repo (a few seconds); no model is called."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import resume_test as rt  # noqa: E402


class ResumeScenario(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.dest, cls.out1, cls.out2, cls.problems = rt.scenario("t-main")

    def test_scenario_is_clean(self):
        self.assertEqual(self.problems, [])

    def test_two_different_agent_invocations(self):
        self.assertEqual([c[1] for c in rt.calls(self.dest)], ["A", "B", "B", "B"])
        self.assertEqual([c[2] for c in rt.calls(self.dest)][:2], ["partial-stop", "resume"])

    def test_iteration_numbers_continue_from_ledger(self):
        self.assertIn("start at iteration 2", self.out2)

    def test_log_shows_the_resume(self):
        text = rt.read(os.path.join(self.dest, "loop", "log.md"))
        self.assertIn("2 T-1 done resumed from HANDOFF.md and the queue at segment 3", text)

    def test_negative_tampered_log_is_caught(self):
        rt.write(os.path.join(self.dest, "loop", "log.md"), "1 T-1 partial x\n2 T-1 done all segments\n")
        p = rt.check_resume(self.dest, self.out1, self.out2)
        self.assertTrue(any("does not show the resume" in x for x in p), p)

    def test_negative_duplicated_segments_are_caught(self):
        rt.write(os.path.join(self.dest, "work", "T-1.part"), "T-1 segment 1\nT-1 segment 2\nT-1 segment 1\n")
        p = rt.check_resume(self.dest, self.out1, self.out2)
        self.assertTrue(any("not resumed" in x for x in p), p)

    def test_negative_leftover_handoff_and_stop_are_caught(self):
        rt.write(os.path.join(self.dest, "loop", "HANDOFF.md"), "x")
        rt.write(os.path.join(self.dest, "loop", "STOP"), "x")
        try:
            p = rt.check_resume(self.dest, self.out1, self.out2)
        finally:
            os.remove(os.path.join(self.dest, "loop", "HANDOFF.md"))
            os.remove(os.path.join(self.dest, "loop", "STOP"))
        self.assertTrue(any("HANDOFF.md was not consumed" in x for x in p), p)
        self.assertTrue(any("STOP is still there" in x for x in p), p)

    def test_negative_wrong_driver_output_is_caught(self):
        p = rt.check_resume(self.dest, self.out1, "ralph: finished.")
        self.assertTrue(any("DONE sentinel" in x for x in p), p)


class ResumeNegatives(unittest.TestCase):
    def test_agent_that_restarts_is_caught(self):
        _, _, _, p = rt.scenario("t-restart", mode_b="restart")
        self.assertTrue(any("not resumed" in x for x in p), p)

    def test_stopped_state_check_fails_on_a_wrong_state(self):
        dest = rt.build_scratch("t-stopped")
        p = rt.check_stopped(dest, "ralph: finished.")  # nothing ran
        self.assertTrue(any("STOP sentinel" in x for x in p), p)
        self.assertTrue(any("HANDOFF.md is missing" in x for x in p), p)

    def test_stop_at_start_runs_no_agent(self):
        self.assertEqual(rt.negative_stop_first(), [])

    def test_stalled_agent_trips_the_breaker(self):
        self.assertEqual(rt.negative_stall(), [])

    def test_held_lock_refuses_a_second_loop(self):
        self.assertEqual(rt.negative_lock(), [])

    def test_resume_note_is_the_only_thing_that_moves_the_start(self):
        # the agent in resume mode with no note starts at segment 1 (T-2 case), so the note is what resumes
        dest, _, _, p = rt.scenario("t-note")
        self.assertEqual(p, [])
        self.assertEqual(rt.part_lines(dest, "T-2"), ["T-2 segment %d" % n for n in range(1, 5)])


if __name__ == "__main__":
    unittest.main()
