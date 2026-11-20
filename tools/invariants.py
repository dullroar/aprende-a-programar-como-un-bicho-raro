#!/usr/bin/env python3
"""invariants: deterministic checks I1 to I16 (plan 7.2). Every check fails closed and returns Findings.

Three entry points, all pure functions over text (no network, no model):

  check_segment(src, target, ctx)        I2 to I12, I14, I15 for ONE segment. `src` is a segment of the English
                                         Segmentation (Block or Label), `target` the translated MASKED text.
  check_po(en_text, po, rel, ctx)        every entry of one PO file against its English file: the segment
                                         checks on each applied entry plus I16 coverage (orphan, duplicate, stale,
                                         missing, empty, fuzzy).
  check_files(en_text, es_text, rel, ctx)  the file-level checks on a pair of finished files: I1 (T0 on the
                                         English file), I4 links, I5 Mermaid skeleton, I6 front matter,
                                         I11 bold count, I13 code and output spans, and I2 by value.
  protected_files(root)                  I13 for the frozen files of the whole tree (wraps lock_code).

Invariant table (plan 7.2)
  I1  T0 identity round trip          I9  no English left (stopword ratio)
  I2  placeholder multiset            I10 paired inverted marks, straight quotes, Mermaid label syntax
  I3  digit-token multiset            I11 bold-span count, fixed lead-ins from the locale catalog
  I4  link destinations (anchor map)  I12 sentence length (N) and register (tu), tier T1 only
  I5  Mermaid skeleton                I13 code and output spans equal the English source
  I6  front-matter keys and enums     I14 surviving English phase letters and names, literal Spanish letters
  I7  glossary rendering and banned   I15 humor register status
  I8  DNT phrases present             I16 segment coverage
A finding can be waived only by a row in translation/exception-register.jsonl that names the segment and the
invariant ({"segment": "s-...", "invariant": "I9", "reason": "..."}); nothing else turns a finding off.

Usage:
  python3 -I tools/invariants.py --list                       print the invariant table
  python3 -I tools/invariants.py --po FILE.md [PO]            check one PO file (default translation/po/FILE.md.po)
  python3 -I tools/invariants.py --files EN.md ES.md          file-level checks on a pair of finished files
  python3 -I tools/invariants.py --t0 [FILE.md ...]           I1 on the given (default: all authored) files
  python3 -I tools/invariants.py --protected                  I13 for the protected files of the tree
Exit 0 = no findings.
"""
import json
import os
import re
import sys
from collections import Counter, namedtuple

import polib
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
import apply as apply_mod  # noqa: E402
import catalog  # noqa: E402
import enpath  # noqa: E402
import mask  # noqa: E402
import mermaid  # noqa: E402
import phase_lint  # noqa: E402
import segment  # noqa: E402

TRANSLATION = os.path.join(ROOT, "translation")
TABLE = {
    "I1": "Segmenter identity round trip is byte-identical (T0)",
    "I2": "Placeholder multiset in the target equals the source's",
    "I3": "Digit-token multiset equal",
    "I4": "Link destinations equal after the anchor map",
    "I5": "Mermaid skeleton equal",
    "I6": "Front-matter keys and enums unchanged",
    "I7": "Glossary: approved rendering present, banned terms absent",
    "I8": "DNT phrases of the source are in the target",
    "I9": "No segment left in English",
    "I10": "Paired inverted marks; straight quotes; Mermaid label syntax",
    "I11": "Bold-span count equal; fixed lead-ins from the locale catalog",
    "I12": "Sentence length and register (tier T1)",
    "I13": "Code and output spans equal the English source",
    "I14": "Phase-letter lint",
    "I15": "Humor register status recorded",
    "I16": "Segment coverage",
}

Finding = namedtuple("Finding", "inv where msg")

PLACEHOLDER_RE = mask.PH_RE
MACRO_RE = re.compile(r"\{\{[^}\n]+\}\}|\[\[[^\]\n]+\]\]")
NUMBER_RE = re.compile(r"\d+(?:\.\d+)*")
WORD_RE = re.compile(r"[^\W\d_]+(?:['’][^\W\d_]+)?")
BOLD_RE = re.compile(r"\*\*(?=\S)(.+?)(?<=\S)\*\*")
LINK_RE = re.compile(r"\]\(\s*<?([^)\s>]+)>?(?:\s+\"[^\"]*\")?\s*\)")
REFDEF_RE = re.compile(r"^ {0,3}\[[^\]\n]+\]:\s*(\S+)", re.M)
FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})")
SENTENCE_END_RE = re.compile(r"(?<=[.!?…])[*_\"')\]]*\s+")  # closing emphasis or quote may follow the stop
BAD_QUOTES = "“”«»‘’"
# unambiguous English function words (words that are also Spanish words, such as a, no, me, he, as, are left out)
EN_STOP = frozenset("""the and of to is are was were that with for this you your not from it be can what which when
if or by an at on in has have will would should does do been being their there then than these those into
about because while where who how why also only just but more most some any each every other such both""".split())
ES_STOP = frozenset("""el la los las de del que y en un una unos unas con por para es son no se lo al como más pero
su sus este esta estos estas ese esa eso muy también sin sobre entre cuando donde qué cómo tú te tu si ya hay""".split())
REGISTER_BAD = re.compile(r"\b(?:usted|vos|tenés|podés|querés|sabés|mirá|hacé|decime|fijate)\b", re.I)
SKIP_FENCE_KINDS = ("mermaid", "generated")


