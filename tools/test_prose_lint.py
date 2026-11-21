#!/usr/bin/env python3
"""Tests for tools/prose_lint.py (I21 to I26). Run: python3 -I tools/test_prose_lint.py

Every lint has a passing and a failing case; the identifier lint has one failing case per name of the review
(also, step, where, from persisted in, over-40? without its "?")."""
import os
import sys
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lessons", "book", "locale"))
import invariants as inv  # noqa: E402
import prose_lint as pl  # noqa: E402
import segment  # noqa: E402

NBSP = chr(0xA0)
CFG = pl.load_config(render=False)


def diagram(*lines, acc=None):
    body = "\n".join("    " + l for l in lines)
    head = "    accDescr: %s\n" % acc if acc else ""
    return "```mermaid\nflowchart TB\n%s%s\n```\n" % (head, body)


def label_seg(md, role=None):
    segs = [s for s in segment.Segmentation(md, "x.md").segments() if s.kind == "mermaid_label" and (role is None or s.info == role)]
    assert segs, "no label segment in the fixture"
    return segs[0]


def para_seg(text):
    return segment.Segmentation(text + "\n", "x.md").segments()[0]


def hits(inv_id, found):
    return [h for h in found if h.inv == inv_id]


class TestIdentifiers(unittest.TestCase):
    """I21: a label, accDescr or table cell that names code keeps the name, whatever the prose around it says."""

    def check(self, en_label, es_label, role="label"):
        src = label_seg(diagram('A["%s"] --> B["x"]' % en_label), role)
        return hits("I21", pl.identifier_hits(src, es_label, "x.md", CFG))

    def test_also_kept(self):
        self.assertEqual([], self.check("also chain: lock, add hours", "cadena de also: bloquea, suma horas"))

    def test_also_translated(self):
        self.assertEqual(1, len(self.check("also chain: lock, add hours", "También encadena: bloquea, suma horas")))

    def test_step_kept(self):
        self.assertEqual([], self.check("step returns False, the sentinel", "step devuelve False, el centinela"))

    def test_step_translated(self):
        self.assertEqual(1, len(self.check("step returns False, the sentinel", "paso devuelve False, el centinela")))

    def test_where_kept(self):
        self.assertEqual([], self.check("where: prefix sum is 40 or less", "where: la suma acumulada es 40 o menos"))

    def test_where_translated(self):
        self.assertEqual(1, len(self.check("where: prefix sum is 40 or less", "donde: la suma acumulada es 40 o menos")))

    def test_from_persisted_in_kept(self):
        self.assertEqual([], self.check("from persisted in the EF query", "from persisted in la consulta de EF"))

    def test_from_persisted_in_translated(self):
        self.assertEqual(1, len(self.check("from persisted in the EF query", "de persistido en la consulta de EF")))

    def test_over40_keeps_its_question_mark(self):
        self.assertEqual([], self.check("over-40? leaves a flag", "over-40? deja una bandera"))

    def test_over40_without_the_question_mark(self):
        self.assertEqual(1, len(self.check("over-40? leaves a flag", "over-40 deja una bandera")))

    def test_over40_in_accdescr_is_written_without_it(self):
        src = label_seg(diagram('A["x"] --> B["y"]', acc="Then over-40 leaves a flag on the stack."), "accDescr")
        self.assertEqual([], pl.identifier_hits(src, "Luego over-40 deja una bandera.", "x.md", CFG))
        self.assertEqual(1, len(pl.identifier_hits(src, "Luego sobre-40 deja una bandera.", "x.md", CFG)))

    def test_token_boundary(self):
        # 'where' inside 'nowhere' or 'where-clause' is not the keyword
        self.assertEqual(1, len(self.check("where: prefix sum", "nowhere: la suma")))

    def test_ordinary_english_word_is_not_a_rule_hit(self):
        # "also" as an ordinary word in a paragraph is not the Kotlin function: no rule applies
        src = para_seg("The loop is also simple.")
        self.assertEqual([], pl.identifier_hits(src, "El bucle es tambien simple.", "x.md", CFG))

    def test_camelcase_name_in_a_table_cell(self):
        src = segment.Segmentation("| a | b |\n|---|---|\n| SaveChanges runs last | x |\n", "x.md").segments()
        row = [s for s in src if s.kind == "table_row"][-1]
        self.assertEqual(1, len(pl.identifier_hits(row, "| GuardarCambios corre al final | x |", "x.md", CFG)))
        self.assertEqual([], pl.identifier_hits(row, "| SaveChanges corre al final | x |", "x.md", CFG))

    def test_files_restriction(self):
        cfg = pl.Config([{"literal": "step", "en": r"\bstep\b", "files": ["src/Only/*.md"]}])
        src = para_seg("Call step now.")
        self.assertEqual([], pl.identifier_hits(src, "Llama al paso ahora.", "src/Other/README.md", cfg))
        self.assertEqual(1, len(pl.identifier_hits(src, "Llama al paso ahora.", "src/Only/README.md", cfg)))

    def test_through_check_segment(self):
        ctx = inv.Context(prose=CFG)
        src = label_seg(diagram('A["also chain: lock"] --> B["x"]'))
        self.assertIn("I21", {f.inv for f in inv.check_segment(src, "También encadena: bloquea", ctx, "x.md")})
        self.assertNotIn("I21", {f.inv for f in inv.check_segment(src, "cadena de also: bloquea", ctx, "x.md")})


