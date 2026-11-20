#!/usr/bin/env python3
"""tools/jury_ingest.py: ingest the Jury replies in review/inbox/ (plan 7C, task P2-017).

For every reply file (review/inbox/<juror>-<lens>-<date>.md, saved exactly as given):
  1. parse the header line and the JSONL findings (the format of ralph-kit-es/ADVERSARIAL-REVIEW-PROMPT.md);
  2. validate every finding (required fields, enums from translation/schemas/finding.schema.json);
  3. discard a finding whose English or Spanish excerpt is not an EXACT substring of the unit the juror saw
     (the unit text comes from review/units.index.jsonl, canary mutations included);
  4. score the juror: of the canaries planted in the packets the juror reviewed, how many were caught, in total
     and for critical and major faults; unreliable jurors are down-weighted;
  5. drop findings that only caught a canary, merge duplicates across jurors (highest severity wins);
  6. write review/report-<date>.md and review/findings-<date>.jsonl (finding schema, status "open", for the
     fresh-context adjudicator).

Later, once an adjudicator has set statuses, `--enqueue FILE` turns every "accepted" finding into a review-fix
task of the queue and removes loop/DONE so that the loop runs again.

Usage:
  python3 -I tools/jury_ingest.py [--review review] [--date YYYY-MM-DD]
  python3 -I tools/jury_ingest.py --enqueue review/findings-<date>.jsonl [--queue loop/queue/generated] [--done loop/DONE]
"""
from __future__ import annotations

import argparse
import datetime
import glob
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)

SCHEMA = os.path.join(ROOT, "translation", "schemas", "finding.schema.json")
SEVERITY_ORDER = {"critical": 0, "major": 1, "minor": 2, "suggestion": 3}
EXCERPT_MAX = 300
RELIABLE_RECALL, PARTIAL_RECALL = 0.75, 0.40      # juror weight 1.0 / 0.5 / 0.25 by canary recall
JUROR_REQUIRED = ("severity", "category", "problem", "evidence", "proposed_fix", "confidence", "type")
HEADER_REQUIRED = ("juror_model", "lens")


# ---------------------------------------------------------------------------------------------- parsing

FENCE_RE = re.compile(r"^```[ \t]*(?P<info>[A-Za-z0-9_-]*)[ \t]*\n(?P<body>.*?)^```[ \t]*$", re.S | re.M)


def parse_reply(text):
    """Return (header, findings, errors). `findings` is a list of (line_number, dict or None, error or None)."""
    header, findings, errors = None, [], []
    for m in FENCE_RE.finditer(text):
        info, body = m.group("info").lower(), m.group("body")
        lines = [ln for ln in body.split("\n") if ln.strip()]
        if header is None and info in ("json", "") and len(lines) == 1:
            try:
                obj = json.loads(lines[0])
            except ValueError:
                obj = None
            if isinstance(obj, dict) and "juror_model" in obj:
                header = obj
                continue
        if info in ("jsonl", "json", ""):
            first_line = text[:m.start("body")].count("\n") + 1
            for i, ln in enumerate(body.split("\n")):
                if not ln.strip():
                    continue
                try:
                    obj = json.loads(ln)
                except ValueError as e:
                    findings.append((first_line + i, None, "not JSON (%s)" % e))
                    continue
                if isinstance(obj, dict) and "juror_model" in obj and header is None:
                    header = obj
                elif isinstance(obj, dict):
                    findings.append((first_line + i, obj, None))
                else:
                    findings.append((first_line + i, None, "a finding must be a JSON object"))
    if header is None:
        errors.append("no header line with juror_model")
    else:
        for k in HEADER_REQUIRED:
            if not header.get(k):
                errors.append("header lacks %s" % k)
    return header, findings, errors


def load_enums(path=SCHEMA):
    with open(path, encoding="utf-8") as f:
        schema = json.load(f)
    props = schema["properties"]
    return {k: set(props[k]["enum"]) for k in ("severity", "category", "confidence", "type")}


