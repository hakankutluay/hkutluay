#!/usr/bin/env python3
"""Fetch app icons and screenshots from the App Store and write web-ready images into site/.

Usage: python3 tools/fetch_store_assets.py

Re-run after an app update to refresh the screenshots. Requires Pillow.
If the number of screenshots changes, update the screenshot list in site/<app>/index.html
and APPS in tests/sitelib.py.
"""
from __future__ import annotations

import io
import json
import re
import urllib.request
from pathlib import Path

from PIL import Image, ImageDraw, ImageFilter, ImageFont

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"

APPS = {
    # Chronolyze: icon navy with a faint timegrapher paper grid.
    "chronolyze": {"id": "6790505948", "bg": "#061628", "grid": (97, 171, 161, 34)},
    # Reelo: electric blue with the lime disc from its store artwork.
    "reelo": {"id": "6783331223", "bg": "#0048fe", "disc": "#e7fb67"},
}
HOME_BG = "#f7f6f2"
HOME_INK = "#111111"
SHOT_WIDTH = 600
OG_SIZE = (1200, 630)
BADGE_URL = "https://developer.apple.com/assets/elements/badges/download-on-the-app-store.svg"
LANCZOS = Image.Resampling.LANCZOS


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": "hkutluay-site-assets/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def lookup(app_id: str) -> dict:
    return json.loads(fetch(f"https://itunes.apple.com/lookup?id={app_id}"))["results"][0]


def rendition(url: str, size: str) -> str:
    """mzstatic image URLs end in /<w>x<h>bb.<ext>; ask for a larger PNG rendition instead."""
    return re.sub(r"/\d+x\d+bb\.(jpg|png|webp)$", f"/{size}bb.png", url)


def open_image(url: str) -> Image.Image:
    return Image.open(io.BytesIO(fetch(url))).convert("RGB")


def rounded(image: Image.Image, size: int) -> Image.Image:
    """Resize to a square and clip to the iOS icon corner radius (drawn at 4x for smooth edges)."""
    out = image.resize((size, size), LANCZOS).convert("RGBA")
    big = size * 4
    mask = Image.new("L", (big, big), 0)
    ImageDraw.Draw(mask).rounded_rectangle((0, 0, big - 1, big - 1), radius=int(big * 0.225), fill=255)
    out.putalpha(mask.resize((size, size), LANCZOS))
    return out


def paste_icon(canvas: Image.Image, icon: Image.Image, size: int, xy: tuple[int, int]) -> None:
    """Paste a rounded icon with a soft drop shadow."""
    pad = 48
    shadow = Image.new("RGBA", (size + pad * 2, size + pad * 2), (0, 0, 0, 0))
    ImageDraw.Draw(shadow).rounded_rectangle(
        (pad, pad + 14, pad + size, pad + 14 + size), radius=int(size * 0.225), fill=(0, 0, 0, 80)
    )
    shadow = shadow.filter(ImageFilter.GaussianBlur(20))
    canvas.paste(shadow, (xy[0] - pad, xy[1] - pad), shadow)
    badge = rounded(icon, size)
    canvas.paste(badge, xy, badge)


def app_share_image(icon: Image.Image, cfg: dict) -> Image.Image:
    width, height = OG_SIZE
    canvas = Image.new("RGBA", OG_SIZE, cfg["bg"])
    draw = ImageDraw.Draw(canvas, "RGBA")
    if "grid" in cfg:
        for x in range(0, width, 30):
            draw.line([(x, 0), (x, height)], fill=cfg["grid"], width=1)
        for y in range(0, height, 30):
            draw.line([(0, y), (width, y)], fill=cfg["grid"], width=1)
    if "disc" in cfg:
        draw.ellipse((width - 230, -230, width + 230, 230), fill=cfg["disc"])
    size = 320
    paste_icon(canvas, icon, size, ((width - size) // 2, (height - size) // 2))
    return canvas.convert("RGB")


def home_share_image(icons: list[Image.Image]) -> Image.Image:
    width, height = OG_SIZE
    canvas = Image.new("RGBA", OG_SIZE, HOME_BG)
    size, gap = 260, 72
    x = (width - (size * len(icons) + gap * (len(icons) - 1))) // 2
    for icon in icons:
        paste_icon(canvas, icon, size, (x, (height - size) // 2))
        x += size + gap
    return canvas.convert("RGB")


def monogram(size: int, *, round_corners: bool) -> Image.Image:
    """"hk" mark in Pillow's bundled font (no Apple fonts are rendered into images)."""
    image = Image.new("RGBA", (size, size), (0, 0, 0, 0) if round_corners else HOME_INK)
    draw = ImageDraw.Draw(image)
    if round_corners:
        draw.rounded_rectangle((0, 0, size - 1, size - 1), radius=int(size * 0.225), fill=HOME_INK)
    font = ImageFont.load_default(size=int(size * 0.52))
    draw.text((size / 2, size / 2), "hk", font=font, fill=HOME_BG, anchor="mm")
    return image


def write_app_assets(app: str, cfg: dict) -> Image.Image:
    info = lookup(cfg["id"])
    out = SITE / app / "img"
    out.mkdir(parents=True, exist_ok=True)
    for old in out.glob("shot-*.webp"):
        old.unlink()

    icon = open_image(rendition(info["artworkUrl512"], "1024x1024"))
    icon.resize((512, 512), LANCZOS).save(out / "icon-512.png", optimize=True)
    icon.resize((180, 180), LANCZOS).save(out / "icon-180.png", optimize=True)
    app_share_image(icon, cfg).save(out / "og.png", optimize=True)

    for n, url in enumerate(info["screenshotUrls"], start=1):
        shot = open_image(rendition(url, "1290x2796"))
        height = round(shot.height * SHOT_WIDTH / shot.width)
        shot.resize((SHOT_WIDTH, height), LANCZOS).save(out / f"shot-{n}.webp", quality=82, method=6)
    print(f"{app}: icon, share image, {len(info['screenshotUrls'])} screenshots")
    return icon


def main() -> None:
    icons = [write_app_assets(app, cfg) for app, cfg in APPS.items()]
    assets = SITE / "assets"
    assets.mkdir(parents=True, exist_ok=True)
    home_share_image(icons).save(assets / "og-home.png", optimize=True)
    monogram(64, round_corners=True).save(assets / "favicon.png", optimize=True)
    monogram(180, round_corners=False).save(assets / "apple-touch-icon.png", optimize=True)
    (assets / "appstore-badge.svg").write_bytes(fetch(BADGE_URL))
    print("home: share image, favicon, touch icon, App Store badge")


if __name__ == "__main__":
    main()
