#!/usr/bin/env python3
"""Tests for tools/lock_code.py. Run: python3 -I tools/test_lock_code.py
Each test builds a throwaway English clone and Spanish repo; the negative cases must fail."""
import contextlib
import io
import os
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import lock_code as lc  # noqa: E402

REAL_ROOT = os.path.dirname(HERE)

ENGLISH = {
    "LICENSE": "MIT License\nCopyright (c) English Author\n",
    "README.md": "# English prose\n",
    "src/forth/timecards.fs": ": total 40 > ;\n",
    "src/forth/README.md": "# Forth\n",
    "lessons/solutions/s1.txt": "solution\n",
    "lessons/cs/generated.md": "generated\n",
    "gradlew.bat": "@echo off\nexit /b 0\n",
    ".gitattributes": "*.bat text eol=crlf\n",
}
FROZEN = {"LICENSE", "src/forth/timecards.fs", "lessons/solutions/s1.txt", "gradlew.bat",
          ".gitattributes"}


def git(cwd, *args, check=True):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid",
                           "-c", "commit.gpgsign=false", "-C", cwd, *args],
                          capture_output=True, text=True, check=check)


def write(root, rel, text):
    full = os.path.join(root, rel)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)


def run(*argv):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        rc = lc.main(list(argv))
    return rc, out.getvalue(), err.getvalue()


class Env:
    """English clone + Spanish repo (a git repo whose files are the English tree)."""

    def __init__(self):
        self._tmp = tempfile.TemporaryDirectory()
        base = self._tmp.name
        self.eng = os.path.join(base, "english")
        self.es = os.path.join(base, "spanish")
        for d in (self.eng, self.es):
            os.makedirs(d)
            git(d, "init", "-q")
        for rel, text in ENGLISH.items():
            write(self.eng, rel, text)
        git(self.eng, "add", "-A")
        git(self.eng, "commit", "-q", "-m", "english")
        self.sha = git(self.eng, "rev-parse", "HEAD").stdout.strip()
        # Spanish repo: same files, plus its own loop/ and translation/ dirs
        for rel, text in ENGLISH.items():
            write(self.es, rel, text)
        write(self.es, "loop/CONFIG.yaml",
              f"english_clone_path: {self.eng}\nenglish_commit: {self.sha}\n")
        write(self.es, "translation/notes.md", "ours\n")
        git(self.es, "add", "-A")
        git(self.es, "commit", "-q", "-m", "import")

    def close(self):
        self._tmp.cleanup()

    def manifest(self):
        with open(os.path.join(self.es, lc.MANIFEST), encoding="utf-8") as fh:
            return lc.parse_manifest(fh.read())


