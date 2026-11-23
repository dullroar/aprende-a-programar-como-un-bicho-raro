#!/usr/bin/env python3
"""Tests for tools/loc_map.py. Run: python3 -I tools/test_loc_map.py

Negative cases: unscoped entry, frozen and never families, unknown path, collision with a keyword,
a Python builtin and a case-folded COBOL word, not-extracted language, duplicate new name, swap,
bad evidence, extra field, malformed JSON.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import loc_map as lm  # noqa: E402

SCOPE = {"fam": {"status": "localizing", "never": False},
         "frozen": {"status": "frozen", "never": False},
         "nope": {"status": "localizing", "never": True}}
FAMS = {"a.py": "fam", "b.py": "frozen", "c.py": "nope", "d.cob": "fam"}
REG = {"python": {"status": "extracted", "tokens": [{"token": "class"}, {"token": "def"}]},
       "cobol": {"status": "extracted", "tokens": [{"token": "PERFORM"}]},
       "forth": {"status": "not-extracted", "tokens": []}}


def rec(**kw):
    base = {"language": "python", "entry": "e1", "path": "a.py", "old": "total", "new": "suma",
            "role": "variable", "scope": "function:main",
            "evidence": ["translation/part2/reports/e1.md"], "approver": "loop"}
    base.update(kw)
    return base


def check(*records):
    return lm.validate(list(records), SCOPE, FAMS, REG)


class Valid(unittest.TestCase):
    def test_good_record(self):
        self.assertEqual(check(rec()), [])

    def test_empty_ledger(self):
        self.assertEqual(check(), [])

    def test_same_new_name_in_other_scope_is_fine(self):
        self.assertEqual(check(rec(), rec(old="x", scope="function:other")), [])

    def test_repo_ledger_is_valid(self):
        self.assertEqual(lm.validate(lm.load_jsonl(lm.MAP)), [])


class Negative(unittest.TestCase):
    def has(self, errs, text):
        self.assertTrue(any(text in e for e in errs), errs)

    def test_unscoped(self):
        self.has(check(rec(scope="somewhere")), "unscoped")
        self.has(check(rec(scope="")), "empty")
        self.has(check(rec(scope="function:")), "unscoped")

    def test_frozen_family(self):
        self.has(check(rec(path="b.py")), "not localizing")

    def test_never_family(self):
        self.has(check(rec(path="c.py")), "not localizing")

    def test_unknown_path(self):
        self.has(check(rec(path="zzz.py")), "not a protected file")

    def test_keyword_collision(self):
        self.has(check(rec(new="class")), "collides")

    def test_builtin_collision(self):
        self.has(check(rec(new="print")), "collides")

    def test_case_folded_collision(self):
        self.has(check(rec(language="cobol", path="d.cob", old="X", new="perform")), "collides")

    def test_case_sensitive_language_allows_other_case(self):
        self.assertEqual(check(rec(new="Class")), [])

    def test_not_extracted_language(self):
        self.has(check(rec(language="forth")), "collision cannot be checked")
        self.has(check(rec(language="unknown")), "collision cannot be checked")

    def test_duplicate_new(self):
        self.has(check(rec(), rec(old="other")), "already used")

    def test_old_renamed_twice(self):
        self.has(check(rec(), rec(new="otra")), "renamed twice")

    def test_swap(self):
        self.has(check(rec(old="a", new="b"), rec(old="b", new="a")), "old name of record")

    def test_same_name(self):
        self.has(check(rec(new="total")), "identical")

    def test_not_identifier(self):
        self.has(check(rec(new="1x")), "not an identifier")
        self.has(check(rec(new="a b")), "not an identifier")

    def test_evidence(self):
        self.has(check(rec(evidence=[])), "evidence")
        self.has(check(rec(evidence=["elsewhere/x.md"])), "evidence")
        self.has(check(rec(evidence="translation/part2/reports/x.md")), "evidence")

    def test_role_and_approver(self):
        self.has(check(rec(role="vibe")), "role")
        self.has(check(rec(approver=" ")), "empty")

    def test_extra_and_missing_fields(self):
        r = rec()
        r["bonus"] = 1
        self.has(check(r), "extra")
        r2 = rec()
        del r2["scope"]
        self.has(check(r2), "missing")


class Cli(unittest.TestCase):
    def run_main(self, text):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "m.jsonl")
            with open(p, "w", encoding="utf-8") as fh:
                fh.write(text)
            return lm.main(["--check", "--map", p])

    def test_empty_file_ok(self):
        self.assertEqual(self.run_main(""), 0)

    def test_bad_json_fails(self):
        self.assertEqual(self.run_main("{not json\n"), 1)

    def test_entry_in_frozen_repo_fails(self):
        line = json.dumps(rec(path=".gitattributes", language="python")) + "\n"
        self.assertEqual(self.run_main(line), 1)


if __name__ == "__main__":
    unittest.main()
