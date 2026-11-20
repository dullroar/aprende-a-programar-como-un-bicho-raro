#!/usr/bin/env python3
"""enpath: the English path is the key, the working tree holds the Spanish path (plan 5.6, P3B-004).

Every record our own tools keep (PO files under translation/po/, the ledger, locked-code.sha256, anchors.json, the
inventory, packets) names a file by its ENGLISH path. Until P3B-005 the working tree uses the same names; afterwards the
files of translation/path-map.yaml sit at their Spanish names. This module is the one place that converts:

  layer.english(p)   the English key of a path given in either form (identity for a path the map does not name)
  layer.work(en)     where the file lives in this checkout (English key while paths.layout is "english", else Spanish)
  layer.spanish(en)  the Spanish name of an English key, whatever the layout
  layer.full(en)     os.path.join(root, work(en))

The layout switch is the same one the build tooling reads: `paths.layout` in lessons/book/locale/es.yaml. A root with no
path map (a scratch repository in a test) gets the identity layer, so tools that call this module keep working there.

Usage:  python3 -I tools/enpath.py PATH...     print english -> work for each path (debugging aid)
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
MAP_REL = "translation/path-map.yaml"
CATALOG_REL = "lessons/book/locale/es.yaml"
LAYOUTS = ("english", "spanish")


class PathLayerError(ValueError):
    pass


def norm(p):
    """A repository-relative path with '/' separators and no leading './'."""
    p = p.replace(os.sep, "/")
    while p.startswith("./"):
        p = p[2:]
    return p


class PathLayer:
    def __init__(self, en_to_es=None, layout="english", root=ROOT, dirs=None):
        if layout not in LAYOUTS:
            raise PathLayerError("layout must be one of %s, not %r" % (LAYOUTS, layout))
        self.root = root
        self.layout = layout
        self.en_to_es = dict(en_to_es or {})
        self.dirs = dict(dirs or {})
        self.es_to_en = {}
        for en, es in self.en_to_es.items():
            if es in self.es_to_en and self.es_to_en[es] != en:
                raise PathLayerError("two English paths map to %s: %s and %s" % (es, self.es_to_en[es], en))
            self.es_to_en[es] = en

    @property
    def moved(self):
        return self.layout == "spanish"

    def english(self, p):
        p = norm(p)
        if p in self.en_to_es:
            return p
        return self.es_to_en.get(p, p)

    def spanish(self, en):
        en = self.english(en)
        return self.en_to_es.get(en, en)

    def work(self, en):
        return self.spanish(en) if self.moved else self.english(en)

    def full(self, en):
        return os.path.join(self.root, *self.work(en).split("/"))

    def english_of_abs(self, path):
        """The English key of a file given by an absolute or cwd-relative path inside this root."""
        return self.english(os.path.relpath(os.path.abspath(path), self.root))

    def renamed(self):
        return {en: es for en, es in self.en_to_es.items() if en != es}


# ---------------------------------------------------------------------------------------- reference remapping
# The pinned English text names other files in the English layout. In a Spanish-layout checkout every reference to a
# renamed file or folder (Markdown link destinations, `lesson:` front matter, full repo-relative paths in prose and code
# spans) must name the Spanish path. remap_text() is that one deterministic function: tools apply it to the English text
# (or to the PO applied to it) and compare or write the result. It is never run on a file that is already remapped.

_LINK = re.compile(r'(\]\(\s*<?)([^)\s>]+)|(^\[[^\]]+\]:\s*)(\S+)|((?:href|src)=")([^"]+)', re.M)
_LESSON = re.compile(r'^(lesson:\s*")([^"]+)(")', re.M)
_SCHEME = re.compile(r"^[A-Za-z][A-Za-z0-9+.-]*:")
CS_SOURCE_PAGES = ("lessons/cs-source/chapters/", "lessons/cs-source/concepts/", "lessons/cs-source/roles/")
CS_SOURCE_INDEX = "lessons/cs-source/index.md"
CS_PAGE_DIR = "lessons/cs"          # cs-source bodies are written for pages that the generator puts here


def read_dirs(root=ROOT):
    """paths.dirs of the Spanish catalog: renamed folder -> Spanish folder (English key first)."""
    path = os.path.join(root, *CATALOG_REL.split("/"))
    if not os.path.isfile(path):
        return {}
    with open(path, encoding="utf-8") as fh:
        text = fh.read()
    m = re.search(r"^  dirs:\n((?:    \"[^\"]+\": \"[^\"]+\"\n)+)", text, re.M)
    if not m:
        return {}
    return dict(re.findall(r'"([^"]+)": "([^"]+)"', m.group(1)))


def map_path(layer, p):
    """The Spanish form of any repository path, file or folder (exact file, else the longest renamed folder prefix)."""
    p = norm(p)
    if p in layer.en_to_es:
        return layer.en_to_es[p]
    best = None
    for d in layer.dirs:
        if (p == d or p.startswith(d + "/")) and (best is None or len(d) > len(best)):
            best = d
    return layer.dirs[best] + p[len(best):] if best else p


def _virtual_dirs(layer, en_key):
    """(English directory, Spanish directory) that relative links in this file are written against."""
    if en_key.startswith(CS_SOURCE_PAGES) or en_key == CS_SOURCE_INDEX:
        return CS_PAGE_DIR, map_path(layer, CS_PAGE_DIR)
    en_dir = posixpath_dirname(en_key)
    return en_dir, posixpath_dirname(layer.spanish(en_key))


def posixpath_dirname(p):
    return p.rsplit("/", 1)[0] if "/" in p else ""


def _fix_dest(layer, en_key, dest):
    import posixpath
    if _SCHEME.match(dest) or dest.startswith(("#", "/")):
        return dest
    base, sep, frag = dest.partition("#")
    if not base:
        return dest
    en_dir, es_dir = _virtual_dirs(layer, en_key)
    target = posixpath.normpath(posixpath.join(en_dir, base))
    new_base = posixpath.relpath(map_path(layer, target), es_dir or ".")
    if base.endswith("/") and not new_base.endswith("/"):
        new_base += "/"
    return (new_base if new_base != base else base) + sep + frag


def _full_regex(layer):
    keys = sorted({k for k, v in layer.en_to_es.items() if k != v} | set(layer.dirs), key=len, reverse=True)
    return re.compile(r"(?<![\w./-])(" + "|".join(re.escape(k) for k in keys) + r")(?![\w-]|\.\w)") if keys else None


def remap_text(text, en_key, layer=None, root=ROOT):
    """`text` (English layout) with every reference to a renamed path written in the Spanish layout. Identity when the
    layer is not moved or the map renames nothing."""
    layer = layer or load(root)
    if not layer.moved or not layer.renamed():
        return text
    en_key = layer.english(en_key)
    new = text
    if en_key.endswith(".md"):
        def sub(m):
            if m.group(2) is not None:
                return m.group(1) + _fix_dest(layer, en_key, m.group(2))
            if m.group(4) is not None:
                return m.group(3) + _fix_dest(layer, en_key, m.group(4))
            return m.group(5) + _fix_dest(layer, en_key, m.group(6))
        new = _LINK.sub(sub, new)

        def lesson(m):
            base, sep, frag = m.group(2).partition("#")
            full = map_path(layer, "lessons/" + base)
            return m.group(1) + (full[len("lessons/"):] if full.startswith("lessons/") else base) + sep + frag + m.group(3)
        new = _LESSON.sub(lesson, new)
    rx = _full_regex(layer)
    if rx:
        new = rx.sub(lambda m: map_path(layer, m.group(1)), new)
    return new


def english_source(rel, root=ROOT):
    """The pinned English text of the file with English key `rel` (None when the clone or file is missing). Tools that
    segment a file read this, never the working file: the working file of an untranslated page is the English text
    with its references already remapped, and segment ids are hashes of the English text."""
    import subprocess
    import inventory
    cfg = inventory.read_config(root)
    clone, sha = cfg.get("english_clone_path"), cfg.get("english_commit")
    if not clone or not sha or not os.path.isdir(clone):
        return None
    r = subprocess.run(["git", "-C", clone, "show", "%s:%s" % (sha, rel)], capture_output=True)
    return r.stdout.decode("utf-8") if r.returncode == 0 else None


def locate(arg, root=ROOT, layer=None):
    """(english key, full path) for a command-line path: a path that exists (absolute or relative to the cwd) is taken
    as it is; any other is a repository-relative path in either form. A file outside `root` keeps its own name."""
    layer = layer or load(root)
    if os.path.isabs(arg) or os.path.exists(arg):
        full = os.path.abspath(arg)
        rel = os.path.relpath(full, root).replace(os.sep, "/")
        if rel == ".." or rel.startswith("../"):
            return norm(arg), full
        return layer.english(rel), full
    en = layer.english(arg)
    return en, layer.full(en)


def read_layout(root=ROOT):
    """paths.layout of the Spanish catalog under `root` ("english" when there is none)."""
    path = os.path.join(root, *CATALOG_REL.split("/"))
    if not os.path.isfile(path):
        return "english"
    with open(path, encoding="utf-8") as fh:
        m = re.search(r'^  layout:\s*"?(\w+)"?', fh.read(), re.M)
    return m.group(1) if m else "english"


def read_map(root=ROOT):
    path = os.path.join(root, *MAP_REL.split("/"))
    if not os.path.isfile(path):
        return {}
    import yaml
    with open(path, encoding="utf-8") as fh:
        data = yaml.safe_load(fh) or {}
    paths = data.get("paths", "missing")
    if paths is None:                      # `paths:` with no rows: an empty map (the layer is the identity)
        paths = {}
    if not isinstance(paths, dict):
        raise PathLayerError("%s has no paths: table" % path)
    return {str(k): str(v) for k, v in paths.items()}


_CACHE = {}


def load(root=ROOT, layout=None):
    """The layer of `root` (cached per root and layout). `layout` overrides the catalog switch (tests, proofs)."""
    key = (os.path.abspath(root), layout)
    if key not in _CACHE:
        _CACHE[key] = PathLayer(read_map(root), layout or read_layout(root), root, read_dirs(root))
    return _CACHE[key]


def main(argv):
    if len(argv) < 2:
        print(__doc__.split("Usage:")[1].rstrip())
        return 2
    layer = load()
    print("layout: %s" % layer.layout)
    for p in argv[1:]:
        en = layer.english(p)
        print("%s -> %s" % (en, layer.work(en)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
