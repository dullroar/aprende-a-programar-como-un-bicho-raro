#!/usr/bin/env python3
"""negative: proof that the release gates can FAIL (plan 10.2). One catalog of throwaway mutations.

  python3 -I tools/negative.py              run the control and every fixture; exit 0 only if the control is clean
                                            and EVERY fixture makes its gate fail with the expected check id
  python3 -I tools/negative.py --list       print the catalog (plan item, id, expected check)
  python3 -I tools/negative.py --show ID    print the problems one fixture produces

Each fixture is a mutation of a CONTROL that passes, applied to a throwaway copy that lives only in memory or under
translation/work/negative/ (git-ignored). The mutation is judged by the same function that `verify.py --release`
calls (so a green control and a red fixture prove the gate is armed):

  kind "file"   a synthetic English file and its hand-written Spanish version, turned into a PO and applied, then
                verify.check_file(release=True): the per-file check of --release (I1 to I16);
  kind "lock"   a copy of a frozen file and a manifest row, then verify.check_lock (I13);
  kind "path"   a tiny synthetic tree and its path map, then pathcheck (I17 to I20, plan 5.6);
  kind "tool"   the localized generator or linter named in the fixture, fed a mutated Spanish text.

verify.run_release calls run_all() as the check "negative fixtures", so a gate that stops failing (a disarmed gate)
fails the release. A fixture that does not fail is a finding, never something to loosen.

Exit codes: 0 all good, 1 a fixture did not fail or the control is not clean, 2 usage error.
"""
import contextlib
import copy
import os
import re
import shutil
import sys
from collections import namedtuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
sys.path.insert(0, os.path.join(ROOT, "lessons", "book"))
sys.path.insert(0, os.path.join(ROOT, "lessons", "curriculum"))

REL = "lessons/negative-fixture.md"
SPANISH_REPO = "https://github.com/dullroar/aprende-a-programar-como-un-bicho-raro"
APL_LINE = "Alive←40≥T"      # the real sentinel "APL stop rule" of pdf_sentinels: Alive←40≥T
WORK = os.path.join(ROOT, "translation", "work", "negative")

Fixture = namedtuple("Fixture", "id item title kind expect run")

# ------------------------------------------------------------------------------------------ the control pair

EN = """---
name: Timecards fixture
assurance: guaranteed
kind: concept
---

# Timecards and the stop rule

The total must be **strictly greater than 40** to stop. A total of exactly 40 continues.

The program prints the card categories `Meetings`, `Coding`, `Debugging` and `Learning`. The loop stops when `total > 40` is true.

See [the evidence questions](#evidence-questions) for the checks.

This paragraph explains why the order of the cards does not change the result.

## Evidence questions

Ask what evidence shows each claim.

```mermaid
flowchart TB
    accTitle: The stop rule
    accDescr: A decision diagram. The loop adds a card and compares the total with 40. If the total is strictly greater than 40 the loop stops. Otherwise the loop continues.
    A["Add a card"] --> D{"Is the total greater than 40?"}
    D -- "yes" --> S(["Stop"])
    D -- "no" --> A
```
"""

ES = """---
name: Timecards fixture
assurance: guaranteed
kind: concept
---

# La tarjeta de horas y la regla de parada

El total debe ser **estrictamente mayor que 40** para detenerse. Un total de exactamente 40 continúa.

El programa imprime las categorías de tarjeta `Meetings`, `Coding`, `Debugging` y `Learning`. El bucle se detiene cuando `total > 40` es verdadero.

Mira [las preguntas de evidencia](#evidence-questions) para ver las comprobaciones.

Este párrafo explica por qué el orden de las tarjetas no cambia el resultado.

## Preguntas de evidencia

Pregunta qué evidencia respalda cada afirmación.

```mermaid
flowchart TB
    accTitle: La regla de parada
    accDescr: Un diagrama de decisión. El bucle agrega una tarjeta y compara el total con 40. Si el total es estrictamente mayor que 40, el bucle se detiene. De lo contrario, el bucle continúa.
    A["Agrega una tarjeta"] --> D{"¿El total pasa de 40?"}
    D -- "sí" --> S(["Detener"])
    D -- "no" --> A
```
"""


# The second control pair (item 13, review lints I21 to I26): names that stay literal in labels, a range with its unit, one
# gloss, a typographic percent, a table and a diagram whose edge label has no parenthesis. <NB> is a non-breaking space.
EN_B = """---
name: Review fixture
assurance: guaranteed
kind: concept
---

# Chaining and units

Each card has 10 to 19 hours per card. The target is 30% of the week.

Run it in the sandbox.

Use the sandbox again.

| Name | Meaning |
|------|---------|
| `x` | one |

```text
out
```

```mermaid
flowchart TB
    accTitle: The chain
    accDescr: A flowchart. The also chain runs, then over-40 leaves a flag.
    A["also chain: lock, add hours"] --> B{"over-40? leaves a flag"}
    B -->|yes| C["where: prefix sum is 40 or less"]
    B -->|no| D["from persisted in the query"]
    C --> E["step returns False"]
    D --> E
```
"""

