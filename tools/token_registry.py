#!/usr/bin/env python3
"""Protected-token registry (Part II, plan 4.5, task S1-002).

Writes translation/protected-tokens/tokens.jsonl (the machine file) and one Markdown page per
language (generated from the JSONL, so the two cannot drift).

Rules (plan 4.5): tokens come from introspection of the real language runtime, or from a pinned
specification file; never from a model's memory. Each language record states the version tested,
the extraction command and the compile fixtures that verified it. A language with no introspection
tool and no pinned specification gets a `not-extracted` record with the reason and zero tokens:
its family stays English (policy H-05) and any report says NOT TESTED.

Usage:
  python3 -I tools/token_registry.py --write     extract, verify, write JSONL and Markdown
  python3 -I tools/token_registry.py --check     Markdown and JSONL on disk must agree (drift gate)
  python3 -I tools/token_registry.py --check --reextract
                                                  also re-extract and compare tokens and versions
  python3 -I tools/token_registry.py --render    regenerate Markdown from the JSONL only
"""
import builtins
import json
import keyword
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
OUT_DIR = os.path.join(ROOT, "translation", "protected-tokens")
JSONL = "tokens.jsonl"
KINDS = ("reserved", "contextual", "api")
SPEC_DIR = "specs"  # translation/protected-tokens/specs/<language>.txt: pinned specification extracts

# Languages seen in translation/part2/code-inventory.jsonl that have no extractor here, with why.
# A future task adds an extractor or a pinned spec file; until then the family stays English.
NOT_EXTRACTED = {
    "apl": "GNU APL not installed on this host; no pinned specification extract in specs/",
    "awk": "gawk has no keyword listing command; no pinned specification extract in specs/",
    "batch": "cmd.exe is not available in WSL; no pinned specification extract in specs/",
    "c": "no compiler introspection for keywords; no pinned specification extract in specs/",
    "cmake": "cmake introspection was refused in this session (dontAsk mode); rerun where allowed",
    "cobol": "GnuCOBOL not installed on this host (cobc --list-reserved would be the source)",
    "csharp": "dotnet SDK is present but running it was refused in this session (dontAsk mode); rerun where allowed with a Roslyn probe",
    "forth": "gforth not installed on this host (words listing would be the source)",
    "go": "no go toolchain on this host (go/token would be the source)",
    "haskell": "GHC not installed on this host",
    "java": "no JDK on this host",
    "kotlin": "no Kotlin compiler on this host",
    "lisp": "SBCL not installed on this host (cl package symbols would be the source)",
    "makefile": "no pinned specification extract in specs/",
    "perl": "perl has no keyword listing command; no pinned specification extract in specs/",
    "powershell": "pwsh not installed on this host",
    "rust": "rustc is present but running it was refused in this session (dontAsk mode); rerun where allowed with a compile probe",
    "sed": "no pinned specification extract in specs/",
    "shell": "bash `compgen -k` would be the source; not run by this tool yet",
    "sql": "dialect not fixed; no pinned specification extract in specs/",
    "tcl": "Tcl not installed on this host",
}

# ---------------------------------------------------------------------------------------------
# Python: keyword.kwlist, keyword.softkwlist, the builtins module; verified with compile().


def _py_compiles(src):
    try:
        compile(src, "<fixture>", "exec")
        return True
    except SyntaxError:
        return False