# ------------------------------------------------------------------------------------------ context

class Context:
    """Everything the checks read besides the two texts. Build it once; tests build small ones by hand."""

    def __init__(self, dnt=(), glossary=None, cat=None, humor=None, exceptions=None, anchor_map=None,
                 sentence_limit=28, tier_of=None, phase_names=None, lang_cat=None, exercise_prefixes=()):
        self.dnt = list(dnt)
        self.terms = []                       # [(en regex, es text, banned list, id)]
        self.banned_phrases = []              # [(phrase, label)] extra banned phrases (frozen wording)
        self.load_glossary(glossary or {})
        self.cat = cat                        # target-language catalog (phases, acronym), or None
        self.lang_cat = lang_cat              # English catalog, for fixed lead-ins
        self.humor = humor or {}              # english text -> row
        self.exceptions = exceptions or set()  # {(segment id, invariant)}
        self.anchor_map = anchor_map or {}
        self.sentence_limit = sentence_limit
        self.tier_of = tier_of or (lambda rel: "T2")
        self.phase_names = phase_names or []  # English phase names to hunt for (Weird, Execution, ...)
        self.exercise_prefixes = list(exercise_prefixes)  # letters that start exercise IDs (phase_lint, I14)

    def load_glossary(self, data):
        plain = re.compile(r"^[A-Za-z][A-Za-z' -]*$")
        for t in data.get("terms", []) or []:
            en, es = t.get("en"), t.get("es")
            if not isinstance(en, str) or not isinstance(es, str):
                continue
            rx = None
            if plain.match(en) and not t.get("literal"):
                rx = re.compile(r"(?<!\w)%s(?:s|es)?(?!\w)" % re.escape(en), re.I)
            self.terms.append((rx, es, list(t.get("banned") or []), t.get("id")))
        frozen = data.get("frozen", {}) or {}
        for p in (frozen.get("timecard_rule", {}) or {}).get("banned", []) or []:
            self.banned_phrases.append((p, "timecard rule"))
        for lab in (frozen.get("assurance_labels", {}) or {}).get("labels", []) or []:
            # An assurance label is banned only where the English names that label ('safe' is not 'guaranteed').
            stem = re.sub(r"[^a-z]", "", str(lab.get("enum", "")).split("-")[0].lower())[:6]
            trigger = re.compile(r"(?<!\w)%s" % re.escape(stem), re.I) if stem else None
            for p in lab.get("banned", []) or []:
                self.banned_phrases.append((p, "assurance label", trigger))

    def waived(self, seg_id, inv):
        return (seg_id, inv) in self.exceptions


def load_context(lang="es", root=ROOT):
    """The real context of this repository."""
    tr = os.path.join(root, "translation")
    with open(os.path.join(tr, "glossary.es.yaml"), encoding="utf-8") as f:
        glossary = yaml.safe_load(f)
    humor = {}
    path = os.path.join(tr, "humor-register.jsonl")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for ln in f:
                if ln.strip():
                    row = json.loads(ln)
                    humor[row["english"]] = row
    exceptions = set()
    path = os.path.join(tr, "exception-register.jsonl")
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for ln in f:
                if ln.strip():
                    row = json.loads(ln)
                    if row.get("segment") and row.get("invariant"):
                        exceptions.add((row["segment"], row["invariant"]))
    import inventory
    cfg = inventory.read_config(root)
    en_cat = catalog.load("en")
    names = [en_cat.get("phases.%d.name" % n) for n in range(1, 6)]
    return Context(dnt=mask.load_dnt(os.path.join(tr, "dnt.txt")), glossary=glossary, cat=catalog.load(lang),
                   lang_cat=en_cat, humor=humor, exceptions=exceptions,
                   sentence_limit=int(cfg.get("sentence_word_limit_N", 28)), tier_of=tier_of_path,
                   phase_names=[n for n in names if isinstance(n, str)],
                   exercise_prefixes=phase_lint.load_prefixes(os.path.join(tr, "phase-letters.json")))


