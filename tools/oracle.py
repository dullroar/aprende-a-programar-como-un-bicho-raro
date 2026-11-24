#!/usr/bin/env python3
"""Differential oracle for Part II code localization (plan 4.5.4, task S2-004).

Runs the English (pinned clone) and the Spanish version of an entry through the same runner
(the sandbox container for real runs), reduces both outputs to a language-neutral semantic
record, and requires equality. Words may differ; meaning and shape may not.

Verdicts: PASS, FAIL, NOT TESTED (with a reason). NOT TESTED is never upgraded to PASS.

Layers implemented here:
  1. smoke run + semantic record (cards, running totals, crossing card, final total, exit code,
     stdout/stderr separation, persisted bytes digest);
  2. record equality English vs Spanish;
  3. boundary properties on the record itself (stop only when total > 40; the first card over
     40 is kept; total of exactly 40 continues);
  4. planted-mutant self-test: the checks must reject a program that stops at `total >= 40`.
     An oracle that fails its self-test reports NOT TESTED for every family.

Runners are callables `runner(entry_dir, seed) -> RunResult`. `docker_runner` shells out to
sandbox/container/run-image.sh (host never runs example programs). If docker or the entry image
is absent, it raises NotTested and the verdict is NOT TESTED.

Usage:
  python3 -I tools/oracle.py --selftest
  python3 -I tools/oracle.py --entry src/forth --english ~/english-source [--seed N]
"""
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from dataclasses import dataclass, field

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CATEGORIES = ("Meetings", "Coding", "Debugging", "Learning")  # English words; the mapped Spanish word of a localized family is accepted (decision 11)
CATEGORIES_ES = ("Reuniones", "Programación", "Depuración", "Aprendizaje")
LIMIT = 40

CARD_RE = re.compile(r"^(Meetings|Coding|Debugging|Learning|Reuniones|Programación|Depuración|Aprendizaje)[\t ]+(\d+)[\t ]+(\d+)\b")
TOTAL_RE = re.compile(r"\btotal=(\d+)")
ENTRIES_RE = re.compile(r"\bentries=(\d+)")
COMMIT_RE = re.compile(r"committed|confirmad[oa]", re.I)


class NotTested(Exception):
    """The family cannot be run here; the report says NOT TESTED with this reason."""


@dataclass
class RunResult:
    stdout: str
    stderr: str = ""
    exit_code: int = 0
    files: dict = field(default_factory=dict)  # relative path -> bytes written by the run


def reduce_record(res: RunResult) -> dict:
    """Language-neutral semantic record of one run (plan 4.5.4)."""
    cards = []
    for line in res.stdout.splitlines():
        m = CARD_RE.match(line)
        if m:
            cards.append({"category": (CATEGORIES + CATEGORIES_ES).index(m.group(1)) % 4,
                          "hours": int(m.group(2)), "running": int(m.group(3))})
    total = None
    entries = None
    committed = False
    for line in res.stdout.splitlines():
        if line.startswith("#") or "total=" in line:
            t = TOTAL_RE.search(line)
            e = ENTRIES_RE.search(line)
            if t:
                total = int(t.group(1))
            if e:
                entries = int(e.group(1))
            if COMMIT_RE.search(line):
                committed = True
    crossing = next((c for c in cards if c["running"] > LIMIT), None)
    digest = {p: hashlib.sha256(b).hexdigest() for p, b in sorted(res.files.items())}
    return {
        "cards": cards,
        "crossing_card": crossing,
        "final_total": total if total is not None else (cards[-1]["running"] if cards else None),
        "cards_kept": entries if entries is not None else len(cards),
        "committed": committed,
        "exit_code": res.exit_code,
        "stdout_empty": not res.stdout.strip(),
        "stderr_empty": not res.stderr.strip(),
        "persisted": digest,
    }


def boundary_findings(rec: dict) -> list:
    """Properties every record must satisfy: stop only when total > 40, crossing card kept."""
    out = []
    cards = rec["cards"]
    run = 0
    for i, c in enumerate(cards):
        if run > LIMIT:
            out.append(f"card {i} exists after the total passed {LIMIT}")
        run += c["hours"]
        if c["running"] != run:
            out.append(f"card {i}: running total {c['running']}, expected {run}")
    if cards:
        if run <= LIMIT:
            out.append(f"stopped at {run}, which is not strictly greater than {LIMIT}")
        if rec["final_total"] != run:
            out.append(f"final total {rec['final_total']} differs from card sum {run}")
        if rec["crossing_card"] is None or rec["crossing_card"] != cards[-1]:
            out.append("the first card over 40 was not kept as the last card")
    return out


def compare_records(en: dict, es: dict) -> list:
    out = []
    for key in sorted(en):
        if en[key] != es.get(key):
            out.append(f"{key}: english={en[key]!r} spanish={es.get(key)!r}")
    return out


