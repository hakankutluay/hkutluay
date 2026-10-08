# hkutluay.com Implementation Plan

> Executed inline (native) in the session that wrote it — Hakan asked to proceed without further gates.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and publish hkutluay.com — a home page plus marketing, privacy and support pages for Chronolyze and Reelo — on GitHub Pages for free.

**Architecture:** Hand-written HTML + one CSS file in `site/`, themed per app with CSS custom properties. Python tools (stdlib + Pillow) pull App Store assets and import the existing legal pages once. A `unittest` suite guards metadata, links, assets and verbatim legal text; a GitHub Actions workflow runs it and publishes `site/`.

**Tech Stack:** HTML, CSS, Python 3 (stdlib `unittest`, `html.parser`), Pillow, GitHub Actions, GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-10-08-hkutluay-site-design.md`

## Global Constraints

- Canonical origin `https://hkutluay.com`; directory URLs end in `/`.
- App Store IDs: Chronolyze `6790505948`, Reelo `6783331223`; store links exactly `https://apps.apple.com/app/id<ID>`.
- Display name "Hakan Kutluay"; footer "© 2026 Hakan Kutluay"; contact `hkutluay@hotmail.com`.
- No third-party requests from pages: no external scripts, stylesheets, fonts or analytics. System font stacks only.
- Every internal URL in markup is root-absolute (starts with `/`).
- Theme token values exactly as in the spec's table.
- Privacy/support body text carried over verbatim.
- Python stdlib + Pillow only. Tests: `python3 -m unittest discover -v`.
- Never push, create repos, or change DNS/GitHub/App Store settings without Hakan's OK in chat. Never touch the Zoho MX/TXT records.
- Deviations from spec, decided while planning:
  - Chronolyze's requirement line says "iPhone", because its support FAQ says it's iPhone-only and runs on iPad in compatibility mode.
  - The home share image shows the two app icons rather than text, to avoid rendering Apple's SF fonts into an image.

## Review Focus

1. Phones 320–375px wide: no horizontal page scroll; grids collapse to one column; the screenshot strip scrolls inside itself. Covered by the Task 7 browser check, and by `minmax(min(…, 100%), 1fr)` grids.
2. App Store ID cross-wiring: a Reelo page must never link to Chronolyze's listing, or show its Smart App Banner. Covered by `test_store_ids_match_app_section` (Task 3).
3. 404 at a deep path such as `/chronolyze/nope/` must render styled. Covered by `test_internal_refs_are_root_absolute` (Task 2).
4. The old App Store URLs (`/chronolyze-site/…`, `/reelo-site/…`) must not be shadowed by folders in the new site. Covered by `test_old_project_paths_not_shadowed` (Task 6) and `tools/check_live.sh` (Task 8).
5. Home in dark mode: cards keep their brand colours and text stays legible; app pages ignore dark mode. Covered by the Task 7 browser check.

---

### Task 1: Store asset pipeline

**Files:** Create `tests/__init__.py`, `tests/sitelib.py` (constants `ROOT`, `SITE`, `ORIGIN`, `APPS`), `tests/test_assets.py`, `tools/fetch_store_assets.py`; generates `site/<app>/img/{icon-512.png,icon-180.png,og.png,shot-N.webp}` and `site/assets/{og-home.png,favicon.png,apple-touch-icon.png,appstore-badge.svg}`.

- [ ] Write `test_assets.py`. It checks: icons are 512² and 180²; OG images are 1200×630; screenshot count is 6 and 7; screenshots are 600px wide and ≤150 KB each; favicon 64², touch icon 180²; the badge is an SVG.
- [ ] Run it and confirm it fails.
- [ ] Write `fetch_store_assets.py`. It uses the iTunes Lookup API with mzstatic size rewrites, saves WebP at q82, draws the OG images with Pillow, and draws the monogram in Pillow's bundled font.
- [ ] Run the tool, then the tests, and confirm they pass. Eyeball the OG images, then commit.

### Task 2: Page model, stylesheet, home and 404

**Files:** Extend `tests/sitelib.py` (`Page`, `load_page`, `all_pages`, `url_for`, `is_internal`, `resolve`, `visible_text`, `normalize`, `ALLOWED_LINK_HOSTS`). Create `tests/test_pages.py`, `site/assets/site.css`, `site/index.html`, `site/404.html`.

- [ ] Write the every-page tests:
  - lang, title, viewport, description of at least 50 characters, exactly one theme class
  - canonical and `og:url` equal the page's URL, and `og:image` exists (404 is skipped for both)
  - resources are root-absolute, local, and exist
  - internal hrefs are root-absolute
  - external links use https and an allowed host, and `_blank` links have `noopener`
  - every img has alt, width and height, and webp images match their real size
