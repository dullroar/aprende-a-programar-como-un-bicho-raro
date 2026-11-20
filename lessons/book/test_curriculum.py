"""Tests for lessons/curriculum/build.py: the rules that keep docs/curriculum.md inside its plan.

    python lessons/book/test_curriculum.py

The first group runs the checks against the real curriculum (in BOOK_LANG, default "en"). The second group breaks one thing in a copy of the
English text and checks that the right problem is reported, so each rule is shown to be able to fail. The third group does the same for a
synthetic Spanish curriculum, because the real one is still English: it shows the Spanish words (Cap., the sentence limit, the register rule, the
BICHO phase letters) are enforced and that an English phase letter or acronym that survives is reported. Nothing in the repository is touched.
Needs the Python standard library and PyYAML (the locale catalog).
"""
import importlib.util, os, re, sys, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.dont_write_bytecode = True
_spec = importlib.util.spec_from_file_location("curriculum_build", os.path.join(os.path.dirname(HERE), "curriculum", "build.py"))
cb = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cb)
sys.path.insert(0, os.path.join(HERE, "locale"))
import catalog
BOOK_LANG = os.environ.get("BOOK_LANG", "en")


class InLanguage(unittest.TestCase):
    """A test class that runs with the curriculum words of `lang` and puts the previous language back afterwards."""
    lang = "en"

    @classmethod
    def setUpClass(cls):
        cls._before = cb.LANG
        cb.set_language(cls.lang)

    @classmethod
    def tearDownClass(cls):
        cb.set_language(cls._before)


def real():
    with open(cb.SOURCE, encoding="utf-8") as f:
        return f.read()


class RealCurriculum(InLanguage):
    lang = BOOK_LANG

    def test_has_no_problems(self):
        self.assertEqual(cb.check_curriculum(), [])

    def test_has_the_weird_phases_in_order(self):
        text = real()
        self.assertEqual(re.findall(r"^\| \| \*\*([^:*|]+): ", text, re.M), [p[0] for p in cb.PHASES])

    def test_points_at_the_study_guides_and_chapters_it_names(self):
        text = real()
        for target in ("study-guides/concepts/reading-adversarial-programs.md", "cs/10-events-callbacks-and-reactive-control-flow.md",
                       "exercises.md#f1-test-a-claim-of-your-choice"):
            self.assertIn(target, text)


