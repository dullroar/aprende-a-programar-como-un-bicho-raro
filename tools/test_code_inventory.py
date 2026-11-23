#!/usr/bin/env python3
"""Tests for tools/code_inventory.py. Run: python3 -I tools/test_code_inventory.py"""
import hashlib
import json
import os
import shutil
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import code_inventory as ci  # noqa: E402

REAL_ROOT = os.path.dirname(HERE)


def rec(path, text):
    d = tempfile.mkdtemp()
    try:
        full = os.path.join(d, path)
        os.makedirs(os.path.dirname(full), exist_ok=True)
        with open(full, "w", encoding="utf-8", newline="") as f:
            f.write(text)
        return ci.inventory_file(d, path)
    finally:
        shutil.rmtree(d)


def names(r, role=None):
    return {i["name"] for i in r["identifiers"] if role is None or role in i["roles"]}


class Lexers(unittest.TestCase):
    def test_python_ast_roles(self):
        r = rec("a.py", "import os\n# note\ndef f(hours):\n    total = hours + os.sep  # sum\n"
                        "    return 'Total: %d' % total\n")
        self.assertEqual(r["parser"], "python-ast+tokenize")
        self.assertEqual(len(r["comments"]), 2)
        self.assertIn("total", names(r, "declaration"))
        self.assertIn("hours", names(r, "declaration"))
        self.assertIn("sep", names(r, "member"))
        self.assertIn("def", names(r, "keyword"))

    def test_comment_marker_inside_string_is_not_comment(self):
        r = rec("a.py", "x = '# not a comment'\n")
        self.assertEqual(r["comments"], [])
        self.assertEqual(len(r["strings"]), 1)

    def test_csharp_string_vs_comment(self):
        r = rec("P.cs", 'var s = "// not"; // real\n/* block\nmore */ int total = 1;\n')
        self.assertEqual(r["comments"][0]["text"], "// real")
        self.assertEqual(r["comments"][1]["end_line"], 3)
        self.assertEqual(r["strings"][0]["text"], "// not")
        self.assertIn("total", names(r, "declaration"))

    def test_rust_lifetime_is_not_string(self):
        r = rec("m.rs", "fn f<'a>(x: &'a str) -> char { 'z' }\n")
        self.assertEqual([s["text"] for s in r["strings"]], ["'z'"])

    def test_shell_hash_and_heredoc_sql(self):
        r = rec("x.sh", "#!/bin/sh\necho a#b # c\nsqlite3 db <<'SQL'\nSELECT 1; -- x\nSQL\necho done\n")
        self.assertEqual(len(r["comments"]), 2)  # shebang and '# c'; a#b is not a comment
        self.assertTrue(any(e["kind"] == "heredoc" and e["lang"] == "sql" for e in r["embedded"]))
        self.assertNotIn("SELECT", names(r))  # the heredoc body is not host code

    def test_cobol_fixed_comment_and_hyphen(self):
        r = rec("t.cob", "      * a note\n       PROGRAM-ID. T.\n       DISPLAY \"hi\". *> tail\n")
        self.assertEqual(len(r["comments"]), 2)
        self.assertIn("PROGRAM-ID", names(r))
        self.assertEqual(r["strings"][0]["text"], "hi")

    def test_apl_and_lisp(self):
        self.assertEqual(rec("a.apl", "x←1 ⍝ note\n")["comments"][0]["text"], "⍝ note")
        r = rec("a.lisp", "; c\n#| b |#\n(format t \"hi~%\") #\\;\n")
        self.assertEqual(len(r["comments"]), 2)

    def test_forth_comments_and_strings(self):
        r = rec("src/forth/t.fs", "\\ line\n( stack ) : f .\" Total\" ;\n")
        self.assertEqual(r["host"], "forth")
        self.assertEqual(len(r["comments"]), 2)
        self.assertEqual(r["strings"][0]["text"], "Total")

    def test_fsharp_outside_forth(self):
        self.assertEqual(rec("src/fsharp/p.fs", "let x = 1\n")["host"], "fsharp")

    def test_sql_string_embedded_in_host(self):
        r = rec("a.py", "q = 'SELECT total FROM cards'\n")
        self.assertTrue(any(e["lang"] == "sql" for e in r["embedded"]))

    def test_regex_family_flagged(self):
        r = rec("src/regex-perl/run.pl", "print 1 if /a/;\n")
        self.assertTrue(any(e["lang"] == "regex" for e in r["embedded"]))

    def test_script_block_in_xml(self):
        r = rec("a.xaml", "<!-- c --><Page><script>var a=1;</script></Page>\n")
        self.assertTrue(any(e["lang"] == "javascript" for e in r["embedded"]))
        self.assertEqual(len(r["comments"]), 1)

    def test_binary_and_crlf(self):
        d = tempfile.mkdtemp()
        try:
            with open(os.path.join(d, "x.jar"), "wb") as f:
                f.write(b"PK\0\0")
            self.assertEqual(ci.inventory_file(d, "x.jar")["host"], "binary")
        finally:
            shutil.rmtree(d)
        self.assertIn("crlf", rec("a.bat", "REM hi\r\necho x\r\n")["flags"])

    def test_string_classes(self):
        self.assertEqual(ci.classify_string("Total hours so far", "python"), "display-candidate")
        self.assertEqual(ci.classify_string("%d items", "c"), "format-or-template")
        self.assertEqual(ci.classify_string("./data/cards.db", "sh"), "path-or-contract")
        self.assertEqual(ci.classify_string("INSERT INTO t VALUES (1)", "sh"), "sql")