def tier_of_path(rel):
    """Tier from the house style (section 1). Unknown files take the strictest tier."""
    if rel.startswith(("lessons/study-guides/", "docs/curriculum", "lessons/curriculum/")) or "SHARED_CHALLENGE" in rel:
        return "T1"
    if rel in ("CONTRIBUTING.md", "SANDBOX-SETUP.md") or rel.startswith(("docs/sandbox", "lessons/book/")):
        return "T3"
    if rel.startswith(("lessons/", "src/")) or rel in ("README.md", "CHALLENGE.md"):
        return "T2"
    return "T1"


# ------------------------------------------------------------------------------------------ helpers

def strip_ph(text):
    return PLACEHOLDER_RE.sub(" ", text)


def prose(text):
    """Text with placeholders, macros and inline code removed: what a reader reads as words."""
    return MACRO_RE.sub(" ", strip_ph(re.sub(r"`[^`\n]*`", " ", text)))


def numbers(text):
    return Counter(NUMBER_RE.findall(prose(text)))


def restore(seg, target):
    mk = mask.Masker([])
    mk.mapping = seg.mapping
    return mk.unmask(target)


def link_destinations(text):
    """Link destinations in `text` (inline links and reference definitions), fenced code excluded, in order."""
    out, fenced = [], False
    for line in text.split("\n"):
        if FENCE_RE.match(line):
            fenced = not fenced
            continue
        if fenced:
            continue
        out.extend(LINK_RE.findall(line))
        m = REFDEF_RE.match(line)
        if m:
            out.append(m.group(1))
    return out


def map_anchor(dest, anchor_map):
    if dest in anchor_map:
        return anchor_map[dest]
    if "#" in dest:
        base, frag = dest.split("#", 1)
        if frag in anchor_map:
            return base + "#" + anchor_map[frag]
        if "#" + frag in anchor_map:
            return base + anchor_map["#" + frag]
    return dest


def sentences(text):
    return [s for s in SENTENCE_END_RE.split(text.strip()) if s.strip()]


def word_count(sentence):
    return sum(1 for tok in sentence.split() if re.search(r"[^\W_]", tok))


# ------------------------------------------------------------------------------------------ segment checks

def i2(src, target):
    return [Finding("I2", "", p) for p in mask.check_placeholders(src.masked, target)]


COMPARE_RE = re.compile(r"[≤≥<>≠]")


def _signs(text):
    return text.replace("<=", "≤").replace(">=", "≥").replace("!=", "≠")


def i3(src, target):
    a, b = numbers(src.masked), numbers(target)
    out = []
    for tok in sorted(set(a) | set(b)):
        if a[tok] != b[tok]:
            out.append(Finding("I3", "", "digit token %s appears %d time(s) in the source, %d in the target" % (tok, a[tok], b[tok])))
    # a comparison sign written in prose or in a diagram label ("total ≤ 40") is a boundary: < for ≤ moves the stop rule
    # (words may replace a sign, so only a sign the source does not have as often is refused)
    ca, cb = Counter(COMPARE_RE.findall(_signs(src.masked))), Counter(COMPARE_RE.findall(_signs(target)))
    for sign in sorted(cb):
        if cb[sign] > ca[sign]:
            out.append(Finding("I3", "", "comparison sign %s appears %d time(s) in the target, %d in the source" % (sign, cb[sign], ca[sign])))
    return out


def i4(src_text, tgt_text, ctx):
    a = [map_anchor(d, ctx.anchor_map) for d in link_destinations(src_text)]
    b = link_destinations(tgt_text)
    if a != b:
        return [Finding("I4", "", "link destinations differ: %s -> %s" % (a, b))]
    return []


def approved_form(es):
    """The approved rendering without its parenthetical gloss: 'sandbox entorno aislado (*sandbox*)' needs
    only the part before the parentheses to be present."""
    return re.sub(r"\s*\([^)]*\)", "", es).strip().lower()


def es_plural(word):
    """Regular Spanish plural of one lowercase word (the English term regex already accepts -s/-es)."""
    if word.endswith("ón"):
        return word[:-2] + "ones"
    if word.endswith("z"):
        return word[:-1] + "ces"
    if word.endswith(("a", "e", "i", "o", "u", "á", "é", "í", "ó", "ú")):
        return word + "s"
    return word + "es"


def form_variants(es):
    """The approved form and its regular plurals: 'tarjeta de horas' -> 'tarjetas de horas';
    'total acumulado' -> 'totales acumulados'. A missing term still fails; only the plural is also accepted."""
    base = approved_form(es)
    words = base.split()
    variants = {base}
    if words:
        variants.add(" ".join([es_plural(words[0])] + words[1:]))
        if "de" not in words and len(words) > 1:
            variants.add(" ".join(es_plural(w) for w in words))
    # Gender agreement of an adjective ending in -o: 'recursivo' -> 'recursiva', 'recursivas' (a feminine noun).
    for v in list(variants):
        w = v.split()
        if w and w[-1].endswith("os"):
            variants.add(" ".join(w[:-1] + [w[-1][:-2] + "as"]))
        elif w and w[-1].endswith("o"):
            variants.add(" ".join(w[:-1] + [w[-1][:-1] + "a"]))
    return variants


