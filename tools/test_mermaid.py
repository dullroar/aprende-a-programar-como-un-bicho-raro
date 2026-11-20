#!/usr/bin/env python3
"""Tests for tools/mermaid.py and the Mermaid path of tools/segment.py (plan 7.1 R6; invariants I2, I5, I10).
Run: python3 -I tools/test_mermaid.py"""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mermaid  # noqa: E402
import segment  # noqa: E402

ROOT = os.path.dirname(HERE)

FLOW = [
    "flowchart TB",
    "    accTitle: A short title",
    "    accDescr: A longer description, with commas.",
    '    subgraph INV["Invariant I holds"]',
    '        S["State s: bits"] -->|step one| T(["allowed step"])',
    "        T --> S2",
    "    end",
    "    classDef warn fill:#fdd,stroke:#a00",
    "    class S warn",
]
SEQ = [
    "sequenceDiagram",
    "    accTitle: Choosing is not computing",
    "    participant H as Orchestrator / host",
    "    participant W as Worker",
    "    H->>W: invoke or resume",
    "    Note over H,W: the host decides",
    "    loop until done",
    "        W-->>H: done",
    "    end",
]
STATE = [
    "stateDiagram-v2",
    '    state "Waiting for input" as Wait',
    "    [*] --> Wait",
    "    Wait --> Run : key pressed",
]


def roles(lines):
    return [(s.role, s.text) for s in mermaid.extract(lines)]


class ExtractTests(unittest.TestCase):
    def test_flowchart_labels(self):
        self.assertEqual(roles(FLOW), [
            ("accTitle", "A short title"),
            ("accDescr", "A longer description, with commas."),
            ("label", "Invariant I holds"),
            ("label", "State s: bits"),
            ("edge", "step one"),
            ("label", "allowed step"),
        ])

    def test_sequence_labels(self):
        self.assertEqual(roles(SEQ), [
            ("accTitle", "Choosing is not computing"),
            ("participant", "Orchestrator / host"),
            ("participant", "Worker"),
            ("message", "invoke or resume"),
            ("note", "the host decides"),
            ("block", "until done"),
            ("message", "done"),
        ])

    def test_state_labels(self):
        self.assertEqual(roles(STATE), [("state", "Waiting for input"), ("transition", "key pressed")])

    def test_spans_point_at_the_text(self):
        for body in (FLOW, SEQ, STATE):
            for sp in mermaid.extract(body):
                self.assertEqual(body[sp.line][sp.start:sp.end], sp.text)

    def test_identity_replacement_changes_nothing(self):
        for body in (FLOW, SEQ, STATE):
            spans = mermaid.extract(body)
            self.assertEqual(mermaid.apply_spans(body, spans, [s.text for s in spans]), body)

    def test_ids_arrows_and_styles_are_not_labels(self):
        text = " ".join(s.text for s in mermaid.extract(FLOW))
        for skeleton_word in ("classDef", "fill", "S2", "-->", "flowchart", "INV"):
            self.assertNotIn(skeleton_word, text)


class SkeletonTests(unittest.TestCase):
    def translated(self, body):
        spans = mermaid.extract(body)
        return mermaid.apply_spans(body, spans, ["ES " + s.text for s in spans])

    def test_translating_labels_keeps_the_skeleton(self):
        for body in (FLOW, SEQ, STATE):
            self.assertEqual(mermaid.skeleton(self.translated(body)), mermaid.skeleton(body))
            self.assertEqual(mermaid.skeleton_problems(body, self.translated(body)), [])

    def test_changed_node_id_is_reported(self):
        bad = [ln.replace("S2", "S9") for ln in self.translated(FLOW)]
        self.assertTrue(mermaid.skeleton_problems(FLOW, bad))

    def test_changed_arrow_is_reported(self):
        bad = [ln.replace("T --> S2", "T --- S2") for ln in self.translated(FLOW)]
        self.assertTrue(any("skeleton line" in p for p in mermaid.skeleton_problems(FLOW, bad)))

    def test_dropped_line_is_reported(self):
        bad = self.translated(SEQ)[:-2] + ["end"]
        self.assertTrue(any("line count" in p or "slots" in p for p in mermaid.skeleton_problems(SEQ, bad)))

    def test_translated_class_name_is_reported(self):
        bad = [ln.replace("class S warn", "class S aviso") for ln in self.translated(FLOW)]
        self.assertTrue(mermaid.skeleton_problems(FLOW, bad))


class FailClosedTests(unittest.TestCase):
    def bad(self, *lines):
        with self.assertRaises(mermaid.MermaidError):
            mermaid.extract(list(lines))

    def test_unquoted_node_label(self):
        self.bad("flowchart TD", "    A[Start here] --> B")

    def test_unquoted_edge_label(self):
        self.bad("flowchart TD", '    A["x"] -- maybe --> B')

    def test_click_directive(self):
        self.bad("flowchart TD", '    A["x"]', "    click A href \"http://x\"")

    def test_multiline_accdescr(self):
        self.bad("flowchart TD", "    accDescr {", "      text", "    }")

    def test_unknown_diagram_type(self):
        self.bad("gantt", "    title x")

    def test_empty_diagram(self):
        self.bad("%% only a comment")

    def test_sequence_title(self):
        self.bad("sequenceDiagram", "    title Not supported")

    def test_unrecognised_sequence_line(self):
        self.bad("sequenceDiagram", "    gibberish line here")