class BrokenCurriculum(InLanguage):
    """Edits of the English text; pinned to "en". When the real curriculum is Spanish (stage 5), port these edits to it, do not delete them."""
    lang = "en"

    def problems(self, old, new):
        text = real()
        self.assertIn(old, text)
        return cb.check_curriculum(text.replace(old, new, 1))

    def test_a_missing_week_is_reported(self):
        self.assertTrue(any("weeks 1 to 16" in p for p in self.problems("| 9 | What does a closure", "| 99 | What does a closure")))

    def test_a_diagram_without_a_description_is_reported(self):
        self.assertTrue(any("accDescr" in p for p in self.problems("accDescr:", "accDesc:")))

    def test_a_wrong_chapter_number_is_reported(self):
        self.assertTrue(any("chapter 4 of the printed book" in p for p in self.problems("[Ch 4](../lessons/cs/01-", "[Ch 1](../lessons/cs/01-")))

    def test_an_arrow_to_the_box_is_reported(self):
        self.assertTrue(any("arrow to or from the box" in p for p in self.problems("    S([\"Start: phase = W\"]) --> W", "    S([\"Start: phase = W\"]) --> weeks")))

    def test_the_loop_is_bounded(self):
        text = real()
        self.assertIn("A second failed review ends the course", text)
        self.assertIn("Stop and report the gap", text)

    def test_every_week_has_a_required_guide_in_bold(self):
        rows = [l for l in real().splitlines() if re.match(r"^\| \d+ \|", l)]
        self.assertEqual(len(rows), 16)
        for row in rows:
            self.assertIn("**[", row, row[:40])

    def test_a_broken_link_is_reported(self):
        self.assertTrue(any("missing file" in p for p in self.problems("study-guides/languages/cobol.md", "study-guides/languages/cobol-gone.md")))
        self.assertTrue(any("missing heading" in p for p in self.problems("#running-things-safely", "#running-things-safe")))

    def test_a_host_outside_the_allowlist_is_reported(self):
        self.assertTrue(any("not in lessons/book/link-hosts.txt" in p for p in self.problems("https://en.wikipedia.org/wiki/Sed", "https://example.com/sed")))

    def test_a_long_sentence_is_reported(self):
        long = "This sentence keeps going " + "and going " * 12 + "until it breaks the limit."
        self.assertTrue(any("sentence of" in p for p in self.problems("The ideas are the subject.", long)))

    def test_a_contraction_and_a_dash_are_reported(self):
        self.assertTrue(any("contraction" in p for p in self.problems("You do not need a degree.", "You don't need a degree.")))
        self.assertTrue(any("em dash" in p for p in self.problems("The ideas are the subject.", "The ideas — not the syntax — are the subject.")))


    def test_a_wrong_phase_letter_is_reported(self):
        self.assertTrue(any("phase rows" in p for p in self.problems("| | **E: Execution**", "| | **X: Execution**")))
        self.assertTrue(any("labeled with the letter 'X'" in p for p in self.problems('E["E: Execution', 'E["X: Execution')))

    def test_a_wrong_exercise_id_is_reported(self):
        link = "[A1](../lessons/exercises.md#a1-read-the-rows-verified)"
        self.assertEqual(self.problems(link, link), [])
        self.assertTrue(any("an exercise ID must not change" in p for p in self.problems(link, link.replace("[A1]", "[Z9]"))))
        self.assertTrue(any("exercise link 'A1' points at the heading of exercise B3" in p
                            for p in self.problems(link, "[A1](../lessons/exercises.md#b3-forth-move-the-anchor-verified)")))

    def test_a_week_under_the_wrong_phase_is_reported(self):
        text = real()
        row = next(l for l in text.splitlines() if l.startswith("| 3 |"))
        moved = text.replace(row + "\n", "", 1).replace("| | **W: Weird** | | |\n", "| | **W: Weird** | | |\n" + row + "\n", 1)
        self.assertTrue(any("week 3 is under phase W" in p for p in cb.check_curriculum(moved)))

    def test_a_changed_acronym_sentence_is_reported(self):
        self.assertTrue(any("acronym sentence is missing" in p for p in self.problems("The W is recursive.", "The W is recursive, too.")))