LEAD_IN_RE = re.compile(r"^\s*\*\*(.+?)\*\*")


def has_catalog_lead_in(src, ctx):
    """True when the segment opens with a fixed catalog lead-in; I11 pins its exact Spanish, so I7 skips it."""
    if ctx.lang_cat is None or ctx.cat is None:
        return False
    m = LEAD_IN_RE.match(src.text)
    return bool(m) and any(("lead_in" in k or "leadin" in k) and ctx.lang_cat.get(k) == m.group(1)
                           for k in ctx.lang_cat.keys())


def i7(src, target, ctx):
    out = []
    src_words = prose(src.masked)
    low = prose(target).lower()
    if has_catalog_lead_in(src, ctx):
        src_words = LEAD_IN_RE.sub(" ", src_words, count=1)
        low = LEAD_IN_RE.sub(" ", low, count=1)
    for rx, es, banned, tid in ctx.terms:
        if rx is not None and rx.search(src_words) and not any(v in low for v in form_variants(es)):
            out.append(Finding("I7", "", "glossary term %s must be rendered '%s'" % (tid, es)))
        # A banned rendering is banned FOR its term: it counts only where the English uses that term
        # ('carpeta' for 'folder' and 'mecanismo' for 'mechanism' are not renderings of 'directory' or 'machine').
        if rx is not None and not rx.search(src_words):
            continue
        for b in banned:
            pat = r"(?<!\w)%s(?!\w)" % re.escape(b.lower())
            if re.search(pat, low) and not re.search(pat, src_words.lower()):
                out.append(Finding("I7", "", "banned rendering '%s' for glossary term %s" % (b, tid)))
    for entry in ctx.banned_phrases:
        phrase, label = entry[0], entry[1]
        trigger = entry[2] if len(entry) > 2 else None
        if trigger is not None and not trigger.search(src_words):
            continue
        if phrase.lower() in low and phrase.lower() not in src_words.lower():
            out.append(Finding("I7", "", "banned phrase '%s' (%s)" % (phrase, label)))
    return out


def dnt_in(text, phrase):
    return re.search(r"(?<!\w)%s(?!\w)" % re.escape(phrase), text) is not None


def i8(src_text, tgt_text, ctx):
    return [Finding("I8", "", "DNT phrase '%s' of the source is missing in the target" % p)
            for p in sorted(set(ctx.dnt)) if dnt_in(src_text, p) and not dnt_in(tgt_text, p)]


def i9(src, target):
    words = [w.lower() for w in WORD_RE.findall(prose(target))]
    src_words = WORD_RE.findall(prose(src.masked))
    if len(words) < 3:
        return []
    en = sum(1 for w in words if w in EN_STOP)
    es = sum(1 for w in words if w in ES_STOP)
    ratio = en / len(words)
    if ratio >= 0.2 and en > es:
        return [Finding("I9", "", "looks English: %d of %d words are English function words" % (en, len(words)))]
    if len(src_words) >= 4 and prose(target).strip() == prose(src.masked).strip():
        return [Finding("I9", "", "target equals the English source")]
    return []


def paired_marks(text):
    """Problems with inverted marks: every opener has its closer, in order, and no closer is bare."""
    out = []
    for open_, close in (("¿", "?"), ("¡", "!")):
        depth = 0
        for ch in text:
            if ch == open_:
                depth += 1
            elif ch == close:
                depth -= 1
                if depth < 0:
                    out.append("'%s' without '%s'" % (close, open_))
                    depth = 0
        if depth:
            out.append("'%s' without '%s'" % (open_, close))
    return out


def i10(src, target, tgt_text):
    out = [Finding("I10", "", p) for p in paired_marks(strip_ph(target))]
    for ch in BAD_QUOTES:
        if ch in strip_ph(target) and ch not in src.masked:
            out.append(Finding("I10", "", "curly or angle quote %r (use straight quotes)" % ch))
    if getattr(src, "kind", "") == "mermaid_label":
        out.extend(Finding("I10", "", p) for p in mermaid.label_problems(src.span, tgt_text))
    return out


def bold_spans(masked):
    return BOLD_RE.findall(masked)


SHARED_KEY = "study_guides.shared_challenge"
ANCHOR_RE = r"[^)\s]+"


def _norm_ws(text):
    return " ".join(text.split())


def _template_regex(template):
    """Regex for a catalog template whose only variable part is {anchor}; whitespace runs match one another."""
    parts = _norm_ws(template).split("{anchor}")
    return re.compile(ANCHOR_RE.join(re.escape(p) for p in parts))


