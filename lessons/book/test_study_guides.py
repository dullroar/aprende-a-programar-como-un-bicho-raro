"""Tests for study_guides.py: the rules that keep the hand-written study guides honest.

    python lessons/book/test_study_guides.py

The first group runs the rules against the real guides and the real book. The second group copies the lessons tree and the entries' READMEs into a
scratch folder, breaks one thing, and checks that the right problem is reported, so each rule is shown to be able to fail. Nothing in the
repository is touched. Needs only the Python standard library.
"""
import os, re, shutil, sys, tempfile, unicodedata, unittest
from unittest import mock
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import study_guides as sg

REPO = sg.REPO
# The language of the real guides under lessons/study-guides/. It is English until the guides are translated; then BOOK_LANG=es
# (or flipping the default in study_guides.py) makes RealRepository check the Spanish guides. The Mutations class edits English
# text on purpose and stays pinned to "en"; the Spanish contract is tested on a synthetic guide (class SpanishContract below).
REAL_LANG = os.environ.get("BOOK_LANG", "en")


def use_language(testcase, lang):
    """Switch study_guides (and diagrams) to `lang` for one test and restore the previous language afterwards."""
    old = sg.LANG
    sg.set_language(lang)
    testcase.addCleanup(sg.set_language, old)


def snapshot(dest):
    """Copy what the checks read: the lessons tree (minus build output and the Mermaid tools), the entries (minus build output, so source-line
    links can be checked) and the root Markdown files that guides link to."""
    shutil.copytree(os.path.join(REPO, "lessons"), os.path.join(dest, "lessons"),
                    ignore=shutil.ignore_patterns("out", "__pycache__", "node_modules"))
    shutil.copytree(os.path.join(REPO, "src"), os.path.join(dest, "src"),
                    ignore=shutil.ignore_patterns("target", "node_modules", "obj", "bin", ".gradle", "build", "__pycache__", ".git"))
    for f in os.listdir(REPO):
        if f.endswith(".md") and os.path.isfile(os.path.join(REPO, f)):
            shutil.copy(os.path.join(REPO, f), os.path.join(dest, f))
    for sub in ("docs",):
        if os.path.isdir(os.path.join(REPO, sub)):
            shutil.copytree(os.path.join(REPO, sub), os.path.join(dest, sub))


class RealRepository(unittest.TestCase):
    def setUp(self):
        use_language(self, REAL_LANG)

    def test_every_rule_passes_on_the_real_guides(self):
        problems = sg.check_all()
        self.assertEqual(problems, [], "\n".join(problems))

    def test_thirteen_language_guides_and_eight_concept_guides(self):
        self.assertEqual(len(sg.LANGUAGE_GUIDES), 13)
        self.assertEqual(len(sg.CONCEPT_GUIDES), 8)
        for g in sg.ALL_GUIDES:
            self.assertTrue(os.path.isfile(os.path.join(sg.GUIDES, g)), g)

    def test_every_guide_is_in_the_manifest_and_the_index(self):
        chap = sg.manifest()
        index = sg.read(os.path.join(sg.GUIDES, "README.md"))
        for g in sg.ALL_GUIDES:
            self.assertIn(g, chap)
            self.assertIn(f"]({g}", index, f"the index does not link to {g}")

    def test_the_book_does_not_contain_the_guides(self):
        book = sg.read(os.path.join(sg.LESSONS, "book", "chapters.txt"))
        self.assertNotIn("study-guides", book)

    def test_every_expected_program_flow_diagram_is_reused_verbatim(self):
        for rel, entries in sg.EXPECTED_DIAGRAMS.items():
            found = {m[1] for _, _, m in sg.guide_diagrams(sg.read(os.path.join(sg.GUIDES, rel))) if m and m[0] == "source"}
            for e in entries:
                self.assertIn(f"src/{e}/README.md#program-flow", found, f"{rel} lacks the Program Flow diagram of {e}")

    def test_the_book_points_at_each_guide(self):
        for g, pages in sg.BOOK_LINKS.items():
            for page in pages:
                head = "\n".join(sg.read(os.path.join(sg.LESSONS, page)).split("\n")[:40])
                self.assertIn(f"study-guides/{g}", head, f"lessons/{page} should link to {g} near its start")

    def test_the_generated_chapters_were_not_edited_by_hand(self):
        # The links in lessons/cs/ come from lessons/cs-source/. Both must carry them.
        for g, pages in sg.BOOK_LINKS.items():
            for page in (p for p in pages if p.startswith("cs/")):
                src = os.path.join(sg.LESSONS, "cs-source", "chapters", os.path.basename(page))
                self.assertIn(f"study-guides/{g}", sg.read(src), f"{src} is the source of {page}")

    def test_the_companion_edition_matches_the_book(self):
        book = re.search(r'^title:\s*"(.+)"', sg.read(os.path.join(sg.LESSONS, "book", "metadata.yaml")), re.M).group(1)
        self.assertIn(f'companion-to: "{book}"', sg.read(os.path.join(sg.GUIDES, "metadata.yaml")))


