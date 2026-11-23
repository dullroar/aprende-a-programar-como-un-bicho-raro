#!/usr/bin/env python3
"""Tests for tools/jury_packet.py (task P2-017). Run: python3 -I tools/test_jury_packet.py

Covers: units from English plus a PO file, risk tiers, every canary mutator (each with a case where it must
decline), canary injection (deterministic, 5 to 8 percent, never touches the input), packet chunking, the
EDITION-FACTS generator following the catalog, the written artifacts, and the leak check.
"""
import json
import os
import sys
import tempfile
import unittest
import zipfile

import polib

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "lessons", "book", "locale"))
import apply as ap  # noqa: E402
import catalog  # noqa: E402
import jury_packet as jp  # noqa: E402
import segment  # noqa: E402

CAT = catalog.load("es")
GL = jp.load_glossary()
CTX = jp.canary_context(CAT)

ENGLISH = """# Timecards

Add cards until the total is strictly greater than 40. A total of exactly 40 continues.

Run `Meetings` first, then `Coding`. Never run this outside a sandbox.

Phase 1 asks a question.
"""

SPANISH = {
    "Timecards": "Tarjetas de horas",
    "Add cards until the total is strictly greater than 40. A total of exactly 40 continues.":
        "Agrega tarjetas hasta que el total sea estrictamente mayor que 40. Un total de exactamente 40 continúa.",
    "Never run this outside a sandbox.": None,
}


def u(n, en, es, kind="paragraph", file="README.md"):
    return {"file": file, "id": "s-%012x-%04d" % (n * 7919, n), "line": n + 1, "kind": kind,
            "english": en, "spanish": es}


def make_units(count=60):
    """Synthetic units with something for every mutator, plus plain filler."""
    base = [
        ("Add cards until the total is strictly greater than 40. A total of exactly 40 continues.",
         "Agrega tarjetas y detente cuando el total pasa de 40. Un total de exactamente 40 continúa."),
        ("This entry is guaranteed to stop.", "Esta entrada es garantizado que se detiene."),
        ("Phase 2 does not run the code.", "La fase I no ejecuta el código."),
        ("Run `Meetings` first. It prints 3 cards.", "Ejecuta `Meetings` primero. Imprime 3 tarjetas."),
        ("Open the file. Read the first line. Write the answer.",
         "Abre el archivo. Lee la primera línea. Escribe la respuesta."),
        ("Nothing special here.", "Aquí no hay nada especial."),
    ]
    out = []
    for i in range(count):
        en, es = base[i % len(base)]
        out.append(u(i, en + " (%d)" % i if i >= len(base) else en, es + (" (%d)" % i if i >= len(base) else "")))
    return out


def po_for(english, rel="README.md", fill=None):
    seg = segment.Segmentation(english, rel)
    po = ap.new_po(seg, rel)
    for e in po:
        text = fill(e.msgid) if fill else None
        if text is not None:
            e.msgstr = text
    return po


class UnitsTests(unittest.TestCase):
    def test_units_hold_english_and_restored_spanish(self):
        def fill(msgid):
            if msgid.startswith("Run "):
                return "Ejecuta " + msgid[len("Run "):].replace("first, then", "primero, luego").replace(
                    "Never run this outside a sandbox.", "Nunca lo ejecutes fuera de un entorno aislado.")
            if msgid.startswith("Phase 1"):
                return "La fase {{phase.1.letter}} hace una pregunta."
            if msgid == "Timecards":
                return "Tarjetas de horas"
            return None
        po = po_for(ENGLISH, fill=fill)
        units, skipped = jp.units_for_file("README.md", ENGLISH, po, CAT)
        self.assertEqual(skipped, 1)                       # the timecard paragraph has no msgstr
        by_en = {x["english"]: x for x in units}
        run = next(x for x in units if x["english"].startswith("Run `Meetings`"))
        self.assertIn("`Meetings`", run["spanish"])          # placeholders restored from the English mask
        self.assertNotIn("\x00", run["spanish"])
        phase = by_en["Phase 1 asks a question."]
        self.assertEqual(phase["spanish"], "La fase B hace una pregunta.")   # macro expanded
        self.assertTrue(all(x["file"] == "README.md" and x["line"] >= 1 for x in units))

    def test_stale_po_fails_closed(self):
        po = po_for(ENGLISH, fill=lambda m: "x")
        po[0].msgid = "Something else entirely"
        with self.assertRaises(ap.ApplyError):
            jp.units_for_file("README.md", ENGLISH, po, CAT)