def extract_python():
    version = "%d.%d.%d" % sys.version_info[:3]
    tokens, fixtures = [], []
    for w in sorted(keyword.kwlist):
        tokens.append({"token": w, "kind": "reserved", "source": "keyword.kwlist"})
        # Compile fixture (negative): a reserved word cannot be an assignment target.
        # `__peg_parser__` style oddities do not exist in 3.12; True/False/None also fail.
        ok = not _py_compiles("%s = 1" % w)
        fixtures.append({"token": w, "fixture": "%s = 1" % w, "expect": "SyntaxError", "ok": ok})
    for w in sorted(keyword.softkwlist):
        tokens.append({"token": w, "kind": "contextual", "source": "keyword.softkwlist"})
        ok = _py_compiles("%s = 1" % w)
        fixtures.append({"token": w, "fixture": "%s = 1" % w, "expect": "compiles", "ok": ok})
    for w in sorted(n for n in dir(builtins) if not n.startswith("_")):
        tokens.append({"token": w, "kind": "api", "source": "dir(builtins)"})
    return {
        "language": "python",
        "status": "extracted",
        "version": "CPython " + version,
        "command": "python3 -c 'import keyword, builtins; keyword.kwlist; keyword.softkwlist; dir(builtins)'",
        "positive_examples": ["if x: pass", "print(len(items))"],
        "negative_examples": ["class = 1", "def = 2"],
        "tokens": tokens,
        "fixtures": fixtures,
    }


# ---------------------------------------------------------------------------------------------
# JavaScript: reserved words verified by node itself; globals by Object.getOwnPropertyNames.

# Candidate list for the compile probe. It is only a probe list: a word becomes `reserved` only
# if node refuses `var <word>` and the word is not a plain global; nothing is trusted from memory.
JS_PROBE = (
    "await break case catch class const continue debugger default delete do else enum export extends "
    "false finally for function if import in instanceof new null return super switch this throw true "
    "try typeof var void while with yield let static implements interface package private protected "
    "public async of get set arguments eval undefined NaN Infinity"
).split()

JS_SCRIPT = r"""
const probe = JSON.parse(process.argv[1]);
const out = {version: process.version, reserved: [], contextual: [], globals: []};
for (const w of probe) {
  let sloppy = true, strict = true;
  try { new Function('var ' + w + ' = 1;'); } catch (e) { sloppy = false; }
  try { new Function('"use strict"; var ' + w + ' = 1;'); } catch (e) { strict = false; }
  if (!sloppy) out.reserved.push(w);
  else if (!strict) out.contextual.push(w);
}
out.globals = Object.getOwnPropertyNames(globalThis).filter(n => !n.startsWith('_')).sort();
console.log(JSON.stringify(out));
"""


def run_node(args):
    """Run node with the probe script; separated so tests can substitute it."""
    p = subprocess.run(["node", "-e", JS_SCRIPT, "--"] + args, capture_output=True, text=True,
                       timeout=60, check=True)
    return p.stdout


def extract_javascript(runner=run_node):
    data = json.loads(runner([json.dumps(JS_PROBE)]))
    tokens, fixtures = [], []
    for w in sorted(data["reserved"]):
        tokens.append({"token": w, "kind": "reserved", "source": "node: new Function('var w') refused"})
        fixtures.append({"token": w, "fixture": "var %s = 1;" % w, "expect": "SyntaxError (node)", "ok": True})
    for w in sorted(data["contextual"]):
        tokens.append({"token": w, "kind": "contextual",
                       "source": "node: allowed sloppy, refused in strict mode"})
        fixtures.append({"token": w, "fixture": "var %s = 1;" % w,
                         "expect": "sloppy compiles, strict SyntaxError (node)", "ok": True})
    for w in data["globals"]:
        tokens.append({"token": w, "kind": "api", "source": "Object.getOwnPropertyNames(globalThis)"})
    return {
        "language": "javascript",
        "status": "extracted",
        "version": "Node " + data["version"],
        "command": "node -e <probe script in tools/token_registry.py JS_SCRIPT>",
        "positive_examples": ["const total = cards.length;", "console.log(total);"],
        "negative_examples": ["var class = 1;", "var export = 2;"],
        "tokens": tokens,
        "fixtures": fixtures,
    }


# ---------------------------------------------------------------------------------------------
# Pinned specification files: translation/protected-tokens/specs/<language>.txt
# Format: header lines "# key: value" (version, source, sha256 optional), then "kind token" lines.


