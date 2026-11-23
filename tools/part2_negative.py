#!/usr/bin/env python3
"""part2_negative: Part II negative controls (plan Appendix A.2). Disposable fixtures; each must fail FOR THE STATED REASON.

  python3 -I tools/part2_negative.py            run every control and fixture; print passed/planned; exit 0 only if all pass
  python3 -I tools/part2_negative.py --list     print the catalog (row, id, detector, expected reason)

A fixture is a planted defect fed to the detector the plan names. It passes only when the detector reports a problem whose text
contains the expected reason (`expect`); a missing dependency or an unrelated error is a failure of the fixture, not a pass.
Every row has a CONTROL (the clean input) that must report nothing, so a detector that always fails proves nothing.

Rows whose detector is not built yet (tools/impact.py, the idempotence gate for Part II, the workflow allowlist review) are listed as
DEFERRED with the task that owes them; they are not counted as passed. Coverage is "passed/planned" over the rows that can run now,
and the deferred rows are printed beside it, so the gate can never claim full coverage.

Exit codes: 0 all planned fixtures failed for their stated reason and every control is clean; 1 otherwise; 2 usage.
"""
import contextlib
import os
import re
import subprocess
import sys
import tempfile
from collections import namedtuple

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

import loc_apply  # noqa: E402
import lock_code  # noqa: E402
import negative  # noqa: E402
import oracle  # noqa: E402
import part2_inv as p2  # noqa: E402

Row = namedtuple("Row", "id row title detector expect control run")
Deferred = namedtuple("Deferred", "row title detector owner")

DEFERRED = [
    Deferred(10, "A hostile demo becomes an unrestricted CI job, or scope-check.sh is relaxed",
             "workflow and sandbox allowlist review", "a later S3 sandbox task (no automated reviewer exists yet)"),
    Deferred(12, "Re-running generation changes a file", "idempotence gate for Part II generation",
             "S6 gate tasks (the English-side gate exists; no Part II gate yet)"),
    Deferred(14, "A synthetic upstream delta (new paragraph, renamed symbol, new API)", "tools/impact.py",
             "tools/impact.py is not built"),
]


def msgs(findings):
    return ["%s %s %s" % (f.inv, f.where, f.msg) for f in findings]


def has(problems, expect):
    """The expected reason as a whole word: "I6" must not be satisfied by "I16"."""
    return any(re.search(r"(?<![\w])%s(?![\w])" % re.escape(expect), p) for p in problems)


# ---------------------------------------------------------------------------------------------- row 1: the stop predicate

HOURS = [10] * 8


def stop_problems(stop):
    return oracle.boundary_findings(oracle.reduce_record(oracle._reference_run(HOURS, stop)))


def row1_control():
    return stop_problems(oracle.CORRECT)


def row1_ge():
    return stop_problems(oracle.MUTANT_GE)


def row1_differential():
    good = oracle._reference_run(HOURS, oracle.CORRECT)
    bad = oracle._reference_run(HOURS, oracle.MUTANT_GE)
    return oracle.judge(good, bad, True)["findings"]


# ---------------------------------------------------------------------------------------------- row 2 and 5: code tokens

CS = 'var cards = new List<int>();\ncards.Add(40);\n'
CS_BAD = 'var cards = new Lista<int>();\ncards.Add(40);\n'
SQL = "BEGIN;\nINSERT INTO t VALUES (1);\nCOMMIT;\n"
SQL_BAD = SQL.replace("COMMIT", "CONFIRMAR")
RX = "(?<total>\\d+) hours\n"
RX_BAD = "(?<suma>\\d+) hours\n"
M4 = "define(`total_hours', `40')\n"
M4_BAD = "definir(`total_hours', `40')\n"
XAML = '<TextBlock Text={Binding Total}/>\n'
XAML_BAD = '<TextBlock Text={Binding Suma}/>\n'


def code(path, en, es, reserved=()):
    return msgs(p2.i28_i29_code(path, en, es, [], reserved=reserved))


# ---------------------------------------------------------------------------------------------- row 3: I30 guard

TOK = {"List": ["csharp"]}


def prose(text):
    return msgs(p2.i30_unfenced("lessons/x.md", text, TOK))


# ---------------------------------------------------------------------------------------------- row 4: stale symbols

REC = [{"old": "total", "new": "suma", "path": "src/a.py"}]


def stale(text):
    return msgs(p2.i28_stale(REC, {"src/a.py": "suma = 0\n", "src/README.md": text}))


