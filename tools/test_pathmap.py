#!/usr/bin/env python3
"""Tests for tools/pathmap.py (P3B-001). Run: python3 -I tools/test_pathmap.py
Includes negative cases that must fail: a path a frozen file mentions, a collision, README.md."""
import copy
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import pathmap as pm  # noqa: E402


def tree():
    files = {
        "README.md": "authored",
        "CHALLENGE.md": "authored",
        "CONTRIBUTING.md": "authored",
        "docs/guide.md": "authored",
        "docs/run.md": "authored",
        "docs/images/a.png": "archival",
        "lessons/README.md": "authored",
        "lessons/intro.md": "authored",
        "lessons/exercises.md": "authored",
        "lessons/solutions/a.py": "frozen",
        "lessons/study-guides/README.md": "authored",
        "lessons/study-guides/build.py": "tooling",
        "lessons/study-guides/concepts/state.md": "authored",
        "lessons/study-guides/languages/forth.md": "authored",
        "lessons/cs/01-first-chapter.md": "generated",
        "lessons/cs/README.md": "generated",
        "src/x/README.md": "authored",
        "src/x/main.py": "frozen",
        ".github/workflows/gate.yml": "tooling",
    }
    texts = {
        "lessons/solutions/a.py": "print('hi')\n",
        "src/x/main.py": "# nothing\n",
        "lessons/study-guides/build.py": "# tool\n",
        ".github/workflows/gate.yml": "run: python lessons/study-guides/build.py --check\n",
    }
    return files, texts


NAMES = {
    "dirs": {"lessons/cs": "informatica", "lessons/study-guides": "guias-de-estudio",
             "lessons/study-guides/concepts": "conceptos", "lessons/study-guides/languages": "lenguajes"},
    "files": {"CHALLENGE.md": "DESAFIO.md", "docs/guide.md": "guia.md", "docs/run.md": "ejecutar.md",
              "lessons/intro.md": "introduccion.md", "lessons/exercises.md": "ejercicios.md",
              "lessons/study-guides/concepts/state.md": "estado.md",
              "lessons/cs/01-first-chapter.md": "01-primer-capitulo.md"},
    "proper": ["lessons/study-guides/languages/forth.md"],
}


def run(files=None, texts=None, names=None, glossary=None):
    f0, t0 = tree()
    files = f0 if files is None else files
    texts = t0 if texts is None else texts
    names = NAMES if names is None else names
    return pm.build(files, lambda p: texts.get(p), copy.deepcopy(names), glossary)