class LockTests(unittest.TestCase):
    def setUp(self):
        self.e = Env()
        self.addCleanup(self.e.close)

    def test_write_lists_exactly_the_frozen_files(self):
        rc, out, _ = run("--write", "--root", self.e.es)
        self.assertEqual(rc, 0, out)
        self.assertEqual(set(self.e.manifest()), FROZEN)
        self.assertNotIn("README.md", self.e.manifest())
        self.assertNotIn("lessons/cs/generated.md", self.e.manifest())

    def test_verify_passes_on_clean_import(self):
        run("--write", "--root", self.e.es)
        rc, out, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 0, out)

    def test_one_byte_change_in_frozen_file_fails(self):
        run("--write", "--root", self.e.es)
        write(self.e.es, "src/forth/timecards.fs", ": total 40 >= ;\n")  # > becomes >=
        rc, out, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 1)
        self.assertIn("CHANGED  src/forth/timecards.fs", out)

    def test_single_byte_flip_even_same_length_fails(self):
        run("--write", "--root", self.e.es)
        write(self.e.es, "LICENSE", "MIT License\nCopyright (c) English Authoz\n")
        rc, out, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 1)
        self.assertIn("CHANGED  LICENSE", out)

    def test_deleted_frozen_file_fails(self):
        run("--write", "--root", self.e.es)
        os.remove(os.path.join(self.e.es, "lessons/solutions/s1.txt"))
        rc, out, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 1)
        self.assertIn("MISSING  lessons/solutions/s1.txt", out)

    def test_markdown_edit_is_not_a_violation(self):
        run("--write", "--root", self.e.es)
        write(self.e.es, "README.md", "# Prosa en español\n")
        rc, _, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 0)

    def test_tampered_manifest_fails_against_english_clone(self):
        run("--write", "--root", self.e.es)
        # lock in a damaged file: change the tree and the manifest together
        write(self.e.es, "src/forth/timecards.fs", "damaged\n")
        path = os.path.join(self.e.es, lc.MANIFEST)
        entries = self.e.manifest()
        entries["src/forth/timecards.fs"] = lc.sha256_bytes(b"damaged\n")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(lc.format_manifest(entries))
        rc, out, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 1)
        self.assertIn("MANIFEST-DIFFERS  src/forth/timecards.fs", out)

    def test_manifest_missing_a_frozen_file_fails(self):
        run("--write", "--root", self.e.es)
        path = os.path.join(self.e.es, lc.MANIFEST)
        entries = self.e.manifest()
        del entries["LICENSE"]
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(lc.format_manifest(entries))
        rc, out, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 1)
        self.assertIn("NOT-LOCKED  LICENSE", out)

    def test_unreachable_clone_fails_not_passes(self):
        run("--write", "--root", self.e.es)
        shutil.rmtree(self.e.eng)
        rc, out, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 1)
        self.assertIn("CLONE-UNREACHABLE", out)

    def test_missing_manifest_is_an_error(self):
        rc, _, err = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 2)
        self.assertIn("missing", err)

    def test_crlf_checkout_of_bat_file_is_accepted_but_other_changes_are_not(self):
        run("--write", "--root", self.e.es)
        # eol=crlf attribute: checkout writes CRLF, index stays LF (as in the real repo)
        os.remove(os.path.join(self.e.es, "gradlew.bat"))
        git(self.e.es, "checkout", "--", "gradlew.bat")
        with open(os.path.join(self.e.es, "gradlew.bat"), "rb") as fh:
            self.assertIn(b"\r\n", fh.read())
        rc, out, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 0, out)
        # a real edit on top of the CRLF checkout still fails
        write(self.e.es, "gradlew.bat", "@echo off\r\nexit /b 1\r\n")
        rc, out, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 1)
        self.assertIn("CHANGED  gradlew.bat", out)

    def test_crlf_checkout_is_accepted_in_a_linked_worktree(self):
        run("--write", "--root", self.e.es)
        git(self.e.es, "add", "-A")
        git(self.e.es, "commit", "-q", "-m", "lock")
        wt = os.path.join(self._tmp_dir(), "linked")
        git(self.e.es, "worktree", "add", "-q", "-b", "linked-test", wt)
        # in a linked worktree `.git` is a file, not a directory
        self.assertTrue(os.path.isfile(os.path.join(wt, ".git")))
        with open(os.path.join(wt, "gradlew.bat"), "rb") as fh:
            self.assertIn(b"\r\n", fh.read())
        rc, out, _ = run("--verify", "--root", wt)
        self.assertEqual(rc, 0, out)
        write(wt, "gradlew.bat", "@echo off\r\nexit /b 1\r\n")
        rc, out, _ = run("--verify", "--root", wt)
        self.assertEqual(rc, 1)
        self.assertIn("CHANGED  gradlew.bat", out)

    def _tmp_dir(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        return tmp.name

    def test_crlf_in_a_file_without_crlf_attribute_fails(self):
        run("--write", "--root", self.e.es)
        write(self.e.es, "src/forth/timecards.fs", ": total 40 > ;\r\n")
        rc, out, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 1)
        self.assertIn("CHANGED  src/forth/timecards.fs", out)

    def test_malformed_manifest_rejected(self):
        with self.assertRaises(lc.LockError):
            lc.parse_manifest("nothex  file\n")
        with self.assertRaises(lc.LockError):
            lc.parse_manifest(("a" * 64) + "  f\n" + ("b" * 64) + "  f\n")


