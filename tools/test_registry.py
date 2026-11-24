"""Registry tests: paths that the Spanish edition owns must be classed `owned`."""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import inventory as inv  # noqa: E402

OWNED_PATHS = (
    "AGENTS.md",
    "CLAUDE.md",
    "controls.toml",
    "GUIA-DEL-REPO.md",
    ".secret-guard-allow",
    "memory/AGENTS.md",
    "plans/AGENTS.md",
    "plans/adopt-ralph/steps/t01-baseline.md",
    "scripts/check_context.py",
    "tools/batch.py",
    "translation/routing.md",
)


class RegistryTests(unittest.TestCase):
    def test_edition_paths_are_owned(self):
        for path in OWNED_PATHS:
            with self.subTest(path=path):
                self.assertEqual(inv.classify(path), ["owned"])

    def test_unregistered_markdown_is_not_owned(self):
        # Known bad: a new lesson file is authored content, not edition-owned.
        self.assertNotIn("owned", inv.classify("lessons/unregistered-new-file.md"))
        self.assertFalse(inv.is_owned("lessons/unregistered-new-file.md"))


if __name__ == "__main__":
    unittest.main()
