#!/usr/bin/env python3
"""Tests for tools/invariants.py (plan 7.2, I1 to I16). Run: python3 -I tools/test_invariants.py

Every invariant has at least one passing and one failing case. A failing case must name the invariant,
so a check that silently stops firing makes a test fail.
"""
import hashlib
import io
import os
import sys
import tempfile
import unittest
from contextlib import redirect_stdout

import polib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lessons", "book", "locale"))
import catalog  # noqa: E402
import invariants as inv  # noqa: E402
import lock_code  # noqa: E402
import mask  # noqa: E402
import segment  # noqa: E402

ROOT = os.path.dirname(HERE)
O, C = mask.OPEN, mask.CLOSE


def ph(kind, n):
    return "%s%s_%04d%s" % (O, kind, n, C)


GLOSSARY = {
    "frozen": {
        "timecard_rule": {"banned": ["hasta 40", "40 o más"]},
        "assurance_labels": {"labels": [{"enum": "guaranteed", "es": "garantizado", "banned": ["asegurado"]}]},
    },
    "terms": [
        {"id": "loop", "en": "loop", "es": "bucle", "banned": ["ciclo"]},
        {"id": "sandbox", "en": "sandbox", "es": "entorno aislado (*sandbox*)"},
        {"id": "weird-program", "en": "weird (kind of program)", "es": "raro"},
    ],
}
HUMOR = {
    "Behold the monstrosity": {"id": "H002", "kind": "heading", "english": "Behold the monstrosity",
                               "status": "pending", "spanish": None, "reviewer_note": None},
    "How the hell does that work?": {"id": "H003", "kind": "heading", "english": "How the hell does that work?",
                                     "status": "transcreated", "spanish": "¿Cómo demonios funciona?",
                                     "reviewer_note": None},
    "It does not, of course.": {"id": "H090", "kind": "prose", "english": "It does not, of course.",
                                "status": "deliberately-flattened", "spanish": None, "reviewer_note": None},
}


def make_ctx(**kw):
    base = dict(dnt=["Meetings", "DEMO ONLY"], glossary=GLOSSARY, cat=catalog.load("es"), lang_cat=catalog.load("en"),
                humor=HUMOR, sentence_limit=10, tier_of=lambda rel: "T2",
                phase_names=["Weird", "Execution", "Indirect", "Results", "Data"])
    base.update(kw)
    return inv.Context(**base)


def segs(text, rel="x.md"):
    return segment.Segmentation(text, rel)


def first(text):
    return segs(text).segments()[0]


def codes(findings):
    return sorted({f.inv for f in findings})


class Base(unittest.TestCase):
    def setUp(self):
        self.ctx = make_ctx()

    def run_seg(self, src_text, target, **ctx_kw):
        ctx = make_ctx(**ctx_kw) if ctx_kw else self.ctx
        return inv.check_segment(first(src_text), target, ctx)

    def assertClean(self, findings):
        self.assertEqual([], [tuple(f) for f in findings])

    def assertFires(self, findings, code):
        self.assertIn(code, codes(findings), "expected %s, got %s" % (code, [tuple(f) for f in findings]))


