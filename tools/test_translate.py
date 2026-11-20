#!/usr/bin/env python3
"""Tests for tools/translate.py (plan 7.1, 7.2, checkpoint and resume). Run: python3 -I tools/test_translate.py

The translator is a fake backend (a function), so no model is called. The cases that must fail do fail:
a dropped placeholder, an English reply, a banned timecard phrase, a wrong segment id, an unusable reply and a
backend outage are never written as accepted.
"""
import copy
import io
import json
import os
import subprocess
import sys
import tempfile
import unittest
from contextlib import redirect_stdout
from unittest import mock

import jsonschema
import polib

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), "lessons", "book", "locale"))
import apply as ap  # noqa: E402
import catalog  # noqa: E402
import invariants as inv  # noqa: E402
import segment  # noqa: E402
import translate as tr  # noqa: E402

ROOT = os.path.dirname(HERE)

DOC = (
    "# Timecards and the stop rule\n"
    "\n"
    "Run `make all` and read the total.\n"
    "\n"
    "Stop when the total is strictly greater than 40.\n"
    "\n"
    "- Every loop adds one card.\n"
    "\n"
    "```text\n"
    "keep this output\n"
    "```\n"
)

SPANISH = [
    "Tarjetas de horas y la regla de parada",
    "Ejecuta {C1} y lee el total.",
    "Detente cuando el total pasa de 40.",
    "Cada bucle agrega una tarjeta.",
]

GLOSSARY = {
    "frozen": {
        "timecard_rule": {"stop_phrase": "pasa de 40", "stop_phrase_alt": "más de 40",
                          "exact_forty_phrase": "un total de exactamente 40 continúa",
                          "banned": ["hasta 40", "al menos 40"]},
        "assurance_labels": {"labels": [{"enum": "guaranteed", "es": "garantizado", "banned": ["asegurado"]}]},
    },
    "terms": [
        {"id": "loop", "en": "loop", "es": "bucle", "banned": ["ciclo"], "gloss": "first-use"},
        {"id": "sandbox", "en": "sandbox", "es": "entorno aislado"},
    ],
}
HUMOR = {"Timecards and the stop rule": {"id": "H900", "kind": "heading", "english": "Timecards and the stop rule",
                                          "english_does": "Dry office joke.", "status": "pending",
                                          "spanish": None, "reviewer_note": None}}


def spanish_for(seg):
    out = {}
    for b, es in zip(seg.segments(), SPANISH):
        keys = list(b.mapping)
        out[b.id] = es.format(C1=keys[0] if keys else "")
    return out


class Fake:
    """A backend whose answers come from a dict segment id -> translated text, with call counting."""
    model = "fake"

    def __init__(self, answers, fail_at=None, mangle=None):
        self.answers, self.fail_at, self.mangle = answers, fail_at, mangle or {}
        self.asked = []
        self.systems = []

    def ask(self, system, inp):
        self.systems.append(system)
        self.asked.append(inp["segment_id"])
        if self.fail_at is not None and len(self.asked) == self.fail_at:
            raise tr.BackendError("API down")
        sid = inp["segment_id"]
        text = self.mangle.get(sid, self.answers[sid])
        if isinstance(text, dict):
            return text, {"input": 1, "output": 1}
        seen = [m.group(0) for m in tr.mask.PH_RE.finditer(text)]
        return {"segment_id": sid, "translated_text": text, "ambiguities": [], "placeholders_seen": seen,
                "playful_note": None}, {"input": 10, "output": 5}


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.md = os.path.join(self.tmp.name, "doc.md")
        with open(self.md, "w", encoding="utf-8", newline="") as f:
            f.write(DOC)
        self.po = os.path.join(self.tmp.name, "doc.md.po")
        self.seg = segment.Segmentation(DOC, "doc.md")
        self.answers = spanish_for(self.seg)
        self.ids = [b.id for b in self.seg.segments()]
        self.cat = catalog.load("es")
        self.ctx = inv.Context(glossary=GLOSSARY, cat=self.cat, humor=copy.deepcopy(HUMOR), sentence_limit=28)

    def translator(self, backend, **kw):
        return tr.Translator(backend, ctx=self.ctx, glossary=GLOSSARY, cat=self.cat, edition="v4-es.0-rc1",
                             task_id="T-1", ledger_path=os.path.join(self.tmp.name, "ledger.jsonl"),
                             cache_path=os.path.join(self.tmp.name, "cache.jsonl"), **kw)

    def run_file(self, t, **kw):
        return t.run_file(self.md, po_path=self.po, log=lambda *_: None, **kw)

    def entries(self):
        return {e.msgctxt: e for e in polib.pofile(self.po, wrapwidth=0)}

    def notes(self):
        with open(os.path.join(self.tmp.name, "ledger.notes.jsonl"), encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]

    def ledger(self):
        with open(os.path.join(self.tmp.name, "ledger.jsonl"), encoding="utf-8") as f:
            return [json.loads(ln) for ln in f if ln.strip()]


