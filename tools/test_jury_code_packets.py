#!/usr/bin/env python3
"""Tests for the Part II (code) side of tools/jury_packet.py and tools/jury_ingest.py (task S8-004).
Run: python3 -I tools/test_jury_code_packets.py

Covers: code units (chunks that differ only), the five Part II canary faults (each with a case where it must
decline), a code packet with the identifier-map slice, registry slice and oracle report, canaries on code units,
ingest of a code finding (exact quote, Part II categories, report section, review-fix task acceptance) and the
negative cases (unknown category, a quote of the original code the juror never saw).
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
import jury_ingest as ji  # noqa: E402
import jury_packet as jp  # noqa: E402
import test_jury_packet as tp  # noqa: E402

ENUMS = ji.load_enums()

EN_SH = """#!/bin/bash
# Check the card total.
set -eu
total=0
for h in 8 9 10; do
  total=$((total + h))
done
if [ "$total" -gt 40 ]; then
  echo "stop"
else
  echo "continue"
fi
exit 1
"""
ES_SH = EN_SH.replace("# Check the card total.", "# Comprueba el total de las tarjetas.")
EN_DOCKER = "# base image\nFROM python:3.12-slim\nCOPY . /app\n"
ES_DOCKER = EN_DOCKER.replace("# base image", "# imagen base")
EN_MD = "See [the rule](src/x/run.sh#L8-L11) for the check.\n"
IDMAP = [{"language": "shell", "entry": "x", "path": "src/x/run.sh", "old": "total", "new": "suma",
          "role": "variable", "scope": "file", "evidence": ["translation/part2/reports/x.md"], "approver": "t"}]


def code_unit(rel, en, es, idmap=None):
    units = jp.code_units_for_file(rel, en, es, None, idmap)
    assert units, rel
    return units[0]


class CodeUnitTests(unittest.TestCase):
    def test_only_chunks_that_differ_become_units(self):
        en = "\n".join("line %d" % i for i in range(150)) + "\n"
        es = en.replace("line 70", "linea 70")
        units = jp.code_units_for_file("src/x/a.sh", en, es, None, None)
        self.assertEqual(len(units), 1)
        self.assertEqual(units[0]["line"], 61)
        self.assertEqual(units[0]["kind"], "code")
        self.assertTrue(units[0]["id"].startswith("c-"))
        self.assertEqual(jp.tier_of(units[0]), "code")

    def test_identical_file_gives_no_units(self):
        self.assertEqual(jp.code_units_for_file("src/x/a.sh", EN_SH, EN_SH, None, None), [])

    def test_idmap_slice_is_limited_to_the_file(self):
        u = code_unit("src/x/run.sh", EN_SH, ES_SH, IDMAP)
        self.assertEqual(len(u["idmap"]), 1)
        other = code_unit("src/y/run.sh", EN_SH, ES_SH, IDMAP)
        self.assertEqual(other["idmap"], [])

    def test_ids_are_stable_and_distinct_per_file(self):
        self.assertEqual(jp.code_unit_id("a", 1), jp.code_unit_id("a", 1))
        self.assertNotEqual(jp.code_unit_id("a", 1), jp.code_unit_id("b", 1))


class MutatorTests(unittest.TestCase):
    def test_code_semantics_changes_the_threshold_on_a_code_line_not_a_comment(self):
        u = code_unit("src/x/run.sh", EN_SH, ES_SH)
        out, frag, cat, sev = jp.m_code_semantics(u, {})
        self.assertEqual((cat, sev), ("code-semantics", "critical"))
        self.assertNotEqual(out, u["spanish"])
        self.assertIn(frag, out)
        self.assertIn("# Comprueba el total", out)       # the comment line is intact

    def test_code_semantics_declines_on_comments_only(self):
        u = dict(code_unit("src/x/run.sh", EN_SH, ES_SH), spanish="# solo comentarios 40\n# otro 1\n")
        self.assertIsNone(jp.m_code_semantics(u, {}))

    def test_protected_token_translates_a_keyword(self):
        u = code_unit("src/x/run.sh", EN_SH, ES_SH)
        out, frag, cat, sev = jp.m_protected_token(u, {})
        self.assertEqual(cat, "protected-token")
        self.assertTrue(any(w in out for _, w in jp.PROTECTED_WORDS))

    def test_protected_token_declines_without_keywords(self):
        u = dict(code_unit("src/x/run.sh", EN_SH, ES_SH), spanish="x = y\n# if for\n")
        self.assertIsNone(jp.m_protected_token(u, {}))

    def test_identifier_stale_needs_a_ledger_row(self):
        es = ES_SH.replace("total", "suma").replace("Comprueba el suma", "Comprueba el total")
        u = code_unit("src/x/run.sh", EN_SH, es)
        self.assertIsNone(jp.m_identifier_stale(u, {"idmap": []}))
        out, frag, cat, sev = jp.m_identifier_stale(u, {"idmap": IDMAP})
        self.assertEqual((frag, cat), ("total", "identifier-stale"))
        self.assertNotEqual(out, u["spanish"])

    def test_identifier_stale_declines_for_another_file(self):
        u = code_unit("src/y/run.sh", EN_SH, ES_SH.replace("total", "suma"))
        self.assertIsNone(jp.m_identifier_stale(u, {"idmap": IDMAP}))

    def test_build_ci_only_on_build_files(self):
        sh = code_unit("src/x/check.sh", EN_SH, ES_SH)
        out, _, cat, _ = jp.m_build_ci(sh, {})
        self.assertEqual(cat, "build-ci")
        self.assertIn("exit 0", out.replace("set +e", "") if "exit 0" in out else out)
        py = dict(code_unit("src/x/a.py", "x = 1\n", "y = 1\n"))
        self.assertIsNone(jp.m_build_ci(py, {}))

    def test_build_ci_changes_the_image_tag(self):
        d = code_unit("src/x/Dockerfile", EN_DOCKER, ES_DOCKER)
        out, _, _, _ = jp.m_build_ci(d, {})
        self.assertIn("FROM python:latest", out)

    def test_link_anchor_moves_a_line_anchor_and_declines_without_one(self):
        u = tp.u(1, EN_MD, EN_MD)
        out, frag, cat, _ = jp.m_link_anchor(u, {})
        self.assertEqual((frag, cat), ("#L9", "link-semantic"))
        self.assertIn("#L9-L11", out)
        self.assertIsNone(jp.m_link_anchor(tp.u(2, "No link.", "Sin enlace."), {}))


class CodePacketTests(unittest.TestCase):
    def units(self):
        out = []
        for rel, en, es in (("src/x/run.sh", EN_SH, ES_SH), ("src/x/check.sh", EN_SH, ES_SH),
                            ("src/x/Dockerfile", EN_DOCKER, ES_DOCKER)):
            out += jp.code_units_for_file(rel, en, es, None, IDMAP)
        for u in out:
            u["oracle"] = "# S5-fam-x batch report\nVerdict: oracle PASS."
            u["registry"] = ["echo", "set"]
        return tp.make_units(40) + out

    def build(self, tmp, **kw):
        units = self.units()
        return units, jp.build(units, tp.CAT, tp.GL, tmp, rate=0.08, seed=3, target=800, minimum=500,
                               maximum=1200, idmap=IDMAP, **kw)

    def test_code_packet_has_side_by_side_text_and_the_three_slices(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest = self.build(tmp)
            codes = [p for p in manifest["packets"] if p["tier"] == "code"]
            self.assertTrue(codes)
            text = ""
            for p in codes:
                with open(os.path.join(tmp, "packets", p["name"] + ".md"), encoding="utf-8") as f:
                    text += f.read()
            self.assertIn("Identifier map (old -> new): `total` -> `suma`", text)
            self.assertIn("Registry slice (protected tokens): `echo`, `set`", text)
            self.assertIn("Oracle report (behavior check", text)
            self.assertIn("oracle PASS", text)
            self.assertIn("EN:\n~~~", text)
            self.assertEqual(jp.leaks(tmp), [])

    def test_a_family_without_an_oracle_report_says_so(self):
        u = dict(code_unit("src/x/run.sh", EN_SH, ES_SH), oracle="")
        self.assertIn("not proved equivalent", "\n".join(jp.part2_context(u)))

    def test_canaries_reach_code_units_with_part2_categories(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.build(tmp)
            key = ji.load_canaries(tmp)
            cats = {c["category"] for c in key if c["segment"].startswith("c-")}
            self.assertTrue(cats, key)
            self.assertTrue(cats <= set(jp.PART2_CATEGORIES), cats)
            for c in key:
                if c["segment"].startswith("c-"):
                    self.assertNotEqual(c["original_spanish"], c["mutated_spanish"])

    def test_prose_only_builds_are_unchanged_by_part2(self):
        with tempfile.TemporaryDirectory() as a, tempfile.TemporaryDirectory() as b:
            jp.build(tp.make_units(60), tp.CAT, tp.GL, a, rate=0.06, seed=2, target=800, minimum=500, maximum=1200)
            jp.build(tp.make_units(60), tp.CAT, tp.GL, b, rate=0.06, seed=2, target=800, minimum=500, maximum=1200,
                     idmap=IDMAP)
            with open(os.path.join(a, "canaries.key.json"), encoding="utf-8") as f1, \
                    open(os.path.join(b, "canaries.key.json"), encoding="utf-8") as f2:
                self.assertEqual(f1.read(), f2.read())


class CodeIngestTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        units = CodePacketTests().units()
        jp.build(units, tp.CAT, tp.GL, self.tmp.name, rate=0.08, seed=3, target=800, minimum=500, maximum=1200,
                 idmap=IDMAP)
        self.index = ji.load_units(self.tmp.name)
        self.canaries = ji.load_canaries(self.tmp.name)
        self.plain = next(u for u in self.index if u["segment"].startswith("c-") and not u["canary"])

    def tearDown(self):
        self.tmp.cleanup()

    def finding(self, **kw):
        u = self.plain
        f = {"id": "F001", "file": u["file"], "segment": u["segment"], "severity": "major",
             "category": "code-semantics", "english_excerpt": "-gt 40", "spanish_excerpt": "-gt 40",
             "problem": "The comparison changed.", "evidence": "EN and ES differ.", "proposed_fix": "Restore it.",
             "confidence": "high", "type": "defect"}
        f.update(kw)
        return f

    def ingest(self, f):
        return ji.ingest_reply(tp_reply([f]), self.index, self.canaries, ENUMS, "r.md")

    def test_a_code_finding_with_exact_quotes_is_kept(self):
        r = self.ingest(self.finding())
        self.assertEqual(len(r["kept"]) + len(r["canary_hits"]) + len(r["discarded"]), 1)
        self.assertEqual(len(r["discarded"]), 0, r["discarded"])

    def test_every_part2_category_is_accepted_by_the_schema(self):
        for cat in ji.PART2_CATEGORIES:
            self.assertEqual(ji.validate_finding(self.finding(category=cat), ENUMS), [], cat)

    def test_an_unknown_category_is_rejected(self):
        self.assertTrue(ji.validate_finding(self.finding(category="code-vibes"), ENUMS))

    def test_a_quote_that_is_not_in_the_shown_code_is_discarded(self):
        r = self.ingest(self.finding(spanish_excerpt="echo 'never shown'"))
        self.assertEqual(len(r["discarded"]), 1)
        self.assertIn("not an exact substring", r["discarded"][0][2])

    def test_report_has_a_part2_section_and_row_schema_accepts_c_ids(self):
        r = self.ingest(self.finding())
        merged = ji.merge_findings([r])
        text = ji.report_md([r], merged, "2026-01-01")
        self.assertIn("## Part II findings (code, %d)" % len(merged), text)
        rows = ji.to_schema_rows(merged)
        with open(os.path.join(ROOT, "translation", "schemas", "finding.schema.json"), encoding="utf-8") as f:
            pattern = json.load(f)["properties"]["segment_id"]["pattern"]
        import re
        for row in rows:
            self.assertTrue(re.match(pattern, row["segment_id"]), row["segment_id"])

    def test_a_code_review_fix_task_uses_the_part2_gates(self):
        with tempfile.TemporaryDirectory() as q:
            fp = os.path.join(q, "findings.jsonl")
            row = {"id": "F001", "segment_id": self.plain["segment"], "file": self.plain["file"],
                   "severity": "major", "category": "code-semantics", "problem": "bad", "status": "accepted"}
            prose = dict(row, id="F002", segment_id="s-%012x-0001" % 5, category="meaning", file="README.md")
            with open(fp, "w", encoding="utf-8") as f:
                f.write(json.dumps(row) + "\n" + json.dumps(prose) + "\n")
            new = ji.enqueue_review_fixes(fp, q)
            self.assertEqual(len(new), 2)
            with open(os.path.join(q, "review-fix.jsonl"), encoding="utf-8") as f:
                tasks = [json.loads(x) for x in f]
            self.assertIn("lock_code.py --verify", tasks[0]["accept"])
            self.assertIn("loc_apply.py", tasks[0]["notes"])
            self.assertEqual(tasks[1]["accept"], "python3 tools/verify.py --fast")
            self.assertNotIn("notes", tasks[1])


def tp_reply(findings):
    h = {"juror_model": "juror-a", "lens": "L1", "mode": "packet", "packets_or_files_reviewed": [],
         "date": "2026-01-01"}
    return "```json\n%s\n```\n\n```jsonl\n%s\n```\n" % (
        json.dumps(h), "\n".join(json.dumps(f, ensure_ascii=False) for f in findings))


if __name__ == "__main__":
    unittest.main()
