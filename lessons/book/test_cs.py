"""Tests for the metadata rules in cs.py: what grounds a concept, what the linter refuses, and that the output is stable.

    python lessons/book/test_cs.py

Each test copies the real sources into a scratch folder and breaks one thing, so the rules are tested against the real data
and nothing in the repository is touched. Needs only the Python standard library.
"""
import os, posixpath, re, shutil, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cs

REPO = cs.REPO
LAY = cs.catalog.checkout()         # the names the real files have in this checkout (identity in the English repository)
LANGUAGE = os.environ.get("BOOK_LANG", "en")
ENGLISH_LAYER = LAY.path("lessons/intro.md") == "lessons/intro.md"      # path-ok: probe for the English layout
english_only = unittest.skipUnless(ENGLISH_LAYER, "edits and reads English text under the English names: it runs in the English layer (tools/scratch_proof.py --tests)")
ES_LAY = cs.catalog.load("es", layout="spanish")      # the Spanish edition's names, whatever this checkout is

def snapshot(dest):
    """Copy what cs.Model reads (the entries' READMEs and the whole lessons tree, minus build output) and point cs at it.
    The copy is laid out in the ENGLISH names whatever this checkout calls its files: the tests below name the English path
    as the key (`cs.P`, `edit`), and TestRenamedLayout moves the copy into the Spanish names itself."""
    real = os.path.join(REPO, "lessons")
    for root, dirs, names in os.walk(real):
        dirs[:] = [d for d in dirs if d not in ("out", "__pycache__", "node_modules")]
        for n in names:
            rel = os.path.relpath(os.path.join(root, n), REPO).replace(os.sep, "/")
            target = os.path.join(dest, *LAY.english(rel).split("/"))
            os.makedirs(os.path.dirname(target), exist_ok=True)
            if n.endswith((".md", ".txt")):         # the references inside move with the files
                with open(os.path.join(root, n), encoding="utf-8", newline="") as f, open(target, "w", encoding="utf-8", newline="") as g:
                    g.write(LAY.english_text(f.read()))
            else:
                shutil.copy(os.path.join(root, n), target)
    for d in os.listdir(os.path.join(REPO, "src")):
        r = os.path.join(REPO, "src", d, "README.md")
        if os.path.isfile(r):
            os.makedirs(os.path.join(dest, "src", d))
            with open(r, encoding="utf-8", newline="") as f, open(os.path.join(dest, "src", d, "README.md"), "w", encoding="utf-8", newline="") as g:
                g.write(re.sub(r'^(lesson: ")([^"]+)', lambda m: m.group(1) + LAY.english_text(m.group(2)), f.read(), flags=re.M))
    cs.REPO, cs.SRC = dest, os.path.join(dest, "src")
    cs.LESSONS, cs.CSSRC, cs.CSOUT = os.path.join(dest, "lessons"), os.path.join(dest, "lessons", "cs-source"), os.path.join(dest, "lessons", cs.CAT.lessons_path("cs"))

class Base(unittest.TestCase):
    NAMES = "english"       # the scratch copy has the English names (tools/tooling_paths.py skips classes that say so)
    LANG = LANGUAGE         # the words the scratch copy is read in; a test may switch with cs.set_language
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.saved = (cs.REPO, cs.SRC, cs.LESSONS, cs.CSSRC, cs.CSOUT, cs.CAT.lang)
        self.saved_override = cs.catalog.LAYOUT_OVERRIDE
        cs.catalog.LAYOUT_OVERRIDE = "english"      # the scratch copy has the English names, in every language
        cs.set_language(self.LANG)
        snapshot(self.tmp)
    def tearDown(self):
        cs.catalog.LAYOUT_OVERRIDE = self.saved_override
        cs.REPO, cs.SRC, cs.LESSONS, cs.CSSRC, cs.CSOUT, lang = self.saved
        cs.set_language(lang)
        cs.CSOUT = self.saved[4]
        shutil.rmtree(self.tmp)
    def edit(self, rel, fn):
        p = os.path.join(self.tmp, rel)
        with open(p, encoding="utf-8") as f:
            s = f.read()
        t = fn(s)
        self.assertNotEqual(s, t, f"the edit changed nothing in {rel}")
        with open(p, "w", encoding="utf-8") as f:
            f.write(t)
    def problems(self):
        return list(cs.Model().problems)

