# hkutluay.com

Website for Hakan Kutluay's iOS apps, Chronolyze and Reelo. Plain HTML and one stylesheet in `site/`,
published to GitHub Pages by `.github/workflows/pages.yml` on every push to `main` (after the tests pass).

## Preview locally

```bash
python3 -m http.server 8080 --directory site
```

Then open http://localhost:8080.

## Test

```bash
python3 -m pip install pillow
python3 -m unittest discover -v
```

## Refresh App Store icons and screenshots

```bash
python3 tools/fetch_store_assets.py
```

If an app's number of screenshots changes, update its screenshot list in `site/<app>/index.html`
and `APPS` in `tests/sitelib.py`.

## After launch

`tools/check_live.sh` checks every public URL, the redirects, and that email (Zoho MX) is untouched.

Design: `docs/superpowers/specs/2026-10-08-hkutluay-site-design.md`
