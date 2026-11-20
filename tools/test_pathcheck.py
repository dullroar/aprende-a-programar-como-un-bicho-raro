#!/usr/bin/env python3
"""Tests for tools/pathcheck.py (P3B-006, invariants I17 to I20). Run: python3 -I tools/test_pathcheck.py
Negative cases: a link to an old English name, two files to one name, a renamed path a frozen file mentions,
README.md renamed, an English word kept in a renamed name; and the real checkout must be clean."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import negative  # noqa: E402
import pathcheck as pc  # noqa: E402


class LinkExtraction(unittest.TestCase):
    def dests(self, text):
        return [d for _, d in pc.link_destinations(text)]

    def test_inline_image_reference_and_html(self):
        text = ('See [a](docs/a.md) and ![img](img/x.png "title") and [b][r].\n\n[r]: other/b.md\n'
                '<a href="c/d.md">c</a>\n')
        self.assertEqual(self.dests(text), ["docs/a.md", "img/x.png", "other/b.md", "c/d.md"])

    def test_code_fences_and_code_spans_are_skipped(self):
        text = "`[x](no/such.md)`\n\n```md\n[y](no/such2.md)\n```\n\n~~~\n[z](no/such3.md)\n~~~\n[ok](real.md)\n"
        self.assertEqual(self.dests(text), ["real.md"])

    def test_not_local(self):
        for d in ("https://example.com/x", "mailto:a@b.c", "#anchor", "//cdn.x/y", "{{REPOSITORY_WEB_URL}}/x", ""):
            self.assertIsNone(pc.local_target(d), d)

    def test_fragment_query_and_escapes_are_dropped(self):
        self.assertEqual(pc.local_target("docs/a%20b.md#top"), "docs/a b.md")
        self.assertEqual(pc.local_target("a.md?x=1"), "a.md")


class I17(unittest.TestCase):
    def run_i17(self, docs, present, renamed=None):
        return pc.i17_problems(docs, lambda p: p in present, renamed)

    def test_resolving_links_are_clean(self):
        docs = {"lessons/a.md": ("[x](../docs/b.md#h) [y](c.md)", "lessons")}
        self.assertEqual(self.run_i17(docs, {"docs/b.md", "lessons/c.md"}), [])

    def test_missing_target_fails_with_the_id(self):
        docs = {"lessons/a.md": ("[x](c.md)", "lessons")}
        p = self.run_i17(docs, set())
        self.assertEqual(len(p), 1)
        self.assertTrue(p[0].startswith("I17 lessons/a.md:1"), p)

    def test_old_english_name_names_the_fix(self):
        docs = {"a.md": ("[x](docs/curriculum.md)", "")}
        p = self.run_i17(docs, {"docs/plan-de-estudios.md"}, {"docs/curriculum.md": "docs/plan-de-estudios.md"})
        self.assertTrue(p and "plan-de-estudios.md" in p[0], p)

    def test_link_out_of_the_repository_fails(self):
        p = self.run_i17({"a.md": ("[x](../../etc/passwd)", "")}, set())
        self.assertTrue(p and "leaves the repository" in p[0], p)

    def test_link_inside_code_is_not_checked(self):
        self.assertEqual(self.run_i17({"a.md": ("`[x](gone.md)`", "")}, set()), [])


class SyntheticTree(unittest.TestCase):
    def test_control_is_clean(self):
        self.assertEqual(negative.path_problems(), [])

    def test_every_path_fixture_fails_with_its_id(self):
        fixtures = [f for f in negative.catalog() if f.kind == "path"]
        self.assertEqual(sorted(f.expect for f in fixtures), ["I17", "I18", "I19", "I20", "I20"])
        for fx in fixtures:
            problems = fx.run()
            self.assertTrue(any(p.startswith(fx.expect + " ") for p in problems), (fx.id, problems))

    def test_kept_english_markdown_name_is_flagged(self):
        def mutate(t):
            t["names"]["files"].pop("docs/guide.md")
        problems = negative.path_problems(mutate)
        self.assertTrue(any(p.startswith("I18 ") for p in problems) or
                        any("NEEDS NAME" in p for p in problems), problems)

    def test_frozen_file_renamed_is_i19(self):
        problems = negative.path_problems(
            lambda t: t.update(map_edit=lambda m: m.update({"src/x/main.py": "src/x/principal.py"})))
        self.assertTrue(any(p.startswith("I19 ") for p in problems), problems)

    def test_collision_by_case_only_is_i20(self):
        problems = negative.path_problems(
            lambda t: t.update(map_edit=lambda m: m.update({"docs/guide.md": "reto.md"})))
        self.assertTrue(any(p.startswith("I20 ") and "collision" in p for p in problems), problems)

    def test_map_row_missing_is_i20(self):
        problems = negative.path_problems(lambda t: t.update(map_edit=lambda m: m.pop("docs/guide.md")))
        self.assertTrue(any(p.startswith("I20 ") and "missing from the map" in p for p in problems), problems)

    def test_banned_word_in_a_name_is_i18(self):
        def mutate(t):
            t["names"]["files"]["docs/guide.md"] = "tutorial.md"
            t["glossary"]["terms"][1]["banned"] = ["tutorial"]
        problems = negative.path_problems(mutate)
        self.assertTrue(any(p.startswith("I18 ") and "banned" in p for p in problems), problems)


class RealCheckout(unittest.TestCase):
    def test_checkout_is_clean(self):
        self.assertEqual(pc.run(pc.ROOT), [])

    def test_stale_committed_map_is_i20(self):
        import enpath
        real = enpath.read_map
        try:
            def edited(root=pc.ROOT):
                m = dict(real(root))
                m["CHALLENGE.md"] = "OTRO.md"
                return m
            enpath.read_map = edited
            problems = pc.run(pc.ROOT)
        finally:
            enpath.read_map = real
        self.assertTrue(any(p.startswith("I20 ") and "stale" in p for p in problems), problems[:3])


if __name__ == "__main__":
    unittest.main()
