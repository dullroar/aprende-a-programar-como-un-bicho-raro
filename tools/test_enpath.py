#!/usr/bin/env python3
"""Tests for tools/enpath.py and for every tool that keys on the English path (plan 5.6, P3B-004).
Run: python3 -I tools/test_enpath.py

The English path is the key (PO files, ledger, locked-code.sha256, anchors.json, the inventory); the working tree
holds the Spanish name once P3B-005 applies the rename. The scratch repositories here already hold the files at their
Spanish names (paths.layout "spanish"); each negative case must fail."""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
import anchors  # noqa: E402
import apply as ap  # noqa: E402
import enpath  # noqa: E402
import inventory  # noqa: E402
import lock_code as lc  # noqa: E402
import segment  # noqa: E402
import verify  # noqa: E402

WORK = os.path.join(ROOT, "translation", "work")
MAP = {
    "docs/curriculum.md": "docs/plan-de-estudios.md",
    "lessons/answers-key.md": "lessons/respuestas.md",
    "lessons/cs/01-x.md": "lessons/informatica/01-equis.md",
    "lessons/study-guides/languages/forth.md": "lessons/guias-de-estudio/lenguajes/forth.md",
    "README.md": "README.md",
    "src/forth/README.md": "src/forth/README.md",
}
CATALOG_SPANISH = 'identity:\n  title: "x"\npaths:\n  layout: "spanish"\n  dirs:\n'


def write(root, rel, text, mode="w"):
    full = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, mode, **({} if "b" in mode else {"encoding": "utf-8", "newline": ""})) as fh:
        fh.write(text)


def write_map(root, mapping, layout):
    body = "schema: 1\npaths:\n" + "".join('  "%s": "%s"\n' % kv for kv in sorted(mapping.items()))
    write(root, "translation/path-map.yaml", body)
    write(root, "lessons/book/locale/es.yaml", CATALOG_SPANISH.replace("spanish", layout))


@contextlib.contextmanager
def in_dir(path):
    """locate() takes a path that exists relative to the cwd as it is: run from the scratch root, not the real repo."""
    old = os.getcwd()
    os.chdir(path)
    try:
        yield
    finally:
        os.chdir(old)


def git(cwd, *args):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                           "-c", "commit.gpgsign=false", "-C", cwd, *args],
                          capture_output=True, text=True, check=True)


class Scratch:
    def __init__(self):
        os.makedirs(WORK, exist_ok=True)
        self.root = tempfile.mkdtemp(prefix="enpath-", dir=WORK)
        enpath._CACHE.clear()

    def close(self):
        shutil.rmtree(self.root, ignore_errors=True)
        enpath._CACHE.clear()


class Layer(unittest.TestCase):
    def setUp(self):
        self.en = enpath.PathLayer(MAP, "english")
        self.es = enpath.PathLayer(MAP, "spanish")

    def test_english_layout_is_identity_on_disk(self):
        self.assertEqual(self.en.work("docs/curriculum.md"), "docs/curriculum.md")
        self.assertEqual(self.en.spanish("docs/curriculum.md"), "docs/plan-de-estudios.md")

    def test_spanish_layout_works_at_the_spanish_name(self):
        self.assertEqual(self.es.work("docs/curriculum.md"), "docs/plan-de-estudios.md")
        self.assertEqual(self.es.work("lessons/cs/01-x.md"), "lessons/informatica/01-equis.md")

    def test_english_accepts_either_form(self):
        for layer in (self.en, self.es):
            self.assertEqual(layer.english("docs/plan-de-estudios.md"), "docs/curriculum.md")
            self.assertEqual(layer.english("docs/curriculum.md"), "docs/curriculum.md")
            self.assertEqual(layer.english("./docs/plan-de-estudios.md"), "docs/curriculum.md")

    def test_unmapped_path_is_identity(self):
        self.assertEqual(self.es.work("src/forth/timecards.fs"), "src/forth/timecards.fs")
        self.assertEqual(self.es.english("loop/STATE.md"), "loop/STATE.md")

    def test_kept_name_stays(self):
        self.assertEqual(self.es.work("README.md"), "README.md")

    def test_two_english_paths_to_one_name_is_an_error(self):
        with self.assertRaises(enpath.PathLayerError):
            enpath.PathLayer({"a.md": "z.md", "b.md": "z.md"})

    def test_bad_layout_is_an_error(self):
        with self.assertRaises(enpath.PathLayerError):
            enpath.PathLayer(MAP, "french")

    def test_full_joins_root(self):
        self.assertEqual(enpath.PathLayer(MAP, "spanish", "/r").full("lessons/answers-key.md"),
                         os.path.join("/r", "lessons", "respuestas.md"))