def validate_finding(f, enums):
    """Field problems of one juror finding (not the quotes). Empty list means the shape is fine."""
    errs = []
    for k in JUROR_REQUIRED:
        v = f.get(k)
        if not isinstance(v, str) or not v.strip():
            errs.append("missing or empty %s" % k)
    for k, allowed in enums.items():
        v = f.get(k)
        if isinstance(v, str) and v and v not in allowed:
            errs.append("%s %r is not allowed" % (k, v))
    for k in ("english_excerpt", "spanish_excerpt"):
        if k not in f:
            errs.append("missing %s (use null)" % k)
            continue
        v = f[k]
        if v is not None and not isinstance(v, str):
            errs.append("%s must be a string or null" % k)
        elif v == "":
            errs.append("%s is empty (use null)" % k)
        elif isinstance(v, str) and len(v) > EXCERPT_MAX:
            errs.append("%s is longer than %d characters" % (k, EXCERPT_MAX))
    if f.get("english_excerpt") is None and f.get("spanish_excerpt") is None and \
            "english_excerpt" in f and "spanish_excerpt" in f:
        errs.append("both excerpts are null: nothing to check")
    return errs


# ---------------------------------------------------------------------------------------------- units and quotes

def load_units(review):
    """Every unit shown to jurors: list of dicts from review/units.index.jsonl."""
    out = []
    with open(os.path.join(review, "units.index.jsonl"), encoding="utf-8") as f:
        for line in f:
            if line.strip():
                out.append(json.loads(line))
    return out


def load_canaries(review):
    with open(os.path.join(review, "canaries.key.json"), encoding="utf-8") as f:
        return json.load(f)["canaries"]


def reviewed_units(units, header):
    """The units of the packets the header names; every unit when it names none that exists."""
    names = {str(x).replace(".md", "") for x in (header or {}).get("packets_or_files_reviewed", []) or []}
    names = {os.path.basename(n) for n in names}
    known = {u["packet"] for u in units}
    hit = names & known
    return [u for u in units if u["packet"] in hit] if hit else list(units)


def locate(finding, units):
    """The unit the finding is about, or None. The segment id decides; the file narrows a tie; failing both,
    the one unit that contains every given excerpt."""
    seg = str(finding.get("segment") or finding.get("segment_id") or "").strip()
    cands = [u for u in units if u["segment"] == seg] if seg else []
    if len(cands) > 1 and finding.get("file"):
        narrowed = [u for u in cands if u["file"] == finding["file"]]
        cands = narrowed or cands
    if len(cands) == 1:
        return cands[0]
    if cands:                                   # same id in two files: keep those that contain the quotes
        ok = [u for u in cands if not quote_errors(finding, u)]
        return ok[0] if ok else cands[0]
    ex = [(k, finding.get(k)) for k in ("english_excerpt", "spanish_excerpt") if finding.get(k)]
    if not ex:
        return None
    found = [u for u in units if all(v in u["english" if k == "english_excerpt" else "spanish"] for k, v in ex)]
    return found[0] if len(found) == 1 else None


def quote_errors(finding, unit):
    """Exact-substring check against the text the juror saw. Returns problem strings."""
    errs = []
    for key, field in (("english_excerpt", "english"), ("spanish_excerpt", "spanish")):
        ex = finding.get(key)
        if ex is not None and ex not in unit[field]:
            errs.append("%s is not an exact substring of the %s text: %r" % (key, field, str(ex)[:60]))
    return errs


# ---------------------------------------------------------------------------------------------- canaries

def overlaps(a, b):
    return bool(a and b and (a in b or b in a))


def caught(canary, findings_with_units):
    """True when a validated finding is about the canary's unit and either quotes the planted text or names the
    planted category."""
    for f, unit in findings_with_units:
        if unit["segment"] != canary["segment"] or unit["file"] != canary["file"]:
            continue
        if f.get("category") == canary["category"] or overlaps(f.get("spanish_excerpt"), canary["fragment"]):
            return True
    return False


