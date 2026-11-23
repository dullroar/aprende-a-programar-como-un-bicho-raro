#!/usr/bin/env python3
"""apply: write PO targets back into a Markdown file (plan 5.2, 7.1 R2, 8; invariant I1/T0).

One PO file per Markdown file: translation/po/<path>.po. Each entry is one translatable segment:

  msgctxt  segment id (s-<sha12>-<pos>)          msgid   the English MASKED text
  msgstr   the Spanish MASKED text (placeholders such as ⟦CODE_0001⟧ stay as they are)
  #:       <path>:<first line>                   #, fuzzy   marks a draft: NOT applied until the flag is cleared

PO files hold text only; provenance lives in the JSONL ledger. Applying a PO file to the English source:

  * replaces only the lines of segments that have a non-empty, non-fuzzy msgstr (R2); every other line,
    prefix, suffix, fence, comment, table separator and generated block is copied unchanged;
  * expands the phase macros {{phase.N.letter}}, {{phase.N.name}} and {{acronym.word}} in the TRANSLATED
    text from the locale catalog, before placeholders are restored, so English-side {{...}} macros that
    were masked are never touched;
  * checks invariant I2 (placeholders) on every target and fails closed: a wrong target raises ApplyError
    and no output is written.

An identity PO (msgstr == msgid) and an empty PO (no msgstr) both reproduce the English file byte for byte.
A PO entry whose segment id is not in the English file is an orphan (stale after the English changed): it
is an error in strict mode (the default) so a moved or edited paragraph cannot be silently dropped.

Usage:
  python3 -I tools/apply.py --identity [FILE.md ...]   T0 through the PO layer on every hand-written file
  python3 -I tools/apply.py --init FILE.md [--identity] [--po PO]    create a PO (empty msgstr, or identity)
  python3 -I tools/apply.py FILE.md [--po PO] [--out OUT|-|--write] [--lang es] [--lenient]
                                       apply a PO file (no --out/--write = dry run with counts only)
  python3 -I tools/apply.py --relink [--write] [FILE.md ...]
                                       re-aim the link fragments of every hand-written file (or the named ones) after
                                       `anchors.py --generate`: the file is its PO applied (or the English text) through
                                       anchors.layout_text; prints the files that change, writes them with --write
"""
import os
import re
import sys

import polib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
import anchors  # noqa: E402
import categories  # noqa: E402
import catalog  # noqa: E402
import enpath  # noqa: E402
import segment  # noqa: E402

PO_DIR = os.path.join(ROOT, "translation", "po")
DEFAULT_LANG = "es"


class ApplyError(ValueError):
    """The PO file cannot be applied to this source. Nothing is written."""


def po_path_for(rel_path, po_dir=PO_DIR):
    return os.path.join(po_dir, rel_path + ".po")


def new_po(seg, rel_path, identity=False):
    """A PO file for `seg`: one entry per translatable segment (msgstr empty, or equal to msgid)."""
    po = polib.POFile(wrapwidth=0)
    po.metadata = {
        "Project-Id-Version": "aprende-a-programar-como-un-bicho-raro",
        "Language": "es-419",
        "MIME-Version": "1.0",
        "Content-Type": "text/plain; charset=UTF-8",
        "Content-Transfer-Encoding": "8bit",
    }
    for b in seg.segments():
        po.append(polib.POEntry(msgctxt=b.id, msgid=b.masked, msgstr=b.masked if identity else "",
                                occurrences=[(rel_path, str(b.start + 1))]))
    return po


def load_po(path):
    po = polib.pofile(path, wrapwidth=0, encoding="utf-8")
    seen = set()
    for e in po:
        if not e.msgctxt:
            raise ApplyError("%s: entry without msgctxt (segment id): %r" % (path, e.msgid[:40]))
        if e.msgctxt in seen:
            raise ApplyError("%s: duplicate segment id %s" % (path, e.msgctxt))
        seen.add(e.msgctxt)
    return po


