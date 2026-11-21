"""The curated study guides under lessons/study-guides/: what they must contain, and checks that keep them honest.

The guides are written by hand. Nothing here writes or generates prose. This module only *reads* the guides and reports
problems, and it is used twice: by `lessons/study-guides/build.py --check` and by `lessons/book/test_study_guides.py`.

What is checked (the rules come from the study-guides implementation plan):

  * the set of guides: 13 language-family guides and 8 concept guides exist, are listed in `chapters.txt` and in the
    guides' README (the index), and are not in the book's `chapters.txt`;
  * the template: each guide is `# <Topic> study guide` with the eleven required `##` sections, in order, none empty;
  * required content: the DEMO ONLY safety model, the exact-40 rule, the five questions, the four self-check
    questions, a prediction prompt, a link to a verified exercise, and one of the three assurance labels;
  * no `TODO`, `TBD` or other placeholder text;
  * diagrams: a `diagram-source` block must equal its canonical Mermaid source exactly; a new diagram must say which of the
    allowed relationships it adds; every diagram has `accTitle` and `accDescr`; every language guide has at least one diagram
    and shows the Program Flow diagram of each entry the brief names;
  * links: relative links resolve (file, heading anchor or source line); external links use an allowed host;
  * the book side: each topic page of the book links to its guide, and the guides are in the index pages.

Standard library only.
"""
import os, posixpath, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, "locale"))            # never name a package `locale`: it would shadow the stdlib module
import catalog                                              # the locale catalog (needs PyYAML, like the rest of the book tooling)
import diagrams

LESSONS = os.path.dirname(HERE)
REPO = os.path.dirname(LESSONS)
GUIDES = None       # the guides folder of this edition (set with the language; plan 5.6)
CAT = None          # the locale catalog of the current language; it names this edition's files and folders (paths.*)


# The guide names below (LANGUAGE_GUIDES, CONCEPT_GUIDES, EXPECTED_DIAGRAMS, BOOK_LINKS) are English paths, the canonical keys.
# Every place that touches a disk or a link goes through GW/GP/LP, which give the path in the edition being checked.
def GW(rel):
    """Repository-relative path, in this edition, of the English guide path `rel` (relative to lessons/study-guides/)."""
    return CAT.path("lessons/study-guides/" + rel)


def GP(rel):
    """`rel` in this edition, relative to the guides folder (the spelling chapters.txt and the index use)."""
    return posixpath.relpath(GW(rel), CAT.path("lessons/study-guides"))


def LP(rel):
    """This edition's path, relative to lessons/, of the English path `rel` (relative to lessons/)."""
    return CAT.lessons_path(rel)


def groot(repo):
    return os.path.join(repo, *CAT.path("lessons/study-guides").split("/"))

# The words the checks require come from the locale catalog (lessons/book/locale/<lang>.yaml, block study_guides). The language is
# BOOK_LANG (default "en", as in diagrams.py); `set_language` switches it, for example in tests. A missing key fails loudly
# (catalog.MissingKeyError); there is no silent fallback to English. SHARED_CHALLENGE has exactly one source: the catalog.
#   TITLE_PREFIX/TITLE_SUFFIX  the H1 is PREFIX + topic + SUFFIX      SECTIONS  the eleven required H2 titles, in order
#   FIVE_QUESTIONS, FOUR_QUESTIONS  bold lead-ins                     ASSURANCE_LABELS  the three labels, lower case
LANG = TITLE_PREFIX = TITLE_SUFFIX = SECTIONS = CHALLENGE_HEADING = SHARED_CHALLENGE = EXACT_FORTY = None
FIVE_QUESTIONS = FOUR_QUESTIONS = ASSURANCE_LABELS = SANDBOX_WORD = PREDICT = PLACEHOLDER = None
S_CHALLENGE, S_MACHINE, S_SELF = 2, 3, 9    # positions in SECTIONS of the sections the content checks look inside


def nfc(text):
    """One normal form for text that is compared with catalog words (an accented letter may be one code point or two)."""
    return unicodedata.normalize("NFC", text)