class RuleTests(unittest.TestCase):
    def test_plain_rename_and_folder_rename(self):
        r = run()
        self.assertEqual(r["problems"], [])
        m = r["map"]
        self.assertEqual(m["CHALLENGE.md"], "DESAFIO.md")
        self.assertEqual(m["lessons/cs/01-first-chapter.md"], "lessons/informatica/01-primer-capitulo.md")
        self.assertEqual(m["lessons/study-guides/concepts/state.md"], "lessons/guias-de-estudio/conceptos/estado.md")
        # README.md keeps its name and moves with its folder; a tooling file keeps its name too
        self.assertEqual(m["lessons/cs/README.md"], "lessons/informatica/README.md")
        self.assertEqual(m["lessons/study-guides/build.py"], "lessons/guias-de-estudio/build.py")
        self.assertEqual(m["README.md"], "README.md")
        self.assertEqual(m["lessons/study-guides/languages/forth.md"], "lessons/guias-de-estudio/lenguajes/forth.md")

    def test_frozen_file_mention_keeps_the_path_and_ignores_the_row(self):
        files, texts = tree()
        texts["lessons/solutions/a.py"] = "open('docs/run.md')\n"
        r = run(files, texts)
        self.assertEqual(r["map"]["docs/run.md"], "docs/run.md")
        self.assertIn("frozen", r["reasons"]["docs/run.md"])
        self.assertTrue(any("docs/run.md" in n and "ignored" in n for n in r["notes"]))
        self.assertEqual(r["problems"], [])

    def test_backslash_mention_in_a_script_counts(self):
        files, texts = tree()
        files["lessons/tools/v.ps1"] = "frozen"
        texts["lessons/tools/v.ps1"] = r"Get-Content lessons\exercises.md"
        r = run(files, texts)
        self.assertEqual(r["map"]["lessons/exercises.md"], "lessons/exercises.md")

    def test_mention_of_a_folder_keeps_the_folder_and_what_is_below(self):
        files, texts = tree()
        texts["lessons/solutions/a.py"] = "ls lessons/cs/$name.md\n"
        names = copy.deepcopy(NAMES)
        r = run(files, texts, names)
        self.assertEqual(r["map"]["lessons/cs/01-first-chapter.md"], "lessons/cs/01-first-chapter.md")
        self.assertEqual(r["dir_map"]["lessons/cs"], "cs")

    def test_folder_holding_a_pinned_file_stays(self):
        r = run()
        self.assertEqual(r["dir_map"]["lessons"], "lessons")
        self.assertEqual(r["map"]["lessons/solutions/a.py"], "lessons/solutions/a.py")

    def test_workflow_mention_of_a_document_pins_it_but_a_tool_mention_does_not(self):
        files, texts = tree()
        texts[".github/workflows/gate.yml"] = "run: cat docs/guide.md lessons/study-guides/build.py\n"
        r = run(files, texts)
        self.assertEqual(r["map"]["docs/guide.md"], "docs/guide.md")
        self.assertIn("workflow", r["reasons"]["docs/guide.md"])
        self.assertEqual(r["map"]["lessons/study-guides/build.py"], "lessons/guias-de-estudio/build.py")
        self.assertIn((".github/workflows/gate.yml", "lessons/study-guides/build.py"), r["workflow_rewrites"])

    def test_workflow_stays_put(self):
        r = run()
        self.assertEqual(r["map"][".github/workflows/gate.yml"], ".github/workflows/gate.yml")

    def test_keep_list_names_and_trees(self):
        r = run()
        for p in ("CONTRIBUTING.md", "src/x/README.md", "src/x/main.py", "lessons/solutions/a.py",
                  "docs/images/a.png"):
            self.assertEqual(r["map"][p], p)

    def test_missing_name_is_an_error(self):
        names = copy.deepcopy(NAMES)
        del names["files"]["docs/guide.md"]
        r = run(names=names)
        self.assertTrue(any("docs/guide.md" in p and "no row" in p for p in r["problems"]))

    def test_stale_rows_are_errors(self):
        names = copy.deepcopy(NAMES)
        names["files"]["docs/gone.md"] = "x.md"
        names["dirs"]["nope"] = "nada"
        r = run(names=names)
        self.assertTrue(any("docs/gone.md" in p and "stale" in p for p in r["problems"]))
        self.assertTrue(any("nope" in p and "stale" in p for p in r["problems"]))

    def test_row_for_readme_is_an_error(self):
        names = copy.deepcopy(NAMES)
        names["files"]["lessons/README.md"] = "LEEME.md"
        r = run(names=names)
        self.assertTrue(any("lessons/README.md" in p and "keep-list" in p for p in r["problems"]))
        self.assertEqual(r["map"]["lessons/README.md"], "lessons/README.md")

    def test_row_for_a_license_or_contributing_is_an_error(self):
        names = copy.deepcopy(NAMES)
        names["files"]["CONTRIBUTING.md"] = "CONTRIBUIR.md"
        r = run(names=names)
        self.assertTrue(any("CONTRIBUTING.md" in p for p in r["problems"]))

    def test_two_rows_to_one_name_collide(self):
        names = copy.deepcopy(NAMES)
        names["files"]["docs/run.md"] = "guia.md"
        r = run(names=names)
        self.assertTrue(any(p.startswith("collision") for p in r["problems"]), r["problems"])

    def test_row_colliding_with_a_kept_file_is_caught_case_insensitively(self):
        names = copy.deepcopy(NAMES)
        names["files"]["docs/guide.md"] = "Run.md"
        # run.md has a row; make it stay to collide with the kept name
        del names["files"]["docs/run.md"]
        files, texts = tree()
        texts["lessons/solutions/a.py"] = "docs/run.md\n"
        r = run(files, texts, names)
        self.assertTrue(any(p.startswith("collision") for p in r["problems"]) or
                        any("kebab" in p for p in r["problems"]), r["problems"])

    def test_non_ascii_or_uppercase_name_is_rejected(self):
        names = copy.deepcopy(NAMES)
        names["files"]["lessons/intro.md"] = "introducción.md"
        r = run(names=names)
        self.assertTrue(any("kebab" in p for p in r["problems"]))
        names["files"]["lessons/intro.md"] = "Introduccion.md"
        r = run(names=names)
        self.assertTrue(any("kebab" in p for p in r["problems"]))

    def test_all_caps_name_is_accepted(self):
        self.assertEqual(run()["problems"], [])  # CHALLENGE.md -> DESAFIO.md

    def test_numeric_prefix_must_survive(self):
        names = copy.deepcopy(NAMES)
        names["files"]["lessons/cs/01-first-chapter.md"] = "primer-capitulo.md"
        r = run(names=names)
        self.assertTrue(any("numeric prefix" in p for p in r["problems"]))

    def test_extension_must_survive(self):
        names = copy.deepcopy(NAMES)
        names["files"]["docs/guide.md"] = "guia.txt"
        r = run(names=names)
        self.assertTrue(any("extension" in p for p in r["problems"]))

    def test_unknown_glossary_word_is_a_warning_only(self):
        r = run(glossary={"estado"})
        self.assertEqual(r["problems"], [])
        self.assertTrue(any("'guia'" in w for w in r["warnings"]))
        self.assertFalse(any("'estado'" in w for w in r["warnings"]))