class Scanner(unittest.TestCase):
    def setUp(self):
        use_language(self, "en")

    def test_sections_ignore_headings_inside_fences(self):
        text = "# T study guide\n\n## One\n\nbody\n\n```text\n## Not a heading\n```\n\n## Two\n\nmore\n"
        self.assertEqual([t for t, _, _ in sg.sections(text)], ["One", "Two"])

    def test_canonical_source_by_block_number_and_heading(self):
        a = sg.canonical_source("lessons/cs-source/chapters/04-evaluation-and-demand.md#block-1")
        self.assertTrue(a.startswith("flowchart"))
        b = sg.canonical_source("lessons/intro.md#what-the-challenge-does")
        self.assertIn("What the challenge does", b)
        c = sg.canonical_source("src/cobol-weird/README.md#program-flow")
        self.assertTrue(c.startswith("stateDiagram-v2"))

    def test_canonical_source_refuses_generated_files(self):
        for ref in ("lessons/cs/04-evaluation-and-demand.md#block-1", "lessons/languages/cobol.md#block-1"):
            with self.assertRaises(ValueError):
                sg.canonical_source(ref)

    def test_diagram_markers_are_found_across_blank_lines(self):
        text = "<!-- diagram-source: src/x/README.md#program-flow -->\n\n```mermaid\nflowchart TD\n```\n\n<!-- diagram-new: lazy-demand-trace - why -->\n```mermaid\nflowchart TD\n```\n\n```mermaid\nflowchart TD\n```\n"
        found = [m for _, _, m in sg.guide_diagrams(text)]
        self.assertEqual(found[0], ("source", "src/x/README.md#program-flow"))
        self.assertEqual(found[1][:2], ("new", "lazy-demand-trace"))
        self.assertIsNone(found[2])


