#!/usr/bin/env python3
"""release_report: the evidence page of a release candidate (plan 7.2, 9).

One Markdown file that answers "what was run, with what, and did it pass?":

  * the edition and the pinned English commit;
  * toolchain versions (python3, pandoc, node, npm, java, git);
  * every recorded command with its exit code and duration;
  * the hash manifest result (translation/locked-code.sha256 against the tree and the English clone);
  * coverage: segments per PO file (accepted, fuzzy, untranslated), files without a PO;
  * reviewer model IDs: the configured roles plus every model that appears in the ledger and the findings.

The report ends with a verdict. OK needs: at least one recorded command, every exit code 0, a clean hash
manifest, every authored file with a PO, no fuzzy or untranslated segment, and a model ID for the translator
and the in-loop reviewer. Anything else is NOT READY and the report lists each reason. Nothing is
published, tagged or pushed.

Usage:
  python3 -I tools/release_report.py record --out FILE [--name NAME] [--timeout S] -- CMD [ARGS...]
        run CMD, append {name, argv, exit, seconds} to the run record FILE (a JSON list), keep CMD's exit code
  python3 -I tools/release_report.py build [--record FILE] [--ledger FILE ...] [--findings FILE ...]
        [--out FILE] [--no-versions] [--no-lock]
        collect everything from the repository and write the report (default translation/release-report.md)
  python3 -I tools/release_report.py check FILE
        the report must hold its seven sections and its verdict line (exit 1 when not)

Exit codes: build 0 verdict OK, 1 NOT READY (the report is still written), 2 usage or unreadable input.
"""
import glob
import hashlib
import json
import os
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

DEFAULT_OUT = os.path.join(ROOT, "translation", "release-report.md")
DEFAULT_RECORD = os.path.join(ROOT, "translation", "work", "release", "run-record.json")
SECTIONS = ("Edition", "Toolchain", "Commands", "Hash manifest", "Coverage", "Reviewer models", "Verdict")
VERDICT_OK = "VERDICT: OK"
VERDICT_BAD = "VERDICT: NOT READY"
TOOLS = (("python3", ["python3", "--version"]), ("pandoc", ["pandoc", "--version"]),
         ("node", ["node", "--version"]), ("npm", ["npm", "--version"]),
         ("java", ["java", "-version"]), ("git", ["git", "--version"]))
ROLE_KEYS = ("translator", "in_loop_reviewer")
OPTIONAL_ROLE_KEYS = ("cross_vendor_review",)


class ReportError(Exception):
    """Input that cannot be trusted (unreadable record, bad JSON). Fails closed: no report is written."""


# ------------------------------------------------------------------------------------------ readers

def read_jsonl(path):
    rows = []
    with open(path, encoding="utf-8") as f:
        for n, line in enumerate(f, 1):
            if not line.strip():
                continue
            try:
                obj = json.loads(line)
            except ValueError as e:
                raise ReportError("%s line %d: not JSON (%s)" % (path, n, e)) from None
            if not isinstance(obj, dict):
                raise ReportError("%s line %d: not a JSON object" % (path, n))
            rows.append(obj)
    return rows


def read_record(path):
    """The run record: a JSON list of {name, argv, exit, seconds}. A missing file is an empty record."""
    if not os.path.isfile(path):
        return []
    try:
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
    except ValueError as e:
        raise ReportError("%s: not JSON (%s)" % (path, e)) from None
    if not isinstance(data, list):
        raise ReportError("%s: the run record must be a JSON list" % path)
    for i, row in enumerate(data):
        if not isinstance(row, dict) or not isinstance(row.get("argv"), list) or "exit" not in row:
            raise ReportError("%s row %d: needs argv (list) and exit" % (path, i))
    return data


def tool_versions(tools=TOOLS):
    import shutil
    out = {}
    for name, cmd in tools:
        if shutil.which(cmd[0]) is None:
            out[name] = "NOT INSTALLED"
            continue
        try:
            p = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            lines = (p.stdout + p.stderr).strip().splitlines()
            out[name] = lines[0] if lines else "(no output)"
        except (OSError, subprocess.SubprocessError) as e:
            out[name] = "error: %s" % e
    return out


