"""The four card categories and their Spanish words (decision 11).

A family whose code still prints the English words keeps them in its prose; a family localized through loc_apply prints
the mapped Spanish words and its prose follows. Both forms are valid, a file must use one form only, and any other
spelling (a missing accent, a singular, a translation not in the glossary) is a fault."""
import re

EN = ("Meetings", "Coding", "Debugging", "Learning")
ES = ("Reuniones", "Programación", "Depuración", "Aprendizaje")
EN_TO_ES = dict(zip(EN, ES))
ES_TO_EN = dict(zip(ES, EN))
# Near misses that look like the word but are not the approved one.
WRONG = ("Reunión", "Reunion", "Reunions", "Programacion", "Depuracion", "Debugueo", "Codificación", "Aprendizage")
# (?<=xxx): ed-weird joins a card and a ledger copy, so tally marks sit right before the word (`...xxxMeetings 12|xx`)
WORD_RE = re.compile(r"(?:(?<!\w)|(?<=xxx))(%s)(?!\w)" % "|".join(EN + ES))


def to_english(word):
    """Return the English category for an English or Spanish word, else the word unchanged."""
    return ES_TO_EN.get(word, word)


FENCE_RE = re.compile(r"^(`{3,}|~{3,})[^\n]*\n.*?^\1[ \t]*$", re.M | re.S)
SPAN_RE = re.compile(r"(?<!`)(`+)(?!`)(.+?)(?<!`)\1(?!`)", re.S)


def code_text(text):
    """Only the code of a Markdown text (fenced blocks and inline spans): the category as data, not as an ordinary word.

    'Depuración' as a heading or 'aprendizaje' in a sentence is plain Spanish and is never checked."""
    parts = [m.group(0) for m in FENCE_RE.finditer(text)]
    rest = FENCE_RE.sub("", text)
    parts += [m.group(2) for m in SPAN_RE.finditer(rest)]
    return "\n".join(parts)


def forms_used(text):
    """Return which forms appear as whole words in `text`: a subset of {'en', 'es'}."""
    return {"en" if m.group(1) in EN else "es" for m in WORD_RE.finditer(code_text(text))}


def mixed(text):
    """True when one text uses both the English and the Spanish category words."""
    return len(forms_used(text)) > 1


def wrong_spellings(text):
    """Unapproved near-miss spellings found as whole words (an empty list when clean)."""
    code = code_text(text)
    return [w for w in WRONG if re.search(r"(?<!\w)%s(?!\w)" % re.escape(w), code)]