ES_B = """---
name: Review fixture
assurance: guaranteed
kind: concept
---

# Encadenar y medir

Cada tarjeta tiene de 10 a 19 horas por tarjeta. El objetivo es el 30<NB>% de la semana.

Ejecútalo en el entorno aislado (*sandbox*).

Usa de nuevo el entorno aislado.

| Nombre | Significado |
|--------|-------------|
| `x` | uno |

```text
out
```

```mermaid
flowchart TB
    accTitle: La cadena
    accDescr: Un diagrama de flujo. La cadena also corre y luego over-40? deja una bandera.
    A["cadena de also: bloquea, suma horas"] --> B{"over-40? deja una bandera"}
    B -->|sí| C["where: la suma acumulada es 40 o menos"]
    B -->|no| D["from persisted in de la consulta de EF: pasamos a objetos"]
    C --> E["step devuelve False"]
    D --> E
```
""".replace("<NB>", chr(0xA0))


def file_b_fixture(old, new, count=1, after=False):
    """A mutation of the second control's Spanish text: the control with `old` replaced by `new` (a stale fixture is loud).
    `after` edits the finished file instead (a hand edit that the PO layer would refuse, such as a dropped table cell)."""
    old, new = old.replace("<NB>", chr(0xA0)), new.replace("<NB>", chr(0xA0))

    def run():
        if old not in ES_B:
            raise AssertionError("fixture is stale: %r is not in the control" % old)
        if after:
            return file_problems(ES_B, EN_B, after=swap(old, new, count))
        return file_problems(ES_B.replace(old, new, count), EN_B)
    return run


# ------------------------------------------------------------------------------------------ plumbing

def build_po(en_text, es_text, rel=REL):
    """A PO whose msgstr are the MASKED segments of the hand-written Spanish text, paired by position.
    A Spanish text with fewer segments leaves the last entries empty (untranslated)."""
    import apply as apply_mod
    import segment
    en = segment.Segmentation(en_text, rel)
    es = [s.masked for s in segment.Segmentation(es_text, rel).segments()]
    po = apply_mod.new_po(en, rel)
    for i, entry in enumerate(po):
        if i < len(es):
            entry.msgstr = es[i]
    return po


_ENV = {}


def env():
    if "env" not in _ENV:
        import verify
        _ENV["env"] = verify.Env(ROOT)
    return _ENV["env"]


def file_problems(es_source, en_text=EN, after=None, ctx=None, po_edit=None, rel=REL):
    """What `verify.py --release` reports for one authored file: the Spanish text is turned into a PO, applied to the
    English text, and the finished file is checked. `after` edits the finished file (a hand edit after the PO),
    `po_edit` edits the PO, `ctx` replaces the invariants context."""
    import apply as apply_mod
    import verify
    e = env()
    po = build_po(en_text, es_source, rel)
    if po_edit:
        po_edit(po)
    try:
        finished, _ = apply_mod.apply_text(en_text, po, rel, e.cat, strict=False)
    except apply_mod.ApplyError as err:                  # the PO is refused before any file exists
        return ["I2 PO cannot be applied: %s" % err] + verify.check_file(rel, en_text, None, po, ctx or e.ctx, True, e.cat, verify.layout_remap(rel, ROOT))
    if after:
        finished = after(finished)
    return verify.check_file(rel, en_text, finished, po, ctx or e.ctx, True, e.cat, verify.layout_remap(rel, ROOT))


def swap(old, new, count=1):
    """A mutation of the Spanish source that must change something (a stale fixture must not pass silently)."""
    def run(text):
        if old not in text:
            raise AssertionError("fixture is stale: %r is not in the control" % old)
        return text.replace(old, new, count)
    return run


def file_fixture(es_edit=None, after=None, en_edit=None, po_edit=None, ctx_edit=None):
    def run():
        en = en_edit(EN) if en_edit else EN
        es = es_edit(ES) if es_edit else ES
        ctx = ctx_edit(copy.copy(env().ctx)) if ctx_edit else None
        return file_problems(es, en, after, ctx, po_edit)
    return run


def stale_fragment_problems(rel="src/GoChallenge1/README.md"):
    """verify's report for a REAL translated file whose links into a translated heading still carry the English fragment
    (renamed paths are remapped, anchors are not): the PO applied through anchors.layout_text is the only text that passes."""
    import apply as apply_mod
    import enpath
    import verify
    e = env()
    en = verify.english_text(e.cfg, rel)
    po = apply_mod.load_po(apply_mod.po_path_for(rel))
    applied, _ = apply_mod.apply_text(en, po, rel, e.cat, strict=False)
    stale = enpath.remap_text(applied, rel)
    return verify.check_file(rel, en, stale, po, e.ctx, False, e.cat, verify.layout_remap(rel, ROOT))


