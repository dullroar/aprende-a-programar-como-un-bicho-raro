#!/usr/bin/env python3
"""Tests for tools/prompt_check.py. Run: python3 -I tools/test_prompt_check.py"""
import copy
import json
import os
import shutil
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import prompt_check as pc  # noqa: E402

REPO = os.path.dirname(HERE)
SCRATCH = os.path.join(REPO, "translation", "work", "test_prompt_check")


def sample(key, n=0):
    with open(os.path.join(REPO, pc.SAMPLES, key + ".jsonl"), encoding="utf-8") as f:
        return json.loads([l for l in f if l.strip()][n])


def make_root():
    """Copy prompts and schemas into a scratch root so tests can break them."""
    shutil.rmtree(SCRATCH, ignore_errors=True)
    os.makedirs(os.path.join(SCRATCH, "translation"))
    shutil.copytree(os.path.join(REPO, pc.PROMPTS), os.path.join(SCRATCH, pc.PROMPTS))
    shutil.copytree(os.path.join(REPO, pc.SCHEMAS), os.path.join(SCRATCH, pc.SCHEMAS))
    return SCRATCH


def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def write(path, text):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


class RealRepo(unittest.TestCase):
    def test_prompts_ok(self):
        self.assertEqual(pc.check_prompts(REPO), [])

    def test_samples_ok(self):
        self.assertEqual(pc.check_samples(REPO), [])

    def test_four_prompts_exist(self):
        for name in ("translate", "review", "backtranslate", "adjudicate"):
            self.assertTrue(os.path.isfile(os.path.join(REPO, pc.PROMPTS, name + ".md")))

    def test_hash_is_stable_and_changes(self):
        p = os.path.join(REPO, pc.PROMPTS, "translate.md")
        self.assertEqual(pc.prompt_sha256(p), pc.prompt_sha256(p))
        self.assertEqual(len(pc.prompt_sha256(p)), 64)


class SchemaNegatives(unittest.TestCase):
    def bad(self, key, ref, mutate):
        obj = copy.deepcopy(sample(key))
        mutate(obj)
        errs = pc.validate(ref, obj, REPO)
        self.assertTrue(errs, "mutated row should fail")

    def test_segment_id_format(self):
        self.bad("translator_output", pc.SAMPLE_TARGETS["translator_output"],
                 lambda o: o.update(segment_id="seg-1"))

    def test_placeholder_format(self):
        self.bad("translator_output", pc.SAMPLE_TARGETS["translator_output"],
                 lambda o: o.update(placeholders_seen=["CODE_0001"]))

    def test_missing_required(self):
        self.bad("translator_output", pc.SAMPLE_TARGETS["translator_output"],
                 lambda o: o.pop("placeholders_seen"))

    def test_extra_field_rejected(self):
        self.bad("translator_output", pc.SAMPLE_TARGETS["translator_output"],
                 lambda o: o.update(rationale="because"))

    def test_finding_bad_severity_and_category(self):
        self.bad("finding", "finding.schema.json", lambda o: o.update(severity="blocker"))
        self.bad("finding", "finding.schema.json", lambda o: o.update(category="negation"))

    def test_finding_without_any_excerpt_rejected(self):
        self.bad("finding", "finding.schema.json",
                 lambda o: o.update(english_excerpt=None, spanish_excerpt=None))

    def test_finding_excerpt_length(self):
        self.bad("finding", "finding.schema.json", lambda o: o.update(spanish_excerpt="x" * 301))

    def test_adjudication_accepted_needs_correction(self):
        self.bad("adjudication", pc.SAMPLE_TARGETS["adjudication"],
                 lambda o: o.update(corrected_spanish=None))

    def test_adjudication_duplicate_needs_target(self):
        obj = sample("adjudication", 1)
        obj["duplicate_of"] = None
        self.assertTrue(pc.validate(pc.SAMPLE_TARGETS["adjudication"], obj, REPO))

    def test_adjudication_needs_human_must_escalate(self):
        obj = sample("adjudication", 2)
        obj["escalate"] = False
        self.assertTrue(pc.validate(pc.SAMPLE_TARGETS["adjudication"], obj, REPO))

    def test_adjudication_unknown_decision(self):
        self.bad("adjudication", pc.SAMPLE_TARGETS["adjudication"],
                 lambda o: o.update(decision="majority-agrees"))

    def test_backtranslation_stage_const(self):
        self.bad("backtranslation_blind", pc.SAMPLE_TARGETS["backtranslation_blind"],
                 lambda o: o.update(stage=2))

    def test_ledger_round_cap(self):
        self.bad("ledger-row", "ledger-row.schema.json", lambda o: o.update(round=3))

    def test_ledger_bad_hash(self):
        self.bad("ledger-row", "ledger-row.schema.json", lambda o: o.update(spanish_sha256="abc"))

    def test_ledger_unknown_field_rejected(self):
        self.bad("ledger-row", "ledger-row.schema.json", lambda o: o.update(surprise=1))

    def test_ledger_finding_row_embeds_checked_finding(self):
        obj = sample("ledger-row", 1)
        obj["finding"]["severity"] = "blocker"
        self.assertTrue(pc.validate("ledger-row.schema.json", obj, REPO))

    def test_ledger_disposition_missing_applied(self):
        obj = sample("ledger-row", 2)
        del obj["applied"]
        self.assertTrue(pc.validate("ledger-row.schema.json", obj, REPO))

    def test_valid_rows_have_no_errors(self):
        for key, ref in pc.SAMPLE_TARGETS.items():
            self.assertEqual(pc.validate(ref, sample(key), REPO), [], key)