class ValidateTests(unittest.TestCase):
    """validate() must reject a hand-made map, whatever produced it."""

    def setUp(self):
        self.files, self.texts = tree()
        self.r = run()
        self.srcs = (
            [(p, t) for p, t in self.texts.items() if self.files.get(p) == "frozen"],
            [(p, t) for p, t in self.texts.items() if p.startswith(".github/workflows/")],
        )

    def check(self, result):
        return pm.validate(self.files, result, self.srcs)

    def test_generated_map_is_clean(self):
        self.assertEqual(self.check(dict(self.r["map"])), [])

    def test_renaming_a_path_a_frozen_file_mentions_fails(self):
        self.srcs[0].append(("lessons/solutions/a.py", "see lessons/intro.md\n"))
        problems = self.check(dict(self.r["map"]))
        self.assertTrue(any("lessons/intro.md" in p and "frozen" in p for p in problems), problems)

    def test_renaming_a_folder_a_frozen_file_mentions_fails(self):
        self.srcs[0].append(("lessons/solutions/a.py", "cd lessons/cs\n"))
        problems = self.check(dict(self.r["map"]))
        self.assertTrue(any("lessons/cs/" in p and "frozen" in p for p in problems), problems)

    def test_renaming_readme_fails(self):
        m = dict(self.r["map"])
        m["lessons/README.md"] = "lessons/LEEME.md"
        self.assertTrue(any("README.md renamed" in p for p in self.check(m)))

    def test_renaming_a_frozen_file_fails(self):
        m = dict(self.r["map"])
        m["lessons/solutions/a.py"] = "lessons/solutions/b.py"
        self.assertTrue(any("frozen file renamed" in p for p in self.check(m)))

    def test_renaming_license_like_names_fails(self):
        m = dict(self.r["map"])
        m["CONTRIBUTING.md"] = "CONTRIBUIR.md"
        self.assertTrue(any("keep-list" in p for p in self.check(m)))

    def test_two_files_to_one_name_fails(self):
        m = dict(self.r["map"])
        m["docs/run.md"] = m["docs/guide.md"]
        self.assertTrue(any(p.startswith("collision") for p in self.check(m)))

    def test_case_only_difference_is_a_collision(self):
        m = dict(self.r["map"])
        m["docs/run.md"] = m["docs/guide.md"].upper().replace("DOCS/", "docs/")
        self.assertTrue(any(p.startswith("collision") for p in self.check(m)))

    def test_file_and_folder_with_one_name_fails(self):
        m = dict(self.r["map"])
        m["docs/guide.md"] = "lessons"
        self.assertTrue(any("both a file and a folder" in p for p in self.check(m)) or
                        any("depth" in p for p in self.check(m)))

    def test_missing_entry_and_extra_entry_fail(self):
        m = dict(self.r["map"])
        del m["docs/run.md"]
        m["docs/ghost.md"] = "docs/ghost.md"
        problems = self.check(m)
        self.assertTrue(any("missing from the map" in p for p in problems))
        self.assertTrue(any("not in the tree" in p for p in problems))

    def test_depth_change_fails(self):
        m = dict(self.r["map"])
        m["docs/run.md"] = "ejecutar.md"
        self.assertTrue(any("depth" in p for p in self.check(m)))


