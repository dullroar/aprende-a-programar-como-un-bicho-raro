import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import embedded_blocks as eb  # noqa: E402

REC = [
    {"path": "a.sh", "host": "shell", "embedded": [{"lang": "sql", "kind": "string", "line": 3, "end_line": 4}]},
    {"path": "b.py", "host": "python", "embedded": []},
]


class T(unittest.TestCase):
    def test_rows(self):
        rows = eb.rows_from(REC)
        self.assertEqual(len(rows), 1)
        self.assertEqual((rows[0]["host"], rows[0]["embedded"]), ("shell", "sql"))

    def test_md_counts(self):
        self.assertIn("| shell | sql | 1 | 1 |", eb.render_md(eb.rows_from(REC)))

    def test_on_disk_matches_inventory(self):
        self.assertEqual(eb.check(), [])

    def test_negative_drift_detected(self):
        # an inventory with an extra block must disagree with the files on disk
        extra = REC + [{"path": "c.sh", "host": "shell",
                        "embedded": [{"lang": "regex", "kind": "string", "line": 1, "end_line": 1}]}]
        self.assertNotEqual(eb.render_jsonl(eb.rows_from(extra)), eb.read(eb.OUT_JSONL))
        self.assertTrue(eb.check(extra))


if __name__ == "__main__":
    unittest.main()
