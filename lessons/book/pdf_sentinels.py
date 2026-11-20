"""Expected selectable snippets from the two publications' current sources.

Each check is restricted to a distinctive snippet on one page, anywhere in the
document. Diagram labels may lose spaces at SVG tspan boundaries during extraction.

The words of the diagram labels come from the locale catalog (block sentinels, language BOOK_LANG, default "en");
`set_language` switches them. Code sentinels (APL, Forth, sed, Make) are the same in every language.
PROFILES is one dict that is updated in place, so a module that imported it sees the new language.
"""
from dataclasses import dataclass
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "locale"))   # never name a package `locale`: it would shadow the stdlib module
import catalog


@dataclass(frozen=True)
class Sentinel:
    name: str
    expected: str
    pattern: str = ""

    def matches(self, page_text):
        return bool(re.search(self.pattern, page_text)) if self.pattern else self.expected in page_text


WORD_KEYS = ["sentinels.apl_diagram", "sentinels.ascii_diagram", "sentinels.forth_diagram",
             "sentinels.awk_diagram", "sentinels.apl_book", "sentinels.apl_guide"]


def tolerant(text):
    """A pattern for `text` that also accepts the space after ≤ or ≥ lost at a tspan boundary (and no other lost space)."""
    return "".join(re.escape(part) + (" ?" if part in ("≤", "≥") else "")
                   for part in re.split(r"([≤≥]) ?", text) if part)


def label(name, text):
    """A diagram label sentinel; the pattern is only set when the label has a comparison sign followed by a space."""
    pattern = tolerant(text)
    return Sentinel(name, text, pattern if re.search(r"[≤≥] ", text) else "")


def profiles(lang):
    cat = catalog.load(lang)
    cat.require(WORD_KEYS)
    word = {key.split(".", 1)[1]: cat.text(key) for key in WORD_KEYS}
    apl_diagram = label("Mermaid apl-weird ≤", word["apl_diagram"])
    ascii_diagram = Sentinel("Mermaid forth-weird <=", word["ascii_diagram"])
    forth_diagram = Sentinel("Mermaid Forth parse position >", word["forth_diagram"])
    return {
        "book": (
            apl_diagram, ascii_diagram, forth_diagram,
            Sentinel("APL stop rule ≥", "Alive←40≥T"),
            label("Mermaid awk-weird ≥", word["awk_diagram"]),
            Sentinel("APL reshape and iota", word["apl_book"]),
            Sentinel("APL function definition", "Kid←⎕FX Alive/"),
            Sentinel("Forth checker regex", r"[\]([[:space:]].*)?$//"),
            Sentinel("sed capture groups", r"sed -i 's/^\(4[1-5]\)"),
            Sentinel("wrapped Forth alternation", "recurse|e↩ / ↪ xit|leave", r"recurse\|e↩\n[ \t]*↪ xit\|leave"),
        ),
        "study-guides": (
            apl_diagram, ascii_diagram, forth_diagram,
            Sentinel("APL reshape and iota", word["apl_guide"]),
            Sentinel("APL function definition", "Kid←⎕FX Alive/"),
            Sentinel("wrapped Make trace", "total=46↩ / ↪ 41st-word-exists=yes",
                     r"total=46↩\n[ \t]*↪ 41st-word-exists=yes"),
        ),
    }


PROFILES = {}
LANG = None


def set_language(lang):
    """Load the label sentinels of `lang`. All or nothing: a missing key leaves the previous profiles."""
    global LANG
    new = profiles(lang)
    PROFILES.clear()
    PROFILES.update(new)
    LANG = lang


set_language(os.environ.get("BOOK_LANG", "en"))