# ---------------------------------------------------------------------------------------------- row 7: line anchors

SCOPE = {"fam": {"status": "localizing", "never": False}}
FAMS = {"a.sh": "fam"}
REG = {"shell": {"status": "not-extracted", "tokens": []}}
SH = "# add up\necho total\n# done\n"


def apply_comment(msgstr):
    with tempfile.TemporaryDirectory() as root:
        with open(os.path.join(root, "a.sh"), "w", encoding="utf-8", newline="") as fh:
            fh.write(SH)
        po = [{"kind": "L", "line": 1, "msgid": "# add up", "msgstr": msgstr}]
        try:
            loc_apply.apply_file(root, "a.sh", scope=SCOPE, families=FAMS, reg=REG, records=[], po=po, anchors=[])
        except loc_apply.Refused as e:
            return [str(e)]
        return []


# ---------------------------------------------------------------------------------------------- row 9: NOT TESTED


def absent(*_a, **_k):
    raise oracle.NotTested("compiler absent")


def row9():
    rep = oracle.run_family("en", "es", runner=absent)
    out = []
    if rep["verdict"] == "NOT TESTED":
        out.append("verdict NOT TESTED: " + rep["reason"])
    gate = p2.i31_oracle([{"path": "x"}], {"x": "fam"}, {"fam": rep["verdict"]})
    return out + msgs(gate)


def row9_control():
    ok = lambda d, seed=None: oracle._reference_run(HOURS, oracle.CORRECT)  # noqa: E731
    rep = oracle.run_family("en", "es", runner=ok, seed=1)
    return msgs(p2.i31_oracle([{"path": "x"}], {"x": "fam"}, {"fam": rep["verdict"]}))


# ---------------------------------------------------------------------------------------------- row 11: hook on a localized file

SCOPE_YAML = 'families:\n  "fam": {status: localizing}\n'


def git(cwd, *a):
    return subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@example.invalid", "-C", cwd] + list(a),
                          capture_output=True, text=True, check=True)


def hook_problems(with_entry):
    with tempfile.TemporaryDirectory() as root:
        def put(rel, text):
            p = os.path.join(root, rel)
            os.makedirs(os.path.dirname(p), exist_ok=True)
            with open(p, "w", encoding="utf-8", newline="") as fh:
                fh.write(text)

        old, new = "# add up\necho total\n", "# suma\necho total\n"
        put("translation/localization-scope.yaml", SCOPE_YAML)
        put("translation/part2/code-inventory.jsonl", '{"path": "src/a.sh", "family": "fam"}\n')
        put("src/a.sh", old)
        put(lock_code.MANIFEST, lock_code.format_manifest({"src/a.sh": lock_code.sha256_bytes(old.encode())}))
        put("translation/identifier-map.jsonl", "")
        git(root, "init", "-q")
        git(root, "add", "-A")
        git(root, "commit", "-q", "-m", "base")
        put("src/a.sh", new)
        put(lock_code.LOCALIZED, lock_code.format_manifest({"src/a.sh": lock_code.sha256_bytes(new.encode())}))
        if with_entry:
            put(os.path.join(lock_code.PO_CODE, "src/a.sh.po"), 'msgid "add up"\nmsgstr "suma"\n')
        git(root, "add", "-A")
        return lock_code.staged_violations(root, lock_code.load_manifest(root))


# ---------------------------------------------------------------------------------------------- delegation to Part I fixtures


def part1(ident):
    fx = next(f for f in negative.catalog() if f.id == ident)
    return negative.run_fixture(fx)


def via_part1(ident):
    def run():
        problems, err = part1(ident)
        if err:
            raise RuntimeError("Part I fixture %s is broken: %s" % (ident, err))
        return problems
    return run


