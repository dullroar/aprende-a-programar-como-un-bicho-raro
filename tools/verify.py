#!/usr/bin/env python3
"""verify: the gate runner (plan 7.2, 10). One command for "is this tree still sound?".

  python3 -I tools/verify.py --fast             the files touched since HEAD (staged, unstaged, untracked)
  python3 -I tools/verify.py --fast --files A B explicit paths instead of the git state
  python3 -I tools/verify.py --fast --since REV the files changed since REV, plus the working tree
  python3 -I tools/verify.py --release          everything: all files, all tool tests, the repo gates
  python3 -I tools/verify.py --release --no-gates   same without the slow English build gates (exit 3)
  python3 -I tools/verify.py --plan             print what --fast would run, run nothing

Fast (aims at well under 60 seconds):
  * lock: every frozen file equals its pinned hash (translation/locked-code.sha256), always;
  * per touched Markdown file or PO file (translation/po/<path>.po): the English source is read from the
    pinned clone, then I1 T0, I4 to I6, I11, I13 and I2 on the finished file (invariants.check_files), the
    segment invariants I2 to I15 on every accepted PO entry plus orphan, duplicate and stale entries
    (I16), and "working file == PO applied to English". Untranslated, fuzzy and missing entries are
    NOT findings in fast mode (a partial task is allowed); they are in release;
  * per touched tooling file: it equals the English file unless translation/tooling-allowlist.txt lists it;
  * the tests or checkers that belong to a touched tool, locale, glossary, prompt, fixture, DNT list,
    humor register or JSONL file.
Release adds: every authored file with its complete PO (I16), the tooling report for all tooling files, the
file counts of the plan (40 entry READMEs, 108 CS sources, 23 guide files), inventory --check, the negative fixtures
of plan 10.2 (tools/negative.py: the control is clean and every mutation makes its gate fail), every
tools/test_*.py, the English repo gates (baseline.GATES) and a double build of the three release documents
with identical hashes. A release that skipped the gates is INCOMPLETE (exit 3), never OK.

Exit codes: 0 all checks passed, 1 at least one check failed, 2 usage error, 3 passed but incomplete.
"""
import hashlib
import json
import os
import subprocess
import sys
import time
from collections import namedtuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))

ALLOWLIST = "translation/tooling-allowlist.txt"
FAST_BUDGET_SECONDS = 60
EXPECTED_COUNTS = (("entry_readmes", 40), ("cs_sources", 108), ("study_guides", 23))
# Coverage findings that only a release cares about (a partial translate task leaves these).
RELEASE_ONLY_I16 = ("untranslated", "fuzzy", "no PO entry")

Result = namedtuple("Result", "name problems seconds")


# ------------------------------------------------------------------------------------------ small helpers

def read_bytes(path):
    with open(path, "rb") as f:
        return f.read()


def read_text(path):
    with open(path, encoding="utf-8", newline="") as f:
        return f.read()


def sha256_file(path):
    return hashlib.sha256(read_bytes(path)).hexdigest()


def english_bytes(cfg, rel):
    """The bytes of `rel` at the pinned English commit, or None when the clone or the file is missing."""
    clone, sha = cfg.get("english_clone_path"), cfg.get("english_commit")
    if not clone or not sha or not os.path.isdir(clone):
        return None
    r = subprocess.run(["git", "-C", clone, "show", "%s:%s" % (sha, rel)], capture_output=True)
    return r.stdout if r.returncode == 0 else None


def english_text(cfg, rel):
    data = english_bytes(cfg, rel)
    return None if data is None else data.decode("utf-8")


def parse_porcelain(raw):
    """Paths from `git status --porcelain=v1 -z -uall` output (bytes). Renames yield the new path."""
    parts = raw.decode("utf-8").split("\0")
    out, i = [], 0
    while i < len(parts):
        rec = parts[i]
        i += 1
        if len(rec) < 4:
            continue
        status, path = rec[:2], rec[3:]
        if "R" in status or "C" in status:
            i += 1                                  # the old path follows as its own record
        out.append(path)
    return out


