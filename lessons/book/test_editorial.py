"""Cross-volume editorial regressions. Run from any directory with Python 3.

    python lessons/book/test_editorial.py

The words the checks look for (the acronym phrase, the headings that bound the opening, the count line, the assurance tally and the
APL explanations) come from the locale catalog (lessons/book/locale/<lang>.yaml, blocks editorial, acronym, study_guides, cs and
sentinels). The checks are functions that return a list of problems, so a test can both run them on the real sources and break a
copy to show that each one can fail.

  * RealSources runs the checks against the real repository in BOOK_LANG (default "en"). The Spanish run passes once the Spanish
    sources are translated (stage 4); until then the real README, intro and guides are English and it reports them.
  * The Mutations and PdfSentinels classes run in English and in Spanish on synthetic texts built from the catalog words. They
    show that the Spanish words are enforced, that English words are refused in a Spanish edition, and that every rule fails when
    its text is broken. Nothing in the repository is touched.
Needs the Python standard library and PyYAML (the locale catalog); the PDF row test also needs WeasyPrint and Ghostscript.
"""
from collections import Counter
from pathlib import Path
import os
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "locale"))   # never name a package `locale`: it would shadow the stdlib module
sys.dont_write_bytecode = True
import build
import catalog
import cs
import guide_impact
import pdf_sentinels
import study_guides

ROOT = Path(cs.REPO)
BOOK_LANG = os.environ.get("BOOK_LANG", "en")
LABEL_KEYS = ("guaranteed", "implementation_permitted", "accidentally_exploited")   # catalog keys; the frontmatter value uses hyphens
WORD_KEYS = (["acronym.expansion", "study_guides.challenge_heading", "cs.index_entries"]
             + ["editorial." + k for k in ("root_opening_end", "guides_opening_end", "root_count_pattern", "tally_pattern",
                                           "apl_four", "apl_five_pattern", "apl_up_to_five", "apl_seven_slots")]
             + ["study_guides.assurance." + k for k in LABEL_KEYS])


class Words:
    """The editorial words of one language, read from the catalog. A missing key raises catalog.MissingKeyError."""

    def __init__(self, lang):
        cat = catalog.load(lang)
        cat.require(WORD_KEYS)
        text = {key: cat.text(key) for key in WORD_KEYS}
        self.lang = lang
        self.aside = text["acronym.expansion"]
        self.challenge_heading = text["study_guides.challenge_heading"]
        self.index_entries = text["cs.index_entries"]
        self.root_end, self.guides_end = text["editorial.root_opening_end"], text["editorial.guides_opening_end"]
        self.count_pattern, self.tally_pattern = text["editorial.root_count_pattern"], text["editorial.tally_pattern"]
        self.apl_four, self.apl_five = text["editorial.apl_four"], text["editorial.apl_five_pattern"]
        self.apl_up_to, self.apl_seven = text["editorial.apl_up_to_five"], text["editorial.apl_seven_slots"]
        # label as written in the guide (lower case) -> the frontmatter value
        self.labels = {text["study_guides.assurance." + k].lower(): k.replace("_", "-") for k in LABEL_KEYS}
        if "{labels}" not in self.tally_pattern:
            raise catalog.CatalogError("editorial.tally_pattern must contain {labels}")
        for pattern in (self.count_pattern, self.tally_pattern.replace("{labels}", "x"), self.apl_five):
            re.compile(pattern)


def read(path):
    return (ROOT / path).read_text(encoding="utf-8")


def aside_count(book, guides, aside):
    return sum(text.count(aside) for text in book), sum(text.count(aside) for text in guides)


def before(text, heading):
    """The text before `## heading`; the whole text when the heading is absent (the opening is then the whole file)."""
    return text.split("## " + heading)[0]


def acronym_problems(w, intro, first_guide, root, book, guides):
    """The recursive-acronym aside occurs once near each opening and once in each volume."""
    problems = []
    for name, text, end in (("intro", intro, w.challenge_heading), ("first study guide", first_guide, w.guides_end),
                            ("root README", root, w.root_end)):
        if w.aside not in before(text, end):
            problems.append(f"{name}: the aside is not before '## {end}'")
    if root.count(w.aside) != 1:
        problems.append(f"root README: the aside occurs {root.count(w.aside)} times, expected 1")
    counts = aside_count(book, guides, w.aside)
    if counts != (1, 1):
        problems.append(f"occurrences in the book and in the guides are {counts}, expected (1, 1)")
    return problems


