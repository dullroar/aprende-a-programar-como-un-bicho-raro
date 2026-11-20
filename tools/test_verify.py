#!/usr/bin/env python3
"""Tests for tools/verify.py. Run: python3 -I tools/test_verify.py

The gate runner must be able to FAIL: every check below has a passing case and at least one failing case.
The long-running parts (the English repo gates, every tool test) are not started here."""
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lessons", "book", "locale"))
import apply as apply_mod  # noqa: E402
import invariants  # noqa: E402
import segment  # noqa: E402
import verify  # noqa: E402

EN = "# Hello\n\nThis is a book with `code` inside.\n"
ES = "# Hola\n\nEste es un libro con `code` dentro.\n"
CTX = invariants.load_context()


def make_po(en_text, rel, translations=None):
    """A PO for `en_text`; `translations` maps the position of a segment to its Spanish MASKED text."""
    seg = segment.Segmentation(en_text, rel)
    po = apply_mod.new_po(seg, rel)
    for i, e in enumerate(po):
        if translations and i in translations:
            e.msgstr = translations[i]
    return po


def spanish_po(rel="x.md"):
    seg = segment.Segmentation(EN, rel)
    masked = [s.masked for s in seg.segments()]
    es_masked = [verify_translate(m) for m in masked]
    po = make_po(EN, rel, dict(enumerate(es_masked)))
    return po


def verify_translate(masked):
    table = {"Hello": "Hola", "This is a book with": "Este es un libro con", "inside.": "dentro."}
    out = masked
    for k, v in table.items():
        out = out.replace(k, v)
    return out