class Mutations(unittest.TestCase):
    """Each test breaks one thing in a scratch copy and expects the matching problem."""

    def setUp(self):
        use_language(self, "en")
        self.tmp = tempfile.mkdtemp()
        snapshot(self.tmp)

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def path(self, rel):
        return os.path.join(self.tmp, rel)

    def edit(self, rel, fn):
        p = self.path(rel)
        with open(p, encoding="utf-8") as f:
            s = f.read()
        t = fn(s)
        self.assertNotEqual(s, t, f"the edit changed nothing in {rel}")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)

    def guide(self, g="languages/cobol.md"):
        return sg.read(self.path(f"lessons/study-guides/{g}"))

    def problems(self, g="languages/cobol.md"):
        return [p for p in sg.check_guide(g, self.guide(g), self.tmp)]

    def edit_guide(self, fn, g="languages/cobol.md"):
        self.edit(f"lessons/study-guides/{g}", fn)

    def assertProblem(self, text, g="languages/cobol.md"):
        ps = self.problems(g)
        self.assertTrue(any(text in p for p in ps), f"expected a problem containing {text!r}; got {ps}")

    def test_the_copy_starts_clean(self):
        self.assertEqual(sg.check_all(self.tmp), [])

    def test_a_drifted_diagram_is_caught(self):
        self.edit_guide(lambda s: s.replace("A[\"SET-UP, OPEN-SCRIPT", "A[\"SET UP, OPEN SCRIPT", 1))
        self.assertProblem("differs from its canonical source")

    def test_a_diagram_without_accessibility_text_is_caught(self):
        self.edit_guide(lambda s: re.sub(r"^\s*accDescr:.*\n", "", s, count=1, flags=re.M))
        self.assertProblem("needs 'accDescr:'")
        self.edit_guide(lambda s: re.sub(r"^\s*accTitle:.*\n", "", s, count=1, flags=re.M))
        self.assertProblem("needs 'accTitle:'")

    def test_a_diagram_without_provenance_is_caught(self):
        self.edit_guide(lambda s: re.sub(r"<!-- diagram-source: [^>]*-->\n", "", s, count=1))
        self.assertProblem("needs the line before it")

    def test_a_diagram_copied_from_a_generated_file_is_caught(self):
        self.edit_guide(lambda s: s.replace("diagram-source: src/cobol/README.md#program-flow", "diagram-source: lessons/languages/cobol.md#block-1", 1))
        self.assertProblem("never generated files")

    def test_a_new_diagram_needs_an_allowed_kind(self):
        self.edit_guide(lambda s: s.replace("diagram-source: src/cobol/README.md#program-flow", "diagram-new: pretty-picture - because", 1))
        self.assertProblem("must add one of")

    def test_a_language_guide_needs_a_diagram(self):
        self.edit_guide(lambda s: re.sub(r"<!-- diagram-source:.*?```mermaid\n.*?\n```\n", "", s, flags=re.S))
        self.assertProblem("at least one diagram")

    def test_a_missing_expected_flow_is_caught(self):
        self.edit_guide(lambda s: re.sub(r"<!-- diagram-source: src/cobol-weird/README.md#program-flow -->\n\n```mermaid\n.*?\n```\n", "", s, flags=re.S))
        self.assertProblem("must reuse the Program Flow diagram of src/cobol-weird")

    def test_placeholder_text_is_caught(self):
        for word in ("TODO", "TBD", "lorem ipsum"):
            self.edit_guide(lambda s, w=word: s.replace("## Further reading\n", f"## Further reading\n\n{w}: fill this in.\n", 1))
            self.assertProblem("placeholder text")
            self.edit_guide(lambda s, w=word: s.replace(f"{w}: fill this in.\n\n", "", 1))

    def test_an_empty_required_section_is_caught(self):
        self.edit_guide(lambda s: re.sub(r"(## Self-check\n).*?(\n## Further reading)", r"\1\nNothing.\n\2", s, flags=re.S))
        self.assertProblem("section 'Self-check' is empty or too short")

    def test_a_missing_or_reordered_section_is_caught(self):
        self.edit_guide(lambda s: s.replace("## Trace one run\n", "## Trace\n", 1))
        self.assertProblem("exactly the template")

    def test_the_title_must_say_study_guide(self):
        self.edit_guide(lambda s: s.replace("# COBOL study guide", "# COBOL notes", 1))
        self.assertProblem("# <Topic> study guide")

    def test_the_safety_model_is_required(self):
        self.edit_guide(lambda s: s.replace("DEMO ONLY", "demo", -1))
        self.assertProblem("safety model")

    def test_shared_challenge_paragraph_must_use_standard_wording(self):
        self.edit_guide(lambda s: s.replace("first card that takes the total over 40", "card that makes the total exceed 40", 1))
        self.assertProblem("must start with the standard paragraph")

    def test_exactly_40_must_be_stated(self):
        self.edit_guide(lambda s: s.replace("exactly 40", "forty", -1))
        self.assertProblem("exactly 40")

    def test_the_five_questions_and_the_four_self_check_questions_are_required(self):
        self.edit_guide(lambda s: s.replace("**What stops it.**", "**Stopping.**", 1))
        self.assertProblem("**What stops it.**")
        self.edit_guide(lambda s: s.replace("**Evidence.**", "**Proof.**", 1))
        self.assertProblem("**Evidence.**")

    def test_a_link_to_a_missing_file_or_heading_is_caught(self):
        self.edit_guide(lambda s: s.replace("(../../exercises.md#a1-read-the-rows-verified)", "(../../exercises.md#a1-no-such-heading)", 1))
        self.assertProblem("missing heading")
        self.edit_guide(lambda s: s.replace("(forth.md)", "(nowhere.md)", 1))
        self.assertProblem("missing file")

    def test_a_source_line_anchor_out_of_range_is_caught(self):
        self.edit_guide(lambda s: s.replace("timecards.cob#L93)", "timecards.cob#L9999)", 1))
        self.assertProblem("out of range")

    def test_a_line_link_whose_text_and_anchor_disagree_is_caught(self):
        self.edit_guide(lambda s: s.replace("[L93](../../../src/cobol/timecards.cob#L93)", "[L93](../../../src/cobol/timecards.cob#L94)", 1))
        self.assertProblem("the link text says L93 but the anchor is #L94")

    def test_an_external_host_must_be_on_the_allowlist(self):
        self.edit_guide(lambda s: s.replace("## Further reading\n", "## Further reading\n\n- [Blog](https://example.com/a-blog-post) (a blog).\n", 1))
        self.assertProblem("is not in lessons/book/link-hosts.txt")

    def test_generated_markers_are_refused_in_a_guide(self):
        self.edit_guide(lambda s: s.replace("## Further reading\n", "## Further reading\n\n<!-- BEGIN GENERATED x -->\n", 1))
        self.assertProblem("BEGIN/END GENERATED")

    def test_a_guide_missing_from_the_manifest_or_the_index_is_caught(self):
        self.edit("lessons/study-guides/chapters.txt", lambda s: s.replace("languages/cobol.md\n", "", 1))
        self.assertTrue(any("chapters.txt: missing languages/cobol.md" in p for p in sg.check_set(self.tmp)))
        self.edit("lessons/study-guides/README.md", lambda s: s.replace("(languages/haskell.md)", "(languages/hask.md)", 1))
        self.assertTrue(any("the index does not link to languages/haskell.md" in p for p in sg.check_set(self.tmp)))

    def test_a_missing_guide_file_is_caught(self):
        os.remove(self.path("lessons/study-guides/languages/m4.md"))
        self.assertTrue(any("languages/m4.md: the guide does not exist" in p for p in sg.check_set(self.tmp)))

    def test_a_guide_that_is_not_planned_is_caught(self):
        with open(self.path("lessons/study-guides/languages/extra.md"), "w", encoding="utf-8") as f:
            f.write("# Extra study guide\n")
        self.assertTrue(any("not one of the planned guides" in p for p in sg.check_set(self.tmp)))

    def test_the_guides_must_stay_out_of_the_book_manifest(self):
        self.edit("lessons/book/chapters.txt", lambda s: s + "study-guides/languages/cobol.md\n")
        self.assertTrue(any("separate set, not book chapters" in p for p in sg.check_set(self.tmp)))

    def test_the_book_page_must_link_to_its_guide(self):
        self.edit("lessons/languages/cobol.md", lambda s: s.replace("study-guides/languages/cobol.md", "study-guides/", 1))
        self.assertTrue(any("lessons/languages/cobol.md: needs a link to study-guides/languages/cobol.md" in p for p in sg.check_set(self.tmp)))

    def test_the_index_pages_need_a_study_guides_section(self):
        self.edit("lessons/README.md", lambda s: s.replace("study-guides/README.md", "study-guides/", 1))
        self.assertTrue(any("lessons/README.md: needs a Study Guides section" in p for p in sg.check_set(self.tmp)))

    def test_the_companion_edition_must_match_the_book(self):
        self.edit("lessons/study-guides/metadata.yaml", lambda s: s.replace("companion-to: \"", "companion-to: \"An older edition of ", 1))     # any language: the title no longer matches the book's
        self.assertTrue(any("companion-to must equal the book title" in p for p in sg.check_set(self.tmp)))