def members(text, marker):
    return re.findall(marker + r"\[`([^`]+)`\]\([^)]*src/[^)]*\)", text, re.M)


def membership_problems(name, text, marker, names):
    found = Counter(members(text, marker))
    return [] if found == Counter(names) else [f"{name} lists {sorted(found.elements())}, the model has {sorted(Counter(names).elements())}"]


def tally(w, text):
    """{assurance value: count} read from the sentences of the portability guide."""
    alternation = "|".join(re.escape(label) for label in sorted(w.labels, key=len, reverse=True))
    return {w.labels[label]: int(count) for count, label in re.findall(w.tally_pattern.replace("{labels}", alternation), text)}


def count_problems(w, root, challenges, languages):
    found = re.search(w.count_pattern, root)
    if not found:
        return ["root README: no count line"]
    got = tuple(map(int, found.groups()))
    return [] if got == (challenges, languages) else [f"root README says {got}, the model has {(challenges, languages)}"]


def tally_problems(w, guide, assurance):
    got = tally(w, guide)
    return [] if got == dict(assurance) else [f"guide tally is {got}, the model has {dict(assurance)}"]


APL_ASSIGNMENTS = [
    ("Drawn", "(10-⎕IO)+?5⍴10"),
    ("Hours", "Drawn↑⍨1++/40≥+\\Drawn"),
    ("Totals", "+\\Hours"),
    ("Kinds", "(≢Hours)⍴Categories"),
]


def apl_source_problems(source):
    assignments = re.findall(r"^(Drawn|Hours|Totals|Kinds)←(.+?)(?:\s+⍝.*)?$", source, re.M)
    return [] if assignments == APL_ASSIGNMENTS else [f"timecards.apl assignments are {assignments}"]


def apl_text_problems(w, path, text):
    problems = []
    if w.apl_four not in text.lower():
        problems.append(f"{path}: missing '{w.apl_four}'")
    if not re.search(w.apl_five, text):
        problems.append(f"{path}: no match for '{w.apl_five}'")
    if w.apl_up_to not in text:
        problems.append(f"{path}: missing '{w.apl_up_to}'")
    if w.apl_seven in text:
        problems.append(f"{path}: still says '{w.apl_seven}'")
    return problems


def P(path):
    """This edition's path for an English repository path (plan 5.6; the identity while the catalog layout is english)."""
    return cs.CAT.path(path)


