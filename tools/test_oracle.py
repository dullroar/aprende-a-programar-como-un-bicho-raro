import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import oracle as o  # noqa: E402


def run(hours, stop=o.CORRECT, **kw):
    r = o._reference_run(hours, stop)
    r.__dict__.update(kw)
    return r


class OracleTests(unittest.TestCase):
    def test_selftest_clean(self):
        self.assertEqual(o.selftest(), [])

    def test_mutant_ge_rejected(self):
        bad = run(o.BOUNDARY_HOURS, o.MUTANT_GE)
        self.assertTrue(o.boundary_findings(o.reduce_record(bad)))
        self.assertEqual(o.judge(run(o.BOUNDARY_HOURS), bad, True)["verdict"], "FAIL")

    def test_late_stop_rejected(self):
        bad = run(o.BOUNDARY_HOURS, o.MUTANT_LATE)
        self.assertTrue(o.boundary_findings(o.reduce_record(bad)))

    def test_exactly_40_continues(self):
        rec = o.reduce_record(run(o.BOUNDARY_HOURS))
        self.assertEqual(rec["final_total"], 50)
        self.assertEqual(rec["crossing_card"], rec["cards"][-1])
        self.assertEqual(o.boundary_findings(rec), [])

    def test_equal_runs_pass(self):
        self.assertEqual(o.judge(run([12, 15, 14]), run([12, 15, 14]), True)["verdict"], "PASS")

    def test_differing_hours_fail_when_deterministic(self):
        v = o.judge(run([12, 15, 14]), run([12, 16, 14]), True)
        self.assertEqual(v["verdict"], "FAIL")

    def test_exit_code_difference_fails(self):
        v = o.judge(run([12, 15, 14]), run([12, 15, 14], exit_code=1), False)
        self.assertEqual(v["verdict"], "FAIL")

    def test_stderr_swap_fails(self):
        v = o.judge(run([12, 15, 14]), run([12, 15, 14], stderr="oops"), False)
        self.assertEqual(v["verdict"], "FAIL")

    def test_persisted_bytes_differ_fails(self):
        a = run([12, 15, 14], files={"db": b"x"})
        b = run([12, 15, 14], files={"db": b"y"})
        self.assertEqual(o.judge(a, b, True)["verdict"], "FAIL")

    def test_nondeterministic_runs_need_only_shape(self):
        self.assertEqual(o.judge(run([12, 15, 14]), run([11, 14, 16]), False)["verdict"], "PASS")

    def test_not_tested_reported(self):
        def deny(d, s):
            raise o.NotTested("docker denied")
        rep = o.run_family("a", "b", runner=deny)
        self.assertEqual(rep["verdict"], "NOT TESTED")
        self.assertIn("docker denied", rep["reason"])

    def test_missing_dockerfile_is_not_tested(self):
        with self.assertRaises(o.NotTested):
            o.docker_runner("/nonexistent-entry-dir")

    def test_broken_selftest_never_passes(self):
        saved = o.selftest
        o.selftest = lambda: ["forced"]
        try:
            rep = o.run_family("a", "b", runner=lambda d, s: run([12, 15, 14]))
        finally:
            o.selftest = saved
        self.assertEqual(rep["verdict"], "NOT TESTED")

    def test_run_family_pass_with_fake_runner(self):
        rep = o.run_family("a", "b", runner=lambda d, s: run([12, 15, 14]), seed=7)
        self.assertEqual(rep["verdict"], "PASS")

    def test_run_family_mutant_spanish_fails(self):
        def r(d, s):
            return run(o.BOUNDARY_HOURS, o.MUTANT_GE if d == "es" else o.CORRECT)
        self.assertEqual(o.run_family("en", "es", runner=r, seed=7)["verdict"], "FAIL")

    def test_card_category_is_never_translated(self):
        r = o.RunResult("Reuniones\t12\t12\nMeetings\t12\t12\n")
        self.assertEqual(len(o.reduce_record(r)["cards"]), 1)


if __name__ == "__main__":
    unittest.main()