def shared_paragraph(src_text, ctx):
    """The Spanish catalog paragraph (a template with {anchor}) when `src_text` is the English standard
    'shared challenge' paragraph of the study guides, else None. The study-guide check wants this text exactly."""
    if ctx.lang_cat is None or ctx.cat is None:
        return None
    try:
        en, es = ctx.lang_cat.text(SHARED_KEY), ctx.cat.text(SHARED_KEY)
    except (catalog.CatalogError, KeyError):
        return None
    if _template_regex(en).fullmatch(_norm_ws(src_text)):
        return es
    return None


def shared_paragraph_masked(src, ctx):
    """The same paragraph written over the source's placeholders (link destination, then the DNT category names, in
    order), the form a PO msgstr must have; None when `src` is not that paragraph or its placeholders do not line up."""
    es = shared_paragraph(src.text, ctx)
    if es is None:
        return None
    dests = [k for k in src.mapping if k.startswith("⟦DEST_")]
    dnts = [k for k in src.mapping if k.startswith("⟦DNT_")]
    names = re.findall(r"`([^`]+)`", es)
    if len(dests) != 1 or len(dnts) != len(names):
        return None
    out = _norm_ws(es).replace("{anchor}", "\0")
    out = re.sub(r"\(\.\./\.\./intro\.md#\0\)", "(" + dests[0] + ")", out)
    for k in dnts:
        out = out.replace("`" + src.mapping[k] + "`", "`" + k + "`", 1)
    return out if "\0" not in out else None


def i11_shared(src, tgt_text, ctx):
    es = shared_paragraph(src.text, ctx)
    if es is None or _template_regex(es).fullmatch(_norm_ws(tgt_text)):
        return []
    return [Finding("I11", "", "the standard shared-challenge paragraph must be the catalog text %s exactly" % SHARED_KEY)]


def i11(src, target, tgt_text, ctx):
    out = i11_shared(src, tgt_text, ctx) if getattr(src, "kind", "") != "mermaid_label" else []
    a, b = bold_spans(src.masked), bold_spans(target)
    if len(a) != len(b):
        out.append(Finding("I11", "", "bold spans: %d in the source, %d in the target" % (len(a), len(b))))
    if ctx.lang_cat is not None and ctx.cat is not None and a:
        m = re.match(r"^\s*\*\*(.+?)\*\*", src.text)
        if m:
            for key in ctx.lang_cat.keys():
                if "leadin" not in key and "lead_in" not in key:
                    continue
                if ctx.lang_cat.get(key) == m.group(1):
                    want = "**%s**" % ctx.cat.text(key)
                    if not tgt_text.lstrip().startswith(want):
                        out.append(Finding("I11", "", "fixed lead-in %s must be %s" % (key, want)))
    return out


def i12(src, target, rel, ctx):
    if ctx.tier_of(rel) != "T1":
        return []
    out = []
    for s in sentences(strip_ph_keep_words(target)):
        n = word_count(s)
        if n > ctx.sentence_limit:
            out.append(Finding("I12", "", "sentence of %d words (limit %d): %s..." % (n, ctx.sentence_limit, s[:40])))
    for m in REGISTER_BAD.finditer(prose(target)):
        out.append(Finding("I12", "", "register: '%s' (use tu)" % m.group(0)))
    return out


SEP_RE = re.compile(r"⟦SEP_[0-9]{4}⟧")


def strip_ph_keep_words(text):
    """Placeholders count as one word each (they stand for code); a table-cell separator ends a sentence."""
    return PLACEHOLDER_RE.sub("X", SEP_RE.sub(" . ", text))