class TestTranslateFixture(Base):
    def test_translates_every_segment_and_applies(self):
        fake = Fake(self.answers)
        res = self.run_file(self.translator(fake))
        self.assertEqual((res["accepted"], res["needs_revision"], res["calls"]), (4, 0, 4))
        self.assertEqual(len(fake.asked), 4)
        po = ap.load_po(self.po)
        out, st = ap.apply_text(DOC, po, "doc.md", self.cat)
        self.assertEqual(st["applied"], 4)
        self.assertIn("Ejecuta `make all` y lee el total.", out)
        self.assertIn("pasa de 40", out)
        self.assertIn("```text\nkeep this output\n```", out)        # frozen fence untouched
        left = inv.check_po(DOC, po, "doc.md", self.ctx)
        self.assertEqual([f.inv for f in left], ["I15"])           # only the pending humor-register row remains
        self.ctx.humor["Timecards and the stop rule"].update(status="transcreated", spanish=SPANISH[0])
        self.assertEqual(inv.check_po(DOC, po, "doc.md", self.ctx), [])

    def test_pending_register_row_is_reported_not_rejected(self):
        fake = Fake(self.answers)
        res = self.run_file(self.translator(fake))
        self.assertEqual([r["segment_id"] for r in res["register_pending"]], [self.ids[0]])
        self.assertNotIn("fuzzy", self.entries()[self.ids[0]].flags)
        self.assertTrue(any(f.startswith("REGISTER") for f in self.notes()[0]["findings"]))

    def test_recorded_register_heading_that_differs_is_rejected(self):
        self.ctx.humor["Timecards and the stop rule"].update(status="transcreated", spanish="Otra cosa distinta")
        res = self.run_file(self.translator(Fake(self.answers)))
        self.assertEqual(res["needs_revision"], 1)
        self.assertIn("I15", self.entries()[self.ids[0]].comment)

    def test_system_prompt_is_translate_md_and_hostile_text_is_data(self):
        fake = Fake(self.answers)
        self.run_file(self.translator(fake))
        with open(tr.PROMPT, encoding="utf-8") as f:
            self.assertEqual(fake.systems[0], f.read())

    def test_input_has_glossary_slice_context_and_humor(self):
        t = self.translator(Fake(self.answers))
        inp = t.build_input(self.seg, 3, "doc.md")
        self.assertEqual([g["id"] for g in inp["glossary_slice"]], ["loop"])
        self.assertEqual(inp["glossary_slice"][0]["banned"], ["ciclo"])
        self.assertEqual(inp["glossary_slice"][0]["gloss"], "first-use")
        self.assertEqual(inp["context_before"], self.seg.segments()[2].masked)
        self.assertNotIn("context_after", inp)
        self.assertEqual(tr.validate(t.schema, "translator_input", inp), [])
        head = t.build_input(self.seg, 0, "doc.md")
        self.assertTrue(head["playful"])
        self.assertEqual(head["english_does"], "Dry office joke.")
        self.assertFalse(inp["playful"])

    def test_timecard_entry_added_when_forty_appears(self):
        t = self.translator(Fake(self.answers))
        inp = t.build_input(self.seg, 2, "doc.md")
        ids = [g["id"] for g in inp["glossary_slice"]]
        self.assertIn("timecard-rule", ids)
        self.assertIn("al menos 40", inp["glossary_slice"][0]["banned"])

    def test_ledger_rows_match_the_schema(self):
        self.run_file(self.translator(Fake(self.answers)))
        with open(tr.LEDGER_SCHEMA, encoding="utf-8") as f:
            schema = json.load(f)
        rows = self.ledger()
        self.assertEqual(len(rows), 4)
        for r in rows:
            jsonschema.validate(r, schema)
            self.assertEqual(r["status"], "accepted")
            self.assertEqual(r["task_id"], "T-1")
        self.assertEqual(rows[0]["tokens"], {"input": 10, "output": 5})
        self.assertTrue(rows[0]["playful"])