class TestKeptNamesAreNotRenderings(unittest.TestCase):
    """A name the rules keep literal must not trip the glossary (I7, 'step' is not 'paso') or the inverted marks (I10, the '?' of over-40?)."""

    def setUp(self):
        self.ctx = inv.Context(prose=CFG, glossary={"terms": [{"id": "step", "en": "step", "es": "paso"}]})

    def codes(self, md, target):
        return {f.inv for f in inv.check_segment(label_seg(diagram(md)), target, self.ctx, "x.md")}

    def test_kept_step_is_not_flagged_by_the_glossary(self):
        self.assertNotIn("I7", self.codes('A["step returns False"] --> B["x"]', "step devuelve False"))

    def test_a_step_the_rules_do_not_name_still_needs_the_glossary(self):
        self.assertIn("I7", self.codes('A["Take one step now"] --> B["x"]', "Da un salto ahora"))

    def test_over40_question_mark_is_not_an_unpaired_mark(self):
        self.assertNotIn("I10", self.codes('A["over-40? leaves a flag"] --> B["x"]', "over-40? deja una bandera"))

    def test_a_real_unpaired_mark_still_fails(self):
        self.assertIn("I10", self.codes('A["over-40? leaves a flag"] --> B["x"]', "Es esto? over-40? deja una bandera"))


class TestUnits(unittest.TestCase):
    """I22: 10 to 19 are hours per card; 3 to 5 are cards."""

    def test_hours_per_card_passes(self):
        self.assertEqual([], pl.unit_hits("Cada tarjeta suma de 10 a 19 horas por tarjeta."))

    def test_cards_fail(self):
        self.assertEqual(1, len(hits("I22", pl.unit_hits("Suma de 10 a 19 tarjetas hasta pasar de 40."))))

    def test_range_without_unit_fails(self):
        self.assertEqual(1, len(hits("I22", pl.unit_hits("Suma de 10 a 19 en cada paso."))))

    def test_unit_after_the_range_passes(self):
        self.assertEqual([], pl.unit_hits("Cada tarjeta tiene de 10 a 19 horas."))

    def test_card_count_with_hours_fails(self):
        self.assertEqual(1, len(hits("I22", pl.unit_hits("Necesitas de 3 a 5 horas para pasar de 40."))))

    def test_card_count_with_cards_passes(self):
        self.assertEqual([], pl.unit_hits("Necesitas de 3 a 5 tarjetas para pasar de 40."))

    def test_other_ranges_are_ignored(self):
        self.assertEqual([], pl.unit_hits("Los pasos 1 a 3 preparan la base."))

    def test_code_is_ignored(self):
        self.assertEqual([], pl.unit_hits("Escribe `10 a 19 tarjetas` en el campo."))


class TestDiagrams(unittest.TestCase):
    """I23: static edge-label rule, then (with a renderer) parse, render, 8.4 pt."""

    def test_unquoted_parenthesis_fails(self):
        self.assertEqual(1, len(pl.edge_label_hits('A -.->|demanda (pull)| B')))

    def test_quoted_parenthesis_passes(self):
        self.assertEqual([], pl.edge_label_hits('A -.->|"demanda (pull)"| B'))

    def test_reworded_passes(self):
        self.assertEqual([], pl.edge_label_hits('A -.->|demanda por tirón| B'))

    def test_dash_form_edge_label(self):
        self.assertEqual(1, len(pl.edge_label_hits('A -- demanda (pull) --> B')))

    def test_node_label_with_parentheses_is_not_an_edge_label(self):
        self.assertEqual([], pl.edge_label_hits('A["demanda (pull)"] --> B'))

    def fake(self, points, errors=()):
        return pl.Config(render=True, renderer=lambda sources: ({s: points for s in sources}, list(errors)))

    EN = diagram('A["Add"] --> B["Stop"]')
    ES = diagram('A["Suma"] --> B["Para"]')

    def test_render_ok(self):
        self.assertEqual([], pl.diagram_hits(self.EN, self.ES, self.fake(9.6)))

    def test_too_small_fails(self):
        found = pl.diagram_hits(self.EN, self.ES, self.fake(7.9))
        self.assertEqual(1, len(found))
        self.assertIn("8.4", found[0].msg)

    def test_exactly_the_floor_passes(self):
        self.assertEqual([], pl.diagram_hits(self.EN, self.ES, self.fake(8.4)))

    def test_render_error_fails(self):
        found = pl.diagram_hits(self.EN, self.ES, self.fake(9.6, ["diagram 1: Mermaid could not render the diagram: Parse error"]))
        self.assertEqual(1, len(found))

    def test_unavailable_renderer_fails_closed(self):
        cfg = pl.Config(render=True, renderer=lambda sources: ({}, ["cannot render: Mermaid CLI is not installed"]))
        self.assertEqual(1, len(pl.diagram_hits(self.EN, self.ES, cfg)))

    def test_an_untranslated_copy_is_not_rendered(self):
        cfg = pl.Config(render=True, renderer=lambda sources: self.fail("rendered a diagram identical to the English one"))
        self.assertEqual([], pl.diagram_hits(self.EN, self.EN, cfg))

    def test_no_render_when_switched_off(self):
        cfg = pl.Config(render=False, renderer=lambda sources: self.fail("render is off"))
        self.assertEqual([], pl.diagram_hits(self.EN, self.ES, cfg))