def set_language(lang):
    """Load the study_guides.* words of `lang` into the module constants, and the diagrams.* words too. All or nothing: a missing
    key leaves the old language in place."""
    global LANG, TITLE_PREFIX, TITLE_SUFFIX, SECTIONS, CHALLENGE_HEADING, SHARED_CHALLENGE, EXACT_FORTY, CAT, GUIDES, CANONICAL_HOMES
    global FIVE_QUESTIONS, FOUR_QUESTIONS, ASSURANCE_LABELS, SANDBOX_WORD, PREDICT, PLACEHOLDER
    cat = catalog.load(lang)
    t = lambda key: nfc(cat.text("study_guides." + key))
    many = lambda key, n: [t(f"{key}.{i}") for i in range(1, n + 1)]
    prefix, found, suffix = t("title").partition("{topic}")
    if not found or "{topic}" in suffix:
        raise catalog.CatalogError("study_guides.title must contain {topic} exactly once")
    heading = t("challenge_heading")
    shared = " ".join(t("shared_challenge").split()).replace("{anchor}", slug(heading))
    assurance = tuple(t("assurance." + k).lower() for k in ("guaranteed", "implementation_permitted", "accidentally_exploited"))
    placeholder = re.compile(r"\b((?-i:TODO|TBD|FIXME|XXX)|lorem ipsum)\b|\b(?:" + t("placeholder_pattern") + r")\b|<[A-Za-z ]*here>|\[\.\.\.\]|…", re.I)
    values = (lang, prefix, suffix, many("sections", 11), heading, shared, t("exact_forty"), many("lead_in_five", 5),
              many("lead_in_four", 4), assurance, t("sandbox_word").lower(), re.compile(t("predict_pattern"), re.I), placeholder)
    diagrams.set_language(lang)      # last, so that nothing above can fail after it has switched
    (LANG, TITLE_PREFIX, TITLE_SUFFIX, SECTIONS, CHALLENGE_HEADING, SHARED_CHALLENGE, EXACT_FORTY, FIVE_QUESTIONS, FOUR_QUESTIONS,
     ASSURANCE_LABELS, SANDBOX_WORD, PREDICT, PLACEHOLDER) = values
    CAT = cat
    GUIDES = os.path.join(LESSONS, cat.lessons_path("study-guides"))
    CANONICAL_HOMES = ("src/", "lessons/cs-source/", cat.path("lessons/intro.md"))

def challenge_anchor(repo=None):
    """The fragment the shared-challenge link must carry: the id of the introduction's challenge heading AS THE INTRODUCTION IS
    NOW. The catalog says what the translated heading is (study_guides.challenge_heading); until the introduction is translated it
    still has the English heading, and a link to a heading that does not exist is worse than one to the English id. Once the
    introduction is translated, `apply.py --relink` re-aims every source at the catalog heading and this returns its id."""
    wanted = slug(CHALLENGE_HEADING)
    path = os.path.join(repo or REPO, "lessons", CAT.lessons_path("intro.md"))
    if not os.path.isfile(path):
        return wanted
    ids = {slug(nfc(m.group(1))) for m in re.finditer(r"^## (.+?)\s*$", read(path), re.M)}
    if wanted in ids:
        return wanted
    english = slug(nfc(catalog.load("en").text("study_guides.challenge_heading")))
    return english if english in ids else wanted

# A new (non-canonical) diagram is allowed only for a relationship the source diagram does not show.
NEW_DIAGRAM_KINDS = ("cross-language-state", "lazy-demand-trace", "transaction-boundary", "authority-boundary")

MIN_SECTION_WORDS = 15

LANGUAGE_GUIDES = [
    "languages/csharp-linq-xaml-and-ports.md",
    "languages/cobol.md",
    "languages/haskell.md",
    "languages/forth.md",
    "languages/make-and-cmake.md",
    "languages/regex-engines-and-sed.md",
    "languages/apl.md",
    "languages/javascript.md",
    "languages/common-lisp.md",
    "languages/m4.md",
    "languages/tcl.md",
    "languages/ed-and-ex.md",
    "languages/tar.md",
]
CONCEPT_GUIDES = [
    "concepts/reading-adversarial-programs.md",
    "concepts/state-and-control-beyond-variables.md",
    "concepts/evaluation-demand-and-laziness.md",
    "concepts/formal-languages-and-weird-machines.md",
    "concepts/effects-errors-and-commitment.md",
    "concepts/portability-abstraction-and-cost.md",
    "concepts/events-callbacks-and-reactive-control.md",
    "concepts/comparative-machine-design.md",
]
ALL_GUIDES = LANGUAGE_GUIDES + CONCEPT_GUIDES

