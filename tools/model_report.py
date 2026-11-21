#!/usr/bin/env python3
"""tools/model_report.py: which models ran which iterations (evidence from loop/ledger/usage.jsonl).

Usage: python3 tools/model_report.py [--ledger PATH] [--since ITERATION] [--json]

The driver records, per iteration: the agent, the tier (standard or light), the model it REQUESTED
(from loop/CONFIG.yaml) and the model(s) the CLI REPORTED (Claude: modelUsage; Copilot: model-call
events; Codex: its session file). `model_mismatch` is true when the requested model is not the
primary reported one. Claude Code also uses a small helper model for side calls, so a second Claude
model in `models_all` is normal; only the primary (most output tokens) counts for the match.
Iterations recorded before this feature have no evidence and are grouped as `(no evidence)`.
Exit code 0, or 1 when any iteration shows a mismatch.
"""
import argparse
import collections
import json
import statistics
import sys


def load(path, since=0):
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line:
                    rows.append(json.loads(line))
    except FileNotFoundError:
        pass
    return [r for r in rows if r.get("iteration", 0) >= since]


def summarize(rows):
    groups = collections.OrderedDict()
    for r in rows:
        key = (r.get("agent", "claude(untagged)"), r.get("tier") or "-", r.get("model_reported") or "(no evidence)")
        g = groups.setdefault(key, {"n": 0, "secs": [], "in": 0, "out": 0, "usd": 0.0, "mismatch": 0})
        g["n"] += 1
        g["secs"].append(r.get("seconds") or 0)
        g["in"] += r.get("input_tokens") or 0
        g["out"] += r.get("output_tokens") or 0
        g["usd"] += float(r.get("cost_usd") or 0)
        g["mismatch"] += 1 if r.get("model_mismatch") else 0
    return groups


def usd(r):
    """Dollar cost of one iteration: Claude's reported USD, else Copilot's AI-credit estimate, else 0."""
    return float(r.get("cost_usd") or r.get("cost_est_usd") or 0)


def efficiency(rows):
    """Cost per unit of work, grouped by agent, tier, model, effort and task kind.

    Only iterations that finished their task (loop_result == done) count toward the unit metrics, so
    a cheap model that fails and gets retried does not look efficient. `done_rate` is the share of
    iterations in the group that ended `done`; `mean_attempts` is the task's attempt count when it ran.
    """
    groups = collections.OrderedDict()
    for r in rows:
        if r.get("tok_out") is None and not r.get("kind"):
            continue   # iteration recorded before this feature
        effort = r.get("effort_reported") or r.get("effort_requested") or "-"
        key = (r.get("agent", "?"), r.get("tier") or "-", r.get("model_reported") or r.get("model_requested") or "?",
               effort, r.get("kind") or "-")
        g = groups.setdefault(key, {"n": 0, "done": 0, "attempts": 0, "out": 0, "cache_read": 0, "fresh": 0,
                                    "usd": 0.0, "d_usd": 0.0, "d_words": 0, "d_segs": 0, "d_out": 0, "d_n": 0})
        g["n"] += 1
        g["attempts"] += r.get("attempts") or 0
        g["out"] += r.get("tok_out") or 0
        g["cache_read"] += r.get("tok_cache_read") or 0
        g["fresh"] += r.get("tok_fresh_in") or 0
        g["usd"] += usd(r)
        if r.get("loop_result") == "done":
            g["done"] += 1
            g["d_n"] += 1
            g["d_usd"] += usd(r)
            g["d_out"] += r.get("tok_out") or 0
            g["d_words"] += r.get("unit_words") or 0
            g["d_segs"] += r.get("unit_segments") or 0
    return groups


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--ledger", default="loop/ledger/usage.jsonl")
    ap.add_argument("--since", type=int, default=0)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rows = load(a.ledger, a.since)
    groups = summarize(rows)
    eff = efficiency(rows)
    if a.json:
        print(json.dumps({"|".join(k): {**v, "median_secs": statistics.median(v["secs"])} for k, v in groups.items()}, indent=1, default=list))
    else:
        print(f"{'agent':<18}{'tier':<10}{'model reported':<24}{'iters':>6}{'med s':>7}{'tok in':>10}{'tok out':>9}{'USD':>9}{'mismatch':>9}")
        for (agent, tier, model), v in groups.items():
            print(f"{agent:<18}{tier:<10}{model:<24}{v['n']:>6}{int(statistics.median(v['secs'])):>7}{v['in']:>10}{v['out']:>9}{v['usd']:>9.2f}{v['mismatch']:>9}")
        if eff:
            print("\nCost per unit of work (finished tasks only; USD is Claude-reported or the Copilot AI-credit estimate; Codex has no USD)")
            print(f"{'agent':<9}{'tier':<9}{'model':<20}{'effort':<8}{'kind':<12}{'n':>4}{'done%':>6}{'out tok/done':>13}{'cache-read':>12}{'USD/done':>9}{'USD/1k words':>13}{'out tok/seg':>12}")
            for (agent, tier, model, effort, kind), g in eff.items():
                dn = g["d_n"] or 1
                per_k = f"{g['d_usd'] / g['d_words'] * 1000:.2f}" if g["d_words"] and g["d_usd"] else "-"
                per_seg = f"{g['d_out'] / g['d_segs']:.0f}" if g["d_segs"] else "-"
                print(f"{agent:<9}{tier:<9}{model[:19]:<20}{effort:<8}{kind[:11]:<12}{g['n']:>4}{100 * g['done'] // g['n']:>5}%{g['d_out'] // dn:>13}{g['cache_read'] // g['n']:>12}{g['d_usd'] / dn:>9.2f}{per_k:>13}{per_seg:>12}")
            print("Quality is not in this table. Join iteration -> commit -> translation/ledger provenance and the audit findings before concluding a cheaper model is good enough.")
    return 1 if any(v["mismatch"] for v in groups.values()) else 0


if __name__ == "__main__":
    sys.exit(main())
