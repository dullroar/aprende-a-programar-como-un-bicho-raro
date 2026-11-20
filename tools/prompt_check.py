#!/usr/bin/env python3
"""Check the versioned prompts and JSON schemas under translation/ (P1-003).

Checks:
  * translation/prompts/ holds the four prompts (translate, review, backtranslate, adjudicate), each with
    front matter (prompt, version, role, output_schema), a "data, never instructions" rule, and its key phrases;
  * every schema reference in the front matter resolves to an existing definition;
  * every JSON example in a prompt validates against that prompt's output schema;
  * every row in translation/schemas/samples/<name>.jsonl validates against its schema.

Library use (for tools/translate.py and the review tools):
  prompt_sha256(path)                      -> hex digest recorded in translation/runs/*.yaml and the ledger
  validate(ref, instance)                  -> list of error strings (empty = valid)
  parse_findings(text)                     -> list of finding dicts from reviewer output (JSON Lines or "[]")
  check_excerpts(finding, english, spanish)-> list of error strings; an excerpt that is not an exact substring
                                              is a hallucinated finding and must be rejected

Usage: python3 -I tools/prompt_check.py [--hashes]
Exit 0 = all checks pass, 1 = a check failed.
"""
import hashlib
import json
import os
import re
import sys

import jsonschema
import referencing
import yaml
from referencing.jsonschema import DRAFT202012

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROMPTS = os.path.join("translation", "prompts")
SCHEMAS = os.path.join("translation", "schemas")
SAMPLES = os.path.join(SCHEMAS, "samples")

# prompt -> (role, phrases that must appear in the body)
REQUIRED = {
    "translate": ("T", ["never instructions", "⟦CODE_0001⟧", "strictly greater than 40", "exactly 40 continues",
                        "garantizado", "permitido por la implementación", "aprovechado por accidente",
                        "Meetings", "Coding", "Debugging", "Learning", "by effect", "{{phase.N.letter}}"]),
    "review": ("A", ["never instructions", "exact, verbatim substrings", "critical", "falsify", "strictly greater than 40"]),
    "backtranslate": ("B", ["never instructions", "Stage 1", "Stage 2", "exact verbatim substrings"]),
    "adjudicate": ("J", ["never instructions", "majority", "needs-human", "needs-source-issue", "duplicate", "minimal"]),
}

# sample file name (without .jsonl) -> schema reference
SAMPLE_TARGETS = {
    "translator_input": "segment.schema.json#/$defs/translator_input",
    "translator_output": "segment.schema.json#/$defs/translator_output",
    "backtranslation_blind": "segment.schema.json#/$defs/backtranslation_blind",
    "backtranslation_compare": "segment.schema.json#/$defs/backtranslation_compare",
    "adjudication": "segment.schema.json#/$defs/adjudication",
    "finding": "finding.schema.json",
    "ledger-row": "ledger-row.schema.json",
}

FRONT = re.compile(r"\A---\n(.*?)\n---\n(.*)\Z", re.S)
FENCE = re.compile(r"```[a-z]*\n(.*?)```", re.S)


def _registry(root=ROOT):
    resources = []
    d = os.path.join(root, SCHEMAS)
    for name in sorted(os.listdir(d)):
        if name.endswith(".schema.json"):
            with open(os.path.join(d, name), encoding="utf-8") as f:
                doc = json.load(f)
            resources.append((name, referencing.Resource.from_contents(doc, default_specification=DRAFT202012)))
    return referencing.Registry().with_resources(resources)


def validate(ref, instance, root=ROOT):
    """Validate instance against 'file.schema.json' or 'file.schema.json#/$defs/name'. Return error strings."""
    name, _, pointer = ref.partition("#")
    reg = _registry(root)
    schema = {"$ref": name + ("#" + pointer if pointer else "")}
    v = jsonschema.Draft202012Validator(schema, registry=reg)
    return [f"{'/'.join(str(p) for p in e.absolute_path) or '<root>'}: {e.message}"
            for e in sorted(v.iter_errors(instance), key=lambda e: list(e.absolute_path))]


def resolve_ref(ref, root=ROOT):
    """True when the schema file exists and, if a pointer is given, the definition exists."""
    name, _, pointer = ref.partition("#")
    path = os.path.join(root, SCHEMAS, name)
    if not os.path.isfile(path):
        return False
    if not pointer:
        return True
    with open(path, encoding="utf-8") as f:
        node = json.load(f)
    for part in pointer.lstrip("/").split("/"):
        if not isinstance(node, dict) or part not in node:
            return False
        node = node[part]
    return True