class Loading(unittest.TestCase):
    def setUp(self):
        self.s = Scratch()

    def tearDown(self):
        self.s.close()

    def test_no_map_is_identity(self):
        layer = enpath.load(self.s.root)
        self.assertEqual(layer.work("docs/curriculum.md"), "docs/curriculum.md")
        self.assertFalse(layer.moved)

    def test_layout_and_map_are_read_from_the_checkout(self):
        write_map(self.s.root, MAP, "spanish")
        layer = enpath.load(self.s.root)
        self.assertTrue(layer.moved)
        self.assertEqual(layer.work("docs/curriculum.md"), "docs/plan-de-estudios.md")

    def test_layout_override(self):
        write_map(self.s.root, MAP, "spanish")
        self.assertEqual(enpath.load(self.s.root, "english").work("docs/curriculum.md"), "docs/curriculum.md")

    def test_real_map_loads_and_layout_is_known(self):
        layer = enpath.load(ROOT)
        self.assertIn(layer.layout, enpath.LAYOUTS)
        self.assertGreater(len(layer.renamed()), 50)
        self.assertEqual(layer.english(layer.spanish("lessons/answers-key.md")), "lessons/answers-key.md")

    def test_locate_forms(self):
        write_map(self.s.root, MAP, "spanish")
        write(self.s.root, "docs/plan-de-estudios.md", "# x\n")
        layer = enpath.load(self.s.root)
        full = os.path.join(self.s.root, "docs", "plan-de-estudios.md")
        with in_dir(self.s.root):
            for arg in ("docs/curriculum.md", "docs/plan-de-estudios.md", full):
                en, got = enpath.locate(arg, self.s.root, layer)
                self.assertEqual((en, got), ("docs/curriculum.md", full), arg)

    def test_locate_outside_the_root_keeps_the_file(self):
        out = os.path.join(tempfile.gettempdir(), "enpath-outside.md")
        en, full = enpath.locate(out, self.s.root)
        self.assertEqual(full, out)
        self.assertTrue(en.endswith("enpath-outside.md"))