def judge(en_res: RunResult, es_res: RunResult, deterministic: bool) -> dict:
    """Verdict for one family. Equality is only demanded when the run is deterministic
    (a frozen seed, or an entry with no randomness); otherwise both records must satisfy
    the boundary properties and agree on the shape (non-card fields)."""
    en, es = reduce_record(en_res), reduce_record(es_res)
    findings = [f"english: {f}" for f in boundary_findings(en)]
    findings += [f"spanish: {f}" for f in boundary_findings(es)]
    if deterministic:
        findings += compare_records(en, es)
    else:
        shape = ("exit_code", "stdout_empty", "stderr_empty", "committed")
        findings += [f"{k}: english={en[k]!r} spanish={es[k]!r}" for k in shape if en[k] != es[k]]
    return {"verdict": "FAIL" if findings else "PASS", "findings": findings,
            "deterministic": deterministic}


# ---- planted-mutant self-test -------------------------------------------------------------

def _reference_run(hours, stop):
    """A tiny reference program: deal cards until stop(total) is true; print the card rows."""
    total, lines = 0, []
    for i, h in enumerate(hours):
        total += h
        lines.append(f"{CATEGORIES[i % 4]}\t{h}\t{total}")
        if stop(total):
            break
    lines.append(f"# committed entries={len(lines)} total={total}")
    return RunResult("\n".join(lines) + "\n")


CORRECT = lambda t: t > LIMIT      # noqa: E731
MUTANT_GE = lambda t: t >= LIMIT   # noqa: E731  (the planted defect)
MUTANT_LATE = lambda t: t > LIMIT + 10  # noqa: E731  (keeps dealing after 40)
BOUNDARY_HOURS = [10] * 8  # exactly 40 after four cards: must continue to 50


def selftest() -> list:
    """Return a list of problems; empty means the oracle can tell a mutant from the truth."""
    problems = []
    good = _reference_run(BOUNDARY_HOURS, CORRECT)
    if boundary_findings(reduce_record(good)):
        problems.append("correct reference rejected")
    for name, mut in (("total >= 40", MUTANT_GE), ("keeps going past 40", MUTANT_LATE)):
        bad = _reference_run(BOUNDARY_HOURS, mut)
        if not boundary_findings(reduce_record(bad)):
            problems.append(f"mutant '{name}' not rejected by boundary properties")
        if judge(good, bad, True)["verdict"] != "FAIL":
            problems.append(f"mutant '{name}' not rejected by differential comparison")
    return problems


# ---- real runner and entry point ----------------------------------------------------------

def docker_runner(entry_dir: str, seed=None) -> RunResult:
    """Run an entry in the sandbox container. Never runs the program on the host."""
    if shutil.which(os.environ.get("DOCKER", "docker")) is None:
        raise NotTested("docker not available in this session")
    script = os.path.join(ROOT, "sandbox", "container", "run-image.sh")
    if not os.path.isfile(os.path.join(entry_dir, "Dockerfile")):
        raise NotTested(f"{os.path.basename(entry_dir)} has no Dockerfile (no entry image)")
    env = dict(os.environ)
    if seed is not None:
        env["SEED"] = str(seed)
    p = subprocess.run([script, entry_dir], capture_output=True, text=True, env=env, timeout=600)
    if p.returncode == 2:
        raise NotTested("sandbox refused to build or run: " + p.stderr.strip()[:200])
    return RunResult(p.stdout, p.stderr, p.returncode)


def run_family(english_dir, spanish_dir, runner=docker_runner, seed=None) -> dict:
    """Self-test first; then both runs through the same runner. Never raises on NOT TESTED."""
    st = selftest()
    if st:
        return {"verdict": "NOT TESTED", "reason": "oracle self-test failed: " + "; ".join(st)}
    try:
        en = runner(english_dir, seed)
        es = runner(spanish_dir, seed)
    except NotTested as e:
        return {"verdict": "NOT TESTED", "reason": str(e)}
    return judge(en, es, deterministic=seed is not None)


def main(argv):
    if "--selftest" in argv:
        problems = selftest()
        print("selftest: " + ("PASS (mutants rejected)" if not problems else "FAIL: " + "; ".join(problems)))
        return 1 if problems else 0
    if "--entry" in argv:
        entry = argv[argv.index("--entry") + 1]
        eng = argv[argv.index("--english") + 1] if "--english" in argv else None
        seed = argv[argv.index("--seed") + 1] if "--seed" in argv else None
        if not eng:
            print("--english <pinned clone> required", file=sys.stderr)
            return 2
        rep = run_family(os.path.join(eng, entry), os.path.join(ROOT, entry), seed=seed)
        print(json.dumps(rep, indent=2, ensure_ascii=False))
        return 0 if rep["verdict"] == "PASS" else (3 if rep["verdict"] == "NOT TESTED" else 1)
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
