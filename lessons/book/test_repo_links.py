"""Tests for the one place that knows the repository's web address, and for how the book's link rewrite uses it."""
import os
import re
import unittest
import uuid
from pathlib import Path
from unittest.mock import patch

import build
import repo_links

BASE = "https://github.com/dullroar/learn-programming-the-weird-way"
BASE_ES = "https://github.com/dullroar/aprende-a-programar-como-un-bicho-raro"
LESSONS = Path(__file__).resolve().parents[1]
METADATA = {"book": LESSONS / "book" / "metadata.yaml", "study-guides": LESSONS / "study-guides" / "metadata.yaml",
            "curriculum": LESSONS / "curriculum" / "metadata.yaml"}

build.set_language("en")        # the English tests below must not depend on BOOK_LANG in the environment


class Resolver(unittest.TestCase):
    def test_canonical_default_needs_no_environment_and_no_git(self):
        self.assertEqual(repo_links.web_base({}), BASE)
        self.assertEqual(repo_links.blob_base({}), BASE + "/blob/master/")
        self.assertEqual(repo_links.tree_base({}), BASE + "/tree/master/")

    def test_a_fork_overrides_the_base_and_the_branch(self):
        env = {"REPOSITORY_WEB_BASE": "https://github.com/someone/their-fork/", "REPOSITORY_BRANCH": "release/2"}
        self.assertEqual(repo_links.file_url("src/apl/README.md", environ=env),
                         "https://github.com/someone/their-fork/blob/release/2/src/apl/README.md")
        self.assertEqual(repo_links.folder_url("src/apl", environ=env), "https://github.com/someone/their-fork/tree/release/2/src/apl")

    def test_an_empty_override_means_the_default(self):
        self.assertEqual(repo_links.web_base({"REPOSITORY_WEB_BASE": ""}), BASE)

    def test_a_bad_override_is_refused(self):
        for bad in ("http://github.com/a/b", "github.com/a/b", "https://github.com", "https://github.com/a/b c", "javascript:alert(1)"):
            with self.subTest(bad=bad), self.assertRaises(SystemExit):
                repo_links.web_base({"REPOSITORY_WEB_BASE": bad})
        with self.assertRaises(SystemExit):
            repo_links.branch({"REPOSITORY_BRANCH": "a b"})

    def test_paths_and_anchors_are_encoded(self):
        self.assertEqual(repo_links.file_url("lessons/My Code Challenge.pdf", environ={}), BASE + "/blob/master/lessons/My%20Code%20Challenge.pdf")
        self.assertEqual(repo_links.file_url("a/b.md", "run-it-1", environ={}), BASE + "/blob/master/a/b.md#run-it-1")
        self.assertEqual(repo_links.file_url("a/b.md", "a b?", environ={}), BASE + "/blob/master/a/b.md#a%20b%3F")
        self.assertEqual(repo_links.file_url("src/c#/x.md", environ={}), BASE + "/blob/master/src/c%23/x.md")

    def test_the_label_has_no_scheme_and_placeholders_are_filled(self):
        self.assertEqual(repo_links.label({}), "github.com/dullroar/learn-programming-the-weird-way")
        text = '<a href="{{REPOSITORY_WEB_URL}}">{{REPOSITORY_WEB_LABEL}}</a>'
        self.assertEqual(repo_links.fill_placeholders(text, {}), f'<a href="{BASE}">github.com/dullroar/learn-programming-the-weird-way</a>')


class LinkTarget(unittest.TestCase):
    """build.link_target for a link written in lessons/languages/x.md (so ../ reaches lessons/, ../../ the repository root)."""
    chapter = "languages/x.md"

    def resolve(self, target):
        return build.link_target(target, self.chapter, {}, {self.chapter: {}})

    def test_a_file_in_the_repository_becomes_a_blob_url(self):
        self.assertEqual(self.resolve("../../src/apl/README.md"), BASE + "/blob/master/src/apl/README.md")

    def test_a_folder_becomes_a_tree_url_and_ignores_the_anchor_rule(self):
        self.assertEqual(self.resolve("../../src/apl"), BASE + "/tree/master/src/apl")
        self.assertEqual(self.resolve("../../src/apl/"), BASE + "/tree/master/src/apl")

    def test_anchors_and_encoded_spaces_survive(self):
        self.assertEqual(self.resolve("../../README.md#the-list"), BASE + "/blob/master/README.md#the-list")
        self.assertEqual(self.resolve("../../src/a%20b/c.md"), BASE + "/blob/master/src/a%20b/c.md")

    def test_links_that_are_not_repository_paths_are_left_alone(self):
        for target in ("https://example.org/x", "mailto:a@b.c", "/absolute", "../../../outside.md", ""):
            with self.subTest(target=target):
                self.assertEqual(self.resolve(target), target)

    def test_the_old_repository_name_never_appears(self):
        self.assertNotRegex(self.resolve("../../src/apl/README.md"), r"code[-_]challenge")   # spelled as a pattern so this file does not contain the old name

    def test_an_override_reaches_every_published_link(self):
        with patch.dict(os.environ, {"REPOSITORY_WEB_BASE": "https://github.com/x/y"}):
            self.assertEqual(build.repo_links.file_url("a.md"), "https://github.com/x/y/blob/master/a.md")


