#!/usr/bin/env python3
"""Tests for tools/batch.py. Offline only: the HTTP function is injected, nothing touches the network.

Run: python3 -m unittest tools/test_batch.py
"""
import json
import os
import sys
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import batch  # noqa: E402

FIX = os.path.join(HERE, "fixtures", "batch")
PENDING = os.path.join(FIX, "pending.jsonl")
CID1 = "s-111111111111-0001-7a242184323f"


def jl(path):
    with open(path, encoding="utf-8") as f:
        return [json.loads(ln) for ln in f if ln.strip()]


class Base(unittest.TestCase):
    def setUp(self):
        td = tempfile.TemporaryDirectory()
        self.addCleanup(td.cleanup)
        self.dir = td.name
        # A synthetic key, built at run time. It is never stored in the repository.
        self.key = "sk-test-" + os.urandom(12).hex()
        self.env = {batch.KEY_ENV: self.key}
        self.log = []
        self.calls = []

    def p(self, name):
        return os.path.join(self.dir, name)

    def run_cli(self, *argv, http=None, env=None):
        out = []
        code = batch.main(list(argv), http=http, env=self.env if env is None else env, out=out.append)
        return code, out

    def fake_http(self, responses):
        def http(method, url, headers, body=None):
            self.calls.append((method, url, headers, body))
            return responses.pop(0)
        return http

    def files(self):
        return sorted(os.listdir(self.dir))

    def assert_no_key_in_files(self):
        for name in self.files():
            with open(self.p(name), encoding="utf-8") as f:
                self.assertNotIn(self.key, f.read(), name)

    def build(self):
        code, _ = self.run_cli("build", "--input", PENDING, "--model", "test-model", "--out", self.p("req.jsonl"))
        self.assertEqual(code, 0)
        return jl(self.p("req.jsonl"))

    def collect(self, results, name="drafts.jsonl", cost="costs.jsonl"):
        return self.run_cli("collect", "--batch-id", "msgbatch_1", "--results", os.path.join(FIX, results),
                            "--out", self.p(name), "--cost-file", self.p(cost), "--price-in", "1.5", "--price-out", "7.5")