def touched_files(root, since=None):
    r = subprocess.run(["git", "-C", root, "status", "--porcelain=v1", "-z", "-uall"], capture_output=True)
    if r.returncode != 0:
        raise RuntimeError("git status failed: %s" % r.stderr.decode(errors="replace"))
    paths = parse_porcelain(r.stdout)
    if since:
        d = subprocess.run(["git", "-C", root, "diff", "--name-only", "-z", since], capture_output=True)
        if d.returncode != 0:
            raise RuntimeError("git diff failed: %s" % d.stderr.decode(errors="replace"))
        paths += [p for p in d.stdout.decode("utf-8").split("\0") if p]
    return sorted(set(paths))


def parse_allowlist(text):
    return {ln.split("#", 1)[0].strip() for ln in text.splitlines() if ln.split("#", 1)[0].strip()}


def load_allowlist(root):
    p = os.path.join(root, ALLOWLIST)
    return parse_allowlist(read_text(p)) if os.path.isfile(p) else set()


# ------------------------------------------------------------------------------------------ routing (pure)

def md_rel_of_po(path):
    """translation/po/<rel>.po -> <rel>, else None."""
    pre = "translation/po/"
    if path.startswith(pre) and path.endswith(".po"):
        return path[len(pre):-3]
    return None


def route(path, classes):
    """What `--fast` does with one touched path. Returns a list of (kind, argument) actions."""
    acts = []
    rel = md_rel_of_po(path)
    if rel is not None:
        acts.append(("file", rel))
    elif "authored" in classes:
        acts.append(("file", path))
    elif "tooling" in classes:
        acts.append(("tooling", path))
    if path.endswith(".jsonl"):
        acts.append(("jsonl", path))
    name = os.path.basename(path)
    if path.startswith("tools/") and name.endswith(".py"):
        test = path if name.startswith("test_") else "tools/test_" + name
        acts.append(("test", test))
    elif path.startswith("lessons/book/locale/"):
        acts.append(("locale", None))
    elif path == "translation/glossary.es.yaml":
        acts.append(("cmd", ("glossary", ["python3", "-I", "tools/glossary_check.py"])))
    elif path.startswith(("translation/prompts/", "translation/schemas/")):
        acts.append(("cmd", ("prompts", ["python3", "-I", "tools/prompt_check.py"])))
    elif path.startswith("tests/fixtures/"):
        acts.append(("cmd", ("fixtures", ["python3", "-I", "tools/fixture_check.py"])))
    elif path == "translation/path-map.yaml" or path == "translation/path-names.es.yaml":
        acts.append(("cmd", ("path map", ["python3", "tools/pathmap.py", "--check"])))
    elif path == "translation/dnt.txt":
        acts.append(("cmd", ("dnt", ["python3", "-I", "tools/dnt.py", "--check"])))
    elif path == "translation/humor-register.jsonl":
        acts.append(("cmd", ("humor-register", ["python3", "-I", "tools/humor_register.py", "--check"])))
    if path.startswith("lessons/") and name.endswith(".py") and not name.startswith("test_"):
        acts.append(("cmd", PATH_CMD))           # a build or check tool must not hard-code a renamed path (plan 5.6)
    return acts


PATH_CMD = ("tooling paths", ["python3", "-I", "tools/tooling_paths.py"])
LOCALE_CMDS = (
    ("locale phases", ["python3", "-I", "tools/locale_check.py"]),
    ("locale catalog", ["python3", "-I", "lessons/book/locale/catalog.py", "--check", "es", "en"]),
    ("test_catalog", ["python3", "-I", "tools/test_catalog.py"]),
    ("path map and catalog paths", ["python3", "tools/pathmap.py", "--check"]),
    PATH_CMD,
)


