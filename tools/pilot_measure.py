#!/usr/bin/env python3
"""Calibrate the Spanish sentence limit N from the pilot PO files (plan 6.2).

    python3 -I tools/pilot_measure.py                 # print the table
    python3 -I tools/pilot_measure.py --write         # also write translation/pilot-calibration.md

N = 25 x (Spanish words / English words) over the prose segments of the pilot. Only segments whose English has at least
MIN_WORDS words count: that leaves out headings, table cells, Mermaid labels and one-word list items, which would add noise
and no information about sentence length. Words are counted the way invariant I12 counts them (placeholders count as one word).

Exit code 0 when the measured N is a usable integer, 1 otherwise (no PO files, or no prose).
"""
import math
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "tools"))
import apply as apply_mod      # noqa: E402
import invariants              # noqa: E402

PILOT = [
    "src/forth/README.md",
    "lessons/cs-source/concepts/recursion.md",
    "lessons/study-guides/languages/forth.md",
    "docs/curriculum.md",
    "lessons/study-guides/languages/apl.md",
]
MIN_WORDS = 6
BASE = 25          # the English limit (house-style 6.2)
REPORT = os.path.join("translation", "pilot-calibration.md")


def words(text):
    return sum(invariants.word_count(s) for s in invariants.sentences(invariants.strip_ph_keep_words(text)))


def sentence_lengths(text):
    return [invariants.word_count(s) for s in invariants.sentences(invariants.strip_ph_keep_words(text))]


def measure(po_entries):
    """po_entries: iterable of (msgid, msgstr). Returns (english_words, spanish_words, spanish_sentence_lengths)."""
    en = es = 0
    lens = []
    for msgid, msgstr in po_entries:
        if not msgstr.strip() or msgstr == msgid:
            continue
        w = words(msgid)
        if w < MIN_WORDS:
            continue
        en += w
        es += words(msgstr)
        lens.extend(sentence_lengths(msgstr))
    return en, es, lens


def calibrated_n(en, es):
    if en <= 0:
        return None
    return int(math.floor(BASE * es / en + 0.5))


def percentile(sorted_vals, p):
    if not sorted_vals:
        return 0
    k = min(len(sorted_vals) - 1, int(math.ceil(p * len(sorted_vals))) - 1)
    return sorted_vals[max(k, 0)]


def load(rel, root=ROOT):
    path = apply_mod.po_path_for(rel, os.path.join(root, "translation", "po"))
    if not os.path.isfile(path):
        return None
    po = apply_mod.load_po(path)
    return [(e.msgid, e.msgstr) for e in po if e.msgctxt]


def main(argv):
    rows, all_en, all_es, all_lens = [], 0, 0, []
    for rel in PILOT:
        entries = load(rel)
        if entries is None:
            print("missing PO file for " + rel)
            continue
        en, es, lens = measure(entries)
        rows.append((rel, en, es, lens))
        all_en += en
        all_es += es
        all_lens += lens
    n = calibrated_n(all_en, all_es)
    if n is None:
        print("no pilot prose measured")
        return 1
    ordered = sorted(all_lens)
    lines = ["# Pilot calibration of the sentence limit N", "",
             "Measured by `tools/pilot_measure.py` from the PO files of the five pilot files. Prose segments only (English side of at least %d words)." % MIN_WORDS, "",
             "| File | English words | Spanish words | Ratio |", "| --- | ---: | ---: | ---: |"]
    for rel, en, es, _ in rows:
        lines.append("| `%s` | %d | %d | %.3f |" % (rel, en, es, es / en if en else 0))
    ratio = all_es / all_en
    lines += ["| **Total** | **%d** | **%d** | **%.3f** |" % (all_en, all_es, ratio), "",
              "N = %d x %.3f = %.1f, rounded to **%d**." % (BASE, ratio, BASE * ratio, n), "",
              "Spanish sentences measured: %d. Longest %d words, 95th percentile %d, median %d. Sentences above the measured N: %d; above 28: %d."
              % (len(ordered), ordered[-1] if ordered else 0, percentile(ordered, 0.95), percentile(ordered, 0.5),
                 sum(1 for x in ordered if x > n), sum(1 for x in ordered if x > 28)), ""]
    text = "\n".join(lines)
    print(text)
    if "--write" in argv:
        with open(os.path.join(ROOT, REPORT), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        print("wrote " + REPORT)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
