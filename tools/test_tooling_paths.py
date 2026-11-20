#!/usr/bin/env python3
"""Tests for tools/tooling_paths.py. Run: python3 -I tools/test_tooling_paths.py"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import tooling_paths as tp  # noqa: E402

MAPPING = {
    "lessons/answers-key.md": "lessons/respuestas.md",
    "lessons/cs/README.md": "lessons/informatica/README.md",
    "lessons/cs/01-a.md": "lessons/informatica/01-a.md",
    "lessons/study-guides/languages/apl.md": "lessons/guias-de-estudio/lenguajes/apl.md",
    "lessons/index.md": "lessons/indice.md",
    "lessons/cs-source/index.md": "lessons/cs-source/index.md",
    "lessons/book/build.py": "lessons/book/build.py",
    "README.md": "README.md",
}
LITERALS, FOLDERS = tp.candidates(MAPPING)


def scan(source):
    return [text for _, text in tp.scan_source(source, LITERALS, FOLDERS)]


class Candidates(unittest.TestCase):
    def test_suffixes_that_differ_are_candidates(self):
        self.assertIn("lessons/answers-key.md", LITERALS)
        self.assertIn("answers-key.md", LITERALS)
        self.assertIn("cs/README.md", LITERALS)
        self.assertIn("languages/apl.md", LITERALS)
        self.assertIn("study-guides", FOLDERS)

    def test_names_that_do_not_change_are_not(self):
        self.assertNotIn("README.md", LITERALS)
        self.assertNotIn("apl.md", LITERALS)         # the file name is the same in Spanish
        self.assertNotIn("build.py", LITERALS)


class Scanning(unittest.TestCase):
    def test_a_hard_coded_path_is_found(self):
        self.assertEqual(scan('x = open("lessons/answers-key.md")\n'), ["lessons/answers-key.md"])
        self.assertEqual(scan('x = "cs/README.md"\n'), ["cs/README.md"])
        self.assertEqual(scan('x = "see ../cs/README.md#top"\n'), ["see ../cs/README.md#top"])   # a message naming a path is flagged too
        self.assertEqual(scan('x = "../cs/README.md#top"\n'), ["../cs/README.md#top"])

    def test_an_f_string_part_is_found(self):
        self.assertEqual(scan('x = f"study-guides/languages/apl.md"\n'), ["study-guides/languages/apl.md"])
        self.assertEqual(scan('x = f"lessons/answers-key.md:{n}"\n'), [])        # not a path: has a suffix after the name

    def test_a_bare_folder_in_a_join_is_found(self):
        self.assertEqual(scan('import os\nx = os.path.join(LESSONS, "study-guides")\n'), ["study-guides"])
        self.assertEqual(scan('x = {"study-guides": 1}\n'), [])                   # a dictionary key is not a path

    def test_a_mapper_argument_is_exempt(self):
        self.assertEqual(scan('x = P("cs/README.md")\n'), [])
        self.assertEqual(scan('x = cat.path("lessons/answers-key.md")\n'), [])
        self.assertEqual(scan('x = P(f"cs/{fn}")\n'), [])
        self.assertEqual(scan('x = os.path.join(a, P("study-guides"))\n'), [])

    def test_a_table_of_english_keys_is_exempt(self):
        self.assertEqual(scan('ALL_GUIDES = ["languages/apl.md"]\n'), [])
        self.assertEqual(scan('OTHER = ["languages/apl.md"]\n'), ["languages/apl.md"])

    def test_docstrings_and_comments_are_exempt(self):
        self.assertEqual(scan('"""lessons/answers-key.md"""\ndef f():\n    """lessons/answers-key.md"""\n    return 1  # lessons/index.md\n'), [])

    def test_markers_exempt_a_line_but_only_that_line(self):
        self.assertEqual(scan('x = "lessons/index.md"  # en-key\ny = "lessons/index.md"\n'), ["lessons/index.md"])
        self.assertEqual(scan('x = "index.md"  # path-ok: cs-source/index.md is not renamed\n'), [])

    def test_a_kept_path_that_shares_a_name_needs_the_marker(self):
        # "index.md" is also the name of lessons/index.md, so the tool cannot tell them apart: that is why the marker exists
        self.assertEqual(scan('x = os.path.join(CSSRC, "index.md")\n'), ["index.md"])


class TestModules(unittest.TestCase):
    """P3B-006b: a test module that names a renamed file fails in the Spanish checkout, so it is scanned like the tooling."""

    def test_a_literal_in_a_test_class_is_found(self):
        src = 'import unittest\nclass T(unittest.TestCase):\n    def test_x(self):\n        open("lessons/answers-key.md")\n'
        self.assertEqual(scan(src), ["lessons/answers-key.md"])
        self.assertEqual(scan('class T:\n    def test_x(self):\n        open("study-guides/languages/apl.md")\n'),
                         ["study-guides/languages/apl.md"])

    def test_a_class_decorated_english_only_is_skipped_whole(self):
        src = '@english_only\nclass T:\n    def test_x(self):\n        open("lessons/answers-key.md")\n'
        self.assertEqual(scan(src), [])
        self.assertEqual(scan('@unittest.english_only\nclass T:\n    x = "lessons/answers-key.md"\n'), [])
        self.assertEqual(scan(src.replace("@english_only\n", "")), ["lessons/answers-key.md"])        # the control: same class, no decorator

    def test_a_class_that_declares_english_names_and_its_subclasses_are_skipped(self):
        base = 'class Base:\n    NAMES = "english"\n    x = "lessons/answers-key.md"\n'
        self.assertEqual(scan(base), [])
        self.assertEqual(scan(base + 'class Sub(Base):\n    y = "lessons/answers-key.md"\n'), [])
        self.assertEqual(scan(base + 'class Other:\n    y = "lessons/answers-key.md"\n'), ["lessons/answers-key.md"])
        self.assertEqual(scan(base.replace('"english"', '"spanish"')), ["lessons/answers-key.md"])      # only the English declaration exempts

    def test_the_exemption_does_not_leak_past_the_class(self):
        src = '@english_only\nclass T:\n    x = 1\ny = "lessons/answers-key.md"\n'
        self.assertEqual(scan(src), ["lessons/answers-key.md"])

    def test_the_literals_the_gate_failed_on_are_found(self):
        # regression fixture: the literals the Spanish checkout broke on (gate report of P3B-007), spelled as the tests had them
        literals, folders = tp.candidates(tp.load_map())
        old = ('METADATA = {"study-guides": ROOT / "lessons/study-guides/metadata.yaml"}\n'
               'front = open("lessons/front-matter.md")\n'
               'goals = read("docs/curriculum.md")\n')
        self.assertEqual(len(tp.scan_source(old, literals, folders)), 3)


class RealTooling(unittest.TestCase):
    def test_the_build_and_check_tooling_is_clean(self):
        literals, folders = tp.candidates(tp.load_map())
        for f in tp.default_files():
            with open(f, encoding="utf-8") as fh:
                hits = tp.scan_source(fh.read(), literals, folders)
            self.assertEqual(hits, [], f)

    def test_the_default_set_covers_the_builders(self):
        names = {os.path.relpath(f, tp.ROOT) for f in tp.default_files()}
        for must in ("lessons/book/cs.py", "lessons/book/study_guides.py", "lessons/book/build.py",
                     "lessons/plan-de-estudios/build.py", "lessons/guias-de-estudio/build.py",     # the builders move with their folder
                     "lessons/book/guide_impact.py"):
            self.assertIn(must, names)
        for must in ("lessons/book/test_repo_links.py", "lessons/book/test_cs.py", "lessons/book/test_study_guides.py",
                     "lessons/book/test_editorial.py", "lessons/book/test_curriculum.py", "lessons/book/test_pdf_lint.py",
                     "lessons/book/test_document_links.py"):      # P3B-006b: the tests are scanned too
            self.assertIn(must, names)

    def test_it_would_fail_on_the_old_hard_coded_code(self):
        # the pre-catalog line from cs.py, as a regression fixture: this is what the tool exists to stop
        literals, folders = tp.candidates(tp.load_map())
        old = 'CSOUT = os.path.join(LESSONS, "cs")\nmanifest = os.path.join(LESSONS, "study-guides", "chapters.txt")\nx = "lessons/answers-key.md"\n'
        self.assertEqual(len(tp.scan_source(old, literals, folders)), 3)


if __name__ == "__main__":
    unittest.main()
