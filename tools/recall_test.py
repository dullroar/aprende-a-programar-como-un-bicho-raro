#!/usr/bin/env python3
"""tools/recall_test.py: seeded-fault recall test of the in-loop reviewer (plan 9.3, task P3-007).

Takes the translated units of the pilot files (units from English + PO, as tools/jury_packet.py builds them),
plants about 50 known faults in the Spanish of different units (the mutators of jury_packet: the 40-rule flip,
negation, swapped number, dropped clause, unapproved or mixed card category word (decision 11), wrong assurance label, wrong phase letter,
usted slip), adds clean controls, and asks the reviewer (translation/prompts/review.md, one unit per call) to
review each one. A fault is *caught* only when a schema-valid finding with exact-substring excerpts points at
the changed place of the Spanish (or, for a pure omission, says so). A finding elsewhere is not credit.

Pass bar (plan 9.3, CONFIG seeded_fault_recall_bar): recall on critical and major faults at or above the bar AND
every 40-rule flip caught. Below the bar the reviewer role is downgraded in loop/CONFIG.yaml and the Jury weight
is raised (the report says so; `--apply-config` writes the CONFIG key).

Usage:
  python3 -I tools/recall_test.py --run [--faults 50] [--controls 10] [--seed 7] [--model sonnet] [--workers 4]
                                  [--max-usd 3.0] [--out translation/reviews/pilot-recall.md]
  python3 -I tools/recall_test.py --rescore            re-score the saved raw replies, no model call
Raw replies are kept in translation/work/recall/replies.jsonl (git-ignored); a rerun resumes from them.
"""
from __future__ import annotations

import argparse
import concurrent.futures
import difflib
import hashlib
import json
import os
import random
import re
import subprocess
import threading
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
import jury_packet as jp  # noqa: E402

PROMPT_PATH = os.path.join(ROOT, "translation", "prompts", "review.md")
WORK = os.path.join(ROOT, "translation", "work", "recall")
REPLIES = os.path.join(WORK, "replies.jsonl")
FAULTS_PATH = os.path.join(WORK, "faults.json")
DEFAULT_OUT = os.path.join(ROOT, "translation", "reviews", "pilot-recall.md")
MAJOR_PLUS = ("critical", "major")
SEV_RANK = {"critical": 0, "major": 1, "minor": 2, "suggestion": 3}
OMISSION_CATEGORIES = ("omission", "meaning", "structure", "safety-warning")
HOUSE_RULES = [
    "tú imperative for instructions; never usted or vos",
    "¿? and ¡! paired; straight quotes; sentence-case headings",
    "logic words are exact: si y solo si, más de, al menos, puede, debe",
    "the total must be strictly greater than 40 to stop (más de 40); exactly 40 continues",
    "assurance labels: garantizado, permitido por la implementación, aprovechado por accidente",
    "code, identifiers, paths, URLs never translated; card categories are localized (Meetings/Reuniones, Coding/Programación, Debugging/Depuración, Learning/Aprendizaje): one form per file, no other spelling",
    "do not add, drop or reorder content; keep every warning",
]


# ---------------------------------------------------------------------------------------------- faults

# Decision 11: both the English and the approved Spanish word are valid; the seeded fault is a word that is neither.
CATEGORY_WORDS = {"Meetings": "Reunión", "Coding": "Programacion", "Debugging": "Depuracion", "Learning": "Aprendizage",
                  "Reuniones": "Reunión", "Programación": "Programacion", "Depuración": "Depuracion", "Aprendizaje": "Aprendizage"}


def m_category_in_span(u, ctx):
    """Replace a card category inside a longer code span (`Meetings 15 15`) by an unapproved spelling: the pilot files
    print categories inside terminal output, where jury_packet.m_identifier (whole-span match) finds nothing."""
    s = u["spanish"]
    for m in re.finditer(r"`[^`\n]*`", s):
        for old, new in CATEGORY_WORDS.items():
            j = m.group(0).find(old)
            if j >= 0:
                i = m.start() + j
                return s[:i] + new + s[i + len(old):], new, "dnt-violation", "major"
    return None


