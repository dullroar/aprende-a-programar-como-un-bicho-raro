#!/usr/bin/env python3
"""Tests for tools/fixture_check.py. Run: python3 -I tools/test_fixture_check.py"""
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import fixture_check as fc  # noqa: E402


class FixtureCheck(unittest.TestCase):
    def setUp(self):
        work = os.path.join(os.path.dirname(HERE), "translation", "work")
        os.makedirs(work, exist_ok=True)
        self.tmp = tempfile.mkdtemp(dir=work)
        for name in fc.REQUIRED:
            shutil.copy(os.path.join(fc.DEFAULT_DIR, name), os.path.join(self.tmp, name))

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def edit(self, name, old, new):
        p = os.path.join(self.tmp, name)
        with open(p, encoding="utf-8", newline="") as f:
            t = f.read()
        self.assertIn(old, t)
        with open(p, "w", encoding="utf-8", newline="") as f:
            f.write(t.replace(old, new))

    def test_real_fixtures_pass(self):
        self.assertEqual(fc.check(), [])

    def test_copy_passes(self):
        self.assertEqual(fc.check(self.tmp), [])

    def test_missing_file_fails(self):
        os.remove(os.path.join(self.tmp, "hostile.md"))
        self.assertTrue(any("hostile.md: missing fixture file" in p for p in fc.check(self.tmp)))

    def test_normalized_unicode_fails(self):
        self.edit("mixed.md", "n" + fc.COMBINING_TILDE, chr(0xF1))
        self.assertTrue(any("combining mark" in p for p in fc.check(self.tmp)))

    def test_lost_nbsp_fails(self):
        self.edit("mixed.md", fc.NBSP, " ")
        self.assertTrue(any("non-breaking space" in p for p in fc.check(self.tmp)))

    def test_crlf_on_disk_fails(self):
        self.edit("mixed.md", "\n# Timecards", "\r\n# Timecards")
        self.assertTrue(any("contains CR" in p for p in fc.check(self.tmp)))

    def test_mermaid_without_accdescr_fails(self):
        self.edit("mermaid.md", "    accDescr: Alice sends a greeting to Bob and Bob replies.\n", "")
        self.assertTrue(any("accTitle and accDescr" in p for p in fc.check(self.tmp)))

    def test_unclosed_fence_fails(self):
        self.edit("mixed.md", "DEMO ONLY run\n```\n", "DEMO ONLY run\n")
        self.assertTrue(any("unclosed fence" in p or "missing feature" in p for p in fc.check(self.tmp)))

    def test_lost_timecard_rule_fails(self):
        self.edit("mixed.md", "exactly 40 continues", "continues")
        self.assertTrue(any("timecard rule" in p for p in fc.check(self.tmp)))

    def test_invalid_utf8_fails(self):
        with open(os.path.join(self.tmp, "data.yaml"), "wb") as f:
            f.write(b"id: \xff\xfe\n")
        self.assertTrue(any("not valid UTF-8" in p for p in fc.check(self.tmp)))

    def test_fences_parser(self):
        self.assertEqual(fc.fences("```py\nx\n```\n~~~\ny\n~~~\n"), [("py", "x"), ("", "y")])
        with self.assertRaises(ValueError):
            fc.fences("```py\nx\n")


if __name__ == "__main__":
    unittest.main()