class HookTests(unittest.TestCase):
    def setUp(self):
        self.e = Env()
        self.addCleanup(self.e.close)
        # the hook runs tools/lock_code.py of the repo it guards
        shutil.copytree(HERE, os.path.join(self.e.es, "tools"),
                        ignore=shutil.ignore_patterns("__pycache__", "test_*"))
        run("--write", "--root", self.e.es)
        rc, _, _ = run("--install-hook", "--root", self.e.es)
        self.assertEqual(rc, 0)
        git(self.e.es, "add", "-A")
        git(self.e.es, "commit", "-q", "-m", "tooling and manifest")

    def commit(self, msg="change"):
        return git(self.e.es, "commit", "-q", "-m", msg, check=False)

    def test_hook_rejects_changed_frozen_file(self):
        write(self.e.es, "src/forth/timecards.fs", ": total 40 >= ;\n")
        git(self.e.es, "add", "-A")
        r = self.commit()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("CHANGED  src/forth/timecards.fs", r.stderr)

    def test_hook_rejects_deleted_frozen_file(self):
        git(self.e.es, "rm", "-q", "LICENSE")
        r = self.commit()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("DELETED  LICENSE", r.stderr)

    def test_hook_rejects_rename_of_frozen_file(self):
        git(self.e.es, "mv", "lessons/solutions/s1.txt", "lessons/solutions/s2.txt")
        r = self.commit()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("DELETED  lessons/solutions/s1.txt", r.stderr)

    def test_hook_allows_markdown_and_owned_changes(self):
        write(self.e.es, "README.md", "# Prosa\n")
        write(self.e.es, "translation/notes.md", "nuestro\n")
        git(self.e.es, "add", "-A")
        r = self.commit()
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_hook_ignores_unstaged_frozen_edit(self):
        write(self.e.es, "src/forth/timecards.fs", "unstaged damage\n")
        write(self.e.es, "README.md", "# Prosa\n")
        git(self.e.es, "add", "README.md")
        r = self.commit()
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_install_refuses_to_overwrite_foreign_hook(self):
        hook = os.path.join(self.e.es, ".git", "hooks", "pre-commit")
        with open(hook, "w", encoding="utf-8") as fh:
            fh.write("#!/bin/sh\necho mine\n")
        rc, _, err = run("--install-hook", "--root", self.e.es)
        self.assertEqual(rc, 2)
        self.assertIn("not managed", err)
        with open(hook, encoding="utf-8") as fh:
            self.assertIn("echo mine", fh.read())

    def test_install_is_idempotent(self):
        rc, _, _ = run("--install-hook", "--root", self.e.es)
        self.assertEqual(rc, 0)


SCOPE_TEXT = (
    'version: 1\nfamilies:\n'
    '  "src/forth": {status: %s, files: 1}\n'
    '  "lessons/solutions": {status: frozen, files: 1}\n'
)
INVENTORY_TEXT = (
    '{"path": "src/forth/timecards.fs", "family": "src/forth"}\n'
    '{"path": "lessons/solutions/s1.txt", "family": "lessons/solutions"}\n'
)
LOCALIZED_FS = ": total 40 > ; \\ comentario\n"


