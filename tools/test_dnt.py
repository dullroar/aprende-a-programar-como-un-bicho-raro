#!/usr/bin/env python3
"""Tests for tools/dnt.py. Run: python3 -I tools/test_dnt.py"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dnt  # noqa: E402


def program_files(n=3, extra=""):
    """Fake frozen sources: n entries each printing the required phrases."""
    files = {}
    for i in range(n):
        files[f"src/lang{i}/timecards.py"] = (
            'cats = ["Meetings", "Coding", "Debugging", "Learning"]\n'
            'print("# DEMO ONLY run " + run)\n'
            'print("# committed total=" + t + " entries=" + e + " DEMO ONLY")\n'
            + extra
        )
    return files


class ClassifyTests(unittest.TestCase):
    def test_category_needs_enough_entries(self):
        self.assertIn(("category", "Coding"), dnt.classify_literal("Coding", 3))
        self.assertEqual(dnt.classify_literal("Coding", 2), [])

    def test_marker_is_stripped_and_kept(self):
        self.assertIn(("marker", "# DEMO ONLY run"), dnt.classify_literal("# DEMO ONLY run ", 3))

    def test_shell_variables_and_escapes_are_not_phrases(self):
        self.assertEqual(dnt.classify_literal("# got $x", 5), [])
        self.assertEqual(dnt.classify_literal("# a\\tb", 5), [])
        self.assertEqual(dnt.classify_literal("", 5), [])

    def test_env_var_and_path(self):
        self.assertIn(("identifier", "XDG_DATA_HOME"), dnt.classify_literal("XDG_DATA_HOME", 3))
        self.assertIn(("path", "demo-timecards.db"), dnt.classify_literal("demo-timecards.db", 3))

    def test_ordinary_words_are_not_dnt(self):
        for word in ("window", "title", "start", "data", "for", "while"):
            self.assertEqual(dnt.classify_literal(word, 9), [], word)

    def test_sql_identifiers(self):
        sql = "INSERT INTO demo_timecards(run_id,running_total) VALUES (?, ?)"
        got = {p for k, p in dnt.classify_literal(sql, 2) if k == "identifier"}
        self.assertEqual(got, {"demo_timecards", "run_id", "running_total"})


class BuildTests(unittest.TestCase):
    def test_build_finds_required_phrases(self):
        found = dnt.build(program_files())
        for p in dnt.REQUIRED:
            self.assertIn(p, found)
        self.assertIn("# committed total=", found)
        self.assertIn("entries=", found)

    def test_non_program_files_are_ignored(self):
        files = program_files()
        for i in range(5):
            files[f"src/lang{i}/check.sh"] = 'echo "FAIL: # nope="\necho "HOME_DIR_X"\n'
        found = dnt.build(files)
        self.assertNotIn("FAIL: # nope=", found)
        self.assertNotIn("HOME_DIR_X", found)

    def test_missing_required_phrase_fails(self):
        files = {p: t.replace("Learning", "Studying") for p, t in program_files().items()}
        with self.assertRaises(dnt.DntError) as cm:
            dnt.build(files)
        self.assertIn("Learning", str(cm.exception))

    def test_too_few_entries_fails(self):
        with self.assertRaises(dnt.DntError):
            dnt.build(program_files(n=2))

    def test_render_is_sorted_unique_and_stable(self):
        a = dnt.render(dnt.build(program_files()))
        b = dnt.render(dnt.build(dict(reversed(list(program_files().items())))))
        self.assertEqual(a, b)
        lines = a.splitlines()
        self.assertEqual(lines, sorted(set(lines)))

    def test_entry_of(self):
        self.assertEqual(dnt.entry_of("src/awk/timecards.awk"), "src/awk")
        self.assertEqual(dnt.entry_of("lessons/solutions/awk-port/x.awk"), "lessons/solutions")


class RealTreeTests(unittest.TestCase):
    """Against the actual frozen sources and the committed translation/dnt.txt."""

    def test_committed_list_is_current_and_has_required_phrases(self):
        root = dnt.repo_root()
        fresh = dnt.render(dnt.build(dnt.load_files(root)))
        with open(os.path.join(root, dnt.OUTPUT), encoding="utf-8") as fh:
            committed = fh.read()
        self.assertEqual(committed, fresh)
        lines = committed.splitlines()
        for p in ("Meetings", "Coding", "Debugging", "Learning", "DEMO ONLY"):
            self.assertIn(p, lines)

    def test_check_detects_drift(self):
        import tempfile
        root = dnt.repo_root()
        with tempfile.TemporaryDirectory(dir=os.path.join(root, "translation", "work")) as tmp:
            os.makedirs(os.path.join(tmp, "translation"))
            # copy the manifest and the frozen program files that matter
            for rel in dnt.read_manifest_paths(root):
                if dnt.is_program(rel):
                    dst = os.path.join(tmp, rel)
                    os.makedirs(os.path.dirname(dst), exist_ok=True)
                    with open(os.path.join(root, rel), "rb") as s, open(dst, "wb") as d:
                        d.write(s.read())
            with open(os.path.join(root, dnt.MANIFEST), "rb") as s, \
                    open(os.path.join(tmp, dnt.MANIFEST), "wb") as d:
                d.write(s.read())
            with open(os.path.join(tmp, dnt.OUTPUT), "w", encoding="utf-8") as fh:
                fh.write("Meetings\n")  # stale on purpose
            self.assertEqual(dnt.main(["--check", "--root", tmp]), 1)
            self.assertEqual(dnt.main(["--write", "--root", tmp]), 0)
            self.assertEqual(dnt.main(["--check", "--root", tmp]), 0)


if __name__ == "__main__":
    unittest.main()