def m_phase_letter_after_fase(u, ctx):
    """Replace the letter in 'fase B' or 'fase en B' by the next phase letter (the base mutator needs 'Fase X')."""
    letters = ctx["phase_letters"]
    if len(letters) < 2:
        return None
    m = re.search(r"\b[Ff]ase (?:en )?(%s)\b" % "|".join(re.escape(x) for x in letters), u["spanish"])
    if not m or not jp._outside_code(u["spanish"], m.start()):
        return None
    new = letters[(letters.index(m.group(1)) + 1) % len(letters)]
    s = u["spanish"]
    return s[:m.start(1)] + new + s[m.end(1):], m.group(0)[:-1] + new, "phase-acronym", "critical"


def m_code_category(u, ctx):
    """Code unit: respell one localized card category on a code line (neither the English nor the approved word)."""
    for a, b, ln in jp._code_lines(u["spanish"]):
        for old in ("Reuniones", "Programación", "Depuración", "Aprendizaje"):
            j = ln.find(old)
            if j >= 0:
                new = CATEGORY_WORDS[old]
                return u["spanish"][:a + j] + new + u["spanish"][a + j + len(old):], new, "dnt-violation", "major"
    return None


def m_code_unwiden(u, ctx):
    """Code unit: put the narrow ASCII class back where G1 widened it to accented letters (a regex that no longer matches)."""
    for a, b, ln in jp._code_lines(u["spanish"]):
        j = ln.find("A-Za-zÁÉÍÓÚáéíóúñ")
        if j >= 0:
            return (u["spanish"][:a + j] + "A-Za-z" + u["spanish"][a + j + len("A-Za-zÁÉÍÓÚáéíóúñ"):],
                    "A-Za-z", "code-semantics", "critical")
    return None


CODE_FAULTS = tuple(jp.CODE_MUTATORS) + (("code_category", m_code_category), ("code_unwiden", m_code_unwiden))
MUTATORS = tuple(jp.MUTATORS) + (("category_in_span", m_category_in_span),
                                 ("phase_letter_after_fase", m_phase_letter_after_fase))


def changed_span(original, mutated):
    """(start, end) of the changed place in `mutated`: strip the common prefix and suffix. An empty span
    (start == end) is a pure deletion at that point."""
    a, b = 0, 0
    n = min(len(original), len(mutated))
    while a < n and original[a] == mutated[a]:
        a += 1
    while b < n - a and original[len(original) - 1 - b] == mutated[len(mutated) - 1 - b]:
        b += 1
    return a, len(mutated) - b


def select_faults(units, ctx, total=50, seed=7, mutators=None, flip=True):
    """Pick up to `total` (unit, mutated Spanish) pairs, mutators in rotation so every category is present.

    Each unit carries at most one fault. Every unit that can take the 40-rule flip is used for it (up to
    FORTY_MAX), because the bar wants every flip caught. Deterministic for one seed; never mutates `units`.
    """
    rnd = random.Random(seed)
    order = list(range(len(units)))
    rnd.shuffle(order)
    used, faults = set(), []

    def add(i, name, fn):
        r = fn(units[i], ctx)
        if r is None or r[0] == units[i]["spanish"]:
            return False
        spanish, fragment, category, severity = r
        a, b = changed_span(units[i]["spanish"], spanish)
        faults.append({"fault_id": "X%03d" % (len(faults) + 1), "mutator": name, "category": category,
                       "severity": severity, "fragment": fragment, "unit": jp.unit_key(units[i]),
                       "file": units[i]["file"], "segment": units[i]["id"],
                       "original_spanish": units[i]["spanish"], "mutated_spanish": spanish,
                       "span": [a, b]})
        used.add(i)
        return True

    mutators = mutators or MUTATORS
    forty = dict(jp.MUTATORS)["flip_forty"]
    for i in order if flip else []:
        if len(faults) >= FORTY_MAX:
            break
        if forty(units[i], ctx):
            add(i, "flip_forty", forty)
    rot = 0
    stalled = 0
    while len(faults) < total and stalled < len(mutators):
        name, fn = mutators[rot % len(mutators)]
        rot += 1
        for i in order:
            if i in used:
                continue
            if add(i, name, fn):
                stalled = 0
                break
        else:
            stalled += 1
    return faults