class TestRepositoryAsItIs(Base):
    def test_no_problems_and_no_orphans(self):
        m = cs.Model()
        self.assertEqual(list(m.problems), [])
        lines, bad = cs.orphan_report(m)
        self.assertEqual(bad, 0, "\n".join(lines))

    def test_output_is_deterministic(self):
        a, b = cs.generate_all(cs.Model()), cs.generate_all(cs.Model())
        self.assertEqual(a, b)

    def test_generated_text_never_says_a_concept_is_unused(self):
        for rel, text in cs.generate_all(cs.Model()).items():
            self.assertNotIn("no entry uses this yet", text.lower(), rel)

    def test_every_new_entry_is_in_the_by_language_by_pattern_and_concept_indexes(self):
        files = cs.generate_all(cs.Model())
        for d in ("tar-gnu", "tar-gnu-weird", "ed-weird", "ex-weird", "javascript", "javascript-weird"):
            self.assertIn(f"`{d}`", files["index.md"], d)
            self.assertIn(f"src/{d}/README.md", files["cs/09-comparative-case-studies.md"], d)
            with open(os.path.join(cs.LESSONS, cs.P("languages"), "README.md"), encoding="utf-8") as f:
                self.assertIn(f"`{d}`", f.read(), f"{d} is missing from the By language page")
            self.assertIn(f"src/{d}/README.md", cs.generate_blocks(cs.Model(), "patterns.md"), f"{d} is missing from the By solution patterns page")

    def test_teaches_line_matches_the_frontmatter_for_every_entry(self):
        m = cs.Model()
        for d, e in m.entries.items():
            hit = cs.teaches_line(e["_body"])
            if hit:
                self.assertEqual(hit.group(1).strip(), e["teaches"], d)

    @english_only
    def test_the_two_cross_cutting_claims_are_true(self):
        """applies-to: all is a statement about every entry, so check it. (sandbox: a Dockerfile or a Windows Sandbox section;
        code-review: a How the stunt works section.)"""
        m = cs.Model()
        for d in m.entries:
            with open(os.path.join(cs.SRC, d, "README.md"), encoding="utf-8") as f:
                readme = f.read()
            self.assertIn("\n## How the stunt works\n", readme, d)
            has_docker = os.path.isfile(os.path.join(REPO, "src", d, "Dockerfile"))
            self.assertTrue(has_docker or "\n## Run it in Windows Sandbox" in readme, d)