def score_juror(canaries, units_seen, valid):
    """Canary recall of one juror over the canaries planted in the packets they reviewed."""
    seen_keys = {(u["file"], u["segment"]) for u in units_seen}
    seeded = [c for c in canaries if (c["file"], c["segment"]) in seen_keys]
    hits = [c for c in seeded if caught(c, valid)]
    miss = [c for c in seeded if c not in hits]

    def rec(sub_s, sub_h):
        return None if not sub_s else len(sub_h) / len(sub_s)
    by_sev = {}
    for sev in ("critical", "major"):
        s = [c for c in seeded if c["severity"] == sev]
        by_sev[sev] = (len([c for c in s if c in hits]), len(s))
    recall = rec(seeded, hits)
    if recall is None:
        weight, label = 1.0, "unscored (no canary in the reviewed packets)"
    elif recall >= RELIABLE_RECALL and not any(c["severity"] == "critical" for c in miss):
        weight, label = 1.0, "reliable"
    elif recall >= PARTIAL_RECALL:
        weight, label = 0.5, "down-weighted"
    else:
        weight, label = 0.25, "unreliable"
    return {"seeded": len(seeded), "caught": len(hits), "recall": recall, "by_severity": by_sev,
            "missed": [c["canary_id"] for c in miss], "caught_ids": [c["canary_id"] for c in hits],
            "weight": weight, "label": label}


# ---------------------------------------------------------------------------------------------- ingest

def ingest_reply(text, units, canaries, enums, name=""):
    """Process one reply. Returns a dict: header, kept (list of (finding, unit)), discarded, score, errors."""
    header, raw, errors = parse_reply(text)
    res = {"name": name, "header": header, "errors": list(errors), "kept": [], "discarded": [], "score": None,
           "canary_hits": []}
    if header is None:
        return res
    seen = reviewed_units(units, header)
    valid = []
    for line_no, f, err in raw:
        if f is None:
            res["discarded"].append((line_no, None, err))
            continue
        probs = validate_finding(f, enums)
        unit = None
        if not probs:
            unit = locate(f, seen)
            if unit is None:
                probs.append("segment %r not found in the packets reviewed" % (f.get("segment") or f.get("segment_id")))
            else:
                probs += quote_errors(f, unit)
        if probs:
            res["discarded"].append((line_no, f, "; ".join(probs)))
        else:
            valid.append((f, unit))
    res["score"] = score_juror(canaries, seen, valid)
    planted = {c["canary_id"] for c in canaries if c["canary_id"] in res["score"]["caught_ids"]}
    by_id = {c["canary_id"]: c for c in canaries}
    for f, unit in valid:
        hit = next((by_id[i] for i in planted
                    if by_id[i]["segment"] == unit["segment"] and by_id[i]["file"] == unit["file"]
                    and caught(by_id[i], [(f, unit)])), None)
        if hit:
            res["canary_hits"].append((f, hit["canary_id"]))      # a planted fault found: not a real defect
        else:
            res["kept"].append((f, unit))
    return res


def merge_findings(results):
    """Deduplicate across jurors: same unit and category with overlapping excerpts, or the same quotes.
    The highest severity wins; reporters and their weights are kept."""
    merged = []
    for r in results:
        who = (r["header"] or {}).get("juror_model", "?")
        lens = (r["header"] or {}).get("lens", "")
        weight = r["score"]["weight"] if r["score"] else 1.0
        for f, unit in r["kept"]:
            row = None
            for m in merged:
                if m["unit"] is unit or (m["unit"]["file"], m["unit"]["segment"]) == (unit["file"], unit["segment"]):
                    if m["category"] == f["category"] and (
                            overlaps(m["spanish_excerpt"], f.get("spanish_excerpt")) or
                            overlaps(m["english_excerpt"], f.get("english_excerpt")) or
                            (m["spanish_excerpt"] is None and f.get("spanish_excerpt") is None
                             and m["english_excerpt"] == f.get("english_excerpt"))):
                        row = m
                        break
            rep = {"juror": who, "lens": lens, "weight": weight, "source_id": f.get("id", "")}
            if row is None:
                merged.append({"unit": unit, "category": f["category"], "severity": f["severity"],
                               "english_excerpt": f.get("english_excerpt"), "spanish_excerpt": f.get("spanish_excerpt"),
                               "problem": f["problem"], "learner_impact": f.get("learner_impact", ""),
                               "evidence": f["evidence"], "proposed_fix": f["proposed_fix"],
                               "confidence": f["confidence"], "type": f["type"], "reporters": [rep]})
            else:
                row["reporters"].append(rep)
                if SEVERITY_ORDER[f["severity"]] < SEVERITY_ORDER[row["severity"]]:
                    row["severity"] = f["severity"]
    merged.sort(key=lambda m: (SEVERITY_ORDER[m["severity"]], -sum(r["weight"] for r in m["reporters"]),
                               m["unit"]["file"], m["unit"]["line"]))
    return merged


