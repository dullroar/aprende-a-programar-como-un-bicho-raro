#!/usr/bin/env python3
"""Tests for tools/model_report.py. Run: python3 -I tools/test_model_report.py"""
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import model_report as mr  # noqa: E402


class ReportTests(unittest.TestCase):
    def ledger(self, rows):
        fd, path = tempfile.mkstemp(suffix=".jsonl")
        with os.fdopen(fd, "w") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        self.addCleanup(os.unlink, path)
        return path

    def test_groups_by_agent_tier_model_and_old_rows_have_no_evidence(self):
        p = self.ledger([
            {"iteration": 1, "seconds": 10, "cost_usd": 1.0},
            {"iteration": 2, "agent": "claude", "tier": "standard", "model_reported": "claude-sonnet-5-5", "seconds": 20, "cost_usd": 2.0},
            {"iteration": 3, "agent": "claude", "tier": "standard", "model_reported": "claude-sonnet-5-5", "seconds": 40, "cost_usd": 1.0},
        ])
        g = mr.summarize(mr.load(p))
        self.assertEqual(g[("claude(untagged)", "-", "(no evidence)")]["n"], 1)
        self.assertEqual(g[("claude", "standard", "claude-sonnet-5-5")]["n"], 2)
        self.assertAlmostEqual(g[("claude", "standard", "claude-sonnet-5-5")]["usd"], 3.0)

    def test_mismatch_gives_exit_code_1(self):
        p = self.ledger([{"iteration": 5, "agent": "codex", "tier": "light", "model_requested": "gpt-6-luna",
                          "model_reported": "gpt-6.2-sol", "model_mismatch": True, "seconds": 5}])
        self.assertEqual(mr.main(["--ledger", p]), 1)

    def test_no_mismatch_exit_0_and_missing_ledger_ok(self):
        p = self.ledger([{"iteration": 5, "agent": "codex", "model_reported": "gpt-6-luna", "model_mismatch": False, "seconds": 5}])
        self.assertEqual(mr.main(["--ledger", p]), 0)
        self.assertEqual(mr.main(["--ledger", p + ".missing"]), 0)

    def test_efficiency_counts_only_finished_tasks_for_unit_cost(self):
        rows = [
            {"iteration": 1, "agent": "claude", "tier": "standard", "model_reported": "m", "kind": "translate", "tok_out": 1000,
             "cost_usd": 2.0, "unit_words": 2000, "unit_segments": 100, "loop_result": "done"},
            {"iteration": 2, "agent": "claude", "tier": "standard", "model_reported": "m", "kind": "translate", "tok_out": 500,
             "cost_usd": 1.0, "unit_words": 2000, "loop_result": "partial"},
        ]
        g = mr.efficiency(rows)[("claude", "standard", "m", "-", "translate")]
        self.assertEqual((g["n"], g["done"], g["d_words"], g["d_segs"]), (2, 1, 2000, 100))
        self.assertAlmostEqual(g["usd"], 3.0)      # all spend counts as spend ...
        self.assertAlmostEqual(g["d_usd"], 2.0)    # ... but unit metrics use finished tasks only

    def test_copilot_credit_estimate_is_the_usd_when_no_reported_cost(self):
        self.assertAlmostEqual(mr.usd({"cost_est_usd": 0.63}), 0.63)
        self.assertAlmostEqual(mr.usd({"cost_usd": 1.5, "cost_est_usd": 0.63}), 1.5)
        self.assertEqual(mr.usd({}), 0.0)

    def test_old_rows_are_skipped_by_efficiency(self):
        self.assertEqual(len(mr.efficiency([{"iteration": 1, "seconds": 5}])), 0)

    def test_since_filters(self):
        p = self.ledger([{"iteration": 1, "seconds": 1}, {"iteration": 9, "seconds": 1}])
        self.assertEqual(len(mr.load(p, since=5)), 1)


if __name__ == "__main__":
    unittest.main()