def i14(src, target, ctx, raw=None):
    """Surviving English phase letters and names; literal letters where a macro belongs.

    `target` is the text as the reader sees it (macros expanded); `raw` is the text as written in the PO file,
    before expansion. The literal-letter checks read `raw`, because an expanded macro is a literal by then."""
    out = []
    text = prose(target)
    raw_text = prose(raw if raw is not None else target)
    src_text = prose(src.masked)
    for n, name in enumerate(ctx.phase_names, 1):
        pat = r"\b[A-Z]\s*:\s*%s\b|\bphase\s+(?:[A-Z]\b|%s\b)" % (re.escape(name), re.escape(name))
        # the English name only counts as a surviving phase name when it is written the phase way
        for m in re.finditer(pat, text):
            out.append(Finding("I14", "", "English phase name survives: '%s'" % m.group(0)))
    for msg in phase_lint.ambiguity(text, ctx.cat, ctx.exercise_prefixes):
        out.append(Finding("I14", "", msg))
    if ctx.lang_cat is not None and ctx.cat is not None:
        en_word, es_word = ctx.lang_cat.get("acronym.word"), ctx.cat.get("acronym.word")
        if en_word != es_word and dnt_in(text, en_word) and not dnt_in(src_text, es_word):
            out.append(Finding("I14", "", "English acronym %s survives (use {{acronym.word}})" % en_word))
        if es_word and dnt_in(raw_text, es_word):
            out.append(Finding("I14", "", "write {{acronym.word}}, not the literal acronym %s" % es_word))
        for n in range(1, 6):
            try:
                letter, name = ctx.cat.get("phases.%d.letter" % n), ctx.cat.get("phases.%d.name" % n)
            except catalog.CatalogError:
                break
            if isinstance(letter, str) and re.search(r"\b%s\s*:\s*%s\b" % (re.escape(letter), re.escape(name)), raw_text):
                out.append(Finding("I14", "", "literal phase '%s: %s' (use the phase macros)" % (letter, name)))
        # an English phase letter kept as a label ("W: Raro", "fase = W"); a letter shared with the Spanish set is skipped (ambiguous)
        es_letters = {ctx.cat.get("phases.%d.letter" % k) for k in range(1, 6) if "phases.%d.letter" % k in ctx.cat.flat}
        for k in range(1, 6):
            en_letter = ctx.lang_cat.flat.get("phases.%d.letter" % k)
            if not isinstance(en_letter, str) or en_letter in es_letters:
                continue
            if re.search(r"(?<![\w\-])%s\s*:\s*[A-ZÁÉÍÓÚÑ]|\bfase\s*=\s*%s\b" % (re.escape(en_letter), re.escape(en_letter)), raw_text):
                out.append(Finding("I14", "", "English phase letter '%s' kept as a label (use the phase macros)" % en_letter))
            # a bare English phase letter that the source also wrote bare ("starts at W again"), kept as it was
            # (a letter that also starts an exercise ID, such as the section D, is ambiguous and skipped)
            bare = r"(?<![\w\-/.])%s(?![\w\-/])" % re.escape(en_letter)
            if en_letter not in ctx.exercise_prefixes and re.search(bare, src_text) and re.search(bare, raw_text):
                out.append(Finding("I14", "", "English phase letter '%s' survives in prose (use {{phase.%d.letter}})" % (en_letter, k)))
    return out


def i15(src, tgt_text, ctx):
    row = ctx.humor.get(src.text.strip()) if src.kind == "heading" else None
    if row is None and src.kind != "heading":
        flat = " ".join(src.text.split())
        row = next((r for e, r in ctx.humor.items() if r.get("kind") != "heading" and e in flat), None)
    if row is None:
        return []
    status = row.get("status")
    if status not in ("kept", "transcreated", "deliberately-flattened"):
        return [Finding("I15", "", "playful segment %s has status '%s' in the humor register" % (row["id"], status))]
    if status == "deliberately-flattened" and not row.get("reviewer_note"):
        return [Finding("I15", "", "%s is flattened without a recorded reason" % row["id"])]
    if status in ("kept", "transcreated") and row.get("spanish") and row["kind"] == "heading" \
            and row["spanish"].strip() != tgt_text.strip():
        return [Finding("I15", "", "heading differs from the recorded %s '%s'" % (status, row["spanish"]))]
    return []


def check_segment(src, target, ctx, rel="", raw=None):
    """All per-segment invariants for one translated MASKED `target`. Returns a list of Findings.

    `raw` is the PO msgstr before macro expansion (I14 reads it for literal letters); default: `target`."""
    findings = i2(src, target)
    if findings:
        return [f._replace(where=src.id) for f in findings]      # nothing else can be trusted
    try:
        tgt_text = restore(src, target)
    except ValueError as e:
        return [Finding("I2", src.id, str(e))]
    findings += i3(src, target)
    if src.kind != "mermaid_label":
        findings += i4(src.text, tgt_text, ctx)
    findings += i7(src, target, ctx)
    findings += i8(src.text, tgt_text, ctx)
    findings += i9(src, target)
    findings += i10(src, target, tgt_text)
    findings += i11(src, target, tgt_text, ctx)
    findings += i12(src, target, rel, ctx)
    findings += i14(src, target, ctx, raw)
    findings += i15(src, tgt_text, ctx)
    return [f._replace(where=src.id) for f in findings if not ctx.waived(src.id, f.inv)]


# ------------------------------------------------------------------------------------------ I16 and PO

