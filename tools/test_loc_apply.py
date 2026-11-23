#!/usr/bin/env python3
"""Tests for tools/loc_apply.py. Run: python3 -I tools/test_loc_apply.py

Positive: comment, display string and identifier edits; idempotent re-run; CRLF comment kept.
Negative: frozen/never/unknown family, binary, protected-token rename (old and new), new name already
in the file, comment terminator smuggling, line-count change without anchor, PO msgid mismatch,
non-display string, placeholder drift, unmapped file, lexical scope limits, unparsable Python,
bad msgctxt.
"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import loc_apply as la  # noqa: E402

SCOPE = {"fam": {"status": "localizing", "never": False},
         "frozen": {"status": "frozen", "never": False},
         "nope": {"status": "localizing", "never": True}}
FAMS = {"a.py": "fam", "b.py": "frozen", "c.py": "nope", "d.c": "fam", "e.bin": "fam", "f.sh": "fam",
        "g.bat": "fam"}
REG = {"python": {"status": "extracted", "tokens": [{"token": "def"}, {"token": "len"}]},
       "c": {"status": "extracted", "tokens": [{"token": "int"}]},
       "shell": {"status": "not-extracted", "tokens": []}}

PY = '# add up the hours\ndef main():\n    total = 0\n    print("Total hours worked")\n    return total\n'
EV = ["translation/part2/reports/x.md"]


def idrec(path="a.py", old="total", new="suma", scope="function:main", lang="python", role="variable"):
    return {"language": lang, "entry": "e", "path": path, "old": old, "new": new, "role": role,
            "scope": scope, "evidence": EV, "approver": "loop"}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name

    def tearDown(self):
        self.tmp.cleanup()

    def put(self, rel, content, mode="w"):
        p = os.path.join(self.root, rel)
        with open(p, mode, **({} if "b" in mode else {"encoding": "utf-8", "newline": ""})) as fh:
            fh.write(content)

    def run_apply(self, rel, po=None, records=None, anchors=None, families=None, scope=None):
        return la.apply_file(self.root, rel, scope=scope or SCOPE, families=families or FAMS, reg=REG,
                             records=records or [], po=po or [], anchors=anchors or [])


def L(line, old, new):
    return {"kind": "L", "line": line, "msgid": old, "msgstr": new}


def S(line, old, new):
    return {"kind": "S", "line": line, "msgid": old, "msgstr": new}


class Positive(Base):
    def test_comment_string_identifier(self):
        self.put("a.py", PY)
        old, new = self.run_apply("a.py", po=[L(1, "# add up the hours", "# suma las horas"),
                                              S(4, "Total hours worked", "Horas totales")],
                                  records=[idrec()])
        self.assertEqual(new, '# suma las horas\ndef main():\n    suma = 0\n    print("Horas totales")\n    return suma\n')

    def test_idempotent(self):
        self.put("a.py", PY)
        po = [L(1, "# add up the hours", "# suma las horas")]
        _, new = self.run_apply("a.py", po=po)
        self.put("a.py", new)
        old2, new2 = self.run_apply("a.py", po=po)
        self.assertEqual(old2, new2)

    def test_attribute_not_renamed(self):
        self.put("a.py", "def main():\n    total = 1\n    return obj.total + total\n")
        _, new = self.run_apply("a.py", records=[idrec()])
        self.assertIn("obj.total + suma", new)

    def test_crlf_comment_kept(self):
        self.put("f.sh", "# hola\r\necho hi\r\n")
        _, new = self.run_apply("f.sh", po=[L(1, "# hola", "# hello")])
        self.assertEqual(new, "# hello\r\necho hi\r\n")

    def test_line_change_with_anchor(self):
        self.put("d.c", "/* one */\nint x;\n")
        po = [L(1, "/* one */", "/* uno\n   dos */")]
        _, new = self.run_apply("d.c", po=po, anchors=[{"path": "d.c", "old_lines": 2, "new_lines": 3}])
        self.assertEqual(new.count("\n"), 3)

    def test_file_scope_lexical(self):
        self.put("d.c", "int total;\n/* total */\nchar *s = \"total\";\ntotal = 1;\n")
        _, new = self.run_apply("d.c", records=[idrec(path="d.c", lang="c", scope="file")])
        self.assertEqual(new, "int suma;\n/* total */\nchar *s = \"total\";\nsuma = 1;\n")


class Negative(Base):
    def refused(self, rel, **kw):
        with self.assertRaises(la.Refused) as cm:
            self.run_apply(rel, **kw)
        return str(cm.exception)

    def test_frozen_family(self):
        self.put("b.py", PY)
        self.assertIn("frozen", self.refused("b.py", po=[L(1, "# add up the hours", "# x")]))

    def test_never_family(self):
        self.put("c.py", PY)
        self.assertIn("never", self.refused("c.py", po=[L(1, "# add up the hours", "# x")]))

    def test_unknown_path(self):
        self.put("z.py", PY)
        self.assertIn("not a protected file", self.refused("z.py", po=[L(1, "# a", "# b")]))

    def test_binary(self):
        self.put("e.bin", b"\x00\x01\x02", mode="wb")
        self.assertIn("binary", self.refused("e.bin", po=[L(1, "a", "b")]))

    def test_nothing_mapped(self):
        self.put("a.py", PY)
        self.assertIn("nothing is mapped", self.refused("a.py"))

    def test_protected_token_new_name(self):
        self.put("a.py", PY)
        self.assertIn("collides", self.refused("a.py", records=[idrec(new="len")]))

    def test_protected_token_old_name(self):
        self.put("a.py", "def main():\n    len = 1\n    return len\n")
        self.assertIn("cannot be renamed", self.refused("a.py", records=[idrec(old="len", new="largo")]))

    def test_builtin_old_name(self):
        self.put("a.py", "def main():\n    print = 1\n    return print\n")
        self.assertIn("cannot be renamed", self.refused("a.py", records=[idrec(old="print", new="imprime")]))

    def test_new_name_already_in_file(self):
        self.put("a.py", "def main():\n    total = 1\n    suma = 2\n    return total + suma\n")
        self.assertIn("already occurs", self.refused("a.py", records=[idrec()]))

    def test_unscoped_record(self):
        self.put("a.py", PY)
        self.assertIn("unscoped", self.refused("a.py", records=[idrec(scope="somewhere")]))

    def test_no_occurrence(self):
        self.put("a.py", PY)
        self.assertIn("no occurrence", self.refused("a.py", records=[idrec(old="nothing", new="nada")]))

    def test_lexical_function_scope(self):
        self.put("d.c", "int total;\n")
        self.assertIn("lexical", self.refused("d.c", records=[idrec(path="d.c", lang="c")]))

    def test_comment_terminator_smuggled(self):
        self.put("d.c", "/* one */\nint x;\n")
        msg = self.refused("d.c", po=[L(1, "/* one */", "/* uno */ int y; /* dos */")])
        self.assertIn("exactly one comment", msg)

    def test_line_comment_gains_newline(self):
        self.put("a.py", PY)
        msg = self.refused("a.py", po=[L(1, "# add up the hours", "# suma\nimport os")])
        self.assertTrue("exactly one comment" in msg)

    def test_line_count_without_anchor(self):
        self.put("d.c", "/* one */\nint x;\n")
        msg = self.refused("d.c", po=[L(1, "/* one */", "/* uno\n   dos */")])
        self.assertIn("line-anchors", msg)

    def test_line_count_wrong_anchor(self):
        self.put("d.c", "/* one */\nint x;\n")
        msg = self.refused("d.c", po=[L(1, "/* one */", "/* uno\n   dos */")],
                           anchors=[{"path": "d.c", "old_lines": 2, "new_lines": 9}])
        self.assertIn("line-anchors", msg)

    def test_msgid_mismatch(self):
        self.put("a.py", PY)
        self.assertIn("does not match", self.refused("a.py", po=[L(1, "# something else", "# x")]))

    def test_no_comment_on_line(self):
        self.put("a.py", PY)
        self.assertIn("need exactly one", self.refused("a.py", po=[L(3, "# x", "# y")]))

    def test_string_not_display(self):
        self.put("a.py", 'x = "SELECT * FROM t"\n')
        self.assertIn("display-candidate", self.refused("a.py", po=[S(1, "SELECT * FROM t", "SELECCIONA")]))

    def test_format_string_refused(self):
        self.put("a.py", 'x = "Total: %d"\n')
        self.assertIn("display-candidate", self.refused("a.py", po=[S(1, "Total: %d", "Suma: %d")]))

    def test_placeholder_drift(self):
        self.put("a.py", PY)
        self.assertIn("placeholders", self.refused("a.py", po=[S(4, "Total hours worked", "Horas %s")]))

    def test_string_quote_smuggled(self):
        self.put("a.py", PY)
        self.assertIn("exactly one string", self.refused("a.py", po=[S(4, "Total hours worked", 'Horas" + x + "')]))

    def test_python_must_parse(self):
        self.put("a.py", "x = 1  # hola\n")
        # a comment replaced by a valid comment parses; make it fail by renaming into a keyword-like name
        r = idrec(old="x", new="1x", scope="file")
        self.assertTrue("not an identifier" in self.refused("a.py", records=[r]))

    def test_bad_msgctxt(self):
        with self.assertRaises(la.Refused):
            la.parse_po('msgctxt "line 3"\nmsgid "a"\nmsgstr "b"\n')


class PoReader(unittest.TestCase):
    def test_parse(self):
        po = la.parse_po('msgid ""\nmsgstr ""\n\nmsgctxt "L2"\nmsgid "# a\\n"\n"# b"\nmsgstr "# c"\n')
        self.assertEqual(po, [{"kind": "L", "line": 2, "msgid": "# a\n# b", "msgstr": "# c"}])


if __name__ == "__main__":
    unittest.main()
