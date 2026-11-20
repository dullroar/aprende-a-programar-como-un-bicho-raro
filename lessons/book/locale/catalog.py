#!/usr/bin/env python3
"""Locale catalog loader (plan 5.4): data-only catalog plus its English mirror.

Usage in tooling (do not name a package `locale`; it would shadow the stdlib module):

    sys.path.insert(0, os.path.join(HERE, "locale"))
    import catalog
    cat = catalog.load("es")            # or "en"
    cat.get("diagrams.section")         # raises MissingKeyError if absent
    cat.text("acronym.gloss")           # value with {{macros}} expanded

CLI:  python3 -I lessons/book/locale/catalog.py --check [lang ...]
Exit 0 = every key of en.yaml exists in each language file and vice versa, 1 = problems.

Keys are dotted paths. Lists are addressed by 1-based position, so the phase list is
`phases.1.letter` and the macro `{{phase.1.letter}}` is an alias for it. Supported macros:
{{acronym.word}}, {{phase.N.letter}}, {{phase.N.name}}. Any other macro is an error.
There is no fallback to English: a missing key fails loudly, never silently.
"""
import os
import re
import sys

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
MIRROR_LANG = "en"
MACRO = re.compile(r"\{\{([A-Za-z0-9_.]+)\}\}")
FIELD = re.compile(r"(?<!\{)\{([A-Za-z_][A-Za-z0-9_]*)\}(?!\})")  # str.format style {n}


class CatalogError(Exception):
    pass


class MissingKeyError(CatalogError, KeyError):
    def __str__(self):
        return "locale key missing: %s" % self.args[0]


def flatten(data, prefix=""):
    """Flatten nested mappings and lists into {dotted.key: leaf}. Lists are 1-based."""
    out = {}
    if isinstance(data, dict):
        items = [(str(k), v) for k, v in data.items()]
    elif isinstance(data, list):
        items = [(str(i), v) for i, v in enumerate(data, 1)]
    else:
        raise CatalogError("catalog root must be a mapping")
    for k, v in items:
        key = prefix + k
        if isinstance(v, (dict, list)):
            out.update(flatten(v, key + "."))
        else:
            if key in out:
                raise CatalogError("duplicate key %s" % key)
            out[key] = v
    return out


def macro_key(name):
    """Map a macro name to a catalog key, or None if the macro is not supported."""
    parts = name.split(".")
    if parts == ["acronym", "word"]:
        return "acronym.word"
    if len(parts) == 3 and parts[0] == "phase" and parts[1].isdigit() and parts[2] in ("letter", "name"):
        return "phases.%s.%s" % (parts[1], parts[2])
    return None


class Catalog:
    def __init__(self, lang, flat):
        self.lang = lang
        self.flat = flat

    def keys(self):
        return set(self.flat)

    def get(self, key):
        try:
            return self.flat[key]
        except KeyError:
            raise MissingKeyError(key) from None

    def require(self, keys):
        """Raise one MissingKeyError listing every absent key."""
        missing = [k for k in keys if k not in self.flat]
        if missing:
            raise MissingKeyError(", ".join(missing))

    def expand(self, text):
        """Expand macros in `text` in one non-recursive pass; unknown or unresolved macros raise."""
        def sub(m):
            key = macro_key(m.group(1))
            if key is None:
                raise CatalogError("unknown macro {{%s}}" % m.group(1))
            val = self.get(key)
            if not isinstance(val, str) or MACRO.search(val):
                raise CatalogError("macro target %s must be plain text" % key)
            return val
        return MACRO.sub(sub, text)

    def text(self, key):
        val = self.get(key)
        if not isinstance(val, str):
            raise CatalogError("key %s is not text" % key)
        return self.expand(val)

    # ---- file and folder names (plan 5.6): the English path is the key, the catalog gives the path in this edition
    def _paths(self):
        cached = self.__dict__.get("_path_tables")
        if cached is None:
            pick = lambda pre: {k[len(pre):]: v for k, v in self.flat.items() if k.startswith(pre)}
            layout = self.flat.get("paths.layout")
            if layout not in ("english", "spanish"):
                raise CatalogError("paths.layout must be english or spanish, not %r" % (layout,))
            files, dirs = pick("paths.files."), pick("paths.dirs.")
            cached = self._path_tables = (layout == "spanish", files, dirs,
                                          {v: k for k, v in files.items()}, {v: k for k, v in dirs.items()})
        return cached

    def path(self, rel):
        """The path, in this edition, of the English repository-relative path `rel` (a file or a folder, '/' separated).
        Identity while paths.layout is english, and for every path the map does not rename."""
        moved, files, dirs, _, _ = self._paths()
        if not moved:
            return rel
        if rel in files:
            return files[rel]
        return _swap_prefix(rel, dirs)

    def english(self, rel):
        """The reverse of `path`: the English path of a path of this edition."""
        moved, _, _, files, dirs = self._paths()
        if not moved:
            return rel
        if rel in files:
            return files[rel]
        return _swap_prefix(rel, dirs)

    def english_text(self, text):
        """`text` with every file and folder name of this edition written back as the English one, both as a repository path
        (lessons/guias-de-estudio/...) and as a path relative to lessons/. For the scratch copies that tests lay out in the
        English names. Identity while paths.layout is english."""
        moved, files, dirs, _, _ = self._paths()
        if not moved:
            return text
        pairs = []
        for table, tail in ((files, ""), (dirs, "/")):
            for en, es in table.items():
                if en != es:
                    pairs.append((es + tail, en + tail))
                    if en.startswith("lessons/") and es.startswith("lessons/"):
                        pairs.append((es[len("lessons/"):] + tail, en[len("lessons/"):] + tail))
                    if es.rsplit("/", 1)[-1] != en.rsplit("/", 1)[-1]:      # a sibling link names the file (or the folder) alone
                        pairs.append((es.rsplit("/", 1)[-1] + tail, en.rsplit("/", 1)[-1] + tail))
        for es, en in sorted(pairs, key=lambda p: -len(p[0])):
            text = text.replace(es, en)
        return text

    def lessons_path(self, rel):
        """`path` for a path given relative to lessons/ (the form the book tools use); the result is relative to lessons/ too."""
        out = self.path("lessons/" + rel)
        if not out.startswith("lessons/"):
            raise CatalogError("%s moves out of lessons/" % rel)
        return out[len("lessons/"):]

    def lessons_english(self, rel):
        out = self.english("lessons/" + rel)
        return out[len("lessons/"):] if out.startswith("lessons/") else out

    def phase_letters(self):
        n = 1
        out = []
        while "phases.%d.letter" % n in self.flat:
            out.append(self.flat["phases.%d.letter" % n])
            n += 1
        return out


