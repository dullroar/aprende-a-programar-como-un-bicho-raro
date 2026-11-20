#!/usr/bin/env python3
"""Build the curriculum (docs/curriculum.md) as its own document set: one HTML file, one EPUB and one PDF.

    python lessons/curriculum/build.py            # writes curriculum.pdf and curriculum.epub in the repository root
    python lessons/curriculum/build.py --release  # build and require the PDF layout and content checks
    python lessons/curriculum/build.py --check    # lint the curriculum, build the HTML and verify every internal link resolves
    python lessons/curriculum/build.py --artifacts-dir DIR   # write the PDF and EPUB to DIR (used to test reproducibility)

The words the checks depend on come from the locale catalog (lessons/book/locale/<lang>.yaml): the printed chapter label ("Ch" or "Cap."),
the sentence limit, the register rule, and the acronym, the phase letters and their weeks. The language is BOOK_LANG (default "en").

The curriculum is one hand-written Markdown file. This script does not write prose. It only
  * checks it with check_curriculum() below (links, the one diagram, the plan, the house style and the length), and
  * gives it to the book's own pipeline, lessons/book/build.py, which does the link rewriting, the Mermaid rendering, the Pandoc call,
    the stylesheet and the reproducibility rule. Nothing is copied from that file; it is imported and called, so a fix there fixes
    every document set.

A link from the curriculum to a chapter, a study guide or an exercise becomes its GitHub URL, because those are different documents.
"""
import importlib.util, os, re, shutil, subprocess, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
LESSONS = os.path.dirname(HERE)
REPO = os.path.dirname(LESSONS)
BOOKDIR = os.path.join(LESSONS, "book")
SOURCE = None                         # the curriculum document of this edition (docs/curriculum.md in English); set with the language
sys.path.insert(0, BOOKDIR)
sys.path.insert(0, os.path.join(BOOKDIR, "locale"))     # never name a package `locale`: it would shadow the stdlib module
import catalog, diagrams, repo_links, study_guides

STEM = repo_links.IDENTITY["curriculum_stem"]     # from the locale catalog (identity.curriculum_stem)
HTML = "curriculum.html"
CHAPTER = None                        # the same, relative to lessons/, as the book's link rewriting expects
FRONT_MATTER = None                   # this edition's name for front-matter.md in this folder
CS_DIR = None                         # this edition's name for the generated chapters folder, relative to lessons/
CAT = None
WEEKS = 16
TARGET_PAGES, MAX_PAGES = 8, 12       # the plan: aim for about 8 pages in the whole PDF, never more than 12 (the rubric and the log template added two)
ENGLISH_ACRONYM = "WEIRD"             # the source edition's acronym; a translated edition must not keep it
# The words of the checks come from the catalog (block curriculum, plus acronym and phases). `set_language` switches them, for example in tests.
#   MAX_WORDS       the longest descriptive sentence (Simplified Technical English)    CHAPTER_LABEL  "Ch" or "Cap." in "[Ch 4](...)"
#   REGISTER        the pattern of forbidden register forms, and REGISTER_LABEL its name in a problem
#   ACRONYM, GLOSS, PHASES_NOTE   the sentences that state the acronym             PHASES  (letter, Mermaid node id, first week, last week)
LANG = MAX_WORDS = CHAPTER_LABEL = REGISTER = REGISTER_LABEL = ACRONYM = GLOSS = PHASES_NOTE = PHASES = None
WORD_KEYS = ["curriculum.max_words", "curriculum.chapter_label", "curriculum.register_pattern", "curriculum.register_label",
             "acronym.word", "acronym.gloss", "acronym.phases_note"]

def norm(text):
    """One normal form for comparing text with catalog words: NFC, one space for each run of white space."""
    return " ".join(unicodedata.normalize("NFC", text).split())

