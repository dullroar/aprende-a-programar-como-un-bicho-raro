"""Candidate search for the Spanish acronym that replaces WEIRD (plan section 2.4, step 1).

Takes a Spanish word list that YOU supply (no list ships with this repo and none was found
on the machine; the English-only /usr/share/dict lists are the wrong language), keeps the
words that have exactly five letters, all different, and prints them. A human then filters
the output for the "weird/playful" register and tries to fill letters 2 to 5.

Accent rule: letters are compared after dropping the accent (a, e, i, o, u and the
dieresis of u), so "áreas" counts as a, r, e, a, s and repeats the a. The n-tilde stays
its own letter, so "niños" has five different letters.

Usage:
  python3 tools/acronym_search.py WORDLIST [--starts-with LETTER] [--limit N] [--counts]
  python3 tools/acronym_search.py --check-word BICHO [--check-word TORCE]

  WORDLIST  UTF-8 text, one word per line (lines may carry extra columns after a space,
            tab or slash, as in hunspell .dic files; only the first field is read).
  --counts  also print how many candidates start with each letter (a rough N3 guide:
            you need five different letters that each have friendly words).
"""
import argparse
import sys
import unicodedata

LETTERS = set("abcdefghijklmnopqrstuvwxyzñ")


def base_letter(ch):
    """Lowercase one character and drop an accent; the n-tilde is kept as its own letter."""
    ch = ch.lower()
    if ch == "ñ":
        return ch
    decomposed = unicodedata.normalize("NFD", ch)
    return decomposed[0] if decomposed else ch


def fold(word):
    """Return the word as a lowercase string of plain letters, or None if it has any
    character that is not a Spanish letter (digits, hyphens, apostrophes, spaces)."""
    word = unicodedata.normalize("NFC", word.strip())
    out = []
    for ch in word:
        b = base_letter(ch)
        if b not in LETTERS:
            return None
        out.append(b)
    return "".join(out)


def is_candidate(word):
    """True if the word is exactly five letters, all different."""
    folded = fold(word)
    return folded is not None and len(folded) == 5 and len(set(folded)) == 5


def first_field(line):
    line = line.strip()
    for sep in ("/", "\t", " "):
        line = line.split(sep, 1)[0]
    return line


def candidates(lines):
    """Unique candidate words in first-seen order, folded to plain lowercase letters."""
    seen = set()
    out = []
    for line in lines:
        word = first_field(line)
        if not word or not is_candidate(word):
            continue
        folded = fold(word)
        if folded not in seen:
            seen.add(folded)
            out.append(folded)
    return out


def letter_counts(words):
    counts = {}
    for w in words:
        counts[w[0]] = counts.get(w[0], 0) + 1
    return dict(sorted(counts.items()))


def check_word(word):
    """Explain why a word does or does not pass the five-letters-all-different test."""
    folded = fold(word)
    if folded is None:
        return False, "contains a character that is not a letter"
    if len(folded) != 5:
        return False, "has %d letters, not 5" % len(folded)
    repeated = sorted({c for c in folded if folded.count(c) > 1})
    if repeated:
        return False, "repeats the letter(s) " + ", ".join(repeated)
    return True, "five different letters"


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("wordlist", nargs="?")
    ap.add_argument("--starts-with", metavar="LETTER")
    ap.add_argument("--limit", type=int, default=0)
    ap.add_argument("--counts", action="store_true")
    ap.add_argument("--check-word", action="append", default=[])
    args = ap.parse_args(argv)

    if args.check_word:
        bad = 0
        for w in args.check_word:
            ok, why = check_word(w)
            print("%s: %s (%s)" % (w, "ok" if ok else "FAIL", why))
            bad += 0 if ok else 1
        return 1 if bad else 0

    if not args.wordlist:
        ap.error("give a WORDLIST file or --check-word")
    try:
        with open(args.wordlist, encoding="utf-8") as f:
            words = candidates(f)
    except (OSError, UnicodeDecodeError) as e:
        print("cannot read %s: %s" % (args.wordlist, e), file=sys.stderr)
        return 2
    if args.starts_with:
        start = fold(args.starts_with)
        words = [w for w in words if start and w.startswith(start)]
    if args.counts:
        for letter, n in letter_counts(words).items():
            print("%s %d" % (letter, n))
    shown = words[:args.limit] if args.limit > 0 else words
    for w in shown:
        print(w)
    print("%d candidate(s)" % len(words), file=sys.stderr)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