class LabelProblemTests(unittest.TestCase):
    def span(self, body, role):
        return [s for s in mermaid.extract(body) if s.role == role][0]

    def test_ok_text(self):
        self.assertEqual(mermaid.label_problems(self.span(FLOW, "label"), "Estado s: bits"), [])

    def test_quote_in_quoted_label(self):
        self.assertTrue(mermaid.label_problems(self.span(FLOW, "label"), 'dice "hola"'))

    def test_quote_entity_is_fine(self):
        self.assertEqual(mermaid.label_problems(self.span(FLOW, "label"), "dice #quot;hola#quot;"), [])

    def test_pipe_in_edge_label(self):
        self.assertTrue(mermaid.label_problems(self.span(FLOW, "edge"), "a | b"))

    def test_semicolon_in_message(self):
        self.assertTrue(mermaid.label_problems(self.span(SEQ, "message"), "uno; dos"))

    def test_entity_semicolon_is_fine(self):
        self.assertEqual(mermaid.label_problems(self.span(SEQ, "message"), "x #gt; y"), [])

    def test_empty_and_multiline(self):
        sp = self.span(FLOW, "label")
        self.assertTrue(mermaid.label_problems(sp, "  "))
        self.assertTrue(mermaid.label_problems(sp, "a\nb"))


DOC = ("Intro text.\n\n```mermaid\nflowchart TD\n    A[\"Start #gt; here\"] -->|go| B[\"Run `x`\"]\n"
       "    classDef warn fill:#fdd\n```\n\nOutro.\n")


class SegmenterTests(unittest.TestCase):
    def setUp(self):
        self.s = segment.Segmentation(DOC, "t.md")

    def labels(self):
        return [x for x in self.s.segments() if x.kind == "mermaid_label"]

    def test_labels_become_segments(self):
        self.assertEqual([x.text for x in self.labels()], ["Start #gt; here", "go", "Run `x`"])

    def test_entities_and_code_are_masked_placeholders(self):
        first, _, third = self.labels()
        self.assertEqual(len(first.mapping), 1)
        self.assertNotIn("#gt;", first.masked)
        self.assertNotIn("`x`", third.masked)

    def test_placeholder_multiset_preserved_on_translation(self):
        lab = self.labels()[0]
        tgt = lab.masked.replace("Start", "Inicio").replace("here", "aquí")
        self.assertIn("#gt;", self.s.reassemble({lab.id: tgt}))

    def test_dropped_placeholder_fails_closed(self):
        lab = self.labels()[2]
        with self.assertRaises(ValueError):
            self.s.reassemble({lab.id: "Ejecuta"})

    def test_invented_placeholder_fails_closed(self):
        lab = self.labels()[1]
        with self.assertRaises(ValueError):
            self.s.reassemble({lab.id: lab.masked + " " + self.labels()[2].masked})

    def test_quote_in_target_fails_closed(self):
        lab = self.labels()[0]
        with self.assertRaises(ValueError):
            self.s.reassemble({lab.id: lab.masked.replace("Start", 'di "hola"')})

    def test_identity_reassembles_byte_identical(self):
        self.assertEqual(self.s.reassemble(), DOC)

    def test_translated_diagram_has_equal_skeleton(self):
        targets = {}
        for lab in self.labels():
            targets[lab.id] = lab.masked.replace("Start", "Inicio").replace("here", "aquí").replace("go", "ir") \
                .replace("Run", "Ejecuta")
        out = self.s.reassemble(targets)
        self.assertIn("Inicio", out)
        self.assertNotEqual(out, DOC)
        en = DOC.split("\n")[3:7]
        es = out.split("\n")[3:7]
        self.assertEqual(mermaid.skeleton_problems(en, es), [])
        self.assertEqual(out.split("\n")[0], "Intro text.")
        self.assertEqual(out.split("\n")[-2], "Outro.")

    def test_unsupported_construct_raises_segment_error(self):
        with self.assertRaises(segment.SegmentError):
            segment.Segmentation("```mermaid\nflowchart TD\n    A[Start] --> B\n```\n", "t.md")

    def test_segment_ids_are_unique(self):
        ids = [x.id for x in self.s.segments()]
        self.assertEqual(len(ids), len(set(ids)))


class RealDiagramTests(unittest.TestCase):
    def test_every_authored_mermaid_fence_extracts_and_round_trips(self):
        n = 0
        for path in segment.authored_files():
            full = os.path.join(ROOT, path)
            s = segment.Segmentation(segment.read_raw(full), path)
            for b in s.blocks:
                if b.kind == "mermaid":
                    n += 1
                    body = b.lines[1:-1]
                    self.assertTrue(b.labels, path)
                    self.assertEqual(mermaid.skeleton_problems(body, body), [], path)
        self.assertGreater(n, 0)


if __name__ == "__main__":
    unittest.main()