def set_language(lang):
    """Load the curriculum words of `lang` into the module constants. All or nothing: a missing or malformed key leaves the old language."""
    global LANG, MAX_WORDS, CHAPTER_LABEL, REGISTER, REGISTER_LABEL, ACRONYM, GLOSS, PHASES_NOTE, PHASES
    global SOURCE, CHAPTER, FRONT_MATTER, CS_DIR, CAT
    cat = catalog.load(lang)
    letters = cat.phase_letters()
    cat.require(WORD_KEYS + [f"phases.{n}.{f}" for n in range(1, len(letters) + 1) for f in ("mermaid_node_id", "weeks")])
    if len(letters) != 5:
        raise catalog.CatalogError(f"the catalog must define 5 phases, it defines {len(letters)}")
    phases = []
    for n, letter in enumerate(letters, 1):
        weeks = [int(w) for w in re.findall(r"\d+", cat.get(f"phases.{n}.weeks"))]
        if len(weeks) != 2 or weeks[0] > weeks[1]:
            raise catalog.CatalogError(f"phases.{n}.weeks must name a first and a last week")
        phases.append((letter, cat.get(f"phases.{n}.mermaid_node_id"), weeks[0], weeks[1]))
    limit = cat.text("curriculum.max_words").strip()
    if not limit.isdigit() or int(limit) < 1:
        raise catalog.CatalogError("curriculum.max_words must be a positive whole number")
    limit = int(limit)
    pattern = re.compile(cat.text("curriculum.register_pattern"), re.I)
    values = (lang, limit, norm(cat.text("curriculum.chapter_label")), pattern, cat.text("curriculum.register_label"),
              cat.text("acronym.word"), norm(cat.text("acronym.gloss")), norm(cat.text("acronym.phases_note")), tuple(phases))
    LANG, MAX_WORDS, CHAPTER_LABEL, REGISTER, REGISTER_LABEL, ACRONYM, GLOSS, PHASES_NOTE, PHASES = values
    CAT = cat
    SOURCE = os.path.join(REPO, *cat.path("docs/curriculum.md").split("/"))
    CHAPTER = "../" + cat.path("docs/curriculum.md")
    FRONT_MATTER = os.path.basename(cat.path("lessons/curriculum/front-matter.md"))
    CS_DIR = cat.lessons_path("cs")
    study_guides.set_language(lang)      # last, so that nothing above can fail after it has switched

set_language(os.environ.get("BOOK_LANG", "en"))