class Excerpts(unittest.TestCase):
    EN = "Stop when the total is strictly greater than 40."
    ES = "Detente cuando el total sea al menos 40."

    def test_exact_substrings_pass(self):
        f = {"english_excerpt": "strictly greater than 40", "spanish_excerpt": "al menos 40"}
        self.assertEqual(pc.check_excerpts(f, self.EN, self.ES), [])

    def test_hallucinated_english_rejected(self):
        f = {"english_excerpt": "greater than or equal to 40", "spanish_excerpt": "al menos 40"}
        self.assertEqual(len(pc.check_excerpts(f, self.EN, self.ES)), 1)

    def test_hallucinated_spanish_rejected(self):
        f = {"english_excerpt": None, "spanish_excerpt": "al menos 41"}
        self.assertEqual(len(pc.check_excerpts(f, self.EN, self.ES)), 1)

    def test_case_and_whitespace_matter(self):
        f = {"english_excerpt": "Strictly greater", "spanish_excerpt": None}
        self.assertTrue(pc.check_excerpts(f, self.EN, self.ES))

    def test_null_means_nothing_to_quote(self):
        f = {"english_excerpt": "Stop when", "spanish_excerpt": None}
        self.assertEqual(pc.check_excerpts(f, self.EN, self.ES), [])

    def test_empty_string_rejected(self):
        f = {"english_excerpt": "", "spanish_excerpt": None}
        self.assertTrue(pc.check_excerpts(f, self.EN, self.ES))


class ParseFindings(unittest.TestCase):
    def test_empty_array(self):
        self.assertEqual(pc.parse_findings("[]\n"), [])

    def test_json_lines(self):
        self.assertEqual(len(pc.parse_findings('{"id":"F001"}\n\n{"id":"F002"}\n')), 2)

    def test_malformed_line_raises(self):
        with self.assertRaises(ValueError):
            pc.parse_findings('{"id":"F001"}\nnot json\n')


class BrokenPrompts(unittest.TestCase):
    def setUp(self):
        self.root = make_root()
        self.pdir = os.path.join(self.root, pc.PROMPTS)

    def tearDown(self):
        shutil.rmtree(SCRATCH, ignore_errors=True)

    def test_clean_copy_passes(self):
        self.assertEqual(pc.check_prompts(self.root), [])
        self.assertEqual(pc.check_samples(self.root), [])

    def test_missing_prompt_fails(self):
        os.remove(os.path.join(self.pdir, "adjudicate.md"))
        self.assertTrue(any("adjudicate" in e for e in pc.check_prompts(self.root)))

    def test_missing_front_matter_fails(self):
        p = os.path.join(self.pdir, "review.md")
        write(p, read(p).split("---\n", 2)[2])
        self.assertTrue(any("front matter" in e for e in pc.check_prompts(self.root)))

    def test_wrong_role_fails(self):
        p = os.path.join(self.pdir, "review.md")
        write(p, read(p).replace("role: A", "role: T"))
        self.assertTrue(any("role" in e for e in pc.check_prompts(self.root)))

    def test_dangling_schema_ref_fails(self):
        p = os.path.join(self.pdir, "translate.md")
        write(p, read(p).replace("$defs/translator_output", "$defs/nope"))
        self.assertTrue(any("does not resolve" in e for e in pc.check_prompts(self.root)))

    def test_dropped_data_rule_fails(self):
        p = os.path.join(self.pdir, "translate.md")
        write(p, read(p).replace("never instructions", "maybe instructions"))
        self.assertTrue(any("never instructions" in e for e in pc.check_prompts(self.root)))

    def test_dropped_forty_rule_fails(self):
        p = os.path.join(self.pdir, "translate.md")
        write(p, read(p).replace("strictly greater than 40", "at least 40"))
        self.assertTrue(any("strictly greater than 40" in e for e in pc.check_prompts(self.root)))

    def test_bad_example_fails(self):
        p = os.path.join(self.pdir, "adjudicate.md")
        write(p, read(p).replace('"decision":"accepted"', '"decision":"maybe"'))
        self.assertTrue(any("example does not validate" in e for e in pc.check_prompts(self.root)))

    def test_bad_sample_row_fails(self):
        p = os.path.join(self.root, pc.SAMPLES, "finding.jsonl")
        write(p, read(p).replace('"critical"', '"blocker"', 1))
        self.assertTrue(any("finding.jsonl:1" in e for e in pc.check_samples(self.root)))

    def test_missing_sample_file_fails(self):
        os.remove(os.path.join(self.root, pc.SAMPLES, "ledger-row.jsonl"))
        self.assertTrue(any("ledger-row" in e for e in pc.check_samples(self.root)))

    def test_hash_changes_when_prompt_changes(self):
        p = os.path.join(self.pdir, "translate.md")
        before = pc.prompt_sha256(p)
        write(p, read(p) + "\nExtra line.\n")
        self.assertNotEqual(before, pc.prompt_sha256(p))


if __name__ == "__main__":
    unittest.main()