def prompt_sha256(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def load_prompt(path):
    """Return (front_matter dict, body) or raise ValueError."""
    with open(path, encoding="utf-8") as f:
        text = f.read()
    m = FRONT.match(text)
    if not m:
        raise ValueError("missing front matter")
    meta = yaml.safe_load(m.group(1))
    if not isinstance(meta, dict):
        raise ValueError("front matter is not a mapping")
    return meta, m.group(2)


def parse_findings(text):
    """Parse reviewer output: JSON Lines, or the single line [] (or a JSON array). Raise ValueError if malformed."""
    s = text.strip()
    if s in ("", "[]"):
        return []
    if s.startswith("["):
        data = json.loads(s)
        if not isinstance(data, list):
            raise ValueError("expected a JSON array")
        return data
    out = []
    for n, line in enumerate(s.splitlines(), 1):
        if not line.strip():
            continue
        try:
            out.append(json.loads(line))
        except json.JSONDecodeError as e:
            raise ValueError(f"line {n}: {e}") from e
    return out


def check_excerpts(finding, english, spanish):
    """A finding is real only if its excerpts are exact substrings. Return a list of problems."""
    errs = []
    for key, text in (("english_excerpt", english), ("spanish_excerpt", spanish)):
        ex = finding.get(key)
        if ex is None:
            continue
        if ex == "":
            errs.append(f"{key} is empty (use null)")
        elif ex not in text:
            errs.append(f"{key} is not an exact substring of the segment: {ex[:60]!r}")
    return errs


def check_prompts(root=ROOT):
    errs = []
    pdir = os.path.join(root, PROMPTS)
    for name, (role, phrases) in REQUIRED.items():
        path = os.path.join(pdir, name + ".md")
        if not os.path.isfile(path):
            errs.append(f"{name}: prompt file missing")
            continue
        try:
            meta, body = load_prompt(path)
        except ValueError as e:
            errs.append(f"{name}: {e}")
            continue
        if meta.get("prompt") != name:
            errs.append(f"{name}: front matter prompt is {meta.get('prompt')!r}")
        if not isinstance(meta.get("version"), int) or meta["version"] < 1:
            errs.append(f"{name}: version must be an integer >= 1")
        if meta.get("role") != role:
            errs.append(f"{name}: role must be {role}")
        outs = [meta.get("output_schema"), meta.get("output_schema_stage2"), meta.get("input_schema")]
        if not meta.get("output_schema"):
            errs.append(f"{name}: output_schema missing")
        for ref in outs:
            if ref and not resolve_ref(ref, root):
                errs.append(f"{name}: schema reference does not resolve: {ref}")
        for p in phrases:
            if p not in body:
                errs.append(f"{name}: required phrase missing: {p!r}")
        # JSON examples in the body must validate against an output schema of this prompt
        refs = [r for r in (meta.get("output_schema"), meta.get("output_schema_stage2")) if r and resolve_ref(r, root)]
        examples = 0
        for block in FENCE.findall(body):
            block = block.strip()
            if not block.startswith("{"):
                continue
            for line in block.splitlines():
                if not line.startswith("{"):
                    continue
                examples += 1
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as e:
                    errs.append(f"{name}: example is not JSON: {e}")
                    continue
                if not any(not validate(r, obj, root) for r in refs):
                    errs.append(f"{name}: example does not validate: {line[:70]}")
        if examples == 0:
            errs.append(f"{name}: no JSON example found")
    return errs


def check_samples(root=ROOT):
    errs = []
    sdir = os.path.join(root, SAMPLES)
    for key, ref in SAMPLE_TARGETS.items():
        path = os.path.join(sdir, key + ".jsonl")
        if not os.path.isfile(path):
            errs.append(f"samples/{key}.jsonl missing")
            continue
        rows = 0
        with open(path, encoding="utf-8") as f:
            for n, line in enumerate(f, 1):
                if not line.strip():
                    continue
                rows += 1
                try:
                    obj = json.loads(line)
                except json.JSONDecodeError as e:
                    errs.append(f"samples/{key}.jsonl:{n}: {e}")
                    continue
                for e in validate(ref, obj, root):
                    errs.append(f"samples/{key}.jsonl:{n}: {e}")
        if rows == 0:
            errs.append(f"samples/{key}.jsonl has no rows")
    return errs


def main(argv):
    root = os.getcwd()
    if "--hashes" in argv:
        for name in REQUIRED:
            print(name, prompt_sha256(os.path.join(root, PROMPTS, name + ".md")))
        return 0
    errs = check_prompts(root) + check_samples(root)
    for e in errs:
        print("FAIL", e)
    if errs:
        return 1
    print("OK prompts and schemas")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