class Coverage(unittest.TestCase):
    def setUp(self):
        self.d = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.d, "translation/part2"))
        os.makedirs(os.path.join(self.d, "src"))
        lines = []
        for p, t in {"src/a.py": "x = 1\n", "src/b.sh": "echo hi\n"}.items():
            with open(os.path.join(self.d, p), "w") as f:
                f.write(t)
            lines.append(hashlib.sha256(t.encode()).hexdigest() + "  " + p)
        with open(os.path.join(self.d, ci.MANIFEST), "w") as f:
            f.write("\n".join(lines) + "\n")
        self.out = os.path.join(self.d, ci.OUT_JSONL)
        with open(self.out, "w") as f:
            f.write(ci.dump_jsonl(ci.build(self.d)))

    def tearDown(self):
        shutil.rmtree(self.d)

    def test_complete_inventory_passes(self):
        self.assertEqual(ci.check(self.d), [])

    def test_missing_path_fails(self):  # negative
        lines = open(self.out).read().splitlines()[:1]
        open(self.out, "w").write("\n".join(lines) + "\n")
        self.assertTrue(any("0 times" in p for p in ci.check(self.d)))

    def test_duplicate_path_fails(self):  # negative
        lines = open(self.out).read().splitlines()
        open(self.out, "w").write("\n".join(lines + lines[:1]) + "\n")
        self.assertTrue(any("2 times" in p for p in ci.check(self.d)))

    def test_changed_file_fails(self):  # negative: inventory sha vs lock
        r = [json.loads(x) for x in open(self.out)]
        r[0]["sha256"] = "0" * 64
        open(self.out, "w").write(ci.dump_jsonl(r))
        self.assertTrue(any("differs" in p for p in ci.check(self.d)))


class RealRepo(unittest.TestCase):
    def test_committed_inventory_covers_every_locked_path_once(self):
        self.assertEqual(ci.check(REAL_ROOT), [])
        n = len(ci.load_manifest(REAL_ROOT))
        with open(os.path.join(REAL_ROOT, ci.OUT_JSONL), encoding="utf-8") as f:
            self.assertEqual(sum(1 for _ in f), n)


if __name__ == "__main__":
    unittest.main()
