import json
import os
import sys
import tempfile
import unittest

import polib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import waive_po  # noqa: E402


class TestWaivePo(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.po = os.path.join(self.tmp.name, "a.md.po")
        self.reg = os.path.join(self.tmp.name, "reg.jsonl")
        with open(self.reg, "w", encoding="utf-8") as f:
            f.write('{"id":"EXC-001","segment":"s-x","invariant":"I7","reason":"r","task":"T"}\n')
        po = polib.POFile()
        for sid, en, es in (("s-a-0000", "Run it in Windows Sandbox", "Ejecútalo en Windows Sandbox"),
                            ("s-b-0001", "How the stunt works", "Cómo funciona la acrobacia"),
                            ("s-c-0002", "Plain", "Llano")):
            po.append(polib.POEntry(msgctxt=sid, msgid=en, msgstr=es, flags=["fuzzy"], comment="I7: finding"))
        po.save(self.po)

    def entries(self):
        return {e.msgctxt: e for e in polib.pofile(self.po, wrapwidth=0)}

    def test_waive_clears_fuzzy_and_adds_register_row(self):
        rules = {"waive": {"s-a-0000": ["I7", "product name"]}, "set": {"s-b-0001": "Cómo funciona el truco"}}
        self.assertEqual(waive_po.waive(self.po, "T-9", rules, self.reg), (1, 1))
        ent = self.entries()
        self.assertNotIn("fuzzy", ent["s-a-0000"].flags)
        self.assertEqual(ent["s-a-0000"].msgstr, "Ejecútalo en Windows Sandbox")
        self.assertEqual(ent["s-b-0001"].msgstr, "Cómo funciona el truco")
        self.assertNotIn("fuzzy", ent["s-b-0001"].flags)
        self.assertIn("fuzzy", ent["s-c-0002"].flags)              # untouched entry stays a draft
        with open(self.reg, encoding="utf-8") as f:
            rows = [json.loads(line) for line in f if line.strip()]
        self.assertEqual([r["id"] for r in rows], ["EXC-001", "EXC-002"])
        self.assertEqual((rows[1]["segment"], rows[1]["task"]), ("s-a-0000", "T-9"))

    def test_unknown_segment_changes_nothing(self):
        with self.assertRaises(KeyError):
            waive_po.waive(self.po, "T", {"waive": {"s-zzz": ["I7", "why"]}}, self.reg)
        self.assertIn("fuzzy", self.entries()["s-a-0000"].flags)
        with open(self.reg, encoding="utf-8") as f:
            self.assertEqual(len(f.readlines()), 1)

    def test_empty_reason_is_refused_and_nothing_written(self):
        with self.assertRaises(ValueError):
            waive_po.waive(self.po, "T", {"waive": {"s-a-0000": ["I7", "  "]}}, self.reg)
        self.assertIn("fuzzy", self.entries()["s-a-0000"].flags)
        with open(self.reg, encoding="utf-8") as f:
            self.assertEqual(len(f.readlines()), 1)


if __name__ == "__main__":
    unittest.main()
