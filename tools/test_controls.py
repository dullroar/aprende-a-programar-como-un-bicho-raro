#!/usr/bin/env python3
"""Probe test for the pinned controls. Usage: python3 -m unittest tools/test_controls.py

It builds a scratch Git repository at run time. It runs the `repo.forbidden-artifacts`
check there. A tracked `review/canaries.key.json` must fail the check (known bad).
After the file is removed, the check must pass (known good).
"""
from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

RULE = "repo.forbidden-artifacts"
ENV = {**os.environ, "GIT_CONFIG_GLOBAL": os.devnull, "GIT_CONFIG_NOSYSTEM": "1",
       "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "test@example.invalid",
       "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "test@example.invalid"}
MANIFEST = f"""schema_version = 1
profile = "ci"
enabled = ["{RULE}"]

[parameters."{RULE}"]
extra_patterns = ["review/canaries.key.json", "review/packets/**"]
"""


def git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, env=ENV)


def run_check(root: Path) -> tuple[int, str]:
    proc = subprocess.run(
        [sys.executable, "-m", "deterministic_controls", "check", "--root", str(root),
         "--profile", "ci", "--format", "json"],
        capture_output=True, text=True, env=ENV, check=False,
    )
    return proc.returncode, proc.stdout


@unittest.skipIf(importlib.util.find_spec("deterministic_controls") is None, "library not available")
class ForbiddenArtifactsProbe(unittest.TestCase):
    def test_known_bad_then_known_good(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            git(root, "init", "-q")
            (root / "controls.toml").write_text(MANIFEST, encoding="utf-8")
            (root / "review").mkdir()
            (root / "review" / "canaries.key.json").write_text("{}\n", encoding="utf-8")
            git(root, "add", "-A")
            git(root, "commit", "-q", "-m", "bad copy")

            code, out = run_check(root)
            self.assertEqual(code, 1, out)
            self.assertIn(RULE, out)
            self.assertIn("review/canaries.key.json", out)

            git(root, "rm", "-q", "review/canaries.key.json")
            git(root, "commit", "-q", "-m", "good copy")

            code, out = run_check(root)
            self.assertEqual(code, 0, out)
            statuses = {c["check_id"]: c["status"] for c in json.loads(out)["checks"]}
            self.assertEqual(statuses.get(RULE), "passed")


if __name__ == "__main__":
    unittest.main()
