"""Checks every page in site/ must pass, plus page-specific content checks."""
import unittest
from urllib.parse import urlsplit

from PIL import Image

from tests.sitelib import (
    ALLOWED_LINK_HOSTS,
    APPS,
    ORIGIN,
    SITE,
    all_pages,
    is_internal,
    load_page,
    resolve,
    url_for,
)

THEMES = {"theme-home", "theme-chronolyze", "theme-reelo"}

APP_PAGES = {
    "chronolyze": {
        "h1": "Is your watch keeping time?",
        "features": [
            "Live measurement",
            "Classic trace",
            "Accuracy tracking",
            "Positional test",
            "Magnetization check",
            "Watch collection",
            "104 movements built in",
            "Plain-language verdicts",
        ],
    },
}


class EveryPageTest(unittest.TestCase):
    def setUp(self):
        self.pages = [load_page(path) for path in all_pages()]
        self.assertTrue(self.pages, "site/ has no pages yet")

    def indexable(self):
        return [page for page in self.pages if page.path.name != "404.html"]

    def test_document_basics(self):
        for page in self.pages:
            with self.subTest(page=page.name):
                self.assertEqual(page.lang, "en")
                self.assertTrue(page.title)
                self.assertIn("width=device-width", page.metas.get("viewport", ""))
                self.assertGreaterEqual(len(page.metas.get("description", "")), 50)
                self.assertEqual(len(THEMES & set(page.body_classes)), 1, page.body_classes)

    def test_canonical_and_og_url_match_location(self):
        for page in self.indexable():
            with self.subTest(page=page.name):
                self.assertEqual(page.link_href("canonical"), url_for(page.path))
                self.assertEqual(page.metas.get("og:url"), url_for(page.path))

    def test_share_image_exists(self):
        for page in self.indexable():
            image = page.metas.get("og:image", "")
            with self.subTest(page=page.name):
                self.assertTrue(image.startswith(ORIGIN + "/"), image)
                self.assertTrue(resolve(image, page.path).is_file(), image)

    def test_resources_are_local_and_exist(self):
        for page in self.pages:
            for ref in page.resource_refs():
                with self.subTest(page=page.name, ref=ref):
                    self.assertTrue(is_internal(ref), "pages must not load third-party resources")
                    self.assertTrue(resolve(ref, page.path).is_file())

    def test_internal_refs_are_root_absolute(self):
        # Root-absolute paths let /404.html render styled at any depth, e.g. /chronolyze/nope/.
        for page in self.pages:
            refs = page.resource_refs() + [h for h in page.hrefs() if is_internal(h)]
            for ref in refs:
                with self.subTest(page=page.name, ref=ref):
                    self.assertTrue(ref.startswith("/") or ref.startswith("#"), ref)

    def test_external_links_are_https_to_expected_hosts(self):
        for page in self.pages:
            for href in page.hrefs():
                parts = urlsplit(href)
                if parts.scheme in ("http", "https") and not is_internal(href):
                    with self.subTest(page=page.name, href=href):
                        self.assertEqual(parts.scheme, "https")
                        self.assertIn(parts.netloc, ALLOWED_LINK_HOSTS)
            for anchor in page.anchors:
                if anchor.get("target") == "_blank":
                    with self.subTest(page=page.name, href=anchor.get("href")):
                        self.assertIn("noopener", anchor.get("rel", ""))

    def test_store_ids_match_app_section(self):
        # A page under site/<app>/ may only point at that app's App Store listing.
        for page in self.pages:
            app = page.name.split("/")[0]
            if app not in APPS:
                continue
            app_id = APPS[app]["id"]
            with self.subTest(page=page.name):
                for href in page.hrefs():
                    if "apps.apple.com" in href:
                        self.assertEqual(href, f"https://apps.apple.com/app/id{app_id}")
                banner = page.metas.get("apple-itunes-app")
                if banner is not None:
                    self.assertEqual(banner, f"app-id={app_id}")

    def test_images_have_alt_and_dimensions(self):
        for page in self.pages:
            for img in page.images:
                with self.subTest(page=page.name, src=img.get("src")):
                    self.assertIn("alt", img)
                    self.assertTrue(img.get("width") and img.get("height"))
                    if img["src"].endswith(".webp"):
                        with Image.open(resolve(img["src"], page.path)) as image:
                            self.assertEqual((int(img["width"]), int(img["height"])), image.size)


class HomePageTest(unittest.TestCase):
    def setUp(self):
        self.page = load_page(SITE / "index.html")

    def test_links_to_both_apps(self):
        self.assertIn("/chronolyze/", self.page.hrefs())
        self.assertIn("/reelo/", self.page.hrefs())

    def test_uses_home_theme_and_intro(self):
        self.assertIn("theme-home", self.page.body_classes)
        self.assertEqual(self.page.headings[0], "Hi, I’m Hakan.")


class AppPageMixin:
    app = ""

    def setUp(self):
        self.page = load_page(SITE / self.app / "index.html")
        self.info = APPS[self.app]
        self.expected = APP_PAGES[self.app]

    def test_smart_app_banner(self):
        self.assertEqual(self.page.metas.get("apple-itunes-app"), f"app-id={self.info['id']}")

    def test_links_to_store_listing_more_than_once(self):
        store = [h for h in self.page.hrefs() if "apps.apple.com" in h]
        self.assertGreaterEqual(len(store), 2)
        self.assertEqual(set(store), {f"https://apps.apple.com/app/id{self.info['id']}"})

    def test_headline_and_features(self):
        self.assertEqual(self.page.headings[0], self.expected["h1"])
        for feature in self.expected["features"]:
            self.assertIn(feature, self.page.headings)

    def test_shows_every_screenshot_in_order(self):
        shots = [img["src"] for img in self.page.images if "/img/shot-" in img["src"]]
        self.assertEqual(shots, [f"/{self.app}/img/shot-{n}.webp" for n in range(1, self.info["shots"] + 1)])

    def test_links_to_privacy_and_support(self):
        self.assertIn(f"/{self.app}/privacy/", self.page.hrefs())
        self.assertIn(f"/{self.app}/support/", self.page.hrefs())

    def test_uses_app_theme(self):
        self.assertIn(f"theme-{self.app}", self.page.body_classes)


class ChronolyzePageTest(AppPageMixin, unittest.TestCase):
    app = "chronolyze"


class NotFoundPageTest(unittest.TestCase):
    def test_is_not_indexed_and_links_home(self):
        page = load_page(SITE / "404.html")
        self.assertIn("noindex", page.metas.get("robots", ""))
        self.assertIn("/", page.hrefs())


if __name__ == "__main__":
    unittest.main()