def field(text, key):
    found = re.search(rf'^{key}:\s*"?([^"\n]+?)"?\s*$', text, re.M)
    return found.group(1) if found else None


def identity_problems(metadata, lang):
    """What is wrong with the three metadata texts ({"book": text, "study-guides": text, "curriculum": text}) for edition `lang`."""
    repo_links.set_language(lang)
    ident = repo_links.IDENTITY
    problems = []
    book_title = f"{ident['book_title']} v{field(metadata['book'], 'book-version')}"
    if field(metadata["book"], "title") != book_title:
        problems.append(f"book title is {field(metadata['book'], 'title')!r}, expected {book_title!r}")
    for kind, text in metadata.items():
        if field(text, "lang") != ident["language_tag"]:
            problems.append(f"{kind}: lang is {field(text, 'lang')!r}, expected {ident['language_tag']!r}")
        want = repo_links.publication_uuid(kind)
        if field(text, "identifier") != want:
            problems.append(f"{kind}: identifier is {field(text, 'identifier')!r}, expected {want}")
        if kind != "book" and field(text, "companion-to") != book_title:
            problems.append(f"{kind}: companion-to is {field(text, 'companion-to')!r}, expected {book_title!r}")
    return problems


class Identity(unittest.TestCase):
    """The edition's identity: stems, title, language tag, repository address and EPUB identifiers come from one catalog block."""
    def tearDown(self):
        build.set_language("en")

    def test_the_english_identity_is_what_it_was(self):
        self.assertEqual(repo_links.IDENTITY["language_tag"], "en-US")
        self.assertEqual((build.BOOK, build.TOC_TITLE, build.PDF_NAME), ("learn-programming-the-weird-way", "Contents", "learn-programming-the-weird-way.pdf"))
        self.assertEqual(repo_links.web_base({}), BASE)

    def test_the_spanish_identity(self):
        build.set_language("es")
        self.assertEqual(repo_links.web_base({}), BASE_ES)
        self.assertEqual(repo_links.blob_base({}), BASE_ES + "/blob/main/")
        self.assertEqual(repo_links.label({}), "github.com/dullroar/aprende-a-programar-como-un-bicho-raro")
        self.assertEqual((build.BOOK, build.BOOK_TITLE, build.TOC_TITLE),
                         ("aprende-a-programar-como-un-bicho-raro", "¡Aprende a programar como un bicho raro!", "Contenido"))
        self.assertEqual(build.GITHUB, BASE_ES + "/blob/main/")
        self.assertEqual(repo_links.IDENTITY["language_tag"], "es-419")
        self.assertEqual(repo_links.IDENTITY["study_guides_stem"], "aprende-a-programar-como-un-bicho-raro-guias-de-estudio")

    def test_a_published_link_in_spanish_points_at_the_spanish_repository(self):
        build.set_language("es")
        target = build.link_target("../../src/apl/README.md", "languages/x.md", {}, {"languages/x.md": {}})
        self.assertEqual(target, BASE_ES + "/blob/main/src/apl/README.md")
        self.assertNotIn("learn-programming-the-weird-way", target)

    def test_a_language_without_the_identity_block_changes_nothing(self):
        with patch.object(repo_links.catalog, "load", side_effect=repo_links.catalog.MissingKeyError("identity.repo_url")):
            with self.assertRaises(repo_links.catalog.MissingKeyError):
                repo_links.set_language("es")
        self.assertEqual(repo_links.web_base({}), BASE)

    def test_the_identifiers_are_stable_and_differ_by_publication_and_by_repository(self):
        repo_links.set_language("es")
        ids = {k: repo_links.publication_uuid(k) for k in ("book", "study-guides", "curriculum")}
        self.assertEqual(len(set(ids.values())), 3)
        self.assertEqual(ids["book"], "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, BASE_ES)))
        self.assertEqual(ids["study-guides"], "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, BASE_ES + "/study-guides")))
        self.assertNotEqual(ids["book"], repo_links.publication_uuid("book", BASE))
        with self.assertRaises(ValueError):
            repo_links.publication_uuid("pamphlet")

    def test_the_metadata_files_of_this_edition_agree_with_the_catalog(self):
        # This repository is the Spanish edition; the English edition's files would pass the same check with lang "en".
        metadata = {k: p.read_text(encoding="utf-8") for k, p in METADATA.items()}
        self.assertEqual(identity_problems(metadata, "es"), [])

    def test_the_metadata_check_can_fail(self):
        good = {k: p.read_text(encoding="utf-8") for k, p in METADATA.items()}
        self.assertEqual(identity_problems(good, "es"), [])
        self.assertTrue(identity_problems(good, "en"), "the Spanish files must not pass as the English edition")
        title_es, title_en = '"¡Aprende a programar como un bicho raro! v4"', '"Learn Programming the Weird Way! v4"'
        for kind, old, new, expect in [
                ("book", "lang: es-419", "lang: en-US", "lang is 'en-US'"),
                ("curriculum", "lang: es-419", "lang: es-ES", "lang is 'es-ES'"),
                ("study-guides", "urn:uuid:09033379", "urn:uuid:09033378", "study-guides: identifier"),
                ("book", "urn:uuid:44970ac2", "urn:uuid:1cb8694e", "book: identifier"),
                ("curriculum", "companion-to: " + title_es, 'companion-to: "¡Aprende a programar como un bicho raro! v3"', "companion-to"),
                ("book", "title: " + title_es, "title: " + title_en, "book title")]:
            with self.subTest(kind=kind, new=new):
                bad = dict(good, **{kind: good[kind].replace(old, new, 1)})
                self.assertNotEqual(bad[kind], good[kind], "the mutation did not apply")
                self.assertTrue(any(expect in p for p in identity_problems(bad, "es")), expect)

    def test_the_english_repository_address_is_nowhere_in_the_tooling_defaults(self):
        for name in ("build.py", "repo_links.py", "lint_pdf.py", "metadata.yaml"):
            self.assertNotIn("dullroar/learn-programming-the-weird-way", (LESSONS / "book" / name).read_text(encoding="utf-8"), name)

    def test_a_link_into_the_other_edition_is_foreign(self):
        # Plan 10.2 item 9: a Spanish PDF or EPUB whose links go to the English repository must fail the link check.
        english = f'<a href="{BASE}/blob/master/src/apl/README.md#run-it">x</a>'
        spanish = f'<a href="{BASE_ES}/blob/main/src/apl/README.md">x</a>'
        build.set_language("es")
        self.assertEqual(repo_links.foreign_repo_links(spanish), [])
        self.assertEqual(repo_links.foreign_repo_links(english), [f"{BASE}/blob/master/src/apl/README.md#run-it"])
        self.assertEqual(repo_links.foreign_repo_links(f'<a href="{BASE}">x</a><img src="{BASE}/raw/x.png">'), [BASE, f"{BASE}/raw/x.png"])
        build.set_language("en")
        self.assertEqual(repo_links.foreign_repo_links(english), [])
        self.assertEqual(repo_links.foreign_repo_links(spanish), [f"{BASE_ES}/blob/main/src/apl/README.md"])

    def test_a_longer_repository_name_is_not_foreign(self):
        build.set_language("es")
        self.assertEqual(repo_links.foreign_repo_links(f'<a href="{BASE}-extras/blob/main/x.md">x</a>'), [])
        self.assertEqual(repo_links.foreign_repo_links('<a href="#local">x</a><a href="https://example.com/">y</a>'), [])

    def test_the_build_check_reports_a_foreign_link_and_fails(self):
        import tempfile
        build.set_language("es")
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "book.html")
            for body, status in ((f'<a href="{BASE_ES}/blob/main/x.md">ok</a>', 0), (f'<a href="{BASE}/blob/master/x.md">english</a>', 1)):
                with open(path, "w", encoding="utf-8") as f:
                    f.write(body)
                with self.assertRaises(SystemExit) as caught:
                    with patch("builtins.print") as out:
                        build.check(path)
                self.assertEqual(caught.exception.code, status)
                if status:
                    self.assertTrue(any("FOREIGN repository link" in str(c) for c in out.call_args_list))

    def test_the_sandbox_image_tag_keeps_its_name(self):
        # `code-challenge-sandbox:local` is an internal image tag, not a stale repository reference (plan 5.4); test_repo_identity.py allows it on purpose.
        tagged = [p for p in (LESSONS.parent / "src").rglob("Dockerfile*") if "code-challenge-sandbox:local" in p.read_text(encoding="utf-8", errors="replace")]
        self.assertTrue(tagged, "no Dockerfile uses the sandbox image tag any more")


if __name__ == "__main__":
    unittest.main()
