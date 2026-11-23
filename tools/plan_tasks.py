#!/usr/bin/env python3
"""tools/plan_tasks.py: generate the per-file translate tasks from translation/work/inventory.json.

Writes (only when the content changed, so a second run leaves identical bytes):
  loop/queue/generated/translate.jsonl    translate tasks plus interleaved audit tasks
  loop/queue/generated/amendments.jsonl   one record that makes the Phase 4 gate wait for them

Rules (plan 11.3):
  * Only class "authored" files become tasks (generated blocks and lessons/cs/*.md never do).
  * A task covers at most `translate_task_max_source_words` (CONFIG.yaml) source words. A file
    over the cap is split into numbered parts by segment range (unit key "path#s<lo>-<hi>");
    a split part always forms its own task. Small files are packed greedily, in path order,
    within one group (a directory, or "src" for all entries).
  * An audit task follows every `audit_every_n_translate_tasks` translate tasks; the next batch
    of translate tasks depends on that audit, which is what makes the audits interleaved.
  * Idempotent and non-destructive: a task whose status is not "todo" is copied verbatim and its
    inputs are never planned again. A "todo" task is kept (status, attempts, notes intact) while
    all its inputs still exist in the inventory; otherwise it is dropped and its units re-packed.
    Tasks are never deleted from a file once they are doing, done, blocked or skipped.

Usage:
  python3 tools/plan_tasks.py            write the generated queue files
  python3 tools/plan_tasks.py --check    exit 1 if the files on disk differ from a fresh plan
  python3 tools/plan_tasks.py --dry-run  print the summary and write nothing
  python3 tools/plan_tasks.py --part2    plan Part II: one S5-fam-<entry> task per localizable
                                         entry family (see "Part II planning" below); combine with
                                         --check or --dry-run

Part II planning (plan section 4.5, task S4-006): families come from translation/localization-scope.yaml
(rows marked `never: true` are skipped), sizes from translation/part2/code-inventory.jsonl, order from
RISK_ORDER (pilot re-runs, comment-only, identifier renames, then COBOL, APL, m4, Forth, Unicode,
regex, archive, ed/ex, adversarial last). A family with no RISK_ORDER rule is an error, so a new family
can never be planned silently. Audits come after every `audit_every_n_translate_tasks` family tasks;
the next batch waits for that audit; S5-999 is amended to wait for all of them. Writes
loop/queue/generated/s5-families.jsonl and s5-amendments.jsonl. Finished tasks are copied verbatim.
"""
from __future__ import annotations

import argparse
import json
import math
import os
import re
import shlex
import sys

STAGE = 4
GATE_DEP = "P4-000"          # seed task that runs this tool
GATE_TASK = "P4-999"         # seed gate that must wait for every generated task
GENERATED_DIR = "loop/queue/generated"
TRANSLATE_FILE = "translate.jsonl"
AMEND_FILE = "amendments.jsonl"
INVENTORY = "translation/work/inventory.json"
CONFIG = "loop/CONFIG.yaml"
SEED = "loop/queue/seed.jsonl"

# Order in which groups are planned (plan: entry READMEs, CS sources, book lessons,
# study guides, curriculum remainder, support docs). First matching prefix wins.
GROUP_ORDER = ("src", "lessons/cs-source", "lessons/book", "lessons/study-guides",
               "lessons/languages", "lessons/curriculum", "lessons", "docs", ".", "sandbox")


def read_config(path=CONFIG):
    """Flat `key: value  # comment` parser (same shape ralph.sh reads)."""
    cfg = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.split("#", 1)[0].rstrip()
            if ":" not in line or line.lstrip() != line:
                continue
            k, v = line.split(":", 1)
            cfg[k.strip()] = v.strip().strip('"')
    return cfg


def group_of(path):
    parts = path.split("/")
    if len(parts) > 2 and parts[0] == "src":
        return "src"
    return "/".join(parts[:-1]) or "."