def lock_problems(mutate, rel="src/forth/timecards.fs"):
    """check_lock on a one-file mini repo: a real frozen file and its row of translation/locked-code.sha256."""
    import lock_code
    import verify
    root = os.path.join(WORK, "lock")
    shutil.rmtree(root, ignore_errors=True)
    for r in (rel, lock_code.MANIFEST):
        os.makedirs(os.path.dirname(os.path.join(root, r)), exist_ok=True)
    import enpath
    shutil.copyfile(enpath.load(ROOT).full(rel), os.path.join(root, rel))    # the mini repo keeps English names
    with open(os.path.join(ROOT, lock_code.MANIFEST), encoding="utf-8") as f:
        row = next(ln for ln in f if ln.rstrip().endswith("  " + rel))
    with open(os.path.join(root, lock_code.MANIFEST), "w", encoding="utf-8", newline="") as f:
        f.write(row)
    mutate(os.path.join(root, rel))
    try:
        return verify.check_lock(root)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def flip_byte(path):
    with open(path, "rb") as f:
        data = bytearray(f.read())
    data[len(data) // 2] ^= 0x01
    with open(path, "wb") as f:
        f.write(bytes(data))


def set_anchor_map(table):
    def edit(ctx):
        ctx.anchor_map = table
        return ctx
    return edit


def lock_fixture(mutate):
    return lambda: lock_problems(mutate)


def delete_file(path):
    os.remove(path)


# ---- generator and linter checks, fed mutated TEXT. They run on the pinned English sources (always English, whatever
# the repository holds), so a fixture keeps its meaning after the Spanish files replace the English ones.

@contextlib.contextmanager
def language(lang, *modules):
    """Switch the word tables of `modules` to `lang` and put the previous language back, whatever happens."""
    saved = [(m, m.LANG) for m in modules]
    try:
        for m in modules:
            m.set_language(lang)
        yield
    finally:
        for m, old in reversed(saved):
            m.set_language(old)


def clone():
    path = env().cfg.get("english_clone_path")
    if not path or not os.path.isdir(path):
        raise RuntimeError("the English clone (english_clone_path in loop/CONFIG.yaml) is missing")
    return path


def clone_text(rel):
    with open(os.path.join(clone(), rel), encoding="utf-8", newline="") as f:
        return f.read()


GUIDE = "languages/cobol.md"


def guide_problems(edit=None):
    """study_guides.check_guide on the pinned English COBOL guide, edited by `edit(text)`."""
    import study_guides
    text = clone_text("lessons/study-guides/" + GUIDE)
    with language("en", study_guides):
        return study_guides.check_guide(GUIDE, edit(text) if edit else text, clone())


def guide_fixture(edit):
    return lambda: guide_problems(edit)


def subst(pattern, new, flags=0):
    """A regex edit that must change something."""
    def run(text):
        out, n = re.subn(pattern, new, text, count=1, flags=flags)
        if not n:
            raise AssertionError("fixture is stale: %r is not in the control" % pattern)
        return out
    return run


def drop_labels(text):
    import study_guides
    for label in study_guides.ASSURANCE_LABELS:
        text = re.sub(re.escape(label), "assured", text, flags=re.I)
    return text


def curriculum_module():
    import test_curriculum
    return test_curriculum


def curriculum_problems(edit=None, lang="en"):
    """curriculum.build.check_curriculum on the pinned English curriculum (lang en) or on the synthetic Spanish one (es)."""
    tc = curriculum_module()
    with language(lang, tc.cb):
        if lang == "en":
            text = clone_text("docs/curriculum.md")
            return tc.cb.check_curriculum(edit(text) if edit else text, clone())
        return tc.cb.check_curriculum(tc.spanish_curriculum(**(edit or {})))


def curriculum_fixture(edit, lang="en"):
    return lambda: curriculum_problems(edit, lang)


def moved_week(text):
    row = next(ln for ln in text.splitlines() if ln.startswith("| 3 |"))
    marker = "| | **W: Weird** | | |\n"
    if marker not in text:
        raise AssertionError("fixture is stale: no W phase row")
    return text.replace(row + "\n", "", 1).replace(marker, marker + row + "\n", 1)


def foreign_link_problems(html):
    """repo_links.foreign_repo_links as the Spanish book check (build.check) calls it."""
    import repo_links
    with language("es", repo_links):
        return ["FOREIGN repository link: " + u for u in repo_links.foreign_repo_links(html)]


def pdf_problems(draw, sentinel=None):
    """lint_pdf on a one-page PDF drawn by `draw(page)`. Returns 'PDF-nnn message' strings for the errors."""
    import json
    import io
    import pymupdf
    import lint_pdf
    from pdf_sentinels import Sentinel
    os.makedirs(WORK, exist_ok=True)
    doc = pymupdf.open()
    try:
        draw(doc.new_page(width=612, height=792), pymupdf)
        path = os.path.join(WORK, "page.pdf")
        report = os.path.join(WORK, "report.json")
        doc.save(path)
    finally:
        doc.close()
    saved = dict(lint_pdf.PROFILES)
    try:
        lint_pdf.PROFILES["book"] = (Sentinel("apl", sentinel),) if sentinel else ()
        with contextlib.redirect_stdout(io.StringIO()):
            status = lint_pdf.main([path, "--json", report, "--profile", "book"])
        with open(report, "rb") as f:
            data = json.load(f)
    finally:
        lint_pdf.PROFILES.clear()
        lint_pdf.PROFILES.update(saved)
    found = [f for d in data["documents"] for f in d["findings"] if f["severity"] == "error"]
    out = ["%s %s" % (f["rule"], f.get("message", "")) for f in found]
    if status and not out:
        out.append("PDF-000 lint_pdf exit %d" % status)
    return out


DEJAVU = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"


def content_right():
    import lint_pdf
    from pdf_layout import read_geometry
    return read_geometry((lint_pdf.HERE / "book.css").read_text(encoding="utf-8")).content[2]


def draw_text(text, x=100, font=None):
    def draw(page, pymupdf):
        if font:
            page.insert_text((x, 120), text, fontname="negfont", fontfile=font)
        else:
            page.insert_text((x, 120), text)
    return draw


def text_ending_at(right, text="XXXX"):
    def draw(page, pymupdf):
        width = pymupdf.get_text_length(text, fontsize=12)
        page.insert_text((right - width, 120), text, fontsize=12)
    return draw


# ------------------------------------------------------------------------------------------ the path invariants

PATH_FILES = {
    "README.md": "authored",
    "CHALLENGE.md": "authored",
    "docs/guide.md": "authored",
    "lessons/README.md": "authored",
    "lessons/intro.md": "authored",
    "lessons/solutions/a.py": "frozen",
    "src/x/main.py": "frozen",
}
PATH_NAMES = {"dirs": {}, "files": {"CHALLENGE.md": "RETO.md", "docs/guide.md": "guia.md",
                                    "lessons/intro.md": "introduccion.md"}, "proper": []}
PATH_TEXTS = {"lessons/solutions/a.py": "print('hi')\n", "src/x/main.py": "# nothing\n"}
PATH_GLOSSARY = {"terms": [{"id": "challenge", "es": "reto"}, {"id": "guide", "es": "guía"},
                           {"id": "intro", "es": "introducción"}],
                 "path_words": [{"en": "guide", "es": "guía"}],
                 "path_function_words": ["de", "y"], "path_proper_names": ["linq"]}


def path_problems(mutate=None):
    """The four path checks (I17 to I20) on a tiny synthetic tree and its computed map, after `mutate(t)` changed it.
    t is a dict: files, texts, names, glossary, docs (working path -> (text, dir)), map_edit (a function that edits the
    computed map in place: a hand-made or stale map)."""
    import copy
    import pathcheck
    import pathmap
    t = {"files": dict(PATH_FILES), "texts": dict(PATH_TEXTS), "names": copy.deepcopy(PATH_NAMES), "map_edit": None,
         "glossary": copy.deepcopy(PATH_GLOSSARY),
         "docs": {"RETO.md": ("See [the guide](docs/guia.md) and [the intro](lessons/introduccion.md).\n", "")}}
    if mutate:
        mutate(t)
    res = pathmap.build(t["files"], lambda p: t["texts"].get(p), t["names"], None)
    result = dict(res["map"])
    if t.get("map_edit"):
        t["map_edit"](result)
    sources = ([(p, x) for p, x in sorted(t["texts"].items()) if t["files"].get(p) == "frozen"], [])
    out = pathcheck.map_problems(t["files"], result, sources)
    out += pathcheck.i18_problems(t["files"], res, t["glossary"])
    present = set(result.values()) | {d for q in result.values() for d in pathmap.ancestors(q)}
    out += pathcheck.i17_problems(t["docs"], lambda p: p in present, {p: q for p, q in result.items() if p != q})
    return out


def path_fixture(mutate):
    return lambda: path_problems(mutate)


# ------------------------------------------------------------------------------------------ the catalog

def catalog():
    """Every fixture of plan 10.2, in the order of the plan. `expect` is the check id that must appear."""
    F = []

    def add(item, ident, title, kind, expect, run):
        F.append(Fixture(ident, item, title, kind, expect, run))

    # 1. > 40 changed to >= 40, or "exactly 40 continues" omitted.
    add(1, "40-code-span-ge", "the code span `total > 40` becomes `total >= 40`", "file", "I13",
        file_fixture(after=swap("`total > 40`", "`total >= 40`")))
    add(1, "40-code-span-dropped", "the translator drops the code span `total > 40`", "file", "I2",
        file_fixture(swap("cuando `total > 40` es verdadero", "cuando el total es mayor que cuarenta")))
    add(1, "40-exact-sentence-dropped", "the sentence 'exactly 40 continues' is omitted", "file", "I3",
        file_fixture(swap(" Un total de exactamente 40 continúa.", "")))
    add(1, "40-banned-stop-phrase", "the rule is rewritten as 'alcanza 40' (a banned stop condition)", "file", "I7",
        file_fixture(swap("El bucle se detiene cuando `total > 40` es verdadero.", "El bucle se detiene cuando el total alcanza 40 y `total > 40` es verdadero.")))
    add(1, "40-english-rule-kept", "the exactly-40 sentence is left in English", "file", "I9",
        file_fixture(swap("El total debe ser **estrictamente mayor que 40** para detenerse. Un total de exactamente 40 continúa.",
                          "The total must be **strictly greater than 40** to stop. A total of exactly 40 continues.")))

    # 2. One byte changed in a frozen challenge file.
    add(2, "frozen-byte-flipped", "one byte of src/forth/timecards.fs is flipped", "lock", "I13", lock_fixture(flip_byte))
    add(2, "frozen-file-deleted", "src/forth/timecards.fs is deleted", "lock", "I13", lock_fixture(delete_file))

    # 3. A YAML enum translated or an entry ID changed.
    add(3, "enum-translated", "front matter 'assurance: guaranteed' becomes 'garantizado'", "file", "I6",
        file_fixture(after=swap("assurance: guaranteed", "assurance: garantizado")))
    add(3, "enum-key-translated", "front matter key 'assurance' becomes 'garantia'", "file", "I6",
        file_fixture(after=swap("assurance: guaranteed", "garantia: guaranteed")))
    add(3, "entry-id-changed", "an entry macro [[entry:m4]] becomes [[entry:m5]]", "file", "I2",
        file_fixture(en_edit=swap("See [the", "Entry [[entry:m4]]. See [the"),
                     es_edit=swap("Mira [las", "Entrada [[entry:m4]]. Mira [las"),
                     after=swap("[[entry:m4]]", "[[entry:m5]]")))

    # 4. accDescr missing or still English; a swapped branch edge; a drifted diagram copy.
    add(4, "accdescr-removed", "the accDescr line is removed from the diagram", "file", "I5",
        file_fixture(after=swap("    accDescr: Un diagrama de decisión. El bucle agrega una tarjeta y compara el total con 40. "
                          "Si el total es estrictamente mayor que 40, el bucle se detiene. De lo contrario, el bucle continúa.\n", "")))
    add(4, "accdescr-english", "the accDescr line stays in English", "file", "I9",
        file_fixture(swap("accDescr: Un diagrama de decisión. El bucle agrega una tarjeta y compara el total con 40. "
                          "Si el total es estrictamente mayor que 40, el bucle se detiene. De lo contrario, el bucle continúa.",
                          "accDescr: A decision diagram. The loop adds a card and compares the total with 40. "
                          "If the total is strictly greater than 40 the loop stops. Otherwise the loop continues.")))
    add(4, "branch-edge-swapped", "the yes and no branches of the decision are swapped", "file", "I5",
        file_fixture(after=swap('D -- "sí" --> S(["Detener"])\n    D -- "no" --> A', 'D -- "sí" --> A\n    D -- "no" --> S(["Detener"])')))
    add(4, "node-id-translated", "the node id D is renamed in one edge only", "file", "I5",
        file_fixture(after=swap('D -- "no" --> A', 'E -- "no" --> A')))
    add(4, "diagram-copy-drifted", "a guide's diagram copy differs from the canonical Program Flow", "tool", "canonical source",
        guide_fixture(subst(r'A\["SET-UP, OPEN-SCRIPT', 'A["SET UP, OPEN SCRIPT')))
    add(4, "guide-accdescr-removed", "a guide diagram loses its accDescr", "tool", "accDescr",
        guide_fixture(subst(r"^\s*accDescr:.*\n", "", re.M)))
    add(4, "guide-acctitle-removed", "a guide diagram loses its accTitle", "tool", "accTitle",
        guide_fixture(subst(r"^\s*accTitle:.*\n", "", re.M)))

    # 5. A missing guide evidence question, wrong assurance label, missing section.
    add(5, "guide-evidence-question-missing", "the **Evidence.** self-check question is renamed", "tool", "**Evidence.**",
        guide_fixture(subst(r"\*\*Evidence\.\*\*", "**Proof.**")))
    add(5, "guide-assurance-label-wrong", "every assurance label is replaced by an invented one", "tool", "must label behavior",
        guide_fixture(drop_labels))
    add(5, "guide-section-missing", "the section 'Trace one run' is renamed", "tool", "exactly the template",
        guide_fixture(subst(r"^## Trace one run$", "## Trace", re.M)))
    add(5, "guide-exact-40-omitted", "the guide never says that exactly 40 continues", "tool", "exactly 40",
        guide_fixture(lambda text: text.replace("exactly 40", "forty")))
    add(5, "guide-safety-model-dropped", "the DEMO ONLY safety statement is removed", "tool", "safety model",
        guide_fixture(lambda text: text.replace("DEMO ONLY", "demo")))

    # 6. A missing week, wrong exercise ID, changed phase order, duplicated phase letter, a surviving English letter.
    add(6, "curriculum-week-missing", "week 9 is numbered 99", "tool", "weeks 1 to 16",
        curriculum_fixture(swap("| 9 | What does a closure", "| 99 | What does a closure")))
    add(6, "curriculum-week-under-wrong-phase", "week 3 is moved under phase W", "tool", "week 3 is under phase",
        curriculum_fixture(moved_week))
    add(6, "curriculum-phase-letter-duplicated", "phase E is labeled W as well", "tool", "phase rows",
        curriculum_fixture(swap("| | **E: Execution**", "| | **W: Execution**")))
    add(6, "curriculum-exercise-id-wrong", "an exercise link text A1 becomes Z9 while the anchor stays", "tool", "exercise",
        curriculum_fixture(swap("[A1](../lessons/exercises.md#a1-read-the-rows-verified)", "[Z9](../lessons/exercises.md#a1-read-the-rows-verified)")))
    add(6, "curriculum-es-english-letter-survives", "the Spanish phase row keeps the English letter W", "tool", "phase rows",
        curriculum_fixture({"row_b": "| | **W: Bicho raro** | | |"}, "es"))
    add(6, "curriculum-es-english-acronym-survives", "the Spanish text uses the acronym WEIRD", "tool", "English acronym",
        curriculum_fixture({"sentence": "El curso usa WEIRD como regla."}, "es"))
    add(6, "curriculum-es-diagram-letter-survives", "the Spanish diagram node keeps the letter E", "tool", "labeled with the letter",
        curriculum_fixture({"node_e": 'E["E: Interpreta, semanas 3 a 6"]'}, "es"))
    add(6, "phase-literal-letter-and-name", "a literal 'B: Bicho raro' is written next to the phase macros", "file", "I14",
        file_fixture(en_edit=swap("Ask what", "In phase {{phase.1.letter}}: {{phase.1.name}}, ask what"),
                     es_edit=swap("Pregunta qué", "En la fase {{phase.1.letter}}: {{phase.1.name}} (B: Bicho raro), pregunta qué")))
    add(6, "phase-english-acronym-survives", "the English acronym WEIRD survives in Spanish prose", "file", "I14",
        file_fixture(es_edit=swap("Pregunta qué", "Con WEIRD pregunta qué")))
    add(6, "phase-english-letter-and-name-survive", "the Spanish text says 'W: Weird'", "file", "I14",
        file_fixture(es_edit=swap("Pregunta qué", "En la fase W: Weird pregunta qué")))
    add(6, "phase-macro-dropped-for-letter", "the phase macro is replaced by a literal letter in Spanish prose", "file", "I2",
        file_fixture(en_edit=swap("Ask what", "In phase {{phase.1.letter}}, ask what"),
                     es_edit=swap("Pregunta qué", "En la fase B, pregunta qué")))

    # 7. A paragraph silently deleted from an otherwise excellent file.
    add(7, "paragraph-deleted-before-po", "a paragraph is missing from the Spanish text", "file", "I16",
        file_fixture(swap("Este párrafo explica por qué el orden de las tarjetas no cambia el resultado.\n\n", "")))
    add(7, "paragraph-deleted-after-po", "a paragraph is deleted by hand from the finished file", "file", "I16",
        file_fixture(after=swap("Este párrafo explica por qué el orden de las tarjetas no cambia el resultado.\n\n", "")))
    add(7, "po-entry-dropped", "a PO entry is dropped", "file", "I16", file_fixture(po_edit=lambda po: po.remove(po[3])))

    # 8. A link fragment broken only on GitHub while the PDF link still works.
    add(8, "fragment-not-remapped", "the heading is translated but the link keeps the English fragment", "file", "I4",
        file_fixture(ctx_edit=set_anchor_map({"#evidence-questions": "#preguntas-de-evidencia"})))

    add(8, "stale-fragment-in-a-real-file", "a translated README keeps the English fragment of a link into a translated heading", "file", "I16",
        stale_fragment_problems)

    add(8, "guide-link-fragment-broken", "a guide link to an exercise heading no longer resolves", "tool", "missing heading",
        guide_fixture(subst(r"\(\.\./\.\./exercises\.md#a1-read-the-rows-verified\)", "(../../exercises.md#a1-no-such-heading)")))

    # 9. A PDF or EPUB link pointing at the English repo.
    add(9, "link-to-english-repo", "a Spanish document links into the English repository", "tool", "FOREIGN repository link",
        lambda: foreign_link_problems(
            '<a href="%s/blob/main/src/apl/README.md">ok</a><a href="https://github.com/dullroar/learn-programming-the-weird-way/blob/master/src/apl/README.md">bad</a>' % SPANISH_REPO))
    add(9, "image-from-english-repo", "a Spanish document embeds an image from the English repository", "tool", "FOREIGN repository link",
        lambda: foreign_link_problems('<img src="https://github.com/dullroar/learn-programming-the-weird-way/raw/master/a.png">'))

    # 10. APL glyphs missing, a clipped diagram caption, code beyond margins.
    add(10, "pdf-apl-glyph-missing", "the APL line is drawn with a font that has no APL glyphs", "tool", "PDF-010",
        lambda: pdf_problems(draw_text(APL_LINE), APL_LINE))
    add(10, "pdf-caption-beyond-page-edge", "text runs past the physical page edge", "tool", "PDF-003",
        lambda: pdf_problems(text_ending_at(612 + 10)))
    add(10, "pdf-code-beyond-margin", "text runs past the content margin", "tool", "PDF-004",
        lambda: pdf_problems(text_ending_at(content_right() + 10)))

    # 11. A translated card category in prose where the program prints English.
    add(11, "card-category-translated", "`Meetings` is written 'Reuniones' where the program prints Meetings", "file", "I13",
        file_fixture(after=swap("`Meetings`", "`Reuniones`")))
    add(11, "card-category-in-prose", "a prose mention of the category Coding is translated", "file", "I2",
        file_fixture(en_edit=swap("Ask what", "The Coding cards come first. Ask what"),
                     es_edit=swap("Pregunta qué", "Las tarjetas de Programación van primero. Pregunta qué")))

    # 12. Plan 5.6: the Spanish file names (invariants I17 to I20).
    def stale_link(t):
        t["docs"]["RETO.md"] = ("See [the guide](docs/guide.md).\n", "")          # still the old English name

    def two_to_one(t):
        t["map_edit"] = lambda m: m.update({"docs/guide.md": "RETO.md"})

    def frozen_mention(t):
        t["texts"]["lessons/solutions/a.py"] = "open('lessons/intro.md')\n"        # pins the path in the real rules
        t["map_edit"] = lambda m: m.update({"lessons/intro.md": "lessons/introduccion.md"})

    def readme_renamed(t):
        t["map_edit"] = lambda m: m.update({"lessons/README.md": "lessons/LEEME.md"})

    def english_word_kept(t):
        t["names"]["files"]["docs/guide.md"] = "guide-and-patterns.md"

    add(12, "path-link-old-english-name", "a link still points at the old English file name", "path", "I17",
        path_fixture(stale_link))
    add(12, "path-two-files-one-name", "two files are mapped to one Spanish name", "path", "I20",
        path_fixture(two_to_one))
    add(12, "path-frozen-file-mentions-renamed", "a path a frozen file mentions is renamed", "path", "I19",
        path_fixture(frozen_mention))
    add(12, "path-readme-renamed", "README.md is renamed", "path", "I20", path_fixture(readme_renamed))
    add(12, "path-english-word-kept", "a renamed file keeps English words in its name", "path", "I18",
        path_fixture(english_word_kept))
    # 13. Editorial-review lints (review-decisions-2026-11-20.md Part E): identifiers, units, diagrams, glosses, typography, layout.
    add(13, "ident-also-translated", "`also` in a label becomes 'también'", "file", "I21",
        file_b_fixture('"cadena de also: bloquea, suma horas"', '"También encadena: bloquea, suma horas"'))
    add(13, "ident-step-translated", "`step` in a label becomes 'paso'", "file", "I21",
        file_b_fixture('"step devuelve False"', '"paso devuelve False"'))
    add(13, "ident-where-translated", "`where` in a label becomes 'donde'", "file", "I21",
        file_b_fixture('"where: la suma acumulada', '"donde: la suma acumulada'))
    add(13, "ident-from-persisted-in-translated", "`from persisted in` becomes 'de persistido en'", "file", "I21",
        file_b_fixture('"from persisted in de la consulta de EF', '"de persistido en la consulta de EF'))
    add(13, "ident-over40-question-mark-dropped", "`over-40?` loses its question mark", "file", "I21",
        file_b_fixture('"over-40? deja una bandera"', '"over-40 deja una bandera"'))
    add(13, "ident-over40-accdescr-translated", "`over-40?` in the accDescr is translated", "file", "I21",
        file_b_fixture("luego over-40? deja", "luego sobre-40? deja"))
    add(13, "ident-over40-accdescr-question-mark-dropped", "`over-40?` in the accDescr loses its question mark (B2)", "file", "I21",
        file_b_fixture("luego over-40? deja", "luego over-40 deja"))
    add(13, "units-range-takes-cards", "'de 10 a 19 horas por tarjeta' becomes 'de 10 a 19 tarjetas'", "file", "I22",
        file_b_fixture("de 10 a 19 horas por tarjeta", "de 10 a 19 tarjetas"))
    add(13, "units-range-without-unit", "the 10 to 19 range loses its unit", "file", "I22",
        file_b_fixture("de 10 a 19 horas por tarjeta", "de 10 a 19"))
    add(13, "diagram-edge-label-parenthesis", "an edge label carries an unquoted parenthesis", "file", "I23",
        file_b_fixture("B -->|sí| C", "B -->|sí (parar)| C"))
    add(13, "gloss-repeated", "the sandbox gloss is written a second time in the same file", "file", "I24",
        file_b_fixture("Usa de nuevo el entorno aislado.", "Usa de nuevo el entorno aislado (*sandbox*)."))
    add(13, "guarantee-added", "the translator adds 'donde un error no daña tu equipo'", "file", "I24",
        file_b_fixture("Ejecútalo en el entorno aislado (*sandbox*).",
                       "Ejecútalo en el entorno aislado (*sandbox*), donde un error no daña tu equipo."))
    add(13, "typography-percent-plain-space", "'30<NB>%' becomes '30 %' with a plain space", "file", "I25",
        file_b_fixture("30<NB>%", "30 %"))
    add(13, "typography-comma-before-y", "a comma is written before a simple 'y'", "file", "I25",
        file_b_fixture("Usa de nuevo el entorno aislado.", "Usa el entorno aislado, y sal."))
    add(13, "layout-table-cell-dropped", "a table row loses a cell", "file", "I26",
        file_b_fixture("| `x` | uno |", "| `x` |", after=True))
    add(13, "layout-fence-kind-changed", "a fenced block changes its kind (text to console)", "file", "I26",
        file_b_fixture("```text\nout", "```console\nout", after=True))
    return F


# ------------------------------------------------------------------------------------------ the runner

def run_fixture(fx):
    """(problems, error): the problems the gate reports for this fixture; `error` when the fixture itself is broken."""
    try:
        return list(fx.run()), None
    except Exception as e:  # a stale fixture must be loud, not a pass
        return [], "%s: %s" % (type(e).__name__, e)


def control_problems():
    """Every control must be clean: a gate that fails on the good input proves nothing about the bad input."""
    out = ["file: " + p for p in file_problems(ES)]
    out += ["file B: " + p for p in file_problems(ES_B, EN_B)]
    out += ["guide: " + p for p in guide_problems()]
    out += ["curriculum en: " + p for p in curriculum_problems()]
    out += ["curriculum es: " + p for p in curriculum_problems({}, "es")]
    out += ["links: " + p for p in foreign_link_problems('<a href="%s/blob/main/x.md">ok</a><a href="#here">x</a>' % SPANISH_REPO)]
    out += ["pdf apl: " + p for p in pdf_problems(draw_text(APL_LINE, font=DEJAVU), APL_LINE)]
    out += ["pdf margin: " + p for p in pdf_problems(text_ending_at(content_right() - 5))]
    out += ["lock: " + p for p in lock_problems(lambda path: None)]
    out += ["paths: " + p for p in path_problems()]
    return out


def run_all():
    """Problems for verify.py --release: the control must be clean and every fixture must fail as expected."""
    out = ["control: " + p for p in control_problems()]
    for fx in catalog():
        problems, err = run_fixture(fx)
        if err:
            out.append("fixture %s is broken: %s" % (fx.id, err))
        elif not problems:
            out.append("fixture %s (plan %s item %d: %s) did not fail: the gate is disarmed"
                       % (fx.id, "10.2" if fx.item <= 11 else "5.6" if fx.item == 12 else "the editorial review, Part E", fx.item, fx.title))
        elif not any(fx.expect in p for p in problems):
            out.append("fixture %s failed, but not with %s: %s" % (fx.id, fx.expect, problems[0]))
    return out


def main(argv):
    args = argv[1:]
    if args and args[0] == "--list":
        for fx in catalog():
            print("%2d  %-28s %-5s %-6s %s" % (fx.item, fx.id, fx.kind, fx.expect, fx.title))
        return 0
    if args and args[0] == "--show" and len(args) == 2:
        fx = next((f for f in catalog() if f.id == args[1]), None)
        if fx is None:
            print("no fixture %s" % args[1])
            return 2
        problems, err = run_fixture(fx)
        print("\n".join(problems) or "(no problems)")
        if err:
            print("ERROR " + err)
        return 0
    if args:
        print(__doc__.split("Exit codes")[0].rstrip())
        return 2
    problems = run_all()
    items = sorted({f.item for f in catalog()})
    if problems:
        print("\n".join(problems))
        print("negative: FAIL (%d problem(s))" % len(problems))
        return 1
    print("negative: OK (control clean; %d fixtures all fail as expected; plan 10.2 items %s)" % (len(catalog()), items))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