def tmp_file(dirname, name, text):
    p = os.path.join(dirname, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(text)
    return p


class RoutingTests(unittest.TestCase):
    def test_porcelain_parses_modified_untracked_and_renames(self):
        raw = b" M tools/a.py\0?? translation/po/x.md.po\0R  new.md\0old.md\0A  b b.md\0"
        self.assertEqual(verify.parse_porcelain(raw), ["tools/a.py", "translation/po/x.md.po", "new.md", "b b.md"])

    def test_po_routes_to_its_markdown_file(self):
        self.assertEqual(verify.md_rel_of_po("translation/po/src/forth/README.md.po"), "src/forth/README.md")
        self.assertIsNone(verify.md_rel_of_po("translation/po/notes.txt"))
        self.assertIn(("file", "src/forth/README.md"), verify.route("translation/po/src/forth/README.md.po", ["owned"]))

    def test_authored_markdown_tooling_and_tools(self):
        self.assertEqual(verify.route("README.md", ["authored"]), [("file", "README.md")])
        self.assertEqual(verify.route("lessons/book/build.py", ["tooling"]), [("tooling", "lessons/book/build.py")])
        self.assertEqual(verify.route("tools/mask.py", ["owned"]), [("test", "tools/test_mask.py")])
        self.assertEqual(verify.route("tools/test_mask.py", ["owned"]), [("test", "tools/test_mask.py")])

    def test_checkers_for_owned_data(self):
        kinds = lambda p: [a[0] for a in verify.route(p, ["owned"])]  # noqa: E731
        self.assertEqual(kinds("translation/glossary.es.yaml"), ["cmd"])
        self.assertEqual(kinds("translation/prompts/translate.md"), ["cmd"])
        self.assertEqual(kinds("lessons/book/locale/es.yaml"), ["locale"])
        self.assertEqual(kinds("translation/humor-register.jsonl"), ["jsonl", "cmd"])
        self.assertEqual(kinds("loop/log.md"), [])

    def test_frozen_and_generated_files_get_no_action_beyond_the_lock(self):
        self.assertEqual(verify.route("src/forth/timecards.fs", ["frozen"]), [])
        self.assertEqual(verify.route("lessons/cs/forth.md", ["generated"]), [])

    def test_plan_deduplicates(self):
        acts = verify.plan_fast(["tools/mask.py", "tools/test_mask.py", "translation/po/x.md.po", "x.md"])
        self.assertEqual(acts.count(("test", "tools/test_mask.py")), 1)


class AllowlistTests(unittest.TestCase):
    def test_parse(self):
        self.assertEqual(verify.parse_allowlist("# c\n\na.py  # why\n  b.yaml\n"), {"a.py", "b.yaml"})

    def lookup(self, table):
        return lambda r: table.get(r)

    def test_identical_tooling_passes(self):
        t = {"a.py": b"x"}
        self.assertEqual(verify.check_tooling(["a.py"], self.lookup(t), self.lookup(t), set()), [])

    def test_changed_tooling_off_the_allowlist_fails(self):
        out = verify.check_tooling(["a.py"], self.lookup({"a.py": b"x"}), self.lookup({"a.py": b"y"}), set())
        self.assertEqual(len(out), 1)
        self.assertIn("a.py", out[0])

    def test_changed_tooling_on_the_allowlist_passes(self):
        out = verify.check_tooling(["a.py"], self.lookup({"a.py": b"x"}), self.lookup({"a.py": b"y"}), {"a.py"})
        self.assertEqual(out, [])

    def test_missing_and_new_tooling_fail(self):
        self.assertEqual(len(verify.check_tooling(["a.py"], self.lookup({"a.py": b"x"}), self.lookup({}), set())), 1)
        self.assertEqual(len(verify.check_tooling(["n.py"], self.lookup({}), self.lookup({"n.py": b"x"}), set())), 1)

    def test_stale_allowlist_row_fails(self):
        t = {"a.py": b"x"}
        out = verify.check_tooling(["a.py"], self.lookup(t), self.lookup(t), {"a.py"})
        self.assertEqual(len(out), 1)
        self.assertIn("allowlist", out[0])


class FileCheckTests(unittest.TestCase):
    def check(self, en, es, po, release=False, rel="x.md"):
        return verify.check_file(rel, en, es, po, CTX, release, None)

    def test_translated_file_with_its_po_passes(self):
        po = spanish_po()
        applied, _ = apply_mod.apply_text(EN, po, "x.md")
        self.assertEqual(applied, ES)
        self.assertEqual(self.check(EN, ES, po, release=True), [])

    def test_untranslated_file_without_po_passes_fast_fails_release(self):
        self.assertEqual(self.check(EN, EN, None), [])
        out = self.check(EN, EN, None, release=True)
        self.assertTrue(any("no PO file" in p for p in out))

    def test_hand_edited_file_without_po_fails(self):
        out = self.check(EN, ES, None)
        self.assertTrue(any("hand edit" in p for p in out))

    def test_partial_po_passes_fast_fails_release(self):
        po = make_po(EN, "x.md")                         # every msgstr empty
        self.assertEqual(self.check(EN, EN, po), [])
        out = self.check(EN, EN, po, release=True)
        self.assertTrue(any("untranslated" in p for p in out))

    def test_fuzzy_entry_is_release_only(self):
        po = spanish_po()
        po[0].flags.append("fuzzy")
        self.assertEqual([p for p in self.check(EN, None, po) if "fuzzy" in p], [])
        self.assertTrue(any("fuzzy" in p for p in self.check(EN, None, po, release=True)))

    def test_orphan_entry_fails_even_in_fast_mode(self):
        po = spanish_po()
        orphan = apply_mod.polib.POEntry(msgctxt="s-000000000000-99", msgid="Gone", msgstr="Ido")
        po.append(orphan)
        out = self.check(EN, None, po)
        self.assertTrue(any("orphan" in p for p in out), out)

    def test_stale_msgid_fails_in_fast_mode(self):
        po = spanish_po()
        po[0].msgid = "Something else"
        out = self.check(EN, None, po)
        self.assertTrue(any("stale" in p for p in out), out)

    def test_dropped_code_span_fails_i2(self):
        po = spanish_po()
        for e in po:
            e.msgstr = e.msgstr.replace("`code`", "código")
            e.msgstr = e.msgstr.replace(chr(0x27e6) + "CODE_0001" + chr(0x27e7), "")
        out = self.check(EN, None, po)
        self.assertTrue(any(p.startswith("I2") for p in out), out)

    def test_working_file_that_is_not_the_po_applied_fails(self):
        po = spanish_po()
        stale = ES.replace("libro", "tomo")
        out = self.check(EN, stale, po)
        self.assertTrue(any("not the PO applied" in p for p in out), out)

    def test_changed_inline_code_in_the_file_fails(self):
        po = make_po(EN, "x.md")
        bad = EN.replace("`code`", "`kode`")
        out = self.check(EN, bad, po)
        self.assertTrue(out)

    def test_missing_english_source_fails(self):
        out = self.check(None, ES, None)
        self.assertEqual(len(out), 1)
        self.assertIn("no English source", out[0])


class SmallCheckTests(unittest.TestCase):
    def test_jsonl_valid_and_invalid(self):
        with tempfile.TemporaryDirectory() as d:
            good = tmp_file(d, "good.jsonl", '{"a": 1}\n\n{"b": 2}\n')
            bad = tmp_file(d, "bad.jsonl", '{"a": 1}\n{"b": \n')
            self.assertEqual(verify.check_jsonl(good), [])
            out = verify.check_jsonl(bad)
            self.assertEqual(len(out), 1)
            self.assertIn(":2:", out[0])
            self.assertEqual(len(verify.check_jsonl(os.path.join(d, "missing.jsonl"))), 1)

    def test_counts_match_the_plan_and_a_wrong_expectation_fails(self):
        root = os.path.dirname(HERE)
        self.assertEqual(verify.check_counts(root), [])
        out = verify.check_counts(root, (("entry_readmes", 41),))
        self.assertEqual(len(out), 1)
        self.assertIn("entry_readmes", out[0])

    def test_dir_hashes_equal_and_different(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            tmp_file(a, "x/one.txt", "1")
            tmp_file(b, "x/one.txt", "1")
            self.assertEqual(verify.compare_dirs(a, b), [])
            tmp_file(b, "x/one.txt", "2")
            self.assertTrue(any("differs" in p for p in verify.compare_dirs(a, b)))
            tmp_file(b, "x/one.txt", "1")
            tmp_file(b, "extra.txt", "e")
            self.assertTrue(any("only in the second" in p for p in verify.compare_dirs(a, b)))

    def test_empty_build_directory_fails(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            self.assertEqual(len(verify.compare_dirs(a, b)), 1)

    def test_run_cmd_pass_fail_timeout_and_missing_program(self):
        py = sys.executable
        self.assertEqual(verify.run_cmd([py, "-c", "pass"])[0], [])
        out = verify.run_cmd([py, "-c", "import sys; print('boom'); sys.exit(3)"])[0]
        self.assertIn("exit 3", out[0])
        self.assertIn("boom", "\n".join(out))
        self.assertIn("timed out", verify.run_cmd([py, "-c", "import time; time.sleep(5)"], timeout=1)[0][0])
        self.assertIn("cannot run", verify.run_cmd(["definitely-not-a-program-xyz"])[0][0])

    def test_lock_fails_without_a_manifest_and_on_a_changed_file(self):
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(verify.check_lock(d))                       # no manifest
            tmp_file(d, "translation/locked-code.sha256", "0" * 64 + "  src/a.txt\n")
            self.assertTrue(any("MISSING" in p for p in verify.check_lock(d)))
            tmp_file(d, "src/a.txt", "changed")
            self.assertTrue(any("CHANGED" in p for p in verify.check_lock(d)))

    def test_lock_passes_on_this_repo(self):
        self.assertEqual(verify.check_lock(os.path.dirname(HERE)), [])

    def test_release_gate_commands_point_at_the_artifacts_dir(self):
        plain, rel = verify.release_gate_commands("OUT")
        self.assertEqual(len(rel), 3)
        self.assertTrue(all(argv[-1] == "OUT" and argv[-2] == "--artifacts-dir" for _, argv, _ in rel))
        self.assertFalse(any(n.startswith("release-") for n, _, _ in plain))
        self.assertGreaterEqual(len(plain), 10)


class ReportAndCliTests(unittest.TestCase):
    def run_report(self, results, label="release", incomplete=False):
        buf = io.StringIO()
        with redirect_stdout(buf):
            code = verify.report(results, label, incomplete)
        return code, buf.getvalue()

    def test_exit_codes(self):
        ok = verify.Result("a", [], 0.1)
        bad = verify.Result("b", ["I2 x: broke"], 0.1)
        self.assertEqual(self.run_report([ok])[0], 0)
        code, text = self.run_report([ok, bad])
        self.assertEqual(code, 1)
        self.assertIn("I2 x: broke", text)
        self.assertEqual(self.run_report([ok], incomplete=True)[0], 3)
        self.assertEqual(self.run_report([bad], incomplete=True)[0], 1)    # a failure beats incomplete

    def test_slow_fast_run_is_called_out(self):
        code, text = self.run_report([verify.Result("a", [], 61.0)], "fast")
        self.assertEqual(code, 0)
        self.assertIn("SLOW", text)

    def test_usage_errors_exit_2(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(verify.main(["verify.py"]), 2)
            self.assertEqual(verify.main(["verify.py", "--fast", "--release"]), 2)
            self.assertEqual(verify.main(["verify.py", "--bogus"]), 2)

    def test_fast_on_explicit_files_runs_end_to_end(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(verify.main(["verify.py", "--fast", "--files", "README.md"]), 0)
        self.assertIn("verify --fast: OK", buf.getvalue())


if __name__ == "__main__":
    unittest.main()