- [ ] Write the home tests: links to both apps, `theme-home`, and the "Hi, I’m Hakan." heading. Write the 404 tests: `noindex` and a link home.
- [ ] Run the tests and confirm they fail. Write the CSS, the home page and the 404 page. Run them again and confirm they pass, then commit.

### Task 3: Chronolyze page

**Files:** Create `site/chronolyze/index.html`. Modify `tests/test_pages.py`: add `APP_PAGES`, `AppPageMixin`, `ChronolyzePageTest`, and `test_store_ids_match_app_section`.

- [ ] Write the tests:
  - Smart App Banner `app-id=6790505948`
  - every store link equals `https://apps.apple.com/app/id6790505948`, with at least two of them
  - h1 is "Is your watch keeping time?"
  - the 8 feature headings are present
  - screenshots are `shot-1..6` in order
  - links to `/chronolyze/privacy/` and `/chronolyze/support/`
  - `theme-chronolyze`
- [ ] Confirm they fail, build the page, confirm they pass, then commit.

### Task 4: Reelo page

**Files:** Create `site/reelo/index.html`; modify `tests/test_pages.py` to add the Reelo entry to `APP_PAGES` and `ReeloPageTest`.

- [ ] Same checks as Task 3, with ID `6783331223`, h1 "Reminders that restart when you do.", the 8 Reelo features, and 7 screenshots. Confirm the tests fail, build, confirm they pass, then commit.

### Task 5: Privacy and support pages

**Files:** Create `tools/import_legal_pages.py`, `tests/test_legal.py`, `tests/fixtures/legal/*.html` (downloaded originals) and `site/<app>/{privacy,support}/index.html`.

- [ ] Write the tests:
  - `<main>` text equals the original's visible text, after removing the old footer, badge and wordmark
  - titles are "Privacy Policy — App" and "Support — App"
  - no `privacy.html`/`support.html` hrefs remain
  - the footer links to both legal pages
- [ ] Confirm the tests fail, write and run the import tool, confirm they pass, then commit.

### Task 6: Site integrity and deploy workflow

**Files:** Create `site/robots.txt`, `site/sitemap.xml`, `.github/workflows/pages.yml`, `tests/test_site.py`, `README.md`.

- [ ] Write the tests:
  - every internal anchor resolves
  - the sitemap lists exactly the indexable pages
  - robots.txt points at the sitemap
  - `site/chronolyze-site` and `site/reelo-site` don't exist
  - the workflow runs unittest and uploads `path: site`
- [ ] Confirm the tests fail, then write the files. Confirm the full suite passes, then commit.

### Task 7: Browser verification

- [ ] Serve `site/` via `.claude/launch.json` (`python3 -m http.server 8080 --directory site`).
- [ ] At 320px and 375px, check every page: `scrollWidth === clientWidth`, and no element outside `.shots` overflows.
- [ ] Take desktop and phone screenshots of home, both app pages and one legal page.
- [ ] With dark colour scheme, check home: body `rgb(14, 15, 17)`, Chronolyze card `rgb(6, 22, 40)`. Check that the Chronolyze page body stays `rgb(240, 242, 234)`.
- [ ] Fix anything found, re-run the tests, then commit.

### Task 8: Publish (needs Hakan)

- [ ] Hakan creates a public, empty repo `hakankutluay/hakankutluay.github.io`.
- [ ] Hakan sets Settings → Pages → Source: GitHub Actions.
- [ ] With Hakan's OK, add the remote and `git push -u origin main`. Watch the workflow through the public API, then check `https://hakankutluay.github.io/` returns 200.
- [ ] Hakan adds `hkutluay.com` under github.com/settings/pages (verified domains) and copies the TXT record.
- [ ] Hakan edits Squarespace DNS per the spec's table. Then verify with `dig`: A/AAAA point at GitHub, `www` CNAMEs to `hakankutluay.github.io`, the TXT record is present, and MX is still Zoho.
- [ ] Hakan clicks Verify, sets the custom domain `hkutluay.com` in the repo, and enables Enforce HTTPS once the certificate is ready.
- [ ] Run `tools/check_live.sh` (created in this task) and make sure every line reports ok.
- [ ] Hakan updates App Store Connect. The privacy URL can change now; the support and marketing URLs change with the next app versions.

### Task 9: Redirect stubs in old repos (needs Hakan)

- [ ] Clone `chronolyze-site` and `reelo-site` into the scratchpad. Replace their `privacy.html`/`support.html` with stubs that redirect to the new URLs (canonical, meta refresh, `location.replace`, a visible link, `noindex`).
- [ ] Show Hakan the diff. Push only after his OK, then re-run `tools/check_live.sh`.