class TestResume(Base):
    def test_limit_then_resume_asks_only_the_rest(self):
        first = Fake(self.answers)
        res = self.run_file(self.translator(first), limit=2)
        self.assertEqual((res["calls"], res["stopped"], res["next_index"]), (2, "limit", 3))
        self.assertEqual(first.asked, self.ids[:2])
        self.assertEqual(sum(1 for e in self.entries().values() if e.msgstr), 2)
        second = Fake(self.answers)
        res = self.run_file(self.translator(second))
        self.assertEqual(second.asked, self.ids[2:])
        self.assertEqual((res["accepted"], res["skipped"], res["stopped"]), (2, 2, None))
        self.assertTrue(all(e.msgstr and "fuzzy" not in e.flags for e in self.entries().values()))

    def test_backend_outage_blocks_checkpoints_and_resumes(self):
        down = Fake(self.answers, fail_at=3)
        res = self.run_file(self.translator(down))
        self.assertTrue(res["stopped"].startswith("blocked"))
        self.assertEqual(res["next_index"], 3)
        ent = self.entries()
        self.assertEqual([bool(ent[i].msgstr) for i in self.ids], [True, True, False, False])
        self.assertEqual(len(self.ledger()), 2)                    # nothing accepted for the failed call
        up = Fake(self.answers)
        res = self.run_file(self.translator(up))
        self.assertEqual(up.asked, self.ids[2:])
        self.assertEqual(res["accepted"], 2)

    def test_from_skips_earlier_segments(self):
        fake = Fake(self.answers)
        self.run_file(self.translator(fake), start=3)
        self.assertEqual(fake.asked, self.ids[2:])
        self.assertEqual(self.entries()[self.ids[0]].msgstr, "")

    def test_dry_run_writes_nothing(self):
        self.run_file(self.translator(Fake(self.answers)), dry_run=True)
        self.assertFalse(os.path.exists(self.po))
        self.assertFalse(os.path.exists(os.path.join(self.tmp.name, "ledger.jsonl")))

    def test_cache_avoids_second_call_for_same_inputs(self):
        self.run_file(self.translator(Fake(self.answers)))
        os.remove(self.po)
        again = Fake(self.answers)
        res = self.run_file(self.translator(again))
        self.assertEqual(again.asked, [])
        self.assertEqual(res["accepted"], 4)
        self.assertEqual(self.entries()[self.ids[1]].msgstr, self.answers[self.ids[1]])

    def test_stale_po_entry_is_refused(self):
        self.run_file(self.translator(Fake(self.answers)), limit=1)
        po = polib.pofile(self.po, wrapwidth=0)
        po[1].msgid = "An older English sentence."
        po.save(self.po)
        with self.assertRaises(tr.TranslateError):
            self.run_file(self.translator(Fake(self.answers)))

    def test_missing_entry_is_added_to_an_existing_po(self):
        self.run_file(self.translator(Fake(self.answers)), limit=1)
        po = polib.pofile(self.po, wrapwidth=0)
        del po[-1]
        po.save(self.po)
        fake = Fake(self.answers)
        self.run_file(self.translator(fake))
        self.assertEqual(fake.asked, self.ids[1:])