# ------------------------------------------------------------------------------------------ checks

def fmt(f):
    return "%s %s: %s" % (f.inv, f.where, f.msg)


def check_lock(root, full=False):
    import inventory
    import lock_code
    try:
        entries = lock_code.load_manifest(root)
    except lock_code.LockError as e:
        return ["I13 %s" % e]
    out = ["I13 " + p for p in lock_code.tree_problems(root, entries)]
    if full:
        try:
            out += ["I13 " + p for p in lock_code.clone_problems(inventory.read_config(root), entries)]
        except lock_code.LockError as e:
            out.append("I13 English clone: %s" % e)
    return out


def layout_remap(rel, root=ROOT):
    """The `remap` argument of check_file for the file with English key `rel` in the checkout `root`."""
    import enpath
    layer = enpath.load(root)
    return lambda text: enpath.remap_text(text, rel, layer)


def check_file(rel, en_text, es_text, po, ctx, release, cat=None, remap=None):
    """One authored file: its PO (or none) and the finished file against the English source.
    `po` is a polib POFile or None. `remap` (enpath.remap_text bound to the layer) writes the English text's references
    to renamed paths in the checkout's layout; the file is compared with that form, the PO and ids with the original.
    Returns problem strings."""
    import apply as apply_mod
    import invariants
    out = []
    if en_text is None:
        return ["I1 %s: no English source at the pinned commit (stale PO or wrong path)" % rel]
    remap = remap or (lambda t: t)
    en_view = remap(en_text)                    # the English text as it reads in this layout
    if po is None:
        if release:
            out.append("I16 %s: no PO file; the file is not translated" % rel)
        if es_text is not None and es_text != en_view:
            out.append("I16 %s: the file differs from the English source but has no PO file (hand edit)" % rel)
    else:
        found = invariants.check_po(en_text, po, rel, ctx)
        if not release:
            found = [f for f in found if not (f.inv == "I16" and any(k in f.msg for k in RELEASE_ONLY_I16))]
        out += [fmt(f) for f in found]
        if es_text is not None:
            try:
                applied, _ = apply_mod.apply_text(en_text, po, rel, cat, strict=False)
            except (apply_mod.ApplyError, ValueError) as e:
                out.append("I16 %s: PO cannot be applied: %s" % (rel, e))
            else:
                if remap(applied) != es_text:
                    out.append("I16 %s: the file is not the PO applied to the English source (stale or hand-edited)" % rel)
    if es_text is not None:
        out += [fmt(f) for f in invariants.check_files(en_view, es_text, rel, ctx)]
        for p in apply_mod.identity_check(en_text, rel) if release else []:
            out.append("I1 %s: %s" % (rel, p))
    return out


def check_tooling(rels, en_of, es_of, allowlist):
    """I13 tooling report. `en_of(rel)` and `es_of(rel)` return bytes or None."""
    out = []
    for rel in rels:
        es, en = es_of(rel), en_of(rel)
        if es is None:
            out.append("I13 %s: tooling file is missing" % rel)
        elif en is None:
            if rel not in allowlist:
                out.append("I13 %s: tooling file does not exist in the English source and is not on the allowlist" % rel)
        elif es != en and rel not in allowlist:
            out.append("I13 %s: tooling file differs from the English source and is not on %s" % (rel, ALLOWLIST))
    for rel in sorted(allowlist):
        if es_of(rel) is not None and en_of(rel) is not None and es_of(rel) == en_of(rel):
            out.append("I13 %s: on the allowlist but identical to English (remove the row so a later change is caught)" % rel)
    return out


def check_jsonl(path):
    out = []
    try:
        text = read_text(path)
    except OSError as e:
        return ["%s: %s" % (path, e)]
    for n, ln in enumerate(text.splitlines(), 1):
        if ln.strip():
            try:
                json.loads(ln)
            except ValueError as e:
                out.append("%s:%d: not valid JSON (%s)" % (path, n, e))
    return out