class RealSources(unittest.TestCase):
    """The checks against the real repository, in BOOK_LANG."""

    @classmethod
    def setUpClass(cls):
        cls.w = Words(BOOK_LANG)

    def test_recursive_acronym_occurs_once_near_each_opening(self):
        guide_files = [f"{P('lessons/study-guides')}/{path}" for path in study_guides.manifest(study_guides.GUIDES)]
        book = list(build.chapter_texts().values()) + [read(P("lessons/front-matter.md"))]
        guides = [read(path) for path in guide_files + [P("lessons/study-guides/front-matter.md")]]
        self.assertEqual(acronym_problems(self.w, read(P("lessons/intro.md")), guides[0], read("README.md"), book, guides), [])

    def test_count_and_assurance_tally_follow_the_model(self):
        model = cs.Model()
        files = cs.generate_all(model)
        marker = "## " + self.w.index_entries
        self.assertIn(marker, files["index.md"])  # en-key
        index = files["index.md"].split(marker, 1)[1]  # en-key
        roles = cs.blk_roles(model, cs.Links(model, "cs/09-comparative-case-studies.md"), lambda text: text)  # en-key
        self.assertEqual(membership_problems("index", index, r"^- ", model.entries.keys()), [])
        self.assertEqual(membership_problems("roles", roles, r"^\| ", model.entries.keys()), [])
        languages = {language for e in model.entries.values() for language in e["languages"]}
        self.assertEqual(count_problems(self.w, read("README.md"), len(model.entries), len(languages)), [])
        guide = read(P("lessons/study-guides/concepts/portability-abstraction-and-cost.md"))
        self.assertEqual(tally_problems(self.w, guide, Counter(e["assurance"] for e in model.entries.values())), [])

    def test_apl_explanations_match_the_four_array_assignments(self):
        self.assertEqual(apl_source_problems(read("src/apl/timecards.apl")), [])
        for path in ["src/apl/README.md", P("lessons/languages/apl.md"), P("lessons/study-guides/languages/apl.md")]:
            with self.subTest(path=path):
                self.assertEqual(apl_text_problems(self.w, path, read(path)), [])

    @unittest.skipUnless(shutil.which("weasyprint") and shutil.which("gs"), "needs WeasyPrint and Ghostscript")
    def test_a_table_row_moves_together_across_pdf_pages(self):
        with tempfile.TemporaryDirectory() as tmp:
            directory = Path(tmp)
            html = directory / "rows.html"
            html.write_text("""<html><meta charset="utf-8"><style>
                @page { size: 400px 210px; margin: 16px; }
                table { break-inside: auto; }
                td { font: 12px/22px sans-serif; }
                </style><body>
                <table><thead><tr><th>Heading</th><th>Meaning</th><th>Evidence</th></tr></thead>
                <tbody><tr><td>One<br>Two<br>Three<br>Four</td><td></td><td></td></tr>
                <tr><td>RowStarts<br>MiddleOne<br>MiddleTwo<br>MiddleThree<br>RowEnds</td>
                <td>Explanation</td><td>Witness</td></tr></tbody></table></body></html>
                """, encoding="utf-8")
            pdf = directory / "rows.pdf"
            subprocess.run(["weasyprint", "-q", "-s", str(ROOT / "lessons/book/book.css"), str(html), str(pdf)], check=True)
            subprocess.run(["gs", "-q", "-dBATCH", "-dNOPAUSE", "-sDEVICE=txtwrite",
                            f"-sOutputFile={directory}/page-%d.txt", str(pdf)], check=True, capture_output=True)
            pages = sorted(directory.glob("page-*.txt"))
            self.assertEqual(len(pages), 2)
            first, second = (page.read_text(encoding="utf-8") for page in pages)
            self.assertIn("Four", first)
            self.assertNotIn("Witness", first)
            for term in ("Heading", "RowStarts", "RowEnds", "Explanation", "Witness"):
                self.assertIn(term, second)

    def test_changed_source_invalidates_a_guide_review(self):
        path = "src/regex-dotnet/README.md"
        guide = "languages/regex-engines-and-sed.md"  # path-ok: a synthetic key of a pure function
        text = "[pattern](../../../src/regex-dotnet/README.md#program-flow)"
        queue = guide_impact.candidate_reviews([path], {guide: text}, {})
        self.assertEqual(queue, {guide: [path]})
        original = {path: b"capture witness"}
        before_ = {path: b"earlier witness"}
        token = guide_impact.review_token(queue[guide], before_, original, text)
        changed = guide_impact.review_token(queue[guide], before_, {path: b"changed witness"}, text)
        self.assertEqual(guide_impact.missing_reviews({guide: token}, {guide: token}), [])
        self.assertEqual(guide_impact.missing_reviews({guide: changed}, {guide: token}), [guide])

    def test_indirect_dependencies_can_add_guides(self):
        path = "src/awk-weird/README.md"
        guide = "concepts/comparative-machine-design.md"  # path-ok: a synthetic key of a pure function
        text = {guide: "An input engine supplies the next record."}
        self.assertEqual(guide_impact.candidate_reviews([path], text, {}), {})
        self.assertEqual(guide_impact.candidate_reviews([path], text, {path: [guide]}), {guide: [path]})


# Sample sentences, one set per language, written the way the catalog patterns expect (the Spanish ones are the contract for stage 4).
SAMPLES = {
    "en": {"count": "> **{n} challenges in {l} languages**", "tally": "| **{n}** entries are {label} | the ports |",
           "tally_short": "| **{n}** are {label} | APL |", "rolls": "`Drawn` holds five rolls.",
           "other_lang": "es"},
    "es": {"count": "> **{n} retos en {l} lenguajes**", "tally": '| **{n}** entradas tienen la garantía "{label}" | los puertos |',
           "tally_short": '| **{n}** tienen la garantía "{label}" | APL |', "rolls": "`Drawn` guarda cinco tiradas.",
           "other_lang": "en"},
}
ENGLISH = {"count": "> **40 challenges in 29 languages**", "tally": "| **17** entries are guaranteed | the ports |"}