class TierTests(unittest.TestCase):
    def test_tiers(self):
        self.assertEqual(jp.tier_of(u(1, "The total is strictly greater than 40.", "x")), "critical")
        self.assertEqual(jp.tier_of(u(1, "It is guaranteed.", "x")), "critical")
        self.assertEqual(jp.tier_of(u(1, "Use a sandbox.", "x")), "critical")
        self.assertEqual(jp.tier_of(u(1, "Alive", "x", kind="mermaid_label")), "high")
        self.assertEqual(jp.tier_of(u(1, "You must read it.", "x")), "high")
        self.assertEqual(jp.tier_of(u(1, "A tidy sentence.", "x", file="lessons/study-guides/a.md")), "high")
        self.assertEqual(jp.tier_of(u(1, "A tidy sentence.", "x")), "normal")


class MutatorTests(unittest.TestCase):
    def apply(self, fn, es, en="x", kind="paragraph"):
        return fn(u(1, en, es, kind), CTX)

    def test_flip_forty(self):
        out = self.apply(jp.m_flip_forty, "Detente cuando el total pasa de 40.")
        self.assertEqual(out[0], "Detente cuando el total llega a 40.")
        self.assertEqual((out[2], out[3]), ("number-operator", "critical"))
        out = self.apply(jp.m_flip_forty, "Un total de exactamente 40 continúa.")
        self.assertIn("se detiene", out[0])
        self.assertIsNone(self.apply(jp.m_flip_forty, "Un texto sin la regla."))

    def test_swap_number_skips_code_and_unshared_numbers(self):
        out = self.apply(jp.m_swap_number, "Imprime 3 tarjetas.", "Prints 3 cards.")
        self.assertEqual(out[0], "Imprime 4 tarjetas.")
        self.assertIsNone(self.apply(jp.m_swap_number, "Imprime `3` tarjetas.", "Prints 3 cards."))      # inside code
        self.assertIsNone(self.apply(jp.m_swap_number, "Imprime 7 tarjetas.", "Prints some cards."))     # not in English
        self.assertIsNone(self.apply(jp.m_swap_number, "Total 40.", "Total 40."))                        # the 40 rule has its own mutator

    def test_negation(self):
        out = self.apply(jp.m_negation, "La fase no ejecuta el código.")
        self.assertEqual(out[0], "La fase ejecuta el código.")
        self.assertIn(out[1], out[0])
        self.assertIsNone(self.apply(jp.m_negation, "La fase ejecuta el código."))
        self.assertIsNone(self.apply(jp.m_negation, "Mira `no es` código."))

    def test_drop_clause_needs_two_sentences_in_prose(self):
        out = self.apply(jp.m_drop_clause, "Primera frase. Segunda frase.")
        self.assertEqual(out[0], "Primera frase.")
        self.assertIsNone(self.apply(jp.m_drop_clause, "Una sola frase."))
        self.assertIsNone(self.apply(jp.m_drop_clause, "Primera frase. Segunda frase.", kind="heading"))

    def test_assurance_label_moves_to_the_next_label(self):
        out = self.apply(jp.m_assurance, "Es garantizado.")
        self.assertEqual(out[0], "Es permitido por la implementación.")
        self.assertEqual(out[3], "critical")
        self.assertIsNone(self.apply(jp.m_assurance, "No dice nada de eso."))

    def test_phase_letter(self):
        out = self.apply(jp.m_phase_letter, "Estás en la fase B ahora.")
        self.assertEqual(out[0], "Estás en la fase I ahora.")
        self.assertEqual(out[2], "phase-acronym")
        self.assertIsNone(self.apply(jp.m_phase_letter, "Estás en la fase Z ahora."))
        self.assertIsNone(self.apply(jp.m_phase_letter, "Estás en la `fase B` ahora."))

    def test_identifier_and_register(self):
        out = self.apply(jp.m_identifier, "Usa `Meetings` aquí.")
        self.assertIn("`Reunión`", out[0])                                        # decision 11: an unapproved spelling is the fault
        self.assertNotIn("`Reuniones`", out[0])
        self.assertIsNone(self.apply(jp.m_identifier, "Usa Meetings aquí."))        # not code: nothing to break
        out = self.apply(jp.m_register, "Ejecuta el programa.")
        self.assertEqual(out[0], "Ejecute el programa.")
        self.assertIsNone(self.apply(jp.m_register, "El programa corre."))


