"""The privacy and support pages must carry the original text over word for word."""
import re
import unittest

from tests.sitelib import ROOT, SITE, load_page, visible_text

FIXTURES = ROOT / "tests" / "fixtures" / "legal"

TITLES = {
    ("chronolyze", "privacy"): "Privacy Policy — Chronolyze",
    ("chronolyze", "support"): "Support — Chronolyze",
    ("reelo", "privacy"): "Privacy Policy — Reelo",
    ("reelo", "support"): "Support — Reelo",
}

# Chrome from the old pages that the new layout replaces: footers, the app badge, the wordmark.
OLD_CHROME = [
    r"(?s)<footer>.*?</footer>",
    r'(?s)<span class="badge">.*?</span>',
    r'(?s)<a class="wordmark"[^>]*>.*?</a>',
]


def original_text(app: str, kind: str) -> str:
    html = (FIXTURES / f"{app}-{kind}.html").read_text(encoding="utf-8")
    for pattern in OLD_CHROME:
        html = re.sub(pattern, "", html)
    return visible_text(html)


class LegalPagesTest(unittest.TestCase):
    def test_text_is_carried_over_verbatim(self):
        for app, kind in TITLES:
            with self.subTest(page=f"{app}/{kind}"):
                page = load_page(SITE / app / kind / "index.html")
                self.assertEqual(page.main_text, original_text(app, kind))

    def test_titles(self):
        for (app, kind), title in TITLES.items():
            with self.subTest(page=f"{app}/{kind}"):
                self.assertEqual(load_page(SITE / app / kind / "index.html").title, title)

    def test_old_relative_links_are_rewritten(self):
        for app, kind in TITLES:
            hrefs = load_page(SITE / app / kind / "index.html").hrefs()
            with self.subTest(page=f"{app}/{kind}"):
                self.assertNotIn("privacy.html", hrefs)
                self.assertNotIn("support.html", hrefs)
                self.assertIn(f"/{app}/privacy/", hrefs)
                self.assertIn(f"/{app}/support/", hrefs)


if __name__ == "__main__":
    unittest.main()
