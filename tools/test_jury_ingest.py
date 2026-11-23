#!/usr/bin/env python3
"""Tests for tools/jury_ingest.py (task P2-017). Run: python3 -I tools/test_jury_ingest.py

Covers: parsing a juror reply, field validation, the exact-quote rule (English, Spanish, the planted text a juror
actually saw, the original text a juror never saw), canary recall and juror weights, deduplication across
jurors, the written report and findings file, and the review-fix queue (including that the queue stays valid).
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
import next_task  # noqa: E402
import test_jury_packet as tp  # noqa: E402

ENUMS = ji.load_enums()


def finding(unit, **kw):
    f = {"id": "F001", "file": unit["file"], "segment": unit["segment"], "severity": "major", "category": "meaning",
         "english_excerpt": unit["english"][:20], "spanish_excerpt": unit["spanish"][:20],
         "problem": "The Spanish changes the meaning.", "learner_impact": "A learner predicts the wrong output.",
         "evidence": "Compare the two sentences.", "proposed_fix": "Restore the English meaning.",
         "confidence": "high", "type": "defect"}
    f.update(kw)
    return f


def reply(findings, header=None, extra=""):
    h = {"juror_model": "juror-a", "lens": "L1", "mode": "packet", "packets_or_files_reviewed": [],
         "date": "2026-01-01"}
    h.update(header or {})
    body = "\n".join(json.dumps(f, ensure_ascii=False) if isinstance(f, dict) else f for f in findings)
    return ("```json\n%s\n```\n\n```jsonl\n%s\n```\n\n## Coverage\n(table)\n%s\n" % (json.dumps(h), body, extra))


class Review:
    """A built review directory in a temporary folder."""

    def __init__(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.dir = self.tmp.name
        self.units = tp.make_units(60)
        self.manifest = jp.build(self.units, tp.CAT, tp.GL, self.dir, rate=0.08, seed=5, target=800,
                                 minimum=500, maximum=1200)
        self.index = ji.load_units(self.dir)
        self.canaries = ji.load_canaries(self.dir)

    def plain(self):
        keys = {(c["file"], c["segment"], ) for c in self.canaries}
        return [u for u in self.index if not u["canary"]]

    def canary_unit(self, canary):
        return next(u for u in self.index if u["canary"] == canary["canary_id"])

    def ingest(self, text, name="r.md"):
        return ji.ingest_reply(text, self.index, self.canaries, ENUMS, name)

    def close(self):
        self.tmp.cleanup()


class ParseTests(unittest.TestCase):
    def test_header_and_findings_are_found(self):
        h, rows, errs = ji.parse_reply(reply(['{"a": 1}', '{"b": 2}']))
        self.assertEqual(h["juror_model"], "juror-a")
        self.assertEqual([r[1] for r in rows], [{"a": 1}, {"b": 2}])
        self.assertEqual(errs, [])

    def test_a_missing_header_is_an_error_and_a_bad_line_is_reported(self):
        h, rows, errs = ji.parse_reply('```jsonl\n{"a": 1}\nnot json\n```\n')
        self.assertIsNone(h)
        self.assertTrue(errs)
        self.assertEqual([bool(r[2]) for r in rows], [False, True])

    def test_header_without_a_lens_is_an_error(self):
        _, _, errs = ji.parse_reply(reply([], header={"lens": ""}))
        self.assertTrue(any("lens" in e for e in errs))


class ValidationTests(unittest.TestCase):
    def setUp(self):
        self.r = Review()
        self.unit = self.r.plain()[0]

    def tearDown(self):
        self.r.close()

    def test_a_good_finding_with_exact_quotes_is_kept(self):
        res = self.r.ingest(reply([finding(self.unit)]))
        self.assertEqual(len(res["kept"]), 1)
        self.assertEqual(res["discarded"], [])

    def test_a_non_exact_quote_is_discarded(self):
        bad = {
            "paraphrase": finding(self.unit, spanish_excerpt="una frase que no está"),
            "ellipsis": finding(self.unit, english_excerpt=self.unit["english"][:5] + "..." + self.unit["english"][-4:]),
            "changed case": finding(self.unit, spanish_excerpt=self.unit["spanish"][:15].swapcase()),
            "english in the spanish field": finding(self.unit, spanish_excerpt=self.unit["english"][:20]),
        }
        for label, f in bad.items():
            res = self.r.ingest(reply([f]))
            self.assertEqual(res["kept"], [], label)
            self.assertEqual(len(res["discarded"]), 1, label)
            self.assertIn("exact substring", res["discarded"][0][2], label)

    def test_a_juror_quoting_the_original_of_a_planted_unit_is_discarded(self):
        c = self.r.canaries[0]
        unit = self.r.canary_unit(c)
        f = finding(unit, spanish_excerpt=c["original_spanish"], english_excerpt=None)
        self.assertNotEqual(c["original_spanish"], c["mutated_spanish"])
        res = self.r.ingest(reply([f]))
        self.assertEqual(res["kept"], [])
        self.assertIn("exact substring", res["discarded"][0][2])

    def test_shape_problems(self):
        u = self.unit
        cases = {
            "missing evidence": {k: v for k, v in finding(u).items() if k != "evidence"},
            "bad severity": finding(u, severity="blocker"),
            "bad category": finding(u, category="vibes"),
            "empty excerpt": finding(u, spanish_excerpt=""),
            "both null": finding(u, english_excerpt=None, spanish_excerpt=None),
            "too long": finding(u, english_excerpt="x" * 301),
            "unknown segment": finding(u, segment="s-000000000000-9999", english_excerpt=None,
                                       spanish_excerpt="zzz no existe"),
        }
        for label, f in cases.items():
            res = self.r.ingest(reply([f]))
            self.assertEqual(res["kept"], [], label)
            self.assertEqual(len(res["discarded"]), 1, label)

    def test_a_null_excerpt_is_fine_when_the_other_is_exact(self):
        res = self.r.ingest(reply([finding(self.unit, english_excerpt=None)]))
        self.assertEqual(len(res["kept"]), 1)

    def test_no_header_keeps_nothing(self):
        res = self.r.ingest('```jsonl\n%s\n```\n' % json.dumps(finding(self.unit)))
        self.assertEqual(res["kept"], [])
        self.assertTrue(res["errors"])

    def test_findings_outside_the_reviewed_packets_are_discarded(self):
        other = next(u for u in self.r.plain() if u["packet"] != self.unit["packet"])
        res = self.r.ingest(reply([finding(other)], header={"packets_or_files_reviewed": [self.unit["packet"] + ".md"]}))
        self.assertEqual(res["kept"], [])
        self.assertIn("not found in the packets reviewed", res["discarded"][0][2])


class CanaryScoreTests(unittest.TestCase):
    def setUp(self):
        self.r = Review()

    def tearDown(self):
        self.r.close()

    def catch_all(self, skip=()):
        rows = []
        for c in self.r.canaries:
            if c["canary_id"] in skip:
                continue
            u = self.r.canary_unit(c)
            rows.append(finding(u, category=c["category"], severity=c["severity"], english_excerpt=None,
                                spanish_excerpt=c["fragment"], id="F%03d" % (len(rows) + 1)))
        return rows

    def test_catching_every_canary_gives_full_recall_and_no_real_findings(self):
        res = self.r.ingest(reply(self.catch_all()))
        s = res["score"]
        self.assertEqual(s["seeded"], len(self.r.canaries))
        self.assertEqual(s["recall"], 1.0)
        self.assertEqual(s["weight"], 1.0)
        self.assertEqual(res["kept"], [])                         # planted faults are not real defects
        self.assertEqual(len(res["canary_hits"]), len(self.r.canaries))

    def test_an_empty_review_is_unreliable(self):
        res = self.r.ingest(reply([]))
        s = res["score"]
        self.assertEqual(s["recall"], 0.0)
        self.assertEqual(s["weight"], 0.25)
        self.assertEqual(sorted(s["missed"]), sorted(c["canary_id"] for c in self.r.canaries))

    def test_recall_is_computed_per_severity(self):
        crit = [c for c in self.r.canaries if c["severity"] == "critical"]
        self.assertTrue(crit)
        res = self.r.ingest(reply(self.catch_all(skip={c["canary_id"] for c in crit})))
        s = res["score"]
        self.assertEqual(s["by_severity"]["critical"], (0, len(crit)))
        self.assertLess(s["recall"], 1.0)

    def test_missing_a_critical_canary_costs_weight_even_at_high_recall(self):
        crit = [c for c in self.r.canaries if c["severity"] == "critical"][0]
        res = self.r.ingest(reply(self.catch_all(skip={crit["canary_id"]})))
        s = res["score"]
        if s["recall"] >= ji.RELIABLE_RECALL:
            self.assertLess(s["weight"], 1.0)
        self.assertIn(crit["canary_id"], s["missed"])

    def test_only_canaries_in_the_reviewed_packets_count(self):
        c = self.r.canaries[0]
        packet = self.r.canary_unit(c)["packet"]
        res = self.r.ingest(reply([], header={"packets_or_files_reviewed": [packet + ".md"]}))
        in_packet = [k for k in self.r.canaries if self.r.canary_unit(k)["packet"] == packet]
        self.assertEqual(res["score"]["seeded"], len(in_packet))

    def test_a_finding_on_a_canary_unit_about_something_else_stays_a_real_finding(self):
        c = self.r.canaries[0]
        u = self.r.canary_unit(c)
        other = "register" if c["category"] != "register" else "clarity"
        # quote the English only: it is not the planted fragment and the category differs
        f = finding(u, category=other, spanish_excerpt=None, english_excerpt=u["english"][:10])
        res = self.r.ingest(reply([f]))
        self.assertEqual(len(res["kept"]), 1)
        self.assertNotIn(c["canary_id"], res["score"]["caught_ids"])


class MergeTests(unittest.TestCase):
    def setUp(self):
        self.r = Review()
        self.u = self.r.plain()[0]

    def tearDown(self):
        self.r.close()

    def test_duplicates_across_jurors_merge_and_keep_the_highest_severity(self):
        a = self.r.ingest(reply([finding(self.u, severity="minor")], header={"juror_model": "juror-a"}), "a.md")
        b = self.r.ingest(reply([finding(self.u, severity="critical", spanish_excerpt=self.u["spanish"][:10])],
                                header={"juror_model": "juror-b", "lens": "L2"}), "b.md")
        merged = ji.merge_findings([a, b])
        self.assertEqual(len(merged), 1)
        self.assertEqual(merged[0]["severity"], "critical")
        self.assertEqual(sorted(r["juror"] for r in merged[0]["reporters"]), ["juror-a", "juror-b"])

    def test_different_categories_do_not_merge_and_order_is_by_severity(self):
        v = self.r.plain()[1]
        a = self.r.ingest(reply([finding(self.u, severity="minor", category="register"),
                                 finding(self.u, severity="critical", category="meaning"),
                                 finding(v, severity="major", category="omission")]))
        merged = ji.merge_findings([a])
        self.assertEqual([m["severity"] for m in merged], ["critical", "major", "minor"])


class RunTests(unittest.TestCase):
    def test_run_writes_the_report_and_schema_shaped_findings(self):
        r = Review()
        try:
            u = r.plain()[0]
            os.makedirs(os.path.join(r.dir, "inbox"))
            with open(os.path.join(r.dir, "inbox", "juror-a-L1-2026-01-01.md"), "w", encoding="utf-8") as f:
                f.write(reply([finding(u), finding(u, english_excerpt="not in the unit at all")]))
            results, merged, rows = ji.run(r.dir, "2026-02-02")
            self.assertEqual(len(rows), 1)
            with open(os.path.join(r.dir, "report-2026-02-02.md"), encoding="utf-8") as f:
                report = f.read()
            self.assertIn("Canary", report)
            self.assertIn("exact substring", report)                 # the discarded line says why
            self.assertIn("juror-a", report)
            with open(os.path.join(ROOT, "translation", "schemas", "finding.schema.json"), encoding="utf-8") as f:
                schema = json.load(f)
            with open(os.path.join(r.dir, "findings-2026-02-02.jsonl"), encoding="utf-8") as f:
                out = [json.loads(x) for x in f if x.strip()]
            self.assertEqual(len(out), 1)
            for row in out:
                self.assertTrue(set(schema["required"]) <= set(row), set(schema["required"]) - set(row))
                self.assertTrue(set(row) <= set(schema["properties"]), set(row) - set(schema["properties"]))
                self.assertEqual(row["status"], "open")
                for k in ("severity", "category", "confidence", "type", "status"):
                    self.assertIn(row[k], schema["properties"][k]["enum"])
        finally:
            r.close()


class QueueTests(unittest.TestCase):
    def rows(self, statuses):
        out = []
        for n, st in enumerate(statuses, 1):
            out.append({"id": "F%03d" % n, "segment_id": "s-0123456789ab-%04d" % n, "file": "README.md",
                        "severity": "major", "category": "meaning", "problem": "p%d" % n, "status": st})
        return out

    def test_a_code_packet_finding_is_kept_and_a_part2_category_is_valid(self):
        chk = "# Check.\nif [ \"$t\" -gt 40 ]; then echo stop; fi\n"
        en = chk + "# pad\n" * 70 + chk
        es = en.replace("# Check.", "# Revisa.")
        units = tp.make_units(40) + jp.code_units_for_file("src/x/check.sh", en, es, None, None)
        self.assertEqual(len([x for x in units if x["kind"] == "code"]), 2)
        with tempfile.TemporaryDirectory() as tmp:
            jp.build(units, tp.CAT, tp.GL, tmp, rate=0.05, seed=9, target=800, minimum=500, maximum=1200)
            index, canaries = ji.load_units(tmp), ji.load_canaries(tmp)
            u = next(x for x in index if x["segment"].startswith("c-") and not x["canary"])
            f = finding(u, category="build-ci", english_excerpt="-gt 40", spanish_excerpt="-gt 40")
            r = ji.ingest_reply(reply([f]), index, canaries, ENUMS, "r.md")
            self.assertEqual(r["discarded"], [])
            self.assertEqual(len(r["kept"]), 1)
            bad = finding(u, category="build-ci", spanish_excerpt="# Check.")   # the original, never shown
            r2 = ji.ingest_reply(reply([bad]), index, canaries, ENUMS, "r.md")
            self.assertEqual(len(r2["discarded"]), 1)

    def test_only_accepted_findings_become_tasks_and_done_is_removed(self):
        with tempfile.TemporaryDirectory() as tmp:
            findings = os.path.join(tmp, "findings-2026-02-02.jsonl")
            with open(findings, "w", encoding="utf-8") as f:
                for r in self.rows(["accepted", "rejected", "duplicate", "accepted", "needs-human", "open"]):
                    f.write(json.dumps(r) + "\n")
            queue = os.path.join(tmp, "queue", "generated")
            done = os.path.join(tmp, "DONE")
            with open(done, "w") as f:
                f.write("DONE\n")
            new = ji.enqueue_review_fixes(findings, queue, done)
            self.assertEqual(new, ["RF-001", "RF-002"])
            self.assertFalse(os.path.exists(done))
            with open(os.path.join(queue, "review-fix.jsonl"), encoding="utf-8") as f:
                tasks = [json.loads(x) for x in f if x.strip()]
            self.assertEqual([t["kind"] for t in tasks], ["review-fix", "review-fix"])
            self.assertEqual([t["status"] for t in tasks], ["todo", "todo"])
            tasks_loaded, problems = next_task.load_queue(os.path.join(tmp, "queue"))
            self.assertEqual(problems, [])
            self.assertEqual(len(tasks_loaded), 2)

    def test_enqueue_is_idempotent_and_leaves_done_when_nothing_is_new(self):
        with tempfile.TemporaryDirectory() as tmp:
            findings = os.path.join(tmp, "findings-x.jsonl")
            with open(findings, "w", encoding="utf-8") as f:
                f.write(json.dumps(self.rows(["accepted"])[0]) + "\n")
            queue = os.path.join(tmp, "q")
            done = os.path.join(tmp, "DONE")
            self.assertEqual(ji.enqueue_review_fixes(findings, queue, done), ["RF-001"])
            with open(done, "w") as f:
                f.write("DONE\n")
            self.assertEqual(ji.enqueue_review_fixes(findings, queue, done), [])
            self.assertTrue(os.path.exists(done))                      # nothing new: the loop stays finished

    def test_nothing_accepted_changes_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            findings = os.path.join(tmp, "findings-x.jsonl")
            with open(findings, "w", encoding="utf-8") as f:
                for r in self.rows(["rejected", "open"]):
                    f.write(json.dumps(r) + "\n")
            done = os.path.join(tmp, "DONE")
            with open(done, "w") as f:
                f.write("DONE\n")
            self.assertEqual(ji.enqueue_review_fixes(findings, os.path.join(tmp, "q"), done), [])
            self.assertTrue(os.path.exists(done))


if __name__ == "__main__":
    unittest.main()
