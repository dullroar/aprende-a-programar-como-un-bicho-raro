#!/usr/bin/env python3
"""Validate translation/glossary.es.yaml (P1-001).

Checks: the file parses; every term has id/en/es; ids are unique; `banned` is a list of plain strings;
no approved `es` rendering is banned for another term; the assurance labels and the frozen 40-rule
wording are present and consistent; no literal phase letters appear in phase entries.

Path names (P3B-002): every word of a Spanish file or folder name in translation/path-names.es.yaml must be a
word of a `terms` entry, of `path_words`, a function word or a proper name; a glossary-banned word fails.

Usage: python3 -I tools/glossary_check.py [glossary [path-names]]     (exit 0 = OK, 1 = problems)
"""
import os
import re
import sys
import unicodedata

import yaml

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "translation", "glossary.es.yaml")
PATH_NAMES = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "translation", "path-names.es.yaml")

REQUIRED_LABELS = {
    "guaranteed": "garantizado",
    "implementation-permitted": "permitido por la implementación",
    "accidentally-exploited": "aprovechado por accidente",
}
REQUIRED_CATEGORIES = ["Meetings", "Coding", "Debugging", "Learning"]
FROZEN_STOP = "pasa de 40"
FROZEN_EXACT = "un total de exactamente 40 continúa"


def load(path):
    with open(path, encoding="utf-8") as fh:
        return yaml.safe_load(fh)


def check(data):
    """Return a list of problem strings (empty = OK)."""
    problems = []
    if not isinstance(data, dict):
        return ["glossary is not a mapping"]

    terms = data.get("terms")
    if not isinstance(terms, list) or not terms:
        problems.append("terms: missing or empty")
        terms = []

    seen = {}
    es_of = {}
    for i, t in enumerate(terms):
        if not isinstance(t, dict):
            problems.append(f"terms[{i}]: not a mapping")
            continue
        tid = t.get("id")
        for key in ("id", "en", "es"):
            if not isinstance(t.get(key), str) or not t.get(key).strip():
                problems.append(f"terms[{i}] ({tid}): missing or empty '{key}'")
        if tid in seen:
            problems.append(f"terms[{i}]: duplicate id '{tid}'")
        seen[tid] = i
        banned = t.get("banned", [])
        if not isinstance(banned, list) or not all(isinstance(b, str) and b for b in banned):
            problems.append(f"{tid}: 'banned' must be a list of non-empty strings")
        elif isinstance(t.get("es"), str) and t["es"] in banned:
            problems.append(f"{tid}: approved term '{t['es']}' is also banned")
        if isinstance(t.get("es"), str):
            es_of.setdefault(t["es"], []).append(tid)

    # A banned rendering must not be the approved rendering of a different concept.
    for t in terms:
        if not isinstance(t, dict) or not isinstance(t.get("banned"), list):
            continue
        for b in t["banned"]:
            if isinstance(b, str) and b in es_of and t.get("id") not in es_of[b]:
                problems.append(f"{t.get('id')}: banned '{b}' is the approved term of {es_of[b]}")

    frozen = data.get("frozen")
    if not isinstance(frozen, dict):
        problems.append("frozen: missing")
        return problems

    rule = frozen.get("timecard_rule", {})
    if rule.get("stop_phrase") != FROZEN_STOP:
        problems.append(f"frozen.timecard_rule.stop_phrase must be '{FROZEN_STOP}'")
    if rule.get("exact_forty_phrase") != FROZEN_EXACT:
        problems.append(f"frozen.timecard_rule.exact_forty_phrase must be '{FROZEN_EXACT}'")
    es_text = " ".join(str(rule.get("es", "")).split())
    if FROZEN_STOP not in es_text:
        problems.append("frozen.timecard_rule.es does not contain the stop phrase")
    if FROZEN_EXACT.capitalize() not in es_text and FROZEN_EXACT not in es_text:
        problems.append("frozen.timecard_rule.es does not contain the exactly-40 phrase")
    for banned in rule.get("banned", []):
        if banned in es_text:
            problems.append(f"frozen.timecard_rule.es contains banned phrase '{banned}'")
    for cat in REQUIRED_CATEGORIES:
        if f"`{cat}`" not in es_text:
            problems.append(f"frozen.timecard_rule.es: category `{cat}` must appear in code font")

    labels = {l.get("enum"): l for l in frozen.get("assurance_labels", {}).get("labels", []) if isinstance(l, dict)}
    for enum, es in REQUIRED_LABELS.items():
        if enum not in labels:
            problems.append(f"frozen.assurance_labels: missing enum '{enum}'")
        elif labels[enum].get("es") != es:
            problems.append(f"frozen.assurance_labels: '{enum}' must render as '{es}'")
    cats = frozen.get("card_categories", {}).get("values")
    if cats != REQUIRED_CATEGORIES:
        problems.append(f"frozen.card_categories.values must be {REQUIRED_CATEGORIES}")

    phases = data.get("phases")
    if not isinstance(phases, list) or [p.get("n") for p in phases if isinstance(p, dict)] != [1, 2, 3, 4, 5]:
        problems.append("phases: must list phases 1 to 5 in order")
    else:
        for p in phases:
            for key in ("macro_letter", "macro_name"):
                v = str(p.get(key, ""))
                if not (v.startswith("{{phase.") and v.endswith("}}")):
                    problems.append(f"phases[{p['n']}].{key}: must be a {{{{phase.N.*}}}} macro, got '{v}'")
    return problems