# ---- The Spanish contract. The words below are written out on purpose (not read from the catalog), so a change to the catalog
# ---- that drifts from the glossary (translation/glossary.es.yaml) or from the frozen timecard wording fails here.

ES_SECTIONS = ["Para qué sirve esta guía", "Antes de empezar", "El reto compartido", "La máquina que hay que identificar",
               "Traza una ejecución", "Compara los diseños ordinarios y los raros", "Qué demuestran los ejercicios",
               "Modos de fallo, costos y límites", "Conexiones a lo largo del repositorio", "Autoevaluación", "Lecturas adicionales"]
ES_SHARED = ("La [especificación del reto](../../intro.md#qué-hace-el-reto) pide tarjetas con una categoría y de 10 a 19 horas enteras. "
             "Las categorías se repiten en ciclo: `Meetings`, `Coding`, `Debugging` y `Learning`. Suma las horas de cada tarjeta al total "
             "acumulado. Detente cuando el total pasa de 40. Conserva la **primera tarjeta con la que el total pasa de 40**. Un total de "
             "exactamente 40 continúa. Cuatro tarjetas de 10 horas necesitan una quinta tarjeta, de la categoría `Meetings`. Las "
             "ejecuciones conformes tienen de 3 a 5 tarjetas y un total de 41 a 59 horas.")
