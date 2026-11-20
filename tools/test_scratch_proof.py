#!/usr/bin/env python3
"""Tests for tools/scratch_proof.py. Run: python3 -I tools/test_scratch_proof.py (never starts a real build)."""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import scratch_proof as sp  # noqa: E402

SCRATCH_TMP = os.path.join(os.path.dirname(HERE), "translation", "work", "test-scratch-proof")


def six(tag="a"):
    return {"f%d.%s" % (i, "pdf" if i % 2 else "epub"): tag * 64 for i in range(6)}


class LayerTests(unittest.TestCase):
    def test_parse_allowlist_strips_comments_and_blanks(self):
        self.assertEqual(sp.parse_allowlist(["# c", "", "a/b.py  # why", "  c.py "]), ["a/b.py", "c.py"])

    def test_layer_excludes_metadata_and_includes_locale_catalog(self):
        files = sp.layer_files()
        self.assertFalse([f for f in files if f.endswith("metadata.yaml")])
        for must in ("lessons/book/locale/catalog.py", "lessons/book/locale/en.yaml",
                     "lessons/book/locale/es.yaml", "lessons/book/diagrams.py"):
            self.assertIn(must, files)
        self.assertFalse([f for f in files if "__pycache__" in f or f.endswith(".pyc")])

    def test_every_layer_file_exists(self):
        for rel in sp.layer_files():
            self.assertTrue(os.path.isfile(sp.enpath.load(sp.ROOT).full(rel)), rel)      # moved files sit at their working path

    def test_layer_excludes_data_files_workflows_and_metadata(self):
        files = sp.layer_files()
        for data in sp.DATA_FILES + (".github/workflows/pdf-release-gate.yml",):
            self.assertNotIn(data, files)
            self.assertTrue(sp.is_data(data))
        self.assertFalse(sp.is_data("lessons/book/cs.py"))                    # negative: code stays in the layer

    def test_apply_layer_reads_a_moved_file_at_its_working_path(self):
        os.makedirs(SCRATCH_TMP, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=SCRATCH_TMP) as d:
            src, dst = os.path.join(d, "s"), os.path.join(d, "d")
            os.makedirs(os.path.join(src, "translation"))
            os.makedirs(os.path.join(src, "lessons", "book", "locale"))
            os.makedirs(os.path.join(src, "lessons", "guias"))
            with open(os.path.join(src, "translation", "path-map.yaml"), "w", encoding="utf-8") as f:
                f.write('schema: 1\npaths:\n  "lessons/guides/build.py": "lessons/guias/build.py"\n')
            with open(os.path.join(src, "lessons", "book", "locale", "es.yaml"), "w", encoding="utf-8") as f:
                f.write('paths:\n  layout: "spanish"\n')
            with open(os.path.join(src, "lessons", "guias", "build.py"), "wb") as f:
                f.write(b"x = 1\n")
            sp.apply_layer(src, dst, ["lessons/guides/build.py"])
            with open(os.path.join(dst, "lessons", "guides", "build.py"), "rb") as f:   # lands at the English key
                self.assertEqual(f.read(), b"x = 1\n")

    def test_apply_layer_copies_bytes(self):
        os.makedirs(SCRATCH_TMP, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=SCRATCH_TMP) as d:
            src, dst = os.path.join(d, "s"), os.path.join(d, "d")
            os.makedirs(os.path.join(src, "x"))
            with open(os.path.join(src, "x", "a.py"), "wb") as f:
                f.write(b"print(1)\r\n")
            sp.apply_layer(src, dst, ["x/a.py"])
            with open(os.path.join(dst, "x", "a.py"), "rb") as f:
                self.assertEqual(f.read(), b"print(1)\r\n")


class CompareTests(unittest.TestCase):
    def test_identical_maps_pass(self):
        self.assertEqual(sp.compare("pre", six(), "post", six()), [])

    def test_one_changed_byte_fails_and_names_the_file(self):
        b = six()
        b["f3.pdf"] = "b" * 64
        problems = sp.compare("pre", six(), "post", b)
        self.assertEqual(len(problems), 1)
        self.assertIn("f3.pdf differs", problems[0])

    def test_missing_artifact_fails(self):
        b = six()
        del b["f0.epub"]
        problems = sp.compare("pre", six(), "post", b)
        self.assertTrue([p for p in problems if "only in pre" in p])
        self.assertTrue([p for p in problems if "has 5 artifacts" in p])

    def test_two_empty_maps_do_not_pass(self):
        self.assertTrue(sp.compare("pre", {}, "post", {}))

    def test_extra_artifact_fails(self):
        b = six()
        b["extra.pdf"] = "c" * 64
        self.assertTrue([p for p in sp.compare("pre", six(), "post", b) if "extra.pdf only in post" in p])


class BuildRoundTests(unittest.TestCase):
    """build_round with fake builders that write one file; proves failures and nondeterminism are caught."""

    def fake(self, d, name, body):
        path = os.path.join(d, name + ".py")
        with open(path, "w", encoding="utf-8") as f:
            f.write("import sys\nout = sys.argv[sys.argv.index('--artifacts-dir') + 1]\n" + body)
        return (name, name + ".py")

    def test_round_hashes_outputs_and_reports_failure(self):
        os.makedirs(SCRATCH_TMP, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=SCRATCH_TMP) as d:
            good = self.fake(d, "good", "open(out + '/g.pdf', 'w').write('x')\n")
            bad = self.fake(d, "bad", "sys.exit(4)\n")
            out_dir = os.path.join(d, "out")
            probs, _ = sp.build_round(d, out_dir, builders=[good, bad], timeout=60)
            self.assertEqual(len(probs), 1)
            self.assertIn("build bad exit 4", probs[0])
            self.assertEqual(list(sp.hash_dir(out_dir)), ["g.pdf"])

    def test_nondeterministic_builder_is_detected(self):
        os.makedirs(SCRATCH_TMP, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=SCRATCH_TMP) as d:
            flaky = self.fake(d, "flaky", "import os\nopen(out + '/n.pdf', 'wb').write(os.urandom(8))\n")
            r1, r2 = os.path.join(d, "r1"), os.path.join(d, "r2")
            sp.build_round(d, r1, builders=[flaky], timeout=60)
            sp.build_round(d, r2, builders=[flaky], timeout=60)
            problems = sp.compare("r1", sp.hash_dir(r1), "r2", sp.hash_dir(r2), expected=1)
            self.assertTrue([p for p in problems if "n.pdf differs" in p])

    def test_english_env_drops_book_lang(self):
        os.environ["BOOK_LANG"] = "es"
        try:
            self.assertNotIn("BOOK_LANG", sp.english_env())
        finally:
            del os.environ["BOOK_LANG"]


class RenderTests(unittest.TestCase):
    def info(self, problems):
        h = six()
        return {"sha": "abc", "layer": ["a.py"], "problems": problems, "checks": [("book", 0)],
                "secs": [1, 2, 3, 4], "pre1": h, "pre2": h, "post1": h, "post2": h}

    def test_pass_and_fail_wording(self):
        self.assertIn("**PASS**", sp.render(self.info([])))
        text = sp.render(self.info(["f.pdf differs"]))
        self.assertIn("**FAIL**", text)
        self.assertNotIn("**PASS**", text)


if __name__ == "__main__":
    unittest.main()
