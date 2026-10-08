"""Images pulled from the App Store must be present and web-sized."""
import unittest

from PIL import Image

from tests.sitelib import APPS, SITE

SHOT_WIDTH = 600
MAX_SHOT_BYTES = 150_000


def size_of(path):
    with Image.open(path) as image:
        return image.size


class AppAssetsTest(unittest.TestCase):
    def test_icons_and_share_image_have_expected_sizes(self):
        for app in APPS:
            img = SITE / app / "img"
            with self.subTest(app=app):
                self.assertEqual(size_of(img / "icon-512.png"), (512, 512))
                self.assertEqual(size_of(img / "icon-180.png"), (180, 180))
                self.assertEqual(size_of(img / "og.png"), (1200, 630))

    def test_every_store_screenshot_is_web_sized(self):
        for app, info in APPS.items():
            shots = sorted((SITE / app / "img").glob("shot-*.webp"))
            with self.subTest(app=app):
                self.assertEqual(
                    [s.name for s in shots],
                    [f"shot-{n}.webp" for n in range(1, info["shots"] + 1)],
                )
                for shot in shots:
                    self.assertEqual(size_of(shot)[0], SHOT_WIDTH, shot.name)
                    self.assertLessEqual(shot.stat().st_size, MAX_SHOT_BYTES, shot.name)


class SharedAssetsTest(unittest.TestCase):
    def test_home_share_image_and_icons(self):
        assets = SITE / "assets"
        self.assertEqual(size_of(assets / "og-home.png"), (1200, 630))
        self.assertEqual(size_of(assets / "favicon.png"), (64, 64))
        self.assertEqual(size_of(assets / "apple-touch-icon.png"), (180, 180))

    def test_app_store_badge_is_svg(self):
        badge = (SITE / "assets" / "appstore-badge.svg").read_text(encoding="utf-8")
        self.assertIn("<svg", badge)


if __name__ == "__main__":
    unittest.main()