def read_spec(path):
    meta, tokens = {}, []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            line = line.rstrip("\n")
            if not line.strip():
                continue
            if line.startswith("#"):
                if ":" in line:
                    k, v = line[1:].split(":", 1)
                    meta[k.strip()] = v.strip()
                continue
            parts = line.split()
            if len(parts) != 2 or parts[0] not in KINDS:
                raise ValueError("%s:%d: expected '<kind> <token>' with kind in %s" % (path, n, KINDS))
            tokens.append({"token": parts[1], "kind": parts[0], "source": "spec: " + meta.get("source", "?")})
    for need in ("version", "source", "command"):
        if need not in meta:
            raise ValueError("%s: header '# %s:' is required" % (path, need))
    return meta, tokens


def extract_spec(language, path):
    meta, tokens = read_spec(path)
    return {
        "language": language,
        "status": "extracted",
        "version": meta["version"],
        "command": meta["command"],
        "positive_examples": [],
        "negative_examples": [],
        "tokens": tokens,
        "fixtures": [],
    }


def not_extracted(language, reason):
    return {"language": language, "status": "not-extracted", "version": "NOT TESTED", "command": "",
            "reason": reason, "positive_examples": [], "negative_examples": [], "tokens": [], "fixtures": []}


EXTRACTORS = {"python": extract_python, "javascript": extract_javascript}


def build_all(out_dir=OUT_DIR, extractors=None):
    extractors = EXTRACTORS if extractors is None else extractors
    records = []
    for lang in sorted(set(extractors) | set(NOT_EXTRACTED)):
        spec = os.path.join(out_dir, SPEC_DIR, lang + ".txt")
        if lang in extractors:
            records.append(extractors[lang]())
        elif os.path.exists(spec):
            records.append(extract_spec(lang, spec))
        else:
            records.append(not_extracted(lang, NOT_EXTRACTED[lang]))
    return records


# ---------------------------------------------------------------------------------------------
# Validation, JSONL, Markdown.


def validate(records):
    """Return a list of problems; empty means the registry is internally sound."""
    problems = []
    seen_lang = set()
    for r in records:
        lang = r.get("language")
        if lang in seen_lang:
            problems.append("%s: duplicate language record" % lang)
        seen_lang.add(lang)
        if r.get("status") == "extracted":
            if not r.get("version") or r["version"] == "NOT TESTED":
                problems.append("%s: extracted record has no version" % lang)
            if not r.get("command"):
                problems.append("%s: extracted record has no extraction command" % lang)
            if not r["tokens"]:
                problems.append("%s: extracted record has no tokens" % lang)
            seen = {}
            for t in r["tokens"]:
                if t["kind"] not in KINDS:
                    problems.append("%s: token %r has unknown kind %r" % (lang, t["token"], t["kind"]))
                if not t.get("source"):
                    problems.append("%s: token %r has no source" % (lang, t["token"]))
                key = t["token"]
                if key in seen and seen[key] != t["kind"] and "api" not in (seen[key], t["kind"]):
                    problems.append("%s: token %r listed as %s and %s" % (lang, key, seen[key], t["kind"]))
                seen[key] = t["kind"]
            for fx in r["fixtures"]:
                if not fx.get("ok"):
                    problems.append("%s: compile fixture failed for %r (%s)" % (lang, fx["token"], fx["fixture"]))
        elif r.get("status") == "not-extracted":
            if r["tokens"]:
                problems.append("%s: not-extracted record must have no tokens" % lang)
            if not r.get("reason"):
                problems.append("%s: not-extracted record needs a reason" % lang)
        else:
            problems.append("%s: unknown status %r" % (lang, r.get("status")))
    return problems


def dump_jsonl(records):
    return "".join(json.dumps(r, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n"
                   for r in records)


def load_jsonl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(line) for line in f if line.strip()]


