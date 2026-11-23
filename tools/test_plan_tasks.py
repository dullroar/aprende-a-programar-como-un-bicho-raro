#!/usr/bin/env python3
"""Tests for tools/plan_tasks.py. Run: python3 -I tools/test_plan_tasks.py"""
import copy
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import plan_tasks as pt  # noqa: E402


def f(path, words, segs=None, cls="authored"):
    return {"path": path, "class": cls, "words": words,
            "segments": segs if segs is not None else max(1, words // 20)}


def inv(*files):
    return {"files": list(files)}


SAMPLE = inv(
    f("src/a/README.md", 1500), f("src/b/README.md", 1500), f("src/c/README.md", 1500),
    f("src/d/README.md", 900),
    f("lessons/study-guides/languages/big.md", 9000, 450),
    f("lessons/cs/generated.md", 5000, cls="generated"),
    f("src/a/code.py", 700, cls="frozen"),
    f("docs/x.md", 300),
)


def run_plan(inventory, existing=(), cap=4000, batch=8, pilots=frozenset()):
    return pt.plan(inventory, cap, batch, list(existing), set(pilots))


def tasks_of(rows):
    return [r for r in rows if r["kind"] == "translate"]


class SplitAndCapTests(unittest.TestCase):
    def test_only_authored_files_are_planned(self):
        rows, _, _ = run_plan(SAMPLE)
        covered = {i.split("#")[0] for r in tasks_of(rows) for i in r["inputs"]}
        self.assertNotIn("lessons/cs/generated.md", covered)
        self.assertNotIn("src/a/code.py", covered)
        self.assertIn("docs/x.md", covered)

    def test_no_task_exceeds_cap(self):
        rows, _, st = run_plan(SAMPLE)
        for r in tasks_of(rows):
            self.assertLessEqual(r["words"], 4000, r["id"])
        self.assertLessEqual(st["max_task_words"], 4000)

    def test_cap_is_honoured_when_lowered(self):
        rows, _, _ = run_plan(SAMPLE, cap=1000)
        for r in tasks_of(rows):
            self.assertLessEqual(r["words"], 1500 + 1, r["id"])  # a single 1500-word file stands alone
            if len(r["inputs"]) > 1:
                self.assertLessEqual(r["words"], 1000, r["id"])

    def test_big_file_split_into_numbered_parts_covering_all_segments(self):
        rows, _, _ = run_plan(SAMPLE)
        parts = [i for r in tasks_of(rows) for i in r["inputs"]
                 if i.startswith("lessons/study-guides/languages/big.md#")]
        self.assertEqual(len(parts), 3)  # ceil(9000 / 4000)
        spans = sorted(tuple(int(x) for x in p.split("#s")[1].split("-")) for p in parts)
        self.assertEqual(spans[0][0], 1)
        self.assertEqual(spans[-1][1], 450)
        for (a, b), (c, d) in zip(spans, spans[1:]):
            self.assertEqual(c, b + 1)  # no gap, no overlap

    def test_split_parts_stand_alone(self):
        rows, _, _ = run_plan(SAMPLE)
        for r in tasks_of(rows):
            if any("#s" in i for i in r["inputs"]):
                self.assertEqual(len(r["inputs"]), 1)
                self.assertEqual(
                    r["accept"],
                    f"python3 tools/verify.py --fast --files {r['inputs'][0].split('#s')[0]}",
                )

    def test_every_word_planned_exactly_once(self):
        rows, _, st = run_plan(SAMPLE)
        keys = [i for r in tasks_of(rows) for i in r["inputs"]]
        self.assertEqual(len(keys), len(set(keys)))
        want = sum(x["words"] for x in SAMPLE["files"] if x["class"] == "authored")
        self.assertAlmostEqual(st["words"], want, delta=3)

    def test_group_order_follows_plan(self):
        rows, _, _ = run_plan(SAMPLE)
        ids = [r["id"] for r in tasks_of(rows)]
        self.assertTrue(ids[0].startswith("P4-src-"))
        self.assertTrue(ids[-1].startswith("P4-docs-"))


class AuditAndDepTests(unittest.TestCase):
    def many(self, n):
        return inv(*[f("src/e%02d/README.md" % i, 3000) for i in range(n)])

    def test_audit_after_every_batch_and_next_batch_waits_for_it(self):
        rows, _, st = run_plan(self.many(20), batch=8)
        self.assertEqual(st["audits"], 3)
        by = {r["id"]: r for r in rows}
        a1 = by["P4-audit-1"]
        self.assertEqual(len(a1["deps"]), 8)
        order = [r["id"] for r in rows]
        self.assertEqual(order[8], "P4-audit-1")
        ninth = by[order[9]]
        self.assertIn("P4-audit-1", ninth["deps"])
        first = by[order[0]]
        self.assertEqual(first["deps"], ["P4-000"])

    def test_gate_amendment_lists_every_generated_task(self):
        rows, amend, _ = run_plan(self.many(10))
        self.assertEqual(len(amend), 1)
        self.assertEqual(amend[0]["amend"], "P4-999")
        self.assertEqual(set(amend[0]["add_deps"]), {r["id"] for r in rows})

    def test_no_gate_amendment_without_gate_task(self):
        _, amend, _ = pt.plan(self.many(2), 4000, 8, [], set(), "P4-000", None)
        self.assertEqual(amend, [])

    def test_pilot_files_are_noted(self):
        rows, _, _ = run_plan(SAMPLE, pilots={"src/a/README.md"})
        noted = [r for r in tasks_of(rows) if "src/a/README.md" in r["inputs"]][0]
        self.assertIn("already translated in Phase 3", noted["notes"])


class IdempotenceTests(unittest.TestCase):
    def test_second_run_is_identical(self):
        rows1, am1, _ = run_plan(SAMPLE)
        rows2, am2, st2 = run_plan(SAMPLE, existing=rows1)
        self.assertEqual(pt.dumps(rows1), pt.dumps(rows2))
        self.assertEqual(am1, am2)
        self.assertEqual(st2["new"], 0)

    def test_finished_tasks_are_never_reset(self):
        rows1, _, _ = run_plan(SAMPLE)
        done = copy.deepcopy(rows1)
        first = [r for r in done if r["kind"] == "translate"][0]
        first.update(status="done", attempts=2, notes="segments all accepted", claimed_by=9)
        snapshot = dict(first)
        rows2, _, _ = run_plan(SAMPLE, existing=done)
        again = {r["id"]: r for r in rows2}[first["id"]]
        self.assertEqual(again, snapshot)

    def test_blocked_and_doing_tasks_survive_even_if_file_vanishes(self):
        rows1, _, _ = run_plan(SAMPLE)
        rows = copy.deepcopy(rows1)
        tr = tasks_of(rows)
        tr[0]["status"] = "blocked"
        tr[1]["status"] = "doing"
        smaller = inv(*[x for x in SAMPLE["files"] if x["path"] != "src/a/README.md"])
        rows2, _, _ = run_plan(smaller, existing=rows)
        ids = {r["id"] for r in rows2}
        self.assertIn(tr[0]["id"], ids)
        self.assertIn(tr[1]["id"], ids)

    def test_todo_progress_notes_are_kept(self):
        rows1, _, _ = run_plan(SAMPLE)
        rows = copy.deepcopy(rows1)
        t = tasks_of(rows)[0]
        t["notes"] = "segments 1 to 14 done; resume at segment 15"
        rows2, _, _ = run_plan(SAMPLE, existing=rows)
        again = {r["id"]: r for r in rows2}[t["id"]]
        self.assertEqual(again["notes"], t["notes"])

    def test_new_file_becomes_new_task_without_touching_others(self):
        rows1, _, _ = run_plan(SAMPLE)
        grown = inv(*(SAMPLE["files"] + [f("docs/new.md", 500)]))
        rows2, _, st = run_plan(grown, existing=rows1)
        self.assertEqual(st["new"], 1)
        old = {r["id"]: r for r in rows1 if r["kind"] == "translate"}
        new = {r["id"]: r for r in rows2 if r["kind"] == "translate"}
        self.assertEqual(set(new) - set(old), {"P4-docs-2"})
        for tid, r in old.items():
            self.assertEqual(new[tid]["inputs"], r["inputs"])

    def test_done_file_is_not_planned_twice_when_repacking(self):
        rows1, _, _ = run_plan(SAMPLE)
        rows = copy.deepcopy(rows1)
        for r in tasks_of(rows):
            if "docs/x.md" in r["inputs"]:
                r["status"] = "done"
        rows2, _, _ = run_plan(SAMPLE, existing=rows)
        keys = [i for r in tasks_of(rows2) for i in r["inputs"]]
        self.assertEqual(keys.count("docs/x.md"), 1)

    def test_negative_wrong_status_reset_would_be_caught(self):
        """The reset check above must be able to fail: a reset task differs from its snapshot."""
        rows1, _, _ = run_plan(SAMPLE)
        done = copy.deepcopy(rows1)
        first = tasks_of(done)[0]
        first["status"] = "done"
        reset = dict(first, status="todo")
        self.assertNotEqual(reset, first)


class FileIoTests(unittest.TestCase):
    def setUp(self):
        import tempfile
        self.tmp = tempfile.mkdtemp(prefix="plan_tasks_")
        self.old = os.getcwd()
        os.chdir(self.tmp)
        for d in ("loop/queue", "translation/work"):
            os.makedirs(d)
        with open("translation/work/inventory.json", "w", encoding="utf-8") as fh:
            json.dump(SAMPLE, fh)
        with open("loop/CONFIG.yaml", "w", encoding="utf-8") as fh:
            fh.write("translate_task_max_source_words: 4000   # cap\naudit_every_n_translate_tasks: 8\n")
        seed = [{"id": "P4-000", "stage": 4, "kind": "meta", "deps": [], "status": "done"},
                {"id": "P4-999", "stage": 4, "kind": "gate", "deps": ["P4-000"], "status": "todo"}]
        with open("loop/queue/seed.jsonl", "w", encoding="utf-8") as fh:
            fh.write(pt.dumps(seed))

    def tearDown(self):
        import shutil
        os.chdir(self.old)
        shutil.rmtree(self.tmp, ignore_errors=True)

    def read(self):
        out = {}
        for n in (pt.TRANSLATE_FILE, pt.AMEND_FILE):
            with open(os.path.join(pt.GENERATED_DIR, n), "rb") as fh:
                out[n] = fh.read()
        return out

    def test_run_twice_gives_identical_bytes(self):
        self.assertEqual(pt.run(), 0)
        first = self.read()
        self.assertEqual(pt.run(), 0)
        self.assertEqual(first, self.read())

    def test_check_detects_stale_files(self):
        self.assertEqual(pt.run(), 0)
        self.assertEqual(pt.run(check=True), 0)
        with open(os.path.join(pt.GENERATED_DIR, pt.TRANSLATE_FILE), "a", encoding="utf-8") as fh:
            fh.write("\n")
        self.assertEqual(pt.run(check=True), 1)      # stray blank line: bytes differ
        self.assertEqual(pt.run(), 0)                # a normal run repairs it
        self.assertEqual(pt.run(check=True), 0)
        os.remove(os.path.join(pt.GENERATED_DIR, pt.AMEND_FILE))
        self.assertEqual(pt.run(check=True), 1)

    def test_missing_inventory_is_an_error(self):
        os.remove("translation/work/inventory.json")
        self.assertEqual(pt.run(), 2)

    def test_config_cap_is_read(self):
        self.assertEqual(pt.read_config("loop/CONFIG.yaml")["translate_task_max_source_words"], "4000")


SCOPE_SAMPLE = {
    "(root)": {"never": True, "status": "frozen"},
    "src/forth": {"never": False, "status": "frozen"},
    "src/awk": {"never": False, "status": "frozen"},
    "src/GoChallenge1": {"never": False, "status": "frozen"},
    "src/cobol-weird": {"never": False, "status": "frozen"},
    "src/regex-sed": {"never": False, "status": "frozen"},
    "src/ed-weird": {"never": False, "status": "frozen"},
}


def p2(scope=SCOPE_SAMPLE, existing=(), batch=3, **kw):
    return pt.plan_part2(scope, {}, list(existing), batch, **kw)


class Part2Tests(unittest.TestCase):
    def test_covers_every_non_never_family_exactly_once(self):
        rows, _, _ = p2()
        fams = [r["family"] for r in rows if r["kind"] == "localize-code"]
        self.assertEqual(sorted(fams), sorted(f for f, v in SCOPE_SAMPLE.items() if not v["never"]))
        self.assertEqual(len(fams), len(set(fams)))

    def test_risk_order(self):
        rows, _, _ = p2()
        fams = [r["family"] for r in rows if r["kind"] == "localize-code"]
        self.assertEqual(fams, ["src/forth", "src/awk", "src/GoChallenge1", "src/cobol-weird",
                                "src/regex-sed", "src/ed-weird"])

    def test_audit_every_batch_and_chain(self):
        rows, amend, _ = p2()
        by = {r["id"]: r for r in rows}
        self.assertEqual(by["S5-audit-1"]["deps"], ["S5-fam-forth", "S5-fam-awk", "S5-fam-gochallenge1"])
        self.assertIn("S5-audit-1", by["S5-fam-cobol-weird"]["deps"])
        self.assertNotIn("S5-audit-1", by["S5-fam-forth"]["deps"])
        self.assertEqual(amend[0]["amend"], "S5-999")
        self.assertEqual(set(amend[0]["add_deps"]), {r["id"] for r in rows})

    def test_unclassified_family_is_an_error(self):
        scope = dict(SCOPE_SAMPLE)
        scope["src/brand-new"] = {"never": False, "status": "frozen"}
        with self.assertRaises(ValueError):
            p2(scope)

    def test_never_family_is_not_planned(self):
        rows, _, _ = p2()
        self.assertFalse([r for r in rows if r.get("family") == "(root)"])

    def test_finished_task_is_never_reset(self):
        rows, _, _ = p2()
        done = dict(rows[0], status="done", attempts=2, notes="kept")
        again, _, _ = p2(existing=[done])
        self.assertEqual(again[0], done)

    def test_idempotent(self):
        rows, amend, _ = p2()
        again = p2(existing=rows)
        self.assertEqual(pt.dumps(rows), pt.dumps(again[0]))
        self.assertEqual(amend, again[1])

    def test_todo_notes_survive(self):
        rows, _, _ = p2()
        rows[1] = dict(rows[1], notes="resume at file 2", attempts=1)
        again, _, _ = p2(existing=rows)
        self.assertEqual(again[1]["notes"], "resume at file 2")

    def test_size_class(self):
        self.assertEqual(pt.size_of({"lines": 10, "comments": 2, "strings": 1})[0], "S")
        self.assertEqual(pt.size_of({"lines": 900, "comments": 40, "strings": 10})[0], "M")
        self.assertEqual(pt.size_of({"lines": 3000, "comments": 0, "strings": 0})[0], "L")

    def test_real_scope_is_fully_classified(self):
        if not os.path.exists(pt.SCOPE):
            self.skipTest("no scope file")
        scope = pt.read_scope()
        for fam, v in scope.items():
            if not v["never"]:
                self.assertIsNotNone(pt.risk_of(fam), fam)
        rows, _, st = pt.plan_part2(scope, {}, [], 8)
        self.assertEqual(st["families"], sum(1 for v in scope.values() if not v["never"]))


if __name__ == "__main__":
    unittest.main()