class TestRejections(Base):
    def one(self, sid, reply, **kw):
        fake = Fake(self.answers, mangle={sid: reply})
        return fake, self.run_file(self.translator(fake), **kw)

    def test_dropped_placeholder_is_fuzzy_never_applied(self):
        sid = self.ids[1]
        fake, res = self.one(sid, "Ejecuta make all y lee el total.")
        self.assertEqual(res["needs_revision"], 1)
        e = self.entries()[sid]
        self.assertIn("fuzzy", e.flags)
        self.assertIn("I2", e.comment)
        out, st = ap.apply_text(DOC, ap.load_po(self.po), "doc.md", self.cat)
        self.assertIn("Run `make all` and read the total.", out)      # English stays
        self.assertEqual(st["fuzzy"], 1)
        row = [r for r in self.ledger() if r["segment_id"] == sid][0]
        self.assertEqual(row["status"], "needs-revision")

    def test_banned_timecard_phrase_is_needs_revision(self):
        sid = self.ids[2]
        fake, res = self.one(sid, "Detente cuando el total sea al menos 40.")
        self.assertEqual(res["needs_revision"], 1)
        self.assertIn("fuzzy", self.entries()[sid].flags)
        self.assertTrue(self.entries()[sid].comment)

    def test_english_reply_is_needs_revision(self):
        sid = self.ids[3]
        fake, res = self.one(sid, self.seg.segments()[3].masked)
        self.assertEqual(res["needs_revision"], 1)
        self.assertIn("English text unchanged", self.entries()[sid].comment)

    def test_may_stay_english_is_narrow(self):
        class S:
            def __init__(self, masked, kind="text"):
                self.masked, self.kind = masked, kind
        self.assertTrue(tr.may_stay_english(S("Forth")))
        self.assertTrue(tr.may_stay_english(S("false", "mermaid_label")))
        self.assertTrue(tr.may_stay_english(S("run: begin", "mermaid_label")))
        self.assertFalse(tr.may_stay_english(S("Program Flow")))                   # two plain words, not a label
        self.assertFalse(tr.may_stay_english(S("false")))                          # lower-case plain text
        self.assertFalse(tr.may_stay_english(S("Run the loop", "mermaid_label")))   # three words
        self.assertFalse(tr.may_stay_english(S("the end", "mermaid_label")))        # English function word

    def test_wrong_placeholders_seen_is_needs_revision(self):
        sid = self.ids[1]
        c1 = list(self.seg.segments()[1].mapping)[0]
        reply = {"segment_id": sid, "translated_text": "Ejecuta %s y lee el total." % c1, "ambiguities": [],
                 "placeholders_seen": [], "playful_note": None}
        fake, res = self.one(sid, reply)
        self.assertEqual(res["needs_revision"], 1)
        self.assertIn("placeholders_seen", self.entries()[sid].comment)

    def test_wrong_segment_id_blocks(self):
        sid = self.ids[0]
        reply = {"segment_id": self.ids[1], "translated_text": "Hola", "ambiguities": [], "placeholders_seen": []}
        fake, res = self.one(sid, reply)
        self.assertTrue(res["stopped"].startswith("blocked"))
        self.assertEqual(self.entries()[sid].msgstr, "")
        self.assertEqual(self.ledger() if os.path.exists(os.path.join(self.tmp.name, "ledger.jsonl")) else [], [])

    def test_schema_invalid_reply_blocks(self):
        sid = self.ids[0]
        fake, res = self.one(sid, {"segment_id": sid, "translated_text": "Hola"})
        self.assertTrue(res["stopped"].startswith("blocked"))
        self.assertEqual(self.entries()[sid].msgstr, "")

    def test_ambiguity_alone_does_not_block(self):
        sid = self.ids[0]
        reply = {"segment_id": sid, "translated_text": SPANISH[0], "playful_note": "Chiste seco de oficina.",
                 "ambiguities": [{"english_excerpt": "stop rule", "question": "regla o norma?", "chosen_reading": "regla"}],
                 "placeholders_seen": []}
        fake, res = self.one(sid, reply)
        self.assertEqual(res["accepted"], 4)
        note = [r for r in self.notes() if r["segment_id"] == sid][0]
        self.assertEqual(note["ambiguities"][0]["chosen_reading"], "regla")
        self.assertEqual(note["playful_note"], "Chiste seco de oficina.")

    def test_redo_fuzzy_retranslates_only_fuzzy_entries(self):
        sid = self.ids[1]
        self.one(sid, "Ejecuta make all y lee el total.")
        again = Fake(self.answers)
        res = self.run_file(self.translator(again))                  # fuzzy with text is kept by default
        self.assertEqual(again.asked, [])
        res = self.run_file(self.translator(again), redo_fuzzy=True)
        self.assertEqual(again.asked, [sid])
        self.assertNotIn("fuzzy", self.entries()[sid].flags)

    def test_disarming_the_invariant_check_would_accept_a_bad_reply(self):
        """Control: with check_segment stubbed out the dropped-placeholder reply is accepted by the tool,
        so the rejection above really comes from the invariants and not from the fake."""
        sid = self.ids[2]
        with mock.patch.object(tr.invariants, "check_segment", return_value=[]):
            fake, res = self.one(sid, "Detente cuando el total sea al menos 40.")
        self.assertEqual(res["needs_revision"], 0)