def render_markdown(r):
    """The generated page for one language record. Pure function of the record."""
    lang = r["language"]
    lines = ["<!-- GENERATED from tokens.jsonl by tools/token_registry.py; do not edit by hand -->",
             "# Protected tokens: %s" % lang, "",
             "- Status: %s" % r["status"],
             "- Version tested: %s" % r["version"]]
    if r["status"] != "extracted":
        lines += ["- Reason: %s" % r["reason"], "",
                  "No token list exists for this language. Its family stays English and any report says NOT TESTED."]
        return "\n".join(lines) + "\n"
    lines += ["- Extraction command: `%s`" % r["command"], ""]
    for kind, title in (("reserved", "Reserved words"), ("contextual", "Contextual words"),
                        ("api", "Standard API names")):
        names = sorted(t["token"] for t in r["tokens"] if t["kind"] == kind)
        lines += ["## %s (%d)" % (title, len(names)), ""]
        lines += ["`" + "` `".join(names) + "`" if names else "(none)", ""]
    for title, key in (("Positive examples (stay as written)", "positive_examples"),
                       ("Negative examples (do not compile)", "negative_examples")):
        if r[key]:
            lines += ["## " + title, ""] + ["- `%s`" % e for e in r[key]] + [""]
    if r["fixtures"]:
        ok = sum(1 for f in r["fixtures"] if f["ok"])
        lines += ["## Compile fixtures", "", "%d of %d passed." % (ok, len(r["fixtures"])), ""]
    return "\n".join(lines).rstrip("\n") + "\n"


def write_all(records, out_dir=OUT_DIR):
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, JSONL), "w", encoding="utf-8", newline="\n") as f:
        f.write(dump_jsonl(records))
    for r in records:
        with open(os.path.join(out_dir, r["language"] + ".md"), "w", encoding="utf-8", newline="\n") as f:
            f.write(render_markdown(r))


def read_text(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def check(out_dir=OUT_DIR, reextract=False, extractors=None):
    """Drift gate: every page equals the rendering of its JSONL record, no stray pages, JSONL sound."""
    problems = []
    jpath = os.path.join(out_dir, JSONL)
    if not os.path.exists(jpath):
        return ["%s is missing" % jpath]
    records = load_jsonl(jpath)
    problems += validate(records)
    expected = set()
    for r in records:
        expected.add(r["language"] + ".md")
        page = os.path.join(out_dir, r["language"] + ".md")
        if not os.path.exists(page):
            problems.append("%s.md is missing" % r["language"])
        elif read_text(page) != render_markdown(r):
            problems.append("%s.md drifted from tokens.jsonl" % r["language"])
    for name in sorted(os.listdir(out_dir)):
        if name.endswith(".md") and name not in expected:
            problems.append("%s has no record in tokens.jsonl" % name)
    if read_text(jpath) != dump_jsonl(records):
        problems.append("tokens.jsonl is not in canonical form (rewrite with --write)")
    if reextract:
        fresh = {r["language"]: r for r in build_all(out_dir, extractors)}
        for r in records:
            f = fresh.get(r["language"])
            if f is None:
                problems.append("%s: not produced by a fresh extraction" % r["language"])
            elif f != r:
                problems.append("%s: tokens.jsonl differs from a fresh extraction (version %s vs %s)"
                                % (r["language"], r["version"], f["version"]))
    return problems


def main(argv):
    mode = argv[1] if len(argv) > 1 else "--check"
    reextract = "--reextract" in argv
    if mode == "--write":
        records = build_all()
        problems = validate(records)
        if problems:
            print("\n".join(problems))
            return 1
        write_all(records)
        ext = [r["language"] for r in records if r["status"] == "extracted"]
        print("wrote %d languages; extracted: %s" % (len(records), ", ".join(ext)))
        return 0
    if mode == "--render":
        records = load_jsonl(os.path.join(OUT_DIR, JSONL))
        write_all(records)
        return 0
    if mode == "--check":
        problems = check(reextract=reextract)
        print("\n".join(problems) if problems else "token registry OK")
        return 1 if problems else 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