class TestTable(unittest.TestCase):
    def test_all_sixteen_documented(self):
        self.assertEqual(["I%d" % n for n in range(1, 17)], list(inv.TABLE))

    def test_list_cli(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(0, inv.main(["x", "--list"]))
        self.assertIn("I16", buf.getvalue())

    def test_cli_usage_is_nonzero(self):
        with redirect_stdout(io.StringIO()):
            self.assertEqual(2, inv.main(["x"]))


class TestI1(Base):
    def test_pass_on_a_real_file(self):
        with open(os.path.join(ROOT, "tests", "fixtures", "mixed.md"), encoding="utf-8", newline="") as f:
            text = f.read()
        self.assertClean([f for f in inv.check_files(text, text, "mixed.md", self.ctx) if f.inv == "I1"])

    def test_fail_when_the_segmenter_refuses(self):
        bad = "# Title\n\n```text\nnever closed\n"
        self.assertFires(inv.check_files(bad, bad, "bad.md", self.ctx), "I1")


class TestI2(Base):
    SRC = "Run `make all` and see https://example.com now."

    def test_pass(self):
        s = first(self.SRC)
        tgt = "Ejecuta %s y mira %s ahora." % (ph("CODE", 1), ph("URL", 2))
        self.assertEqual(s.masked.count(O), 2)
        self.assertClean(inv.check_segment(s, tgt, self.ctx))

    def test_reordering_is_allowed(self):
        s = first(self.SRC)
        tgt = "Mira %s y ejecuta %s ahora." % (ph("URL", 2), ph("CODE", 1))
        self.assertClean(inv.check_segment(s, tgt, self.ctx))

    def test_dropped_invented_duplicated(self):
        s = first(self.SRC)
        self.assertFires(inv.check_segment(s, "Ejecuta %s ahora." % ph("CODE", 1), self.ctx), "I2")
        self.assertFires(inv.check_segment(s, "Ejecuta %s %s y %s ahora." % (ph("CODE", 1), ph("CODE", 1), ph("URL", 2)), self.ctx), "I2")
        self.assertFires(inv.check_segment(s, "Ejecuta %s %s %s ahora." % (ph("CODE", 1), ph("URL", 2), ph("CODE", 9)), self.ctx), "I2")

    def test_i2_failure_stops_further_checks(self):
        s = first(self.SRC)
        self.assertEqual(["I2"], codes(inv.check_segment(s, "Run it", self.ctx)))


class TestI3(Base):
    SRC = "Each card has 10 to 19 hours; stop above 40."

    def test_pass(self):
        self.assertClean(self.run_seg(self.SRC, "Cada tarjeta tiene de 10 a 19 horas; detente con más de 40."))

    def test_fail_changed_digit(self):
        self.assertFires(self.run_seg(self.SRC, "Cada tarjeta tiene de 10 a 91 horas; detente con más de 40."), "I3")

    def test_fail_added_digit(self):
        self.assertFires(self.run_seg(self.SRC, "Cada tarjeta tiene de 10 a 19 horas; detente con más de 40 o 41."), "I3")

    def test_macro_digits_do_not_count(self):
        self.assertClean(self.run_seg("The W is recursive.", "La {{phase.1.letter}} es recursiva."))

    def test_fail_comparison_sign_changes(self):
        # "≤ 40" written "< 40" moves the stop rule: exactly 40 would stop
        self.assertFires(self.run_seg("Alive: total ≤ 40?", "¿Vivo: total < 40?"), "I3")
        self.assertFires(self.run_seg("Alive: total ≤ 40?", "¿Vivo: total ≥ 40?"), "I3")

    def test_comparison_sign_kept_or_put_in_words_is_clean(self):
        self.assertClean(self.run_seg("Alive: total ≤ 40?", "¿Vivo: total ≤ 40?"))
        self.assertClean(self.run_seg("The flag is -1 while total <= 40.", "La bandera es -1 mientras el total no pasa de 40."))
        self.assertClean(self.run_seg("The flag is -1 while total <= 40.", "La bandera es -1 mientras total ≤ 40."))

    def test_waived_by_exception(self):
        s = first(self.SRC)
        ctx = make_ctx(exceptions={(s.id, "I3")})
        self.assertClean(inv.check_segment(s, "Cada tarjeta tiene de 10 a 91 horas; detente con más de 40.", ctx))


class TestI4(Base):
    SRC = "See [the guide](lessons/guide.md#phase-one) for more."

    def test_pass(self):
        self.assertClean(self.run_seg(self.SRC, "Mira %s para más cosas." % "[la guía](%s)" % ph("DEST", 1)))

    def test_link_destination_helper(self):
        self.assertEqual(["a.md#x", "b.md"], inv.link_destinations("[t](a.md#x) and [u](b.md \"title\")\n```\n[no](c.md)\n```"))

    def test_fail_on_changed_destination(self):
        a = inv.i4("See [g](lessons/guide.md#phase-one) now.", "Mira [g](lessons/guide.md#fase-uno) ya.", self.ctx)
        self.assertFires(a, "I4")

    def test_pass_with_anchor_map(self):
        ctx = make_ctx(anchor_map={"phase-one": "fase-uno"})
        a = inv.i4("See [g](lessons/guide.md#phase-one) now.", "Mira [g](lessons/guide.md#fase-uno) ya.", ctx)
        self.assertClean(a)

    def test_reference_definitions(self):
        self.assertEqual(["x.md"], inv.link_destinations("[a]: x.md\n"))

    def test_fail_on_dropped_link_in_files(self):
        en = "# T\n\nSee [g](g.md) now.\n"
        es = "# T\n\nMira la guía ahora.\n"
        self.assertFires(inv.check_files(en, es, "t.md", self.ctx), "I4")


MERMAID_EN = """# T

```mermaid
flowchart TB
    accTitle: The rule
    S["Start here"] --> D{"total #gt; 40?"}
    D -- "yes" --> E(["Stop"])
```
"""
MERMAID_ES = """# T

```mermaid
flowchart TB
    accTitle: La regla
    S["Empieza aquí"] --> D{"total #gt; 40?"}
    D -- "sí" --> E(["Detente"])
```
"""


class TestI5(Base):
    def test_pass(self):
        self.assertEqual([], [f for f in inv.i5(MERMAID_EN, MERMAID_ES, "t.md")])

    def test_fail_changed_arrow(self):
        bad = MERMAID_ES.replace("D -- ", "D -.- ")
        self.assertFires(inv.i5(MERMAID_EN, bad, "t.md"), "I5")

    def test_fail_changed_node_id(self):
        bad = MERMAID_ES.replace("S[", "Z[")
        self.assertFires(inv.i5(MERMAID_EN, bad, "t.md"), "I5")

    def test_fail_dropped_diagram(self):
        self.assertFires(inv.i5(MERMAID_EN, "# T\n", "t.md"), "I5")

    def test_check_files_runs_i5(self):
        self.assertFires(inv.check_files(MERMAID_EN, MERMAID_ES.replace("TB", "LR"), "t.md", self.ctx), "I5")


class TestI6(Base):
    EN = '---\ntitle: "The weird way"\nslug: weird\nstate: draft\nitems:\n  - one\n---\n\nBody.\n'

    def test_pass_only_allowlisted_keys_differ(self):
        es = self.EN.replace("The weird way", "El camino raro")
        self.assertEqual([], inv.i6(self.EN, es))

    def test_fail_enum_changed(self):
        self.assertFires(inv.i6(self.EN, self.EN.replace("slug: weird", "slug: raro")), "I6")

    def test_fail_key_renamed(self):
        self.assertFires(inv.i6(self.EN, self.EN.replace("slug:", "babosa:")), "I6")

    def test_fail_key_dropped(self):
        self.assertFires(inv.i6(self.EN, self.EN.replace("slug: weird\n", "")), "I6")

    def test_fail_list_value_changed(self):
        self.assertFires(inv.i6(self.EN, self.EN.replace("- one", "- uno")), "I6")


class TestI7(Base):
    def test_pass(self):
        self.assertClean(self.run_seg("The loop stops.", "El bucle se detiene."))

    def test_missing_approved_term(self):
        self.assertFires(self.run_seg("The loop stops.", "La repetición se detiene."), "I7")

    def test_banned_synonym(self):
        self.assertFires(self.run_seg("The loop stops.", "El bucle y el ciclo se detienen."), "I7")

    def test_parenthetical_gloss_needs_only_the_base_form(self):
        self.assertClean(self.run_seg("Use a sandbox here.", "Usa un entorno aislado aquí."))

    def test_plural_still_requires_the_term(self):
        self.assertFires(self.run_seg("Two loops run.", "Dos repeticiones corren."), "I7")

    def test_regular_plural_of_the_approved_form_is_accepted(self):
        self.assertClean(self.run_seg("Two loops run.", "Dos bucles corren."))

    def test_plural_variants_of_multiword_forms(self):
        self.assertIn("tarjetas de horas", inv.form_variants("tarjeta de horas"))
        self.assertIn("totales acumulados", inv.form_variants("total acumulado"))
        self.assertIn("funciones", inv.form_variants("función"))
        self.assertNotIn("tarjeta de horas", inv.form_variants("tarjetas"))

    def test_feminine_forms_of_an_adjective_are_accepted(self):
        self.assertIn("recursiva", inv.form_variants("recursivo"))
        self.assertIn("recursivas", inv.form_variants("recursivo"))
        self.assertIn("total acumulada", inv.form_variants("total acumulado"))
        self.assertNotIn("recursivo", inv.form_variants("recursiva"))
        self.assertNotIn("recursión", inv.form_variants("recursivo"))

    def test_plural_of_another_word_is_not_accepted(self):
        self.assertFires(self.run_seg("Two loops run.", "Dos ciclos corren."), "I7")

    def test_frozen_timecard_wording_is_banned(self):
        self.assertFires(self.run_seg("Stop at the total.", "Detente hasta 40 en el total."), "I7")

    def test_banned_assurance_label(self):
        self.assertFires(self.run_seg("It is guaranteed.", "Es un comportamiento asegurado."), "I7")

    def test_assurance_ban_needs_the_english_label(self):
        self.assertClean(self.run_seg("It is safe here.", "Aquí es seguro."))

    def test_banned_rendering_needs_the_english_term(self):
        # 'ciclo' is banned for 'loop'; an English source without 'loop' may use it
        self.assertClean(self.run_seg("The cycle ends.", "El ciclo termina."))

    def test_banned_word_already_in_source_is_not_blamed(self):
        self.assertClean(self.run_seg("The loop uses the ciclo word.", "El bucle usa la palabra ciclo."))


class TestI8(Base):
    def test_pass(self):
        self.assertEqual([], inv.i8("Use Meetings here", "Usa Meetings aquí", self.ctx))

    def test_fail_when_translated(self):
        self.assertFires(inv.i8("Use Meetings here", "Usa reuniones aquí", self.ctx), "I8")

    def test_word_boundary(self):
        self.assertEqual([], inv.i8("No Meetingsx here", "Nada aquí", self.ctx))

    def test_masked_dnt_survives_the_segment_pipeline(self):
        self.assertClean(self.run_seg("Use Meetings here for the loop.", "Usa %s aquí para el bucle." % ph("DNT", 1)))
        self.assertFires(self.run_seg("Use Meetings here for the loop.", "Usa reuniones aquí para el bucle."), "I2")


class TestI9(Base):
    def test_pass(self):
        self.assertClean(self.run_seg("This is the loop that you run.", "Este es el bucle que ejecutas."))

    def test_fail_left_in_english(self):
        self.assertFires(self.run_seg("The loop is that you can run it.", "The bucle is that you can run it."), "I9")

    def test_fail_identical_to_source(self):
        self.assertFires(self.run_seg("Sentinel values mark every ending.", "Sentinel values mark every ending."), "I9")

    def test_short_segments_are_not_judged(self):
        self.assertClean(self.run_seg("Output", "Output"))

    def test_code_only_segments_are_exempt(self):
        self.assertClean(self.run_seg("`for` and `while`", "%s y %s" % (ph("CODE", 1), ph("CODE", 2))))


class TestI10(Base):
    def test_pass(self):
        self.assertClean(self.run_seg("Why does it stop?", "¿Por qué se detiene?"))

    def test_unpaired_question(self):
        self.assertFires(self.run_seg("Why does it stop?", "Por qué se detiene?"), "I10")

    def test_unclosed_inverted(self):
        self.assertFires(self.run_seg("Wow, it stops!", "¡Vaya, se detiene."), "I10")

    def test_nested_and_two_sentences_ok(self):
        self.assertEqual([], inv.paired_marks("¿Qué? ¡Sí! ¿Cómo, ¡qué!?"))

    def test_curly_quotes_rejected(self):
        self.assertFires(self.run_seg('Say "hello" now.', "Di “hola” ahora."), "I10")

    def test_straight_quotes_pass(self):
        self.assertClean(self.run_seg('Say "hello" now.', 'Di "hola" ahora.'))

    def test_marks_inside_code_are_ignored(self):
        self.assertClean(self.run_seg("Use `a ? b : c` here.", "Usa %s aquí." % ph("CODE", 1)))

    def label(self, text):
        s = segs(text).segments()
        return [x for x in s if x.kind == "mermaid_label"]

    def test_mermaid_label_quote_rejected(self):
        lab = [x for x in self.label(MERMAID_EN) if x.span.quoted][0]
        self.assertFires(inv.check_segment(lab, 'Di "hola"', self.ctx), "I10")

    def test_mermaid_label_clean(self):
        lab = self.label(MERMAID_EN)[0]
        self.assertClean([f for f in inv.check_segment(lab, "Say #quot;hola#quot;", self.ctx) if f.inv == "I10"])

    def test_mermaid_message_semicolon_rejected(self):
        seq = "```mermaid\nsequenceDiagram\n    A->>B: Hello there friend\n```\n"
        lab = self.label(seq)[0]
        self.assertFires(inv.check_segment(lab, "Hola; amigo", self.ctx), "I10")


class TestI11(Base):
    def test_pass(self):
        self.assertClean(self.run_seg("It is **very** odd.", "Es **muy** raro."))

    def test_fail_dropped_bold(self):
        self.assertFires(self.run_seg("It is **very** odd.", "Es muy raro."), "I11")

    def test_fail_added_bold(self):
        self.assertFires(self.run_seg("It is **very** odd.", "Es **muy** **raro**."), "I11")

    def test_file_level_bold_count(self):
        en = "# T\n\nIt is **very** odd.\n"
        self.assertFires(inv.check_files(en, "# T\n\nEs muy raro.\n", "t.md", self.ctx), "I11")

    def test_fixed_lead_in_uses_the_locale_string(self):
        en_cat = catalog.Catalog("en", {"hints.leadin": "Hint", "acronym.word": "WEIRD"})
        es_cat = catalog.Catalog("es", {"hints.leadin": "Pista", "acronym.word": "BICHO"})
        ctx = make_ctx(lang_cat=en_cat, cat=es_cat)
        self.assertClean(inv.check_segment(first("**Hint** think twice."), "**Pista** piensa dos veces.", ctx))
        self.assertFires(inv.check_segment(first("**Hint** think twice."), "**Consejo** piensa dos veces.", ctx), "I11")


class TestI11SharedParagraph(Base):
    """The study guides must open "The shared challenge" with the catalog paragraph, word for word (study_guides.py check)."""
    EN = ("The [challenge specification](../../intro.md#what-the-challenge-does) calls for cards with a category and 10 to 19 whole hours. "
          "Categories cycle through Meetings, Coding, Debugging and Learning. Add each card's hours to the running total. "
          "Stop when the total passes 40. Keep the **first card that takes the total over 40**. A total of exactly 40 continues. "
          "Four 10-hour cards need a fifth card, in the Meetings category. Conforming runs finish with 3 to 5 cards and a total of 41 to 59 hours.")

    def sctx(self):
        return make_ctx(dnt=["Meetings", "Coding", "Debugging", "Learning"], tier_of=lambda rel: "T2", sentence_limit=60)

    def msgstr(self):
        return inv.shared_paragraph_masked(first(self.EN), self.sctx())

    def test_masked_catalog_text_passes(self):
        text = self.msgstr()
        self.assertIsNotNone(text)
        self.assertIn("`" + ph("DNT", 2) + "`", text)
        self.assertClean(inv.check_segment(first(self.EN), text, self.sctx()))

    def test_free_translation_fails(self):
        free = self.msgstr().replace("Detente cuando el total pasa de 40", "Detente cuando el total pase de 40")
        self.assertNotEqual(free, self.msgstr())
        self.assertFires(inv.check_segment(first(self.EN), free, self.sctx()), "I11")

    def test_other_paragraphs_are_not_affected(self):
        self.assertIsNone(inv.shared_paragraph_masked(first("A different paragraph about cards."), self.sctx()))

    def test_edited_english_is_not_the_standard_paragraph(self):
        self.assertIsNone(inv.shared_paragraph_masked(first(self.EN.replace("exactly 40", "at least 40")), self.sctx()))


class TestI7LeadIn(Base):
    def ctx_with_lead_in(self):
        en_cat = catalog.Catalog("en", {"hints.lead_in_a": "The loop part.", "acronym.word": "WEIRD"})
        es_cat = catalog.Catalog("es", {"hints.lead_in_a": "La parte repetida.", "acronym.word": "BICHO"})
        return make_ctx(lang_cat=en_cat, cat=es_cat)

    def test_term_inside_a_catalog_lead_in_is_not_checked(self):
        ctx = self.ctx_with_lead_in()
        self.assertClean(inv.check_segment(first("**The loop part.** Stop now."), "**La parte repetida.** Detente ahora.", ctx))

    def test_term_in_the_body_after_a_lead_in_is_still_checked(self):
        ctx = self.ctx_with_lead_in()
        self.assertFires(inv.check_segment(first("**The loop part.** The loop stops."),
                                           "**La parte repetida.** La repetición se detiene.", ctx), "I7")

    def test_bold_that_is_not_a_catalog_lead_in_is_still_checked(self):
        ctx = self.ctx_with_lead_in()
        self.assertFires(inv.check_segment(first("**The loop part two.** Stop now."), "**La parte dos.** Detente ahora.", ctx), "I7")


class TestI12(Base):
    LONG = "one two three four five six seven eight nine ten eleven twelve."

    def test_pass_short(self):
        self.assertClean(self.run_seg("Stop now. Then go.", "Detente ahora. Luego sigue.", tier_of=lambda rel: "T1"))

    def test_fail_long_sentence_in_t1(self):
        self.assertFires(self.run_seg("A sentence.", "Una oración de este tamaño %s" % self.LONG, tier_of=lambda rel: "T1"), "I12")

    def test_long_sentence_ignored_in_t2(self):
        self.assertClean(self.run_seg("A sentence.", "Una oración de este tamaño %s" % self.LONG))

    def test_placeholder_counts_as_one_word(self):
        ctx = make_ctx(tier_of=lambda rel: "T1", sentence_limit=3)
        self.assertEqual([], inv.i12(first("`x` y."), "Usa %s aquí." % ph("CODE", 1), "g.md", ctx))

    def test_closing_emphasis_after_a_question_mark_ends_the_sentence(self):
        ctx = make_ctx(tier_of=lambda rel: "T1", sentence_limit=5)
        self.assertEqual([], inv.i12(first("a"), "uno dos tres *¿cuatro cinco?* seis siete ocho nueve.", "g.md", ctx))
        self.assertTrue(inv.i12(first("a"), "uno dos tres *¿cuatro cinco seis siete ocho nueve?*", "g.md", ctx))

    def test_table_cell_separator_ends_a_sentence(self):
        ctx = make_ctx(tier_of=lambda rel: "T1", sentence_limit=5)
        sep = ph("SEP", 1)
        self.assertEqual([], inv.i12(first("a"), "uno dos tres %s cuatro cinco seis %s" % (sep, sep), "g.md", ctx))

    def test_long_text_inside_one_cell_still_fails(self):
        ctx = make_ctx(tier_of=lambda rel: "T1", sentence_limit=5)
        sep = ph("SEP", 1)
        self.assertTrue(inv.i12(first("a"), "%s uno dos tres cuatro cinco seis siete %s" % (sep, sep), "g.md", ctx))

    def test_fail_usted(self):
        self.assertFires(self.run_seg("Run it now.", "Ejecute usted el programa.", tier_of=lambda rel: "T1"), "I12")

    def test_fail_voseo(self):
        self.assertFires(self.run_seg("You can run it now.", "Vos podés ejecutarlo ahora.", tier_of=lambda rel: "T1"), "I12")

    def test_tier_table(self):
        self.assertEqual("T1", inv.tier_of_path("lessons/study-guides/forth.md"))
        self.assertEqual("T3", inv.tier_of_path("CONTRIBUTING.md"))
        self.assertEqual("T2", inv.tier_of_path("lessons/exercises.md"))


class TestI13(Base):
    EN = "# T\n\nUse `make all` here.\n\n```text\nTotal: 41\n```\n"

    def test_pass(self):
        es = "# T\n\nUsa `make all` aquí.\n\n```text\nTotal: 41\n```\n"
        self.assertEqual([], inv.i13_text(self.EN, es, "t.md"))

    def test_fail_translated_output_block(self):
        es = "# T\n\nUsa `make all` aquí.\n\n```text\nTotal: cuarenta y uno\n```\n"
        self.assertFires(inv.i13_text(self.EN, es, "t.md"), "I13")

    def test_fail_translated_inline_code(self):
        es = "# T\n\nUsa `hacer todo` aquí.\n\n```text\nTotal: 41\n```\n"
        self.assertFires(inv.i13_text(self.EN, es, "t.md"), "I13")

    def test_fail_dropped_fence(self):
        self.assertFires(inv.i13_text(self.EN, "# T\n\nUsa `make all` aquí.\n", "t.md"), "I13")

    CARDS_EN = "# T\n\nThe categories are Meetings and Coding, then `make all`.\n"

    def file_findings(self, es):
        return [f for f in inv.check_files(self.CARDS_EN, es, "t.md", make_ctx(dnt=["Meetings", "Coding"]))
                if f.inv in ("I2", "I13")]

    def test_dnt_phrase_in_backticks_is_allowed(self):
        """The frozen Spanish wording writes the card categories as code; the English writes them bare."""
        self.assertEqual([], self.file_findings("# T\n\nLas categorías son `Meetings` y `Coding`, luego `make all`.\n"))

    def test_fail_backticks_around_a_word_that_is_not_dnt(self):
        self.assertFires(self.file_findings("# T\n\nLas categorías son Meetings y Coding, luego `make all` y `bucle`.\n"), "I13")

    def test_fail_translated_code_next_to_a_wrapped_dnt_phrase(self):
        self.assertFires(self.file_findings("# T\n\nLas categorías son `Meetings` y `Coding`, luego `hacer todo`.\n"), "I13")

    def test_fail_dnt_phrase_in_backticks_is_not_a_license_to_drop_code(self):
        self.assertFires(self.file_findings("# T\n\nLas categorías son `Meetings` y `Coding`, luego make all.\n"), "I13")

    def test_fail_generated_block_edited(self):
        en = "# T\n\n<!-- BEGIN GENERATED x -->\nA\n<!-- END GENERATED x -->\n"
        self.assertFires(inv.i13_text(en, en.replace("\nA\n", "\nB\n"), "t.md"), "I13")

    def test_protected_files_clean_then_changed(self):
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "translation"))
            data = b"print(40)\n"
            with open(os.path.join(root, "prog.py"), "wb") as f:
                f.write(data)
            manifest = lock_code.format_manifest({"prog.py": hashlib.sha256(data).hexdigest()})
            with open(os.path.join(root, lock_code.MANIFEST), "w", encoding="utf-8") as f:
                f.write(manifest)
            self.assertEqual([], inv.protected_files(root))
            with open(os.path.join(root, "prog.py"), "wb") as f:
                f.write(b"print(41)\n")
            got = inv.protected_files(root)
            self.assertFires(got, "I13")
            self.assertEqual("prog.py", got[0].where)


