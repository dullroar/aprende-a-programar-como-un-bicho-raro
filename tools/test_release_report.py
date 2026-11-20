#!/usr/bin/env python3
"""Tests for tools/release_report.py (task P2-019). Run: python3 -I tools/test_release_report.py

The report is generated from fixtures: a run record, ledger rows, finding rows, PO files built from a small
Markdown file, and a hash manifest in a temporary root. Negative cases: a failing command, a fuzzy or empty
segment, a missing PO, a tampered frozen file, a missing manifest, a missing reviewer model, an empty record,
a broken record file, a report with a section or the verdict removed.
"""
import copy
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
import apply as apply_mod  # noqa: E402
import inventory  # noqa: E402
import lock_code  # noqa: E402
import release_report as rr  # noqa: E402
import segment  # noqa: E402

MD = "# Titulo\n\nPrimer parrafo aqui.\n\nSegundo parrafo aqui.\n"
CFG = {"edition_label": "v4-es.0-rc1", "language_tag": "es-419", "english_commit": "a" * 40,
       "translator": "anthropic/claude-sonnet-5-5", "in_loop_reviewer": "anthropic/claude-opus-5-5",
       "cross_vendor_review": "false"}
SEG_ROW = {"ledger_version": 1, "kind": "segment", "edition": "v4-es.0-rc1", "ts": "2026-11-19T10:00:00Z",
           "segment_id": "s-0123456789ab-0001", "status": "accepted", "translator_model": "anthropic/claude-sonnet-5-5",
           "tokens": {"input": 100, "output": 20}}
DISP_ROW = {"ledger_version": 1, "kind": "disposition", "edition": "v4-es.0-rc1", "ts": "2026-11-19T10:00:00Z",
            "segment_id": "s-0123456789ab-0001", "adjudicator_model": "anthropic/claude-opus-5-5", "decision": "accepted"}
FIND_ROW = {"id": "F001", "segment_id": "s-0123456789ab-0001", "reviewer_model": "anthropic/claude-haiku-5-5, anthropic/claude-opus-5-5"}


def make_po(rel, po_root, states):
    """A PO file for MD with one entry per segment; states is a list of 'ok' | 'fuzzy' | 'empty'."""
    seg = segment.Segmentation(MD, rel)
    po = apply_mod.new_po(seg, rel)
    for e, s in zip(po, states):
        if s == "ok":
            e.msgstr = e.msgid + " (es)"
        elif s == "fuzzy":
            e.msgstr = e.msgid + " (es)"
            e.flags.append("fuzzy")
    path = apply_mod.po_path_for(rel, po_root)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    po.save(path)
    return len(po)


def good_data():
    return {"edition": "v4-es.0-rc1", "language": "es-419", "english_sha": "a" * 40, "date": "2026-11-19",
            "versions": {"python3": "Python 3.12.3", "pandoc": "NOT INSTALLED"},
            "commands": [{"name": "verify", "argv": ["python3", "tools/verify.py", "--release"], "exit": 0, "seconds": 12.5},
                         {"name": "build", "argv": ["python3", "x.py"], "exit": 0, "seconds": 3}],
            "lock": {"entries": 5, "manifest_sha256": "b" * 64, "problems": []},
            "coverage": {"files": {"README.md": {"accepted": 4, "fuzzy": 0, "untranslated": 0}}, "missing_po": []},
            "models": rr.models_from([SEG_ROW, DISP_ROW], [FIND_ROW], CFG),
            "ledger": rr.ledger_stats([SEG_ROW, DISP_ROW])}