ES_FIVE = ["Qué se repite.", "Dónde vive el estado.", "Qué hace avanzar el paso siguiente.", "Qué lo detiene.", "Qué confirma."]
ES_FOUR = ["Traza.", "Explica.", "Transfiere.", "Evidencia."]
FILL = "Este texto de relleno tiene bastantes palabras para superar el mínimo de quince palabras que exige la revisión de cada sección."


def spanish_guide():
    """A minimal guide that satisfies every rule in Spanish (it uses a name outside the planned list, so no diagram is required)."""
    bodies = {i: FILL for i in range(11)}
    bodies[1] = ("**Modelo de seguridad.** Todos los datos son ficticios (**DEMO ONLY**). Lee el código y ejecútalo primero en un entorno "
                 "aislado (*sandbox*).\n\n**Regla de predicción.** Predice el resultado antes de cada ejecución. " + FILL)
    bodies[2] = ES_SHARED + "\n\n" + FILL
    bodies[3] = "\n\n".join(f"**{q}** {FILL}" for q in ES_FIVE)
    bodies[6] = "Practica con `exercises.md#a1-lee-las-filas`. Este comportamiento es garantizado por el lenguaje. " + FILL
    bodies[9] = "\n\n".join(f"**{q}** {FILL}" for q in ES_FOUR)
    out = ["# Guía de estudio de Prueba", ""]
    for i, title in enumerate(ES_SECTIONS):
        out += [f"## {title}", "", bodies[i], ""]
    return "\n".join(out)