class LocalizedTests(unittest.TestCase):
    """Second lock (S2-003): scope file, map entry, localized-code.sha256."""

    def setUp(self):
        self.e = Env()
        self.addCleanup(self.e.close)
        shutil.copytree(HERE, os.path.join(self.e.es, "tools"),
                        ignore=shutil.ignore_patterns("__pycache__", "test_*"))
        write(self.e.es, lc.INVENTORY, INVENTORY_TEXT)
        self.scope("frozen")
        run("--write", "--root", self.e.es)
        run("--install-hook", "--root", self.e.es)
        git(self.e.es, "add", "-A")
        git(self.e.es, "commit", "-q", "-m", "tooling")

    def scope(self, status):
        write(self.e.es, lc.SCOPE, SCOPE_TEXT % status)

    def entry(self):
        write(self.e.es, lc.IDMAP, '{"path": "src/forth/timecards.fs", "old": "a", "new": "b"}\n')

    def edit(self, record=True):
        write(self.e.es, "src/forth/timecards.fs", LOCALIZED_FS)
        if record:
            rc, out, _ = run("--write-localized", "--root", self.e.es)
            self.assertEqual(rc, 0, out)
        git(self.e.es, "add", "-A")
        return git(self.e.es, "commit", "-q", "-m", "loc", check=False)

    def test_unscoped_edit_is_rejected(self):          # negative: family still frozen
        self.entry()
        r = self.edit(record=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("CHANGED  src/forth/timecards.fs", r.stderr)

    def test_unmapped_edit_is_rejected(self):          # negative: localizing but no map or PO entry
        self.scope("localizing")
        r = self.edit()
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("UNMAPPED", r.stderr)

    def test_unrecorded_hash_is_rejected(self):        # negative: edit not in localized-code.sha256
        self.scope("localizing")
        self.entry()
        r = self.edit(record=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("UNRECORDED", r.stderr)

    def test_different_edit_than_recorded_is_rejected(self):
        self.scope("localizing")
        self.entry()
        write(self.e.es, "src/forth/timecards.fs", LOCALIZED_FS)
        run("--write-localized", "--root", self.e.es)
        write(self.e.es, "src/forth/timecards.fs", ": total 40 >= ;\n")
        git(self.e.es, "add", "-A")
        r = git(self.e.es, "commit", "-q", "-m", "x", check=False)
        self.assertNotEqual(r.returncode, 0)
        self.assertIn("UNRECORDED", r.stderr)

    def test_scoped_mapped_recorded_edit_commits_and_verifies(self):
        self.scope("localizing")
        self.entry()
        r = self.edit()
        self.assertEqual(r.returncode, 0, r.stderr)
        rc, out, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 0, out)

    def test_code_po_entry_counts_as_mapped(self):
        self.scope("localizing")
        write(self.e.es, lc.PO_CODE + "/src/forth/timecards.fs.po",
              'msgctxt "L1"\nmsgid "a"\nmsgstr "b"\n')
        r = self.edit()
        self.assertEqual(r.returncode, 0, r.stderr)

    def test_verify_fails_if_localized_file_drifts_after_record(self):
        self.scope("localizing")
        self.entry()
        self.edit()
        write(self.e.es, "src/forth/timecards.fs", "drift\n")
        rc, out, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 1)
        self.assertIn("CHANGED  src/forth/timecards.fs", out)

    def test_localized_manifest_entry_for_frozen_family_fails(self):
        self.entry()
        write(self.e.es, lc.LOCALIZED, "%s  lessons/solutions/s1.txt\n" % ("0" * 64))
        rc, out, _ = run("--verify", "--root", self.e.es)
        self.assertEqual(rc, 1)
        self.assertIn("LOCALIZED-UNSCOPED", out)

    def test_never_family_cannot_localize(self):
        write(self.e.es, lc.SCOPE,
              'families:\n  "src/forth": {status: localizing, files: 1, never: true}\n')
        self.assertEqual(lc.localizing_paths(self.e.es), set())

    def test_missing_scope_file_means_nothing_localizing(self):
        os.remove(os.path.join(self.e.es, lc.SCOPE))
        self.assertEqual(lc.localizing_paths(self.e.es), set())


class RealRepoTests(unittest.TestCase):
    def test_real_manifest_is_wellformed_and_covers_key_files(self):
        with open(os.path.join(REAL_ROOT, lc.MANIFEST), encoding="utf-8") as fh:
            entries = lc.parse_manifest(fh.read())
        self.assertIn("LICENSE", entries)
        self.assertIn("src/forth/timecards.fs", entries)
        self.assertFalse([p for p in entries if p.endswith(".md")], "Markdown must not be frozen")

    def test_real_repo_verify_passes(self):
        rc, out, _ = run("--verify", "--root", REAL_ROOT)
        self.assertEqual(rc, 0, out)


if __name__ == "__main__":
    unittest.main()
