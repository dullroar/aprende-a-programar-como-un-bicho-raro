#!/usr/bin/env python3
"""Tests for tools/impact.py. Run: python3 -m unittest tools/test_impact.py -v
Includes negative cases that must fail."""
import json
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import impact as im  # noqa: E402

B = lambda s: s.encode("utf-8")

EN_README = "# Awk\n\nIntro text.\n\n## Run it\n\nSteps here.\n\n## Diagram\n\n```mermaid\nflowchart TD\n  A --> B\n```\n"
ES_README = "# Awk\n\nTexto de introducción.\n\n## Ejecútalo\n\nPasos aquí.\n\n## Diagrama\n\n```mermaid\nflowchart TD\n  A --> B\n```\n"
CS_SRC = "---\ntitle: X\n---\nBody about [[entry:awk]].\n"
CS_GEN = "---\ntitle: X\n---\nGenerated body.\n"
CODE = "BEGIN { print total }\n"


def base():
    return {
        "src/awk/README.md": B(EN_README),
        "src/awk/timecards.awk": B(CODE),
        "lessons/cs-source/concepts/backpressure.md": B(CS_SRC),
        "lessons/cs/backpressure.md": B(CS_GEN),
        "lessons/languages/awk.md": B("# AWK\n\nSee [the entry](../../src/awk/README.md).\n"),
    }


def spanish():
    d = {k: v for k, v in base().items()}
    d["src/awk/README.md"] = B(ES_README)
    return d


class Units(unittest.TestCase):
    def test_sections_and_duplicates(self):
        s = im.md_sections("pre\n# A\nx\n# A\ny\n")
        self.assertEqual([k for k, _ in s], ["", "a", "a-2"])

    def test_heading_inside_fence_is_not_a_section(self):
        s = im.md_sections("# A\n```\n# not a heading\n```\n")
        self.assertEqual([k for k, _ in s], ["", "a"])

    def test_hash_ignores_trailing_whitespace(self):
        a = im.units("a.md", B("# T\nx  \n"))
        b = im.units("a.md", B("# T\nx\n"))
        self.assertEqual(a[1]["hash"], b[1]["hash"])


class SourceMap(unittest.TestCase):
    def test_sections_pair_by_position_and_hashes_differ(self):
        rows = im.build_source_map(base(), spanish(), {})
        r = [x for x in rows if x["en_unit"] == "src/awk/README.md#run-it"][0]
        self.assertEqual(r["es_unit"], "src/awk/README.md#ejecútalo")
        self.assertNotEqual(r["en_hash"], r["es_hash"])

    def test_path_rename_is_recorded(self):
        es = spanish()
        es["RETO.md"] = es.pop("src/awk/README.md")
        rows = im.build_source_map(base(), es, {"src/awk/README.md": "RETO.md"})
        self.assertTrue(all(r["es_path"] == "RETO.md" for r in rows if r["en_path"] == "src/awk/README.md"))

    def test_missing_spanish_file_is_flagged(self):
        es = spanish()
        del es["lessons/languages/awk.md"]
        rows = im.build_source_map(base(), es, {})
        self.assertIn("missing-in-spanish", [r.get("note") for r in rows])

    def test_section_count_mismatch_pairs_whole_file(self):
        es = spanish()
        es["src/awk/README.md"] = B("# Awk\n\nSolo esto.\n")
        rows = im.build_source_map(base(), es, {})
        self.assertIn("sections-differ", [r.get("note") for r in rows if r["en_path"] == "src/awk/README.md"])

    def test_manifest_classes(self):
        m = im.build_manifest(base(), {})
        self.assertEqual(m["files"]["lessons/cs/backpressure.md"]["class"], "generated")
        self.assertEqual(m["files"]["src/awk/timecards.awk"]["class"], "frozen")
        self.assertEqual(m["files"]["src/awk/README.md"]["class"], "authored")