class TestTheLintersRefuse(Base):
    LANG = "en"             # the stale-wording and message checks below are about the English words
    def test_an_ungrounded_concept(self):
        self.edit("lessons/cs-source/concepts/sandbox.md", lambda s: re.sub(r"applies-to: all\napplies-because: .*\n", "", s))
        self.assertTrue(any("sandbox" in p and "no entry demonstrates" in p for p in self.problems()), self.problems())

    def test_a_cross_cutting_claim_needs_its_reason(self):
        self.edit("lessons/cs-source/concepts/sandbox.md", lambda s: re.sub(r"applies-because: .*\n", "applies-because: \"short\"\n", s))
        self.assertTrue(any("applies-because" in p for p in self.problems()), self.problems())

    def test_a_bad_applies_to_value(self):
        self.edit("lessons/cs-source/concepts/sandbox.md", lambda s: s.replace("applies-to: all", "applies-to: some"))
        self.assertTrue(any("applies-to must be one of" in p for p in self.problems()), self.problems())

    @english_only
    def test_an_exercise_link_that_does_not_exist(self):
        self.edit("lessons/cs-source/concepts/trojan-source.md", lambda s: s.replace("#f2-trojan-source-hide-a-character-then-find-it-verified", "#no-such-exercise"))
        self.assertTrue(any("trojan-source" in p and "no heading with that anchor" in p for p in self.problems()), self.problems())

    def test_an_unknown_concept_in_analogies(self):
        self.edit("src/javascript-weird/README.md", lambda s: s.replace("analogies: [", "analogies: [no-such-concept, ", 1))
        self.assertTrue(any("no-such-concept" in p for p in self.problems()), self.problems())

    def test_a_concept_cannot_be_a_tag_and_an_analogy_of_one_entry(self):
        self.edit("src/javascript-weird/README.md", lambda s: s.replace("analogies: [", "analogies: [closure, ", 1))
        self.assertTrue(any("both a tag" in p for p in self.problems()), self.problems())

    def test_stale_wording_cannot_come_back(self):
        self.edit("lessons/cs-source/concepts/closure.md", lambda s: s + "\nIn this repo: no entry uses this yet; it is background for the others.\n")
        self.assertTrue(any("stale wording" in p for p in self.problems()), self.problems())

    def test_removing_the_last_demonstration_leaves_only_an_analogy_which_is_still_allowed_but_visible(self):
        """continuation has analogies and counterexamples only: the report must say so, and not call it demonstrated."""
        lines, bad = cs.orphan_report(cs.Model())
        text = "\n".join(lines)
        self.assertIn("only an analogy or counterexample", text)
        self.assertRegex(text, r"continuation \(.*analogy.*\)")
        self.assertEqual(bad, 0)

    def test_an_unknown_tag(self):
        self.edit("src/tar-gnu/README.md", lambda s: s.replace("tags: [", "tags: [not-a-concept, ", 1))
        self.assertTrue(any("not-a-concept" in p for p in self.problems()), self.problems())

    # English words over the real files (this class reads in English); the Spanish contract is TestSpanishTeachesContract.
    @english_only
    def test_teaches_needs_a_that_clause(self):
        self.edit("src/tar-gnu/README.md", lambda s: s.replace('teaches: "that a', 'teaches: "A', 1))
        self.assertTrue(any("'teaches' must start" in p for p in self.problems()), self.problems())

    @english_only
    def test_a_missing_teaches_match(self):
        self.edit("src/tar-gnu/README.md", lambda s: s.replace("**Teaches you:** that a tar archive", "**Teaches you:** that a TAR archive", 1))
        self.assertTrue(any("'teaches' differs" in p for p in self.problems()), self.problems())

    def test_every_entry_must_name_its_machine_and_its_state(self):
        """The comparative tables must never show a blank cell. An ordinary entry says so in words ("Ordinary: ...")."""
        self.edit("src/awk/README.md", lambda s: re.sub(r"^machine: .*\n", "", s, count=1, flags=re.M))
        self.assertTrue(any("awk" in p and "missing required key 'machine'" in p for p in self.problems()), self.problems())
        self.edit("src/cobol/README.md", lambda s: re.sub(r"^state: .*\n", "", s, count=1, flags=re.M))
        self.assertTrue(any("cobol" in p and "missing required key 'state'" in p for p in self.problems()), self.problems())

class TestEnglishWordsAreUnchanged(Base):
    """The catalog must give back exactly the literals the generator used before it read the catalog."""
    LANG = "en"
    def test_assurance_labels(self):
        self.assertEqual(cs.ASSURANCE_LABELS, {"guaranteed": "guaranteed", "implementation-permitted": "implementation-permitted",
                                               "accidentally-exploited": "accidentally exploited"})
    def test_banner_and_stale_phrases(self):
        self.assertEqual(cs.BANNER, "<!-- GENERATED by lessons/book/build.py from lessons/cs-source/ and the entries' frontmatter. "
                                    "Do not edit; edit the sources and run build.py. -->")
        self.assertEqual(cs.STALE_PHRASES, ("no entry uses this yet", "it is background for the others"))
    def test_table_headers_and_lead_ins(self):
        m = cs.Model()
        files = cs.generate_all(m)
        self.assertIn("| Language / tool | The machine it really is | Where the program's state lives | Lesson |", cs.generate_blocks(m, "goals.md"))
        self.assertTrue(cs.tbl_glance(m, cs.Links(m, "")).startswith("| Entry | Languages | Kind | What plays the loop | Evaluation | Assurance | Pairs with |\n"))
        self.assertTrue(any("**In this repo:**" in t for r, t in files.items() if r.startswith("cs/0")))
        self.assertIn("## Concept index", files["cs/README.md"])
        self.assertIn("## Index of roles: what plays the loop", files["index.md"])
    def test_the_challenge_anchor_is_the_one_the_book_has_always_used(self):
        self.assertEqual(cs.CHALLENGE_ANCHOR, "what-the-challenge-does")