class ApplyIdentityAtSpanishPaths(unittest.TestCase):
    """plan acceptance: apply with identity targets reproduces every file at its Spanish path."""

    @classmethod
    def setUpClass(cls):
        cls.s = Scratch()
        real = enpath.load(ROOT)
        write_map(cls.s.root, real.en_to_es, "spanish")          # the REAL map, in the Spanish layout
        cls.keys = segment.authored_files(ROOT)
        for en in cls.keys:
            dest = os.path.join(cls.s.root, *real.spanish(en).split("/"))
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            shutil.copyfile(real.full(en), dest)
        enpath._CACHE.clear()
        cls.layer = enpath.load(cls.s.root)

    @classmethod
    def tearDownClass(cls):
        cls.s.close()

    def test_scratch_really_holds_the_spanish_names(self):
        renamed = [k for k in self.keys if self.layer.spanish(k) != k]
        self.assertGreater(len(renamed), 40)
        for k in renamed:
            self.assertTrue(os.path.isfile(os.path.join(self.s.root, *self.layer.spanish(k).split("/"))), k)
            self.assertFalse(os.path.exists(os.path.join(self.s.root, *k.split("/"))), k)

    def test_identity_on_every_authored_file(self):
        self.assertEqual(ap.identity_files(self.keys, self.s.root, self.layer), [])

    def test_identity_accepts_the_spanish_name_too(self):
        spanish = [self.layer.spanish(k) for k in self.keys[:30]]
        with in_dir(self.s.root):
            self.assertEqual(ap.identity_files(spanish, self.s.root, self.layer), [])

    def test_inventory_lists_english_keys(self):
        own = {"translation/path-map.yaml", "lessons/book/locale/es.yaml"}      # the scratch's own two files
        self.assertEqual(set(inventory.list_files(self.s.root)) - own, set(self.keys))

    def test_authored_files_are_the_same_keys(self):
        self.assertEqual(segment.authored_files(self.s.root), self.keys)

    def test_a_file_missing_at_its_spanish_path_is_an_error(self):
        en = "lessons/answers-key.md"
        os.rename(os.path.join(self.s.root, "lessons", "respuestas.md"), os.path.join(self.s.root, "lessons", "x.tmp"))
        try:
            with in_dir(self.s.root), self.assertRaises(FileNotFoundError):
                ap.identity_files([en], self.s.root, self.layer)
        finally:
            os.rename(os.path.join(self.s.root, "lessons", "x.tmp"), os.path.join(self.s.root, "lessons", "respuestas.md"))

    def test_the_english_layout_does_not_find_spanish_names(self):
        wrong = enpath.PathLayer(self.layer.en_to_es, "english", self.s.root)
        with in_dir(self.s.root), self.assertRaises(FileNotFoundError):
            ap.identity_files(["lessons/answers-key.md"], self.s.root, wrong)

    def test_build_inventory_counts_match_the_english_layout(self):
        got = inventory.build_inventory(self.s.root)["totals"]
        want = inventory.build_inventory(ROOT)["totals"]
        for k in ("md_authored", "words_authored", "segments", "headings_authored"):
            self.assertEqual(got[k], want[k], k)


class Verify(unittest.TestCase):
    def setUp(self):
        self.s = Scratch()
        write_map(self.s.root, MAP, "spanish")

    def tearDown(self):
        self.s.close()

    def test_touched_spanish_name_routes_by_the_english_key(self):
        acts = verify.plan_fast(["docs/plan-de-estudios.md"], self.s.root)
        self.assertIn(("file", "docs/curriculum.md"), acts)
        self.assertNotIn(("file", "docs/plan-de-estudios.md"), acts)

    def test_old_and_new_name_of_one_file_run_one_check(self):
        acts = verify.plan_fast(["docs/curriculum.md", "docs/plan-de-estudios.md"], self.s.root)
        self.assertEqual([a for a in acts if a[0] == "file"], [("file", "docs/curriculum.md")])

    def test_generated_page_is_not_a_file_check(self):
        acts = verify.plan_fast(["lessons/informatica/01-equis.md"], self.s.root)
        self.assertEqual([a for a in acts if a[0] == "file"], [])        # generated, class decided by the English key

    def test_file_problems_reads_the_spanish_path(self):
        env = verify.Env(self.s.root)
        write(self.s.root, "docs/plan-de-estudios.md", "# Hola\n")
        self.assertTrue(os.path.isfile(env.layer.full("docs/curriculum.md")))
        env.cfg, env._ctx, env._cat = {}, object(), object()             # no English clone: the check says so by key
        probs = env.file_problems("docs/curriculum.md", False)
        self.assertTrue(probs and probs[0].startswith("I1 docs/curriculum.md"), probs)

    def test_missing_spanish_file_with_po_is_reported_by_key(self):
        write(self.s.root, "translation/po/docs/curriculum.md.po", 'msgid ""\nmsgstr ""\n')
        env = verify.Env(self.s.root)
        env.cfg, env._ctx, env._cat = {}, object(), object()
        probs = env.file_problems("docs/curriculum.md", False)
        self.assertEqual(probs, ["I16 docs/curriculum.md: PO file exists but the Markdown file does not"])