class Mutations:
    """Mixin: the rules on synthetic texts built from the catalog words of `lang`; each rule is shown to be able to fail."""
    lang = "en"

    @classmethod
    def setUpClass(cls):
        cls.w = Words(cls.lang)
        cls.s = SAMPLES[cls.lang]

    def texts(self):
        w = self.w
        return dict(
            intro=f"# Intro\n\n{w.aside}\n\n## {w.challenge_heading}\n\nBody.",
            first_guide=f"# Guide\n\n{w.aside}\n\n## {w.guides_end}\n\nBody.",
            root=f"# Root\n\n{w.aside}\n\n## {w.root_end}\n\nBody.",
            book=["A chapter without it.", "Another."], guides=["A guide without it.", "Another."])

    def acronym(self, **change):
        t = {**self.texts(), **change}
        return acronym_problems(self.w, t["intro"], t["first_guide"], t["root"], t["book"], t["guides"])

    def test_acronym_clean_fixture_passes(self):
        # The intro, the first guide and the root README each carry the aside once; the totals of book and guides are 1 and 1 only
        # when the counted texts hold one each.
        t = self.texts()
        book, guides = t["book"] + [t["intro"]], t["guides"] + [t["first_guide"]]
        self.assertEqual(acronym_problems(self.w, t["intro"], t["first_guide"], t["root"], book, guides), [])

    def test_acronym_missing_before_the_opening_heading_fails(self):
        w = self.w
        t = self.texts()
        book, guides = t["book"] + [t["intro"]], t["guides"] + [t["first_guide"]]
        late = f"# Intro\n\n## {w.challenge_heading}\n\n{w.aside}"
        problems = acronym_problems(w, late, t["first_guide"], t["root"], book, guides)
        self.assertTrue(any(p.startswith("intro:") for p in problems), problems)
        late_root = f"# Root\n\n## {w.root_end}\n\n{w.aside}"
        problems = acronym_problems(w, t["intro"], t["first_guide"], late_root, book, guides)
        self.assertTrue(any(p.startswith("root README: the aside is not") for p in problems), problems)

    def test_acronym_extra_occurrence_fails_in_each_volume(self):
        w = self.w
        t = self.texts()
        book, guides = t["book"] + [t["intro"]], t["guides"] + [t["first_guide"]]
        self.assertTrue(acronym_problems(w, t["intro"], t["first_guide"], t["root"], book + [w.aside], guides))
        self.assertTrue(acronym_problems(w, t["intro"], t["first_guide"], t["root"], book, guides + [w.aside]))
        self.assertTrue(acronym_problems(w, t["intro"], t["first_guide"], t["root"] + w.aside, book, guides))
        self.assertTrue(acronym_problems(w, t["intro"], t["first_guide"], t["root"], book[:-1], guides))   # zero in the book

    def test_the_other_language_aside_is_refused(self):
        other = Words(self.s["other_lang"])
        self.assertNotEqual(other.aside, self.w.aside)
        t = self.texts()
        for key in ("intro", "first_guide", "root"):
            t[key] = t[key].replace(self.w.aside, other.aside)
        self.assertTrue(self.acronym(**t))

    def test_count_line_matches_and_fails_on_a_wrong_number(self):
        line = self.s["count"].format(n=40, l=29)
        self.assertEqual(count_problems(self.w, line, 40, 29), [])
        self.assertTrue(count_problems(self.w, line, 41, 29))
        self.assertTrue(count_problems(self.w, line, 40, 28))
        self.assertEqual(count_problems(self.w, "no count here", 40, 29), ["root README: no count line"])

    def test_count_line_in_the_other_language_is_refused(self):
        line = SAMPLES[self.s["other_lang"]]["count"].format(n=40, l=29)
        self.assertEqual(count_problems(self.w, line, 40, 29), ["root README: no count line"])

    def table(self, counts):
        order = ("guaranteed", "implementation_permitted", "accidentally_exploited")
        rows = []
        for i, key in enumerate(order):
            label = next(lbl for lbl, value in self.w.labels.items() if value == key.replace("_", "-"))
            rows.append(self.s["tally" if i == 0 else "tally_short"].format(n=counts[key.replace("_", "-")], label=label))
        return "\n".join(rows)

    def test_tally_reads_the_three_assurance_rows(self):
        counts = {"guaranteed": 17, "implementation-permitted": 16, "accidentally-exploited": 7}
        self.assertEqual(tally(self.w, self.table(counts)), counts)
        self.assertEqual(tally_problems(self.w, self.table(counts), Counter(counts)), [])

    def test_tally_fails_on_a_wrong_count_a_missing_row_and_the_wrong_language(self):
        counts = {"guaranteed": 17, "implementation-permitted": 16, "accidentally-exploited": 7}
        table = self.table(counts)
        self.assertTrue(tally_problems(self.w, table, Counter({**counts, "guaranteed": 18})))
        self.assertTrue(tally_problems(self.w, "\n".join(table.splitlines()[:2]), Counter(counts)))
        english = "\n".join(SAMPLES["en"]["tally" if i == 0 else "tally_short"].format(n=n, label=lbl) for i, (n, lbl) in enumerate(
            [(17, "guaranteed"), (16, "implementation-permitted"), (7, "accidentally exploited")]))
        if self.lang != "en":
            self.assertEqual(tally(self.w, english), {})

    def test_apl_text_rules_pass_and_fail(self):
        w = self.w
        good = f"{w.apl_four.capitalize()} decide. {self.s['rolls']} Slots: {w.apl_up_to}."
        self.assertEqual(apl_text_problems(w, "x.md", good), [])
        for broken, fragment in [(good.replace(w.apl_four.capitalize(), "Some assignments"), w.apl_four),
                                 (good.replace(self.s["rolls"], "Nothing."), w.apl_five),
                                 (good.replace(w.apl_up_to, "several"), w.apl_up_to),
                                 (good + f" Also {w.apl_seven}.", w.apl_seven)]:
            with self.subTest(fragment=fragment):
                problems = apl_text_problems(w, "x.md", broken)
                self.assertEqual(len(problems), 1, problems)
                self.assertIn(fragment, problems[0])

    def test_apl_source_check_fails_when_an_assignment_changes(self):
        source = "\n".join(f"{name}←{expr}  ⍝ note" for name, expr in APL_ASSIGNMENTS)
        self.assertEqual(apl_source_problems(source), [])
        self.assertTrue(apl_source_problems(source.replace("5⍴10", "7⍴10")))
        self.assertTrue(apl_source_problems("\n".join(source.splitlines()[:3])))

    def test_membership_fails_on_a_missing_extra_or_duplicate_entry(self):
        text = "- [`a`](../../src/a/README.md)\n- [`b`](../../src/b/README.md)\n"
        self.assertEqual(membership_problems("index", text, r"^- ", ["a", "b"]), [])
        self.assertTrue(membership_problems("index", text, r"^- ", ["a"]))
        self.assertTrue(membership_problems("index", text, r"^- ", ["a", "b", "c"]))
        self.assertTrue(membership_problems("index", text + text.splitlines()[0], r"^- ", ["a", "b"]))