def lock_result(root=ROOT):
    """The hash manifest against the tree and the pinned English clone."""
    import inventory
    import lock_code
    res = {"entries": 0, "manifest_sha256": "", "problems": []}
    try:
        entries = lock_code.load_manifest(root)
    except lock_code.LockError as e:
        res["problems"].append(str(e))
        return res
    res["entries"] = len(entries)
    with open(os.path.join(root, lock_code.MANIFEST), "rb") as f:
        res["manifest_sha256"] = hashlib.sha256(f.read()).hexdigest()
    res["problems"] += lock_code.tree_problems(root, entries)
    try:
        res["problems"] += lock_code.clone_problems(inventory.read_config(root), entries)
    except lock_code.LockError as e:
        res["problems"].append("CLONE-UNREACHABLE  %s" % e)
    return res


def coverage(po_root, authored):
    """Per authored file: segments by PO state. `authored` is the list of repo-relative Markdown paths."""
    import apply as apply_mod
    files, missing = {}, []
    for rel in authored:
        path = apply_mod.po_path_for(rel, po_root)
        if not os.path.isfile(path):
            missing.append(rel)
            continue
        po = apply_mod.load_po(path)
        c = {"accepted": 0, "fuzzy": 0, "untranslated": 0}
        for e in po:
            if "fuzzy" in e.flags:
                c["fuzzy"] += 1
            elif e.msgstr.strip():
                c["accepted"] += 1
            else:
                c["untranslated"] += 1
        files[rel] = c
    return {"files": files, "missing_po": missing}


def models_from(ledger_rows, findings_rows, config):
    """Every model ID with where it was seen. Roles come from CONFIG, usage from the ledger and findings."""
    seen = {}

    def add(model, role):
        if model:
            seen.setdefault(model, {}).setdefault(role, 0)
            seen[model][role] += 1

    for r in ledger_rows:
        if r.get("kind") == "segment":
            add(r.get("translator_model"), "translator")
        elif r.get("kind") == "disposition":
            add(r.get("adjudicator_model"), "adjudicator")
        elif r.get("kind") == "finding":
            add((r.get("finding") or {}).get("reviewer_model"), "reviewer")
    for r in findings_rows:
        add(r.get("reviewer_model"), "reviewer")
    roles = {k: config.get(k, "") for k in ROLE_KEYS + OPTIONAL_ROLE_KEYS}
    return {"roles": roles, "seen": seen}


def ledger_stats(ledger_rows):
    st = {"segments": 0, "by_status": {}, "input_tokens": 0, "output_tokens": 0, "findings": 0, "dispositions": 0}
    for r in ledger_rows:
        k = r.get("kind")
        if k == "segment":
            st["segments"] += 1
            s = r.get("status", "?")
            st["by_status"][s] = st["by_status"].get(s, 0) + 1
            tk = r.get("tokens") or {}
            st["input_tokens"] += int(tk.get("input", 0))
            st["output_tokens"] += int(tk.get("output", 0))
        elif k == "finding":
            st["findings"] += 1
        elif k == "disposition":
            st["dispositions"] += 1
    return st


# ------------------------------------------------------------------------------------------ the report

def totals(cov):
    t = {"accepted": 0, "fuzzy": 0, "untranslated": 0}
    for c in cov["files"].values():
        for k in t:
            t[k] += c[k]
    t["segments"] = sum(t[k] for k in ("accepted", "fuzzy", "untranslated"))
    return t


def verdict_reasons(data):
    """Why the release is not ready. An empty list means ready."""
    why = []
    cmds = data["commands"]
    if not cmds:
        why.append("no command was recorded (the report is evidence of runs, and there are none)")
    for c in cmds:
        if c.get("exit") != 0:
            why.append("command %s exited %s" % (c.get("name") or " ".join(c["argv"]), c.get("exit")))
    lock = data["lock"]
    if lock is None:
        why.append("the hash manifest was not checked")
    else:
        if not lock["entries"]:
            why.append("the hash manifest has no entries")
        for p in lock["problems"][:10]:
            why.append("hash manifest: %s" % p)
        if len(lock["problems"]) > 10:
            why.append("hash manifest: %d more problem(s)" % (len(lock["problems"]) - 10))
    cov = data["coverage"]
    if not cov["files"] and not cov["missing_po"]:
        why.append("coverage is empty: no authored file was examined")
    if cov["missing_po"]:
        why.append("%d authored file(s) have no PO" % len(cov["missing_po"]))
    t = totals(cov)
    if t["fuzzy"]:
        why.append("%d fuzzy segment(s)" % t["fuzzy"])
    if t["untranslated"]:
        why.append("%d untranslated segment(s)" % t["untranslated"])
    roles = data["models"]["roles"]
    for k in ROLE_KEYS:
        if not roles.get(k):
            why.append("no model ID recorded for %s" % k)
    return why


def pct(a, b):
    return "n/a" if not b else "%.1f%%" % (100.0 * a / b)


