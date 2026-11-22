#!/usr/bin/env python3
"""Tests for tools/sync_guide_diagrams.py and the pilot-render filters. Run: python3 -I tools/test_sync_guide_diagrams.py"""
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import polib                      # noqa: E402
import apply as ap                # noqa: E402
import pilot_render as pr         # noqa: E402
import segment                    # noqa: E402
import sync_guide_diagrams as sync  # noqa: E402

DIAGRAM = """```mermaid
flowchart TD
    accTitle: Counting loop
    A["Start the counting loop"] --> B["Print the total"]
```
"""
SOURCE = "# Demo\n\n## Program Flow\n\n" + DIAGRAM
GUIDE = "# Guide\n\n<!-- diagram-source: src/demo/README.md#program-flow -->\n\n" + DIAGRAM


def po_for(en_text, rel, translations):
    """A PO for `en_text` where translations maps an English label text to its Spanish."""
    seg = segment.Segmentation(en_text, rel)
    po = ap.new_po(seg, rel)
    for e in po:
        e.msgstr = translations.get(e.msgid, "")
    return po


class TestSync(unittest.TestCase):
    def setUp(self):
        self.src_po = po_for(SOURCE, "src/demo/README.md",
                             {"Counting loop": "Bucle de conteo", "Start the counting loop": "Inicia el bucle de conteo",
                              "Print the total": "Imprime el total"})
        self.guide_seg = segment.Segmentation(GUIDE, "g.md")
        # The guide was translated on its own, with different wording.
        self.guide_po = po_for(GUIDE, "g.md", {"Counting loop": "Bucle que cuenta", "Start the counting loop": "Empieza a contar",
                                               "Print the total": "Muestra el total"})

    def loader(self, po):
        return lambda path: (SOURCE, po)

    def msgstrs(self):
        return {e.msgid: e.msgstr for e in self.guide_po}

    def test_copies_the_source_translation(self):
        changed, pending, problems = sync.sync(self.guide_seg, self.guide_po, self.loader(self.src_po))
        self.assertEqual((3, 0, []), (changed, pending, problems))
        self.assertEqual("Imprime el total", self.msgstrs()["Print the total"])

    def test_second_run_changes_nothing(self):
        sync.sync(self.guide_seg, self.guide_po, self.loader(self.src_po))
        self.assertEqual(0, sync.sync(self.guide_seg, self.guide_po, self.loader(self.src_po))[0])

    def test_untranslated_source_is_pending_and_leaves_the_guide_alone(self):
        before = self.msgstrs()
        changed, pending, problems = sync.sync(self.guide_seg, self.guide_po, self.loader(po_for(SOURCE, "src/demo/README.md", {})))
        self.assertEqual((0, 3, []), (changed, pending, problems))
        self.assertEqual(before, self.msgstrs())

    def test_missing_source_po_is_pending(self):
        self.assertEqual((0, 3, []), sync.sync(self.guide_seg, self.guide_po, self.loader(None)))

    def test_label_that_is_not_in_the_source_is_a_problem(self):
        guide = GUIDE.replace("Print the total", "Print the grand total")
        seg = segment.Segmentation(guide, "g.md")
        po = po_for(guide, "g.md", {})
        changed, pending, problems = sync.sync(seg, po, self.loader(self.src_po))
        self.assertTrue(any("no counterpart" in p for p in problems), problems)

    def test_missing_source_file_is_a_problem(self):
        def gone(path):
            raise FileNotFoundError(path)
        self.assertTrue(sync.sync(self.guide_seg, self.guide_po, gone)[2])

    def test_block_n_source_is_found(self):
        source = "# Chapter\n\nText.\n\n" + DIAGRAM
        guide = GUIDE.replace("src/demo/README.md#program-flow", "lessons/cs-source/chapters/x.md#block-1")
        seg = segment.Segmentation(guide, "g.md")
        changed, pending, problems = sync.sync(seg, self.guide_po, lambda path: (source, self.src_po))
        self.assertEqual((3, 0, []), (changed, pending, problems))

    def test_block_n_out_of_range_is_a_problem(self):
        source = "# Chapter\n\nText.\n\n" + DIAGRAM
        guide = GUIDE.replace("src/demo/README.md#program-flow", "lessons/cs-source/chapters/x.md#block-2")
        seg = segment.Segmentation(guide, "g.md")
        problems = sync.sync(seg, self.guide_po, lambda path: (source, self.src_po))[2]
        self.assertTrue(any("no diagram" in p for p in problems), problems)

    def test_unmarked_diagram_is_ignored(self):
        seg = segment.Segmentation("# G\n\n" + DIAGRAM, "g.md")
        self.assertEqual([], sync.diagrams_with_markers(seg))


class TestPilotFilters(unittest.TestCase):
    def test_only_untranslated_sources_are_excused(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "src", "a"))
            os.makedirs(os.path.join(root, "src", "b"))
            with open(os.path.join(root, "src", "a", "README.md"), "w", encoding="utf-8") as f:
                f.write("# A\n\n## Program Flow\n")
            with open(os.path.join(root, "src", "b", "README.md"), "w", encoding="utf-8") as f:
                f.write("# B\n\n## Flujo del programa\n")
            msg = "line 62: src/%s/README.md#program-flow: the file has no '## Program Flow' section"
            self.assertTrue(pr.expected_during_pilot(msg % "a", "intro.md#x", root))
            self.assertFalse(pr.expected_during_pilot(msg % "b", "intro.md#x", root))     # translated but the section is missing: a real error
            self.assertFalse(pr.expected_during_pilot(msg % "c", "intro.md#x", root))     # no such file
            self.assertFalse(pr.expected_during_pilot("line 3: placeholder text 'TODO'", "intro.md#x", root))

    def test_missing_intro_heading_is_excused_only_while_intro_is_english(self):
        msg = "link to a missing heading: ../../intro.md#qué-hace-el-reto"
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "lessons"))
            intro = os.path.join(root, "lessons", "intro.md")
            with open(intro, "w", encoding="utf-8") as f:
                f.write("## What the challenge does\n")
            self.assertTrue(pr.expected_during_pilot(msg, "intro.md#qué-hace-el-reto", root))
            self.assertFalse(pr.expected_during_pilot(msg.replace("reto", "otro"), "intro.md#qué-hace-el-reto", root))
            with open(intro, "w", encoding="utf-8") as f:
                f.write("## Qué hace el reto\n")
            self.assertFalse(pr.expected_during_pilot(msg, "intro.md#qué-hace-el-reto", root))


if __name__ == "__main__":
    unittest.main()
