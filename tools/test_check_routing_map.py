import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import check_routing_map as crm  # noqa: E402

HEADER = "| kind | route | reason | measurement | expected cost change |\n| --- | --- | --- | --- | --- |\n"


class RoutingMapTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.queue = os.path.join(self.tmp.name, "queue")
        os.makedirs(os.path.join(self.queue, "generated"))
        rows = [{"id": "a", "kind": "alpha"}, {"id": "b", "kind": "beta"}]
        with open(os.path.join(self.queue, "seed.jsonl"), "w", encoding="utf-8") as f:
            for r in rows:
                f.write(json.dumps(r) + "\n")
        with open(os.path.join(self.queue, "generated", "x.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"amend": "a", "set": {"tier": "light"}}) + "\n")
            f.write(json.dumps({"id": "c", "kind": "gamma"}) + "\n")

    def run_map(self, body):
        path = os.path.join(self.tmp.name, "routing.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Map\n\n" + HEADER + body)
        return crm.check(self.queue, path)

    GOOD = (
        "| alpha | script | r1 | no history | none |\n"
        "| beta | `batch` | r2 | 3 runs | lower |\n"
        "| gamma | operator | r3 | no history | none |\n"
    )

    def test_complete_map_passes(self):
        self.assertEqual(self.run_map(self.GOOD), [])

    def test_extra_kind_is_allowed(self):
        self.assertEqual(self.run_map(self.GOOD + "| delta | ci | r4 | no history | none |\n"), [])

    def test_missing_kind_fails(self):
        defects = self.run_map("".join(self.GOOD.splitlines(True)[:2]))
        self.assertEqual(len(defects), 1)
        self.assertIn("gamma", defects[0])
        self.assertIn("no row", defects[0])

    def test_unknown_route_fails(self):
        defects = self.run_map(self.GOOD.replace("| script |", "| magic |"))
        self.assertTrue(any("unknown route" in d and "alpha" in d for d in defects))

    def test_empty_reason_fails(self):
        defects = self.run_map(self.GOOD.replace("| r2 |", "|  |"))
        self.assertEqual(len(defects), 1)
        self.assertIn("empty reason", defects[0])

    def test_empty_measurement_fails(self):
        defects = self.run_map(self.GOOD.replace("| 3 runs |", "|  |"))
        self.assertEqual(len(defects), 1)
        self.assertIn("empty measurement", defects[0])

    def test_kind_with_two_routes(self):
        body = self.GOOD + "| alpha | ci | r5 | no history | none |\n"
        self.assertEqual(self.run_map(body), [])

    def test_missing_file_fails(self):
        defects = crm.check(self.queue, os.path.join(self.tmp.name, "none.md"))
        self.assertEqual(len(defects), 1)
        self.assertIn("not found", defects[0])


if __name__ == "__main__":
    unittest.main()