class CanaryTests(unittest.TestCase):
    def test_rate_must_stay_between_five_and_eight_percent(self):
        for bad in (0.0, 0.04, 0.09, 0.5):
            with self.assertRaises(ValueError):
                jp.canary_count(100, bad)
        self.assertEqual(jp.canary_count(100, 0.05), 5)
        self.assertEqual(jp.canary_count(100, 0.08), 8)
        self.assertEqual(jp.canary_count(0, 0.06), 0)

    def test_injection_is_deterministic_and_counted(self):
        units = make_units(60)
        a, ka = jp.inject_canaries(units, CTX, 0.06, seed=3)
        b, kb = jp.inject_canaries(units, CTX, 0.06, seed=3)
        self.assertEqual(ka, kb)
        self.assertEqual(a, b)
        self.assertEqual(len(ka), 4)                                    # round(60 * 0.06) = 4
        c, kc = jp.inject_canaries(units, CTX, 0.06, seed=4)
        self.assertNotEqual([k["segment"] for k in ka], [k["segment"] for k in kc])

    def test_input_is_never_changed_and_key_matches_the_copy(self):
        units = make_units(60)
        before = json.dumps(units, sort_keys=True)
        shown, key = jp.inject_canaries(units, CTX, 0.08, seed=1)
        self.assertEqual(json.dumps(units, sort_keys=True), before)
        by_unit = {jp.unit_key(s): s for s in shown}
        for k in key:
            s = by_unit[k["unit"]]
            self.assertEqual(s["spanish"], k["mutated_spanish"])
            self.assertNotEqual(k["original_spanish"], k["mutated_spanish"])
            self.assertIn(k["fragment"], k["mutated_spanish"])
            self.assertEqual(s["canary"], k["canary_id"])
        self.assertEqual(sum(1 for s in shown if s["canary"]), len(key))

    def test_the_forty_flip_is_always_included_when_a_unit_allows_it(self):
        units = make_units(60)
        for seed in range(1, 8):
            _, key = jp.inject_canaries(units, CTX, 0.05, seed=seed)
            self.assertIn("flip_forty", [k["mutator"] for k in key])
            self.assertTrue(any(k["severity"] == "critical" for k in key))

    def test_units_nothing_can_break_get_no_canary(self):
        units = [u(i, "Nothing special here.", "Aquí hay algo especial.") for i in range(40)]
        shown, key = jp.inject_canaries(units, CTX, 0.06, seed=1)
        self.assertEqual(key, [])
        self.assertTrue(all(s["canary"] is None for s in shown))


class ChunkTests(unittest.TestCase):
    def test_chunks_respect_the_maximum(self):
        units = [u(i, "a" * 400, "b" * 400) for i in range(100)]            # about 240 tokens each
        chunks = jp.chunk_units(units, target=2000, minimum=1500, maximum=2500)
        self.assertGreater(len(chunks), 5)
        self.assertEqual(sum(len(c) for c, _ in chunks), 100)                 # nothing lost, nothing repeated
        for c, size in chunks:
            self.assertLessEqual(size, 2500)
        ids = [x["id"] for c, _ in chunks for x in c]
        self.assertEqual(ids, [x["id"] for x in units])                       # reading order kept

    def test_a_short_tail_joins_the_previous_chunk_when_it_fits(self):
        units = [u(i, "a" * 400, "b" * 400) for i in range(9)]
        chunks = jp.chunk_units(units, target=2000, minimum=1500, maximum=3000)
        self.assertTrue(all(size >= 1500 for _, size in chunks))

    def test_an_oversize_unit_gets_its_own_chunk_and_empty_input_gives_none(self):
        units = [u(1, "a" * 100, "b" * 100), u(2, "a" * 40000, "b" * 40000), u(3, "a" * 100, "b" * 100)]
        chunks = jp.chunk_units(units, target=2000, minimum=1500, maximum=3000)
        self.assertEqual([len(c) for c, _ in chunks], [1, 1, 1])
        self.assertEqual(jp.chunk_units([]), [])

    def test_rendered_packets_respect_the_maximum_even_with_heavy_overhead(self):
        # The chunker counts unit text only; a packet also carries facts and context, so a tier must shrink.
        units = [u(i, "a" * 400, "b" * 400) for i in range(60)]              # about 240 tokens each
        heavy_facts = "x" * 8000                                              # about 2000 tokens of overhead
        chunks, texts = jp.fit_tier("critical", units, heavy_facts, GL, CAT, 2000, 1500, 2500)
        self.assertEqual(sum(len(c) for c, _ in chunks), 60)
        self.assertEqual(len(texts), len(chunks))
        for (chunk, _), text in zip(chunks, texts):
            if len(chunk) > 1:
                self.assertLessEqual(jp.estimate_tokens(text), 2500)

    def test_a_single_unit_over_the_maximum_is_kept_and_reported_not_split(self):
        units = [u(1, "a" * 40000, "b" * 40000)]
        chunks, texts = jp.fit_tier("critical", units, "", GL, CAT, 2000, 1500, 2500)
        self.assertEqual([len(c) for c, _ in chunks], [1])
        self.assertGreater(jp.estimate_tokens(texts[0]), 2500)


