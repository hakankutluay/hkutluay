"""Shared helpers for the site tests: where things live, and a small model of an HTML page."""
from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
SITE = ROOT / "site"
ORIGIN = "https://hkutluay.com"

APPS = {
    "chronolyze": {"id": "6790505948", "name": "Chronolyze", "shots": 6},
    "reelo": {"id": "6783331223", "name": "Reelo", "shots": 7},
}

# Hosts that pages may link to (never load from).
ALLOWED_LINK_HOSTS = {"apps.apple.com", "www.apple.com", "firebase.google.com", "policies.google.com"}


def normalize(text: str) -> str:
    return " ".join(text.split())


@dataclass
class Page:
    path: Path
    lang: str | None = None
    title: str = ""
    body_classes: list[str] = field(default_factory=list)
    metas: dict[str, str] = field(default_factory=dict)  # name or property -> content
    links: list[dict[str, str]] = field(default_factory=list)  # <link> attributes
    anchors: list[dict[str, str]] = field(default_factory=list)
    images: list[dict[str, str]] = field(default_factory=list)
    scripts: list[dict[str, str]] = field(default_factory=list)
    headings: list[str] = field(default_factory=list)  # h1-h3 text, in document order
    main_text: str = ""

    @property
    def name(self) -> str:
        return self.path.relative_to(SITE).as_posix()

    def link_href(self, rel: str) -> str | None:
        for link in self.links:
            if rel in link.get("rel", "").split():
                return link.get("href")
        return None

    def hrefs(self) -> list[str]:
        return [a["href"] for a in self.anchors if "href" in a]

    def resource_refs(self) -> list[str]:
        """URLs the browser fetches to render the page (not navigation links)."""
        refs = [link["href"] for link in self.links if "href" in link and link.get("rel") != "canonical"]
        refs += [img["src"] for img in self.images if "src" in img]
        refs += [script["src"] for script in self.scripts if "src" in script]
        return refs


class _PageParser(HTMLParser):
    def __init__(self, page: Page):
        super().__init__(convert_charrefs=True)
        self.page = page
        self.in_title = False
        self.heading: list[str] | None = None
        self.skip = 0
        self.main_depth = 0
        self.main_chunks: list[str] = []

    def handle_starttag(self, tag, attrs):
        a = {key: value or "" for key, value in attrs}
        if tag == "html":
            self.page.lang = a.get("lang")
        elif tag == "title":
            self.in_title = True
        elif tag == "body":
            self.page.body_classes = a.get("class", "").split()
        elif tag == "meta":
            key = a.get("name") or a.get("property")
            if key:
                self.page.metas[key] = a.get("content", "")
        elif tag == "link":
            self.page.links.append(a)
        elif tag == "a":
            self.page.anchors.append(a)
        elif tag == "img":
            self.page.images.append(a)
        elif tag == "script":
            self.page.scripts.append(a)
            self.skip += 1
        elif tag == "style":
            self.skip += 1
        elif tag == "main":
            self.main_depth += 1
        elif tag in ("h1", "h2", "h3"):
            self.heading = []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        elif tag in ("script", "style"):
            self.skip -= 1
        elif tag == "main":
            self.main_depth -= 1
        elif tag in ("h1", "h2", "h3") and self.heading is not None:
            self.page.headings.append(normalize(" ".join(self.heading)))
            self.heading = None

    def handle_data(self, data):
        if self.skip:
            return
        if self.in_title:
            self.page.title += data
        if self.heading is not None:
            self.heading.append(data)
        if self.main_depth:
            self.main_chunks.append(data)


class _TextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.chunks: list[str] = []
        self.skip = 0

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "title"):
            self.skip += 1

    def handle_endtag(self, tag):
        if tag in ("script", "style", "title"):
            self.skip -= 1

    def handle_data(self, data):
        if not self.skip:
            self.chunks.append(data)


def visible_text(html: str) -> str:
    """Text a reader sees, whitespace-normalized (same joining rule as Page.main_text)."""
    parser = _TextParser()
    parser.feed(html)
    parser.close()
    return normalize(" ".join(parser.chunks))


def load_page(path: Path) -> Page:
    page = Page(path=path)
    parser = _PageParser(page)
    parser.feed(path.read_text(encoding="utf-8"))
    parser.close()
    page.title = normalize(page.title)
    page.main_text = normalize(" ".join(parser.main_chunks))
    return page


def all_pages() -> list[Path]:
    return sorted(SITE.rglob("*.html"))


def url_for(path: Path) -> str:
    """Public URL GitHub Pages serves a file at (directory URLs keep their trailing slash)."""
    rel = path.relative_to(SITE).as_posix()
    if rel == "index.html":
        return ORIGIN + "/"
    if rel.endswith("/index.html"):
        return f"{ORIGIN}/{rel[: -len('index.html')]}"
    return f"{ORIGIN}/{rel}"


def is_internal(ref: str) -> bool:
    parts = urlsplit(ref)
    if parts.scheme in ("http", "https"):
        return parts.netloc == "hkutluay.com"
    return parts.scheme == ""


def resolve(ref: str, page_path: Path) -> Path:
    """Map an internal URL to the file GitHub Pages would serve for it."""
    path = urlsplit(ref).path
    if not path:  # a bare fragment such as "#top"
        return page_path
    base = SITE if path.startswith("/") else page_path.parent
    target = base / path.lstrip("/")
    if path.endswith("/") or target.is_dir():
        target = target / "index.html"
    return target