# The Program Flow diagrams each language guide must show (the plan's "Diagrams" column), as src/<entry> names.
EXPECTED_DIAGRAMS = {
    "languages/csharp-linq-xaml-and-ports.md": ["ModernChallenge1", "LinqChallenge1", "LinqChallenge2", "xaml"],
    "languages/cobol.md": ["cobol", "cobol-weird"],
    "languages/haskell.md": ["haskell", "haskell-weird"],
    "languages/forth.md": ["forth", "forth-weird"],
    "languages/make-and-cmake.md": ["make-gnu", "cmake"],
    "languages/regex-engines-and-sed.md": ["regex-pcre2", "regex-dotnet", "regex-sed"],
    "languages/apl.md": ["apl", "apl-weird"],
    "languages/javascript.md": ["javascript", "javascript-weird", "javascript-events"],
    "languages/common-lisp.md": ["lisp", "lisp-weird"],
    "languages/m4.md": ["m4"],
    "languages/tcl.md": ["tcl", "tcl-weird"],
    "languages/ed-and-ex.md": ["ed-weird", "ex-weird"],
    "languages/tar.md": ["tar-gnu", "tar-gnu-weird"],
}

# Which pages of the book must point at which guide near their start (the plan's navigation step 3). Paths are under lessons/.
BOOK_LINKS = {
    "languages/csharp-linq-xaml-and-ports.md": ["languages/csharp-linq-xaml.md"],
    "languages/cobol.md": ["languages/cobol.md"],
    "languages/haskell.md": ["languages/haskell.md"],
    "languages/forth.md": ["languages/forth.md"],
    "languages/make-and-cmake.md": ["languages/make-cmake.md"],
    "languages/regex-engines-and-sed.md": ["languages/regex.md"],
    "languages/apl.md": ["languages/apl.md"],
    "languages/javascript.md": ["languages/javascript.md"],
    "languages/common-lisp.md": ["languages/lisp.md"],
    "languages/m4.md": ["languages/m4.md"],
    "languages/tcl.md": ["languages/tcl.md"],
    "languages/ed-and-ex.md": ["languages/editors.md"],
    "languages/tar.md": ["languages/tar.md"],
    "concepts/reading-adversarial-programs.md": ["cs/01-reading-an-adversarial-program.md"],
    "concepts/state-and-control-beyond-variables.md": ["cs/02-what-counts-as-a-machine.md", "cs/03-control-flow-and-continuations.md",
                                                        "cs/06-state-beyond-variables.md"],
    "concepts/evaluation-demand-and-laziness.md": ["cs/04-evaluation-and-demand.md"],
    "concepts/formal-languages-and-weird-machines.md": ["cs/05-formal-languages-as-computational-substrates.md"],
    "concepts/effects-errors-and-commitment.md": ["cs/07-effects-errors-and-commitment.md"],
    "concepts/portability-abstraction-and-cost.md": ["cs/08-abstraction-leaks-and-implementation-dependence.md"],
    "concepts/events-callbacks-and-reactive-control.md": ["cs/10-events-callbacks-and-reactive-control-flow.md"],
    "concepts/comparative-machine-design.md": ["cs/09-comparative-case-studies.md"],
}

LINK = re.compile(r"(?<!!)\[([^\]]*)\]\(([^)\s]+)\)")
SOURCE_COMMENT = re.compile(r"^<!--\s*diagram-source:\s*(\S+?)\s*-->\s*$")
NEW_COMMENT = re.compile(r"^<!--\s*diagram-new:\s*([a-z-]+)\s*[:—-]\s*(.+?)\s*-->\s*$")
# Canonical sources may live only where a person edits them: not in the generated lessons/cs/ or in generated blocks.
CANONICAL_HOMES = None      # set with the language: src/, lessons/cs-source/ and the intro page of this edition


# ---------------------------------------------------------------- reading

def read(path):
    with open(path, encoding="utf-8") as f:
        return f.read().replace("\r\n", "\n")

def manifest(root=None):
    """The guides' chapters.txt: paths relative to lessons/study-guides/, in reading order."""
    root = root or GUIDES
    with open(os.path.join(root, "chapters.txt"), encoding="utf-8") as f:
        return [l.strip() for l in f if l.strip() and not l.lstrip().startswith("#")]

def slug(heading):
    h = re.sub(r"`", "", heading.strip().lower())
    h = re.sub(r"[^\w\- ]", "", h)
    return h.replace(" ", "-")


set_language(os.environ.get("BOOK_LANG", "en"))