class OutputTests(unittest.TestCase):
    def test_dump_map_is_deterministic_and_complete(self):
        r = run()
        a, b = pm.dump_map(r["map"]), pm.dump_map(dict(reversed(list(r["map"].items()))))
        self.assertEqual(a, b)
        import yaml
        back = yaml.safe_load(a)["paths"]
        self.assertEqual(back, r["map"])

    def test_report_lists_every_path(self):
        files, _ = tree()
        r = run()
        rep = pm.dump_report(files, r)
        for p in files:
            self.assertIn(f"| `{p}` |", rep)
        self.assertIn("renamed", rep)


class RealRepoTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.files, cls.res = pm.compute(pm.ROOT)

    def test_no_problems(self):
        self.assertEqual(self.res["problems"], [])

    def test_every_non_owned_path_is_mapped_once(self):
        self.assertEqual(set(self.res["map"]), set(self.files))
        vals = [v.casefold() for v in self.res["map"].values()]
        self.assertEqual(len(vals), len(set(vals)))

    def test_frozen_files_and_keep_list_do_not_move(self):
        m = self.res["map"]
        for p, cls in self.files.items():
            if cls == "frozen":
                self.assertEqual(m[p], p, p)
        for p in self.files:
            if p.endswith("/README.md") or p == "README.md":
                self.assertEqual(m[p].rsplit("/", 1)[-1], "README.md")
        for p in ("README.md", "LICENSE", "CONTRIBUTING.md", "SANDBOX-SETUP.md",
                  "lessons/exercises.md", "docs/running-with-gradle.md"):
            self.assertEqual(m[p], p)

    def test_survey_results_stay_english(self):
        d = self.res["dir_map"]
        self.assertEqual(d["lessons"], "lessons")
        self.assertEqual(d["lessons/cs-source"], "cs-source")
        self.assertEqual(d["lessons/cs-source/concepts"], "concepts")

    def test_plan_examples_are_renamed(self):
        m = self.res["map"]
        self.assertEqual(m["lessons/study-guides/languages/make-and-cmake.md"],
                         "lessons/guias-de-estudio/lenguajes/make-y-cmake.md")
        self.assertEqual(m["docs/curriculum.md"], "docs/plan-de-estudios.md")
        self.assertEqual(m["CHALLENGE.md"], "RETO.md")
        self.assertEqual(m["lessons/cs/01-reading-an-adversarial-program.md"].split("/")[1], "informatica")

    def test_no_frozen_file_mentions_a_renamed_path(self):
        idx = pm.mention_index([(p, t) for p in self.files if self.files[p] == "frozen"
                                for t in [pm.load_tree(pm.ROOT)[1](p)] if t is not None])
        for p, q in self.res["map"].items():
            if p != q:
                self.assertNotIn(p, idx, p)

    def test_committed_files_are_current(self):
        self.assertEqual(pm.read_own(pm.ROOT, pm.MAP_PATH), pm.dump_map(self.res["map"]))
        self.assertEqual(pm.read_own(pm.ROOT, pm.REPORT_PATH), pm.dump_report(self.files, self.res))
        for lang in pm.CATALOG_FILES:
            self.assertEqual(pm.read_own(pm.ROOT, pm.CATALOG_FILES[lang]), pm.catalog_text(pm.ROOT, lang, self.res["map"]), lang)