class TestSpanishTeachesContract(Base):
    """The `teaches:` contract in Spanish (P3C-003): the prefix "que" and the printed label "Te enseña:" come from the catalog,
    so a Spanish entry is held to the same rules as an English one. The scratch README of LinqChallenge1 is given Spanish
    front matter and a Spanish lead-in line (whatever language the real file is in), so the tests do not depend on how much of
    the book is translated."""
    LANG = "es"
    README = "src/LinqChallenge1/README.md"
    FRONT = "que una cadena de métodos de LINQ puede expresar el programa completo."

    def setUp(self):
        super().setUp()
        def spanish(s):
            s = re.sub(r'^teaches: ".*"$', lambda m: 'teaches: "%s"' % self.FRONT, s, count=1, flags=re.M)
            return re.sub(r"^\*\*(?:Teaches you:|Te enseña:)\*\* .*$", lambda m: "**Te enseña:** " + self.FRONT, s, count=1, flags=re.M)
        path = os.path.join(self.tmp, self.README)       # not self.edit: the real file may already be exactly this
        with open(path, encoding="utf-8") as f:
            text = f.read()
        with open(path, "w", encoding="utf-8") as f:
            f.write(spanish(text))
    def teaches_problems(self):
        return [p for p in self.problems() if p.startswith("src/LinqChallenge1/") and "teaches" in p]
    def test_the_words_are_the_catalog_words(self):
        self.assertEqual((cs.W["teaches_prefix"], cs.W["teaches_label"]), ("que", "Te enseña:"))
    def test_a_spanish_entry_that_follows_the_contract_is_clean(self):
        self.assertEqual(self.teaches_problems(), [])
        self.assertIsNotNone(cs.teaches_line(cs.Model().entries["LinqChallenge1"]["_body"]))     # the line is found, so it was compared
    def test_the_english_label_is_not_the_spanish_label(self):
        self.assertIsNone(cs.teaches_line("**Teaches you:** that a thing."))
        self.assertIsNotNone(cs.teaches_line("**Te enseña:** que una cosa."))
        cs.set_language("en")
        self.assertIsNotNone(cs.teaches_line("**Teaches you:** that a thing."))
        self.assertIsNone(cs.teaches_line("**Te enseña:** que una cosa."))
    def test_a_spanish_teaches_without_que_is_refused(self):
        self.edit(self.README, lambda s: s.replace('teaches: "que una', 'teaches: "una', 1))
        self.assertTrue(any("must start with a lowercase 'que' clause" in p for p in self.teaches_problems()), self.teaches_problems())
    def test_an_english_that_does_not_pass_in_spanish(self):
        self.edit(self.README, lambda s: s.replace('teaches: "que una', 'teaches: "that a', 1))
        self.assertTrue(any("'que'" in p for p in self.teaches_problems()), self.teaches_problems())
    def test_regression_line_3_differs_from_line_19(self):
        """The mismatch the first review found in LinqChallenge1 ("el programa completo" against "todo el programa")."""
        self.edit(self.README, lambda s: s.replace("**Te enseña:** " + self.FRONT, "**Te enseña:** " + self.FRONT.replace("el programa completo", "todo el programa"), 1))
        self.assertTrue(any("'teaches' differs from the README's **Te enseña:** line" in p for p in self.teaches_problems()), self.teaches_problems())
    def test_the_english_lead_in_is_not_compared_in_spanish(self):
        """In Spanish the line "**Teaches you:**" is not the contract line (it is an untranslated leftover): nothing is compared."""
        self.edit(self.README, lambda s: s.replace("**Te enseña:** ", "**Teaches you:** that something else. ", 1))
        self.assertEqual(self.teaches_problems(), [])