def group_rank(key):
    for i, p in enumerate(GROUP_ORDER):
        if key == p or (p != "." and key.startswith(p + "/")):
            return i
    return len(GROUP_ORDER)


def group_slug(key):
    return "root" if key == "." else key.replace("/", "-").lower()


def natural(s):
    return [int(x) if x.isdigit() else x for x in re.split(r"(\d+)", s)]


def make_units(files, cap):
    """Return {unit_key: unit dict} for every authored file, split over the cap."""
    units = {}
    for f in files:
        if f["class"] != "authored":
            continue
        path, words, segs = f["path"], f["words"], max(f.get("segments", 0), 0)
        parts = max(1, math.ceil(words / cap)) if cap > 0 else 1
        parts = min(parts, max(segs, 1))
        grp = group_of(path)
        if parts == 1:
            units[path] = {"key": path, "path": path, "group": grp, "words": words,
                           "split": False, "range": None}
            continue
        for i in range(parts):
            lo = (i * segs) // parts + 1
            hi = ((i + 1) * segs) // parts
            key = f"{path}#s{lo}-{hi}"
            w = words * (hi - lo + 1) // segs
            units[key] = {"key": key, "path": path, "group": grp, "words": w,
                          "split": True, "range": (lo, hi)}
    return units


def unit_sort_key(u):
    return (group_rank(u["group"]), u["group"], natural(u["path"]),
            u["range"][0] if u["range"] else 0)


def pack(units, cap):
    """Greedy bins over units already sorted; one group per call. Split parts stand alone."""
    bins, cur, cur_w = [], [], 0
    for u in units:
        if u["split"]:
            if cur:
                bins.append(cur)
                cur, cur_w = [], 0
            bins.append([u])
            continue
        if cur and cur_w + u["words"] > cap:
            bins.append(cur)
            cur, cur_w = [], 0
        cur.append(u)
        cur_w += u["words"]
    if cur:
        bins.append(cur)
    return bins


def _layer():
    """The English-key / working-path layer of the current directory (tools/enpath.py)."""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import enpath
    return enpath.load(os.getcwd())


def pilot_paths(seed_path=SEED):
    """Markdown paths named by Phase 3 pilot translate tasks (already translated there)."""
    found = set()
    if not os.path.exists(seed_path):
        return found
    with open(seed_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                t = json.loads(line)
                if t.get("stage") == 3 and t.get("kind") == "translate":
                    for m in re.findall(r"[\w./-]+/[\w./-]+\.md", t.get("title", "")):
                        found.add(_layer().english(m))     # tasks and the inventory are keyed by the English path
    return found


def describe(bin_units, grp, n_part_label=""):
    paths = []
    for u in bin_units:
        if u["path"] not in paths:
            paths.append(u["path"])
    total = sum(u["words"] for u in bin_units)
    if len(paths) == 1:
        what = paths[0] + (f" (segments {bin_units[0]['range'][0]} to {bin_units[0]['range'][1]})"
                           if bin_units[0]["split"] else "")
    else:
        what = f"{paths[0]} .. {paths[-1]} ({len(paths)} files)"
    return f"Translate {what}, about {total} words"


def translate_task(tid, bin_units, pilots):
    paths = {u["path"] for u in bin_units}
    task = {
        "id": tid, "stage": STAGE, "kind": "translate",
        "title": describe(bin_units, bin_units[0]["group"]),
        "deps": [], "size": "M",
        "inputs": [u["key"] for u in bin_units],
        "words": sum(u["words"] for u in bin_units),
        "accept": shlex.join(["python3", "tools/verify.py", "--fast", "--files", *sorted(paths)]),
        "status": "todo", "attempts": 0,
    }
    hit = sorted(paths & pilots)
    if hit:
        task["notes"] = ("Pilot file(s) already translated in Phase 3: " + ", ".join(hit)
                         + ". Verify their accepted segments; do not retranslate them.")
    return task


def load_jsonl(path):
    out = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                if line.strip():
                    out.append(json.loads(line))
    return out


def dumps(rows):
    return "".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) + "\n" for r in rows)