class SpanishContract(unittest.TestCase):
    GOOD = spanish_guide()

    @classmethod
    def setUpClass(cls):
        # A scratch repo whose intro.md already has the Spanish heading the shared paragraph links to (the real intro.md is
        # still English). The checks also read lessons/book/link-hosts.txt from the repo they are given.
        cls.repo = tempfile.mkdtemp()
        os.makedirs(os.path.join(cls.repo, "lessons", "book"))
        os.makedirs(os.path.join(cls.repo, "lessons", "study-guides", "concepts"))
        shutil.copy(os.path.join(REPO, "lessons", "book", "link-hosts.txt"), os.path.join(cls.repo, "lessons", "book", "link-hosts.txt"))
        with open(os.path.join(cls.repo, "lessons", "intro.md"), "w", encoding="utf-8") as f:
            f.write("# Introducción\n\n## Qué hace el reto\n\nTexto.\n")

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.repo)

    def setUp(self):
        use_language(self, "es")

    def problems(self, text):
        return sg.check_guide("concepts/prueba.md", text, self.repo)

    def assertProblem(self, text, expect):
        ps = self.problems(text)
        self.assertTrue(any(expect in p for p in ps), f"expected a problem containing {expect!r}; got {ps}")

    def broken(self, old, new, expect, count=1):
        self.assertIn(old, self.GOOD, "the test edit would change nothing")
        self.assertProblem(self.GOOD.replace(old, new, count), expect)

    def test_the_spanish_words_are_the_glossary_words(self):
        self.assertEqual(sg.SECTIONS, ES_SECTIONS)
        self.assertEqual(sg.FIVE_QUESTIONS, ES_FIVE)
        self.assertEqual(sg.FOUR_QUESTIONS, ES_FOUR)
        self.assertEqual(sg.SHARED_CHALLENGE, ES_SHARED)
        self.assertEqual(sg.ASSURANCE_LABELS, ("garantizado", "permitido por la implementación", "aprovechado por accidente"))
        self.assertEqual((sg.TITLE_PREFIX, sg.TITLE_SUFFIX), ("Guía de estudio de ", ""))

    def test_the_frozen_timecard_wording_is_in_the_shared_paragraph(self):
        for must in ("pasa de 40", "un total de exactamente 40 continúa", "de 3 a 5 tarjetas", "de 41 a 59 horas"):
            self.assertIn(must, sg.SHARED_CHALLENGE.lower())
        for banned in ("hasta 40", "a partir de 40", "40 o más", "al menos 40", "alcanza 40", "llega a 40", "desafío", "ficha"):
            self.assertNotIn(banned, sg.SHARED_CHALLENGE)
        for category in ("Meetings", "Coding", "Debugging", "Learning"):
            self.assertIn(f"`{category}`", sg.SHARED_CHALLENGE)    # the four categories are data: always in code font, never translated

    def test_the_catalog_paragraph_links_to_the_intro_heading_it_names(self):
        self.assertEqual(sg.CHALLENGE_HEADING, "Qué hace el reto")
        self.assertIn("(../../intro.md#qué-hace-el-reto)", sg.SHARED_CHALLENGE)
        self.assertEqual(sg.slug("Qué hace el reto"), "qué-hace-el-reto")

    def test_a_complete_spanish_guide_has_no_problems(self):
        self.assertEqual(self.problems(self.GOOD), [])

    def test_a_guide_written_with_decomposed_accents_is_still_accepted(self):
        nfd = lambda s: unicodedata.normalize("NFD", s)
        decomposed = nfd(self.GOOD)
        self.assertNotEqual(decomposed, self.GOOD)
        # the words are compared in one normal form; a link anchor must stay NFC (a different byte string would not work on GitHub)
        self.assertEqual(self.problems(decomposed.replace(nfd("#qué-hace-el-reto"), "#qué-hace-el-reto")), [])
        self.assertTrue(any("missing heading" in p for p in self.problems(decomposed)))
        # slug() stays a verbatim copy of build.py's (tools/test_anchors.py checks that), so it does not normalize: headings must be NFC
        self.assertNotEqual(sg.slug(nfd("Qué hace el reto")), sg.slug("Qué hace el reto"))

    def test_accented_words_count_once_each(self):
        self.assertEqual(sg.words("información útil sección"), 3)
        self.assertEqual(sg.words("```\nnot counted\n```\n`code` ya"), 2)

    def test_the_title_must_use_the_spanish_form(self):
        self.broken("# Guía de estudio de Prueba", "# Prueba study guide", "# Guía de estudio de <Topic>")
        self.broken("# Guía de estudio de Prueba", "# Guía de estudio de ", "# Guía de estudio de <Topic>")
        self.broken("# Guía de estudio de Prueba", "# Notas de Prueba", "# Guía de estudio de <Topic>")

    def test_each_of_the_eleven_headings_is_required(self):
        for title in ES_SECTIONS:
            with self.subTest(title):
                self.broken(f"## {title}\n", "## Otro título\n", "exactly the template")

    def test_english_headings_are_refused_in_spanish(self):
        self.broken("## Antes de empezar\n", "## Before you begin\n", "exactly the template")

    def test_a_reordered_section_is_caught(self):
        swapped = self.GOOD.replace("## Autoevaluación", "## @@").replace("## Lecturas adicionales", "## Autoevaluación").replace("## @@", "## Lecturas adicionales")
        self.assertProblem(swapped, "the order is wrong")

    def test_the_shared_paragraph_must_use_the_frozen_wording(self):
        for old, new in (("pasa de 40. Conserva", "llega a 40. Conserva"), ("Detente cuando", "Para cuando"),
                         ("un total de 41 a 59 horas", "un total de 41 a 60 horas"), ("`Debugging`", "Debugging")):
            with self.subTest(old):
                self.broken(old, new, "must start with the standard paragraph")

    def test_exactly_40_must_be_stated(self):
        self.broken("exactamente 40 continúa", "cuarenta continúa", "exactly 40 continues")
        # the paragraph itself is also wrong then, so both problems are reported
        self.broken("exactamente 40 continúa", "cuarenta continúa", "standard paragraph")

    def test_each_of_the_five_and_four_questions_is_required(self):
        for q in ES_FIVE:
            with self.subTest(q):
                self.broken(f"**{q}**", "**Otra cosa.**", f"**{q}**")
        for q in ES_FOUR:
            with self.subTest(q):
                self.broken(f"**{q}**", "**Otra cosa.**", f"**{q}**")

    def test_the_english_question_labels_are_refused_in_spanish(self):
        self.broken("**Qué lo detiene.**", "**What stops it.**", "**Qué lo detiene.**")

    def test_the_safety_model_needs_demo_only_and_the_sandbox_word(self):
        self.broken("**DEMO ONLY**", "**datos de prueba**", "safety model")
        self.broken("entorno aislado", "entorno", "safety model")

    def test_the_reader_must_be_asked_to_predict(self):
        for word in ("Predice", "predicción"):
            text = self.GOOD.replace(word, "Anota")
            self.assertNotEqual(text, self.GOOD)
        no_predict = self.GOOD.replace("**Regla de predicción.** Predice el resultado antes de cada ejecución. ", "")
        self.assertNotEqual(no_predict, self.GOOD)
        self.assertProblem(no_predict, "predict")
        for ok in ("predecir", "predigas", "una predicción"):
            self.assertEqual(self.problems(self.GOOD.replace("Predice", ok)), [], ok)

    def test_an_assurance_label_is_required(self):
        self.broken("garantizado", "seguro", "must label behavior as garantizado")
        for label in ("permitido por la implementación", "aprovechado por accidente"):
            self.assertEqual(self.problems(self.GOOD.replace("garantizado", label)), [], label)

    def test_the_exercise_link_is_still_required(self):
        self.broken("exercises.md#a1-lee-las-filas", "ejercicios", "verified exercise")

    def test_spanish_placeholder_text_is_caught(self):
        for words in ("TODO", "por escribir", "Por completar", "marcador de posición", "lorem ipsum"):
            with self.subTest(words):
                self.assertProblem(self.GOOD.replace("## Lecturas adicionales\n", f"## Lecturas adicionales\n\n{words}.\n"), "placeholder text")

    def test_a_short_section_with_accented_words_is_caught(self):
        self.broken(FILL + "\n\n## Antes", "Poco.\n\n## Antes", "section 'Para qué sirve esta guía' is empty or too short")

    def test_generated_markers_are_refused(self):
        self.broken("## Lecturas adicionales\n", "## Lecturas adicionales\n\n<!-- BEGIN GENERATED x -->\n", "BEGIN/END GENERATED")

    def test_the_english_guides_are_refused_in_spanish(self):
        text = sg.read(os.path.join(sg.GUIDES, "languages", "cobol.md"))
        ps = sg.check_guide("languages/cobol.md", text)
        self.assertTrue(any("exactly the template" in p for p in ps), ps)
        self.assertTrue(any("# Guía de estudio de <Topic>" in p for p in ps), ps)

    def test_diagrams_follow_the_language(self):
        from_diagrams = sg.diagrams
        self.assertEqual(from_diagrams.SECTION, "Flujo del programa")
        sg.set_language("en")
        self.assertEqual(from_diagrams.SECTION, "Program Flow")
        sg.set_language("es")
        self.assertEqual(from_diagrams.SECTION, "Flujo del programa")