class TestRealRenderer(unittest.TestCase):
    """The real Mermaid CLI, when this machine has it: a good diagram renders and a broken one is refused."""

    def setUp(self):
        sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lessons", "book"))
        os.environ.setdefault("BOOK_LANG", "es")
        import diagrams
        r, why = diagrams.find_renderer()
        if r is None:
            self.skipTest(why)

    def test_good_and_bad(self):
        en = diagram('A["Add"] --> B["Stop"]')
        good = diagram('A["Suma"] --> B["Para"]')
        bad = diagram('A["Suma"] -.->|demanda (pull)| B["Para"]')
        cfg = pl.Config(render=True)
        self.assertEqual([], pl.render_hits({good.split("\n", 1)[1].rsplit("```", 1)[0]: "diagram 1"}, cfg))
        self.assertTrue(pl.render_hits({bad.split("\n", 1)[1].rsplit("```", 1)[0]: "diagram 1"}, cfg))
        self.assertTrue(pl.diagram_hits(en, bad, pl.Config(render=False)))


class TestGuarantees(unittest.TestCase):
    """I24 (B3): no absolute claim the English does not make."""

    def test_added_claim_fails(self):
        self.assertEqual(1, len(pl.claim_hits("Run it in the sandbox.", "Ejecútalo en un entorno donde un error no daña tu equipo.", CFG)))

    def test_soft_wording_passes(self):
        self.assertEqual([], pl.claim_hits("Run it in the sandbox.", "Ejecútalo solo en el entorno aislado.", CFG))

    def test_claim_the_english_makes_passes(self):
        self.assertEqual([], pl.claim_hits("The program cannot harm the data.", "El programa no puede dañar los datos.", CFG))

    def test_code_is_not_prose(self):
        self.assertEqual([], pl.claim_hits("Run `no daña`.", "Ejecuta `no daña`.", CFG))

    def test_phrase_list_comes_from_the_config(self):
        cfg = pl.Config(claims=[{"es": "garantía total"}])
        self.assertEqual(1, len(pl.claim_hits("Be careful.", "Es una garantía total.", cfg)))


class TestGlosses(unittest.TestCase):
    """I24 (B5): one first-use gloss per file."""

    def test_once_passes(self):
        self.assertEqual([], pl.gloss_hits("Un entorno aislado (*sandbox*) limita el acceso.\n\nEn el entorno aislado corre.\n", CFG))

    def test_twice_fails(self):
        text = "Un entorno aislado (*sandbox*) limita.\n\nOtro entorno aislado (*sandbox*) limita.\n"
        self.assertEqual(1, len(pl.gloss_hits(text, CFG)))

    def test_different_glosses_pass(self):
        self.assertEqual([], pl.gloss_hits("Un entorno aislado (*sandbox*) y una confirmación (*commit*).\n", CFG))

    def test_a_fence_is_not_prose(self):
        self.assertEqual([], pl.gloss_hits("Un entorno aislado (*sandbox*).\n\n```text\n(*sandbox*)\n```\n", CFG))