def targets_from_po(po, seg, cat=None, strict=True):
    """Map segment id -> translated masked text (macros expanded). Returns (targets, stats).

    Empty msgstr and fuzzy entries are not applied (the English stays). A msgid that differs from the
    English masked text means the entry belongs to an older English text: error in strict mode.
    """
    by_id = {b.id: b for b in seg.segments()}
    targets = {}
    stats = {"segments": len(by_id), "applied": 0, "empty": 0, "fuzzy": 0, "orphan": 0, "stale": 0}
    errors = []
    for e in po:
        b = by_id.get(e.msgctxt)
        if b is None:
            stats["orphan"] += 1
            errors.append("orphan entry %s (no such segment in the English file)" % e.msgctxt)
            continue
        if e.msgid != b.masked:
            stats["stale"] += 1
            errors.append("entry %s: msgid is not the current English text" % e.msgctxt)
            continue
        if "fuzzy" in e.flags:
            stats["fuzzy"] += 1
            continue
        if not e.msgstr.strip():
            stats["empty"] += 1
            continue
        text = e.msgstr
        if cat is not None and "{{" in text:
            try:
                text = cat.expand(text)
            except catalog.CatalogError as ex:
                raise ApplyError("entry %s: %s" % (e.msgctxt, ex)) from None
        targets[e.msgctxt] = text
        stats["applied"] += 1
    if strict and errors:
        raise ApplyError("; ".join(errors))
    return targets, stats


def apply_text(text, po, rel_path="", cat=None, strict=True):
    """Return (new_text, stats): `text` with the PO targets applied."""
    try:
        seg = segment.Segmentation(text, rel_path)
    except segment.SegmentError as e:
        raise ApplyError("segmenter refused %s: %s" % (rel_path, e)) from None
    targets, stats = targets_from_po(po, seg, cat, strict)
    try:
        out = seg.reassemble(targets)
    except ValueError as e:
        raise ApplyError("%s: %s" % (rel_path, e)) from None
    if rel_path in category_files() and any(e.msgstr and e.msgstr != e.msgid and "fuzzy" not in e.flags for e in po):
        out = localize_category_rows(out)
    if rel_path in category_prose_files() and any(e.msgstr and e.msgstr != e.msgid and "fuzzy" not in e.flags for e in po):
        out = localize_category_words(out)
    return out, stats


CATEGORY_PROSE_FILES = os.path.join("translation", "part2", "category-localized-prose.txt")
# (?=tc_tab): the m4 entry's glued-word example `Meetingstc_tab` names the word followed by a macro
_WORD_RE = re.compile(r"(?<![\w(])(%s)(?:(?=tc_tab)|(?![\w)]))" % "|".join(categories.EN))