class FactsTests(unittest.TestCase):
    def test_facts_come_from_the_catalog_and_the_glossary(self):
        text = jp.edition_facts(CAT, GL, {"edition_label": "v4-es.0-rc1"})
        self.assertIn(CAT.get("acronym.word"), text)
        for letter, name in zip(CAT.phase_letters(), range(5)):
            self.assertIn("| %s |" % letter, text)
        self.assertIn("exactamente 40 continúa", text)
        self.assertIn("al menos 40", text)                                    # listed as banned
        for k in ("guaranteed", "implementation_permitted", "accidentally_exploited"):
            self.assertIn(CAT.get("study_guides.assurance.%s" % k), text)
        for word in ("Meetings", "Coding", "Debugging", "Learning"):
            self.assertIn("`%s`" % word, text)
        self.assertIn("v4-es.0-rc1", text)
        self.assertIn(CAT.get("curriculum.max_words"), text)
        bullets = [ln for ln in text.split("\n## ", 1)[0].split("\n") if ln.startswith("- ")]
        self.assertEqual(len(bullets), 5)                                     # edition, title, tag, acronym, limit
        self.assertNotIn("\n\n\n", text)

    def test_changing_the_acronym_changes_the_facts(self):
        flat = dict(CAT.flat)
        flat["acronym.word"] = "TORCE"
        for n, letter in enumerate("TORCE", 1):
            flat["phases.%d.letter" % n] = letter
        torce = catalog.Catalog("es", flat)
        text = jp.edition_facts(torce, GL)
        self.assertIn("TORCE", text)
        self.assertNotIn("BICHO", text.split("## The five phases")[0].split("Acronym:")[1].split("\n")[0])


class GlossaryTests(unittest.TestCase):
    def test_only_terms_present_in_the_english_are_listed(self):
        rows = jp.glossary_slice([u(1, "The idiomatic version uses a for loop.", "x")], GL, CAT)
        self.assertIn("idiomatic", [r[0] for r in rows])
        self.assertEqual(jp.glossary_slice([u(1, "Zzz qqq.", "x")], GL, CAT), [])