class MutationsEn(Mutations, unittest.TestCase):
    lang = "en"


class MutationsEs(Mutations, unittest.TestCase):
    lang = "es"

    def test_spanish_words_are_the_agreed_ones(self):
        # Contract for the translation tasks: these exact words, not the English ones.
        self.assertEqual(self.w.aside, "Bicho raro, Interpreta, Camino indirecto, Hallazgos y Octetos")
        self.assertEqual(self.w.challenge_heading, "Qué hace el reto")
        self.assertEqual(set(self.w.labels), {"garantizado", "permitido por la implementación", "aprovechado por accidente"})
        self.assertNotIn(ENGLISH["count"], SAMPLES["es"]["count"])


class PdfSentinels(unittest.TestCase):
    """The label sentinels of `pdf_sentinels`, in each language, and the code sentinels that never change."""
    LABELS = {   # profile -> {sentinel name: the label as the PDF text shows it}; the English values are the pinned source's literals
        "en": {"Mermaid apl-weird ≤": "Alive: total ≤ 40?", "Mermaid forth-weird <=": "-1 while total <= 40, else 0",
               "Mermaid Forth parse position >": "Interpreter reads: 0 0 >in @", "Mermaid awk-weird ≥": "Last rule: t ≥ 41?"},
        "es": {"Mermaid apl-weird ≤": "Alive: ¿total ≤ 40?", "Mermaid forth-weird <=": "-1 mientras total <= 40; si no, 0",
               "Mermaid Forth parse position >": "El intérprete lee: 0 0 >in @", "Mermaid awk-weird ≥": "Última regla: ¿t ≥ 41?"},
    }
    CODE = ["APL stop rule ≥", "APL function definition", "Forth checker regex", "sed capture groups", "wrapped Forth alternation",
            "wrapped Make trace"]

    def setUp(self):
        self.before = pdf_sentinels.LANG
        self.addCleanup(pdf_sentinels.set_language, self.before)

    def profile(self, lang, publication="book"):
        pdf_sentinels.set_language(lang)
        return {s.name: s for s in pdf_sentinels.PROFILES[publication]}

    def test_each_language_finds_its_own_labels(self):
        for lang, labels in self.LABELS.items():
            book = self.profile(lang)
            for name, text in labels.items():
                with self.subTest(lang=lang, sentinel=name):
                    self.assertTrue(book[name].matches(f"page text\n{text}\nmore"))

    def test_a_lost_space_after_a_comparison_sign_is_tolerated_only_there(self):
        for lang in ("en", "es"):
            book = self.profile(lang)
            for name in ("Mermaid apl-weird ≤", "Mermaid awk-weird ≥"):
                text = self.LABELS[lang][name]
                with self.subTest(lang=lang, sentinel=name):
                    self.assertTrue(book[name].matches(re.sub(r"([≤≥]) ", r"\1", text)))     # the space after the sign is lost
                    self.assertFalse(book[name].matches(text.replace(": ", ":", 1)))           # any other lost space is not tolerated
                    self.assertFalse(book[name].matches(text.replace("40", "41").replace("41", "42")))

    def test_a_wrong_label_fails(self):
        for lang, labels in self.LABELS.items():
            book = self.profile(lang)
            for name, text in labels.items():
                with self.subTest(lang=lang, sentinel=name):
                    self.assertFalse(book[name].matches(text.replace("<=", "<").replace("≤", "<").replace("≥", ">").replace(">in", "in")))
                    self.assertFalse(book[name].matches(""))

    def test_the_other_languages_labels_are_not_accepted(self):
        for lang, other in (("en", "es"), ("es", "en")):
            book = self.profile(lang)
            for name, text in self.LABELS[other].items():
                if text == self.LABELS[lang][name]:
                    continue
                with self.subTest(lang=lang, sentinel=name):
                    self.assertFalse(book[name].matches(text))

    def test_code_sentinels_are_the_same_in_both_languages(self):
        for publication in ("book", "study-guides"):
            en, es = self.profile("en", publication), self.profile("es", publication)
            self.assertEqual({n for n in en if n in self.CODE}, {n for n in es if n in self.CODE})
            for name in en:
                if name in self.CODE:
                    self.assertEqual(en[name], es[name], name)

    def test_the_english_profile_keeps_the_pinned_sentinel_names_and_snippets(self):
        book, guides = self.profile("en"), self.profile("en", "study-guides")
        self.assertEqual(set(book), {"Mermaid apl-weird ≤", "Mermaid forth-weird <=", "Mermaid Forth parse position >", "APL stop rule ≥",
                                     "Mermaid awk-weird ≥", "APL reshape and iota", "APL function definition", "Forth checker regex",
                                     "sed capture groups", "wrapped Forth alternation"})
        self.assertEqual(set(guides), {"Mermaid apl-weird ≤", "Mermaid forth-weird <=", "Mermaid Forth parse position >",
                                       "APL reshape and iota", "APL function definition", "wrapped Make trace"})
        self.assertEqual(book["APL reshape and iota"].expected, "⍴ (reshape), ⍳ (index generator)")
        self.assertEqual(guides["APL reshape and iota"].expected, "basic APL: ⍳, ⍴")
        self.assertEqual(book["APL stop rule ≥"].expected, "Alive←40≥T")

    def test_the_spanish_profile_translates_the_reshape_snippets(self):
        book, guides = self.profile("es"), self.profile("es", "study-guides")
        self.assertEqual(book["APL reshape and iota"].expected, "⍴ (cambio de forma), ⍳ (generador de índices)")
        self.assertEqual(guides["APL reshape and iota"].expected, "APL básico: ⍳, ⍴")

    def test_profiles_is_updated_in_place_and_a_failed_switch_changes_nothing(self):
        import lint_pdf
        self.assertIs(lint_pdf.PROFILES, pdf_sentinels.PROFILES)
        pdf_sentinels.set_language("en")
        snapshot = dict(pdf_sentinels.PROFILES)
        with self.assertRaises(catalog.CatalogError):
            pdf_sentinels.set_language("xx")
        self.assertEqual(dict(pdf_sentinels.PROFILES), snapshot)
        self.assertEqual(pdf_sentinels.LANG, "en")
        pdf_sentinels.set_language("es")
        self.assertIs(lint_pdf.PROFILES, pdf_sentinels.PROFILES)
        self.assertNotEqual(dict(pdf_sentinels.PROFILES), snapshot)


class Catalog(unittest.TestCase):
    def test_every_editorial_and_sentinel_key_exists_in_both_languages(self):
        for lang in ("en", "es"):
            Words(lang)
            catalog.load(lang).require(pdf_sentinels.WORD_KEYS)

    def test_a_missing_key_fails_loudly(self):
        with self.assertRaises(catalog.MissingKeyError):
            catalog.load("en").require(["editorial.no_such_key"])


if __name__ == "__main__":
    unittest.main()