class TestI14(Base):
    def test_pass_with_macros(self):
        self.assertClean(self.run_seg("The W is recursive.", "La {{phase.1.letter}} es recursiva."))

    def test_fail_surviving_english_phase(self):
        self.assertFires(self.run_seg("Phase one is a phase.", "La fase W: Weird sigue aquí y no cambia."), "I14")

    def test_fail_english_acronym_survives(self):
        self.assertFires(self.run_seg("The acronym is cute.", "El acrónimo WEIRD es simpático."), "I14")

    def test_fail_literal_spanish_acronym(self):
        self.assertFires(self.run_seg("The acronym is cute.", "El acrónimo BICHO es simpático."), "I14")

    def test_fail_literal_spanish_phase(self):
        self.assertFires(self.run_seg("The first phase is odd.", "La primera fase es B: Bicho raro, claro."), "I14")

    def test_fail_english_letter_kept_as_label(self):
        self.assertFires(self.run_seg("The first phase is odd.", "W: Raro, semanas 1 a 2, es la primera."), "I14")
        self.assertFires(self.run_seg("Start: phase = W", "Inicio: fase = W"), "I14")

    def test_fail_bare_english_letter_in_prose(self):
        self.assertFires(self.run_seg("If it fails, the second pass starts at W again.",
                                      "Si no la supera, la segunda pasada vuelve a empezar en W."), "I14")
        self.assertFires(self.run_seg("The W is recursive.", "La W es recursiva."), "I14")

    def test_bare_letter_check_skips_what_the_source_never_wrote_and_exercise_sections(self):
        self.assertClean(self.run_seg("If it fails, the second pass starts at W again.",
                                      "Si no la supera, la segunda pasada vuelve a empezar en {{phase.1.letter}}."))
        self.assertClean(self.run_seg("Pick one of the D section.", "Elige uno de la sección D.", exercise_prefixes=["D", "E"]))
        self.assertFires(self.run_seg("Pick one of the D section.", "Elige uno de la sección D.", exercise_prefixes=["B"]), "I14")

    def test_english_letter_check_has_no_false_positive_on_macros(self):
        self.assertClean(self.run_seg("Start: phase = W", "Inicio: fase = {{phase.1.letter}}"))
        self.assertClean(self.run_seg("The first phase is odd, weeks 1 to 2.", "{{phase.1.letter}}: {{phase.1.name}}, semanas 1 a 2, es la primera."))

    def test_macro_form_is_accepted(self):
        self.assertClean(self.run_seg("The acronym is cute.", "El acrónimo {{acronym.word}} es simpático."))

    def test_torce_swap_changes_what_is_literal(self):
        flat = dict(catalog.load("es").flat)
        flat["acronym.word"] = "TORCE"
        ctx = make_ctx(cat=catalog.Catalog("es", flat))
        self.assertFires(inv.check_segment(first("The acronym is cute."), "El acrónimo TORCE es simpático.", ctx), "I14")
        self.assertClean(inv.check_segment(first("The acronym is cute."), "El acrónimo BICHO es simpático.", ctx))

    def test_unknown_macro_is_reported(self):
        po = polib.POFile()
        s = first("The W is recursive.")
        po.append(polib.POEntry(msgctxt=s.id, msgid=s.masked, msgstr="La {{phase.9.letter}} es recursiva."))
        found = inv.check_po("The W is recursive.\n", po, "x.md", self.ctx)
        self.assertFires(found, "I14")


