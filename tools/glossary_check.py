#!/usr/bin/env python3
"""Validate translation/glossary.es.yaml (P1-001).

Checks: the file parses; every term has id/en/es; ids are unique; `banned` is a list of plain strings;
no approved `es` rendering is banned for another term; the assurance labels and the frozen 40-rule
wording are present and consistent; no literal phase letters appear in phase entries.

Usage: python3 -I tools/glossary_check.py [path]     (exit 0 = OK, 1 = problems)
"""
import os
import sys

import yaml

DEFAULT_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "translation", "glossary.es.yaml")

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


def main(argv):
    path = argv[1] if len(argv) > 1 else DEFAULT_PATH
    try:
        data = load(path)
    except (OSError, yaml.YAMLError) as exc:
        print(f"glossary_check: cannot load {path}: {exc}")
        return 1
    problems = check(data)
    if problems:
        for p in problems:
            print("PROBLEM:", p)
        return 1
    print(f"glossary_check: OK ({len(data['terms'])} terms)")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