class TestSpanishWords(Base):
    """BOOK_LANG=es over the English sources: every word the generator adds is Spanish, the shape and the links do not change."""
    LANG = "en"
    def setUp(self):
        super().setUp()
        m = cs.Model()
        self.en = cs.generate_all(m)
        self.en_anchor, self.en_flow = cs.CHALLENGE_ANCHOR, cs.slug(cs.diagrams.SECTION)
        for rel in cs.block_files():       # generate_all lists a block page only when its text differs from the committed one
            self.en.setdefault(rel, cs.read(os.path.join(cs.LESSONS, rel)))
        cs.set_language("es")
        # The English READMEs have an English "## Program Flow" heading; read them with the English diagram words, so that the
        # program-flow blocks are filled and can be compared. (test_program_flow_anchor_follows_the_diagram_language covers the rest.)
        cs.diagrams.set_language("en")
        m = cs.Model()
        self.es = self.es_raw = cs.generate_all(m)
        self.es = dict(self.es)
        for rel in cs.block_files():
            self.es.setdefault(rel, cs.read(os.path.join(cs.LESSONS, rel)))
        # only the generated words: the index pages, the opener and the text between the BEGIN/END GENERATED markers
        self.generated = "\n".join([self.es["index.md"], self.es["cs/README.md"]] + [mk.group(0) for rel in cs.block_files() for mk in cs.MARK.finditer(self.es[rel])])
    def tearDown(self):
        cs.set_language("en")
        super().tearDown()

    def test_the_challenge_anchor_is_the_slug_of_the_spanish_heading(self):
        self.assertEqual((cs.LANG, cs.CHALLENGE_ANCHOR), ("es", "qué-hace-el-reto"))

    def test_assurance_labels_are_the_frozen_glossary_labels(self):
        self.assertEqual(cs.ASSURANCE_LABELS, {"guaranteed": "garantizado", "implementation-permitted": "permitido por la implementación",
                                               "accidentally-exploited": "aprovechado por accidente"})
        self.assertIn("aprovechado por accidente", "\n".join(self.es.values()))

    def test_same_files_same_line_counts_same_table_shapes(self):
        self.assertEqual(sorted(self.en), sorted(self.es))
        for rel in self.en:
            a, b = self.en[rel].split("\n"), self.es[rel].split("\n")
            self.assertEqual(len(a), len(b), rel)
            self.assertEqual([l.count(" | ") for l in a if l.startswith("|")], [l.count(" | ") for l in b if l.startswith("|")], rel)

    @english_only
    def test_links_are_the_same_apart_from_the_two_translated_anchors(self):
        link = re.compile(r"\]\(([^)\s]+)\)")
        # The English hand-written prose still links to the English anchors, so both spellings count as the same placeholder.
        def norm(t, *anchors):
            out = []
            for l in link.findall(t):
                l = ES_LAY.english_text(l)     # the Spanish catalog text names the Spanish edition's folders; the copy has the English ones
                for a, tag in zip(anchors, ("#CH", "#PF", "#CH", "#PF")):
                    l = l.replace("#" + a, tag)
                out.append(l)
            return sorted(out)
        for rel in self.en:
            self.assertEqual(norm(self.en[rel], self.en_anchor, self.en_flow), norm(self.es[rel], cs.CHALLENGE_ANCHOR, self.en_flow, self.en_anchor), rel)

    @english_only
    def test_program_flow_anchor_follows_the_diagram_language(self):
        """With the Spanish diagram words, a README whose section is '## Flujo del programa' gets a Spanish block and a Spanish anchor."""
        self.edit("src/tar-gnu/README.md", lambda s: s.replace("## Program Flow", "## Flujo del programa"))
        cs.diagrams.set_language("es")
        m = cs.Model()
        page = cs.generate_blocks(m, m.entries["tar-gnu"]["lesson"].partition("#")[0])
        self.assertIn("### Flujo del programa de `tar-gnu`", page)
        self.assertIn("/README.md#flujo-del-programa)", page)
        self.assertIn("## Cómo corre cada programa", page)
        self.assertNotIn("## How each program runs", page)

    def test_no_fixed_english_word_is_left_in_the_generated_text(self):
        text = "\n".join(self.es.values())
        for lit in ("**In this repo:**", "**Entries:**", "(analogy)", "(counterexample)", "GENERATED by"):
            self.assertNotIn(lit, text, lit)
        for lit in ("| Entry |", "| Language |", "| Lesson |", "## The chapters", "## Concept index", "# Index\n", "## Index of",
                    "Study guides", "**Language families**", "How each program runs"):
            self.assertNotIn(lit, self.generated, lit)
        for lit in ("| Entrada |", "**En este repositorio:**", "## Los capítulos", "## Índice de conceptos", "# Índice\n", "## Guías de estudio",
                    "**Familias de lenguajes**", "<!-- GENERADO por", "Qué hace de bucle"):
            self.assertIn(lit, text, lit)

    def test_enum_values_in_tables_are_data_and_stay_as_they_are(self):
        text = "\n".join(self.es.values())
        for value in ("| eager |", "| weird |"):
            self.assertIn(value, text)
        self.assertIn("| Evaluación |", text)

    def test_output_is_deterministic_in_spanish_too(self):
        self.assertEqual(self.es_raw, cs.generate_all(cs.Model()))

    def test_the_spanish_stale_phrase_is_refused_in_prose(self):
        self.edit("lessons/cs-source/concepts/closure.md", lambda s: s + "\nEn este repositorio: ninguna entrada usa esto todavía.\n")
        self.assertTrue(any("stale wording" in p and "closure" in p for p in self.problems()), self.problems())

    def test_the_english_stale_phrase_is_not_the_spanish_rule(self):
        self.edit("lessons/cs-source/concepts/closure.md", lambda s: s + "\nIn this repo: no entry uses this yet.\n")
        self.assertFalse(any("closure" in p and "stale wording" in p for p in self.problems()), self.problems())