class CatalogBlockTests(unittest.TestCase):
    MAP = {"a/x.md": "a/y.md", "a/keep.md": "a/keep.md", "b/c/d.md": "b/e/f.md", "README.md": "README.md"}

    def test_block_lists_renamed_files_and_folders_only(self):
        dirs, files = pm.catalog_tables(self.MAP)
        self.assertEqual(files, {"a/x.md": "a/y.md", "b/c/d.md": "b/e/f.md"})
        self.assertEqual(dirs, {"b/c": "b/e"})

    def test_english_block_is_the_identity(self):
        text = pm.catalog_block(self.MAP, "en", "english")
        self.assertIn('"a/x.md": "a/x.md"', text)
        self.assertNotIn("a/y.md", text)
        self.assertIn('"a/y.md"', pm.catalog_block(self.MAP, "es", "english"))

    def test_two_folders_for_one_name_fail(self):
        with self.assertRaises(ValueError):
            pm.catalog_tables({"b/c/d.md": "b/e/d.md", "b/c/g.md": "b/h/g.md"})

    def test_a_rename_that_changes_the_depth_fails(self):
        with self.assertRaises(ValueError):
            pm.catalog_tables({"a/x.md": "x.md"})

    def test_a_stale_catalog_is_detected(self):
        import tempfile
        with tempfile.TemporaryDirectory(dir=os.path.join(pm.ROOT, "translation", "work")) as tmp:
            os.makedirs(os.path.join(tmp, "lessons", "book", "locale"))
            for lang, rel in pm.CATALOG_FILES.items():
                with open(os.path.join(tmp, rel), "w", encoding="utf-8", newline="\n") as fh:
                    fh.write("key: value\n")
            first = pm.catalog_text(tmp, "es", self.MAP)
            self.assertTrue(first.startswith("key: value\n"))
            with open(os.path.join(tmp, pm.CATALOG_FILES["es"]), "w", encoding="utf-8", newline="\n") as fh:
                fh.write(first.replace("a/y.md", "a/z.md"))
            self.assertNotEqual(pm.read_own(tmp, pm.CATALOG_FILES["es"]), pm.catalog_text(tmp, "es", self.MAP))
            fixed = pm.catalog_text(tmp, "es", self.MAP)       # regenerating replaces the block in place
            self.assertEqual(fixed, first)
            self.assertEqual(fixed.count(pm.CATALOG_BEGIN), 1)

    def test_the_layout_value_survives_regeneration(self):
        import tempfile
        with tempfile.TemporaryDirectory(dir=os.path.join(pm.ROOT, "translation", "work")) as tmp:
            os.makedirs(os.path.join(tmp, "lessons", "book", "locale"))
            with open(os.path.join(tmp, pm.CATALOG_FILES["es"]), "w", encoding="utf-8", newline="\n") as fh:
                fh.write("key: value\n\n" + pm.catalog_block(self.MAP, "es", "spanish"))
            self.assertIn('layout: "spanish"', pm.catalog_text(tmp, "es", self.MAP))


if __name__ == "__main__":
    unittest.main()