def category_prose_files():
    """English keys of Markdown files whose family was localized and whose prose or inline spans name the categories."""
    try:
        with open(os.path.join(ROOT, CATEGORY_PROSE_FILES), encoding="utf-8") as fh:
            return {ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")}
    except OSError:
        return set()


def localize_category_words(text):
    """Outside fenced blocks, a whole English category word (in prose, a table cell or an inline code span) gets the mapped
    Spanish word. A word directly inside parentheses is a gloss of a Spanish term, e.g. 'Depuración (Debugging)', and stays,
    as do link targets."""
    out, fence, mermaid = [], None, False
    for line in text.split("\n"):
        s = line.lstrip()
        if fence is None and (s.startswith("```") or s.startswith("~~~")) and len(line) - len(s) <= 3:
            fence = s[:3]
            mermaid = s[3:].strip().lower().startswith("mermaid")
        elif fence is not None and s.startswith(fence):
            fence = None
            mermaid = False
        elif fence is not None and mermaid and (s.startswith("accDescr:") or s.startswith('state "')):
            # Mermaid display text only (an accDescr sentence or a state label); node IDs and syntax never match a whole word.
            line = _WORD_RE.sub(lambda m: categories.EN_TO_ES[m.group(1)], line)
        elif fence is None:
            # a bold-only word (| **Debugging** | ...) is a concept-table row label, not a card category: it stays
            parts = re.split(r"(\]\([^)]*\)|https?://\S+|\*\*(?:%s)\*\*)" % "|".join(categories.EN), line)
            for i in range(0, len(parts), 2):
                parts[i] = _WORD_RE.sub(lambda m: categories.EN_TO_ES[m.group(1)], parts[i])
            line = "".join(parts)
        out.append(line)
    return "\n".join(out)


CATEGORY_FILES = os.path.join("translation", "part2", "category-localized-md.txt")
ROW_RE = re.compile(r"^(%s)(?=\t)" % "|".join(categories.EN))
# the four words in order, space-separated, inside a quoted string (a copied split("Meetings Coding Debugging Learning", ...))
LIST_RE = re.compile(r'(?<=")%s(?=")' % " ".join(categories.EN))


# the four words in order, each double-quoted, space-separated (a copied Lisp list literal)
QUOTED_LIST_RE = re.compile(" ".join('"%s"' % w for w in categories.EN))


def category_files():
    """Markdown files whose family prints the Spanish card categories (decision 11): one path per line."""
    try:
        with open(os.path.join(ROOT, CATEGORY_FILES), encoding="utf-8") as fh:
            return {ln.strip() for ln in fh if ln.strip() and not ln.startswith("#")}
    except OSError:
        return set()


def localize_category_rows(text):
    """Inside fenced blocks only, a line that starts with an English category word and a TAB (a copied output row) gets the
    mapped Spanish word. Nothing else in a fence changes."""
    out, fence = [], None
    for line in text.split("\n"):
        s = line.lstrip()
        if fence is None and (s.startswith("```") or s.startswith("~~~")) and len(line) - len(s) <= 3:
            fence = s[:3]
        elif fence is not None and s.startswith(fence):
            fence = None
        elif fence is not None:
            line = ROW_RE.sub(lambda m: categories.EN_TO_ES[m.group(1)], line)
            line = LIST_RE.sub(lambda m: " ".join(categories.ES), line)
            line = QUOTED_LIST_RE.sub(lambda m: " ".join('"%s"' % w for w in categories.ES), line)
        out.append(line)
    return "\n".join(out)


def identity_check(text, rel_path=""):
    """T0 through the PO layer, for an identity PO and an empty PO. Returns problem strings."""
    problems = []
    try:
        seg = segment.Segmentation(text, rel_path)
    except segment.SegmentError as e:
        return ["segmenter refused: %s" % e]
    for identity in (True, False):
        label = "identity" if identity else "empty"
        po = new_po(seg, rel_path, identity)
        # round trip the PO through its serialized form, as a file on disk would be
        po = polib.pofile(po.__unicode__(), wrapwidth=0)
        try:
            out, _ = apply_text(text, po, rel_path)
        except ApplyError as e:
            problems.append("%s PO: %s" % (label, e))
            continue
        if out != text:
            problems.append("%s PO changed the file" % label)
    return problems


def source_text(rel, path):
    """The text a PO is built on and applied to: the pinned English text of the file with English key `rel` (segment ids are
    hashes of it; the working file of an untranslated page has its references remapped, so its ids would differ). A file
    that has no pinned English text (a scratch file in a test) is read as it is."""
    en = enpath.english_source(rel, ROOT)
    return en if en is not None else segment.read_raw(path)


def write_text(path, text):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(text)


def rel(path):
    """The English key of a file (PO files, ledger and anchors name files by their English path)."""
    return enpath.locate(path, ROOT)[0]


def identity_files(files, root=ROOT, layer=None):
    """T0 through the PO layer on each file, read at its working path. Returns (failures, lines): `files` are English
    keys or paths in either form; each failure is a line naming the English key."""
    layer = layer or enpath.load(root)
    bad = []
    for arg in files:
        p, full = enpath.locate(arg, root, layer)
        probs = identity_check(segment.read_raw(full), p)
        if probs:
            bad.append("FAIL %s: %s" % (p, "; ".join(probs)))
    return bad


def expected_text(rel, path, cat=None, root=ROOT):
    """What the working file with English key `rel` must contain: its PO applied to the English text (the English text when
    there is no PO), through anchors.layout_text. The same text verify.py compares the file with."""
    text = source_text(rel, path)
    po_path = po_path_for(rel)
    if os.path.isfile(po_path):
        text, _ = apply_text(text, load_po(po_path), rel, cat or catalog.load(DEFAULT_LANG), strict=False)
    return anchors.layout_text(text, rel, None, root)


def relink(files, write=False, root=ROOT):
    """Bring the link fragments of `files` (English keys or paths; every authored file by default) in line with
    translation/anchors.json. Returns the English keys of the files that differ from their expected text."""
    layer = enpath.load(root)
    cat = catalog.load(DEFAULT_LANG)
    changed = []
    for arg in files or segment.authored_files(root):
        rel_key, full = enpath.locate(arg, root, layer)
        if not rel_key.endswith(".md") or not os.path.isfile(full):
            continue
        want = expected_text(rel_key, full, cat, root)
        if segment.read_raw(full) != want:
            changed.append(rel_key)
            if write:
                write_text(full, want)
    return changed


def main(argv):
    args = argv[1:]
    if "--relink" in args:
        rest = [a for a in args if a not in ("--relink", "--write")]
        try:
            changed = relink(rest, write="--write" in args)
        except (ApplyError, catalog.CatalogError, OSError) as e:
            print("FAIL %s" % e)
            return 1
        for rel_key in changed:
            print("%s %s" % ("relinked" if "--write" in args else "would change", rel_key))
        print("relink: %d file(s) %s" % (len(changed), "written" if "--write" in args else "differ"))
        return 0
    if not args:
        print(__doc__.split("Usage:")[1].rstrip())
        return 2

    def opt(name):
        if name in args:
            i = args.index(name)
            val = args[i + 1] if i + 1 < len(args) else None
            if val is None:
                raise SystemExit("%s needs a value" % name)
            del args[i:i + 2]
            return val
        return None

    flag_identity = "--identity" in args
    flag_init = "--init" in args
    flag_lenient = "--lenient" in args
    flag_write = "--write" in args
    args = [a for a in args if a not in ("--identity", "--init", "--lenient", "--write")]
    po_arg, out_arg, lang = opt("--po"), opt("--out"), opt("--lang") or DEFAULT_LANG

    if flag_identity and not flag_init:
        files = args or segment.authored_files()
        failing = identity_files(files)
        for line in failing:
            print(line)
        bad = len(failing)
        print("apply identity %s: %d file(s), %d failing" % ("FAILED" if bad else "OK", len(files), bad))
        return 1 if bad else 0

    if len(args) != 1:
        print("expected exactly one FILE.md; see usage")
        return 2
    rp, src = enpath.locate(args[0], ROOT)
    text = source_text(rp, src)
    if flag_init:
        target = po_arg or po_path_for(rp)
        if os.path.exists(target):
            print("refusing to overwrite %s" % target)
            return 1
        try:
            seg = segment.Segmentation(text, rp)
        except segment.SegmentError as e:
            print("FAIL %s" % e)
            return 1
        os.makedirs(os.path.dirname(target), exist_ok=True)
        new_po(seg, rp, flag_identity).save(target)
        print("wrote %s (%d entries)" % (target, len(seg.segments())))
        return 0

    try:
        po = load_po(po_arg or po_path_for(rp))
        out, st = apply_text(text, po, rp, catalog.load(lang), strict=not flag_lenient)
    except (ApplyError, catalog.CatalogError, OSError) as e:
        print("FAIL %s" % e)
        return 1
    out = anchors.layout_text(out, rp)          # renamed paths in the layout of the checkout, fragments of the translated headings
    if flag_write:
        write_text(src, out)
    elif out_arg and out_arg != "-":
        write_text(out_arg, out)
    elif out_arg == "-":
        sys.stdout.write(out)
    print("applied %(applied)d of %(segments)d segments (empty %(empty)d, fuzzy %(fuzzy)d, "
          "orphan %(orphan)d, stale %(stale)d)" % st, file=sys.stderr if out_arg == "-" else sys.stdout)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
