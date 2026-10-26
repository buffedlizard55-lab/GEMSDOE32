"""Regression coverage for the current-decision banner on published pages."""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CurrentReleaseBannerTests(unittest.TestCase):
    def test_archived_h47_candidate_is_not_rendered_as_current(self):
        # H47 is retained as evidence, but registry/current_status.json now declares H50
        # newest. A superseded download must not be reintroduced ahead of that decision.
        for relative in ("index.html", "docs/index.html", "docs/executive-summary.html"):
            with self.subTest(page=relative):
                page = (ROOT / relative).read_text(encoding="utf-8")
                self.assertNotIn('id="h47"', page)
                self.assertNotIn("GEMSDOE32-H47-LLI-UNIQUE-D8DA7E94", page)
                self.assertIn("DO NOT SUBMIT", page)
                self.assertIn("H50", page)

    def test_site_builder_does_not_include_archived_banner(self):
        source = (ROOT / "scripts/build_site.py").read_text(encoding="utf-8")
        self.assertNotIn("def h47_banner(", source)
        self.assertNotIn("h47_banner(", source)


if __name__ == "__main__":
    unittest.main()