class TestLanguageSwitchIsAtomic(unittest.TestCase):
    def tearDown(self):
        cs.set_language("en")
    def test_a_missing_key_leaves_the_old_language_in_place(self):
        cs.set_language("en")
        real = cs.catalog.load
        def broken(lang, base=cs.catalog.HERE):
            cat = real(lang, base)
            del cat.flat["cs.header.concept"]
            return cat
        cs.catalog.load = broken
        try:
            with self.assertRaises(cs.catalog.MissingKeyError) as ctx:
                cs.set_language("es")
        finally:
            cs.catalog.load = real
        self.assertIn("cs.header.concept", str(ctx.exception))
        self.assertEqual((cs.LANG, cs.diagrams.LANG, cs.W["header.concept"]), ("en", "en", "Concept"))

    def test_the_language_switch_reaches_the_diagram_words_too(self):
        cs.set_language("es")
        self.assertEqual((cs.LANG, cs.diagrams.LANG, cs.diagrams.SECTION), ("es", "es", "Flujo del programa"))
        cs.set_language("en")
        self.assertEqual((cs.LANG, cs.diagrams.LANG, cs.diagrams.SECTION), ("en", "en", "Program Flow"))

    def test_an_unknown_language_fails_loudly(self):
        with self.assertRaises(cs.catalog.CatalogError):
            cs.set_language("xx")
        self.assertEqual(cs.LANG, "en")

    def test_fill_replaces_in_one_pass(self):
        cs.set_language("en")
        self.assertEqual(cs.fill("applies_all", n="{because}", because="x"), "({because}). x")

