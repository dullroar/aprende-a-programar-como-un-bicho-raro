#!/usr/bin/env python3
"""translate: segment -> mask -> translator -> restore checks -> PO (plan 7.1, 7.2, section 9 "checkpoint").

For one Markdown file this tool walks the translatable segments in order and, for each one:

  1. builds a `translator_input` (schema segment.schema.json): the MASKED English, its placeholders,
     neighbour segments as read-only context, the glossary slice (terms found in the segment, the frozen
     timecard wording when a 40 appears, the assurance labels), the tier, the humor-register entry
     (playful / english_does) and the sentence limit;
  2. asks the translator backend (the `claude -p` CLI, or a replay file in tests) with prompts/translate.md
     as the system prompt and the input JSON as the user message;
  3. validates the reply against `translator_output`, checks the placeholders it reports, and runs every
     per-segment invariant (tools/invariants.check_segment) on the expanded text, reading the PO msgstr
     before macro expansion for the literal phase-letter check;
  4. writes the PO entry (msgstr = the Spanish MASKED text) and appends a ledger row.

Outcomes per segment: accepted (msgstr written, applies), needs-revision (msgstr written WITH the fuzzy
flag, never applied, findings kept in the entry comment), blocked (backend failure or unusable reply: nothing
written, the run stops). Nothing is ever marked accepted after an API failure.

Checkpoint and resume: the PO file is saved atomically after every segment, so a stopped run loses nothing.
A rerun skips every segment that already has an applied (non-empty, non-fuzzy) msgstr; `--from N` starts at
the Nth translatable segment (1-based) and `--limit K` stops after K calls (a deliberate partial run).
Accepted results are cached by (English masked text, context, glossary, house style, prompt, model).

Usage:
  python3 -I tools/translate.py FILE.md [--backend claude|replay:FILE] [--model sonnet] [--from N]
                                [--limit K] [--redo-fuzzy] [--task-id ID] [--dry-run] [--po PO]
                                [--ledger FILE] [--cache FILE]
  python3 -I tools/translate.py --show FILE.md [--from N]    print the translator input of one segment
"""
import hashlib
import json
import os
import re
import subprocess
import sys
import time

import jsonschema
import polib
import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
import apply as ap  # noqa: E402
import catalog  # noqa: E402
import invariants  # noqa: E402
import inventory  # noqa: E402
import mask  # noqa: E402
import segment  # noqa: E402

TR = os.path.join(ROOT, "translation")
PROMPT = os.path.join(TR, "prompts", "translate.md")
SCHEMA = os.path.join(TR, "schemas", "segment.schema.json")
LEDGER_SCHEMA = os.path.join(TR, "schemas", "ledger-row.schema.json")
CONTEXT_CHARS = 400
MAX_SYSTEM = 40000


class TranslateError(RuntimeError):
    """Run-level failure (bad file, bad PO, backend gone). Nothing wrong is written."""


class BackendError(TranslateError):
    """The translator could not be reached or answered with something unusable."""


# ------------------------------------------------------------------------------------------ helpers