def check_po(en_text, po, rel, ctx):
    """Segment checks for every applied entry of `po`, plus coverage (I16)."""
    out = []
    try:
        seg = segment.Segmentation(en_text, rel)
    except segment.SegmentError as e:
        return [Finding("I1", rel, "segmenter refused: %s" % e)]
    by_id = {s.id: s for s in seg.segments()}
    seen = Counter(e.msgctxt for e in po)
    for sid, n in sorted(seen.items()):
        if n > 1:
            out.append(Finding("I16", sid, "duplicate PO entry (%d times)" % n))
    for e in po:
        s = by_id.get(e.msgctxt)
        if s is None:
            out.append(Finding("I16", e.msgctxt, "orphan PO entry: no such segment in the English file"))
        elif e.msgid != s.masked:
            out.append(Finding("I16", e.msgctxt, "stale PO entry: msgid is not the current English text"))
    done = {e.msgctxt: e for e in po if e.msgctxt in by_id and e.msgid == by_id[e.msgctxt].masked}
    for sid, s in by_id.items():
        e = done.get(sid)
        if ctx.waived(sid, "I16"):
            continue
        if e is None:
            out.append(Finding("I16", sid, "segment has no PO entry (silently dropped)"))
        elif "fuzzy" in e.flags:
            out.append(Finding("I16", sid, "segment is fuzzy: not accepted"))
        elif not e.msgstr.strip():
            out.append(Finding("I16", sid, "segment is untranslated"))
        else:
            text = e.msgstr
            if ctx.cat is not None and "{{" in text:
                try:
                    text = ctx.cat.expand(text)
                except catalog.CatalogError as ex:
                    out.append(Finding("I14", sid, str(ex)))
                    continue
            out.extend(check_segment(s, text, ctx, rel, raw=e.msgstr))
    return out


# ------------------------------------------------------------------------------------------ file-level

def front_matter_lines(text):
    lines = text.split("\n")
    if not lines or lines[0].strip() != "---":
        return []
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return lines[1:i]
    return []


def fm_entries(lines):
    """[(key, [lines])]: a key and its continuation lines."""
    out = []
    for ln in lines:
        m = re.match(r"^([A-Za-z][\w-]*):", ln)
        if m:
            out.append((m.group(1), [ln]))
        elif out:
            out[-1][1].append(ln)
        else:
            out.append((None, [ln]))
    return out


def i6(en_text, es_text):
    a, b = fm_entries(front_matter_lines(en_text)), fm_entries(front_matter_lines(es_text))
    if [k for k, _ in a] != [k for k, _ in b]:
        return [Finding("I6", "", "front-matter keys differ: %s -> %s" % ([k for k, _ in a], [k for k, _ in b]))]
    out = []
    for (k, x), (_, y) in zip(a, b):
        if k in segment.FM_TRANSLATE_KEYS:
            continue
        if x != y:
            out.append(Finding("I6", "", "front-matter value of '%s' changed: %r -> %r" % (k, x[0].strip()[:40], y[0].strip()[:40])))
    return out