def _swap_prefix(rel, table):
    """Replace the longest folder prefix of `rel` that `table` names."""
    parts = rel.split("/")
    for i in range(len(parts), 0, -1):
        head = "/".join(parts[:i])
        if head in table:
            return "/".join([table[head]] + parts[i:])
    return rel


def path_for(lang, base=HERE):
    return os.path.join(base, lang + ".yaml")


# Tests only: "english" or "spanish" replaces paths.layout of every catalog `load` returns. The English layer of
# tools/scratch_proof.py sets BOOK_LAYOUT=english: it carries es.yaml but keeps the English file names.
LAYOUT_OVERRIDE = os.environ.get("BOOK_LAYOUT") or None


def _read(lang, base):
    path = path_for(lang, base)
    if not os.path.isfile(path):
        raise CatalogError("no catalog for language %r (%s)" % (lang, path))
    with open(path, encoding="utf-8") as f:
        return flatten(yaml.safe_load(f))


def load(lang, base=HERE, layout=None):
    flat = _read(lang, base)
    layout = layout or LAYOUT_OVERRIDE
    if layout:
        flat["paths.layout"] = layout
    return Catalog(lang, flat)


def checkout(base=HERE):
    """The catalog that names the files of THIS checkout: es.yaml owns `paths.layout`, the same switch tools/enpath.py reads.
    Identity in the English repository. Tests use it to find the real files whatever language they run in, and to
    lay a scratch copy out in the English or the Spanish names (checkout().english(p) / .path(p)).
    The layout is the one the files are really in: the English clone with the locale layer applied (tools/scratch_proof.py)
    carries es.yaml but keeps the English names, so a probe file decides, not the flag alone."""
    flat = _read("es", base)
    cat = Catalog("es", flat)
    root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(base))))
    probe = "lessons/intro.md"
    spanish = cat.path(probe)
    if spanish != probe and not os.path.isfile(os.path.join(root, *spanish.split("/"))) \
            and os.path.isfile(os.path.join(root, *probe.split("/"))):
        return Catalog("es", dict(flat, **{"paths.layout": "english"}))
    return cat


def problems(cat, mirror):
    """Compare a catalog with the English mirror. Returns a list of problem strings."""
    errs = []
    for k in sorted(mirror.keys() - cat.keys()):
        errs.append("%s: missing key %s (present in %s)" % (cat.lang, k, mirror.lang))
    for k in sorted(cat.keys() - mirror.keys()):
        errs.append("%s: key %s has no %s mirror" % (cat.lang, k, mirror.lang))
    for k in sorted(cat.keys() & mirror.keys()):
        v, e = cat.flat[k], mirror.flat[k]
        if isinstance(e, int) and not isinstance(e, bool):
            # structural index such as phases.N.n: must be the same integer in both files
            if v != e or isinstance(v, bool):
                errs.append("%s: %s must be the integer %r like %s" % (cat.lang, k, e, mirror.lang))
            continue
        if not isinstance(e, str):
            errs.append("%s: %s must be text or an integer in the mirror" % (mirror.lang, k))
            continue
        if not isinstance(v, str) or not v.strip():
            errs.append("%s: %s must be non-empty text" % (cat.lang, k))
            continue
        if sorted(FIELD.findall(v)) != sorted(FIELD.findall(e)):
            errs.append("%s: %s format fields %r differ from %s %r"
                        % (cat.lang, k, FIELD.findall(v), mirror.lang, FIELD.findall(e)))
        for m in MACRO.findall(v):
            key = macro_key(m)
            if key is None:
                errs.append("%s: %s uses unsupported macro {{%s}}" % (cat.lang, k, m))
            elif key not in cat.flat:
                errs.append("%s: %s uses macro {{%s}} with no catalog value" % (cat.lang, k, m))
    return errs


def check(langs, base=HERE):
    mirror = load(MIRROR_LANG, base)
    errs = []
    if "acronym.word" in mirror.flat and mirror.flat["acronym.word"] != "".join(mirror.phase_letters()):
        errs.append("%s: acronym.word is not the phase letters in order" % MIRROR_LANG)
    for lang in langs:
        cat = load(lang, base)
        errs.extend(problems(cat, mirror))
    return errs


def main(argv):
    args = [a for a in argv[1:] if a != "--check"]
    langs = args or ["es"]
    try:
        errs = check(langs)
    except CatalogError as e:
        errs = [str(e)]
    for e in errs:
        print("FAIL " + e)
    if not errs:
        print("OK catalog %s mirrors %s" % (", ".join(langs), MIRROR_LANG))
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