def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def file_sha(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_schemas():
    with open(SCHEMA, encoding="utf-8") as f:
        root = json.load(f)
    return root


def validate(root, name, obj):
    """Validate obj against $defs/name of the segment schema. Returns a list of problem strings."""
    schema = {"$ref": "#/$defs/" + name, "$defs": root["$defs"]}
    v = jsonschema.Draft202012Validator(schema)
    return ["%s: %s" % ("/".join(str(p) for p in e.absolute_path) or "(root)", e.message)
            for e in sorted(v.iter_errors(obj), key=lambda e: list(e.absolute_path))]


def may_stay_english(src):
    """True for a segment whose correct Spanish is the English text: one capitalised proper noun ("Forth"), or a
    Mermaid label of at most two words with no English function word (`false`, `run: begin`). Anything longer,
    any other kind, or any text with an English function word must be translated."""
    words = invariants.WORD_RE.findall(mask.PH_RE.sub(" ", src.masked))
    if not words or len(words) > 2 or any(w.lower() in invariants.EN_STOP for w in words):
        return False
    if getattr(src, "kind", "") == "mermaid_label":
        return True
    return len(words) == 1 and words[0][0].isupper() and src.masked.strip() == words[0]


def now():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def atomic_save(po, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    po.save(tmp)
    os.replace(tmp, path)


def heading_text(text):
    return re.sub(r"^\s*#{1,6}\s+", "", text).strip()


# ------------------------------------------------------------------------------------------ glossary slice

class Glossary:
    """The part of the glossary a segment needs. Matching mirrors the I7 lint: plain words, case-insensitive,
    optional plural. Entries whose English is not a plain word (code, enums) are matched as a substring."""

    def __init__(self, data):
        self.data = data
        self.entries = []
        plain = re.compile(r"^[A-Za-z][A-Za-z' -]*$")
        for t in data.get("terms", []) or []:
            en, es = t.get("en"), t.get("es")
            if not isinstance(en, str) or not isinstance(es, str) or not en.strip():
                continue
            key = re.sub(r"\s*\(.*?\)\s*", " ", en).strip() or en
            if plain.match(key) and not t.get("literal"):
                rx = re.compile(r"(?<!\w)%s(?:s|es)?(?!\w)" % re.escape(key), re.I)
            else:
                rx = re.compile(re.escape(key), re.I)
            row = {"id": str(t.get("id") or key), "en": en, "es": es}
            if t.get("banned"):
                row["banned"] = [str(b) for b in t["banned"]]
            if t.get("gloss"):
                row["gloss"] = str(t["gloss"])
            self.entries.append((rx, row))
        frozen = data.get("frozen", {}) or {}
        tc = frozen.get("timecard_rule", {}) or {}
        self.timecard = None
        if tc.get("stop_phrase_alt"):
            self.timecard = {"id": "timecard-rule", "en": "strictly greater than 40",
                             "es": "%s / %s / %s" % (tc.get("stop_phrase_alt"), tc.get("stop_phrase"),
                                                      tc.get("exact_forty_phrase")),
                             "banned": [str(b) for b in tc.get("banned", []) or []]}
        self.labels = []
        for lab in (frozen.get("assurance_labels", {}) or {}).get("labels", []) or []:
            if lab.get("enum") and lab.get("es"):
                self.labels.append((re.compile(r"(?<!\w)%s(?!\w)" % re.escape(lab["enum"].replace("-", " ")), re.I),
                                    {"id": "assurance-" + lab["enum"], "en": lab["enum"], "es": lab["es"],
                                     "banned": [str(b) for b in lab.get("banned", []) or []]}))

    def slice(self, english):
        text = invariants.strip_ph(english)
        out = [row for rx, row in self.entries if rx.search(text)]
        if self.timecard and re.search(r"\b40\b|greater than|exactly", text):
            out.append(self.timecard)
        out.extend(row for rx, row in self.labels if rx.search(text))
        seen, uniq = set(), []
        for r in out:
            if r["id"] not in seen:
                seen.add(r["id"])
                uniq.append(r)
        return uniq


# ------------------------------------------------------------------------------------------ backends

class ReplayBackend:
    """Answers from a JSONL file of translator outputs (one object per line, keyed by segment_id), or from a
    plain callable. Used by the tests and for offline reruns. Raises BackendError for an unknown segment."""
    name = "replay"
    model = "replay"

    def __init__(self, source):
        self.calls = 0
        if callable(source):
            self.fn = source
        else:
            rows = {}
            with open(source, encoding="utf-8") as f:
                for ln in f:
                    if ln.strip():
                        r = json.loads(ln)
                        rows[r["segment_id"]] = r
            self.fn = lambda inp: rows[inp["segment_id"]] if inp["segment_id"] in rows else None

    def ask(self, system, inp):
        self.calls += 1
        try:
            out = self.fn(inp)
        except Exception as e:  # a test backend that raises models an API failure
            raise BackendError("replay backend failed: %s" % e) from None
        if out is None:
            raise BackendError("replay has no answer for %s" % inp["segment_id"])
        return out, {"input": 0, "output": 0}


class ClaudeBackend:
    """`claude -p` with every tool disabled: the model only sees the system prompt and the input JSON."""
    name = "claude"

    def __init__(self, model="sonnet", timeout=300, binary="claude"):
        self.model, self.timeout, self.binary = model, timeout, binary

    def ask(self, system, inp):
        cmd = [self.binary, "-p", "--output-format", "json", "--model", self.model, "--tools", "",
               "--no-session-persistence", "--system-prompt", system[:MAX_SYSTEM]]
        try:
            r = subprocess.run(cmd, input=json.dumps(inp, ensure_ascii=False), capture_output=True, text=True,
                               timeout=self.timeout, cwd=os.path.join(ROOT, "translation", "work"))
        except (OSError, subprocess.TimeoutExpired) as e:
            raise BackendError("claude CLI failed: %s" % e) from None
        if r.returncode != 0:
            raise BackendError("claude CLI exit %d: %s" % (r.returncode, r.stderr.strip()[:300]))
        try:
            env = json.loads(r.stdout)
        except ValueError:
            raise BackendError("claude CLI did not return JSON") from None
        if env.get("is_error"):
            raise BackendError("claude CLI error: %s" % str(env.get("result"))[:300])
        out = parse_reply(env.get("result", ""))
        use = env.get("usage", {}) or {}
        return out, {"input": int(use.get("input_tokens", 0) or 0), "output": int(use.get("output_tokens", 0) or 0)}


def parse_reply(text):
    """The reply must be one JSON object. One surrounding code fence is tolerated; anything else is an error."""
    if isinstance(text, dict):
        return text
    s = (text or "").strip()
    m = re.match(r"^```(?:json)?\s*\n(.*)\n```$", s, re.S)
    if m:
        s = m.group(1).strip()
    try:
        obj = json.loads(s)
    except ValueError:
        raise BackendError("reply is not a single JSON object: %r" % s[:80]) from None
    if not isinstance(obj, dict):
        raise BackendError("reply is not a JSON object")
    return obj


def make_backend(spec, model):
    if spec == "claude":
        return ClaudeBackend(model)
    if spec.startswith("replay:"):
        return ReplayBackend(spec[len("replay:"):])
    raise TranslateError("unknown backend %r (use claude or replay:FILE)" % spec)


# ------------------------------------------------------------------------------------------ the translator

class Translator:
    def __init__(self, backend, ctx=None, glossary=None, cat=None, edition=None, task_id="", ledger_path=None,
                 cache_path=None, word_limit=None):
        self.backend = backend
        self.ctx = ctx or invariants.load_context("es")
        self.cat = cat or catalog.load("es")
        self._en_cat = None
        if glossary is None:
            with open(os.path.join(TR, "glossary.es.yaml"), encoding="utf-8") as f:
                glossary = yaml.safe_load(f)
        self.glossary = Glossary(glossary)
        cfg = inventory.read_config(ROOT)
        self.edition = edition or cfg.get("edition_label", "v4-es.0-rc1")
        self.word_limit = word_limit or int(cfg.get("sentence_word_limit_N", 28))
        self.task_id = task_id
        self.ledger_path = ledger_path or os.path.join(TR, "ledger", "%s.jsonl" % self.edition)
        self.notes_path = os.path.splitext(self.ledger_path)[0] + ".notes.jsonl"
        self.cache_path = cache_path or os.path.join(TR, "work", "translate-cache.jsonl")
        self.schema = load_schemas()
        with open(PROMPT, encoding="utf-8") as f:
            self.system = f.read()
        self.prompt_sha = sha(self.system)
        self.glossary_sha = file_sha(os.path.join(TR, "glossary.es.yaml"))
        self.style_sha = file_sha(os.path.join(TR, "house-style.es.md"))
        self.cache = self._load_cache()

    # -- cache
    def _load_cache(self):
        rows = {}
        if os.path.isfile(self.cache_path):
            with open(self.cache_path, encoding="utf-8") as f:
                for ln in f:
                    if ln.strip():
                        r = json.loads(ln)
                        rows[r["key"]] = r["output"]
        return rows

    def _cache_key(self, inp):
        blob = json.dumps([inp["english_masked"], inp.get("context_before", ""), inp.get("context_after", ""),
                           inp["glossary_slice"], inp["tier"], inp["playful"], inp.get("word_limit_n"),
                           self.glossary_sha, self.style_sha, self.prompt_sha, self.backend.model],
                          ensure_ascii=False, sort_keys=True)
        return sha(blob)

    def _cache_put(self, key, output):
        self.cache[key] = output
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        with open(self.cache_path, "a", encoding="utf-8") as f:
            f.write(json.dumps({"key": key, "output": output}, ensure_ascii=False) + "\n")

    # -- input
    def lead_in_rows(self, masked):
        """Fixed bold lead-ins (invariant I11) are catalog text; tell the translator the exact Spanish."""
        m = re.match(r"\s*(?:[-*>] )?\*\*(?P<t>[^*]+?)\*\*", masked)
        if not m:
            return []
        if self._en_cat is None:
            self._en_cat = catalog.load("en")
        want = m.group("t").strip()
        rows = []
        for key in sorted(self._en_cat.keys()):
            if ".lead_in_" in key and self._en_cat.get(key) == want and key in self.cat.keys():
                rows.append({"id": "lead-in:" + key, "en": "**%s**" % want, "es": "**%s**" % self.cat.get(key),
                             "gloss": "Fixed lead-in from the catalog; write it exactly, bold, at the start."})
        return rows

    def build_input(self, seg, index, rel):
        items = seg.segments()
        cur = items[index]
        inp = {"segment_id": cur.id, "file": rel, "tier": self.ctx.tier_of(rel),
               "english_masked": cur.masked, "placeholders": list(cur.mapping),
               "glossary_slice": self.glossary.slice(cur.masked) + self.lead_in_rows(cur.masked)}
        before = items[index - 1].masked if index > 0 else ""
        after = items[index + 1].masked if index + 1 < len(items) else ""
        if before:
            inp["context_before"] = before[-CONTEXT_CHARS:]
        if after:
            inp["context_after"] = after[:CONTEXT_CHARS]
        row = self.ctx.humor.get(cur.text) or self.ctx.humor.get(heading_text(cur.text))
        inp["playful"] = bool(row)
        inp["english_does"] = row.get("english_does") if row else None
        inp["word_limit_n"] = self.word_limit
        return inp

    # -- one segment
    def translate_one(self, inp, src):
        """Returns (status, msgstr, findings, output, tokens). Raises BackendError when nothing usable came back."""
        probs = validate(self.schema, "translator_input", inp)
        if probs:
            raise TranslateError("bad translator input for %s: %s" % (inp["segment_id"], "; ".join(probs)))
        key = self._cache_key(inp)
        tokens = {"input": 0, "output": 0}
        out = self.cache.get(key)
        cached = out is not None
        if not cached:
            out, tokens = self.backend.ask(self.system, inp)
        probs = validate(self.schema, "translator_output", out)
        if probs:
            raise BackendError("unusable reply for %s: %s" % (inp["segment_id"], "; ".join(probs)))
        if out["segment_id"] != inp["segment_id"]:
            raise BackendError("reply is for %s, asked %s" % (out["segment_id"], inp["segment_id"]))
        text = out["translated_text"]
        findings = []
        seen = [m.group(0) for m in mask.PH_RE.finditer(text)]
        if list(out["placeholders_seen"]) != seen:
            findings.append("placeholders_seen does not list the placeholders of translated_text in order")
        raw = text
        expanded = text
        if "{{" in text:
            try:
                expanded = self.cat.expand(text)
            except catalog.CatalogError as e:
                findings.append("I14: %s" % e)
        if not findings or all(not f.startswith("I14") for f in findings):
            for f in invariants.check_segment(src, expanded, self.ctx, inp["file"], raw=raw):
                if f.inv == "I15" and "status 'pending'" in f.msg:
                    # The register row is filled by the translate task after this call (plan 6); I15 keeps
                    # failing in verify until it is, so this is a note here, not a rejection.
                    findings.append("REGISTER: %s" % f.msg)
                else:
                    findings.append("%s: %s" % (f.inv, f.msg))
        if (text.strip() == src.masked.strip() and mask.PH_RE.sub("", src.masked).strip()
                and not may_stay_english(src)):
            findings.append("TRANSLATE: the reply is the English text unchanged")
        if out["ambiguities"]:
            findings.append("AMBIGUITY: %d reported by the translator (see ledger)" % len(out["ambiguities"]))
        blocking = [f for f in findings if not f.startswith(("AMBIGUITY", "REGISTER"))]
        status = "needs-revision" if blocking else "accepted"
        if status == "accepted" and not cached:
            self._cache_put(key, out)
        return status, text, findings, out, tokens

    def ledger_row(self, inp, src, status, msgstr, out, tokens, findings):
        row = {"ledger_version": 1, "kind": "segment", "edition": self.edition, "ts": now(),
               "segment_id": inp["segment_id"], "file": inp["file"], "tier": inp["tier"], "status": status,
               "round": 0, "translator_model": "anthropic/%s" % self.backend.model,
               "prompt_sha256": self.prompt_sha, "glossary_sha256": self.glossary_sha,
               "house_style_sha256": self.style_sha, "english_sha256": sha(src.text),
               "spanish_sha256": sha(msgstr), "playful": inp["playful"], "exception_id": None,
               "tokens": tokens}
        if self.task_id:
            row["task_id"] = self.task_id
        return row

    def append_ledger(self, row, findings=(), out=None):
        """The ledger row has a closed schema; findings, ambiguities and the playful note go to a notes file."""
        os.makedirs(os.path.dirname(self.ledger_path), exist_ok=True)
        with open(self.ledger_path, "a", encoding="utf-8") as f:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
        note = {"segment_id": row["segment_id"], "ts": row["ts"], "findings": list(findings)}
        if out and out.get("ambiguities"):
            note["ambiguities"] = out["ambiguities"]
        if out and out.get("playful_note"):
            note["playful_note"] = out["playful_note"]
        if findings or len(note) > 3:
            with open(self.notes_path, "a", encoding="utf-8") as f:
                f.write(json.dumps(note, ensure_ascii=False) + "\n")

    # -- one file
    def run_file(self, path, po_path=None, start=1, limit=None, redo_fuzzy=False, dry_run=False, log=print):
        """Translate a file's segments into its PO. Returns a result dict; raises TranslateError on a bad run."""
        rel = ap.rel(path)
        text = segment.read_raw(path)
        try:
            seg = segment.Segmentation(text, rel)
        except segment.SegmentError as e:
            raise TranslateError("segmenter refused %s: %s" % (rel, e)) from None
        po_path = po_path or ap.po_path_for(rel)
        if os.path.isfile(po_path):
            po = ap.load_po(po_path)
        else:
            po = ap.new_po(seg, rel)
        items = seg.segments()
        by_id = {e.msgctxt: e for e in po}
        known = {b.id for b in items}
        orphans = [c for c in by_id if c not in known]
        if orphans:  # the file was probably applied (already Spanish): never mix its segments into the PO
            raise TranslateError("%s: %d PO entries match no segment of %s (is the file already applied? "
                                 "run `git checkout -- %s` first)" % (po_path, len(orphans), rel, rel))
        for b in items:  # a PO written by an older run may lack entries; never overwrite stale ones
            e = by_id.get(b.id)
            if e is None:
                e = polib.POEntry(msgctxt=b.id, msgid=b.masked, msgstr="",
                                  occurrences=[(rel, str(b.start + 1))])
                po.append(e)
                by_id[b.id] = e
            elif e.msgid != b.masked:
                raise TranslateError("%s: entry %s is stale (msgid is not the current English); "
                                     "refusing to overwrite it" % (po_path, b.id))
        res = {"file": rel, "po": po_path, "segments": len(items), "accepted": 0, "needs_revision": 0,
               "skipped": 0, "calls": 0, "stopped": None, "next_index": None, "register_pending": []}
        calls = 0
        for i, b in enumerate(items):
            n = i + 1
            e = by_id[b.id]
            done = bool(e.msgstr.strip()) and "fuzzy" not in e.flags
            if n < start or done or ("fuzzy" in e.flags and e.msgstr.strip() and not redo_fuzzy):
                res["skipped"] += 1
                continue
            if limit is not None and calls >= limit:
                res["stopped"] = "limit"
                res["next_index"] = n
                break
            inp = self.build_input(seg, i, rel)
            try:
                status, msgstr, findings, out, tokens = self.translate_one(inp, b)
            except BackendError as ex:
                res["stopped"] = "blocked: %s" % ex
                res["next_index"] = n
                if not dry_run:
                    atomic_save(po, po_path)
                log("BLOCKED at segment %d (%s): %s" % (n, b.id, ex))
                return res
            calls += 1
            e.msgstr = msgstr
            if inp["playful"] and any(f.startswith("REGISTER") for f in findings):
                res["register_pending"].append({"segment_id": b.id, "english": b.text,
                                                "spanish": msgstr, "playful_note": out.get("playful_note")})
            if status == "accepted":
                if "fuzzy" in e.flags:
                    e.flags.remove("fuzzy")
                e.comment = ""
                res["accepted"] += 1
            else:
                if "fuzzy" not in e.flags:
                    e.flags.append("fuzzy")
                e.comment = "; ".join(findings)[:900]
                res["needs_revision"] += 1
            if not dry_run:
                atomic_save(po, po_path)
                self.append_ledger(self.ledger_row(inp, b, status, msgstr, out, tokens, findings), findings, out)
            log("%4d/%d %s %s%s" % (n, len(items), b.id, status, ("  " + "; ".join(findings)[:160]) if findings else ""))
        res["calls"] = calls
        if res["stopped"] is None and not dry_run:
            atomic_save(po, po_path)
        return res


# ------------------------------------------------------------------------------------------ CLI

def main(argv):
    args = argv[1:]

    def opt(name, default=None):
        if name in args:
            i = args.index(name)
            if i + 1 >= len(args):
                raise SystemExit("%s needs a value" % name)
            val = args[i + 1]
            del args[i:i + 2]
            return val
        return default

    show = "--show" in args
    redo = "--redo-fuzzy" in args
    dry = "--dry-run" in args
    args = [a for a in args if a not in ("--show", "--redo-fuzzy", "--dry-run")]
    backend_spec = opt("--backend", "claude")
    model = opt("--model", "sonnet")
    start = int(opt("--from", "1"))
    limit = opt("--limit")
    limit = int(limit) if limit is not None else None
    task_id = opt("--task-id", "")
    po_arg = opt("--po")
    ledger_arg, cache_arg = opt("--ledger"), opt("--cache")
    if len(args) != 1:
        print(__doc__.split("Usage:")[1].rstrip())
        return 2
    path = args[0]
    try:
        if show:
            tr = Translator(ReplayBackend(lambda i: None), task_id=task_id)
            rel = ap.rel(path)
            seg = segment.Segmentation(segment.read_raw(path), rel)
            items = seg.segments()
            if not 1 <= start <= len(items):
                print("segment %d is out of range 1..%d" % (start, len(items)))
                return 2
            print(json.dumps(tr.build_input(seg, start - 1, rel), ensure_ascii=False, indent=2))
            return 0
        tr = Translator(make_backend(backend_spec, model), task_id=task_id, ledger_path=ledger_arg,
                        cache_path=cache_arg)
        res = tr.run_file(path, po_path=po_arg, start=start, limit=limit, redo_fuzzy=redo, dry_run=dry)
    except (TranslateError, segment.SegmentError, ap.ApplyError, OSError) as e:
        print("FAIL %s" % e)
        return 1
    print("translate %(file)s: %(accepted)d accepted, %(needs_revision)d needs-revision, %(skipped)d skipped, "
          "%(calls)d call(s), %(segments)d segment(s)" % res)
    for r in res["register_pending"]:
        print("register pending: %(segment_id)s %(english)r -> %(spanish)r (%(playful_note)s)" % r)
    if res["stopped"]:
        print("stopped (%s); resume with --from %s" % (res["stopped"], res["next_index"]))
        return 1 if str(res["stopped"]).startswith("blocked") else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