def spanish_curriculum(**swap):
    """A small, correct Spanish curriculum (the real one is still English). `swap` replaces named parts to make a broken copy."""
    cat = catalog.load("es")
    with open(os.path.join(HERE, "chapters.txt"), encoding="utf-8") as f:
        order = [l.strip() for l in f.read().splitlines() if l.strip() and not l.startswith("#")]
    chapter = next(c for c in order if c.startswith("cs/"))
    n = order.index(chapter) + 1
    parts = dict(
        gloss=cat.text("acronym.gloss") + " " + cat.text("acronym.phases_note"),
        label="Cap.", chapter=chapter, n=n, usted="Lee el texto antes de ejecutarlo.",
        sentence="Este curso enseña informática con lenguajes viejos y raros.",
        row_b="| | **B: Bicho raro** | | |", node_e='E["I: Interpreta, semanas 3 a 6<br/>¿Qué lo hace avanzar?"]',
        week3="| 3 | ¿Dónde está el contador? | [Cap. @N@](../lessons/@CH@), **[guía](../lessons/study-guides/concepts/reading-adversarial-programs.md)** | [A1](../lessons/exercises.md) |",
    )
    parts.update(swap)
    rows = []
    for w in range(1, 17):
        if w == 1: rows.append(parts["row_b"])
        if w == 3: rows.append("| | **I: Interpreta** | | |")
        if w == 7: rows.append("| | **C: Camino indirecto** | | |")
        if w == 11: rows.append("| | **H: Hallazgos** | | |")
        if w == 14: rows.append("| | **O: Octetos** | | |")
        rows.append(parts["week3"] if w == 3 else f"| {w} | ¿Qué hace avanzar el programa? | **[guía](../lessons/study-guides/concepts/reading-adversarial-programs.md)** | [A1](../lessons/exercises.md) |")
    table = "\n".join(["| Semana | Pregunta | Lee | Haz |", "|---|---|---|---|"] + rows)
    text = f"""# Plan de estudios

*Un curso de 16 semanas basado en* ¡Aprende a programar como un bicho raro!

{parts['sentence']} {parts['usted']}

{parts['gloss']}

## El semestre como un algoritmo

```mermaid
flowchart TD
    accTitle: El semestre como un algoritmo
    accDescr: Un diagrama de flujo. El curso empieza en la fase B y avanza por las cinco fases hasta la revisión de la semana 16.
    S(["Inicio: fase = B"]) --> W
    subgraph weeks["Cada semana: identifica, traza, predice, ejecuta, demuestra"]
        W["B: Bicho raro, semanas 1 a 2<br/>¿Qué puede causarlo?"] --> {parts['node_e']} --> I["C: Camino indirecto, semanas 7 a 10<br/>¿Quién exige el trabajo?"] --> R["H: Hallazgos, semanas 11 a 13<br/>¿Qué sobrevive al fallo?"] --> D["O: Octetos, semanas 14 a 15<br/>¿Cuándo el código es solo datos?"]
    end
    D --> C{{{{"Revisión de la semana 16"}}}}
    C -- "sí" --> X(["Confirma y detente"])
    C -- "no, primera pasada" --> W
    C -- "no, segunda pasada" --> G(["Detente e informa de la brecha"])
```

## Semana a semana

{table}
"""
    return text.replace("@N@", str(n)).replace("@CH@", chapter)