class EnglishContract(unittest.TestCase):
    """The English words are exactly what they were before they moved into the catalog (guards the extraction)."""

    def setUp(self):
        use_language(self, "en")

    def test_the_english_words_are_unchanged(self):
        self.assertEqual(sg.SECTIONS, ["What this guide is for", "Before you begin", "The shared challenge", "The machine to identify",
                                       "Trace one run", "Compare the ordinary and weird designs", "What the exercises demonstrate",
                                       "Failure modes, costs and boundaries", "Connections across the repository", "Self-check",
                                       "Further reading"])
        self.assertEqual(sg.FIVE_QUESTIONS, ["What repeats.", "Where state lives.", "What advances the next step.", "What stops it.", "What commits."])
        self.assertEqual(sg.FOUR_QUESTIONS, ["Trace.", "Explain.", "Transfer.", "Evidence."])
        self.assertEqual(sg.ASSURANCE_LABELS, ("guaranteed", "implementation-permitted", "accidentally exploited"))
        self.assertEqual((sg.TITLE_PREFIX, sg.TITLE_SUFFIX), ("", " study guide"))
        self.assertEqual(sg.SHARED_CHALLENGE, (
            "The [challenge specification](../../intro.md#what-the-challenge-does) calls for cards with a category and 10 "
            "to 19 whole hours. Categories cycle through Meetings, Coding, Debugging and Learning. Add each card's hours "
            "to the running total. Stop when the total passes 40. Keep the **first card that takes the total over 40**. A "
            "total of exactly 40 continues. Four 10-hour cards need a fifth card, in the Meetings category. Conforming "
            "runs finish with 3 to 5 cards and a total of 41 to 59 hours."))

    def test_the_spanish_guide_is_refused_in_english(self):
        ps = sg.check_guide("concepts/prueba.md", SpanishContract.GOOD)
        self.assertTrue(any("exactly the template" in p for p in ps), ps)

    def test_the_shared_paragraph_has_one_source_the_catalog(self):
        with open(os.path.join(HERE, "study_guides.py"), encoding="utf-8") as f:
            source = f.read()
        self.assertNotIn("Keep the **first card", source)
        self.assertNotIn("Conserva la **primera", source)


