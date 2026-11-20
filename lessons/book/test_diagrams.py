"""Tests for diagrams.py: the Program Flow contract, the structural scanner, the cache keys, and (when a renderer is installed) a real render.

    python lessons/book/test_diagrams.py

Needs only the Python standard library. The two render tests are skipped, and say so, when Mermaid CLI or a Chromium is missing.
"""
import json, os, sys, tempfile, unittest
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import diagrams

diagrams.set_language("en")       # the English tests below must not depend on BOOK_LANG in the environment

GOOD = '''# Title

## Run it

text

## Program Flow

```mermaid
flowchart TD
    accTitle: A caption
    accDescr: What it shows.
    A["one"] --> B["two"]
```

**What this shows:** x.

**Why this mechanism matters:** y.

## How the stunt works
'''


def read(path):
    with open(path, "rb") as f:
        return f.read()


class Contract(unittest.TestCase):
    def check(self, text):
        return diagrams.program_flow(text, "src/x/README.md")

    def test_a_good_section(self):
        sec, probs = self.check(GOOD)
        self.assertEqual(probs, [])
        self.assertTrue(sec.startswith("```mermaid") and sec.rstrip().endswith("y."))
        self.assertNotIn("How the stunt works", sec)

    def test_missing_section(self):
        sec, probs = self.check(GOOD.replace("## Program Flow", "## Something else"))
        self.assertIsNone(sec)
        self.assertIn("no '## Program Flow' section", probs[0])

    def test_a_synonym_heading_is_refused(self):
        _, probs = self.check(GOOD.replace("## Program Flow", "## Program flow"))
        self.assertTrue(any("exactly '## Program Flow'" in p for p in probs))

    def test_a_heading_inside_a_code_block_is_not_a_heading(self):
        text = GOOD.replace("## Program Flow", "## Other") + "\n```text\n## Program Flow\n```\n"
        sec, probs = self.check(text)
        self.assertIsNone(sec)

    def test_two_diagrams_are_refused(self):
        _, probs = self.check(GOOD.replace("**What this shows:**", "```mermaid\nflowchart TD\n  A-->B\n```\n\n**What this shows:**"))
        self.assertTrue(any("exactly one" in p for p in probs))

    def test_a_non_mermaid_fence_is_refused(self):
        _, probs = self.check(GOOD.replace("**What this shows:**", "```text\nx\n```\n\n**What this shows:**"))
        self.assertTrue(any("only a ```mermaid block" in p for p in probs))

    def test_alt_text_and_caption_are_required(self):
        _, probs = self.check(GOOD.replace("    accTitle: A caption\n", ""))
        self.assertTrue(any("accTitle" in p for p in probs))
        _, probs = self.check(GOOD.replace("    accDescr: What it shows.\n", ""))
        self.assertTrue(any("accDescr" in p for p in probs))

    def test_html_in_a_diagram_is_refused(self):
        _, probs = self.check(GOOD.replace('"one"', '"one<br/>two"'))
        self.assertTrue(any("HTML" in p for p in probs))

    def test_sub_headings_are_refused(self):
        _, probs = self.check(GOOD.replace("**What this shows:** x.", "### Sub\n\n**What this shows:** x."))
        self.assertTrue(any("sub-headings" in p for p in probs))

    def test_both_lead_ins_are_required(self):
        _, probs = self.check(GOOD.replace("**Why this mechanism matters:**", "**Why:**"))
        self.assertTrue(any("Why this mechanism matters" in p for p in probs))

    def test_links_to_the_same_readme_are_refused_but_file_links_are_not(self):
        _, probs = self.check(GOOD.replace("x.", "see [a](#b)."))
        self.assertTrue(any("heading in this README" in p for p in probs))
        _, probs = self.check(GOOD.replace("x.", "see [a](../cobol/README.md)."))
        self.assertEqual(probs, [])

    def test_the_real_entries_all_pass(self):
        diagrams.set_language(os.environ.get("BOOK_LANG", "en"))      # the real entries are in the language of the edition being built
        self.addCleanup(diagrams.set_language, "en")
        src =os.path.join(diagrams.HERE, "..", "..", "src")
        for d in sorted(os.listdir(src)):
            r = os.path.join(src, d, "README.md")
            if os.path.isfile(r):
                with open(r, encoding="utf-8") as f:
                    sec, probs = diagrams.program_flow(f.read(), d)
                self.assertEqual(probs, [], d)


