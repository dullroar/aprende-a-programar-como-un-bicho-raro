#!/usr/bin/env python3
"""Run the English baseline gates and write translation/baseline.md.

Each gate is run as its own subprocess with a timeout. The report lists the
toolchain versions, every command, its exit code and the tail of its output,
and states honestly which gates failed or could not run.

Usage:
    python3 tools/baseline.py            # run all gates, write translation/baseline.md
    python3 tools/baseline.py --only N   # run only gate index N (0-based), print result
"""
import argparse
import os
import shutil
import subprocess
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPORT = os.path.join(ROOT, "translation", "baseline.md")
WORK = os.path.join(ROOT, "translation", "work", "baseline")

PY = "python3"
GATES = [
    ("book-check", [PY, "lessons/book/build.py", "--check"], 600),
    ("study-guides-check", [PY, "lessons/study-guides/build.py", "--check"], 600),
    ("curriculum-check", [PY, "lessons/curriculum/build.py", "--check"], 600),
    ("test_cs", [PY, "lessons/book/test_cs.py"], 600),
    ("test_study_guides", [PY, "lessons/book/test_study_guides.py"], 600),
    ("test_curriculum", [PY, "lessons/book/test_curriculum.py"], 600),
    ("test_editorial", [PY, "lessons/book/test_editorial.py"], 600),
    ("test_repo_links", [PY, "lessons/book/test_repo_links.py"], 600),
    ("test_repo_identity", [PY, "lessons/book/test_repo_identity.py"], 600),
    ("check-diagrams", [PY, "lessons/book/build.py", "--check-diagrams"], 900),
    ("test_pdf_lint", [PY, "lessons/book/test_pdf_lint.py"], 900),
    (
        "release-book",
        [PY, "lessons/book/build.py", "--release", "--artifacts-dir", "translation/work/baseline/release"],
        1200,
    ),
    (
        "release-study-guides",
        [PY, "lessons/study-guides/build.py", "--release", "--artifacts-dir", "translation/work/baseline/release"],
        1200,
    ),
    (
        "release-curriculum",
        [PY, "lessons/curriculum/build.py", "--release", "--artifacts-dir", "translation/work/baseline/release"],
        1200,
    ),
]

TOOLS = [
    ("python3", ["python3", "--version"]),
    ("pandoc", ["pandoc", "--version"]),
    ("node", ["node", "--version"]),
    ("npm", ["npm", "--version"]),
    ("java", ["java", "-version"]),
    ("git", ["git", "--version"]),
]


def tool_version(cmd):
    if shutil.which(cmd[0]) is None:
        return "NOT INSTALLED"
    try:
        p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
    except Exception as exc:  # pragma: no cover
        return "error: %s" % exc
    out = (p.stdout + p.stderr).strip().splitlines()
    return out[0] if out else "(no output)"


def pip_versions():
    try:
        p = subprocess.run(
            [sys.executable, "-m", "pip", "list", "--format=freeze"],
            capture_output=True, text=True, timeout=60,
        )
    except Exception:
        return []
    wanted = ("weasyprint", "pyyaml", "pytest", "jsonschema", "polib", "markdown-it-py", "pillow", "pypdf", "pymupdf")
    return [l for l in p.stdout.splitlines() if l.split("==")[0].lower() in wanted]


def run_gate(name, cmd, timeout):
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    t0 = time.time()
    try:
        p = subprocess.run(cmd, cwd=ROOT, capture_output=True, text=True, timeout=timeout, env=env)
        code, out = p.returncode, p.stdout + p.stderr
    except subprocess.TimeoutExpired as exc:
        code = "timeout"
        out = ((exc.stdout or b"").decode("utf-8", "replace") if isinstance(exc.stdout, bytes) else (exc.stdout or ""))
        out += "\n[timed out after %ss]" % timeout
    return code, out, time.time() - t0


def tail(text, n=12):
    lines = [l for l in text.strip().splitlines() if l.strip()]
    return "\n".join(lines[-n:])


def render(results):
    lines = ["# English baseline gates", ""]
    lines.append("Run by `python3 tools/baseline.py` against the pinned English tree (see `translation/source.json`).")
    lines.append("Nothing here was loosened or skipped. A non-zero exit code is recorded as a failure, not hidden.")
    lines += ["", "## Toolchain", ""]
    for name, cmd in TOOLS:
        lines.append("- %s: %s" % (name, tool_version(cmd)))
    for l in pip_versions():
        lines.append("- pip: %s" % l)
    for var in ("MERMAID_CHROME", "MERMAID_NO_SANDBOX"):
        lines.append("- env %s: %s" % (var, os.environ.get(var, "(unset)")))
    lines += ["", "## Results", "", "| # | gate | command | exit | seconds |", "|---|------|---------|------|---------|"]
    for i, (name, cmd, code, out, secs) in enumerate(results):
        lines.append("| %d | %s | `%s` | %s | %.1f |" % (i, name, " ".join(cmd), code, secs))
    failed = [r for r in results if r[2] != 0]
    lines += ["", "## Summary", ""]
    lines.append("%d of %d gates exit 0; %d did not." % (len(results) - len(failed), len(results), len(failed)))
    if failed:
        lines.append("")
        lines.append("Failing gates: " + ", ".join("%s (exit %s)" % (r[0], r[2]) for r in failed) + ".")
    lines += ["", "## Honest notes", ""]
    lines.append("- Exit codes are the only pass/fail signal used here; warnings in the output tails are recorded, not judged.")
    lines.append("- The diagram gate may answer from the on-disk render cache (`from cache`); the log says how many diagrams were drawn now.")
    lines.append("- Not covered: the per-language challenge programs under `src/` and `sandbox-gate.yml` (they need Java and many other runtimes). Java is NOT INSTALLED here if listed so above.")
    lines.append("- Full logs are in `translation/work/baseline/` (git-ignored); regenerate with `python3 tools/baseline.py`.")
    lines.append("- The release builds write PDFs and EPUBs under `translation/work/baseline/release/`, not into the tree, so frozen files are untouched.")
    lines += ["", "## Output tails", ""]
    for name, cmd, code, out, secs in results:
        lines += ["### %s (exit %s)" % (name, code), "", "```text", tail(out), "```", ""]
    return "\n".join(lines).rstrip() + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", type=int, default=None)
    args = ap.parse_args()
    os.makedirs(WORK, exist_ok=True)
    selected = list(enumerate(GATES))
    if args.only is not None:
        selected = [selected[args.only]]
    results = []
    for i, (name, cmd, timeout) in selected:
        code, out, secs = run_gate(name, cmd, timeout)
        results.append((name, cmd, code, out, secs))
        with open(os.path.join(WORK, "%02d-%s.log" % (i, name)), "w", encoding="utf-8") as fh:
            fh.write(out)
        print("%02d %-22s exit=%s %.1fs" % (i, name, code, secs), flush=True)
    if args.only is None:
        with open(REPORT, "w", encoding="utf-8") as fh:
            fh.write(render(results))
        print("wrote", os.path.relpath(REPORT, ROOT))
    else:
        print(tail(results[0][3], 30))
    return 0


if __name__ == "__main__":
    sys.exit(main())