def negative_problems():
    """The negative fixtures of plan 10.2: the control is clean and every mutation makes its gate fail (tools/negative.py).
    A gate that stopped failing is a disarmed gate, and a release with a disarmed gate is not a release."""
    import breakage_pilot
    import negative
    import resume_test
    return negative.run_all() + breakage_pilot.run_all() + resume_test.run_all()


def check_counts(root, expected=EXPECTED_COUNTS):
    import inventory
    totals = inventory.build_inventory(root)["totals"]
    return ["counts: %s is %s, the plan says %s" % (k, totals.get(k), v)
            for k, v in expected if totals.get(k) != v]


def dir_hashes(path):
    out = {}
    for dp, _, fn in os.walk(path):
        for f in fn:
            full = os.path.join(dp, f)
            out[os.path.relpath(full, path).replace(os.sep, "/")] = sha256_file(full)
    return out


def compare_dirs(a, b):
    """Problems between two build output directories (double build must give identical hashes)."""
    ha, hb = dir_hashes(a), dir_hashes(b)
    if not ha or not hb:
        return ["double build: a build directory is empty (%s: %d files, %s: %d files)" % (a, len(ha), b, len(hb))]
    out = []
    for p in sorted(set(ha) | set(hb)):
        if p not in hb:
            out.append("double build: %s only in the first build" % p)
        elif p not in ha:
            out.append("double build: %s only in the second build" % p)
        elif ha[p] != hb[p]:
            out.append("double build: %s differs between two builds" % p)
    return out


def run_cmd(argv, timeout=300, cwd=ROOT):
    """Run a command; returns (problems, seconds). A non-zero exit or a timeout is a problem."""
    t0 = time.time()
    try:
        r = subprocess.run(argv, cwd=cwd, capture_output=True, timeout=timeout)
    except subprocess.TimeoutExpired:
        return ["%s: timed out after %ds" % (" ".join(argv), timeout)], time.time() - t0
    except OSError as e:
        return ["%s: cannot run (%s)" % (" ".join(argv), e)], time.time() - t0
    if r.returncode != 0:
        tail = (r.stdout + r.stderr).decode("utf-8", "replace").strip().splitlines()[-12:]
        return ["%s: exit %d" % (" ".join(argv), r.returncode)] + ["    " + ln for ln in tail], time.time() - t0
    return [], time.time() - t0


def timed(name, fn, *a):
    t0 = time.time()
    problems = fn(*a)
    return Result(name, problems, time.time() - t0)


# ------------------------------------------------------------------------------------------ drivers

class Env:
    """Lazy shared state: config, context, catalog, allowlist."""

    def __init__(self, root=ROOT):
        import inventory
        import enpath
        self.root = root
        self.cfg = inventory.read_config(root)
        self.layer = enpath.load(root)
        self._ctx = self._cat = None

    @property
    def ctx(self):
        if self._ctx is None:
            import invariants
            self._ctx = invariants.load_context(root=self.root)
        return self._ctx

    @property
    def cat(self):
        if self._cat is None:
            import catalog
            self._cat = catalog.load("es")
        return self._cat

    def file_problems(self, rel, release):
        import apply as apply_mod
        import polib  # noqa: F401  (load_po needs it)
        full = self.layer.full(rel)                 # `rel` is the English key; the file sits at its working path
        es = read_text(full) if os.path.isfile(full) else None
        po_path = apply_mod.po_path_for(rel, os.path.join(self.root, "translation", "po"))
        po = None
        if os.path.isfile(po_path):
            try:
                po = apply_mod.load_po(po_path)
            except (apply_mod.ApplyError, OSError, ValueError) as e:
                return ["I16 %s: PO file unreadable: %s" % (rel, e)]
        if es is None and po is None:
            return []                                           # deleted, nothing left to check
        if es is None:
            return ["I16 %s: PO file exists but the Markdown file does not" % rel]
        return check_file(rel, english_text(self.cfg, rel), es, po, self.ctx, release, self.cat,
                          layout_remap(rel, self.root))

    def tooling_problems(self, rels, allowlist):
        def es_of(r):
            p = self.layer.full(r)
            return read_bytes(p) if os.path.isfile(p) else None
        return check_tooling(rels, lambda r: english_bytes(self.cfg, r), es_of, allowlist)