FORTY_MAX = 12


def select_controls(units, faults, n=10, seed=7):
    """Clean units (not faulted) that look like the faulted ones: same files, no mutation."""
    rnd = random.Random(seed + 1)
    taken = {f["unit"] for f in faults}
    pool = [u for u in units if jp.unit_key(u) not in taken and len(u["english"]) > 40]
    rnd.shuffle(pool)
    return pool[:n]


# ---------------------------------------------------------------------------------------------- reviewer

def review_input(unit, spanish, glossary, cat, task_model):
    return {"segment_id": unit["id"], "file": unit["file"], "tier": jp.tier_of(unit),
            "english": unit["english"], "spanish": spanish,
            "glossary_slice": [{"en": en, "es": es, "banned": banned}
                               for en, es, banned in jp.glossary_slice([unit], glossary, cat, limit=25)],
            "house_style_rules": HOUSE_RULES, "reviewer_model": task_model}


def parse_findings(text):
    """JSON Lines (one finding per line) or `[]`; one code fence is tolerated. Returns (findings, errors)."""
    s = (text or "").strip()
    m = re.match(r"^```(?:json|jsonl)?\s*\n(.*)\n```$", s, re.S)
    if m:
        s = m.group(1).strip()
    if s in ("", "[]"):
        return [], []
    out, errs = [], []
    for n, line in enumerate(s.split("\n"), 1):
        line = line.strip()
        if not line or line == "[]":
            continue
        try:
            obj = json.loads(line)
        except ValueError:
            errs.append("line %d is not JSON" % n)
            continue
        if isinstance(obj, list):
            out += [o for o in obj if isinstance(o, dict)]
        elif isinstance(obj, dict):
            out.append(obj)
        else:
            errs.append("line %d is not an object" % n)
    return out, errs


def valid_findings(findings, english, spanish, schema_enums):
    """Mechanical filter of plan 9.2: required fields, enums, and exact-substring excerpts. Returns
    (kept, rejected) where rejected is a list of (finding, reason)."""
    kept, rejected = [], []
    for f in findings:
        reason = None
        if f.get("severity") not in schema_enums["severity"]:
            reason = "bad severity"
        elif f.get("category") not in schema_enums["category"]:
            reason = "bad category"
        else:
            e, s = f.get("english_excerpt"), f.get("spanish_excerpt")
            if e is None and s is None:
                reason = "no excerpt"
            elif e is not None and (not isinstance(e, str) or e not in english):
                reason = "english excerpt is not an exact substring"
            elif s is not None and (not isinstance(s, str) or s not in spanish):
                reason = "spanish excerpt is not an exact substring"
        (rejected.append((f, reason)) if reason else kept.append(f))
    return kept, rejected


def points_at(finding, fault, tolerance=6):
    """Does this (already valid) finding point at the planted change?"""
    mutated = fault["mutated_spanish"]
    a, b = fault["span"]
    s = finding.get("spanish_excerpt")
    if s is None:
        # a pure omission has no Spanish place; only the omission-type categories claim it
        return fault["category"] == "omission" and finding.get("category") in OMISSION_CATEGORIES
    start = 0
    while True:
        i = mutated.find(s, start)
        if i < 0:
            return False
        j = i + len(s)
        if a == b:                                   # deletion at a point
            if i - tolerance <= a <= j + tolerance:
                return True
        elif i < b + tolerance and j > a - tolerance:
            return True
        start = i + 1