def catalog():
    R = []

    def add(*a):
        R.append(Row(*a))

    add("stop-ge", 1, "total > 40 becomes >= 40 in the program's stop predicate", "oracle boundary property",
        "not strictly greater than 40", row1_control, row1_ge)
    add("stop-ge-differential", 1, "the same mutant against the correct run (planted-mutant self-test)", "oracle.judge",
        "english=", row1_control, row1_differential)
    add("dotnet-list", 2, ".NET List becomes Lista in real library use", "I29 with the protected-token registry",
        "I29", lambda: code("a.cs", CS, CS, ("List",)), lambda: code("a.cs", CS, CS_BAD, ("List",)))
    add("list-prose", 3, "an ordinary Spanish sentence writes List(...) as code outside backticks", "I30 false-positive guard",
        "I30", lambda: prose("Una lista de tarjetas y `List<int>` en código.\n"),
        lambda: prose("Una List<int> de tarjetas.\n"))
    add("stale-symbol", 4, "a variable is renamed in code but the old name stays in a README code span", "I28 stale-symbol sweep",
        "stale symbol", lambda: stale("Usa `suma` para el total.\n"), lambda: stale("Usa `total` para el total.\n"))
    add("sql-commit", 5, "SQL COMMIT becomes CONFIRMAR", "I29", "I29", lambda: code("a.sql", SQL, SQL, ("COMMIT",)),
        lambda: code("a.sql", SQL, SQL_BAD, ("COMMIT",)))
    add("regex-capture", 5, "a regex capture name is translated without a map entry", "I28", "I28",
        lambda: code("a.re", RX, RX), lambda: code("a.re", RX, RX_BAD))
    add("m4-macro", 5, "the m4 builtin define becomes definir", "I29", "I29", lambda: code("a.m4", M4, M4, ("define",)),
        lambda: code("a.m4", M4, M4_BAD, ("define",)))
    add("xaml-binding", 5, "a XAML binding property is translated without a map entry", "I28", "I28",
        lambda: code("a.xaml", XAML, XAML), lambda: code("a.xaml", XAML, XAML_BAD))
    add("yaml-key", 6, "a YAML key (front matter 'assurance') is translated", "schema invariant I6", "I6",
        lambda: [], via_part1("enum-key-translated"))
    add("comment-adds-line", 7, "a comment edit adds a line, so #L88 would show another statement",
        "line-preserving refusal in loc_apply", "not exactly one comment span", lambda: apply_comment("# suma"),
        lambda: apply_comment("# suma\n# una línea más"))
    add("mermaid-node-id", 8, "a Mermaid node ID is translated in one edge only", "Mermaid invariant I5", "I5",
        lambda: [], via_part1("node-id-translated"))
    add("mermaid-accdescr", 8, "accDescr is left in English", "Spanish accessible-text gate I9", "I9",
        lambda: [], via_part1("accdescr-english"))
    add("not-tested", 9, "a family is skipped because the compiler is absent", "oracle NOT TESTED plus I31",
        "NOT TESTED", row9_control, row9)
    add("unmapped-edit", 11, "a localized file is edited with no map or PO entry", "pre-commit hook (staged_violations)",
        "UNMAPPED", lambda: hook_problems(True), lambda: hook_problems(False))
    add("english-repo-link", 13, "a Spanish document links into the English repository", "link audit (category G)",
        "FOREIGN repository link", lambda: [], via_part1("link-to-english-repo"))
    return R


def judge(row):
    """(ok, detail): the control must be clean, and the fixture must fail with the expected reason."""
    try:
        c = row.control()
        if c:
            return False, "control is not clean: %s" % c[0]
        p = row.run()
    except Exception as e:  # a stale fixture is loud, never a pass
        return False, "fixture is broken: %s: %s" % (type(e).__name__, e)
    if not p:
        return False, "did not fail: the detector (%s) is disarmed" % row.detector
    if not has(p, row.expect):
        return False, "failed, but not for the stated reason %r: %s" % (row.expect, p[0])
    return True, p[0]


def run_all():
    results = [(r, *judge(r)) for r in catalog()]
    passed = sum(1 for _r, ok, _d in results if ok)
    return results, passed, len(results)


def main(argv):
    if "--list" in argv:
        for r in catalog():
            print("row %2d  %-22s %-38s expect %r  %s" % (r.row, r.id, r.detector, r.expect, r.title))
        for d in DEFERRED:
            print("row %2d  DEFERRED              %-38s owner: %s  %s" % (d.row, d.detector, d.owner, d.title))
        return 0
    if argv:
        print(__doc__, file=sys.stderr)
        return 2
    results, passed, planned = run_all()
    for r, ok, d in results:
        print("%s row %2d %-22s %s" % ("PASS" if ok else "FAIL", r.row, r.id, d))
    for d in DEFERRED:
        print("DEFERRED row %2d %s (detector: %s; owner: %s)" % (d.row, d.title, d.detector, d.owner))
    print("negative control run: %d/%d planned fixtures failing for their stated reason; %d A.2 rows deferred (not counted)"
          % (passed, planned, len(DEFERRED)))
    return 0 if passed == planned else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