class SpanishCurriculum(InLanguage):
    lang = "es"

    def problems(self, text=None):
        return cb.check_curriculum(spanish_curriculum() if text is None else text)

    def broken(self, **swap):
        return self.problems(spanish_curriculum(**swap))

    def has(self, needle, problems):
        self.assertTrue(any(needle in p for p in problems), (needle, problems))

    def test_the_fixture_is_clean(self):
        self.assertEqual(self.problems(), [])

    def test_the_catalog_words_are_loaded(self):
        self.assertEqual((cb.MAX_WORDS, cb.CHAPTER_LABEL, cb.ACRONYM), (28, "Cap.", "BICHO"))
        self.assertEqual([p[0] for p in cb.PHASES], list("BICHO"))
        self.assertEqual([p[1] for p in cb.PHASES], list("WEIRD"))      # the node ids never change

    def test_the_english_curriculum_fails_the_spanish_rules(self):
        english = BOOK_LANG == "en" and "BICHO" not in real()     # the translated curriculum has BICHO
        problems = self.problems(real()) if english else None
        if problems is None:
            self.skipTest("the real curriculum is already Spanish")
        self.has("acronym sentence is missing", problems)
        self.has("English acronym WEIRD survives", problems)
        self.has("phase rows", problems)

    def test_a_surviving_english_phase_letter_in_the_table_is_reported(self):
        self.has("phase rows", self.broken(row_b="| | **W: Bicho raro** | | |"))

    def test_a_surviving_english_phase_letter_in_the_diagram_is_reported(self):
        self.has("labeled with the letter 'E'", self.broken(node_e='E["E: Interpreta, semanas 3 a 6"]'))

    def test_a_surviving_english_acronym_is_reported(self):
        self.has("English acronym WEIRD survives", self.broken(sentence="El curso usa WEIRD como regla."))

    def test_a_changed_or_english_acronym_sentence_is_reported(self):
        self.has("acronym sentence is missing", self.broken(gloss="**WEIRD** stands for **Weird Execution, Indirect Results and Data**. The W is recursive."))
        self.has("phases sentence is missing", self.broken(gloss=catalog.load("es").text("acronym.gloss")))

    def test_the_english_chapter_label_is_reported(self):
        text = spanish_curriculum()
        self.has("this edition writes 'Cap.", self.problems(text.replace("[Cap. ", "[Ch ")))

    def test_a_wrong_chapter_number_is_reported(self):
        self.has("of the printed book", self.problems(spanish_curriculum().replace("[Cap. ", "[Cap. 9", 1)))

    def test_a_week_under_the_wrong_phase_is_reported(self):
        text = spanish_curriculum().replace("| | **I: Interpreta** | | |\n", "", 1).replace("| 4 |", "| | **I: Interpreta** | | |\n| 4 |", 1)
        self.has("week 3 is under phase B", self.problems(text))

    def test_usted_and_vos_are_reported(self):
        for bad in ("Usted lee el texto antes de ejecutarlo.", "Si vos leés el texto, ejecútalo.", "Lee vuestro texto antes de ejecutarlo."):
            self.has("register slip", self.broken(usted=bad))

    def test_the_tu_imperative_is_not_reported(self):
        self.assertEqual(self.broken(usted="Lee el texto, ejecútalo y compara los resultados de tu prueba."), [])

    def test_the_sentence_limit_is_28_words(self):
        words = lambda n: " ".join(["palabra"] * (n - 1)) + " final."
        self.assertEqual(self.broken(usted=words(28)), [])               # 26 or 28 words pass in Spanish (25 would be the English limit)
        self.has("sentence of 29 words (the limit is 28)", self.broken(usted=words(29)))

    def test_the_chapter_label_does_not_end_a_sentence(self):
        sentences = cb.prose_sentences("Lee el [Cap. 4](../lessons/cs/x.md) antes de empezar la semana.")
        self.assertEqual(sentences, ["Lee el Cap 4 antes de empezar la semana."])

    def test_dashes_and_curly_quotes_are_reported(self):
        self.has("em dash", self.broken(sentence="Las ideas — no la sintaxis — son el tema."))
        self.has("curly quote", self.broken(sentence="Lee “con cuidado” el texto."))

    def test_the_spanish_word_todo_is_not_a_placeholder(self):
        self.assertEqual(self.broken(usted="Lee todo el texto antes de ejecutarlo."), [])

    def test_upper_case_markers_are_still_placeholders(self):
        for marker in ("TODO", "TBD", "lorem ipsum"):
            self.has("placeholder text", self.broken(usted="Lee %s antes de ejecutarlo." % marker))

    def test_the_week_table_is_still_checked(self):
        self.has("weeks 1 to 16",self.problems(spanish_curriculum().replace("| 9 |", "| 99 |", 1)))

    def test_set_language_is_all_or_nothing(self):
        with self.assertRaises(catalog.CatalogError):
            cb.set_language("xx")
        self.assertEqual((cb.LANG, cb.MAX_WORDS), ("es", 28))

    def test_the_spanish_sentence_limit_matches_the_loop_config(self):
        config = os.path.join(cb.REPO, "loop", "CONFIG.yaml")
        if not os.path.exists(config):
            self.skipTest("needs loop/CONFIG.yaml")
        with open(config, encoding="utf-8") as f:
            n = int(re.search(r"^sentence_word_limit_N:\s*(\d+)", f.read(), re.M).group(1))
        self.assertEqual(cb.MAX_WORDS, n)


class Pages(unittest.TestCase):
    def test_the_written_pdf_is_within_the_page_limit(self):
        pdf = os.path.join(cb.REPO, "curriculum.pdf")
        pages = cb.pdf_pages(pdf) if os.path.exists(pdf) else None
        if pages is None:
            self.skipTest("needs curriculum.pdf and Ghostscript")
        self.assertLessEqual(pages, cb.MAX_PAGES)


if __name__ == "__main__":
    unittest.main()