def inline_code(text):
    return Counter(re.findall(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", text))


def drop_dnt_spans(spans, dnt):
    """Remove from an inline-code Counter the single-backtick spans that wrap exactly one DNT phrase (for example `Meetings`).

    The frozen Spanish wording writes the card categories as code where the English prose writes them bare; the phrase itself is
    still required by I8, and every other code span is compared as before."""
    return Counter({k: n for k, n in spans.items() if not (k[0] == "`" and k[1] in dnt)})


def i13_text(en_text, es_text, rel="", dnt=()):
    """Code and output of a Spanish file equal the English file's: fenced blocks in order, inline spans as multisets.

    `dnt` is the list of do-not-translate phrases; a span that wraps only one of them is ignored on both sides."""
    try:
        sa, sb = segment.Segmentation(en_text, rel), segment.Segmentation(es_text, rel)
    except segment.SegmentError as e:
        return [Finding("I13", rel, "segmenter refused: %s" % e)]
    out = []
    ka = [b.kind for b in sa.blocks if b.kind not in ("blank",)]
    kb = [b.kind for b in sb.blocks if b.kind not in ("blank",)]
    if ka != kb:
        out.append(Finding("I13", rel, "block structure differs (%d -> %d blocks)" % (len(ka), len(kb))))
        return out
    for x, y in zip(sa.blocks, sb.blocks):
        if x.kind in SKIP_FENCE_KINDS or x.kind in segment.SEGMENT_KINDS or x.kind in ("blank", "frontmatter_keep"):
            if x.kind == "generated" and x.lines != y.lines:
                out.append(Finding("I13", rel, "generated block at line %d differs (regenerate, never edit)" % (x.start + 1)))
            continue
        if x.lines != y.lines:
            out.append(Finding("I13", rel, "%s block at line %d differs from the English source" % (x.kind, x.start + 1)))
    ca = Counter()
    cb = Counter()
    for b in sa.blocks:
        if b.kind in segment.SEGMENT_KINDS:
            ca.update(inline_code(b.text or ""))
    for b in sb.blocks:
        if b.kind in segment.SEGMENT_KINDS:
            cb.update(inline_code(b.text or ""))
    dnt = set(dnt)
    ca, cb = drop_dnt_spans(ca, dnt), drop_dnt_spans(cb, dnt)
    if ca != cb:
        miss = sorted((ca - cb).elements())[:3]
        extra = sorted((cb - ca).elements())[:3]
        out.append(Finding("I13", rel, "inline code spans differ: missing %s, extra %s" % (miss, extra)))
    return out


def i5(en_text, es_text, rel=""):
    try:
        sa, sb = segment.Segmentation(en_text, rel), segment.Segmentation(es_text, rel)
    except segment.SegmentError as e:
        return [Finding("I5", rel, "segmenter refused: %s" % e)]
    ma = [b for b in sa.blocks if b.kind == "mermaid"]
    mb = [b for b in sb.blocks if b.kind == "mermaid"]
    if len(ma) != len(mb):
        return [Finding("I5", rel, "%d Mermaid diagram(s) in the source, %d in the target" % (len(ma), len(mb)))]
    out = []
    for x, y in zip(ma, mb):
        for p in mermaid.skeleton_problems(x.lines[1:-1], y.lines[1:-1]):
            out.append(Finding("I5", "%s:%d" % (rel, x.start + 1), p))
        if x.lines[0] != y.lines[0] or x.lines[-1] != y.lines[-1]:
            out.append(Finding("I5", "%s:%d" % (rel, x.start + 1), "fence lines differ"))
    return out


def values(seg_blocks, dnt=()):
    """Multiset of protected token values; a single-backtick span around exactly one DNT phrase counts as the bare phrase."""
    dnt = set(dnt)
    c = Counter()
    for b in seg_blocks:
        for v in b.mapping.values():
            m = re.fullmatch(r"`([^`]+)`", v)
            c[m.group(1) if m and m.group(1) in dnt else v] += 1
    return c


def check_files(en_text, es_text, rel="", ctx=None):
    """File-level invariants for a finished Spanish file against its English source."""
    ctx = ctx or Context()
    out = [Finding("I1", rel, p) for p in segment.check_roundtrip(en_text, rel)]
    out += [f._replace(where=f.where or rel) for f in i6(en_text, es_text)]
    out += i5(en_text, es_text, rel)
    out += i13_text(en_text, es_text, rel, ctx.dnt)
    a = [d for d in link_destinations(en_text)]
    b = link_destinations(es_text)
    a = [map_anchor(d, ctx.anchor_map) for d in a]
    if a != b:
        out.append(Finding("I4", rel, "link destinations differ (%d in the source, %d in the target)" % (len(a), len(b))))
    try:
        sa, sb = segment.Segmentation(en_text, rel), segment.Segmentation(es_text, rel)
    except segment.SegmentError as e:
        return out + [Finding("I1", rel, "segmenter refused: %s" % e)]
    ba = [x for x in sa.blocks if x.kind in segment.SEGMENT_KINDS and x.translate]
    bb = [x for x in sb.blocks if x.kind in segment.SEGMENT_KINDS and x.translate]
    if values(ba, ctx.dnt) != values(bb, ctx.dnt):
        out.append(Finding("I2", rel, "protected tokens (code, URLs, macros, DNT) differ between the files"))
    if len(ba) == len(bb):
        for x, y in zip(ba, bb):
            if bold_spans(x.masked).__len__() != bold_spans(y.masked).__len__():
                out.append(Finding("I11", "%s:%d" % (rel, x.start + 1), "bold spans differ"))
    return out


def protected_files(root=ROOT):
    """I13 for the whole tree: every frozen file equals the English bytes (wraps lock_code)."""
    import lock_code
    entries = lock_code.load_manifest(root)
    return [Finding("I13", p.split("  ", 1)[1], p.split("  ", 1)[0].strip().lower() + " frozen file differs from the English source")
            for p in lock_code.tree_problems(root, entries)]


# ------------------------------------------------------------------------------------------ CLI

def report(findings, label):
    for f in findings:
        print("%s %s: %s" % (f.inv, f.where, f.msg))
    print("%s: %s" % (label, "FAIL (%d finding(s))" % len(findings) if findings else "OK"))
    return 1 if findings else 0


def read_raw(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def main(argv):
    args = argv[1:]
    if args == ["--list"]:
        for k, v in TABLE.items():
            print("%-4s %s" % (k, v))
        return 0
    if args and args[0] == "--t0":
        files = args[1:] or segment.authored_files()
        found = []
        for arg in files:
            p, full = enpath.locate(arg, ROOT)
            found += [Finding("I1", p, m) for m in segment.check_roundtrip(read_raw(full), p)]
        return report(found, "I1 on %d file(s)" % len(files))
    if args and args[0] == "--protected":
        return report(protected_files(), "I13 protected files")
    if len(args) >= 2 and args[0] == "--po":
        rel, full = enpath.locate(args[1], ROOT)
        po_path = args[2] if len(args) > 2 else apply_mod.po_path_for(rel)
        ctx = load_context()
        return report(check_po(read_raw(full), apply_mod.load_po(po_path), rel, ctx), "PO %s" % rel)
    if len(args) == 3 and args[0] == "--files":
        ctx = load_context()
        return report(check_files(read_raw(args[1]), read_raw(args[2]), args[1], ctx), "files %s %s" % (args[1], args[2]))
    print(__doc__.split("Usage:")[1].rstrip())
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