class TestTypography(unittest.TestCase):
    """I25 (B6)."""

    def test_nbsp_before_percent_passes(self):
        self.assertEqual([], pl.typography_hits("Sube un 30%s%%." % NBSP))

    def test_plain_space_fails(self):
        self.assertEqual(1, len(pl.typography_hits("Sube un 30 %.")))

    def test_no_space_fails(self):
        self.assertEqual(1, len(pl.typography_hits("Sube un 30%.")))

    def test_comma_before_simple_y_fails(self):
        self.assertEqual(1, len(pl.typography_hits("Suma horas, y para.")))

    def test_comma_before_simple_o_fails(self):
        self.assertEqual(1, len(pl.typography_hits("Lee, o escribe.")))

    def test_serial_comma_fails(self):
        self.assertEqual(1, len(pl.typography_hits("Sumas, restas, y multiplicas.")))

    def test_no_comma_passes(self):
        self.assertEqual([], pl.typography_hits("Suma horas y para. Lee o escribe."))

    def test_long_clauses_may_keep_the_comma(self):
        text = ("El bucle suma las horas de cada tarjeta que se dibuja al azar durante la ejecución completa del programa, "
                "y el informe final muestra el total acumulado de todas las filas guardadas en la base de datos local.")
        self.assertEqual([], pl.typography_hits(text))

    def test_aside_is_not_a_coordination(self):
        self.assertEqual([], pl.typography_hits("Usa un entorno aislado, o sandbox, para ejecutarlo."))

    def test_list_of_code_spans_passes(self):
        self.assertEqual([], pl.typography_hits("Las categorías son `Meetings`, `Coding`, `Debugging` y `Learning`."))

    def test_labels_skip_the_comma_rule_but_not_percent(self):
        self.assertEqual([], pl.typography_hits("Suma, y para", "mermaid_label"))
        self.assertEqual(1, len(pl.typography_hits("Un 30%", "mermaid_label")))


class TestLayout(unittest.TestCase):
    """I26: table dimensions, fences."""

    EN = "| a | b |\n|---|---|\n| 1 | 2 |\n| 3 | 4 |\n\n```text\nout\n```\n"

    def test_same_layout_passes(self):
        self.assertEqual([], pl.layout_hits(self.EN, self.EN.replace("a", "x").replace("1", "uno")))

    def test_dropped_column_fails(self):
        es = "| a |\n|---|\n| 1 |\n| 3 |\n\n```text\nout\n```\n"
        self.assertTrue(pl.layout_hits(self.EN, es))

    def test_row_with_a_cell_too_few_fails(self):
        es = self.EN.replace("| 3 | 4 |", "| 3 |")
        self.assertEqual(1, len(pl.layout_hits(self.EN, es)))

    def test_dropped_row_fails(self):
        self.assertTrue(pl.layout_hits(self.EN, self.EN.replace("| 3 | 4 |\n", "")))

    def test_pipe_in_a_code_span_is_not_a_separator(self):
        en = "| a | b |\n|---|---|\n| `x|y` | 2 |\n"
        self.assertEqual([], pl.layout_hits(en, en))
        self.assertEqual([("x|y", "2")], [tuple(r) for r in [[c.strip("`") for c in pl.tables(en)[0][2][0]]]])

    def test_unclosed_fence_fails(self):
        es = self.EN.rstrip("\n").rsplit("```", 1)[0]
        found = pl.layout_hits(self.EN, es)
        self.assertTrue(any("never closed" in h.msg for h in found))

    def test_fence_kind_changed_fails(self):
        self.assertTrue(pl.layout_hits(self.EN, self.EN.replace("```text", "```python")))

    def test_table_inside_a_fence_is_not_a_table(self):
        en = "```text\n| a | b |\n|---|---|\n```\n"
        self.assertEqual([], pl.tables(en))

    def test_alignment_row_changed_fails(self):
        self.assertTrue(pl.layout_hits(self.EN, self.EN.replace("|---|---|", "|---|:--|")))

    def test_missing_table_fails(self):
        self.assertTrue(pl.layout_hits(self.EN, "```text\nout\n```\n"))


class TestWiring(unittest.TestCase):
    def test_file_level_lints_run_from_check_files(self):
        en = "# T\n\nThe loop.\n\n" + diagram('A["x"] -.->|pull| B["y"]')
        es = "# T\n\nEl bucle.\n\n" + diagram('A["x"] -.->|demanda (pull)| B["y"]')
        ctx = inv.Context(prose=CFG)
        found = inv.check_files(en, es, "x.md", ctx)
        self.assertIn("I23", {f.inv for f in found})

    def test_table_lists_every_id(self):
        self.assertEqual(["I21", "I22", "I23", "I24", "I25", "I26"], list(pl.TABLE))
        for k in pl.TABLE:
            self.assertIn(k, inv.TABLE)

    def test_cli_list_and_usage(self):
        self.assertEqual(0, pl.main(["x", "--list"]))
        self.assertEqual(2, pl.main(["x"]))

    def test_real_config_loads(self):
        self.assertTrue(CFG.rules)
        self.assertTrue(CFG.claims)


if __name__ == "__main__":
    unittest.main()
