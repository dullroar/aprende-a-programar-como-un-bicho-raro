#!/usr/bin/env python3
"""Scratch-clone proof that the locale layer leaves the English edition byte-identical (plan 5.4, P2-016).

Steps (everything happens under translation/work/scratch/, which is git-ignored):
  1. clone the pinned English commit (local clone, no network);
  2. build all six publications twice with --artifacts-dir ("pre" rounds, English tooling untouched);
  3. apply the locale layer: the tooling-allowlist files (minus the metadata YAMLs, which carry the Spanish
     edition's identity and are data, not tooling) and lessons/book/locale/;
  4. build all six publications twice more ("post" rounds, BOOK_LANG unset = English);
  5. require sha256 equality: pre-1 == pre-2 (the build is reproducible, else the proof means nothing),
     post-1 == post-2, and pre == post. The three English --check gates must also pass on the layered clone.

Usage:
    python3 tools/scratch_proof.py              # full proof (about 5 minutes), writes translation/scratch-proof.md
    python3 tools/scratch_proof.py --layer      # print the layer file list and exit
    python3 tools/scratch_proof.py --tests      # apply the layer to the clone and run the tests of lessons/book there, in English
                                                # (the classes that skip in the Spanish checkout, @english_only, must run and pass)
"""
import hashlib
import os
import shutil
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
import enpath  # noqa: E402
SCRATCH = os.path.join(ROOT, "translation", "work", "scratch")
REPORT = os.path.join(ROOT, "translation", "scratch-proof.md")
ALLOWLIST = "translation/tooling-allowlist.txt"
LOCALE_DIR = "lessons/book/locale"
NODE_MODULES = "lessons/book/diagrams/node_modules"
PY = "python3"

# Six publications: three builders, each writes a PDF and an EPUB.
BUILDERS = [
    ("book", "lessons/book/build.py"),
    ("study-guides", "lessons/study-guides/build.py"),
    ("curriculum", "lessons/curriculum/build.py"),
]
CHECKS = [(n, ["lessons/%s/build.py" % ("book" if n == "book" else n), "--check"]) for n, _ in BUILDERS]
EXPECTED_ARTIFACTS = 6


def read_lines(path):
    with open(path, encoding="utf-8") as f:
        return f.read().splitlines()


def parse_allowlist(lines):
    out = []
    for line in lines:
        line = line.split("#", 1)[0].strip()
        if line:
            out.append(line)
    return out


def is_metadata(rel):
    return rel.endswith("metadata.yaml") or rel.endswith("metadata.yml")


# Data in the layout of the edition (P3B-005): these files name other files, so the Spanish layout rewrites them. They are
# allowlisted (I13) but never part of the layer that is applied to the English clone: the English clone keeps its own.
DATA_FILES = ("lessons/book/chapters.txt", "lessons/study-guides/chapters.txt", "lessons/book/guide-dependencies.json")


def is_data(rel):
    return is_metadata(rel) or rel.startswith(".github/") or rel in DATA_FILES


def layer_files(root=ROOT):
    """Repo-relative files that make up the locale layer: allowlisted tooling (not metadata) and the locale dir."""
    files = [r for r in parse_allowlist(read_lines(os.path.join(root, ALLOWLIST))) if not is_data(r)]
    loc = os.path.join(root, LOCALE_DIR)
    for dirpath, dirnames, filenames in os.walk(loc):
        dirnames[:] = [d for d in dirnames if d != "__pycache__"]
        for fn in filenames:
            if fn.endswith(".pyc"):
                continue
            files.append(os.path.relpath(os.path.join(dirpath, fn), root).replace(os.sep, "/"))
    return sorted(set(files))