def plan(inventory, cap, batch, existing, pilots, gate_dep=GATE_DEP, gate_task=GATE_TASK):
    """Pure function: return (translate_rows, amendment_rows, stats)."""
    units = make_units(inventory["files"], cap)
    ex_tr = {t["id"]: t for t in existing if t.get("kind") == "translate"}
    ex_au = {t["id"]: t for t in existing if t.get("kind") == "audit"}

    kept, covered, dropped = {}, set(), []
    for tid in sorted(ex_tr, key=natural):
        t = ex_tr[tid]
        ins = t.get("inputs", [])
        if t.get("status") != "todo":
            kept[tid] = t
            covered.update(ins)
        elif ins and all(k in units and k not in covered for k in ins):
            bin_units = [units[k] for k in ins]
            fresh = translate_task(tid, bin_units, pilots)
            t = dict(t)
            t["title"], t["words"] = fresh["title"], fresh["words"]
            kept[tid] = t
            covered.update(ins)
        else:
            dropped.append(tid)

    leftover = sorted((u for k, u in units.items() if k not in covered), key=unit_sort_key)
    by_group = {}
    for u in leftover:
        by_group.setdefault(u["group"], []).append(u)
    new = 0
    for grp in sorted(by_group, key=lambda g: (group_rank(g), g)):
        slug = "P%d-%s-" % (STAGE, group_slug(grp))
        nums = [int(i[len(slug):]) for i in kept
                if i.startswith(slug) and i[len(slug):].isdigit()]
        n = max(nums or [0])
        for b in pack(by_group[grp], cap):
            n += 1
            kept[f"{slug}{n}"] = translate_task(f"{slug}{n}", b, pilots)
            new += 1

    def order(tid):
        t = kept[tid]
        first = t.get("inputs", [""])[0]
        path = first.split("#", 1)[0]
        g = group_of(path)
        m = re.match(r"(.*)-(\d+)$", tid)
        return (group_rank(g), g, natural(m.group(1)), int(m.group(2)) if m else 0)

    ordered = sorted(kept, key=order)
    rows, all_ids, prev_audit = [], [], None
    batches = [ordered[i:i + batch] for i in range(0, len(ordered), batch)] if batch > 0 else [ordered]
    for k, ids in enumerate(batches, 1):
        for tid in ids:
            t = kept[tid]
            if t.get("status") == "todo":
                t = dict(t)
                t["deps"] = [d for d in (gate_dep, prev_audit) if d]
            rows.append(t)
        aid = f"P{STAGE}-audit-{k}"
        old = ex_au.get(aid)
        if old is not None and old.get("status") != "todo":
            audit = old
        else:
            audit = {
                "id": aid, "stage": STAGE, "kind": "audit",
                "title": f"Audit batch {k}: sample 5 finished segments from {', '.join(ids)}",
                "deps": list(ids), "size": "S", "inputs": list(ids),
                "accept": "five sampled segments reviewed in a fresh context; findings become review-fix tasks",
                "status": "todo" if old is None else old["status"],
                "attempts": 0 if old is None else old.get("attempts", 0),
            }
            if old is not None and "notes" in old:
                audit["notes"] = old["notes"]
        rows.append(audit)
        all_ids += ids + [aid]
        prev_audit = aid

    emitted = {r["id"] for r in rows}
    for aid in sorted(ex_au, key=natural):      # never drop a started or finished audit
        if aid not in emitted and ex_au[aid].get("status") != "todo":
            rows.append(ex_au[aid])
            all_ids.append(aid)

    amend = []
    if gate_task:
        amend.append({"amend": gate_task, "add_deps": sorted(all_ids, key=natural)})
    stats = {"tasks": len(ordered), "audits": len(batches), "new": new, "dropped": dropped,
             "units": len(units), "words": sum(u["words"] for u in units.values()),
             "max_task_words": max([kept[i].get("words", 0) for i in ordered] or [0])}
    return rows, amend, stats


