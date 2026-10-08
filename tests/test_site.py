"""Whole-site integrity: links, sitemap, robots, old URLs, and the deploy workflow."""
import unittest
import xml.etree.ElementTree as ET

from tests.sitelib import ORIGIN, ROOT, SITE, all_pages, is_internal, load_page, resolve, url_for

SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"


class SiteIntegrityTest(unittest.TestCase):
    def test_every_internal_link_resolves(self):
        for path in all_pages():
            page = load_page(path)
            for href in page.hrefs():
                if is_internal(href):
                    with self.subTest(page=page.name, href=href):
                        self.assertTrue(resolve(href, path).is_file())

    def test_sitemap_lists_exactly_the_indexable_pages(self):
        root = ET.parse(SITE / "sitemap.xml").getroot()
        listed = {loc.text.strip() for loc in root.iter(f"{SITEMAP_NS}loc")}
        expected = {url_for(path) for path in all_pages() if path.name != "404.html"}
        self.assertEqual(listed, expected)

    def test_robots_points_at_sitemap(self):
        robots = (SITE / "robots.txt").read_text(encoding="utf-8")
        self.assertIn(f"Sitemap: {ORIGIN}/sitemap.xml", robots)

    def test_old_project_paths_not_shadowed(self):
        # hkutluay.com/chronolyze-site/… and /reelo-site/… are served by the old project repos,
        # which the App Store listings still link to. A folder of the same name here would hide them.
        for name in ("chronolyze-site", "reelo-site"):
            self.assertFalse((SITE / name).exists(), name)


class DeployWorkflowTest(unittest.TestCase):
    def test_runs_tests_then_publishes_site_folder(self):
        workflow = (ROOT / ".github" / "workflows" / "pages.yml").read_text(encoding="utf-8")
        self.assertIn("python -m unittest discover", workflow)
        self.assertIn("path: site", workflow)
        self.assertIn("actions/deploy-pages@", workflow)
        self.assertLess(workflow.index("unittest discover"), workflow.index("actions/deploy-pages@"))


if __name__ == "__main__":
    unittest.main()