def apply_layer(src_root, dest_root, files):
    """Copy each layer file (named by English key) from where it sits in `src_root` to its English path in the clone."""
    layer = enpath.load(src_root)
    for rel in files:
        dst = os.path.join(dest_root, rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(layer.full(rel), dst)


def sha256_file(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def hash_dir(path):
    """{file name: sha256} for the artifacts in a directory (empty if it does not exist)."""
    if not os.path.isdir(path):
        return {}
    return {fn: sha256_file(os.path.join(path, fn)) for fn in sorted(os.listdir(path))
            if os.path.isfile(os.path.join(path, fn))}


def compare(label_a, a, label_b, b, expected=EXPECTED_ARTIFACTS):
    """Problems between two hash maps; an empty list means identical. Fewer artifacts than expected is a problem."""
    problems = []
    if len(a) < expected:
        problems.append("%s has %d artifacts, expected %d" % (label_a, len(a), expected))
    if len(b) < expected:
        problems.append("%s has %d artifacts, expected %d" % (label_b, len(b), expected))
    for name in sorted(set(a) | set(b)):
        if name not in a:
            problems.append("%s only in %s" % (name, label_b))
        elif name not in b:
            problems.append("%s only in %s" % (name, label_a))
        elif a[name] != b[name]:
            problems.append("%s differs: %s %s vs %s %s" % (name, label_a, a[name][:12], label_b, b[name][:12]))
    return problems


def run(cmd, cwd, timeout, env=None):
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, timeout=timeout, env=env)
        return p.returncode, (p.stdout + p.stderr), time.time() - t0
    except subprocess.TimeoutExpired:
        return "timeout", "", time.time() - t0


def build_round(clone, out_dir, builders=None, timeout=1200, env=None):
    """Build every publication into out_dir. Returns (problems, seconds)."""
    builders = BUILDERS if builders is None else builders
    if os.path.isdir(out_dir):
        shutil.rmtree(out_dir)
    os.makedirs(out_dir)
    problems, total = [], 0.0
    for name, script in builders:
        code, out, secs = run([PY, script, "--release", "--artifacts-dir", out_dir], clone, timeout, env)
        total += secs
        if code != 0:
            tail = "\n".join(out.strip().splitlines()[-8:])
            problems.append("build %s exit %s\n%s" % (name, code, tail))
    return problems, total


def english_env():
    env = dict(os.environ)
    env.pop("BOOK_LANG", None)
    env.pop("BOOK_LAYOUT", None)
    return env


def english_layer_env():
    """The environment of the unit tests in the clone: the layer carries es.yaml (layout spanish) but the files keep the English names."""
    env = english_env()
    env["BOOK_LAYOUT"] = "english"
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def prepare_clone(english_path, sha, dest):
    if os.path.isdir(dest):
        shutil.rmtree(dest)
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    for cmd in (["git", "clone", "--quiet", "--no-hardlinks", english_path, dest],
                ["git", "-C", dest, "checkout", "--quiet", sha]):
        code, out, _ = run(cmd, ROOT, 300)
        if code != 0:
            raise RuntimeError("%s failed: %s" % (" ".join(cmd), out.strip()))
    nm_src = os.path.join(ROOT, NODE_MODULES)
    nm_dst = os.path.join(dest, NODE_MODULES)
    if os.path.isdir(nm_src) and not os.path.exists(nm_dst):
        os.symlink(nm_src, nm_dst)


def config_value(key):
    with open(os.path.join(ROOT, "loop", "CONFIG.yaml"), encoding="utf-8") as f:
        for line in f:
            if line.startswith(key + ":"):
                return line.split(":", 1)[1].split("#", 1)[0].strip()
    raise KeyError(key)


def unexpected_changes(clone, layer):
    """Tracked files modified or untracked in the clone that are not part of the layer (build output is ignored)."""
    code, out, _ = run(["git", "status", "--short", "--untracked-files=all"], clone, 120)
    bad = []
    for line in out.splitlines():
        rel = line[3:].strip().strip('"')
        if rel in layer or rel.endswith(".pyc") or "__pycache__" in rel:
            continue
        if rel == NODE_MODULES.rsplit("/", 1)[0] + "/node_modules":
            continue
        bad.append(line.strip())
    return bad


def render(info):
    L = ["# Scratch-clone proof (P2-016)", "",
         "Generated by `python3 tools/scratch_proof.py`. English commit `%s`; layer applied to a scratch clone "
         "under `translation/work/scratch/` (git-ignored); builds with `BOOK_LANG` unset." % info["sha"], "",
         "## Layer applied (%d files)" % len(info["layer"]), ""]
    L += ["- `%s`" % f for f in info["layer"]]
    L += ["", "## Artifact hashes (sha256)", "", "| artifact | pre-1 | pre-2 | post-1 | post-2 |", "|---|---|---|---|---|"]
    names = sorted(set().union(*[set(info[k]) for k in ("pre1", "pre2", "post1", "post2")]))
    for n in names:
        L.append("| %s | %s |" % (n, " | ".join("`%s`" % info[k].get(n, "-")[:16] for k in ("pre1", "pre2", "post1", "post2"))))
    L += ["", "## Timings", "", "pre-1 %.0fs, pre-2 %.0fs, post-1 %.0fs, post-2 %.0fs" % tuple(info["secs"]), "",
          "## English checks on the layered clone", ""]
    for name, code in info["checks"]:
        L.append("- `%s --check`: exit %s" % (name, code))
    L += ["", "## Result", ""]
    if info["problems"]:
        L.append("**FAIL**")
        L += ["", "```text"] + info["problems"] + ["```"]
    else:
        L.append("**PASS**: the six English artifacts are byte-identical before and after the layer, and each pair of "
                 "builds is reproducible.")
    return "\n".join(L) + "\n"


TEST_GLOB = os.path.join("lessons", "book", "test_*.py")
ENGLISH_LAYER_MARK = "English layer (tools/scratch_proof.py --tests)"    # the skip reason of a test that only runs here


def english_layer_tests(clone, env, timeout=900):
    """Run every test module of the layered English clone (BOOK_LANG unset, English names, English text). The tests that skip
    themselves in the Spanish checkout because they edit English text (@english_only) must RUN here: a skip here is a problem.
    Returns (rows, problems); a row is (module, exit code, seconds, last line)."""
    import glob
    rows, problems = [], []
    for path in sorted(glob.glob(os.path.join(clone, TEST_GLOB))):
        name = os.path.basename(path)
        code, out, secs = run([PY, os.path.join("lessons", "book", name), "-v"], clone, timeout, env)
        lines = [l for l in out.splitlines() if l.strip()]
        rows.append((name, code, secs, lines[-1] if lines else ""))
        if code != 0:
            problems.append("English layer: %s exit %s\n%s" % (name, code, "\n".join(lines[-12:])))
        if ENGLISH_LAYER_MARK in out:
            problems.append("English layer: %s skipped tests that must run here (%s)" % (name, ENGLISH_LAYER_MARK))
    if not rows:
        problems.append("English layer: no test module found in the clone")
    return rows, problems


def tests_main():
    sha = config_value("english_commit")
    english = config_value("english_clone_path")
    clone = os.path.join(SCRATCH, "english")
    layer = layer_files()
    prepare_clone(english, sha, clone)
    apply_layer(ROOT, clone, layer)
    rows, problems = english_layer_tests(clone, english_layer_env())
    for name, code, secs, last in rows:
        print("%-28s exit %-3s %5.0fs  %s" % (name, code, secs, last))
    print("PASS" if not problems else "FAIL: %d problem(s)\n%s" % (len(problems), "\n".join(problems)))
    return 0 if not problems else 1


def main(argv):
    if "--layer" in argv:
        print("\n".join(layer_files()))
        return 0
    if "--tests" in argv:
        return tests_main()
    sha = config_value("english_commit")
    english = config_value("english_clone_path")
    clone = os.path.join(SCRATCH, "english")
    layer = layer_files()
    info = {"sha": sha, "layer": layer, "problems": [], "checks": [], "secs": []}
    prepare_clone(english, sha, clone)
    env = english_env()
    for tag in ("pre1", "pre2"):
        out_dir = os.path.join(SCRATCH, tag)
        probs, secs = build_round(clone, out_dir, env=env)
        info["problems"] += ["%s: %s" % (tag, p) for p in probs]
        info["secs"].append(secs)
        info[tag] = hash_dir(out_dir)
        print("%s built in %.0fs" % (tag, secs), flush=True)
    apply_layer(ROOT, clone, layer)
    for tag in ("post1", "post2"):
        out_dir = os.path.join(SCRATCH, tag)
        probs, secs = build_round(clone, out_dir, env=env)
        info["problems"] += ["%s: %s" % (tag, p) for p in probs]
        info["secs"].append(secs)
        info[tag] = hash_dir(out_dir)
        print("%s built in %.0fs" % (tag, secs), flush=True)
    for name, args in CHECKS:
        code, out, _ = run([PY] + args, clone, 900, env)
        info["checks"].append((name, code))
        if code != 0:
            info["problems"].append("English %s --check failed:\n%s" % (name, "\n".join(out.strip().splitlines()[-8:])))
    info["problems"] += compare("pre-1", info["pre1"], "pre-2", info["pre2"])
    info["problems"] += compare("post-1", info["post1"], "post-2", info["post2"])
    info["problems"] += compare("pre-1", info["pre1"], "post-1", info["post1"])
    info["problems"] += ["unexpected change in clone: %s" % c for c in unexpected_changes(clone, set(layer))]
    with open(REPORT, "w", encoding="utf-8") as f:
        f.write(render(info))
    print("PASS" if not info["problems"] else "FAIL: %d problem(s); see %s" % (len(info["problems"]), REPORT))
    return 0 if not info["problems"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