def run(check=False, dry_run=False, root="."):
    os.chdir(root)
    if not os.path.exists(INVENTORY):
        print("missing %s: run python3 tools/inventory.py first" % INVENTORY, file=sys.stderr)
        return 2
    with open(INVENTORY, encoding="utf-8") as f:
        inv = json.load(f)
    cfg = read_config()
    cap = int(cfg.get("translate_task_max_source_words", 4000))
    batch = int(cfg.get("audit_every_n_translate_tasks", 8))
    tr_path = os.path.join(GENERATED_DIR, TRANSLATE_FILE)
    am_path = os.path.join(GENERATED_DIR, AMEND_FILE)
    seed_ids = {t["id"] for t in load_jsonl(SEED)}
    rows, amend, st = plan(inv, cap, batch, load_jsonl(tr_path), pilot_paths(),
                           GATE_DEP if GATE_DEP in seed_ids else None,
                           GATE_TASK if GATE_TASK in seed_ids else None)
    print("plan_tasks: %d translate tasks, %d audits, %d units, %d words, max %d words/task "
          "(cap %d); %d new, %d dropped" % (st["tasks"], st["audits"], st["units"], st["words"],
                                          st["max_task_words"], cap, st["new"], len(st["dropped"])))
    over = [r["id"] for r in rows if r["kind"] == "translate" and r.get("words", 0) > cap]
    if over:
        print("WARNING: over the word cap (uneven segments): " + ", ".join(over))
    want = {tr_path: dumps(rows), am_path: dumps(amend)}
    stale = []
    for p, text in want.items():
        have = None
        if os.path.exists(p):
            with open(p, encoding="utf-8", newline="") as fh:
                have = fh.read()
        if have != text:
            stale.append(p)
    if check:
        for p in stale:
            print("STALE: " + p)
        return 1 if stale else 0
    if dry_run:
        return 0
    os.makedirs(GENERATED_DIR, exist_ok=True)
    for p in stale:
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(want[p])
        print("wrote " + p)
    if not stale:
        print("no change")
    return 0


# ---------------------------------------------------------------- Part II planning

S5_TASKS_FILE = "s5-families.jsonl"
S5_AMEND_FILE = "s5-amendments.jsonl"
S5_PREREQ = "S4-007"          # applies decision 11 to rules and prose before any family starts
S5_GATE = "S5-999"
SCOPE = "translation/localization-scope.yaml"
CODE_INVENTORY = "translation/part2/code-inventory.jsonl"

# (rank, reason, patterns). First matching rule wins; lower rank runs earlier. A pattern is an
# exact family name, a prefix ending in "*", or "src/*Suffix" (any src family ending in Suffix).
RISK_ORDER = (
    (0, "pilot re-run with the oracle (decision 11)",
     ("src/forth", "src/LinqChallenge1", "src/LinqChallenge2", "src/xaml", "src/cobol",
      "src/regex-pcre2", "lessons/solutions/b7-linq")),
    (1, "comment-only",
     ("src/awk", "src/make-gnu", "src/cmake", "src/find-gnu", "src/find-posix", "src/tcl",
      "src/lisp", "src/haskell", "src/javascript", "src/javascript-events",
      "lessons/solutions", "lessons/solutions/awk-port", "lessons/tools",
      "lessons/book/diagrams")),
    (2, "identifier renames", ("src/*Challenge1", "src/*Challenge2")),
    (3, "COBOL", ("src/cobol-weird",)),
    (4, "APL", ("src/apl", "src/apl-weird")),
    (5, "m4", ("src/m4",)),
    (6, "Forth parser tricks", ("src/forth-weird",)),
    (7, "Unicode and weird variants",
     ("src/haskell-weird", "src/lisp-weird", "src/tcl-weird", "src/javascript-weird",
      "src/awk-weird")),
    (8, "regex", ("src/regex-*",)),
    (9, "archive", ("src/tar-gnu", "src/tar-gnu-weird")),
    (10, "ed/ex hooks", ("src/ed-weird", "src/ex-weird")),
    (11, "adversarial", ("sandbox*",)),
)
SIZE_STEPS = ((400, "S"), (1500, "M"))     # work score thresholds; above the last is "L"
EMPTY_SIZE = {"files": 0, "lines": 0, "comments": 0, "strings": 0}