def anchors(text):
    """GitHub heading ids of a Markdown file: the first keeps its slug, repeats get -1, -2, ... in order."""
    seen, out = {}, set()
    for it in diagrams.scan(text):
        if it[0] == "heading":
            base = slug(it[2])
            n = seen.get(base, 0)
            seen[base] = n + 1
            out.add(base if n == 0 else f"{base}-{n}")
    return out

def sections(text):
    """[(title, body_text, first_line)] for each `##` section, fence-aware; `body_text` excludes the heading line."""
    items = diagrams.scan(text)
    lines = text.split("\n")
    heads = [(it[3], it[2]) for it in items if it[0] == "heading" and it[1] == 2]
    h1_after = [it[3] for it in items if it[0] == "heading" and it[1] == 1]
    out = []
    for k, (line, title) in enumerate(heads):
        stop = heads[k + 1][0] if k + 1 < len(heads) else len(lines) + 1
        stop = min([stop] + [l for l in h1_after if l > line])
        out.append((title, "\n".join(lines[line:stop - 1]), line))
    return out

def words(text):
    text = re.sub(r"```.*?```", " ", text, flags=re.S)
    return len(re.findall(r"(?:[^\W_]|`)+", text))      # letters of any language and digits, so accented Spanish words count once


# ---------------------------------------------------------------- canonical diagram sources

def canonical_source(ref, repo=None):
    """The Mermaid text a `diagram-source:` reference names, or raises ValueError saying why it cannot be found.

    `src/<entry>/README.md#program-flow`   the one diagram of the entry's `## Program Flow` section
    `<file>#block-N`                       the Nth ```mermaid fence of the file (for lessons/cs-source/... and lessons/intro.md)
    `<file>#<heading-slug>`                the first ```mermaid fence under that heading"""
    repo = repo or REPO
    path, _, frag = ref.partition("#")
    if not path.startswith(CANONICAL_HOMES):
        raise ValueError(f"{ref}: a diagram may be copied only from {', '.join(CANONICAL_HOMES)} (never generated files such as lessons/cs/ or a lesson page)")
    full = os.path.join(repo, path)
    if not os.path.isfile(full):
        raise ValueError(f"{ref}: no such file")
    text = read(full)
    if not frag:
        raise ValueError(f"{ref}: say which diagram (#program-flow, #block-N or #heading-slug)")
    if frag == "program-flow":
        section, problems = diagrams.program_flow(text, path)
        if section is None:
            raise ValueError(f"{ref}: the file has no '## Program Flow' section")
        blocks = diagrams.mermaid_blocks(section)
        if len(blocks) != 1:
            raise ValueError(f"{ref}: its Program Flow section has {len(blocks)} diagrams, expected 1")
        return blocks[0][2]
    items = diagrams.scan(text)
    blocks = [it for it in items if it[0] == "fence" and it[1] == "mermaid"]
    m = re.fullmatch(r"block-(\d+)", frag)
    if m:
        n = int(m.group(1))
        if not 1 <= n <= len(blocks):
            raise ValueError(f"{ref}: the file has {len(blocks)} diagram(s)")
        return blocks[n - 1][2]
    head = next((it for it in items if it[0] == "heading" and slug(it[2]) == frag), None)
    if head is None:
        raise ValueError(f"{ref}: no heading with that id")
    under = [b for b in blocks if b[3] > head[3]]
    if not under:
        raise ValueError(f"{ref}: no diagram after that heading")
    return under[0][2]

def guide_diagrams(text):
    """Every Mermaid fence of a guide with what precedes it: [(first_line, source, marker)], where `marker` is the
    ('source', ref) or ('new', kind, why) comment on the nearest non-blank line before the fence, or None."""
    lines = text.split("\n")
    out = []
    for first, _, src in diagrams.mermaid_blocks(text):
        k = first - 2                      # index of the line before the fence
        while k >= 0 and not lines[k].strip():
            k -= 1
        marker = None
        if k >= 0:
            m = SOURCE_COMMENT.match(lines[k].strip())
            n = NEW_COMMENT.match(lines[k].strip())
            if m:
                marker = ("source", m.group(1))
            elif n:
                marker = ("new", n.group(1), n.group(2))
        out.append((first, src, marker))
    return out


# ---------------------------------------------------------------- the checks

def hosts(repo=None):
    path = os.path.join(repo or REPO, "lessons", "book", "link-hosts.txt")
    return {l.strip() for l in read(path).splitlines() if l.strip() and not l.startswith("#")}