class RenderTests(unittest.TestCase):
    def test_good_data_gives_ok_verdict_and_all_sections(self):
        text = rr.render(good_data())
        self.assertEqual(rr.check_report(text), [])
        self.assertIn(rr.VERDICT_OK, text)
        self.assertNotIn(rr.VERDICT_BAD, text)

    def test_report_carries_commands_versions_lock_coverage_models(self):
        text = rr.render(good_data())
        self.assertIn("`python3 tools/verify.py --release`", text)
        self.assertIn("| 1 | verify |", text)
        self.assertIn("2 of 2 commands exited 0.", text)
        self.assertIn("- python3: Python 3.12.3", text)
        self.assertIn("5 entries", text)
        self.assertIn("PASS (tree and English clone agree)", text)
        self.assertIn("accepted 4 (100.0%)", text)
        self.assertIn("translator: anthropic/claude-sonnet-5-5", text)
        self.assertIn("anthropic/claude-haiku-5-5 | reviewer x1", text.replace("anthropic/claude-haiku-5-5, anthropic/claude-opus-5-5", "anthropic/claude-haiku-5-5"))
        self.assertIn("tokens in 100, out 20", text)

    def test_failing_command_is_not_ready_and_named(self):
        d = good_data()
        d["commands"][1]["exit"] = 3
        text = rr.render(d)
        self.assertIn(rr.VERDICT_BAD, text)
        self.assertIn("command build exited 3", text)
        self.assertEqual(rr.check_report(text), [])

    def test_timeout_exit_is_not_ready(self):
        d = good_data()
        d["commands"][0]["exit"] = "timeout"
        self.assertTrue(rr.verdict_reasons(d))

    def test_empty_record_is_not_ready(self):
        d = good_data()
        d["commands"] = []
        self.assertTrue([w for w in rr.verdict_reasons(d) if "no command" in w])

    def test_lock_problem_blocks_and_is_listed(self):
        d = good_data()
        d["lock"]["problems"] = ["CHANGED  src/x.py"]
        text = rr.render(d)
        self.assertIn(rr.VERDICT_BAD, text)
        self.assertIn("FAIL (1 problem(s))", text)
        self.assertIn("hash manifest: CHANGED  src/x.py", text)

    def test_unchecked_or_empty_lock_blocks(self):
        d = good_data()
        d["lock"] = None
        self.assertTrue([w for w in rr.verdict_reasons(d) if "not checked" in w])
        d = good_data()
        d["lock"]["entries"] = 0
        self.assertTrue([w for w in rr.verdict_reasons(d) if "no entries" in w])

    def test_fuzzy_untranslated_and_missing_po_block(self):
        d = good_data()
        d["coverage"]["files"]["a.md"] = {"accepted": 1, "fuzzy": 2, "untranslated": 3}
        d["coverage"]["missing_po"] = ["b.md"]
        why = " ".join(rr.verdict_reasons(d))
        self.assertIn("2 fuzzy", why)
        self.assertIn("3 untranslated", why)
        self.assertIn("1 authored file(s) have no PO", why)
        text = rr.render(d)
        self.assertIn("`a.md`: 2 fuzzy, 3 untranslated of 6", text)
        self.assertIn("`b.md`: no PO", text)

    def test_empty_coverage_blocks(self):
        d = good_data()
        d["coverage"] = {"files": {}, "missing_po": []}
        self.assertTrue([w for w in rr.verdict_reasons(d) if "coverage is empty" in w])

    def test_missing_role_models_block(self):
        d = good_data()
        d["models"]["roles"]["in_loop_reviewer"] = ""
        self.assertTrue([w for w in rr.verdict_reasons(d) if "in_loop_reviewer" in w])
        d = good_data()
        d["models"]["roles"]["translator"] = ""
        self.assertTrue([w for w in rr.verdict_reasons(d) if "translator" in w])

    def test_pipe_in_command_does_not_break_table(self):
        d = good_data()
        d["commands"][0]["argv"] = ["sh", "-c", "a | b"]
        row = [l for l in rr.render(d).splitlines() if l.startswith("| 1 |")][0]
        self.assertIn("a \\| b", row)


class CheckReportTests(unittest.TestCase):
    def test_removed_section_fails(self):
        text = rr.render(good_data()).replace("## Coverage\n", "## Something\n")
        self.assertIn("missing section: Coverage", rr.check_report(text))

    def test_removed_verdict_fails(self):
        text = rr.render(good_data()).replace(rr.VERDICT_OK, "all fine")
        self.assertTrue([p for p in rr.check_report(text) if "verdict" in p])

    def test_two_verdicts_fail(self):
        text = rr.render(good_data()) + "\n" + rr.VERDICT_BAD + "\n"
        self.assertTrue([p for p in rr.check_report(text) if "verdict" in p])