class Anchors(unittest.TestCase):
    def setUp(self):
        self.s = Scratch()
        write_map(self.s.root, MAP, "spanish")
        self.layer = enpath.load(self.s.root)

    def tearDown(self):
        self.s.close()

    def test_link_in_a_spanish_folder_resolves_to_the_english_key(self):
        got = anchors.resolve("lessons/study-guides/languages/forth.md", "../../respuestas.md#x", self.layer)
        self.assertEqual(got, ("lessons/answers-key.md", "x"))

    def test_link_written_with_the_old_name_still_resolves_to_the_key(self):
        got = anchors.resolve("lessons/study-guides/languages/forth.md", "../../answers-key.md#x", self.layer)
        self.assertEqual(got, ("lessons/answers-key.md", "x"))

    def test_english_text_resolves_in_the_english_layout(self):
        got = anchors.resolve("lessons/study-guides/languages/forth.md", "../../answers-key.md#x", anchors.ENGLISH)
        self.assertEqual(got, ("lessons/answers-key.md", "x"))

    def test_the_english_folder_of_a_moved_file_is_wrong_in_spanish_text(self):
        # from the Spanish folder "../../x" climbs one level too few or many: the key is not found, not guessed
        got = anchors.resolve("lessons/study-guides/languages/forth.md", "../answers-key.md#x", self.layer)
        self.assertEqual(got, ("lessons/guias-de-estudio/answers-key.md", "x"))

    def test_check_links_follows_the_spanish_layout(self):
        doc = {"format": 1, "files": {"lessons/answers-key.md": {"headings": [{"es_id": "ok"}], "map": {"x": "ok"}}}}
        text = "[a](../../respuestas.md#ok) and [b](../../respuestas.md#nope)\n"
        probs = anchors.check_links("lessons/study-guides/languages/forth.md", text, doc, self.layer)
        self.assertEqual(len(probs), 1)
        self.assertIn("#nope", probs[0])

    def test_remap_follows_the_spanish_layout(self):
        doc = {"format": 1, "files": {"lessons/answers-key.md": {"headings": [], "map": {"x": "equis"}}}}
        out = anchors.remap_text("[a](../../respuestas.md#x)\n", "lessons/study-guides/languages/forth.md", doc,
                                 layer=self.layer)
        self.assertEqual(out, "[a](../../respuestas.md#equis)\n")

    def test_read_es_reads_the_spanish_path(self):
        # read_es uses the real checkout: its English key maps to a file that exists in whatever layout is current
        text = anchors.read_es("lessons/answers-key.md")
        self.assertTrue(text.strip())