class Scanner(unittest.TestCase):
    def test_fences_and_headings(self):
        items = diagrams.scan("# A\n\n```mermaid\n## not a heading\n```\n\n~~~~\n```inner\n~~~~\n\n## B\n")
        self.assertEqual([(i[0], i[2] if i[0] == "heading" else i[1]) for i in items], [("heading", "A"), ("fence", "mermaid"), ("fence", ""), ("heading", "B")])

    def test_diagram_family(self):
        self.assertEqual(diagrams.diagram_type("sequenceDiagram\n  A->>B: x"), "sequenceDiagram")
        self.assertEqual(diagrams.diagram_type("%% c\n\nstateDiagram-v2\n"), "stateDiagram-v2")


GOOD_ES = GOOD.replace("## Program Flow", "## Flujo del programa").replace("**What this shows:**", "**Qué muestra:**") \
              .replace("**Why this mechanism matters:**", "**Por qué importa este mecanismo:**").replace("A caption", "Un pie de figura")


class SpanishContract(unittest.TestCase):
    """The same README contract, with the words taken from the Spanish catalog (lessons/book/locale/es.yaml)."""
    def setUp(self):
        diagrams.set_language("es")
        self.addCleanup(diagrams.set_language, "en")

    def check(self, text):
        return diagrams.program_flow(text, "src/x/README.md")

    def test_the_constants_come_from_the_spanish_catalog(self):
        self.assertEqual((diagrams.SECTION, diagrams.LEAD_SHOWS, diagrams.FIGURE_WORD, diagrams.LANG),
                         ("Flujo del programa", "Qué muestra:", "Figura", "es"))

    def test_a_good_spanish_section(self):
        sec, probs = self.check(GOOD_ES)
        self.assertEqual(probs, [])
        self.assertTrue(sec.startswith("```mermaid") and sec.rstrip().endswith("y."))

    def test_the_english_heading_is_not_accepted(self):
        sec, probs = self.check(GOOD)
        self.assertIsNone(sec)
        self.assertIn("no '## Flujo del programa' section", probs[0])

    def test_a_near_miss_heading_is_reported_with_the_exact_spelling(self):
        for wrong in ("## Flujo del Programa", "## Flujo", "## FLUJO DEL PROGRAMA"):
            _, probs = self.check(GOOD_ES.replace("## Flujo del programa", wrong))
            self.assertTrue(any("exactly '## Flujo del programa'" in p for p in probs), wrong)

    def test_an_unaccented_lead_in_is_refused(self):
        _, probs = self.check(GOOD_ES.replace("**Qué muestra:**", "**Que muestra:**"))
        self.assertTrue(any("**Qué muestra:**" in p for p in probs))
        _, probs = self.check(GOOD_ES.replace("**Por qué importa este mecanismo:**", "**Por qué:**"))
        self.assertTrue(any("Por qué importa este mecanismo" in p for p in probs))

    def test_english_lead_ins_are_refused_under_the_spanish_catalog(self):
        _, probs = self.check(GOOD_ES.replace("**Qué muestra:**", "**What this shows:**"))
        self.assertEqual(len(probs), 1)

    def test_the_caption_says_figura(self):
        src = "flowchart TD\n    accTitle: Un pie\n    accDescr: Texto\n    A-->B"
        fig = diagrams.Figure("k", src, "somewhere")
        fig.w, fig.h = 400.0, 200.0
        fig.pw, fig.ph, fig.scale = 400, 200, 1.0
        self.assertIn("<figcaption>Figura 2. Un pie</figcaption>", diagrams.embed("```mermaid\n" + src + "\n```", {src: fig}, "svg", [2]))
        self.assertEqual(diagrams.Figure("k", "flowchart TD\n  A-->B", "x").title, "Diagrama")

    def test_a_missing_key_fails_loudly_and_leaves_the_language_unchanged(self):
        import catalog
        real = catalog.load
        def broken(lang, base=catalog.HERE):
            cat = real(lang, base)
            del cat.flat["diagrams.figure"]
            return cat
        catalog.load = broken
        try:
            with self.assertRaises(catalog.MissingKeyError):
                diagrams.set_language("es")
        finally:
            catalog.load = real
        self.assertEqual(diagrams.SECTION, "Flujo del programa", "a failed switch must not leave half-loaded constants")