def plan_fast(paths, root=ROOT):
    """Deduplicated, ordered actions for the touched paths (named as git reports them: the working names). Each is
    routed by its English key, the name every PO, ledger row and class rule uses."""
    import enpath
    import inventory
    layer = enpath.load(root)
    seen, acts = set(), []
    for p in paths:
        p = layer.english(p)
        for a in route(p, inventory.classify(p)):
            key = (a[0], repr(a[1]))
            if key not in seen:
                seen.add(key)
                acts.append(a)
    return acts


def run_fast(paths, root=ROOT):
    env = Env(root)
    results = [timed("lock", check_lock, root)]
    acts = plan_fast(paths, root)
    allow = load_allowlist(root)
    tooling = [a[1] for a in acts if a[0] == "tooling"]
    if tooling:
        results.append(timed("tooling (%d file(s))" % len(tooling), env.tooling_problems, tooling, allow))
    for kind, arg in acts:
        if kind == "file":
            results.append(timed("file " + arg, env.file_problems, arg, False))
        elif kind == "jsonl":
            results.append(timed("jsonl " + arg, check_jsonl, os.path.join(root, arg)))
        elif kind == "test":
            if os.path.isfile(os.path.join(root, arg)):
                results.append(timed("test " + arg, lambda a=arg: run_cmd(["python3", "-I", a])[0]))
        elif kind == "locale":
            for name, argv in LOCALE_CMDS:
                results.append(timed(name, lambda a=argv: run_cmd(a)[0]))
        elif kind == "cmd":
            results.append(timed(arg[0], lambda a=arg[1]: run_cmd(a)[0]))
    return results


def release_gate_commands(artifacts):
    """The repo gates: baseline.GATES, with the three release builds pointed at `artifacts`."""
    import baseline
    plain = [(n, list(argv), t) for n, argv, t in baseline.GATES if not n.startswith("release-")]
    release = []
    for n, argv, t in baseline.GATES:
        if n.startswith("release-"):
            if argv[-2] != "--artifacts-dir":
                raise ValueError("baseline gate %s has no --artifacts-dir as its last option" % n)
            release.append((n, list(argv[:-1]) + [artifacts], t))
    return plain, release