def to_schema_rows(merged):
    """Findings in translation/schemas/finding.schema.json shape, status open, ready for the adjudicator."""
    rows = []
    for n, m in enumerate(merged, 1):
        jurors = ", ".join(sorted({r["juror"] for r in m["reporters"]}))
        row = {"id": "F%03d" % n, "segment_id": m["unit"]["segment"], "file": m["unit"]["file"],
               "severity": m["severity"], "category": m["category"],
               "english_excerpt": m["english_excerpt"], "spanish_excerpt": m["spanish_excerpt"],
               "problem": m["problem"], "evidence": m["evidence"], "proposed_fix": m["proposed_fix"],
               "reviewer_model": jurors, "confidence": m["confidence"], "type": m["type"], "status": "open"}
        if m["learner_impact"]:
            row["learner_impact"] = m["learner_impact"]
        rows.append(row)
    return rows


def pct(x):
    return "n/a" if x is None else "%d%%" % round(100 * x)


def report_md(results, merged, date):
    lines = ["# Jury report %s" % date, "",
             "Generated by tools/jury_ingest.py. Findings whose quotes are not exact were discarded; findings that only "
             "found a planted fault are counted in the juror's score and are not listed as defects.", "",
             "## Jurors", "",
             "| Reply | Juror | Lens | Findings kept | Discarded | Canaries seeded | Caught | Recall | Critical | Major | Weight |",
             "|---|---|---|---|---|---|---|---|---|---|---|"]
    for r in results:
        h = r["header"] or {}
        s = r["score"]
        if s is None:
            lines.append("| %s | (header missing) | | 0 | %d | | | | | | |" % (r["name"], len(r["discarded"])))
            continue
        crit, maj = s["by_severity"]["critical"], s["by_severity"]["major"]
        lines.append("| %s | %s | %s | %d | %d | %d | %d | %s | %d/%d | %d/%d | %.2f %s |" % (
            r["name"], h.get("juror_model", ""), h.get("lens", ""), len(r["kept"]), len(r["discarded"]),
            s["seeded"], s["caught"], pct(s["recall"]), crit[0], crit[1], maj[0], maj[1], s["weight"], s["label"]))
    lines += ["", "## Findings for the adjudicator (%d)" % len(merged), ""]
    for n, m in enumerate(merged, 1):
        w = sum(r["weight"] for r in m["reporters"])
        who = ", ".join("%s %s (w %.2f)" % (r["juror"], r["lens"], r["weight"]) for r in m["reporters"])
        lines += ["### F%03d %s / %s: %s:%d" % (n, m["severity"], m["category"], m["unit"]["file"], m["unit"]["line"]),
                  "", "- segment: `%s`" % m["unit"]["segment"], "- reported by: %s (total weight %.2f)" % (who, w),
                  "- EN: %s" % (m["english_excerpt"] if m["english_excerpt"] is not None else "(none)"),
                  "- ES: %s" % (m["spanish_excerpt"] if m["spanish_excerpt"] is not None else "(none)"),
                  "- problem: %s" % m["problem"], "- evidence: %s" % m["evidence"],
                  "- proposed fix: %s" % m["proposed_fix"], ""]
    lines += ["## Discarded findings", ""]
    any_d = False
    for r in results:
        for line_no, f, why in r["discarded"]:
            any_d = True
            lines.append("- %s line %d: %s" % (r["name"], line_no, why))
    if not any_d:
        lines.append("None.")
    lines += ["", "## Canary misses (ids only)", ""]
    for r in results:
        if r["score"] and r["score"]["missed"]:
            lines.append("- %s missed %s" % (r["name"], ", ".join(r["score"]["missed"])))
    for r in results:
        for e in r["errors"]:
            lines.append("- %s: %s" % (r["name"], e))
    return "\n".join(lines).rstrip() + "\n"