class EnglishCatalogMatchesTheOldLiterals(unittest.TestCase):
    """The English catalog reproduces the strings the tool carried before localization, so English output is unchanged."""
    def test_literals(self):
        diagrams.set_language("en")
        self.assertEqual((diagrams.SECTION, diagrams.LEAD_SHOWS, diagrams.LEAD_WHY, diagrams.FIGURE_WORD, diagrams.DEFAULT_TITLE),
                         ("Program Flow", "What this shows:", "Why this mechanism matters:", "Figure", "Diagram"))

    def test_an_unknown_language_is_an_error(self):
        import catalog
        with self.assertRaises(catalog.CatalogError):
            diagrams.set_language("xx")
        self.assertEqual(diagrams.LANG, "en")


class FakeRenderer(diagrams.Renderer):
    def __init__(self, version="1", chrome="c1"):
        self.version, self.chrome_version = version, chrome
        with open(diagrams.CONFIG, "rb") as f:
            self.config_bytes = f.read()


class CacheKeys(unittest.TestCase):
    def test_the_key_follows_the_text_the_renderer_and_the_browser(self):
        r = FakeRenderer()
        a = r.key("flowchart TD\n A-->B")
        self.assertEqual(a, r.key("flowchart TD\n A-->B\n"), "trailing newlines do not matter")
        self.assertNotEqual(a, r.key("flowchart TD\n A-->C"), "editing the text changes the key")
        self.assertNotEqual(a, FakeRenderer(version="2").key("flowchart TD\n A-->B"), "a new Mermaid CLI changes the key")
        self.assertNotEqual(a, FakeRenderer(chrome="c2").key("flowchart TD\n A-->B"), "a new browser changes the key")
        r.config_bytes += b" "
        self.assertNotEqual(a, r.key("flowchart TD\n A-->B"), "a new style changes the key")

    def test_fit_never_enlarges_and_respects_the_page(self):
        self.assertEqual(diagrams.fit(300, 300)[2], 1.0)
        w, h, s = diagrams.fit(1280, 400)
        self.assertEqual(w, diagrams.FIT_W)
        w, h, s = diagrams.fit(300, 1400)
        self.assertEqual(h, diagrams.FIT_H)


class Embedding(unittest.TestCase):
    def test_a_fence_becomes_a_numbered_figure_with_alt_text_and_caption(self):
        src = "flowchart TD\n    accTitle: Cap <b>\n    accDescr: Alt \"q\"\n    A-->B"
        fig = diagrams.Figure("k", src, "somewhere")
        fig.w, fig.h = 400.0, 200.0
        fig.pw, fig.ph, fig.scale = 400, 200, 1.0
        out = diagrams.embed("before\n\n```mermaid\n" + src + "\n```\n\nafter", {src: fig}, "svg", [5])
        self.assertIn("<figcaption>Figure 5. Cap &lt;b&gt;</figcaption>", out)
        self.assertIn('alt="Alt &quot;q&quot;"', out)
        self.assertIn("width:400px;height:200px", out)
        self.assertNotIn("```", out)
        self.assertTrue(out.startswith("before") and out.endswith("after"))
        self.assertIn('width="400"', diagrams.embed("```mermaid\n" + src + "\n```", {src: fig}, "png", [1]))