class TestI15(Base):
    def test_pending_heading_fails(self):
        self.assertFires(self.run_seg("# Behold the monstrosity\n", "Contempla la monstruosidad"), "I15")

    def test_transcreated_heading_passes_only_with_the_recorded_text(self):
        self.assertClean(self.run_seg("# How the hell does that work?\n", "¿Cómo demonios funciona?"))
        self.assertFires(self.run_seg("# How the hell does that work?\n", "¿Cómo funciona eso?"), "I15")

    def test_flattened_without_reason_fails(self):
        self.assertFires(self.run_seg("It does not, of course.", "Claro que no lo hace."), "I15")

    def test_flattened_with_reason_passes(self):
        humor = dict(HUMOR)
        humor["It does not, of course."] = dict(HUMOR["It does not, of course."], reviewer_note="too cultural")
        self.assertClean(self.run_seg("It does not, of course.", "Claro que no lo hace.", humor=humor))

    def test_unlisted_segments_are_not_playful(self):
        self.assertClean(self.run_seg("# Plain heading text\n", "Texto de encabezado simple"))


class TestI16(Base):
    EN = "# Heading text here\n\nFirst paragraph about the loop.\n"

    def po_for(self, en, targets=None, fuzzy=(), drop=(), extra=()):
        seg = segs(en)
        po = polib.POFile()
        for s in seg.segments():
            if s.id in drop:
                continue
            tgt = (targets or {}).get(s.id, s.masked)
            e = polib.POEntry(msgctxt=s.id, msgid=s.masked, msgstr=tgt)
            if s.id in fuzzy:
                e.flags.append("fuzzy")
            po.append(e)
        for e in extra:
            po.append(e)
        return seg, po

    def full_targets(self, seg):
        ids = [s.id for s in seg.segments()]
        return {ids[0]: "Texto del encabezado aquí", ids[1]: "Primer párrafo sobre el bucle."}

    def test_pass(self):
        seg = segs(self.EN)
        _, po = self.po_for(self.EN, self.full_targets(seg))
        self.assertClean(inv.check_po(self.EN, po, "x.md", self.ctx))

    def test_fail_missing_entry(self):
        seg = segs(self.EN)
        ids = [s.id for s in seg.segments()]
        _, po = self.po_for(self.EN, self.full_targets(seg), drop={ids[1]})
        self.assertFires(inv.check_po(self.EN, po, "x.md", self.ctx), "I16")

    def test_fail_empty_and_fuzzy(self):
        seg = segs(self.EN)
        t = self.full_targets(seg)
        ids = list(t)
        _, po = self.po_for(self.EN, {ids[0]: "", ids[1]: t[ids[1]]})
        self.assertIn("untranslated", " ".join(f.msg for f in inv.check_po(self.EN, po, "x.md", self.ctx)))
        _, po = self.po_for(self.EN, t, fuzzy={ids[1]})
        self.assertIn("fuzzy", " ".join(f.msg for f in inv.check_po(self.EN, po, "x.md", self.ctx)))

    def test_fail_orphan(self):
        seg = segs(self.EN)
        orphan = polib.POEntry(msgctxt="s-000000000000-0099", msgid="Gone", msgstr="Ido")
        _, po = self.po_for(self.EN, self.full_targets(seg), extra=[orphan])
        self.assertIn("orphan", " ".join(f.msg for f in inv.check_po(self.EN, po, "x.md", self.ctx)))

    def test_fail_duplicate(self):
        seg = segs(self.EN)
        t = self.full_targets(seg)
        _, po = self.po_for(self.EN, t)
        po.append(polib.POEntry(msgctxt=list(t)[0], msgid="dup", msgstr="dup"))
        self.assertIn("duplicate", " ".join(f.msg for f in inv.check_po(self.EN, po, "x.md", self.ctx)))

    def test_fail_stale_msgid(self):
        seg = segs(self.EN)
        t = self.full_targets(seg)
        _, po = self.po_for(self.EN, t)
        po[0].msgid = "An older English text"
        self.assertIn("stale", " ".join(f.msg for f in inv.check_po(self.EN, po, "x.md", self.ctx)))

    def test_logged_exception_waives_coverage(self):
        seg = segs(self.EN)
        ids = [s.id for s in seg.segments()]
        _, po = self.po_for(self.EN, self.full_targets(seg), drop={ids[1]})
        ctx = make_ctx(exceptions={(ids[1], "I16")})
        self.assertClean(inv.check_po(self.EN, po, "x.md", ctx))

    def test_segment_findings_flow_through_check_po(self):
        seg = segs(self.EN)
        t = self.full_targets(seg)
        ids = list(t)
        t[ids[1]] = "Primer párrafo sobre el ciclo."
        _, po = self.po_for(self.EN, t)
        self.assertFires(inv.check_po(self.EN, po, "x.md", self.ctx), "I7")


