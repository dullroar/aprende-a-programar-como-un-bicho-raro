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

    def phase_letters(self):
        n = 1
        out = []
        while "phases.%d.letter" % n in self.flat:
            out.append(self.flat["phases.%d.letter" % n])
            n += 1
        return out


def path_for(lang, base=HERE):
    return os.path.join(base, lang + ".yaml")


def load(lang, base=HERE):
    path = path_for(lang, base)
    if not os.path.isfile(path):
        raise CatalogError("no catalog for language %r (%s)" % (lang, path))
    with open(path, encoding="utf-8") as f:
        data = yaml.safe_load(f)
    return Catalog(lang, flatten(data))


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
