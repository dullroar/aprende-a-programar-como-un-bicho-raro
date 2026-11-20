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
    def __init__(self, en_to_es=None, layout="english", root=ROOT):
        if layout not in LAYOUTS:
            raise PathLayerError("layout must be one of %s, not %r" % (LAYOUTS, layout))
        self.root = root
        self.layout = layout
        self.en_to_es = dict(en_to_es or {})
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
        _CACHE[key] = PathLayer(read_map(root), layout or read_layout(root), root)
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
