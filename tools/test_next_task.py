#!/usr/bin/env python3
"""Tests for tools/next_task.py and the queue-aware tools/seedtask.py.
Run: python3 -I tools/test_next_task.py"""
import datetime
import json
import os
import shutil
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import next_task as nt  # noqa: E402
import seedtask  # noqa: E402

NOW = datetime.datetime(2026, 11, 19, 12, 0, tzinfo=datetime.timezone.utc)


def t(tid, stage=0, status="todo", deps=(), **kw):
    d = {"id": tid, "stage": stage, "kind": "meta", "deps": list(deps), "status": status}
    d.update(kw)
    return d


class PickTests(unittest.TestCase):
    def test_first_eligible_by_stage_then_id(self):
        tasks = [t("P1-001", 1), t("P0-010", 0), t("P0-002", 0)]
        v, task = nt.pick(tasks, NOW)
        self.assertEqual((v, task["id"]), ("TASK", "P0-002"))

    def test_natural_id_order(self):
        tasks = [t("P4-x-10", 4), t("P4-x-2", 4)]
        self.assertEqual(nt.pick(tasks, NOW)[1]["id"], "P4-x-2")

    def test_unmet_dep_is_not_eligible(self):
        tasks = [t("A-1", deps=["A-0"]), t("A-0", status="doing", claimed_at=NOW.isoformat())]
        self.assertEqual(nt.pick(tasks, NOW)[0], "NONE-WAITING")

    def test_blocked_dep_is_not_satisfied(self):
        tasks = [t("A-0", status="blocked"), t("A-1", deps=["A-0"])]
        self.assertEqual(nt.pick(tasks, NOW)[0], "NONE-BLOCKED")

    def test_skipped_dep_is_not_done(self):
        tasks = [t("A-0", status="skipped"), t("A-1", deps=["A-0"])]
        self.assertNotEqual(nt.pick(tasks, NOW)[0], "TASK")

    def test_unknown_dep_is_not_eligible(self):
        self.assertNotEqual(nt.pick([t("A-1", deps=["ghost"])], NOW)[0], "TASK")

    def test_complete(self):
        tasks = [t("A-0", status="done"), t("A-1", status="skipped")]
        self.assertEqual(nt.pick(tasks, NOW)[0], "NONE-COMPLETE")

    def test_fresh_claim_is_not_reclaimed(self):
        fresh = (NOW - datetime.timedelta(minutes=59)).isoformat()
        self.assertEqual(nt.pick([t("A-0", status="doing", claimed_at=fresh)], NOW)[0], "NONE-WAITING")

    def test_stale_claim_is_reclaimed(self):
        old = (NOW - datetime.timedelta(minutes=61)).isoformat()
        v, task = nt.pick([t("A-0", status="doing", claimed_at=old)], NOW)
        self.assertEqual((v, task["id"]), ("TASK", "A-0"))

    def test_date_only_claim_parses(self):
        v, _ = nt.pick([t("A-0", status="doing", claimed_at="2026-11-18")], NOW)
        self.assertEqual(v, "TASK")

    def test_counts(self):
        c = nt.counts([t("a"), t("b", status="done"), t("c", status="done")])
        self.assertEqual((c["todo"], c["done"], c["blocked"]), (1, 2, 0))


class QueueTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp(prefix="next_task_")
        self.q = os.path.join(self.tmp, "loop", "queue")
        os.makedirs(os.path.join(self.q, "generated"))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def write(self, rel, rows):
        with open(os.path.join(self.q, rel), "w", encoding="utf-8") as fh:
            for r in rows:
                fh.write(json.dumps(r) + "\n")

    def test_amendment_adds_deps_so_gate_waits(self):
        self.write("seed.jsonl", [t("P4-000", 4, "done"), t("P4-999", 4, deps=["P4-000"])])
        self.write("generated/translate.jsonl", [t("P4-src-1", 4, deps=["P4-000"])])
        self.write("generated/amendments.jsonl", [{"amend": "P4-999", "add_deps": ["P4-src-1"]}])
        tasks, problems = nt.load_queue(self.q)
        self.assertEqual(problems, [])
        v, task = nt.pick(tasks, NOW)
        self.assertEqual(task["id"], "P4-src-1")     # the gate no longer jumps the queue
        gate = [x for x in tasks if x["id"] == "P4-999"][0]
        self.assertEqual(gate["deps"], ["P4-000", "P4-src-1"])

    def test_without_amendment_gate_would_run_first(self):
        """Negative control for the test above."""
        self.write("seed.jsonl", [t("P4-000", 4, "done"), t("P4-999", 4, deps=["P4-000"])])
        self.write("generated/translate.jsonl", [t("P4-src-1", 4, deps=["P4-000"])])
        tasks, _ = nt.load_queue(self.q)
        self.assertEqual(nt.pick(tasks, NOW)[1]["id"], "P4-999")

    def test_check_flags_duplicates_unknown_deps_and_cycles(self):
        self.write("seed.jsonl", [t("A", deps=["B"]), t("B", deps=["A"]), t("C", deps=["zzz"])])
        self.write("generated/x.jsonl", [t("C")])
        tasks, problems = nt.load_queue(self.q)
        bad = " | ".join(nt.check(tasks, problems))
        self.assertIn("duplicate task id C", bad)
        self.assertIn("dependency cycle", bad)
        self.assertIn("unknown dep zzz", bad)

    def test_check_passes_on_clean_queue(self):
        self.write("seed.jsonl", [t("A", status="done"), t("B", deps=["A"])])
        tasks, problems = nt.load_queue(self.q)
        self.assertEqual(nt.check(tasks, problems), [])

    def test_amend_of_unknown_task_is_reported(self):
        self.write("seed.jsonl", [t("A")])
        self.write("generated/a.jsonl", [{"amend": "nope", "add_deps": ["A"]}])
        tasks, problems = nt.load_queue(self.q)
        self.assertTrue(any("unknown task nope" in p for p in problems))

    def test_amend_can_set_tier_only(self):
        self.write("seed.jsonl", [t("A")])
        self.write("generated/a.jsonl", [{"amend": "A", "set": {"tier": "light"}}])
        tasks, problems = nt.load_queue(self.q)
        self.assertEqual(problems, [])
        self.assertEqual(tasks[0]["tier"], "light")
        self.write("generated/a.jsonl", [{"amend": "A", "set": {"status": "done"}}])
        tasks, problems = nt.load_queue(self.q)
        self.assertTrue(any("may only set tier" in p for p in problems))
        self.assertNotIn("tier", tasks[0])

    def test_main_exit_codes(self):
        self.write("seed.jsonl", [t("A")])
        self.assertEqual(nt.main(["--queue", self.q, "--id"]), 0)
        self.write("seed.jsonl", [t("A", status="blocked")])
        self.assertEqual(nt.main(["--queue", self.q]), 1)
        self.write("seed.jsonl", [t("A", status="done")])
        self.assertEqual(nt.main(["--queue", self.q]), 3)

    def test_seedtask_updates_generated_task_only(self):
        self.write("seed.jsonl", [t("A")])
        self.write("generated/translate.jsonl", [t("P4-src-1", 4), t("P4-src-2", 4)])
        old = os.getcwd()
        os.chdir(self.tmp)
        try:
            self.assertEqual(seedtask.main(["x", "P4-src-2", "done", "ok"]), 0)
            self.assertEqual(seedtask.main(["x", "nope", "done"]), 1)
        finally:
            os.chdir(old)
        tasks, _ = nt.load_queue(self.q)
        by = {x["id"]: x for x in tasks}
        self.assertEqual(by["P4-src-2"]["status"], "done")
        self.assertEqual(by["P4-src-2"]["notes"], "ok")
        self.assertEqual(by["P4-src-1"]["status"], "todo")
        self.assertEqual(by["A"]["status"], "todo")


class RealQueueTests(unittest.TestCase):
    """The committed queue must stay valid."""

    def test_repo_queue_has_no_problems(self):
        root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        tasks, problems = nt.load_queue(os.path.join(root, "loop", "queue"))
        self.assertEqual(nt.check(tasks, problems), [])


if __name__ == "__main__":
    unittest.main()