def risk_of(family):
    """Return (rank, reason) for a family, or None when no rule covers it."""
    for rank, reason, pats in RISK_ORDER:
        for pat in pats:
            if pat == family:
                return rank, reason
            if pat.startswith("src/*"):
                if family.startswith("src/") and family.endswith(pat[5:]):
                    return rank, reason
            elif pat.endswith("*") and family.startswith(pat[:-1]):
                return rank, reason
    return None


def read_scope(path=SCOPE):
    """Return {family: {"never": bool, "status": str}} from the scope file (flat rows)."""
    out = {}
    with open(path, encoding="utf-8") as f:
        for line in f:
            m = re.match(r'\s+"([^"]+)":\s*\{(.*)\}\s*$', line)
            if not m:
                continue
            body = m.group(2)
            st = re.search(r"status:\s*(\w+)", body)
            out[m.group(1)] = {"never": bool(re.search(r"never:\s*true", body)),
                               "status": st.group(1) if st else "frozen"}
    return out


def family_sizes(path=CODE_INVENTORY):
    sizes = {}
    for r in load_jsonl(path):
        s = sizes.setdefault(r["family"], dict(EMPTY_SIZE))
        s["files"] += 1
        s["lines"] += r.get("lines", 0)
        s["comments"] += len(r.get("comments", []))
        s["strings"] += len(r.get("strings", []))
    return sizes


def family_slug(family):
    return re.sub(r"[^a-z0-9]+", "-", family.replace("src/", "", 1).lower()).strip("-")


def size_of(sz):
    """Size class from counted work (lines plus five per comment and string). These are static
    counts: the pilot cost figures measured only refusals (translation/part2/pilot-measurements.md)."""
    score = sz["lines"] + 5 * (sz["comments"] + sz["strings"])
    for limit, name in SIZE_STEPS:
        if score <= limit:
            return name, score
    return "L", score


def family_task(tid, family, rank, reason, sz, deps):
    size, score = size_of(sz)
    return {
        "id": tid, "stage": 6, "kind": "localize-code",
        "title": "Part II S5: localize entry family %s (%s; %d files, %d lines, %d comments, %d strings)"
                 % (family, reason, sz["files"], sz["lines"], sz["comments"], sz["strings"]),
        "deps": deps, "size": size, "family": family, "risk": rank, "work": score,
        "accept": "oracle PASS (docker) or an exception in translation/exception-register.jsonl with NOT TESTED; "
                  "report translation/part2/reports/%s.md; python3 tools/part2_inv.py --check and "
                  "python3 tools/lock_code.py --check clean; verify --fast ok" % tid,
        "status": "todo", "attempts": 0,
    }