class TestSortingAndLettersFollowSpanish(unittest.TestCase):
    def test_accents_sort_with_their_letter_and_n_tilde_follows_n(self):
        items = [("Zeta", "z"), ("Ñu", "nt"), ("Álgebra", "a1"), ("Oso", "o"), ("Nube", "n"), ("abeja", "a0")]
        self.assertEqual([l for l in cs.lettered(items).split("\n") if l and not l.startswith("**")], ["a0", "a1", "n", "nt", "o", "z"])
        letters = [l for l in cs.lettered(items).split("\n") if l.startswith("**")]
        self.assertEqual(letters, ["**A**", "**N**", "**Ñ**", "**O**", "**Z**"])
        self.assertEqual(cs.letter("Álgebra"), "A")
        self.assertEqual(cs.letter("ñandú"), "Ñ")
        self.assertEqual(cs.letter("42 cosas"), "0-9")

    def test_ascii_order_is_exactly_the_old_casefold_order(self):
        for words in (["b", "A", "a", "B"], ["Closure", "closure", "Eval"]):
            self.assertEqual(sorted(words, key=lambda w: (cs.fold(w), w)), sorted(words, key=lambda w: (w.casefold(), w)))

class TestRenamedLayout(Base):
    """Plan 5.6: the same sources in the Spanish layout (folders and files moved per the catalog) generate the same text at the
    renamed paths. The scratch copy is moved by the catalog, so a path that is still hard-coded in cs.py fails here."""

    def setUp(self):
        super().setUp()
        self.saved_cat, self.saved_csout = cs.CAT, cs.CSOUT
        flat = dict(cs.catalog.load("es").flat)         # the Spanish names, with the layout switched as P3B-005 will leave it
        flat["paths.layout"] = "spanish"
        cs.CAT = cs.catalog.Catalog("es", flat)
        files = {k[len("paths.files."):]: v for k, v in flat.items() if k.startswith("paths.files.lessons/")}
        for old, new in sorted(files.items()):
            src, dst = os.path.join(self.tmp, old), os.path.join(self.tmp, new)
            if os.path.isfile(src) and not old.endswith((".py", ".yaml")):
                os.makedirs(os.path.dirname(dst), exist_ok=True)
                shutil.move(src, dst)
        for root, dirs, names in sorted(os.walk(os.path.join(self.tmp, "lessons"), topdown=False)):
            if not dirs and not names:
                os.rmdir(root)              # a moved folder leaves no empty English twin behind
        cs.CSOUT = os.path.join(self.tmp, "lessons", cs.P("cs"))

        def respell(text):      # content references are in the layout of the edition: rewrite them like P3B-005 will
            for old, new in files.items():
                a, b = old[len("lessons/"):], new[len("lessons/"):]
                text = text.replace(a, b)
            return text
        for d in os.listdir(os.path.join(self.tmp, "src")):
            p = os.path.join(self.tmp, "src", d, "README.md")
            with open(p, encoding="utf-8") as f:
                t = f.read()
            with open(p, "w", encoding="utf-8") as f:
                f.write(re.sub(r'^(lesson: ")([^"]+)', lambda m: m.group(1) + respell(m.group(2)), t, flags=re.M))
        for root, _, names in os.walk(os.path.join(self.tmp, "lessons")):
            for n in names:
                if n.endswith(".md") or n == "chapters.txt":
                    p = os.path.join(root, n)
                    with open(p, encoding="utf-8") as f:
                        t = f.read()
                    if os.path.basename(root) in ("book",):
                        continue
                    if "lessons/cs-source" in p:
                        continue
                    if n == "chapters.txt" and root.endswith(cs.P("study-guides")):      # entries are relative to the guides folder
                        rel = lambda line: posixpath.relpath(cs.CAT.path("lessons/study-guides/" + line), cs.CAT.path("lessons/study-guides"))
                        with open(p, "w", encoding="utf-8") as f:
                            f.write("\n".join(rel(l) if l.strip() and not l.startswith("#") else l for l in t.split("\n")))
                        continue
                    with open(p, "w", encoding="utf-8") as f:
                        f.write(re.sub(r"(<!-- BEGIN GENERATED (?:program-flow:)?)([\w./-]+)", lambda m: m.group(1) + respell(m.group(2)), t))

    def tearDown(self):
        cs.CAT, cs.CSOUT = self.saved_cat, self.saved_csout
        super().tearDown()

    def test_generated_files_are_keyed_by_english_and_written_at_the_renamed_path(self):
        m = cs.Model()
        files = cs.generate_all(m)
        self.assertIn("cs/README.md", files)
        self.assertIn("index.md", files)
        self.assertEqual(sorted(cs.block_files())[:3], ["goals.md", "languages/README.md", "languages/apl.md"])
        cs.write_all(files)
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "lessons", "informatica", "README.md")))
        self.assertTrue(os.path.isfile(os.path.join(self.tmp, "lessons", "indice.md")))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "lessons", "cs")))
        self.assertEqual(cs.drift(cs.generate_all(cs.Model())), [])

    def test_a_block_marker_may_name_its_page_by_the_english_key_or_the_path_here(self):
        """The committed Spanish pages keep the English key in `BEGIN GENERATED program-flow:languages/forth.md` while the
        entries' `lesson:` names the page where it is (lenguajes/forth.md): both must fill the block (P3C-003 found it empty)."""
        here, key = cs.P("languages/forth.md"), "languages/forth.md"
        self.assertNotEqual(here, key)
        page = os.path.join(self.tmp, "lessons", here)
        text = cs.read(page).replace(":" + here, ":" + key)       # the layout respelling above touched only some markers
        def blocks(marker_page):
            with open(page, "w", encoding="utf-8") as f:
                f.write(re.sub(r"(GENERATED [\w-]+:)" + re.escape(key), lambda m: m.group(1) + marker_page, text))
            return cs.generate_blocks(cs.Model(), key)
        by_key, by_path = blocks(key), blocks(here)
        self.assertIn("src/forth/README.md#", by_key)               # the entry's program flow is in the block
        self.assertIn("```mermaid", by_key)
        self.assertEqual(by_key.replace(":" + key, ":" + here), by_path)
        other = blocks("languages/apl.md")                          # negative: a marker for another page fills nothing of forth's
        self.assertNotIn("src/forth/README.md#", other)

    def test_opener_and_index_links_use_the_renamed_names(self):
        files = cs.generate_all(cs.Model())
        opener = files["cs/README.md"]
        self.assertIn("(01-lectura-de-un-programa-adversarial.md)", opener)
        self.assertNotIn("(01-reading-an-adversarial-program.md)", opener)
        self.assertIn("(informatica/", files["index.md"])
        self.assertIn("guias-de-estudio/lenguajes/", files["index.md"])
        entries = [l for l in files["index.md"].splitlines() if l.startswith("- [") and "guias-de-estudio/" in l]
        self.assertGreater(len(entries), 10)        # one link per guide; the intro sentence is catalog text (see P3B-005)
        self.assertFalse([l for l in files["index.md"].splitlines() if l.startswith("- [") and "(study-guides/" in l])

    def test_a_stale_file_in_the_renamed_folder_is_reported(self):
        cs.write_all(cs.generate_all(cs.Model()))
        stale = os.path.join(cs.CSOUT, "99-stale.md")
        with open(stale, "w", encoding="utf-8") as f:
            f.write("x\n")
        self.assertTrue(any("informatica/99-stale.md (stale" in b for b in cs.drift(cs.generate_all(cs.Model()))))

    def test_the_english_name_of_a_moved_folder_is_not_used(self):
        cs.write_all(cs.generate_all(cs.Model()))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "lessons", "cs")))
        self.assertFalse(os.path.exists(os.path.join(self.tmp, "lessons", "languages", "apl.md")))


if __name__ == "__main__":
    unittest.main(verbosity=2)