def load_book_build():
    sys.dont_write_bytecode = True      # importing the book's build must not rewrite a __pycache__ file
    spec = importlib.util.spec_from_file_location("book_build", os.path.join(BOOKDIR, "build.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

def prose_sentences(text):
    """The sentences of running prose: no code, tables, headings, comments or links' targets. A list item counts as prose."""
    text = re.sub(r"```.*?```", "", text, flags=re.S)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.S)
    out = []
    for line in text.splitlines():
        if not line.strip() or line.lstrip().startswith(("|", "#")):
            continue
        line = re.sub(r"^\s*(?:[-*]|\d+\.)\s+", "", line)
        line = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", line)       # keep the label, drop the target
        line = re.sub(r"[*_`]", "", line)
        line = re.sub(re.escape(CHAPTER_LABEL) + r"(?= \d)", CHAPTER_LABEL.replace(".", ""), line)   # "Cap. 4" is not the end of a sentence
        out += [s.strip() for s in re.split(r"(?<=[.!?])\s+", line) if s.strip()]
    return out

def check_curriculum(text=None, repo=REPO):
    """Problems (a list of strings) in docs/curriculum.md."""
    text = study_guides.read(SOURCE) if text is None else text
    where = CAT.path("docs/curriculum.md")
    problems = []
    add = lambda msg: problems.append(f"{where}: {msg}")

    # the plan: every week of a standard semester appears once, in order
    weeks = [int(m.group(1)) for m in re.finditer(r"^\| (\d+) \|", text, re.M)]
    if weeks != list(range(1, WEEKS + 1)):
        add(f"the week-by-week table must list weeks 1 to {WEEKS} once each, in order; it lists {weeks}")

    # the diagram: exactly one, described for readers who cannot see it
    blocks = list(diagrams.mermaid_blocks(text))
    if len(blocks) != 1:
        add(f"expected exactly one Mermaid diagram, found {len(blocks)}")
    for _, _, src in blocks:
        for key in ("accTitle", "accDescr"):
            if f"{key}:" not in src:
                add(f"the diagram needs '{key}:'")
        if not re.search(r"flowchart|stateDiagram", src.split("\n", 1)[0]):
            add("the diagram must be a flowchart or a state diagram")

    # the acronym and its five phases: the sentences, the table rows and the diagram nodes all use the catalog's letters, so an English
    # letter that survived translation fails (the Mermaid node ids never change; only the displayed labels do)
    flat = norm(text)
    for what, sentence in (("acronym sentence", GLOSS), ("phases sentence", PHASES_NOTE)):
        if sentence not in flat:
            add(f"the {what} is missing; it must read exactly: {sentence}")
    if ACRONYM != ENGLISH_ACRONYM and re.search(r"\b" + ENGLISH_ACRONYM + r"\b", text):
        add(f"the English acronym {ENGLISH_ACRONYM} survives; this edition's acronym is {ACRONYM}")
    letters = [p[0] for p in PHASES]
    rows = re.findall(r"^\| \| \*\*([^:*|]+): ", text, re.M)
    if rows != letters:
        add(f"the week-by-week table must have the phase rows {letters} in order; it has {rows}")
    phase, first_week_of = None, {}
    for line in text.splitlines():
        row = re.match(r"^\| \| \*\*([^:*|]+): ", line)
        week = re.match(r"^\| (\d+) \|", line)
        if row:
            phase = row.group(1)
        elif week and phase in letters:
            _, _, lo, hi = PHASES[letters.index(phase)]
            if int(week.group(1)) <= PHASES[-1][3] and not lo <= int(week.group(1)) <= hi:     # the review week after the last phase has no phase
                add(f"week {week.group(1)} is under phase {phase}, which covers weeks {lo} to {hi}")
    for letter, node, _, _ in PHASES:
        label = re.search(r"\b" + re.escape(node) + r'\["([^":]+):', "\n".join(src for _, _, src in blocks))
        if not label:
            add(f"the diagram has no node '{node}' with a label that starts with the phase letter")
        elif label.group(1) != letter:
            add(f"diagram node {node} is labeled with the letter {label.group(1)!r}; the phase letter is {letter!r}")

    # printed chapter numbers: "Ch N" (the catalog's chapter label) must be the chapter's number in the printed book (chapters.txt order, numbered from 1)
    order = [l.strip() for l in study_guides.read(os.path.join(BOOKDIR, "chapters.txt")).splitlines() if l.strip() and not l.startswith("#")]
    for m in re.finditer(r"\[" + re.escape(CHAPTER_LABEL) + r" (\d+)\]\(\.\./lessons/(" + re.escape(CS_DIR) + r"/[^)#]+)", text):
        want = order.index(m.group(2)) + 1 if m.group(2) in order else None
        if want != int(m.group(1)):
            add(f"'{CHAPTER_LABEL} {m.group(1)}' links to {m.group(2)}, which is chapter {want} of the printed book")
    for m in re.finditer(r"\[(\w+\.?) (\d+)\]\(\.\./lessons/" + re.escape(CS_DIR) + "/", text):
        if m.group(1) != CHAPTER_LABEL:
            add(f"chapter link labeled '{m.group(1)} {m.group(2)}'; this edition writes '{CHAPTER_LABEL} {m.group(2)}'")
    # an exercise link's text is the exercise ID and the heading it points at starts with the same ID (the IDs never change in translation)
    for m in re.finditer(r"\[([A-Z]\d+)\]\(\.\./lessons/exercises\.md#([a-z]\d+)-", text):
        if m.group(1).lower() != m.group(2):
            add(f"exercise link '{m.group(1)}' points at the heading of exercise {m.group(2).upper()}; an exercise ID must not change")
    # the diagram's arrows must land on a node, not on the box around the nodes
    for _, _, src in blocks:
        for box in re.findall(r"^\s*subgraph\s+(\w+)", src, re.M):
            if re.search(r"(?:-->|---)\s*(?:\|[^|]*\|\s*)?" + box + r"\b", src) or re.search(r"\b" + box + r"\s*(?:-->|---)", src):
                add(f"the diagram has an arrow to or from the box '{box}'; point arrows at a node inside it")

    # links: relative ones resolve to a file and a heading, external ones use an allowed host over https
    stripped = re.sub(r"```.*?```", "", text, flags=re.S)
    base = os.path.dirname(SOURCE)
    for m in study_guides.LINK.finditer(stripped):
        target = m.group(2)
        if re.match(r"[a-z][a-z0-9+.-]*:", target):
            continue
        path, _, frag = target.partition("#")
        full = os.path.normpath(os.path.join(base, path)) if path else SOURCE
        if not os.path.exists(full):
            add(f"link to a missing file: {target}")
        elif frag and full.endswith(".md") and frag not in study_guides.anchors(study_guides.read(full)):
            add(f"link to a missing heading: {target}")
    allowed = study_guides.hosts(repo)
    for url in study_guides.external_urls(stripped):
        u = re.match(r"https://([^/]+)(/.*)?$", url)
        if not u:
            add(f"external links must use https: {url}")
        elif u.group(1) not in allowed and not any("/" in h and (u.group(1) + (u.group(2) or "")).startswith(h) for h in allowed):
            add(f"host {u.group(1)!r} is not in lessons/book/link-hosts.txt: {url}")

    # house style (house-style.md): Simplified Technical English, plain punctuation
    for s in prose_sentences(text):
        n = len(s.split())
        if n > MAX_WORDS:
            add(f"sentence of {n} words (the limit is {MAX_WORDS}): {s[:70]}...")
        if REGISTER.search(s):
            add(f"{REGISTER_LABEL} in body prose: {s[:70]}...")
    for ch, name in (("—", "em dash"), ("–", "en dash"), ("“", "curly quote"), ("’", "curly apostrophe")):
        if ch in text:
            add(f"contains a {name}; house style types straight quotes and breaks the sentence instead of using a dash")
    # TODO and TBD are upper-case markers: the Spanish word "todo" is ordinary prose.
    if re.search(r"\b(?:(?-i:TODO|TBD)|lorem ipsum)\b", text, re.I):
        add("contains placeholder text")

    # the book's edition: when it changes, someone must review the curriculum against it
    meta = study_guides.read(os.path.join(HERE, "metadata.yaml"))
    book = study_guides.read(os.path.join(BOOKDIR, "metadata.yaml"))
    title = re.search(r'^title:\s*"(.+)"', book, re.M).group(1)
    companion = re.search(r'^companion-to:\s*"(.+)"', meta, re.M).group(1)
    if companion != title:
        add(f"metadata.yaml says it accompanies {companion!r}, but the book is now {title!r}: review the curriculum, then update `companion-to` and front-matter.md")
    return problems

def pdf_pages(path):
    """Page count of a PDF, from Ghostscript."""
    gs = shutil.which("gs")
    if not gs:
        return None
    out = subprocess.run([gs, "-q", "-dNODISPLAY", "-dNOSAFER", "-dBATCH", "-c", f"({path}) (r) file runpdfbegin pdfpagecount = quit"],
                         stdout=subprocess.PIPE, encoding="utf-8", check=True).stdout
    return int(out.strip())

def main():
    book = load_book_build()
    book.release_mode()
    checking = "--check" in sys.argv
    problems = check_curriculum()
    if problems:
        print("\n".join("PROBLEM " + p for p in problems))
        raise SystemExit(f"{len(problems)} curriculum problem(s)")
    print("curriculum: plan, diagram, links and house style ok")
    if not shutil.which("pandoc"):
        raise SystemExit("pandoc not found (https://pandoc.org/installing.html)")
    texts = {CHAPTER: study_guides.read(SOURCE)}
    html = book.build_documents(texts, STEM, os.path.join(HERE, "metadata.yaml"), os.path.join(HERE, FRONT_MATTER),
                                HTML, "curriculum", checking, prune_cache=False)
    if checking:
        book.check(html)
        return
    pdf = os.path.join(book.artifacts_dir(), STEM + ".pdf")
    pages = pdf_pages(pdf) if os.path.exists(pdf) else None
    if pages is not None:
        print(f"curriculum.pdf: {pages} pages (title page and contents included; the plan is about {TARGET_PAGES} in all and at most {MAX_PAGES})")
        if pages > MAX_PAGES:
            raise SystemExit(f"curriculum.pdf has {pages} pages; the limit is {MAX_PAGES}")

if __name__ == "__main__":
    main()