def external_urls(text):
    found = []
    for m in re.finditer(r"https?://[^\s<>\"]+", text):
        u = m.group(0)
        while u and (u[-1] in ".,;:*_" or (u[-1] == ")" and u.count(")") > u.count("("))):
            u = u[:-1]
        found.append(u)
    return found

def check_guide(rel, text, repo=None):
    """Problems (a list of strings) in one guide. `rel` is its path under lessons/study-guides/."""
    repo = repo or REPO
    where = GW(rel)
    problems = []
    add = lambda msg: problems.append(f"{where}: {msg}")
    items = diagrams.scan(text)
    h1s = [it for it in items if it[0] == "heading" and it[1] == 1]
    h1 = nfc(h1s[0][2]) if len(h1s) == 1 else ""
    if len(h1s) != 1 or not (h1.startswith(TITLE_PREFIX) and h1.endswith(TITLE_SUFFIX)) or len(h1) <= len(TITLE_PREFIX) + len(TITLE_SUFFIX):
        add(f"needs exactly one H1 of the form '# {TITLE_PREFIX}<Topic>{TITLE_SUFFIX}'")
    secs = [(nfc(t), b, n) for t, b, n in sections(text)]
    titles = [s[0] for s in secs]
    if titles != SECTIONS:
        missing = [s for s in SECTIONS if s not in titles]
        extra = [t for t in titles if t not in SECTIONS]
        add("the '##' sections must be exactly the template, in order" + (f"; missing: {missing}" if missing else "")
            + (f"; unexpected: {extra}" if extra else "") + ("" if missing or extra else "; the order is wrong"))
    body = {t: b for t, b, _ in secs}
    for t in SECTIONS:
        if t in body and words(body[t]) < MIN_SECTION_WORDS:
            add(f"section '{t}' is empty or too short (under {MIN_SECTION_WORDS} words)")
    for m in PLACEHOLDER.finditer(re.sub(r"<!--.*?-->", "", text, flags=re.S)):
        line = text[:m.start()].count("\n") + 1
        add(f"line {line}: placeholder text {m.group(0)!r}")
    if "BEGIN GENERATED" in text or "END GENERATED" in text:
        add("guides are hand-written: no BEGIN/END GENERATED markers")
    # required content
    low = nfc(text).lower()
    shared, machine, selfcheck = (nfc(body.get(SECTIONS[i], "")) for i in (S_CHALLENGE, S_MACHINE, S_SELF))
    if "DEMO ONLY" not in text or SANDBOX_WORD not in low:
        add(f"must state the safety model: DEMO ONLY data and sandbox-first execution (the word '{SANDBOX_WORD}')")
    first_paragraph = re.split(r"\n\s*\n", shared.strip(), maxsplit=1)[0]
    if " ".join(first_paragraph.split()) != SHARED_CHALLENGE.replace("#" + slug(CHALLENGE_HEADING) + ")", "#" + challenge_anchor(repo) + ")"):
        add(f'"{SECTIONS[S_CHALLENGE]}" must start with the standard paragraph, including the exactly 40 rule')
    if EXACT_FORTY not in shared:
        add(f"'{SECTIONS[S_CHALLENGE]}' must say that a total of exactly 40 continues")
    for q in FIVE_QUESTIONS:
        if f"**{q}**" not in machine:
            add(f"'{SECTIONS[S_MACHINE]}' needs a paragraph that starts with **{q}**")
    for q in FOUR_QUESTIONS:
        if f"**{q}**" not in selfcheck:
            add(f"'{SECTIONS[S_SELF]}' needs a question that starts with **{q}**")
    if not PREDICT.search(text):
        add("must ask the reader to predict before running")
    if not re.search(r"exercises\.md#[a-z]\d", text):
        add("must link to a verified exercise in lessons/exercises.md (for example exercises.md#b1-...)")
    if not any(label in low for label in ASSURANCE_LABELS):
        add("must label behavior as " + ", ".join(ASSURANCE_LABELS[:-1]) + " or " + ASSURANCE_LABELS[-1])
    # diagrams
    found = guide_diagrams(text)
    seen_sources = set()
    for first, src, marker in found:
        w = f"line {first}"
        for key in ("accTitle", "accDescr"):
            if not re.search(rf"^\s*{key}\s*[:{{]", src, re.M):
                add(f"{w}: the diagram needs '{key}:'")
        if marker is None:
            add(f"{w}: a diagram needs the line before it: <!-- diagram-source: path#anchor --> (a copy) or "
                f"<!-- diagram-new: kind - why --> (a new one; kind is one of {', '.join(NEW_DIAGRAM_KINDS)})")
        elif marker[0] == "source":
            seen_sources.add(marker[1])
            try:
                canon = canonical_source(marker[1], repo)
            except ValueError as e:
                add(f"{w}: {e}")
            else:
                if canon.strip("\n") != src.strip("\n"):
                    add(f"{w}: the diagram differs from its canonical source {marker[1]} (copy it verbatim)")
        else:
            if marker[1] not in NEW_DIAGRAM_KINDS:
                add(f"{w}: a new diagram must add one of: {', '.join(NEW_DIAGRAM_KINDS)} (got {marker[1]!r})")
    if rel in LANGUAGE_GUIDES and not found:
        add("a guide that analyzes a runtime machine needs at least one diagram")
    for entry in EXPECTED_DIAGRAMS.get(rel, []):
        if f"src/{entry}/README.md#program-flow" not in seen_sources:
            add(f"must reuse the Program Flow diagram of src/{entry} (<!-- diagram-source: src/{entry}/README.md#program-flow -->)")
    problems += check_links(rel, text, repo)
    return problems

