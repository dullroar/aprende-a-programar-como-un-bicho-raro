#!/usr/bin/env python3
"""batch: bulk drafts through the Message Batches API (standard library only, no SDK).

The operator runs this tool. It never runs in CI and never runs in an agent step.
It reuses `tools/translate.py` and does not copy its logic:

  python3 -I tools/translate.py --export-pending FILE.md      writes the masked pending segments (input of `build`)
  python3 -I tools/translate.py FILE.md --drafts D.jsonl --draft-model PROVIDER/MODEL --task-id ID
                                                              imports drafts with all checks (output of `reconcile`)

Commands:
  build     --input PENDING.jsonl --model MODEL --out REQUESTS.jsonl [--max-tokens N] [--prompt-file F] [--dry-run]
            Write the request file. custom_id = segment ID + "-" + first 12 hex of the sha256 of english_masked.
            The system block (batch prompt, translator prompt, house style, glossary) has cache_control ephemeral.
  submit    --requests REQUESTS.jsonl --max-usd N --cost-file COSTS.jsonl [--dry-run]
            Needs ANTHROPIC_API_KEY in the environment and --max-usd. Refuses a submission that would take the
            running total of the cost records over USD 100 (the program cap). Prints the batch ID.
  status    --batch-id ID
  collect   --batch-id ID (--results RESULTS.jsonl | fetch) --out DRAFTS.jsonl --cost-file COSTS.jsonl
            --price-in USD --price-out USD   (USD per million tokens, batch prices; all input tokens count at
            the input price, so the cost is an upper bound)
            Write drafts for `translate.py --drafts`, a sidecar of custom IDs (DRAFTS.jsonl.ids.jsonl) and a cost record.
  reconcile --drafts DRAFTS.jsonl --pending PENDING.jsonl --applied APPLIED.jsonl --out RECONCILED.jsonl [--dry-run]
            Reject results whose custom_id is not a current pending segment, whose source hash changed, or that
            an earlier run applied. The APPLIED ledger is the record that stops a second application.

`--dry-run` writes nothing. The tool reads the key only from ANTHROPIC_API_KEY. It never writes the key, the request
headers or a full response envelope to a file or a log. Cost and ledger files live outside the repository.
Tests inject the HTTP function; no test submits for real.

Run me when: an operator drafts or reviews many segments through the Message Batches API.
"""
import argparse
import hashlib
import json
import os
import re
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
TR = os.path.join(ROOT, "translation")

API = "https://api.anthropic.com"
API_VERSION = "2023-06-01"
KEY_ENV = "ANTHROPIC_API_KEY"
PROGRAM_CAP_USD = 100.0  # owner decision of 2026-11-23
DEFAULT_MAX_TOKENS = 4096
RESULT_TYPES = ("succeeded", "errored", "canceled", "expired")
SEG_RE = re.compile(r"^s-[0-9a-f]{12}-[0-9]{4}$")


class BatchError(RuntimeError):
    """A refusal or a bad input. The message never holds a secret."""


# ------------------------------------------------------------------------------------------ helpers