def run_release(root=ROOT, gates=True):
    import inventory
    import segment
    env = Env(root)
    results = [timed("lock (manifest and English clone)", check_lock, root, True)]
    results.append(timed("inventory --check", lambda: run_cmd(["python3", "tools/inventory.py", "--check"])[0]))
    results.append(timed("file counts", check_counts, root))
    allow = load_allowlist(root)
    tooling = [p for p in inventory.list_files(root) if "tooling" in inventory.classify(p)]
    results.append(timed("tooling (%d file(s))" % len(tooling), env.tooling_problems, tooling, allow))
    t0 = time.time()
    bad = []
    files = segment.authored_files(root)
    for rel in files:
        bad += env.file_problems(rel, True)
    for dp, _, fn in os.walk(os.path.join(root, "translation", "po")):
        for f in fn:
            if f.endswith(".po"):
                rel = md_rel_of_po(os.path.relpath(os.path.join(dp, f), root).replace(os.sep, "/"))
                if rel is not None and rel not in set(files):
                    bad.append("I16 %s: PO file for a file that is not an authored Markdown file (orphan PO)" % rel)
    results.append(Result("authored files (%d) with PO" % len(files), bad, time.time() - t0))
    results.append(timed("negative fixtures (plan 10.2)", negative_problems))
    for p in ("translation/exception-register.jsonl", "translation/humor-register.jsonl"):
        if os.path.isfile(os.path.join(root, p)):
            results.append(timed("jsonl " + p, check_jsonl, os.path.join(root, p)))
    for name, argv in LOCALE_CMDS + (
            ("glossary", ["python3", "-I", "tools/glossary_check.py"]),
            ("prompts", ["python3", "-I", "tools/prompt_check.py"]),
            ("fixtures", ["python3", "-I", "tools/fixture_check.py"]),
            ("dnt", ["python3", "-I", "tools/dnt.py", "--check"]),
            ("humor-register", ["python3", "-I", "tools/humor_register.py", "--check"])):
        results.append(timed(name, lambda a=argv: run_cmd(a)[0]))
    tests = sorted(f for f in os.listdir(os.path.join(root, "tools")) if f.startswith("test_") and f.endswith(".py"))
    for t in tests:
        results.append(timed("test tools/" + t, lambda a="tools/" + t: run_cmd(["python3", "-I", a], 900)[0]))
    if gates:
        work = os.path.join(root, "translation", "work", "verify")
        a_dir, b_dir = os.path.join(work, "release-a"), os.path.join(work, "release-b")
        for name, argv, timeout in release_gate_commands(a_dir)[0]:
            results.append(timed("gate " + name, lambda a=argv, t=timeout: run_cmd(a, t)[0]))
        for d in (a_dir, b_dir):
            for name, argv, timeout in release_gate_commands(os.path.relpath(d, root))[1]:
                results.append(timed("gate %s (%s)" % (name, os.path.basename(d)),
                                     lambda a=argv, t=timeout: run_cmd(a, t)[0]))
        results.append(timed("double build: identical hashes", compare_dirs, a_dir, b_dir))
    return results


def report(results, label, incomplete=False):
    failed = 0
    for r in results:
        status = "FAIL" if r.problems else "ok  "
        print("%s %-44s %5.1fs" % (status, r.name, r.seconds))
        for p in r.problems[:40]:
            print("       " + p)
        if len(r.problems) > 40:
            print("       ... %d more" % (len(r.problems) - 40))
        failed += bool(r.problems)
    total = sum(r.seconds for r in results)
    if label == "fast" and total > FAST_BUDGET_SECONDS:
        print("SLOW: fast verify took %.0fs, over the %ds budget" % (total, FAST_BUDGET_SECONDS))
    if failed:
        print("verify --%s: FAIL (%d of %d checks failed, %.1fs)" % (label, failed, len(results), total))
        return 1
    if incomplete:
        print("verify --%s: INCOMPLETE (checks passed, the English gates were skipped, %.1fs)" % (label, total))
        return 3
    print("verify --%s: OK (%d checks, %.1fs)" % (label, len(results), total))
    return 0


def main(argv):
    args = argv[1:]
    flags = {a for a in args if a.startswith("--")}
    unknown = flags - {"--fast", "--release", "--no-gates", "--plan", "--files", "--since"}
    if unknown or not ({"--fast", "--release", "--plan"} & flags) or ("--fast" in flags and "--release" in flags):
        print(__doc__.split("Exit codes")[0].rstrip())
        return 2
    if "--release" in flags:
        gates = "--no-gates" not in flags
        return report(run_release(ROOT, gates), "release", incomplete=not gates)
    if "--files" in args:
        i = args.index("--files")
        paths = [a for a in args[i + 1:] if not a.startswith("--")]
    else:
        since = args[args.index("--since") + 1] if "--since" in args and args.index("--since") + 1 < len(args) else None
        paths = touched_files(ROOT, since)
    if "--plan" in flags:
        for a in plan_fast(paths, ROOT):
            print("%s %s" % (a[0], a[1] if a[1] is not None else ""))
        return 0
    return report(run_fast(paths, ROOT), "fast")


if __name__ == "__main__":
    sys.exit(main(sys.argv))
