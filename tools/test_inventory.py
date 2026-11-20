#!/usr/bin/env python3
"""Tests for tools/inventory.py. Run: python3 -m unittest tools/test_inventory.py -v
(or python3 tools/test_inventory.py). Includes negative cases that must fail."""
import contextlib
import io
import json
import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import inventory as inv  # noqa: E402

SAMPLE = """---
name: "AWK"
teaches: "that fields make records."
kind: idiomatic
---

# Title here

Some prose with `code` and a [link text](other.md#some-anchor) and https://example.com/x.

```mermaid
flowchart TD
    A --> B
```

````markdown
```mermaid
graph TD
    X --> Y
```
````

<!-- BEGIN GENERATED t:1 -->
## Generated heading
Generated words that should not be counted as prose.
<!-- END GENERATED t:1 -->

| a | b |
| --- | --- |
| one two | three |
"""


def write(root, rel, text="x"):
    p = os.path.join(root, rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    mode = "wb" if isinstance(text, bytes) else "w"
    with open(p, mode) as fh:
        fh.write(text)


class ClassifyTests(unittest.TestCase):
    def test_each_class(self):
        cases = {
            "src/awk/README.md": "authored",
            "lessons/cs/01-x.md": "generated",
            "src/awk/run.awk": "frozen",
            "src/cobol/.gitignore": "frozen",
            "LICENSE": "frozen",
            "lessons/solutions/a/check.sh": "frozen",
            "lessons/book/build.py": "tooling",
            "lessons/book/diagrams/package.json": "frozen",
            ".github/workflows/sandbox-gate.yml": "tooling",
            "learn-programming-the-weird-way.pdf": "archival",
            "docs/images/x.png": "archival",
            "loop/STATE.md": "owned",
            "translation/glossary.es.yaml": "owned",
            ".gitignore": "owned",
            "SYNTHESIZED-TRANSLATION-PLAN-es-bicho-raro.md": "owned",
        }
        for path, want in cases.items():
            with self.subTest(path=path):
                self.assertEqual(inv.classify(path), [want])

    def test_every_path_gets_exactly_one_class(self):
        for p in ["a.md", "b/c.py", "lessons/book/x.py", "lessons/cs/z.md", "x.pdf",
                  "loop/a.md", "translation/b.py", "src/x/y.sh", "LICENSE"]:
            self.assertEqual(len(inv.classify(p)), 1, p)

    def test_negative_wrong_class_is_detected(self):
        # A generated file must not be reported as authored (this must fail if rules rot).
        self.assertNotEqual(inv.classify("lessons/cs/01-x.md"), ["authored"])
        self.assertNotEqual(inv.classify("src/awk/run.awk"), ["authored"])


class MeasureTests(unittest.TestCase):
    def setUp(self):
        self.m = inv.measure_markdown("lessons/x.md", SAMPLE)

    def test_headings_skip_fences(self):
        # "# Title here" plus the generated-block heading; fenced text is not a heading
        self.assertEqual(self.m["headings"], 2)

    def test_mermaid_only_real_diagram_counted(self):
        # the nested example inside the 4-backtick fence is not a diagram
        self.assertEqual(len(self.m["mermaid_blocks"]), 1)

    def test_anchor_link_resolved(self):
        self.assertEqual(self.m["md_anchor_links"], ["lessons/other.md#some-anchor"])

    def test_code_spans(self):
        self.assertEqual(self.m["inline_code_spans"], 1)

    def test_generated_block_excluded_from_words(self):
        self.assertNotIn("Generated words", SAMPLE.split("<!-- END")[0].split("Title")[0])
        words = self.m["words"]
        without = SAMPLE.replace("Generated words that should not be counted as prose.", "")
        self.assertEqual(words, inv.measure_markdown("lessons/x.md", without)["words"])

    def test_front_matter_prose_counted_enum_not(self):
        fm_only = "---\nname: \"AWK\"\nteaches: \"that fields make records.\"\nkind: idiomatic\n---\n"
        mm = inv.measure_markdown("src/a/README.md", fm_only)
        self.assertEqual(mm["segments"], 2)            # name and teaches, not kind
        self.assertEqual(mm["words"], 1 + 4)
        self.assertTrue(mm["front_matter"])

    def test_negative_url_and_link_target_not_words(self):
        mm = inv.measure_markdown("a.md", "[hi](https://example.com/long/path.md#frag)\n")
        self.assertEqual(mm["words"], 1)

    def test_mermaid_unique_normalizes_whitespace(self):
        a = "```mermaid\nA --> B\n```\n"
        b = "```mermaid\n  A   --> B\n```\n"
        self.assertEqual(inv.measure_markdown("a.md", a)["mermaid_blocks"],
                         inv.measure_markdown("b.md", b)["mermaid_blocks"])


class BuildTests(unittest.TestCase):
    def make_repo(self, root):
        write(root, "README.md", "# Hi\n\nOne two three.\n")
        write(root, "src/a/README.md", SAMPLE)
        write(root, "src/a/run.sh", "echo hi\n")
        write(root, "lessons/cs/01-x.md", "# Gen\n\nWords here.\n")
        write(root, "lessons/book/build.py", "print(1)\n")
        write(root, "book.pdf", b"%PDF")
        write(root, "loop/STATE.md", "# state\n")

    def test_totals_and_owned_skipped(self):
        with tempfile.TemporaryDirectory() as root:
            self.make_repo(root)
            t = inv.build_inventory(root)
            self.assertEqual(t["totals"]["by_class"],
                             {"frozen": 1, "authored": 2, "generated": 1, "tooling": 1, "archival": 1})
            self.assertEqual(t["owned_skipped"], ["loop/STATE.md"])
            self.assertEqual(t["totals"]["entry_readmes"], 1)
            self.assertEqual(t["totals"]["publications"], 1)
            self.assertEqual(t["problems"], [])

    def run_main(self, *args):
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc = inv.main(list(args))
        return rc, buf.getvalue()

    def test_write_then_check_passes(self):
        with tempfile.TemporaryDirectory() as root:
            self.make_repo(root)
            self.assertEqual(self.run_main("--root", root, "--no-english")[0], 0)
            rc, out = self.run_main("--root", root, "--check", "--no-english")
            self.assertEqual(rc, 0, out)

    def test_negative_check_fails_when_inventory_missing(self):
        with tempfile.TemporaryDirectory() as root:
            self.make_repo(root)
            rc, out = self.run_main("--root", root, "--check", "--no-english")
            self.assertEqual(rc, 1)
            self.assertIn("does not exist", out)

    def test_negative_check_fails_when_inventory_stale(self):
        with tempfile.TemporaryDirectory() as root:
            self.make_repo(root)
            self.run_main("--root", root, "--no-english")
            write(root, "README.md", "# Hi\n\nOne two three four five.\n")   # content changed
            rc, out = self.run_main("--root", root, "--check", "--no-english")
            self.assertEqual(rc, 1)
            self.assertIn("stale", out)

    def test_negative_check_fails_when_file_set_differs_from_english(self):
        # Fake English clone: a git repo with one extra frozen file the Spanish tree lacks.
        import subprocess
        with tempfile.TemporaryDirectory() as root, tempfile.TemporaryDirectory() as eng:
            self.make_repo(root)
            write(eng, "README.md", "x")
            write(eng, "src/a/.gitignore", "bin/\n")       # missing in `root`
            env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
                       GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")
            for cmd in (["init", "-q"], ["add", "-A"], ["commit", "-q", "-m", "x"]):
                subprocess.run(["git", "-C", eng] + cmd, check=True, env=env,
                               capture_output=True)
            sha = subprocess.run(["git", "-C", eng, "rev-parse", "HEAD"], check=True,
                                 capture_output=True, text=True).stdout.strip()
            write(root, "loop/CONFIG.yaml",
                  f"english_commit: {sha}\nenglish_clone_path: {eng}\n")
            self.run_main("--root", root)
            rc, out = self.run_main("--root", root, "--check")
            self.assertEqual(rc, 1)
            self.assertIn("src/a/.gitignore", out)

    def test_inventory_json_is_deterministic(self):
        with tempfile.TemporaryDirectory() as root:
            self.make_repo(root)
            a = inv.dumps(inv.build_inventory(root))
            b = inv.dumps(inv.build_inventory(root))
            self.assertEqual(a, b)
            json.loads(a)


class ReadConfigTests(unittest.TestCase):
    def test_keys_with_capital_letters_are_read(self):
        """sentence_word_limit_N was silently ignored (the key has a capital N), so the 28 default always applied."""
        with tempfile.TemporaryDirectory() as root:
            os.makedirs(os.path.join(root, "loop"))
            with open(os.path.join(root, "loop", "CONFIG.yaml"), "w", encoding="utf-8") as f:
                f.write("sentence_word_limit_N: 29   # calibrated\nedition_label: rc1\n")
            cfg = inv.read_config(root)
        self.assertEqual("29", cfg["sentence_word_limit_N"])
        self.assertEqual("rc1", cfg["edition_label"])

    def test_the_real_config_has_the_calibrated_limit(self):
        self.assertEqual("29", inv.read_config(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))["sentence_word_limit_N"])


if __name__ == "__main__":
    unittest.main()