class BuildTests(unittest.TestCase):
    def build(self, tmp, **kw):
        units = make_units(60)
        return units, jp.build(units, CAT, GL, tmp, rate=0.06, seed=2, config={"edition_label": "v-test"},
                               target=800, minimum=500, maximum=1200, **kw)

    def test_artifacts_cover_every_unit_once_and_stay_clean(self):
        with tempfile.TemporaryDirectory() as tmp:
            units, manifest = self.build(tmp)
            for name in ("EDITION-FACTS.md", "MANIFEST.md", "canaries.key.json", "units.index.jsonl",
                         os.path.join("packets", "manifest.json")):
                self.assertTrue(os.path.isfile(os.path.join(tmp, name)), name)
            self.assertEqual(manifest["units"], 60)
            with open(os.path.join(tmp, "units.index.jsonl"), encoding="utf-8") as f:
                index = [json.loads(x) for x in f if x.strip()]
            self.assertEqual(sorted(i["segment"] + i["file"] + str(i["line"]) for i in index),
                             sorted(x["id"] + x["file"] + str(x["line"]) for x in units))
            for p in manifest["packets"]:
                path = os.path.join(tmp, "packets", p["name"] + ".md")
                self.assertTrue(os.path.isfile(path))
                with open(path, encoding="utf-8") as f:
                    text = f.read()
                self.assertIn("## Units", text)
                self.assertEqual(p["send_to_jurors"], 2 if p["tier"] == "critical" else 1)
            self.assertEqual(jp.leaks(tmp), [])
            with open(os.path.join(tmp, "packets", "manifest.json"), encoding="utf-8") as f:
                self.assertNotIn("canar", f.read().lower())
            self.assertTrue(any(p["tier"] == "critical" for p in manifest["packets"]))

    def test_packet_text_shows_the_planted_spanish_not_the_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.build(tmp)
            with open(os.path.join(tmp, "canaries.key.json"), encoding="utf-8") as f:
                key = json.load(f)["canaries"]
            self.assertTrue(key)
            packets = ""
            for n in os.listdir(os.path.join(tmp, "packets")):
                if n.endswith(".md"):
                    with open(os.path.join(tmp, "packets", n), encoding="utf-8") as f:
                        packets += f.read()
            for k in key:
                self.assertIn("ES: " + k["mutated_spanish"], packets)

    def test_rebuild_is_identical_and_removes_stale_packets(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.build(tmp)
            stale = os.path.join(tmp, "packets", "P-normal-99.md")
            with open(stale, "w", encoding="utf-8") as f:
                f.write("old")
            self.build(tmp)
            self.assertFalse(os.path.exists(stale))

    def test_bundle_never_holds_the_private_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.build(tmp)
            path = jp.make_bundle(tmp)
            with zipfile.ZipFile(path) as z:
                names = z.namelist()
            self.assertIn("EDITION-FACTS.md", names)
            self.assertTrue(any(n.startswith("packets/P-") for n in names))
            for private in jp.PRIVATE_FILES:
                self.assertNotIn(private, names)
            self.assertEqual(jp.leaks(tmp), [])

    def test_leak_check_fails_when_a_public_file_names_a_private_one(self):
        with tempfile.TemporaryDirectory() as tmp:
            _, manifest = self.build(tmp)
            first = os.path.join(tmp, "packets", manifest["packets"][0]["name"] + ".md")
            with open(first, encoding="utf-8") as f:
                text = f.read()
            with open(first, "w", encoding="utf-8") as f:
                f.write(text.replace("# Packet", "Some of these are canaries (see canaries.key.json).\n# Packet", 1))
            bad = jp.leaks(tmp)
            self.assertTrue(any("canaries" in b for b in bad), bad)
            self.assertTrue(any("canaries.key.json" in b for b in bad), bad)

    def test_leak_check_fails_when_the_bundle_holds_the_key(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.build(tmp)
            path = jp.make_bundle(tmp)
            with zipfile.ZipFile(path, "a") as z:
                z.writestr("canaries.key.json", "{}")
            self.assertTrue(any("bundle contains" in b for b in jp.leaks(tmp)))

    def test_a_code_packet_holds_both_sources_and_the_part2_slices(self):
        en = "#!/bin/bash\n# Check.\nif [ \"$t\" -gt 40 ]; then echo stop; fi\n"
        units = make_units(40) + jp.code_units_for_file("src/x/check.sh", en, en.replace("# Check.", "# Revisa."),
                                                        None, [{"path": "src/x/check.sh", "old": "t", "new": "suma",
                                                                "role": "variable", "scope": "file"}])
        with tempfile.TemporaryDirectory() as tmp:
            manifest = jp.build(units, CAT, GL, tmp, rate=0.08, seed=3, target=800, minimum=500, maximum=1200)
            code = [p for p in manifest["packets"] if p["tier"] == "code"]
            self.assertEqual(len(code), 1)
            with open(os.path.join(tmp, "packets", code[0]["name"] + ".md"), encoding="utf-8") as f:
                text = f.read()
            self.assertIn("# Check.", text)
            self.assertIn("# Revisa.", text)
            self.assertIn("Identifier map (old -> new): `t` -> `suma`", text)
            self.assertEqual(jp.leaks(tmp), [])

    def test_the_book_may_use_the_word_canary(self):
        with tempfile.TemporaryDirectory() as tmp:
            units = make_units(60)
            units[0]["english"] = "A canary in a coal mine."
            units[0]["spanish"] = "Un canario en una mina."
            jp.build(units, CAT, GL, tmp, rate=0.06, seed=2, target=800, minimum=500, maximum=1200)
            self.assertEqual(jp.leaks(tmp), [])


if __name__ == "__main__":
    unittest.main()