class TestRealContext(unittest.TestCase):
    def test_loads_and_waives_nothing_by_default(self):
        ctx = inv.load_context()
        self.assertTrue(ctx.terms)
        self.assertIn("Meetings", ctx.dnt)
        import inventory
        self.assertEqual(int(inventory.read_config(ROOT)["sentence_word_limit_N"]), ctx.sentence_limit)
        self.assertEqual(29, ctx.sentence_limit)      # calibrated on the pilot (translation/pilot-calibration.md)
        self.assertEqual(["Weird", "Execution", "Indirect", "Results", "Data"], ctx.phase_names)

    def test_identity_po_is_not_accepted_as_a_translation(self):
        path = os.path.join(ROOT, "tests", "fixtures", "mixed.md")
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        import apply
        po = apply.new_po(segment.Segmentation(text, "mixed.md"), "mixed.md", identity=True)
        found = inv.check_po(text, po, "mixed.md", inv.load_context())
        self.assertIn("I9", codes(found))

    def test_empty_po_is_not_coverage(self):
        path = os.path.join(ROOT, "tests", "fixtures", "mixed.md")
        with open(path, encoding="utf-8", newline="") as f:
            text = f.read()
        import apply
        po = apply.new_po(segment.Segmentation(text, "mixed.md"), "mixed.md")
        self.assertEqual({"I16"}, set(codes(inv.check_po(text, po, "mixed.md", inv.load_context()))))

    def test_t0_cli_on_a_fixture(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = inv.main(["x", "--t0", os.path.join(ROOT, "tests", "fixtures", "mixed.md")])
        self.assertEqual(0, rc, buf.getvalue())


if __name__ == "__main__":
    unittest.main()