def check_links(rel, text, repo=None):
    """Relative links must resolve (file, heading anchor, or a source line that exists); external links need an allowed host."""
    repo = repo or REPO
    where = GW(rel)
    problems = []
    base = os.path.dirname(os.path.join(repo, GW(rel)))
    stripped = re.sub(r"```.*?```", "", text, flags=re.S)
    allowed = hosts(repo)
    for m in LINK.finditer(stripped):
        target = m.group(2)
        if re.match(r"[a-z][a-z0-9+.-]*:", target):
            continue
        path, _, frag = target.partition("#")
        full = os.path.normpath(os.path.join(base, path)) if path else os.path.join(repo, GW(rel))
        if not os.path.exists(full):
            problems.append(f"{where}: link to a missing file: {target}")
            continue
        lab = re.fullmatch(r"L(\d+)(?:-(\d+))?", m.group(1))
        if lab and frag:
            want = f"L{lab.group(1)}" + (f"-L{lab.group(2)}" if lab.group(2) else "")
            if frag != want:
                problems.append(f"{where}: the link text says {m.group(1)} but the anchor is #{frag}: {target}")
        if not frag or os.path.isdir(full):
            continue
        if full.endswith(".md"):
            if frag not in anchors(read(full)):
                problems.append(f"{where}: link to a missing heading: {target}")
        else:
            lm = re.fullmatch(r"L(\d+)(?:-L(\d+))?", frag)
            if not lm:
                problems.append(f"{where}: a link into a non-Markdown file must be #L<line> or #L<a>-L<b>: {target}")
            else:
                with open(full, encoding="utf-8", errors="replace") as f:
                    n = sum(1 for _ in f)
                if int(lm.group(2) or lm.group(1)) > n or int(lm.group(1)) < 1:
                    problems.append(f"{where}: the file has {n} lines, so this anchor is out of range: {target}")
    for url in external_urls(stripped):
        u = re.match(r"https://([^/]+)(/.*)?$", url)
        if not u:
            problems.append(f"{where}: external links must use https: {url}")
        elif u.group(1) not in allowed and not any("/" in h and (u.group(1) + (u.group(2) or "")).startswith(h) for h in allowed):
            problems.append(f"{where}: host {u.group(1)!r} is not in lessons/book/link-hosts.txt (add it there, with the reason, first): {url}")
    return problems