class LanguageSwitch(unittest.TestCase):
    def setUp(self):
        use_language(self, "es")

    def test_a_missing_catalog_key_fails_loudly_and_changes_nothing(self):
        real = sg.catalog.load

        def broken(lang, *a, **kw):
            cat = real(lang, *a, **kw)
            flat = dict(cat.flat)
            del flat["study_guides.lead_in_four.4"]
            return sg.catalog.Catalog(lang, flat)

        with mock.patch.object(sg.catalog, "load", broken):
            with self.assertRaises(sg.catalog.MissingKeyError):
                sg.set_language("en")
        self.assertEqual(sg.LANG, "es")
        self.assertEqual(sg.SECTIONS[0], "Para qué sirve esta guía")
        self.assertEqual(sg.diagrams.SECTION, "Flujo del programa")

    def test_an_unknown_language_fails_loudly(self):
        with self.assertRaises(sg.catalog.CatalogError):
            sg.set_language("xx")
        self.assertEqual(sg.LANG, "es")

    def test_a_title_without_the_topic_is_refused(self):
        real = sg.catalog.load

        def no_topic(lang, *a, **kw):
            cat = real(lang, *a, **kw)
            flat = dict(cat.flat)
            flat["study_guides.title"] = "Guía de estudio"
            return sg.catalog.Catalog(lang, flat)

        with mock.patch.object(sg.catalog, "load", no_topic):
            with self.assertRaises(sg.catalog.CatalogError):
                sg.set_language("es")
        self.assertEqual(sg.TITLE_PREFIX, "Guía de estudio de ")


if __name__ == "__main__":
    unittest.main(verbosity=1)