def plan_part2(scope, sizes, existing, batch, prereq=S5_PREREQ, gate=S5_GATE):
    """Pure function: return (rows, amendment_rows, stats). Raises ValueError on unplanned families."""
    fams = sorted((f for f, v in scope.items() if not v["never"]), key=natural)
    bad = [f for f in fams if risk_of(f) is None]
    if bad:
        raise ValueError("no RISK_ORDER rule for: " + ", ".join(bad))
    slugs = {}
    for f in fams:
        slugs.setdefault("S5-fam-" + family_slug(f), []).append(f)
    clash = {k: v for k, v in slugs.items() if len(v) > 1}
    if clash:
        raise ValueError("task id clash: %r" % clash)
    ex = {t["id"]: t for t in existing}
    order = sorted(fams, key=lambda f: (risk_of(f)[0], natural(f)))
    batches = [order[i:i + batch] for i in range(0, len(order), batch)] if batch > 0 else [order]
    rows, all_ids, prev = [], [], None
    for k, group in enumerate(batches, 1):
        ids = []
        for f in group:
            tid = "S5-fam-" + family_slug(f)
            old = ex.get(tid)
            ids.append(tid)
            if old is not None and old.get("status") != "todo":
                rows.append(old)       # started or finished: never touched
                continue
            rank, reason = risk_of(f)
            t = family_task(tid, f, rank, reason, sizes.get(f, EMPTY_SIZE),
                            [d for d in (prereq, prev) if d])
            if old is not None:
                for key in ("attempts", "notes"):
                    if key in old:
                        t[key] = old[key]
            rows.append(t)
        aid = "S5-audit-%d" % k
        old = ex.get(aid)
        if old is not None and old.get("status") != "todo":
            rows.append(old)
        else:
            a = {"id": aid, "stage": 6, "kind": "audit",
                 "title": "Part II S5 audit %d: fresh-context review of the localized families in %s"
                          % (k, ", ".join(ids)),
                 "deps": list(ids), "size": "S", "inputs": list(ids),
                 "accept": "translation/reviews/%s.md written; findings become review-fix tasks" % aid,
                 "status": "todo", "attempts": 0}
            if old is not None:
                a["attempts"] = old.get("attempts", 0)
                if "notes" in old:
                    a["notes"] = old["notes"]
            rows.append(a)
        all_ids += ids + [aid]
        prev = aid
    amend = [{"amend": gate, "add_deps": sorted(all_ids, key=natural)}] if gate else []
    return rows, amend, {"families": len(order), "audits": len(batches)}


def run_part2(check=False, dry_run=False, root="."):
    os.chdir(root)
    cfg = read_config()
    batch = int(cfg.get("audit_every_n_translate_tasks", 8))
    t_path = os.path.join(GENERATED_DIR, S5_TASKS_FILE)
    a_path = os.path.join(GENERATED_DIR, S5_AMEND_FILE)
    known = {t["id"] for t in load_jsonl(SEED)}
    if os.path.isdir(GENERATED_DIR):
        for p in sorted(os.listdir(GENERATED_DIR)):
            if p.endswith(".jsonl") and p not in (S5_TASKS_FILE, S5_AMEND_FILE):
                known |= {r.get("id") for r in load_jsonl(os.path.join(GENERATED_DIR, p))}
    try:
        rows, amend, st = plan_part2(read_scope(), family_sizes(), load_jsonl(t_path), batch,
                                     S5_PREREQ if S5_PREREQ in known else None,
                                     S5_GATE if S5_GATE in known else None)
    except ValueError as e:
        print("plan_tasks --part2: " + str(e), file=sys.stderr)
        return 2
    print("plan_tasks --part2: %d family tasks, %d audits" % (st["families"], st["audits"]))
    want = {t_path: dumps(rows), a_path: dumps(amend)}
    stale = []
    for p, text in want.items():
        have = None
        if os.path.exists(p):
            with open(p, encoding="utf-8", newline="") as fh:
                have = fh.read()
        if have != text:
            stale.append(p)
    if check:
        for p in stale:
            print("STALE: " + p)
        return 1 if stale else 0
    if dry_run:
        return 0
    os.makedirs(GENERATED_DIR, exist_ok=True)
    for p in stale:
        with open(p, "w", encoding="utf-8", newline="\n") as f:
            f.write(want[p])
        print("wrote " + p)
    if not stale:
        print("no change")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--part2", action="store_true")
    a = ap.parse_args(argv)
    if a.part2:
        return run_part2(a.check, a.dry_run)
    return run(a.check, a.dry_run)


if __name__ == "__main__":
    sys.exit(main())