class Lock(unittest.TestCase):
    """locked-code.sha256 stays keyed by English path and verifies the content at the mapped path."""

    FROZEN = {"src/forth/timecards.fs": ": total 40 > ;\n", "lessons/solutions/s1.txt": "solution\n"}
    RENAMED = {"lessons/solutions/s1.txt": "lessons/solutions/s1-es.txt"}

    def setUp(self):
        self.s = Scratch()
        root = self.s.root
        git(root, "init", "-q")
        entries = {}
        for rel, text in self.FROZEN.items():
            write(root, self.RENAMED.get(rel, rel), text)
            entries[rel] = lc.sha256_bytes(text.encode())
        write(root, lc.MANIFEST, lc.format_manifest(entries))
        write_map(root, self.RENAMED, "spanish")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "base")
        self.entries = lc.load_manifest(root)

    def tearDown(self):
        self.s.close()

    def test_clean_tree(self):
        self.assertEqual(lc.tree_problems(self.s.root, self.entries), [])

    def test_changed_content_at_the_mapped_path_is_named_by_the_key(self):
        write(self.s.root, "lessons/solutions/s1-es.txt", "solution!\n")
        self.assertEqual(lc.tree_problems(self.s.root, self.entries), ["CHANGED  lessons/solutions/s1.txt"])

    def test_file_left_at_the_english_name_is_missing(self):
        os.rename(os.path.join(self.s.root, "lessons", "solutions", "s1-es.txt"),
                  os.path.join(self.s.root, "lessons", "solutions", "s1.txt"))
        self.assertEqual(lc.tree_problems(self.s.root, self.entries), ["MISSING  lessons/solutions/s1.txt"])

    def test_unmoved_file_is_still_checked(self):
        write(self.s.root, "src/forth/timecards.fs", ": total 41 > ;\n")
        self.assertEqual(lc.tree_problems(self.s.root, self.entries), ["CHANGED  src/forth/timecards.fs"])

    def test_staged_change_to_the_mapped_file_is_rejected(self):
        write(self.s.root, "lessons/solutions/s1-es.txt", "tampered\n")
        git(self.s.root, "add", "-A")
        self.assertEqual(lc.staged_violations(self.s.root, self.entries), ["CHANGED  lessons/solutions/s1.txt"])

    def test_staged_delete_of_the_mapped_file_is_rejected(self):
        git(self.s.root, "rm", "-q", "lessons/solutions/s1-es.txt")
        self.assertEqual(lc.staged_violations(self.s.root, self.entries), ["DELETED  lessons/solutions/s1.txt"])

    def test_a_pure_rename_with_the_same_bytes_is_accepted(self):
        git(self.s.root, "mv", "lessons/solutions/s1-es.txt", "lessons/solutions/s1.txt")
        write_map(self.s.root, {}, "spanish")                       # the file went back to its English name
        enpath._CACHE.clear()
        self.assertEqual(lc.staged_violations(self.s.root, self.entries), [])

    def test_a_rename_with_changed_bytes_is_rejected(self):
        git(self.s.root, "mv", "lessons/solutions/s1-es.txt", "lessons/solutions/s1.txt")
        write(self.s.root, "lessons/solutions/s1.txt", "tampered\n")
        write_map(self.s.root, {}, "spanish")
        enpath._CACHE.clear()
        git(self.s.root, "add", "-A")
        self.assertEqual(lc.staged_violations(self.s.root, self.entries), ["CHANGED  lessons/solutions/s1.txt"])

    def test_the_real_manifest_still_verifies(self):
        self.assertEqual(lc.tree_problems(ROOT, lc.load_manifest(ROOT)), [])


class Tools(unittest.TestCase):
    def test_apply_rel_returns_the_english_key(self):
        self.assertEqual(ap.rel(os.path.join(ROOT, "docs", "curriculum.md")), "docs/curriculum.md")

    def test_translate_and_segment_agree_on_the_key(self):
        import translate
        self.assertIs(translate.enpath, enpath)
        self.assertEqual(enpath.locate("src/forth/README.md", ROOT)[0], "src/forth/README.md")

    def test_cli_prints_the_layout(self):
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(enpath.main(["enpath.py", "docs/plan-de-estudios.md"]), 0)
        self.assertIn("docs/curriculum.md ->", out.getvalue())


