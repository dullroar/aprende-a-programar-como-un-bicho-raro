"""Where the published documents point when they link into the repository.

The Markdown sources link to files with relative paths, which is right on GitHub and in a clone. A PDF or EPUB is one
document with no repository around it, so those links become absolute GitHub URLs when the document is built. This module
is the only place that knows the repository's web address.

  * The default is the canonical repository below. It is a constant, not a guess: the build never reads `git remote`, so a
    fork, a clone with a remote alias, an offline checkout and a release build all produce the same bytes.
  * A fork that wants its own links sets REPOSITORY_WEB_BASE (and, if it publishes another branch, REPOSITORY_BRANCH).
  * Renaming the repository again means changing identity.repo_url in the locale catalog (lessons/book/locale/<lang>.yaml) and
    nowhere else. The language is BOOK_LANG (default "en"); `set_language` switches it, for example in tests.
  * The same catalog block holds the edition's identity: the title, the language tag, the publication stems. `publication_uuid`
    derives each publication's fixed EPUB identifier from the repository address, so a new repository gets new identifiers.
"""
import os
import re
import sys
import uuid
from urllib.parse import quote

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "locale"))            # never name a package `locale`: it would shadow the stdlib module
import catalog                                              # the locale catalog (needs PyYAML, like the rest of the book tooling)

IDENTITY_KEYS = ("language_tag", "repo_url", "branch", "book_title", "book_stem", "study_guides_stem", "curriculum_stem", "toc_title")
LANG = DEFAULT_WEB_BASE = DEFAULT_BRANCH = None
IDENTITY = {}


def set_language(lang):
    """Load the identity.* words of `lang`. All or nothing: a missing key leaves the old language in place."""
    global LANG, DEFAULT_WEB_BASE, DEFAULT_BRANCH, IDENTITY
    cat = catalog.load(lang)
    cat.require(["identity." + k for k in IDENTITY_KEYS])
    values = {k: cat.text("identity." + k) for k in IDENTITY_KEYS}
    LANG, DEFAULT_WEB_BASE, DEFAULT_BRANCH, IDENTITY = lang, values["repo_url"], values["branch"], values


set_language(os.environ.get("BOOK_LANG", "en"))

# RFC 3986 pchar: what may stay unescaped in a path segment or a fragment.
_SAFE = "-_.~!$&'()*+,;=:@/"


def web_base(environ=None):
    """The repository's web address, without a trailing slash. REPOSITORY_WEB_BASE overrides the default."""
    env = os.environ if environ is None else environ
    base = (env.get("REPOSITORY_WEB_BASE") or DEFAULT_WEB_BASE).strip().rstrip("/")
    if not re.fullmatch(r"https://[A-Za-z0-9.-]+(?::\d+)?(?:/[A-Za-z0-9._~-]+)+", base):
        raise SystemExit(f"REPOSITORY_WEB_BASE must be an https URL with a path, such as {DEFAULT_WEB_BASE}; got {base!r}")
    return base


def branch(environ=None):
    env = os.environ if environ is None else environ
    name = (env.get("REPOSITORY_BRANCH") or DEFAULT_BRANCH).strip()
    if not re.fullmatch(r"[A-Za-z0-9._-]+(?:/[A-Za-z0-9._-]+)*", name):
        raise SystemExit(f"REPOSITORY_BRANCH is not a plain branch name: {name!r}")
    return name


def blob_base(environ=None):
    """The prefix of a link to a file: .../blob/<branch>/ (with the trailing slash)."""
    return f"{web_base(environ)}/blob/{quote(branch(environ), safe='/')}/"


def tree_base(environ=None):
    return f"{web_base(environ)}/tree/{quote(branch(environ), safe='/')}/"


def file_url(path, fragment="", environ=None):
    """URL of a file given its repo-root-relative posix path; the fragment (an anchor, without '#') is kept."""
    return blob_base(environ) + quote(path, safe=_SAFE) + ("#" + quote(fragment, safe=_SAFE) if fragment else "")


def folder_url(path, environ=None):
    """URL of a folder given its repo-root-relative posix path. A folder has no anchor."""
    return tree_base(environ) + quote(path, safe=_SAFE)


def label(environ=None):
    """The address as shown to a reader: no scheme."""
    return web_base(environ).removeprefix("https://")


def publication_uuid(kind="book", base=None):
    """The fixed EPUB identifier (urn:uuid:...) of a publication: a UUIDv5 in the URL namespace of the repository address
    (kind "book") or of that address plus "/study-guides" or "/curriculum". Deterministic, so the EPUB bytes do not change."""
    if kind not in ("book", "study-guides", "curriculum"):
        raise ValueError(f"unknown publication {kind!r}")
    name = (base or DEFAULT_WEB_BASE).rstrip("/") + ("" if kind == "book" else "/" + kind)
    return "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, name))


def other_editions():
    """The repository addresses of every OTHER edition in the locale directory (the active language is left out)."""
    out = set()
    for name in sorted(os.listdir(os.path.join(HERE, "locale"))):
        lang, ext = os.path.splitext(name)
        if ext != ".yaml" or lang == LANG:
            continue
        try:
            out.add(catalog.load(lang).text("identity.repo_url").rstrip("/"))
        except (catalog.CatalogError, OSError):
            continue                                    # a locale without an identity block has no address to guard
    out.discard(DEFAULT_WEB_BASE.rstrip("/"))
    return out


def foreign_repo_links(html):
    """Links of a built document (HTML text) that point into ANOTHER edition's repository, for example a Spanish PDF whose links
    go to the English repository. Returns the sorted URLs; an empty list is good. A prefix match is made on a path boundary,
    so `.../learn-programming-the-weird-way-extras` is not mistaken for `.../learn-programming-the-weird-way`."""
    bad = set()
    for url in re.findall(r'(?:href|src)\s*=\s*"([^"]+)"', html):
        for base in other_editions():
            if url == base or url.startswith(base + "/") or url.startswith(base + "#") or url.startswith(base + "?"):
                bad.add(url)
    return sorted(bad)


def fill_placeholders(text, environ=None):
    """Replace the two placeholders the front-matter files use: {{REPOSITORY_WEB_URL}} and {{REPOSITORY_WEB_LABEL}}."""
    return text.replace("{{REPOSITORY_WEB_URL}}", web_base(environ)).replace("{{REPOSITORY_WEB_LABEL}}", label(environ))
