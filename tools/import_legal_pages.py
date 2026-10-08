#!/usr/bin/env python3
"""One-time import of the existing privacy and support pages into the new site layout.

Downloads the originals from hakankutluay.github.io into tests/fixtures/legal/ (so the tests can
prove the text was carried over verbatim), then writes site/<app>/<kind>/index.html.

Usage: python3 tools/import_legal_pages.py

After the import, edit site/<app>/<kind>/index.html directly; re-running this overwrites it.
"""
from __future__ import annotations

import re
import textwrap
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
FIXTURES = ROOT / "tests" / "fixtures" / "legal"
SOURCE = "https://hakankutluay.github.io/{app}-site/{kind}.html"

APPS = {"chronolyze": ("Chronolyze", "6790505948"), "reelo": ("Reelo", "6783331223")}
KINDS = {"privacy": "Privacy Policy", "support": "Support"}
DESCRIPTIONS = {
    ("chronolyze", "privacy"): "How Chronolyze handles your data: your watch’s ticking is analyzed on your iPhone and the audio is never recorded or sent anywhere.",
    ("chronolyze", "support"): "Help with Chronolyze: how to measure a watch, answers to common questions, tips for the best results and how to contact support.",
    ("reelo", "privacy"): "How Reelo handles your data: your reminders stay on your devices and in your own iCloud account, and are never sold or shared.",
    ("reelo", "support"): "Help with Reelo, the recurring reminder app: how to contact support and answers to common questions.",
}

# Chrome from the old pages that the new layout replaces: footers, the app badge, the wordmark.
OLD_CHROME = [
    r"(?s)<footer>.*?</footer>",
    r'(?s)<span class="badge">.*?</span>\s*',
    r'(?s)<a class="wordmark"[^>]*>.*?</a>\s*',
]

TEMPLATE = """<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{title}</title>
  <meta name="description" content="{description}">
  <link rel="canonical" href="https://hkutluay.com/{app}/{kind}/">
  <link rel="icon" type="image/png" href="/{app}/img/icon-180.png">
  <link rel="apple-touch-icon" href="/{app}/img/icon-180.png">
  <meta property="og:type" content="website">
  <meta property="og:site_name" content="Hakan Kutluay">
  <meta property="og:title" content="{title}">
  <meta property="og:description" content="{description}">
  <meta property="og:url" content="https://hkutluay.com/{app}/{kind}/">
  <meta property="og:image" content="https://hkutluay.com/{app}/img/og.png">
  <meta name="twitter:card" content="summary_large_image">
  <link rel="stylesheet" href="/assets/site.css">
</head>
<body class="theme-{app}">
  <header class="site-header">
    <div class="wrap">
      <a class="brand" href="/{app}/"><img src="/{app}/img/icon-180.png" width="32" height="32" alt=""> {name}</a>
      <nav class="nav" aria-label="{name}">
        <a href="/{app}/">Overview</a>
        <a href="/{app}/{other}/">{other_title}</a>
      </nav>
    </div>
  </header>

  <main class="legal">
{content}
  </main>

  <footer class="site-footer">
    <div class="wrap">
      <p>© 2026 Hakan Kutluay · <a href="mailto:hkutluay@hotmail.com">hkutluay@hotmail.com</a></p>
      <nav aria-label="Footer">
        <a href="/{app}/privacy/">Privacy</a>
        <a href="/{app}/support/">Support</a>
        <a href="https://apps.apple.com/app/id{app_id}">App Store</a>
        <a href="/">Home</a>
      </nav>
    </div>
  </footer>
</body>
</html>
"""


def fetch(url: str) -> str:
    request = urllib.request.Request(url, headers={"User-Agent": "hkutluay-site-import/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8")


def extract_content(original: str, app: str) -> str:
    """The old page's body minus its chrome and outer container, with links pointed at the new URLs."""
    body = re.search(r"(?s)<body[^>]*>(.*)</body>", original).group(1)
    for pattern in OLD_CHROME:
        body = re.sub(pattern, "", body)
    body = re.sub(r"<header>\s*</header>", "", body)  # emptied by removing the wordmark
    body = body.strip()
    container = re.match(r'(?s)<div class="(?:wrap|container)">(.*)</div>$', body)
    if container:
        body = container.group(1)
    body = re.sub(r"</?main>", "", body)
    body = body.replace('href="privacy.html"', f'href="/{app}/privacy/"')
    body = body.replace('href="support.html"', f'href="/{app}/support/"')
    lines = [line.rstrip() for line in textwrap.dedent(body).strip().splitlines()]
    return textwrap.indent(re.sub(r"\n{3,}", "\n\n", "\n".join(lines)), "    ")


def main() -> None:
    FIXTURES.mkdir(parents=True, exist_ok=True)
    for app, (name, app_id) in APPS.items():
        for kind, kind_title in KINDS.items():
            original = fetch(SOURCE.format(app=app, kind=kind))
            (FIXTURES / f"{app}-{kind}.html").write_text(original, encoding="utf-8")
            other = "support" if kind == "privacy" else "privacy"
            page = TEMPLATE.format(
                app=app,
                kind=kind,
                name=name,
                app_id=app_id,
                title=f"{kind_title} — {name}",
                description=DESCRIPTIONS[(app, kind)],
                other=other,
                other_title=KINDS[other],
                content=extract_content(original, app),
            )
            out = SITE / app / kind / "index.html"
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_text(page, encoding="utf-8")
            print(f"{app}/{kind}: imported")


if __name__ == "__main__":
    main()