class Delta(unittest.TestCase):
    def run_impact(self, new, ident=None):
        smap = im.build_source_map(base(), spanish(), {})
        return im.impact(base(), new, smap, ident, "t", {})

    def test_no_change_schedules_nothing(self):
        r = self.run_impact(base())
        self.assertEqual(r["units"], [])
        self.assertEqual(r["gates"], [])
        self.assertEqual(r["model_calls_needed"], 0)

    def test_new_paragraph_schedules_only_that_section(self):
        new = base()
        new["src/awk/README.md"] = B(EN_README.replace("Steps here.", "Steps here.\n\nA new paragraph."))
        r = self.run_impact(new)
        self.assertEqual(r["translate_units"], ["src/awk/README.md#run-it"])
        u = r["units"][0]
        self.assertEqual(u["es_unit"], "src/awk/README.md#ejecútalo")
        self.assertEqual(u["action"], "translate-minimal-edit")
        self.assertGreater(r["reused_spanish_units"], 0)
        self.assertNotIn("oracle", r["gates"])
        self.assertEqual(r["oracle_families"], [])

    def test_generated_only_change_traces_to_source_and_is_not_translated(self):
        new = base()
        new["lessons/cs/backpressure.md"] = B(CS_GEN + "extra\n")
        r = self.run_impact(new)
        self.assertEqual(r["translate_units"], [])
        self.assertEqual(r["model_calls_needed"], 0)
        u = r["units"][0]
        self.assertTrue(u["generated_only"])
        self.assertEqual(u["traced_to"], ["lessons/cs-source/concepts/backpressure.md"])
        self.assertIn("generate", u["gates"])

    def test_authored_change_reaches_generated_chapters_and_links(self):
        new = base()
        new["src/awk/README.md"] = B(EN_README.replace("Intro text.", "Intro text, longer."))
        r = self.run_impact(new)
        deps = r["units"][0]["dependents"]
        self.assertIn("lessons/cs/backpressure.md", deps)
        self.assertIn("lessons/languages/awk.md", deps)  # transitive through the link graph

    def test_code_change_asks_for_reconcile_and_oracle(self):
        new = base()
        new["src/awk/timecards.awk"] = B("BEGIN { print sum }\n")
        r = self.run_impact(new)
        self.assertEqual(r["oracle_families"], ["src/awk"])
        self.assertIn("oracle", r["gates"])
        self.assertIn("three-way", r["units"][0]["action"])
        self.assertEqual(r["translate_units"], [])

    def test_renamed_symbol_triggers_reevaluation(self):
        new = base()
        new["src/awk/timecards.awk"] = B("BEGIN { print sum }\n")
        ident = [{"path": "src/awk/timecards.awk", "old": "total", "new": "suma", "language": "awk"}]
        r = self.run_impact(new, ident)
        self.assertEqual(r["symbols"][0]["english"], "total")
        self.assertIn("ledger", r["gates"])

    def test_symbol_still_present_is_not_flagged(self):
        new = base()
        new["src/awk/timecards.awk"] = B("BEGIN { print total, 1 }\n")
        ident = [{"path": "src/awk/timecards.awk", "old": "total", "new": "suma", "language": "awk"}]
        self.assertEqual(self.run_impact(new, ident)["symbols"], [])

    def test_moved_heading_is_a_rename_free_add_remove_and_hits_link_audit(self):
        new = base()
        new["src/awk/README.md"] = B(EN_README.replace("## Run it", "## Running it"))
        r = self.run_impact(new)
        self.assertIn("link_audit", r["gates"])
        kinds = sorted(u["kind"] for u in r["units"])
        self.assertEqual(kinds, ["added", "removed"])

    def test_diagram_change_reaches_mermaid_gate(self):
        new = base()
        new["src/awk/README.md"] = B(EN_README.replace("A --> B", "A --> C"))
        r = self.run_impact(new)
        self.assertIn("mermaid", r["gates"])

    def test_file_rename_detected_by_hash(self):
        new = base()
        new["lessons/languages/awk-lang.md"] = new.pop("lessons/languages/awk.md")
        r = self.run_impact(new)
        u = r["units"][0]
        self.assertEqual(u["kind"], "renamed")
        self.assertEqual(u["renamed_from"], "lessons/languages/awk.md")
        self.assertEqual(r["translate_units"], [])

    def test_new_file_needs_translation(self):
        new = base()
        new["lessons/languages/sed.md"] = B("# sed\n\nText.\n")
        r = self.run_impact(new)
        self.assertEqual(r["translate_units"], ["lessons/languages/sed.md#sed"])

    # negative controls: these assertions must fail if the tool were wrong
    def test_negative_generated_change_is_not_scheduled_for_translation(self):
        new = base()
        new["lessons/cs/backpressure.md"] = B(CS_GEN + "extra\n")
        r = self.run_impact(new)
        with self.assertRaises(AssertionError):
            self.assertIn("lessons/cs/backpressure.md#", " ".join(r["translate_units"]) + "lessons/cs/backpressure.md#")
            self.assertTrue(r["translate_units"])

    def test_negative_untouched_family_not_scheduled(self):
        new = base()
        new["src/awk/timecards.awk"] = B("BEGIN { print sum }\n")
        r = self.run_impact(new)
        self.assertNotIn("src/sed", r["oracle_families"])

    def test_output_is_json_serializable(self):
        new = base()
        new["src/awk/timecards.awk"] = B("x\n")
        json.dumps(self.run_impact(new))


if __name__ == "__main__":
    unittest.main()