class ModelTests(unittest.TestCase):
    def test_models_seen_by_role(self):
        m = rr.models_from([SEG_ROW, SEG_ROW, DISP_ROW], [FIND_ROW], CFG)
        self.assertEqual(m["seen"]["anthropic/claude-sonnet-5-5"], {"translator": 2})
        self.assertEqual(m["seen"]["anthropic/claude-opus-5-5"], {"adjudicator": 1})
        self.assertEqual(m["roles"]["in_loop_reviewer"], "anthropic/claude-opus-5-5")

    def test_finding_row_in_ledger_counts_reviewer(self):
        row = {"kind": "finding", "finding": {"reviewer_model": "m-x"}}
        self.assertEqual(rr.models_from([row], [], CFG)["seen"], {"m-x": {"reviewer": 1}})

    def test_ledger_stats(self):
        st = rr.ledger_stats([SEG_ROW, SEG_ROW, DISP_ROW, {"kind": "finding"}])
        self.assertEqual((st["segments"], st["dispositions"], st["findings"]), (2, 1, 1))
        self.assertEqual((st["input_tokens"], st["output_tokens"]), (200, 40))
        self.assertEqual(st["by_status"], {"accepted": 2})


class FileTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.dir = self.tmp.name

    def write(self, name, text):
        p = os.path.join(self.dir, name)
        os.makedirs(os.path.dirname(p), exist_ok=True)
        with open(p, "w", encoding="utf-8") as f:
            f.write(text)
        return p

    def test_coverage_counts_each_state_and_missing_po(self):
        po_root = os.path.join(self.dir, "po")
        n = make_po("a.md", po_root, ["ok", "fuzzy", "empty"])
        self.assertEqual(n, 3)
        make_po("c.md", po_root, ["ok", "ok", "ok"])
        cov = rr.coverage(po_root, ["a.md", "b.md", "c.md"])
        self.assertEqual(cov["files"]["a.md"], {"accepted": 1, "fuzzy": 1, "untranslated": 1})
        self.assertEqual(cov["files"]["c.md"], {"accepted": 3, "fuzzy": 0, "untranslated": 0})
        self.assertEqual(cov["missing_po"], ["b.md"])
        self.assertEqual(rr.totals(cov), {"accepted": 4, "fuzzy": 1, "untranslated": 1, "segments": 6})

    def test_complete_po_files_pass_the_verdict(self):
        po_root = os.path.join(self.dir, "po")
        make_po("a.md", po_root, ["ok", "ok", "ok"])
        d = good_data()
        d["coverage"] = rr.coverage(po_root, ["a.md"])
        self.assertEqual(rr.verdict_reasons(d), [])

    def test_record_reads_back_and_missing_file_is_empty(self):
        self.assertEqual(rr.read_record(os.path.join(self.dir, "none.json")), [])
        p = self.write("r.json", json.dumps([{"name": "x", "argv": ["a"], "exit": 0, "seconds": 1}]))
        self.assertEqual(rr.read_record(p)[0]["name"], "x")

    def test_broken_records_fail_closed(self):
        for body in ("not json", "{}", json.dumps([{"argv": "a", "exit": 0}]), json.dumps([{"argv": ["a"]}])):
            with self.assertRaises(rr.ReportError, msg=body):
                rr.read_record(self.write("bad.json", body))

    def test_broken_jsonl_fails_closed(self):
        with self.assertRaises(rr.ReportError):
            rr.read_jsonl(self.write("l.jsonl", '{"a": 1}\nnot json\n'))
        with self.assertRaises(rr.ReportError):
            rr.read_jsonl(self.write("m.jsonl", "[1]\n"))
        self.assertEqual(rr.read_jsonl(self.write("n.jsonl", '{"a": 1}\n\n{"b": 2}\n')), [{"a": 1}, {"b": 2}])

    def test_record_command_appends_rows_and_keeps_exit_code(self):
        out = os.path.join(self.dir, "run", "rec.json")
        self.assertEqual(rr.cmd_record(["--out", out, "--name", "ok", "--", sys.executable, "-c", "pass"]), 0)
        self.assertEqual(rr.cmd_record(["--out", out, "--name", "bad", "--", sys.executable, "-c", "raise SystemExit(3)"]), 1)
        rows = rr.read_record(out)
        self.assertEqual([(r["name"], r["exit"]) for r in rows], [("ok", 0), ("bad", 3)])

    def test_record_command_usage_errors(self):
        self.assertEqual(rr.cmd_record(["--out", "x"]), 2)
        self.assertEqual(rr.cmd_record(["--", "true"]), 2)

    def test_record_command_missing_program_is_failure(self):
        out = os.path.join(self.dir, "rec.json")
        self.assertEqual(rr.cmd_record(["--out", out, "--", "/nonexistent/prog"]), 1)
        self.assertEqual(rr.read_record(out)[0]["exit"], 127)

    def test_lock_result_passes_then_detects_tamper_and_missing_manifest(self):
        root = os.path.join(self.dir, "repo")
        os.makedirs(os.path.join(root, "src"))
        with open(os.path.join(root, "src", "a.py"), "wb") as f:
            f.write(b"print(1)\n")
        res = rr.lock_result(root)
        self.assertEqual(res["entries"], 0)
        self.assertTrue([p for p in res["problems"] if "missing" in p])
        os.makedirs(os.path.join(root, "translation"))
        with open(os.path.join(root, lock_code.MANIFEST), "w", encoding="utf-8") as f:
            f.write(lock_code.format_manifest({"src/a.py": lock_code.sha256_bytes(b"print(1)\n")}))
        res = rr.lock_result(root)
        self.assertEqual(res["entries"], 1)
        self.assertEqual(len(res["manifest_sha256"]), 64)
        self.assertFalse([p for p in res["problems"] if p.startswith(("CHANGED", "MISSING"))])
        with open(os.path.join(root, "src", "a.py"), "wb") as f:
            f.write(b"print(2)\n")
        res = rr.lock_result(root)
        self.assertTrue([p for p in res["problems"] if p.startswith("CHANGED")])

    def test_real_repo_collect_without_po_is_not_ready(self):
        data = rr.collect(ROOT, record=os.path.join(self.dir, "none.json"), ledgers=[], versions=False, lock=False)
        self.assertEqual(data["edition"], inventory.read_config(ROOT)["edition_label"])
        if not os.path.isdir(os.path.join(ROOT, "translation", "po")):
            self.assertTrue(data["coverage"]["missing_po"])
        self.assertTrue(rr.verdict_reasons(data))
        self.assertEqual(rr.check_report(rr.render(data)), [])

    def test_build_writes_report_and_exit_code_follows_verdict(self):
        out = os.path.join(self.dir, "report.md")
        rec = os.path.join(self.dir, "rec.json")
        self.assertEqual(rr.cmd_build(["--out", out, "--record", rec, "--ledger", self.write("l.jsonl", ""),
                                       "--no-versions", "--no-lock"]), 1)
        with open(out, encoding="utf-8") as f:
            self.assertEqual(rr.check_report(f.read()), [])
        self.assertEqual(rr.main(["x", "check", out]), 0)

    def test_build_with_broken_ledger_writes_nothing(self):
        out = os.path.join(self.dir, "report.md")
        bad = self.write("l.jsonl", "nope\n")
        self.assertEqual(rr.cmd_build(["--out", out, "--ledger", bad, "--no-versions", "--no-lock"]), 2)
        self.assertFalse(os.path.exists(out))

    def test_check_command_fails_on_broken_report(self):
        p = self.write("r.md", "# Release report\n")
        self.assertEqual(rr.main(["x", "check", p]), 1)

    def test_unknown_option_and_no_command_are_usage_errors(self):
        self.assertEqual(rr.cmd_build(["--bogus"]), 2)
        self.assertEqual(rr.main(["x"]), 2)
        self.assertEqual(rr.main(["x", "nope"]), 2)

    def test_tool_versions_marks_missing_program(self):
        v = rr.tool_versions((("nothing", ["definitely-not-installed-xyz", "--version"]),))
        self.assertEqual(v, {"nothing": "NOT INSTALLED"})


if __name__ == "__main__":
    unittest.main()