def md_cell(text):
    return str(text).replace("|", "\\|").replace("\n", " ")


def render(data):
    """data: edition, english_sha, language, versions, commands, lock, coverage, models, ledger, date."""
    L = ["# Release report", ""]
    L += ["Generated by `python3 tools/release_report.py`. Nothing was published, tagged or pushed.", ""]
    L += ["## Edition", ""]
    L += ["- Edition: %s" % data["edition"], "- Language tag: %s" % data["language"],
          "- Pinned English commit: `%s`" % data["english_sha"], "- Date: %s" % data["date"], ""]
    L += ["## Toolchain", ""]
    if data["versions"] is None:
        L.append("- (not collected)")
    else:
        for k in sorted(data["versions"]):
            L.append("- %s: %s" % (k, data["versions"][k]))
    L += ["", "## Commands", ""]
    if not data["commands"]:
        L.append("No command was recorded.")
    else:
        L += ["| # | name | command | exit | seconds |", "|---|------|---------|------|---------|"]
        for i, c in enumerate(data["commands"], 1):
            L.append("| %d | %s | `%s` | %s | %.1f |" % (i, md_cell(c.get("name", "")), md_cell(" ".join(c["argv"])),
                                                         c.get("exit"), float(c.get("seconds", 0))))
        bad = [c for c in data["commands"] if c.get("exit") != 0]
        L += ["", "%d of %d commands exited 0." % (len(data["commands"]) - len(bad), len(data["commands"]))]
    L += ["", "## Hash manifest", ""]
    lock = data["lock"]
    if lock is None:
        L.append("Not checked.")
    else:
        L.append("- Manifest: `translation/locked-code.sha256`, %d entries, sha256 `%s`" % (lock["entries"], lock["manifest_sha256"]))
        L.append("- Result: %s" % ("PASS (tree and English clone agree)" if not lock["problems"]
                                   else "FAIL (%d problem(s))" % len(lock["problems"])))
        for p in lock["problems"][:20]:
            L.append("  - `%s`" % p)
    L += ["", "## Coverage", ""]
    cov = data["coverage"]
    t = totals(cov)
    L.append("- Authored files with a PO: %d; without a PO: %d" % (len(cov["files"]), len(cov["missing_po"])))
    L.append("- Segments: %d; accepted %d (%s), fuzzy %d, untranslated %d" % (
        t["segments"], t["accepted"], pct(t["accepted"], t["segments"]), t["fuzzy"], t["untranslated"]))
    st = data["ledger"]
    L.append("- Ledger: %d segment row(s), %d finding(s), %d disposition(s); tokens in %d, out %d" % (
        st["segments"], st["findings"], st["dispositions"], st["input_tokens"], st["output_tokens"]))
    if st["by_status"]:
        L.append("- Ledger statuses: " + ", ".join("%s %d" % (k, v) for k, v in sorted(st["by_status"].items())))
    incomplete = sorted((f, c) for f, c in cov["files"].items() if c["fuzzy"] or c["untranslated"])
    if incomplete or cov["missing_po"]:
        L += ["", "Files not fully translated:", ""]
        for f, c in incomplete[:30]:
            L.append("- `%s`: %d fuzzy, %d untranslated of %d" % (f, c["fuzzy"], c["untranslated"],
                                                                 c["accepted"] + c["fuzzy"] + c["untranslated"]))
        for f in cov["missing_po"][:30]:
            L.append("- `%s`: no PO" % f)
        more = len(incomplete) + len(cov["missing_po"]) - 60
        if more > 0:
            L.append("- ... %d more" % more)
    L += ["", "## Reviewer models", ""]
    roles = data["models"]["roles"]
    for k in ROLE_KEYS + OPTIONAL_ROLE_KEYS:
        L.append("- %s: %s" % (k, roles.get(k) or "(not set)"))
    seen = data["models"]["seen"]
    L.append("")
    if not seen:
        L.append("No model appears in the ledger or the findings.")
    else:
        L += ["| model ID | seen as |", "|----------|---------|"]
        for m in sorted(seen):
            L.append("| %s | %s |" % (md_cell(m), ", ".join("%s x%d" % (r, n) for r, n in sorted(seen[m].items()))))
    why = verdict_reasons(data)
    L += ["", "## Verdict", ""]
    if why:
        L.append(VERDICT_BAD)
        L.append("")
        L += ["- " + w for w in why]
    else:
        L.append(VERDICT_OK)
    return "\n".join(L).rstrip() + "\n"