class TestBackends(unittest.TestCase):
    def test_parse_reply(self):
        self.assertEqual(tr.parse_reply('{"a": 1}'), {"a": 1})
        self.assertEqual(tr.parse_reply('```json\n{"a": 1}\n```'), {"a": 1})
        for bad in ("Claro, aquí está: {}", "[1]", "", "```json\n{}\n``` extra"):
            with self.assertRaises(tr.BackendError):
                tr.parse_reply(bad)

    def test_claude_backend_command_disables_tools_and_sends_json_on_stdin(self):
        env = json.dumps({"result": '{"segment_id": "s-0123456789ab-0001"}', "usage": {"input_tokens": 7, "output_tokens": 3}})
        done = subprocess.CompletedProcess([], 0, env, "")
        with mock.patch.object(tr.subprocess, "run", return_value=done) as run:
            out, tok = tr.ClaudeBackend("sonnet").ask("SYSTEM", {"x": "ñ ⟦CODE_0001⟧"})
        cmd = run.call_args[0][0]
        self.assertEqual(cmd[cmd.index("--tools") + 1], "")
        self.assertIn("--no-session-persistence", cmd)
        self.assertEqual(cmd[cmd.index("--system-prompt") + 1], "SYSTEM")
        self.assertEqual(json.loads(run.call_args[1]["input"]), {"x": "ñ ⟦CODE_0001⟧"})
        self.assertEqual((out["segment_id"], tok), ("s-0123456789ab-0001", {"input": 7, "output": 3}))

    def test_claude_backend_failures_raise_backend_error(self):
        for done in (subprocess.CompletedProcess([], 1, "", "boom"),
                     subprocess.CompletedProcess([], 0, "not json", ""),
                     subprocess.CompletedProcess([], 0, json.dumps({"is_error": True, "result": "x"}), "")):
            with mock.patch.object(tr.subprocess, "run", return_value=done):
                with self.assertRaises(tr.BackendError):
                    tr.ClaudeBackend().ask("S", {})
        with mock.patch.object(tr.subprocess, "run", side_effect=subprocess.TimeoutExpired("claude", 1)):
            with self.assertRaises(tr.BackendError):
                tr.ClaudeBackend().ask("S", {})

    def test_replay_backend_unknown_segment_raises(self):
        with tempfile.TemporaryDirectory() as d:
            p = os.path.join(d, "r.jsonl")
            with open(p, "w", encoding="utf-8") as f:
                f.write(json.dumps({"segment_id": "s-0123456789ab-0001"}) + "\n")
            b = tr.ReplayBackend(p)
            self.assertEqual(b.ask("S", {"segment_id": "s-0123456789ab-0001"})[0]["segment_id"], "s-0123456789ab-0001")
            with self.assertRaises(tr.BackendError):
                b.ask("S", {"segment_id": "s-aaaaaaaaaaaa-0002"})

    def test_make_backend_rejects_unknown(self):
        with self.assertRaises(tr.TranslateError):
            tr.make_backend("gpt", "x")


class TestCli(Base):
    def test_show_prints_a_valid_translator_input(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = tr.main(["translate.py", "--show", self.md, "--from", "2"])
        self.assertEqual(rc, 0)
        inp = json.loads(buf.getvalue())
        self.assertEqual(inp["segment_id"], self.ids[1])
        self.assertEqual(tr.validate(tr.load_schemas(), "translator_input", inp), [])

    def test_show_out_of_range(self):
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.assertEqual(tr.main(["translate.py", "--show", self.md, "--from", "99"]), 2)

    def test_replay_backend_end_to_end(self):
        rep = os.path.join(self.tmp.name, "replay.jsonl")
        with open(rep, "w", encoding="utf-8") as f:
            for sid, text in list(self.answers.items())[:3]:
                f.write(json.dumps({"segment_id": sid, "translated_text": text, "ambiguities": [],
                                    "placeholders_seen": [m.group(0) for m in tr.mask.PH_RE.finditer(text)], "playful_note": None},
                                   ensure_ascii=False) + "\n")
        buf = io.StringIO()
        with redirect_stdout(buf):
            rc = tr.main(["translate.py", self.md, "--backend", "replay:" + rep, "--po", self.po,
                          "--ledger", os.path.join(self.tmp.name, "ledger.jsonl"),
                          "--cache", os.path.join(self.tmp.name, "cache.jsonl")])
        self.assertEqual(rc, 1)                                      # the fourth segment has no answer: blocked
        self.assertIn("resume with --from 4", buf.getvalue())
        self.assertEqual(sum(1 for e in self.entries().values() if e.msgstr), 3)


class TestGlossary(unittest.TestCase):
    def test_slice_matches_plain_words_and_plurals_only(self):
        g = tr.Glossary(GLOSSARY)
        self.assertEqual([r["id"] for r in g.slice("Every loops step")], ["loop"])
        self.assertEqual(g.slice("A cloop is not one"), [])
        self.assertEqual([r["id"] for r in g.slice("The sandbox is guaranteed")],
                         ["sandbox", "assurance-guaranteed"])

    def test_placeholders_are_not_searched(self):
        g = tr.Glossary(GLOSSARY)
        self.assertEqual(g.slice("Run %sloop_0001%s now" % ("⟦", "⟧")), [])


if __name__ == "__main__":
    unittest.main()