class RemapText(unittest.TestCase):
    """enpath.remap_text: the English text with every reference to a renamed path in the layout of the checkout (P3B-005)."""

    def layer(self, layout="spanish"):
        enpath._CACHE.clear()
        return enpath.PathLayer(MAP_REMAP, layout, ROOT, DIRS_REMAP)

    def remap(self, text, key, layout="spanish"):
        return enpath.remap_text(text, key, self.layer(layout))

    def test_a_link_from_a_moved_file_to_a_moved_file(self):
        got = self.remap("[g](../cs/01-x.md#a)", "lessons/languages/forth.md")
        self.assertEqual(got, "[g](../informatica/01-equis.md#a)")

    def test_a_link_from_a_kept_file_to_a_renamed_one(self):
        self.assertEqual(self.remap("[c](docs/curriculum.md)", "README.md"), "[c](docs/plan-de-estudios.md)")

    def test_a_link_to_a_kept_file_is_not_touched(self):
        text = "[r](../../src/forth/README.md#program-flow) and [x](https://example.org/lessons/cs/) and [h](#top)"
        self.assertEqual(self.remap(text, "lessons/study-guides/languages/forth.md"), text)

    def test_depth_changes_follow_the_move(self):
        # the guide moves from lessons/study-guides/languages/ to lessons/guias-de-estudio/lenguajes/ (same depth)
        got = self.remap("[i](../../intro.md#x)", "lessons/study-guides/languages/forth.md")
        self.assertEqual(got, "[i](../../introduccion.md#x)")

    def test_cs_source_bodies_are_written_for_the_generated_chapter_pages(self):
        got = self.remap("[g](../study-guides/concepts/a.md) [i](../intro.md)", "lessons/cs-source/chapters/01-x.md")
        self.assertEqual(got, "[g](../guias-de-estudio/conceptos/a.md) [i](../introduccion.md)")

    def test_lesson_front_matter_is_relative_to_lessons(self):
        got = self.remap('---\nlesson: "languages/apl.md#x"\n---\n', "src/apl/README.md")
        self.assertIn('lesson: "lenguajes/apl.md#x"', got)

    def test_full_repository_paths_in_prose_and_code_spans(self):
        got = self.remap("Run `python lessons/study-guides/build.py --check` and read CHALLENGE.md at docs/curriculum.md.", "CONTRIBUTING.md")
        self.assertEqual(got, "Run `python lessons/guias-de-estudio/build.py --check` and read RETO.md at docs/plan-de-estudios.md.")

    def test_a_longer_name_that_merely_starts_like_a_folder_is_not_touched(self):
        text = "see lessons/cs-source/chapters/ and lessons/cs.md"
        self.assertEqual(self.remap(text, "CONTRIBUTING.md"), text)

    def test_the_english_layout_is_the_identity(self):
        text = "[g](../cs/01-x.md) lessons/cs/ docs/curriculum.md"
        self.assertEqual(self.remap(text, "lessons/languages/forth.md", "english"), text)

    def test_a_wrong_remap_would_be_caught(self):
        # negative: the result is not the input, and a hand edit to a different name is not what the function produces
        got = self.remap("[c](docs/curriculum.md)", "README.md")
        self.assertNotEqual(got, "[c](docs/curriculum.md)")
        self.assertNotEqual(got, "[c](docs/plan.md)")


class SourceText(unittest.TestCase):
    def test_a_file_with_no_pinned_english_text_is_read_as_it_is(self):
        os.makedirs(WORK, exist_ok=True)
        with tempfile.TemporaryDirectory(dir=WORK) as d:
            path = os.path.join(d, "x.md")
            with open(path, "w", encoding="utf-8", newline="") as f:
                f.write("# Hello\n")
            self.assertEqual(ap.source_text(path, path), "# Hello\n")

    def test_an_untranslated_page_is_segmented_from_the_pinned_text_so_the_ids_match(self):
        key = "lessons/goals.md"
        en = enpath.english_source(key, ROOT)
        if en is None:
            self.skipTest("no English clone here")
        work = segment.read_raw(enpath.load(ROOT).full(key))
        ids = lambda t: [b.id for b in segment.Segmentation(t, key).segments()]
        self.assertEqual(ids(ap.source_text(key, enpath.load(ROOT).full(key))), ids(en))
        if enpath.load(ROOT).moved:
            self.assertNotEqual(ids(work), ids(en))      # why the pinned text is needed: the working file's ids differ


MAP_REMAP = {
    "CHALLENGE.md": "RETO.md",
    "docs/curriculum.md": "docs/plan-de-estudios.md",
    "lessons/intro.md": "lessons/introduccion.md",
    "lessons/cs/01-x.md": "lessons/informatica/01-equis.md",
    "lessons/study-guides/concepts/a.md": "lessons/guias-de-estudio/conceptos/a.md",
    "lessons/study-guides/build.py": "lessons/guias-de-estudio/build.py",
    "lessons/study-guides/languages/forth.md": "lessons/guias-de-estudio/lenguajes/forth.md",
    "lessons/languages/forth.md": "lessons/lenguajes/forth.md",
    "lessons/languages/apl.md": "lessons/lenguajes/apl.md",
    "README.md": "README.md",
}
DIRS_REMAP = {"lessons/cs": "lessons/informatica", "lessons/languages": "lessons/lenguajes",
              "lessons/study-guides": "lessons/guias-de-estudio",
              "lessons/study-guides/concepts": "lessons/guias-de-estudio/conceptos",
              "lessons/study-guides/languages": "lessons/guias-de-estudio/lenguajes"}


if __name__ == "__main__":
    unittest.main()