def check_report(text):
    """Problems with a finished report: a missing section, or a verdict line that is absent or doubled."""
    problems = []
    for s in SECTIONS:
        if "\n## %s\n" % s not in "\n" + text:
            problems.append("missing section: %s" % s)
    ok, bad = text.count(VERDICT_OK), text.count(VERDICT_BAD)
    if ok + bad != 1:
        problems.append("expected exactly one verdict line, found %d" % (ok + bad))
    return problems


# ------------------------------------------------------------------------------------------ collect and CLI

def collect(root=ROOT, record=None, ledgers=None, findings=None, versions=True, lock=True, cfg=None):
    import inventory
    import segment
    cfg = cfg if cfg is not None else inventory.read_config(root)
    if ledgers is None:
        ledgers = sorted(p for p in glob.glob(os.path.join(root, "translation", "ledger", "*.jsonl"))
                         if not p.endswith(".notes.jsonl"))
    ledger_rows = [r for p in ledgers for r in read_jsonl(p)]
    findings_rows = [r for p in (findings or []) for r in read_jsonl(p)]
    authored = segment.authored_files(root)
    return {
        "edition": cfg.get("edition_label", "?"), "language": cfg.get("language_tag", "?"),
        "english_sha": cfg.get("english_commit", "?"), "date": time.strftime("%Y-%m-%d", time.gmtime()),
        "versions": tool_versions() if versions else None,
        "commands": read_record(record or DEFAULT_RECORD),
        "lock": lock_result(root) if lock else None,
        "coverage": coverage(os.path.join(root, "translation", "po"), authored),
        "models": models_from(ledger_rows, findings_rows, cfg),
        "ledger": ledger_stats(ledger_rows),
    }


def cmd_record(args):
    if "--" not in args:
        print("record needs `-- CMD [ARGS...]`")
        return 2
    i = args.index("--")
    opts, argv = args[:i], args[i + 1:]
    if not argv or "--out" not in opts or opts.index("--out") + 1 >= len(opts):
        print("record needs --out FILE and a command after --")
        return 2
    out = opts[opts.index("--out") + 1]
    name = opts[opts.index("--name") + 1] if "--name" in opts and opts.index("--name") + 1 < len(opts) else argv[0]
    timeout = float(opts[opts.index("--timeout") + 1]) if "--timeout" in opts else 1800
    t0 = time.time()
    try:
        p = subprocess.run(argv, cwd=ROOT, timeout=timeout)
        code = p.returncode
    except subprocess.TimeoutExpired:
        code = "timeout"
    except OSError as e:
        print("cannot run %s: %s" % (argv[0], e))
        code = 127
    rows = read_record(out)
    rows.append({"name": name, "argv": argv, "exit": code, "seconds": round(time.time() - t0, 1)})
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        json.dump(rows, f, indent=1, ensure_ascii=False)
        f.write("\n")
    return 0 if code == 0 else 1


def cmd_build(args):
    def multi(name):
        vals = [args[i + 1] for i, a in enumerate(args[:-1]) if a == name]
        return vals or None

    def one(name, default):
        v = multi(name)
        return v[-1] if v else default
    known = {"--record", "--ledger", "--findings", "--out", "--no-versions", "--no-lock"}
    if [a for a in args if a.startswith("--") and a not in known]:
        print(__doc__.split("Exit codes")[0].rstrip())
        return 2
    try:
        data = collect(ROOT, one("--record", None), multi("--ledger"), multi("--findings"),
                       "--no-versions" not in args, "--no-lock" not in args)
    except (ReportError, OSError, ValueError) as e:
        print("release_report: %s" % e)
        return 2
    out = one("--out", DEFAULT_OUT)
    text = render(data)
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, "w", encoding="utf-8") as f:
        f.write(text)
    why = verdict_reasons(data)
    print("wrote %s: %s" % (os.path.relpath(out, ROOT), "OK" if not why else "NOT READY (%d reason(s))" % len(why)))
    for w in why[:10]:
        print("  - " + w)
    return 0 if not why else 1


def main(argv):
    args = argv[1:]
    if not args or args[0] not in ("record", "build", "check"):
        print(__doc__.split("Exit codes")[0].rstrip())
        return 2
    if args[0] == "record":
        return cmd_record(args[1:])
    if args[0] == "check":
        if len(args) != 2:
            print("check needs FILE")
            return 2
        with open(args[1], encoding="utf-8") as f:
            probs = check_report(f.read())
        for p in probs:
            print("FAIL " + p)
        return 1 if probs else 0
    return cmd_build(args[1:])


if __name__ == "__main__":
    sys.exit(main(sys.argv))