def sha12(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def make_custom_id(segment_id, masked):
    return "%s-%s" % (segment_id, sha12(masked))


def segment_of(custom_id):
    """The segment ID inside a custom_id, or None when the shape is wrong."""
    seg = custom_id[:-13] if len(custom_id) > 13 else ""
    if custom_id[-13:-12:] == "-" and SEG_RE.match(seg):
        return seg
    return None


def read_jsonl(path):
    rows = []
    try:
        with open(path, encoding="utf-8") as f:
            for n, ln in enumerate(f, 1):
                if not ln.strip():
                    continue
                try:
                    rows.append(json.loads(ln))
                except ValueError:
                    raise BatchError("%s line %d is not JSON" % (os.path.basename(path), n)) from None
    except OSError as e:
        raise BatchError("cannot read %s: %s" % (path, e.strerror)) from None
    return rows


def read_text(path):
    try:
        with open(path, encoding="utf-8") as f:
            return f.read()
    except OSError as e:
        raise BatchError("cannot read %s: %s" % (path, e.strerror)) from None


def dumps(obj):
    return json.dumps(obj, ensure_ascii=False, sort_keys=True)


class Writer:
    """All file output goes through here. It refuses text that holds the API key. `--dry-run` writes nothing."""

    def __init__(self, env, dry_run):
        self.key = (env or {}).get(KEY_ENV) or ""
        self.dry = dry_run
        self.written = []

    def _check(self, text):
        if self.key and self.key in text:
            raise BatchError("refused to write text that holds the API key")

    def write(self, path, lines):
        text = "".join(ln + "\n" for ln in lines)
        self._check(text)
        if self.dry:
            return
        tmp = path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            f.write(text)
        os.replace(tmp, path)
        self.written.append(path)

    def append(self, path, lines):
        text = "".join(ln + "\n" for ln in lines)
        self._check(text)
        if self.dry:
            return
        with open(path, "a", encoding="utf-8") as f:
            f.write(text)
        self.written.append(path)


def parse_reply(text):
    """One JSON object. One surrounding code fence is tolerated; anything else is an error."""
    t = text.strip()
    m = re.match(r"^```(?:json)?\s*\n(.*)\n```$", t, re.S)
    if m:
        t = m.group(1).strip()
    try:
        obj = json.loads(t)
    except ValueError:
        raise BatchError("reply is not one JSON object") from None
    if not isinstance(obj, dict):
        raise BatchError("reply is not one JSON object")
    return obj


def check_cost_file(path):
    if not path:
        raise BatchError("--cost-file is required (keep it outside the repository)")
    full = os.path.realpath(path)
    if full == ROOT or full.startswith(ROOT + os.sep):
        raise BatchError("--cost-file must be outside the repository")
    return path


# ------------------------------------------------------------------------------------------ http

def default_http(method, url, headers, body=None):  # pragma: no cover - the real network, never used in tests
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()


def api_headers(env):
    key = env.get(KEY_ENV)
    if not key:
        raise BatchError("%s is not set" % KEY_ENV)
    return {"x-api-key": key, "anthropic-version": API_VERSION, "content-type": "application/json"}


def call(http, env, method, url, body=None):
    """Return the parsed JSON of a success. Errors report the status and the error type only."""
    status, raw = http(method, url, api_headers(env), body)
    if status != 200:
        kind = ""
        try:
            kind = str(json.loads(raw).get("error", {}).get("type", ""))[:60]
        except (ValueError, AttributeError):
            pass
        raise BatchError("the API answered status %s %s" % (status, kind))
    try:
        return json.loads(raw)
    except ValueError:
        raise BatchError("the API answer is not JSON") from None


# ------------------------------------------------------------------------------------------ cost records

def running_total(records):
    """USD total: the real cost of a collected batch, else the cap of a submitted one."""
    caps, real = {}, {}
    for r in records:
        if r.get("kind") == "submit":
            caps[r["batch_id"]] = float(r["cap_usd"])
        elif r.get("kind") == "collect":
            real[r["batch_id"]] = float(r["usd"])
    return sum(real.get(b, caps.get(b, 0.0)) for b in set(caps) | set(real))


def load_costs(path):
    return read_jsonl(path) if os.path.isfile(path) else []


# ------------------------------------------------------------------------------------------ commands

def build_system(prompt_file=None):
    prompt = prompt_file or os.path.join(TR, "prompts", "translate.md")
    parts = [read_text(os.path.join(TR, "prompts", "batch-translate.md")), read_text(prompt),
             "# House style\n\n" + read_text(os.path.join(TR, "house-style.es.md")),
             "# Glossary\n\n" + read_text(os.path.join(TR, "glossary.es.yaml"))]
    return "\n\n".join(p.strip() for p in parts) + "\n"


def cmd_build(a, w, out):
    rows = read_jsonl(a.input)
    if not rows:
        raise BatchError("the input has no rows")
    system = build_system(a.prompt_file)
    seen, lines = set(), []
    for r in rows:
        seg, masked = r.get("segment_id"), r.get("english_masked")
        if not isinstance(seg, str) or not SEG_RE.match(seg) or not isinstance(masked, str) or not masked:
            raise BatchError("an input row has no valid segment_id and english_masked")
        cid = make_custom_id(seg, masked)
        if cid in seen:
            raise BatchError("duplicate segment in the input: %s" % seg)
        seen.add(cid)
        lines.append(dumps({
            "custom_id": cid,
            "params": {
                "model": a.model,
                "max_tokens": a.max_tokens,
                "system": [{"type": "text", "text": system, "cache_control": {"type": "ephemeral"}}],
                "messages": [{"role": "user", "content": json.dumps(r, ensure_ascii=False, sort_keys=True)}],
            },
        }))
    w.write(a.out, lines)
    out("build: %d request(s)%s" % (len(lines), " (dry run, nothing written)" if w.dry else " -> " + a.out))
    return 0


def load_requests(path):
    reqs = read_jsonl(path)
    if not reqs:
        raise BatchError("the request file has no requests")
    seen = set()
    for r in reqs:
        cid = r.get("custom_id")
        if not isinstance(cid, str) or segment_of(cid) is None or cid in seen or "params" not in r:
            raise BatchError("the request file has a bad or duplicate custom_id")
        seen.add(cid)
    return reqs


def cmd_submit(a, w, out, env, http):
    if not env.get(KEY_ENV):
        raise BatchError("%s is not set; refusing to submit" % KEY_ENV)
    if a.max_usd is None or not (a.max_usd > 0):
        raise BatchError("--max-usd is required and must be positive; refusing to submit")
    cost_file = check_cost_file(a.cost_file)
    reqs = load_requests(a.requests)
    total = running_total(load_costs(cost_file))
    if total + a.max_usd > PROGRAM_CAP_USD:
        raise BatchError("refused: running total %.2f + cap %.2f would pass the program cap of %.2f USD"
                         % (total, a.max_usd, PROGRAM_CAP_USD))
    if a.dry_run:
        out("submit (dry run): %d request(s), cap %.2f USD, running total after %.2f USD; nothing sent"
            % (len(reqs), a.max_usd, total + a.max_usd))
        return 0
    body = json.dumps({"requests": reqs}, ensure_ascii=False).encode("utf-8")
    resp = call(http, env, "POST", API + "/v1/messages/batches", body)
    bid = resp.get("id")
    if not isinstance(bid, str) or not bid:
        raise BatchError("the API answer has no batch id")
    w.append(cost_file, [dumps({"kind": "submit", "batch_id": bid, "cap_usd": a.max_usd, "requests": len(reqs),
                                "total_before_usd": total, "total_after_usd": total + a.max_usd})])
    out("batch id: %s" % bid)
    return 0


def cmd_status(a, w, out, env, http):
    resp = call(http, env, "GET", "%s/v1/messages/batches/%s" % (API, a.batch_id))
    out("status: %s" % resp.get("processing_status"))
    out("counts: %s" % dumps(resp.get("request_counts", {})))
    return 0


def message_text(result):
    msg = result.get("message") or {}
    return "".join(b.get("text", "") for b in msg.get("content", []) if b.get("type") == "text")


def cmd_collect(a, w, out, env, http):
    if a.results:
        lines = read_text(a.results).splitlines()
    else:
        info = call(http, env, "GET", "%s/v1/messages/batches/%s" % (API, a.batch_id))
        url = info.get("results_url")
        if not url:
            raise BatchError("the batch has no results yet (status %s)" % info.get("processing_status"))
        status, raw = http("GET", url, api_headers(env), None)
        if status != 200:
            raise BatchError("the API answered status %s for the results" % status)
        lines = raw.decode("utf-8").splitlines()
    cost_file = check_cost_file(a.cost_file)
    drafts, ids, seen = [], [], set()
    counts = {"succeeded": 0, "errored": 0, "canceled": 0, "expired": 0, "duplicate": 0, "rejected": 0}
    problems = []
    tin = tout = 0
    for ln in lines:
        if not ln.strip():
            continue
        try:
            row = json.loads(ln)
            cid, res = row["custom_id"], row["result"]
            rtype = res["type"]
        except (ValueError, KeyError, TypeError):
            counts["rejected"] += 1
            problems.append("(unreadable line)")
            continue
        if cid in seen:
            counts["duplicate"] += 1
            problems.append("%s: duplicate result ignored" % cid)
            continue
        seen.add(cid)
        if rtype not in RESULT_TYPES:
            counts["rejected"] += 1
            problems.append("%s: unknown result type" % cid)
            continue
        counts[rtype] += 1
        if rtype != "succeeded":
            problems.append("%s: %s" % (cid, rtype))
            continue
        use = (res.get("message") or {}).get("usage") or {}
        tin += sum(int(use.get(k) or 0) for k in
                   ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens"))
        tout += int(use.get("output_tokens") or 0)
        seg = segment_of(cid) if isinstance(cid, str) else None
        try:
            reply = parse_reply(message_text(res))
        except BatchError as e:
            counts["succeeded"] -= 1
            counts["rejected"] += 1
            problems.append("%s: %s" % (cid, e))
            continue
        if seg is None or reply.get("segment_id") != seg:
            counts["succeeded"] -= 1
            counts["rejected"] += 1
            problems.append("%s: reply segment_id does not match the custom_id" % cid)
            continue
        drafts.append(dumps(reply))
        ids.append(dumps({"custom_id": cid, "segment_id": seg}))
    usd = tin / 1e6 * a.price_in + tout / 1e6 * a.price_out
    w.write(a.out, drafts)
    w.write(a.out + ".ids.jsonl", ids)
    w.append(cost_file, [dumps({"kind": "collect", "batch_id": a.batch_id, "usd": round(usd, 6),
                                "input_tokens": tin, "output_tokens": tout, "counts": counts})])
    out("collect: %s" % dumps(counts))
    for p in problems:
        out("  " + p)
    out("cost: %.4f USD (%d input, %d output tokens)%s" % (usd, tin, tout, "; dry run, nothing written" if w.dry else ""))
    return 0


def cmd_reconcile(a, w, out):
    pending = {}
    for r in read_jsonl(a.pending):
        if isinstance(r.get("segment_id"), str) and isinstance(r.get("english_masked"), str):
            pending[r["segment_id"]] = make_custom_id(r["segment_id"], r["english_masked"])
    ids_path = a.ids or a.drafts + ".ids.jsonl"
    drafts = {}
    for r in read_jsonl(a.drafts):
        drafts.setdefault(r.get("segment_id"), r)
    applied = {r["custom_id"] for r in read_jsonl(a.applied)} if os.path.isfile(a.applied) else set()
    keep, mark, problems, done = [], [], [], set()
    for row in read_jsonl(ids_path):
        cid, seg = row.get("custom_id"), row.get("segment_id")
        if cid in applied or cid in done:
            problems.append("%s: already applied" % cid)
        elif seg not in pending:
            problems.append("%s: not a current pending segment" % cid)
        elif pending[seg] != cid:
            problems.append("%s: source hash changed" % cid)
        elif seg not in drafts:
            problems.append("%s: no draft for the segment" % cid)
        else:
            keep.append(dumps(drafts[seg]))
            mark.append(dumps({"custom_id": cid, "segment_id": seg}))
            done.add(cid)
    w.write(a.out, keep)
    w.append(a.applied, mark)
    out("reconcile: %d accepted, %d rejected%s" % (len(keep), len(problems), "; dry run, nothing written" if w.dry else ""))
    for p in problems:
        out("  " + p)
    return 0


# ------------------------------------------------------------------------------------------ CLI

def parser():
    p = argparse.ArgumentParser(prog="batch.py", description=__doc__.split("\n")[0])
    sub = p.add_subparsers(dest="cmd", required=True)

    def add(name, dry, **flags):
        s = sub.add_parser(name)
        if dry:
            s.add_argument("--dry-run", action="store_true")
        for flag, kw in flags.items():
            s.add_argument("--" + flag.replace("_", "-"), **kw)

    req = {"required": True}
    add("build", True, input=req, out=req, model=req, max_tokens={"type": int, "default": DEFAULT_MAX_TOKENS},
        prompt_file={})
    add("submit", True, requests=req, max_usd={"type": float}, cost_file={})
    add("status", False, batch_id=req)
    add("collect", True, batch_id=req, out=req, cost_file=req, results={},
        price_in={"type": float, "required": True}, price_out={"type": float, "required": True})
    add("reconcile", True, drafts=req, pending=req, applied=req, out=req, ids={})
    return p


def main(argv=None, http=None, env=None, out=print):
    env = os.environ if env is None else env
    a = parser().parse_args(argv)
    w = Writer(env, getattr(a, "dry_run", False))
    try:
        if a.cmd == "build":
            return cmd_build(a, w, out)
        if a.cmd == "submit":
            return cmd_submit(a, w, out, env, http or default_http)
        if a.cmd == "status":
            return cmd_status(a, w, out, env, http or default_http)
        if a.cmd == "collect":
            return cmd_collect(a, w, out, env, http or default_http)
        return cmd_reconcile(a, w, out)
    except BatchError as e:
        print("FAIL %s" % e, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