def score_fault(fault, findings, english, schema_enums):
    kept, rejected = valid_findings(findings, english, fault["mutated_spanish"], schema_enums)
    hits = [f for f in kept if points_at(f, fault)]
    best = min((SEV_RANK[f["severity"]] for f in hits), default=None)
    detected_sev = None if best is None else [k for k, v in SEV_RANK.items() if v == best][0]
    return {"fault_id": fault["fault_id"], "caught": bool(hits),
            "caught_at_major": any(f["severity"] in MAJOR_PLUS for f in hits),
            "reported_severity": detected_sev, "valid": len(kept), "rejected": len(rejected),
            "elsewhere": len(kept) - len(hits)}


def score_control(findings, english, spanish, schema_enums):
    kept, rejected = valid_findings(findings, english, spanish, schema_enums)
    return {"valid": len(kept), "rejected": len(rejected),
            "major_plus": [f for f in kept if f["severity"] in MAJOR_PLUS]}


# ---------------------------------------------------------------------------------------------- verdict

def recall_table(faults, scores):
    by = {f["fault_id"]: s for f, s in ((f, scores[f["fault_id"]]) for f in faults)}
    rows = {}
    for f in faults:
        r = rows.setdefault(f["category"], {"n": 0, "caught": 0, "major_n": 0, "major_caught": 0})
        r["n"] += 1
        r["caught"] += by[f["fault_id"]]["caught"]
        if f["severity"] in MAJOR_PLUS:
            r["major_n"] += 1
            r["major_caught"] += by[f["fault_id"]]["caught"]
    return rows


def verdict(faults, scores, bar):
    """PASS only if recall on critical+major faults >= bar and every 40-rule flip is caught."""
    major = [f for f in faults if f["severity"] in MAJOR_PLUS]
    caught = sum(1 for f in major if scores[f["fault_id"]]["caught"])
    recall = caught / len(major) if major else 0.0
    flips = [f for f in faults if f["mutator"] == "flip_forty"]
    missed_flips = [f["fault_id"] for f in flips if not scores[f["fault_id"]]["caught"]]
    reasons = []
    if not major:
        reasons.append("no major faults were seeded")
    if recall < bar:
        reasons.append("recall on critical and major faults %.1f%% is below the bar %.0f%%" % (recall * 100, bar * 100))
    if not flips:
        reasons.append("no 40-rule flip was seeded")
    if missed_flips:
        reasons.append("missed 40-rule flips: " + ", ".join(missed_flips))
    return {"pass": not reasons, "recall_major": recall, "major_n": len(major), "major_caught": caught,
            "flips_n": len(flips), "flips_missed": missed_flips, "reasons": reasons}


# ---------------------------------------------------------------------------------------------- backend

class ReviewerError(Exception):
    pass


class ClaudeReviewer:
    """`claude -p`, every tool disabled, the review prompt as system prompt, one unit as the input JSON."""

    def __init__(self, model="sonnet", timeout=300, binary="claude"):
        self.model, self.timeout, self.binary = model, timeout, binary

    def ask(self, system, inp):
        cmd = [self.binary, "-p", "--output-format", "json", "--model", self.model, "--tools", "",
               "--no-session-persistence", "--system-prompt", system]
        try:
            r = subprocess.run(cmd, input=json.dumps(inp, ensure_ascii=False), capture_output=True, text=True,
                               timeout=self.timeout, cwd=WORK)
        except (OSError, subprocess.TimeoutExpired) as e:
            raise ReviewerError("claude CLI failed: %s" % e) from None
        if r.returncode != 0:
            raise ReviewerError("claude CLI exit %d: %s" % (r.returncode, r.stderr.strip()[:300]))
        try:
            env = json.loads(r.stdout)
        except ValueError:
            raise ReviewerError("claude CLI did not return JSON") from None
        if env.get("is_error"):
            raise ReviewerError("claude CLI error: %s" % str(env.get("result"))[:300])
        return {"text": env.get("result", ""), "cost": float(env.get("total_cost_usd", 0) or 0),
                "models": sorted((env.get("modelUsage") or {}).keys())}