def check_set(repo=None):
    """Problems with the set of guides: the files, the manifest, the index, the book's links and the book's own manifest."""
    repo = repo or REPO
    root = groot(repo)
    gw = GW("chapters.txt")[:-len("chapters.txt")]       # "<guides folder>/", for messages
    mine = [GP(g) for g in ALL_GUIDES]
    problems = []
    on_disk = sorted(os.path.relpath(os.path.join(d, f), root).replace(os.sep, "/")
                     for d, _, fs in os.walk(root) for f in fs if f.endswith(".md") and f not in ("README.md", GP("front-matter.md")))
    for g in mine:
        if g not in on_disk:
            problems.append(f"{gw}{g}: the guide does not exist")
    for g in on_disk:
        if g not in mine:
            problems.append(f"{gw}{g}: not one of the planned guides (add it to study_guides.py and the index first)")
    chap = manifest(root)
    if not chap or chap[0] != "README.md":
        problems.append(f"{gw}chapters.txt: must start with README.md (the index)")
    for g in mine:
        if g not in chap:
            problems.append(f"{gw}chapters.txt: missing {g}")
    for c in chap:
        if not os.path.isfile(os.path.join(root, c)):
            problems.append(f"{gw}chapters.txt: {c} does not exist")
    if len(chap) != len(set(chap)):
        problems.append(f"{gw}chapters.txt: a chapter is listed twice")
    index = read(os.path.join(root, "README.md"))
    linked = set()
    for m in LINK.finditer(index):
        t = m.group(2).partition("#")[0]
        if t and not re.match(r"[a-z][a-z0-9+.-]*:", t):
            linked.add(os.path.relpath(os.path.normpath(os.path.join(root, t)), root).replace(os.sep, "/"))
    for g in mine:
        if g not in linked:
            problems.append(f"{gw}README.md: the index does not link to {g}")
    book = [l.strip() for l in read(os.path.join(repo, "lessons", "book", "chapters.txt")).splitlines() if l.strip() and not l.startswith("#")]
    for c in book:
        if c.startswith(LP("study-guides")):
            problems.append(f"lessons/book/chapters.txt: {c}: the study guides are a separate set, not book chapters")
    # the book points at the guides
    for g, pages in BOOK_LINKS.items():
        for page in pages:
            path = os.path.join(repo, "lessons", LP(page))
            if not os.path.isfile(path):
                problems.append(f"lessons/{LP(page)}: missing")
                continue
            head = "\n".join(read(path).split("\n")[:40])
            if LP(f"study-guides/{g}") not in head:
                problems.append(f"lessons/{LP(page)}: needs a link to {LP(f'study-guides/{g}')} near the top (within the first 40 lines)")
    for page in ("README.md", "index.md"):  # en-key: lessons/<page>, mapped by LP()
        text = read(os.path.join(repo, "lessons", LP(page)))
        if LP("study-guides/README.md") not in text:
            problems.append(f"lessons/{LP(page)}: needs a Study Guides section linking to {LP('study-guides/README.md')}")
    # the guides name the book edition they belong to
    meta = read(os.path.join(root, "metadata.yaml"))
    book_meta = read(os.path.join(repo, "lessons", "book", "metadata.yaml"))
    title = re.search(r'^title:\s*"(.+)"\s*$', book_meta, re.M)
    comp = re.search(r'^companion-to:\s*"(.+)"\s*$', meta, re.M)
    if not title or not comp or comp.group(1) != title.group(1):
        problems.append(f"{gw}metadata.yaml: companion-to must equal the book title ({title.group(1) if title else '?'}); "
                        "review the guides when the book's edition changes")
    return problems

def check_external(repo=None):
    """Network check, not part of the deterministic build: every external link in the guides must load. Returns a list of failures."""
    import urllib.request, urllib.error
    repo = repo or REPO
    root = groot(repo)
    urls = {}
    for rel in manifest(root):
        for u in external_urls(re.sub(r"```.*?```", "", read(os.path.join(root, rel)), flags=re.S)):
            urls.setdefault(u, rel)
    bad = []
    for u, rel in sorted(urls.items()):
        req = urllib.request.Request(u, headers={"User-Agent": "learn-programming-the-weird-way-link-check/1.0"})
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                if r.status != 200:
                    bad.append(f"{rel}: HTTP {r.status}: {u}")
        except urllib.error.HTTPError as e:
            bad.append(f"{rel}: HTTP {e.code}: {u}")
        except Exception as e:
            bad.append(f"{rel}: {type(e).__name__}: {u}")
    print(f"checked {len(urls)} external link(s) in the study guides")
    return bad


def check_all(repo=None):
    repo = repo or REPO
    root = groot(repo)
    problems = check_set(repo)
    for g in ALL_GUIDES:
        path = os.path.join(root, GP(g))
        if os.path.isfile(path):
            problems += check_guide(g, read(path), repo)
    for extra in ("README.md",):
        problems += [p for p in check_links(extra, read(os.path.join(root, extra)), repo)]
    return problems


if __name__ == "__main__":
    probs = check_all()
    print("\n".join("PROBLEM " + p for p in probs) or "study guides ok")
    sys.exit(1 if probs else 0)