def run(review, date, enums=None):
    enums = enums or load_enums()
    units, canaries = load_units(review), load_canaries(review)
    inbox = sorted(glob.glob(os.path.join(review, "inbox", "*.md")))
    results = []
    for path in inbox:
        with open(path, encoding="utf-8") as f:
            results.append(ingest_reply(f.read(), units, canaries, enums, os.path.basename(path)))
    merged = merge_findings(results)
    rows = to_schema_rows(merged)
    with open(os.path.join(review, "report-%s.md" % date), "w", encoding="utf-8", newline="\n") as f:
        f.write(report_md(results, merged, date))
    with open(os.path.join(review, "findings-%s.jsonl" % date), "w", encoding="utf-8", newline="\n") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n")
    return results, merged, rows


# ---------------------------------------------------------------------------------------------- review-fix tasks

def enqueue_review_fixes(findings_path, queue_dir, done_path=None, stage=7):
    """Add one review-fix task per finding with status "accepted"; skip findings already queued.
    Removes loop/DONE (the loop runs again). Returns the list of new task ids."""
    os.makedirs(queue_dir, exist_ok=True)
    out = os.path.join(queue_dir, "review-fix.jsonl")
    have, n = set(), 0
    if os.path.exists(out):
        with open(out, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    t = json.loads(line)
                    have.add(t.get("finding"))
                    n = max(n, int(t["id"].split("-")[-1]))
    base = os.path.basename(findings_path)
    new = []
    with open(findings_path, encoding="utf-8") as f:
        rows = [json.loads(ln) for ln in f if ln.strip()]
    with open(out, "a", encoding="utf-8", newline="\n") as w:
        for r in rows:
            if r.get("status") != "accepted":
                continue
            ref = "%s:%s" % (base, r["id"])
            if ref in have:
                continue
            n += 1
            task = {"id": "RF-%03d" % n, "stage": stage, "kind": "review-fix",
                    "title": "Fix %s finding %s in %s: %s" % (r["severity"], r["id"], r["file"], r["problem"][:80]),
                    "deps": [], "inputs": [r["file"]], "size": "S", "finding": ref, "segment_id": r["segment_id"],
                    "accept": "python3 tools/verify.py --fast", "status": "todo", "attempts": 0}
            w.write(json.dumps(task, ensure_ascii=False, separators=(",", ":")) + "\n")
            new.append(task["id"])
    if new and done_path and os.path.exists(done_path):
        os.remove(done_path)
    return new


def main(argv):
    p = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    p.add_argument("--review", default=os.path.join(ROOT, "review"))
    p.add_argument("--date", default=datetime.date.today().isoformat())
    p.add_argument("--enqueue")
    p.add_argument("--queue", default=os.path.join(ROOT, "loop", "queue", "generated"))
    p.add_argument("--done", default=os.path.join(ROOT, "loop", "DONE"))
    a = p.parse_args(argv[1:])
    if a.enqueue:
        new = enqueue_review_fixes(a.enqueue, a.queue, a.done)
        print("queued %d review-fix task(s): %s" % (len(new), ", ".join(new)))
        return 0
    results, merged, rows = run(a.review, a.date)
    for r in results:
        s = r["score"]
        print("%s: kept %d, discarded %d, canary recall %s" % (
            r["name"], len(r["kept"]), len(r["discarded"]), pct(s["recall"]) if s else "n/a"))
    print("findings for the adjudicator: %d (review/report-%s.md)" % (len(rows), a.date))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