class BuildTests(Base):
    def test_request_shape(self):
        reqs = self.build()
        self.assertEqual(len(reqs), 4)
        r = reqs[0]
        self.assertEqual(r["custom_id"], CID1)
        params = r["params"]
        self.assertEqual(params["model"], "test-model")
        block = params["system"][0]
        self.assertEqual(block["cache_control"], {"type": "ephemeral"})
        self.assertEqual(len(params["system"]), 1)
        self.assertIn("House style", block["text"])
        self.assertIn("Glossary", block["text"])
        self.assertEqual(json.loads(params["messages"][0]["content"])["segment_id"], "s-111111111111-0001")
        self.assertEqual(len({x["custom_id"] for x in reqs}), 4)
        self.assertTrue(all(len(x["custom_id"]) <= 64 for x in reqs))

    def test_dry_run_writes_nothing(self):
        code, out = self.run_cli("build", "--input", PENDING, "--model", "m", "--out", self.p("r.jsonl"), "--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(self.files(), [])

    def test_duplicate_segment_refused(self):
        rows = jl(PENDING)
        with open(self.p("dup.jsonl"), "w", encoding="utf-8") as f:
            for r in rows + rows[:1]:
                f.write(json.dumps(r) + "\n")
        code, _ = self.run_cli("build", "--input", self.p("dup.jsonl"), "--model", "m", "--out", self.p("r.jsonl"))
        self.assertEqual(code, 1)
        self.assertNotIn("r.jsonl", self.files())

    def test_bad_row_refused(self):
        with open(self.p("bad.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"segment_id": "nope", "english_masked": "x"}) + "\n")
        code, _ = self.run_cli("build", "--input", self.p("bad.jsonl"), "--model", "m", "--out", self.p("r.jsonl"))
        self.assertEqual(code, 1)

    def test_key_not_in_build_output(self):
        self.build()
        self.assert_no_key_in_files()


class SubmitTests(Base):
    def submit(self, *extra, env=None, http=None):
        self.build()
        return self.run_cli("submit", "--requests", self.p("req.jsonl"), "--cost-file", self.p("costs.jsonl"),
                            *extra, env=env, http=http)

    def test_refuses_without_key(self):
        code, _ = self.submit("--max-usd", "5", env={}, http=self.fake_http([]))
        self.assertEqual(code, 1)
        self.assertEqual(self.calls, [])

    def test_refuses_without_max_usd(self):
        code, _ = self.submit(http=self.fake_http([]))
        self.assertEqual(code, 1)
        self.assertEqual(self.calls, [])

    def test_refuses_cost_file_inside_the_repository(self):
        self.build()
        code, _ = self.run_cli("submit", "--requests", self.p("req.jsonl"), "--max-usd", "5",
                               "--cost-file", os.path.join(batch.ROOT, "costs.jsonl"), http=self.fake_http([]))
        self.assertEqual(code, 1)

    def test_dry_run_sends_and_writes_nothing(self):
        code, out = self.submit("--max-usd", "5", "--dry-run", http=self.fake_http([]))
        self.assertEqual(code, 0)
        self.assertEqual(self.calls, [])
        self.assertEqual(self.files(), ["req.jsonl"])
        self.assert_no_key_in_files()

    def test_submit_records_cap_and_total(self):
        http = self.fake_http([(200, json.dumps({"id": "msgbatch_1"}).encode())])
        code, out = self.submit("--max-usd", "5", http=http)
        self.assertEqual(code, 0)
        self.assertIn("batch id: msgbatch_1", out)
        method, url, headers, body = self.calls[0]
        self.assertEqual((method, headers["x-api-key"]), ("POST", self.key))
        self.assertTrue(url.endswith("/v1/messages/batches"))
        self.assertEqual(len(json.loads(body)["requests"]), 4)
        rec = jl(self.p("costs.jsonl"))
        self.assertEqual(rec[0]["cap_usd"], 5.0)
        self.assertEqual((rec[0]["total_before_usd"], rec[0]["total_after_usd"]), (0.0, 5.0))
        self.assert_no_key_in_files()

    def test_program_cap_refuses(self):
        with open(self.p("costs.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps({"kind": "submit", "batch_id": "b1", "cap_usd": 60.0}) + "\n")
            f.write(json.dumps({"kind": "submit", "batch_id": "b2", "cap_usd": 30.0}) + "\n")
        code, _ = self.submit("--max-usd", "10.01", http=self.fake_http([]))
        self.assertEqual(code, 1)
        self.assertEqual(self.calls, [])
        http = self.fake_http([(200, json.dumps({"id": "b3"}).encode())])
        code, _ = self.submit("--max-usd", "10", http=http)
        self.assertEqual(code, 0)
        self.assertEqual(jl(self.p("costs.jsonl"))[-1]["total_after_usd"], 100.0)

    def test_real_cost_replaces_cap_in_total(self):
        rows = [{"kind": "submit", "batch_id": "b1", "cap_usd": 90.0}, {"kind": "collect", "batch_id": "b1", "usd": 2.0}]
        self.assertEqual(batch.running_total(rows), 2.0)

    def test_api_error_does_not_leak(self):
        http = self.fake_http([(401, json.dumps({"error": {"type": "authentication_error"}}).encode())])
        code, _ = self.submit("--max-usd", "5", http=http)
        self.assertEqual(code, 1)
        self.assertNotIn("costs.jsonl", self.files())


class StatusTests(Base):
    def test_status(self):
        body = {"id": "b", "processing_status": "ended", "request_counts": {"succeeded": 3}, "results_url": "u"}
        code, out = self.run_cli("status", "--batch-id", "b", http=self.fake_http([(200, json.dumps(body).encode())]))
        self.assertEqual(code, 0)
        self.assertIn("status: ended", out)
        self.assertEqual(self.calls[0][0:2], ("GET", batch.API + "/v1/messages/batches/b"))


class CollectTests(Base):
    def test_success(self):
        code, out = self.collect("results-success.jsonl")
        self.assertEqual(code, 0)
        drafts = jl(self.p("drafts.jsonl"))
        self.assertEqual([d["segment_id"] for d in drafts],
                         ["s-111111111111-0001", "s-222222222222-0002", "s-333333333333-0003"])
        for d in drafts:  # the closed translator_output shape that translate.py --drafts validates
            self.assertEqual(set(d), {"segment_id", "translated_text", "ambiguities", "placeholders_seen"})
        self.assertEqual(jl(self.p("drafts.jsonl.ids.jsonl"))[0]["custom_id"], CID1)
        rec = jl(self.p("costs.jsonl"))[0]
        self.assertEqual((rec["kind"], rec["batch_id"], rec["input_tokens"], rec["output_tokens"]),
                         ("collect", "msgbatch_1", 3000, 600))
        self.assertAlmostEqual(rec["usd"], 0.009, places=6)
        self.assert_no_key_in_files()

    def test_partial_errors(self):
        code, out = self.collect("results-partial.jsonl")
        self.assertEqual(code, 0)
        self.assertEqual([d["segment_id"] for d in jl(self.p("drafts.jsonl"))], ["s-111111111111-0001"])
        counts = jl(self.p("costs.jsonl"))[0]["counts"]
        self.assertEqual((counts["succeeded"], counts["errored"], counts["rejected"]), (1, 1, 2))
        text = "\n".join(out)
        self.assertIn("errored", text)
        self.assertIn("does not match the custom_id", text)
        self.assertNotIn("Overloaded", text)  # no raw error envelope in the log

    def test_expired_and_canceled(self):
        code, out = self.collect("results-expired.jsonl")
        self.assertEqual(code, 0)
        self.assertEqual(jl(self.p("drafts.jsonl")), [])
        counts = jl(self.p("costs.jsonl"))[0]["counts"]
        self.assertEqual((counts["expired"], counts["canceled"], counts["succeeded"]), (1, 1, 0))

    def test_duplicate_result_ignored(self):
        code, out = self.collect("results-duplicate.jsonl")
        self.assertEqual(code, 0)
        drafts = jl(self.p("drafts.jsonl"))
        self.assertEqual(len(drafts), 1)
        self.assertEqual(drafts[0]["translated_text"], "Hola, lector.")
        self.assertEqual(jl(self.p("costs.jsonl"))[0]["counts"]["duplicate"], 1)
        self.assertEqual(jl(self.p("costs.jsonl"))[0]["input_tokens"], 1000)

    def test_dry_run_writes_nothing(self):
        code, _ = self.run_cli("collect", "--batch-id", "b", "--results", os.path.join(FIX, "results-success.jsonl"),
                               "--out", self.p("d.jsonl"), "--cost-file", self.p("c.jsonl"),
                               "--price-in", "1", "--price-out", "1", "--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(self.files(), [])

    def test_fetch_through_injected_http(self):
        with open(os.path.join(FIX, "results-success.jsonl"), "rb") as f:
            raw = f.read()
        info = {"processing_status": "ended", "results_url": "https://example.invalid/results"}
        http = self.fake_http([(200, json.dumps(info).encode()), (200, raw)])
        code, _ = self.run_cli("collect", "--batch-id", "b", "--out", self.p("d.jsonl"), "--cost-file", self.p("c.jsonl"),
                               "--price-in", "1", "--price-out", "1", http=http)
        self.assertEqual(code, 0)
        self.assertEqual(self.calls[1][1], "https://example.invalid/results")
        self.assertEqual(len(jl(self.p("d.jsonl"))), 3)

    def test_secret_in_a_result_is_never_written(self):
        # A result that holds the key, built at run time. It is never stored.
        reply = {"segment_id": "s-111111111111-0001", "translated_text": "leak " + self.key,
                 "ambiguities": [], "placeholders_seen": []}
        line = {"custom_id": CID1, "result": {"type": "succeeded", "message": {
            "content": [{"type": "text", "text": json.dumps(reply)}], "usage": {"input_tokens": 1, "output_tokens": 1}}}}
        src = self.p("leaky.jsonl")
        with open(src, "w", encoding="utf-8") as f:
            f.write(json.dumps(line) + "\n")
        code, _ = self.run_cli("collect", "--batch-id", "b", "--results", src, "--out", self.p("d.jsonl"),
                               "--cost-file", self.p("c.jsonl"), "--price-in", "1", "--price-out", "1")
        self.assertEqual(code, 1)
        self.assertNotIn("d.jsonl", self.files())
        os.unlink(src)
        self.assert_no_key_in_files()


class ReconcileTests(Base):
    def reconcile(self, pending, applied="applied.jsonl", out="ok.jsonl", *extra):
        return self.run_cli("reconcile", "--drafts", self.p("drafts.jsonl"), "--pending", pending,
                            "--applied", self.p(applied), "--out", self.p(out), *extra)

    def test_accepts_current_results_and_never_applies_twice(self):
        self.collect("results-success.jsonl")
        code, out = self.reconcile(PENDING)
        self.assertEqual(code, 0)
        self.assertEqual(len(jl(self.p("ok.jsonl"))), 3)
        self.assertEqual(len(jl(self.p("applied.jsonl"))), 3)
        code, out = self.reconcile(PENDING, out="ok2.jsonl")
        self.assertEqual(code, 0)
        self.assertEqual(jl(self.p("ok2.jsonl")), [])
        self.assertIn("already applied", "\n".join(out))
        self.assertEqual(len(jl(self.p("applied.jsonl"))), 3)

    def test_stale_source_hash_rejected(self):
        self.collect("results-success.jsonl")
        code, out = self.reconcile(os.path.join(FIX, "pending-stale.jsonl"))
        kept = [d["segment_id"] for d in jl(self.p("ok.jsonl"))]
        self.assertEqual(kept, ["s-111111111111-0001", "s-222222222222-0002"])
        self.assertIn("source hash changed", "\n".join(out))
        applied = [r["segment_id"] for r in jl(self.p("applied.jsonl"))]
        self.assertNotIn("s-333333333333-0003", applied)

    def test_segment_not_pending_rejected(self):
        self.collect("results-partial.jsonl")
        with open(self.p("only4.jsonl"), "w", encoding="utf-8") as f:
            f.write(json.dumps(jl(PENDING)[3]) + "\n")
        code, out = self.reconcile(self.p("only4.jsonl"))
        self.assertEqual(jl(self.p("ok.jsonl")), [])
        self.assertIn("not a current pending segment", "\n".join(out))

    def test_dry_run_writes_nothing(self):
        self.collect("results-success.jsonl")
        before = self.files()
        code, out = self.reconcile(PENDING, "a.jsonl", "o.jsonl", "--dry-run")
        self.assertEqual(code, 0)
        self.assertEqual(self.files(), before)


class HelperTests(unittest.TestCase):
    def test_custom_id_round_trip(self):
        cid = batch.make_custom_id("s-111111111111-0001", "Hello, reader.")
        self.assertEqual(cid, CID1)
        self.assertEqual(batch.segment_of(cid), "s-111111111111-0001")
        self.assertIsNone(batch.segment_of("junk"))

    def test_parse_reply(self):
        self.assertEqual(batch.parse_reply('```json\n{"a": 1}\n```'), {"a": 1})
        with self.assertRaises(batch.BatchError):
            batch.parse_reply("[1]")
        with self.assertRaises(batch.BatchError):
            batch.parse_reply("text before {\"a\": 1}")


if __name__ == "__main__":
    unittest.main()
