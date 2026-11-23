#!/usr/bin/env python3
"""Tests for tools/token_registry.py. Run: python3 -I tools/test_token_registry.py

Includes drift negative cases: a hand-edited page, a tampered JSONL token, a stray page, a failed
compile fixture and a not-extracted record that smuggles tokens must all be reported.
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import token_registry as tr  # noqa: E402

FAKE_NODE = json.dumps({"version": "v0.0.0-test", "reserved": ["class", "export"],
                        "contextual": ["let"], "globals": ["Array", "console"]})


def fake_runner(args):
    assert json.loads(args[0]), "probe list must be passed"
    return FAKE_NODE


def small_extractors():
    return {"python": tr.extract_python, "javascript": lambda: tr.extract_javascript(fake_runner)}


class Base(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory(dir=os.path.join(tr.ROOT, "translation", "work")
                                                if os.path.isdir(os.path.join(tr.ROOT, "translation", "work")) else None)
        self.dir = os.path.join(self._tmp.name, "pt")
        self.records = tr.build_all(self.dir, small_extractors())
        tr.write_all(self.records, self.dir)

    def tearDown(self):
        self._tmp.cleanup()

    def check(self, **kw):
        return tr.check(self.dir, extractors=small_extractors(), **kw)


class Extraction(unittest.TestCase):
    def test_python_from_introspection(self):
        import keyword
        r = tr.extract_python()
        reserved = {t["token"] for t in r["tokens"] if t["kind"] == "reserved"}
        self.assertEqual(reserved, set(keyword.kwlist))
        self.assertIn("print", {t["token"] for t in r["tokens"] if t["kind"] == "api"})
        self.assertTrue(all(f["ok"] for f in r["fixtures"]))
        self.assertTrue(r["version"].startswith("CPython 3."))

    def test_javascript_uses_runner_output(self):
        r = tr.extract_javascript(fake_runner)
        kinds = {t["token"]: t["kind"] for t in r["tokens"]}
        self.assertEqual(kinds, {"class": "reserved", "export": "reserved", "let": "contextual",
                                 "Array": "api", "console": "api"})
        self.assertEqual(r["version"], "Node v0.0.0-test")

    def test_unextracted_languages_have_no_tokens(self):
        recs = {r["language"]: r for r in tr.build_all(tempfile.gettempdir(), small_extractors())}
        for lang in ("cobol", "forth", "tcl"):
            self.assertEqual(recs[lang]["status"], "not-extracted")
            self.assertEqual(recs[lang]["tokens"], [])
            self.assertEqual(recs[lang]["version"], "NOT TESTED")

    def test_every_record_validates(self):
        self.assertEqual(tr.validate(tr.build_all(tempfile.gettempdir(), small_extractors())), [])

    def test_spec_file_reader(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "x.txt")
            with open(p, "w", encoding="utf-8") as f:
                f.write("# version: 1.0\n# source: the spec, section 2\n# command: manual extract\n"
                        "reserved if\ncontextual where\napi map\n")
            r = tr.extract_spec("x", p)
            self.assertEqual([t["kind"] for t in r["tokens"]], ["reserved", "contextual", "api"])
            with open(p, "w", encoding="utf-8") as f:
                f.write("# version: 1.0\n# source: s\n# command: c\nbogus if\n")
            with self.assertRaises(ValueError):
                tr.extract_spec("x", p)
            with open(p, "w", encoding="utf-8") as f:
                f.write("reserved if\n")
            with self.assertRaises(ValueError):
                tr.extract_spec("x", p)


class Drift(Base):
    def test_clean_tree_passes(self):
        self.assertEqual(self.check(), [])
        self.assertEqual(self.check(reextract=True), [])

    def test_hand_edited_page_is_drift(self):
        page = os.path.join(self.dir, "python.md")
        with open(page, "a", encoding="utf-8") as f:
            f.write("`bogus`\n")
        self.assertTrue(any("python.md drifted" in p for p in self.check()))

    def test_tampered_jsonl_token_is_drift(self):
        jp = os.path.join(self.dir, tr.JSONL)
        recs = tr.load_jsonl(jp)
        for r in recs:
            if r["language"] == "python":
                r["tokens"] = [t for t in r["tokens"] if t["token"] != "while"]
        with open(jp, "w", encoding="utf-8") as f:
            f.write(tr.dump_jsonl(recs))
        self.assertTrue(any("python.md drifted" in p for p in self.check()))

    def test_stale_registry_caught_by_reextract(self):
        jp = os.path.join(self.dir, tr.JSONL)
        recs = tr.load_jsonl(jp)
        for r in recs:
            if r["language"] == "python":
                r["version"] = "CPython 2.7.18"
        tr.write_all(recs, self.dir)  # pages regenerated, so only a fresh extraction can notice
        self.assertEqual(self.check(), [])
        self.assertTrue(any("differs from a fresh extraction" in p for p in self.check(reextract=True)))

    def test_stray_page_is_reported(self):
        with open(os.path.join(self.dir, "klingon.md"), "w", encoding="utf-8") as f:
            f.write("x\n")
        self.assertTrue(any("klingon.md has no record" in p for p in self.check()))

    def test_missing_page_is_reported(self):
        os.remove(os.path.join(self.dir, "javascript.md"))
        self.assertTrue(any("javascript.md is missing" in p for p in self.check()))

    def test_noncanonical_jsonl_is_reported(self):
        jp = os.path.join(self.dir, tr.JSONL)
        with open(jp, encoding="utf-8") as f:
            text = f.read()
        with open(jp, "w", encoding="utf-8") as f:
            f.write(text.replace('"status":"extracted"', '"status": "extracted"', 1))
        self.assertTrue(any("canonical" in p for p in self.check()))

    def test_missing_jsonl(self):
        os.remove(os.path.join(self.dir, tr.JSONL))
        self.assertTrue(any("missing" in p for p in self.check()))


class Validation(unittest.TestCase):
    def recs(self):
        return tr.build_all(tempfile.gettempdir(), small_extractors())

    def test_failed_fixture_is_a_problem(self):
        recs = self.recs()
        for r in recs:
            if r["language"] == "python":
                r["fixtures"][0]["ok"] = False
        self.assertTrue(any("compile fixture failed" in p for p in tr.validate(recs)))

    def test_not_extracted_with_tokens_is_a_problem(self):
        recs = self.recs()
        for r in recs:
            if r["language"] == "cobol":
                r["tokens"] = [{"token": "MOVE", "kind": "reserved", "source": "memory"}]
        self.assertTrue(any("must have no tokens" in p for p in tr.validate(recs)))

    def test_token_without_source_is_a_problem(self):
        recs = self.recs()
        for r in recs:
            if r["language"] == "python":
                r["tokens"][0]["source"] = ""
        self.assertTrue(any("no source" in p for p in tr.validate(recs)))

    def test_extracted_without_version_is_a_problem(self):
        recs = self.recs()
        for r in recs:
            if r["language"] == "python":
                r["version"] = ""
        self.assertTrue(any("no version" in p for p in tr.validate(recs)))

    def test_conflicting_kinds_are_a_problem(self):
        recs = self.recs()
        for r in recs:
            if r["language"] == "python":
                r["tokens"].append({"token": "if", "kind": "contextual", "source": "x"})
        self.assertTrue(any("listed as" in p for p in tr.validate(recs)))

    def test_compile_fixture_can_fail(self):
        # The fixture logic itself: a soft keyword compiles, a hard one does not.
        self.assertTrue(tr._py_compiles("match = 1"))
        self.assertFalse(tr._py_compiles("class = 1"))


if __name__ == "__main__":
    unittest.main()