def fold(word):
    """Lowercase and strip accents and n-tilde marks: the form a path name is written in."""
    return "".join(c for c in unicodedata.normalize("NFD", word.lower()) if unicodedata.category(c) != "Mn")


def _words(text):
    return [fold(w) for w in re.findall(r"[^\W\d_]+", str(text))]


def _forms(word):
    return {word, word + "s", word + "es", word[:-1] if word.endswith("s") else word}


def path_name_words(names):
    """Content tokens of every Spanish folder and file name in a path-names mapping (extension dropped)."""
    out = {}
    values = list((names.get("dirs") or {}).values()) + list((names.get("files") or {}).values())
    for v in values:
        stem = str(v).rsplit(".", 1)[0] if "." in str(v) else str(v)
        for w in _words(stem):
            out.setdefault(w, v)
    return out


def check_path_words(data, names):
    """Every word of a Spanish path name must come from the glossary (plan 5.6), and none may be a banned word."""
    problems = []
    known = set()
    for t in data.get("terms", []) or []:
        for w in _words(t.get("es", "")):
            known |= _forms(w)
    path_words = data.get("path_words")
    if not isinstance(path_words, list):
        return ["path_words: missing"]
    for i, pw in enumerate(path_words):
        if not isinstance(pw, dict) or not str(pw.get("en", "")).strip() or not str(pw.get("es", "")).strip():
            problems.append(f"path_words[{i}]: needs non-empty 'en' and 'es'")
            continue
        for w in _words(pw["es"]):
            known |= _forms(w)
    allowed = set()
    for key in ("path_function_words", "path_proper_names"):
        vals = data.get(key)
        if not isinstance(vals, list) or not vals:
            problems.append(f"{key}: missing or empty")
            continue
        allowed |= {fold(v) for v in vals}
    banned = {}
    for t in data.get("terms", []) or []:
        for b in t.get("banned") or []:
            if isinstance(b, str) and len(_words(b)) == 1 and fold(b) not in known:
                banned.setdefault(fold(b), t.get("id"))
    for word, name in sorted(path_name_words(names).items()):
        if word in banned:
            problems.append(f"path word '{word}' in '{name}' is banned by glossary term '{banned[word]}'")
        elif not (_forms(word) & (known | allowed)):
            problems.append(f"path word '{word}' in '{name}' has no glossary entry (terms or path_words)")
    return problems


def main(argv):
    path = argv[1] if len(argv) > 1 else DEFAULT_PATH
    try:
        data = load(path)
    except (OSError, yaml.YAMLError) as exc:
        print(f"glossary_check: cannot load {path}: {exc}")
        return 1
    problems = check(data)
    names_path = argv[2] if len(argv) > 2 else PATH_NAMES
    if os.path.exists(names_path):
        try:
            names = load(names_path)
        except (OSError, yaml.YAMLError) as exc:
            print(f"glossary_check: cannot load {names_path}: {exc}")
            return 1
        problems += check_path_words(data, names)
    if problems:
        for p in problems:
            print("PROBLEM:", p)
        return 1
    print(f"glossary_check: OK ({len(data['terms'])} terms)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