@unittest.skipIf(diagrams.find_renderer()[0] is None, "Mermaid CLI or Chromium not installed: the render tests are skipped")
class RealRender(unittest.TestCase):
    def setUp(self):
        self.r = diagrams.find_renderer()[0]
        self.saved = diagrams.CACHE
        diagrams.CACHE = tempfile.mkdtemp()

    def tearDown(self):
        diagrams.CACHE = self.saved

    GOOD = "flowchart TD\n    accTitle: T\n    accDescr: D\n    A[one] --> B[two]"

    def test_render_cache_and_invalidation_touch_only_the_changed_figure(self):
        other = self.GOOD.replace("two", "three")
        figs, errs = diagrams.render_all(self.r, {self.GOOD: "a", other: "b"})
        self.assertEqual(errs, [])
        self.assertFalse(figs[self.GOOD].hit)
        self.assertTrue(figs[self.GOOD].w > 0 and os.path.getsize(figs[self.GOOD].png) > 100)
        files = {f: os.path.getmtime(os.path.join(diagrams.CACHE, f)) for f in os.listdir(diagrams.CACHE)}
        edited = self.GOOD.replace("one", "uno")
        figs2, errs = diagrams.render_all(self.r, {edited: "a", other: "b"})
        self.assertEqual(errs, [])
        self.assertFalse(figs2[edited].hit, "the edited diagram is drawn again")
        self.assertTrue(figs2[other].hit, "the unrelated diagram comes from the cache")
        for f in (figs[other].svg, figs[other].png):
            self.assertEqual(files[os.path.basename(f)], os.path.getmtime(f), "and its files were not touched")
        self.assertEqual(len(diagrams.orphans(figs2)), 2, "the old figure's two files are orphans")
        diagrams.prune(figs2)
        self.assertEqual(diagrams.orphans(figs2), [])

    def test_a_syntax_error_is_reported_and_leaves_no_figure(self):
        bad = "sequenceDiagram\n    A->>B: one; two"
        figs, errs = diagrams.render_all(self.r, {bad: "src/x/README.md, section '## Program Flow'"})
        self.assertEqual(len(errs), 1)
        self.assertIn("src/x/README.md", errs[0])
        self.assertIn("Parse error", errs[0])
        self.assertEqual(os.listdir(diagrams.CACHE), [], "no blank or partial figure is left behind")

    SEQ = "sequenceDiagram\n    accTitle: T\n    accDescr: D\n    participant A\n    participant B\n    A->>B: hello\n    Note over A,B: a note"
    STATE = "stateDiagram-v2\n    accTitle: T\n    accDescr: D\n    [*] --> One\n    One --> Two: go\n    Two --> [*]"

    def test_the_svg_is_light_for_pdf_viewers(self):
        """No centered text and no half-transparent shapes: WeasyPrint turns each into a PDF transparency group, and Edge's viewer
        (PDFium) draws every group into an off-screen bitmap, so a book full of figures showed white pages for a long time."""
        import re, shutil, subprocess
        figs, errs = diagrams.render_all(self.r, {self.GOOD: "a", self.SEQ: "b", self.STATE: "c"})
        self.assertEqual(errs, [])
        for src, fig in figs.items():
            svg = read(fig.svg)
            self.assertNotIn(b'text-anchor="middle"', svg, fig.family)
            if shutil.which("weasyprint"):
                html, pdf = fig.svg + ".html", fig.svg + ".pdf"
                with open(html, "w", encoding="utf-8") as f:
                    f.write("<html><body style='margin:0'>" + svg.decode("utf-8") + "</body></html>")
                subprocess.run(["weasyprint", "-q", html, pdf], check=True, capture_output=True)
                with open(pdf, "rb") as f:
                    data = f.read()
                self.assertEqual(len(re.findall(rb"/S /Transparency", data)), 0, fig.family + ": the PDF has transparency groups")
                self.assertEqual(len(re.findall(rb"/PatternType", data)), 0, fig.family + ": the PDF has gradient patterns")

    def test_comparison_glyphs_survive_the_svg_and_flattening(self):
        import xml.etree.ElementTree as ET

        source = """flowchart TD
    A["total #gt; 40?"] --> B["total < 40?"]
    B --> C["total ≥ 41?"] --> D["total ≤ 40?"]
"""
        expected = {"total > 40?", "total < 40?", "total ≥ 41?", "total ≤ 40?"}
        path = os.path.join(diagrams.CACHE, "comparators.svg")
        self.r.run(source, path)

        def labels():
            return {"".join(node.itertext()) for node in ET.parse(path).iter("{http://www.w3.org/2000/svg}text")}

        self.assertEqual(labels(), expected)
        self.r.flatten(path)
        self.assertEqual(labels(), expected)

    def test_the_output_is_the_same_twice(self):
        a, _ = diagrams.render_all(self.r, {self.GOOD: "a"})
        first = read(a[self.GOOD].svg)
        for f in os.listdir(diagrams.CACHE):
            os.remove(os.path.join(diagrams.CACHE, f))
        b, _ = diagrams.render_all(self.r, {self.GOOD: "a"})
        self.assertEqual(first, read(b[self.GOOD].svg))

    # Mermaid draws some shapes (the stadium A(["..."]) is the common one) with rough.js, which is random unless seeded.
    # mermaid-config.json sets handDrawnSeed; without it a fresh draw of such a diagram is not byte-identical to the last,
    # and the committed PDFs and EPUBs could only be reproduced from the exact diagram cache that built them.
    SHAPES = ("flowchart TD\n    accTitle: T\n    accDescr: D\n"
              "    A([start]) --> B{{decide}} --> C[(store)] --> D((ring)) --> E[[call]] --> F{test}\n"
              "    F -->|yes| G([end])")

    def test_every_node_shape_draws_the_same_twice_from_a_cold_cache(self):
        first = {}
        for attempt in (1, 2):
            for f in os.listdir(diagrams.CACHE):
                os.remove(os.path.join(diagrams.CACHE, f))
            figs, errors = diagrams.render_all(self.r, {self.SHAPES: "a"})
            self.assertEqual(errors, [])
            fig = figs[self.SHAPES]
            drawn = (read(fig.svg), open(fig.png, "rb").read())
            if attempt == 1:
                first = drawn
            else:
                self.assertEqual(first[0], drawn[0], "the SVG changed between two cold draws: is handDrawnSeed still set in mermaid-config.json?")
                self.assertEqual(first[1], drawn[1], "the PNG changed between two cold draws")

    def test_a_spanish_diagram_with_accents_and_inverted_marks_renders_and_keeps_its_labels(self):
        import xml.etree.ElementTree as ET
        src = 'flowchart TD\n    accTitle: Pie\n    accDescr: Texto\n    A["¿total mayor que 40?"] --> B["¡Se acabó! Sí, más de 40"]'
        figs, errs = diagrams.render_all(self.r, {src: "src/x/README.md"})
        self.assertEqual(errs, [])
        texts = {"".join(n.itertext()) for n in ET.parse(figs[src].svg).iter("{http://www.w3.org/2000/svg}text")}
        self.assertEqual(texts, {"¿total mayor que 40?", "¡Se acabó! Sí, más de 40"})

    def test_the_config_seeds_the_hand_drawn_randomness(self):
        with open(diagrams.CONFIG, encoding="utf-8") as f:
            self.assertIsInstance(json.load(f).get("handDrawnSeed"), int)


if __name__ == "__main__":
    unittest.main(verbosity=1)