def load_replies(path=REPLIES):
    rows = {}
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    r = json.loads(line)
                    rows[r["key"]] = r
    return rows


def key_of(inp):
    return hashlib.sha256(json.dumps(inp, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()[:20]


def ask_all(reviewer, system, jobs, replies, path=REPLIES, workers=4, max_usd=3.0, log=print):
    """jobs: list of (job_id, input). Resumes from `replies`; stops starting calls once the spend passes max_usd."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    spent = sum(r.get("cost", 0) for r in replies.values())
    todo = [(j, i) for j, i in jobs if key_of(i) not in replies]

    state = {"spent": spent}
    lock = threading.Lock()

    def one(job):
        j, inp = job
        with lock:                       # the budget is checked in the worker: a lagging consumer must not overspend
            if state["spent"] >= max_usd:
                return j, None, "budget"
        try:
            out = reviewer.ask(system, inp)
        except ReviewerError as e:
            return j, None, str(e)
        row = {"key": key_of(inp), "job": j, "text": out["text"], "cost": out["cost"], "models": out["models"]}
        with lock:
            state["spent"] += out["cost"]
            replies[row["key"]] = row
            with open(path, "a", encoding="utf-8", newline="\n") as f:
                f.write(json.dumps(row, ensure_ascii=False) + "\n")
            log("  %s done (spent $%.2f)" % (j, state["spent"]))
        return j, row, None

    failed = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        for j, row, err in ex.map(one, todo):
            if row is None:
                failed.append((j, err))
                log("  %s: no reply (%s)" % (j, err))
    return failed


# ---------------------------------------------------------------------------------------------- report

def finding_enums():
    with open(os.path.join(ROOT, "translation", "schemas", "finding.schema.json"), encoding="utf-8") as f:
        sch = json.load(f)["properties"]
    return {"severity": sch["severity"]["enum"], "category": sch["category"]["enum"]}


def render_report(meta, faults, scores, controls, control_scores, v, bar):
    L = ["# Pilot: seeded-fault recall of the in-loop reviewer (task P3-007)", ""]
    L.append("**Verdict: %s.** %s" % ("PASS" if v["pass"] else "FAIL",
             "; ".join(v["reasons"]) if v["reasons"] else
             "recall on critical and major faults %.1f%% (bar %.0f%%), every 40-rule flip caught." % (v["recall_major"] * 100, bar * 100)))
    L += ["", "| Item | Value |", "| --- | --- |",
          "| Reviewer | %s (prompt translation/prompts/review.md, tools disabled, one unit per call) |" % meta["reviewer"],
          "| Model ids seen | %s |" % (", ".join(meta["models"]) or "unknown"),
          "| Translator | %s |" % meta["translator"],
          "| Seed | %s |" % meta["seed"],
          "| Faults seeded | %d (%d critical or major) |" % (len(faults), v["major_n"]),
          "| Clean controls | %d |" % len(controls),
          "| Spent | $%.2f |" % meta["spent"], "",
          "A fault counts as caught only when a schema-valid finding with exact-substring excerpts points at the "
          "changed place. A finding elsewhere, or with an excerpt that is not an exact substring, earns nothing.", "",
          "## Recall by category", "", "| Category | Faults | Caught | Critical or major | Caught |", "| --- | --- | --- | --- | --- |"]
    for cat, r in sorted(recall_table(faults, scores).items()):
        L.append("| %s | %d | %d | %d | %d |" % (cat, r["n"], r["caught"], r["major_n"], r["major_caught"]))
    L += ["", "## Recall by mutator", "", "| Mutator | Severity | Faults | Caught | Caught at major or critical |", "| --- | --- | --- | --- | --- |"]
    mut = {}
    for f in faults:
        r = mut.setdefault((f["mutator"], f["severity"]), [0, 0, 0])
        r[0] += 1
        r[1] += scores[f["fault_id"]]["caught"]
        r[2] += scores[f["fault_id"]]["caught_at_major"]
    for (m, s), r in sorted(mut.items()):
        L.append("| %s | %s | %d | %d | %d |" % (m, s, r[0], r[1], r[2]))
    L += ["", "## 40-rule flips", "",
          "%d seeded, %d missed%s." % (v["flips_n"], len(v["flips_missed"]),
                                       (" (" + ", ".join(v["flips_missed"]) + ")") if v["flips_missed"] else ""), "",
          "## Clean controls", ""]
    fp = [(c, s) for c, s in zip(controls, control_scores) if s["major_plus"]]
    L.append("%d of %d clean units drew a critical or major finding with valid excerpts (%d findings rejected for "
             "non-exact excerpts across all controls)." % (len(fp), len(controls), sum(s["rejected"] for s in control_scores)))
    for c, s in fp:
        for f in s["major_plus"]:
            L.append("- `%s`: %s %s: %s" % (jp.unit_key(c), f["severity"], f["category"], f["problem"][:160].replace("\n", " ")))
    L += ["", "These are leads, not proof of a translation fault: a human or the adjudicator decides.", "",
          "## Every fault", "", "| Fault | Mutator | Severity | Unit | Caught | Reported as | Valid findings | Rejected |",
          "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for f in faults:
        s = scores[f["fault_id"]]
        L.append("| %s | %s | %s | `%s` | %s | %s | %d | %d |" % (
            f["fault_id"], f["mutator"], f["severity"], f["unit"], "yes" if s["caught"] else "**NO**",
            s["reported_severity"] or "-", s["valid"], s["rejected"]))
    L += ["", "## Limits of this test", "",
          "- The playfulness fault (a joke replaced by a flat literal rendering) cannot be seeded mechanically and is not measured here; the Jury canaries and the humor register cover it.",
          "- Categories with fewer than 3 faults (%s) have too few cases to show recall; the pilot files hold few such spots. The Jury canaries measure them on the full book." % (
              ", ".join(sorted(c for c, r in recall_table(faults, scores).items() if r["n"] < 3)) or "none"),
          "- The faults are mechanical swaps in one segment. Faults that need context from another file (terminology drift, cross-file links) are not measured.",
          "- The reviewer and the translator are the same model tier; independence is carried by the manual Jury (plan 9.1).", ""]
    return "\n".join(L)


# ---------------------------------------------------------------------------------------------- run

def build_jobs(faults, controls, glossary, cat, units_by_key, reviewer_name):
    jobs = []
    for f in faults:
        u = units_by_key[f["unit"]]
        jobs.append((f["fault_id"], review_input(u, f["mutated_spanish"], glossary, cat, reviewer_name)))
    for i, u in enumerate(controls, 1):
        jobs.append(("K%03d" % i, review_input(u, u["spanish"], glossary, cat, reviewer_name)))
    return jobs


def evaluate(faults, controls, jobs, replies, enums):
    jobmap = dict(jobs)
    scores, control_scores, missing = {}, [], []
    for f in faults:
        inp = jobmap[f["fault_id"]]
        r = replies.get(key_of(inp))
        if r is None:
            missing.append(f["fault_id"])
            scores[f["fault_id"]] = {"fault_id": f["fault_id"], "caught": False, "caught_at_major": False,
                                     "reported_severity": None, "valid": 0, "rejected": 0, "elsewhere": 0}
            continue
        findings, _ = parse_findings(r["text"])
        scores[f["fault_id"]] = score_fault(f, findings, inp["english"], enums)
    for i, u in enumerate(controls, 1):
        inp = jobmap["K%03d" % i]
        r = replies.get(key_of(inp))
        if r is None:
            missing.append("K%03d" % i)
            control_scores.append({"valid": 0, "rejected": 0, "major_plus": []})
            continue
        findings, _ = parse_findings(r["text"])
        control_scores.append(score_control(findings, inp["english"], inp["spanish"], enums))
    return scores, control_scores, missing


def load_units():
    import inventory
    import verify
    import catalog
    cfg = inventory.read_config(ROOT)
    cat = catalog.load("es")
    files = []
    for dirpath, _dirs, names in os.walk(os.path.join(ROOT, "translation", "po")):
        for n in names:
            if n.endswith(".po"):
                rel = os.path.relpath(os.path.join(dirpath, n), os.path.join(ROOT, "translation", "po"))
                files.append(rel[:-3])
    files.sort()
    units, _ = jp.collect_units(ROOT, files, cfg, cat, verify.english_text)
    return units, cat, cfg


def load_code_units(families):
    """Chunks of localized src/ files that differ from the English (Part II code comments and categories)."""
    import inventory
    import verify  # noqa: F401
    cfg = inventory.read_config(ROOT)
    cat = __import__("catalog").load("es")
    english_root = cfg.get("english_clone_path") or "/home/lehmer/english-source"
    rels = [r for r in jp.localized_files(ROOT) if any(r.startswith("src/%s/" % f) for f in families)]
    units = jp.collect_code_units(ROOT, english_root, rels)
    return units, cat, cfg


def main(argv):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--run", action="store_true")
    ap.add_argument("--rescore", action="store_true")
    ap.add_argument("--faults", type=int, default=50)
    ap.add_argument("--controls", type=int, default=10)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--model", default="sonnet")
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--max-usd", type=float, default=3.0)
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--code", default="", help="comma list of src families: seed faults in localized code chunks instead of prose")
    args = ap.parse_args(argv[1:])
    if not (args.run or args.rescore):
        ap.print_help()
        return 2
    import inventory
    if args.code:
        units, cat, cfg = load_code_units([x for x in args.code.split(",") if x])
    else:
        units, cat, cfg = load_units()
    glossary = jp.load_glossary()
    ctx = jp.canary_context(cat)
    faults = select_faults(units, ctx, args.faults, args.seed, CODE_FAULTS if args.code else None, not args.code)
    controls = select_controls(units, faults, args.controls, args.seed)
    by_key = {jp.unit_key(u): u for u in units}
    reviewer_name = str(cfg.get("in_loop_reviewer", args.model))
    jobs = build_jobs(faults, controls, glossary, cat, by_key, reviewer_name)
    with open(PROMPT_PATH, encoding="utf-8") as f:
        system = f.read()
    os.makedirs(WORK, exist_ok=True)
    replies = load_replies()
    print("units %d, faults %d, controls %d, replies on disk %d" % (len(units), len(faults), len(controls), len(replies)))
    if args.run:
        failed = ask_all(ClaudeReviewer(args.model), system, jobs, replies, workers=args.workers, max_usd=args.max_usd)
        if failed:
            print("%d calls got no reply; rerun to resume" % len(failed))
    enums = finding_enums()
    scores, control_scores, missing = evaluate(faults, controls, jobs, replies, enums)
    if missing:
        print("missing replies: %s (not scored as caught; the verdict is provisional)" % ", ".join(missing))
    bar = float(cfg.get("seeded_fault_recall_bar", 0.95))
    v = verdict(faults, scores, bar)
    if missing:
        v = dict(v, **{"pass": False, "reasons": v["reasons"] + ["%d units have no reply" % len(missing)]})
    models = sorted({m for j, i in jobs for m in replies.get(key_of(i), {}).get("models", [])})
    meta = {"reviewer": reviewer_name, "translator": str(cfg.get("translator", "?")), "seed": args.seed,
            "models": models, "spent": sum(r.get("cost", 0) for r in replies.values())}
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    with open(args.out, "w", encoding="utf-8", newline="\n") as f:
        f.write(render_report(meta, faults, scores, controls, control_scores, v, bar))
    with open(FAULTS_PATH, "w", encoding="utf-8", newline="\n") as f:
        json.dump(faults, f, ensure_ascii=False, indent=1)
    print("wrote %s: %s, recall %d/%d" % (args.out, "PASS" if v["pass"] else "FAIL", v["major_caught"], v["major_n"]))
    return 0 if v["pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
