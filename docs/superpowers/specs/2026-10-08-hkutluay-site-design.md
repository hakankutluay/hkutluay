# hkutluay.com — Design Spec

- **Date:** 2026-10-08
- **Owner:** Hakan Kutluay
- **Status:** Approved in chat; awaiting written-spec review

## Goal

Give Hakan's two live iOS apps a real home on the web at **hkutluay.com**, hosted for free,
without breaking the privacy/support URLs the App Store listings already point to.

Success means:

1. `https://hkutluay.com` serves a developer home page linking to both apps.
2. Each app has a marketing page, a privacy page, and a support page under its own path.
3. Every URL currently referenced by App Store Connect keeps resolving (directly or by redirect).
4. Hosting costs nothing; publishing is "push to `main`".
5. Hakan's Zoho email on hkutluay.com keeps working through the DNS change.

## Context (verified 2026-10-08)

### Apps

| | Chronolyze: Watch Accuracy | Reelo: Recurring Reminders |
|---|---|---|
| App Store ID | 6790505948 | 6783331223 |
| Store URL | https://apps.apple.com/app/id6790505948 | https://apps.apple.com/app/id6783331223 |
| Bundle ID | com.hkutluay.chronolyze | com.hkutluay.reelo |
| Version | 1.3.2 | 1.2.4 |
| Price | Free | Free |
| Requires | iOS 26, iPhone + iPad | iOS 26, iPhone + iPad |
| Languages | EN | EN, ES, TR |
| Screenshots | 6 (1284×2778) | 7 (1284×2778) |

### Existing pages (must not break)

App Store Connect currently links to:

- `https://hakankutluay.github.io/chronolyze-site/privacy.html` and `…/support.html`
  (repo `hakankutluay/chronolyze-site`)
- `https://hakankutluay.github.io/reelo-site/privacy.html` and `…/support.html`
  (repo `hakankutluay/reelo-site`)

Neither repo has an `index.html`. Neither app lists a Developer Website.
Contact email on all four pages: `hkutluay@hotmail.com`.

### Domain

- Registrar: **Squarespace Domains** (migrated from Google Domains). DNS is edited in the
  Squarespace Domains panel (nameservers `ns-cloud-a{1..4}.googledomains.com`).
- Apex currently points to parking IPs `15.197.142.173`, `3.33.152.147`; `www` CNAMEs to apex.
- **Zoho Mail is live** on the domain: MX `mx.zoho.eu` (10), `mx2.zoho.eu` (20), `mx3.zoho.eu` (50);
  TXT `zoho-verification=…` and `v=spf1 include:zohomail.eu ~all`. These must not change.

## Decisions

| Topic | Decision | Why |
|---|---|---|
| Host | GitHub Pages, repo `hakankutluay/hakankutluay.github.io` | Already in use, free, HTTPS included, custom domain supported |
| Site tech | Hand-written HTML + one CSS file, no build step | ~8 pages; a generator adds dependencies for no gain |
| Deploy | GitHub Actions workflow publishes only the `site/` folder on push to `main` | Keeps `docs/` and tooling out of the public site |
| Domain | Apex `hkutluay.com` is canonical; `www` redirects to it; HTTPS enforced | Short, matches the email domain |
| One site vs per-app | One site, apps under `/chronolyze/` and `/reelo/` | Hakan's choice |
| Display name | "Hakan Kutluay" | Hakan's choice |
| Fonts | System stacks only (SF Pro / SF Pro Rounded on Apple devices) | No third-party requests; the audience is on iOS |
| Analytics / cookies | None | No consent banner needed; matches the apps' privacy stance |
| Language | English only | YAGNI; Reelo's ES/TR can come later |

## Site map

```
/                         Home: intro + two app cards
/chronolyze/              Chronolyze marketing page
/chronolyze/privacy/      Chronolyze privacy policy (text carried over verbatim)
/chronolyze/support/      Chronolyze support (text carried over verbatim)
/reelo/                   Reelo marketing page
/reelo/privacy/           Reelo privacy policy (text carried over verbatim)
/reelo/support/           Reelo support + FAQ (text carried over verbatim)
/404.html                 Not-found page
/robots.txt, /sitemap.xml
```

## Repository layout

```
hakankutluay.github.io/
├── .github/workflows/pages.yml     Deploy site/ to GitHub Pages
├── site/                           Everything that gets published
│   ├── index.html
│   ├── 404.html
│   ├── robots.txt
│   ├── sitemap.xml
│   ├── assets/
│   │   ├── site.css                Shared layout + components; themes via CSS custom properties
│   │   ├── favicon.png             Neutral "hk" monogram for home/404 (see Favicon)
│   │   └── appstore-badge.svg      Apple's official black "Download on the App Store" badge
│   ├── chronolyze/
│   │   ├── index.html
│   │   ├── privacy/index.html
│   │   ├── support/index.html
│   │   └── img/                    icon-512.png, icon-180.png, og.png, shot-1..6.webp
│   └── reelo/
│       ├── index.html
│       ├── privacy/index.html
│       ├── support/index.html
│       └── img/                    icon-512.png, icon-180.png, og.png, shot-1..7.webp
├── tools/
│   └── fetch_store_assets.py       Pulls icons + screenshots from the iTunes Lookup API, writes WebP/PNG
└── docs/superpowers/               Specs and plans (not published)
```

`fetch_store_assets.py` is kept so screenshots can be refreshed after future app updates.
It depends only on Pillow.

## Visual design

One stylesheet. Each page sets a theme class on `<body>` (`theme-home`, `theme-chronolyze`,
`theme-reelo`); themes only redefine custom properties, components never hard-code colours.

### Theme tokens (sampled from the apps' own store assets)

| Token | Home (light) | Home (dark) | Chronolyze | Reelo |
|---|---|---|---|---|
| `--bg` | `#f7f6f2` | `#0e0f11` | `#f0f2ea` (cream) | `#faf9f3` (cream) |
| `--ink` | `#111111` | `#f2f2f0` | `#0b1a1f` | `#0d0d0d` |
| `--muted` | `#5b5b57` | `#a3a39e` | `#4f6662` | `#55554f` |
| `--accent` | `#111111` | `#f2f2f0` | `#0e6761` (watch green) | `#0048fe` (electric blue) |
| `--accent-2` | — | — | `#61aba1` (teal label) | `#e7fb67` (lime) |
| `--hero-bg` | — | — | `#061628` (icon navy) | `#0048fe` |
| `--hero-ink` | — | — | `#f0f2ea` | `#ffffff` with lime highlight |

- Home follows `prefers-color-scheme`. App pages keep their brand palette in both modes,
  because the brands are defined by them.
- Type: `-apple-system, BlinkMacSystemFont, "SF Pro Display", "Segoe UI", Roboto, Helvetica, Arial, sans-serif`.
  Reelo headings use `ui-rounded, "SF Pro Rounded", <same stack>`.
- Headlines are heavy (800), tight letter-spacing, as in the store screenshots. Chronolyze
  headlines use two tones (ink line + green line); Reelo uses white + lime on blue.
- Layout: centred column, max 1120px; 16px side gutter on phones; no horizontal page scroll.

### Components

- **Site header:** small wordmark ("Hakan Kutluay" on home; app wordmark + "by Hakan Kutluay" on app pages).
- **App card (home):** full-bleed rounded card in the app's hero colours: icon, name, one-line
  pitch, "Learn more →". Two cards side by side on desktop, stacked on phones.
- **Hero (app page):** icon, headline, one-paragraph pitch, App Store badge, small "Free · iPhone & iPad · iOS 26+" line.
- **Screenshot strip:** horizontal scroll-snap row of the store screenshots, `loading="lazy"`,
  explicit width/height to avoid layout shift. Keyboard-scrollable, with alt text describing each screen.
- **Feature grid:** 2–3 columns on desktop, 1 on phones; short title + 1–2 sentence body.
- **Footer:** Privacy · Support · App Store · Home, contact email, © 2026 Hakan Kutluay.
- **Legal page layout:** narrow reading column (max 680px), app wordmark at top, same footer.

### Favicon

Home uses a neutral monogram favicon ("hk", generated as PNG). App pages use their own app icon as favicon/apple-touch-icon.

## Page content

### Home

- Title: "Hakan Kutluay — iOS apps"
- Intro: "Hi, I'm Hakan. I build small, focused iOS apps." (one line; editable)
- Card 1 — Chronolyze: "Is your watch keeping time? Turn your iPhone into a timegrapher for mechanical watches."
- Card 2 — Reelo: "Reminders that restart when you do. For the things you do again and again."

### Chronolyze page

- Headline: "Is your watch keeping time?" Pitch condensed from the store description's first paragraph.
- Features (from the store description): Live measurement (rate, beat error, amplitude, stability,
  12,000–36,000 bph auto-detect); Accuracy tracking (on-wrist, no microphone needed); Positional
  test (six positions, Δ); Magnetization check; Watch collection (iCloud sync); 104-movement library.
- "What you need": a quiet room and a mechanical watch; quartz isn't supported.
- Disclaimer line from the support page: reference tool, not professional instrumentation.

### Reelo page

- Headline: "Reminders that restart when you do."
- Pitch: "Contact lenses every 30 days. Water the plant every 3 days. Set it once, never forget again."
- Features: Counts from completion; Flexible scheduling (every N days/weeks/months/years, pre-alerts,
  time of day); Follow-up nudges; Stay organized (Overdue/Today/This Week/Later, pause, search);
  Calendar view; Widgets (home + lock screen); iCloud sync.

### Privacy and support pages

Body text copied verbatim from the existing `privacy.html` / `support.html` in each repo, including
"Last updated" dates. Only markup/styling changes. Each gets `<link rel="canonical">` to its new URL.

## Metadata (every page)

- `<title>`, `<meta name="description">`, `<link rel="canonical">`, `lang="en"`, viewport meta.
- App pages: `<meta name="apple-itunes-app" content="app-id=…">` (Smart App Banner).
- Open Graph + Twitter card: title, description, `og:image` = a 1200×630 PNG composed from the
  app icon on its hero colour (generated by `fetch_store_assets.py`). Home uses a simple text card.
- `apple-touch-icon`, favicon.

## URL migration

1. **Launch:** once `hkutluay.com` is set on the user site, GitHub serves the old project sites at
   `hkutluay.com/chronolyze-site/…` and `hkutluay.com/reelo-site/…`, and redirects the old
   `hakankutluay.github.io/…` URLs there. Nothing breaks on day one.
2. **App Store Connect (Hakan):**
   - Privacy Policy URL → `https://hkutluay.com/<app>/privacy/` (App Privacy section; editable any time).
   - Support URL → `https://hkutluay.com/<app>/support/`; Marketing URL → `https://hkutluay.com/<app>/`
     (version-level fields; change them with the next app update).
3. **Redirect stubs:** after the new site is verified live, replace the old repos'
   `privacy.html` / `support.html` with stubs that redirect to the new URLs (meta refresh +
   `location.replace` + canonical link + a visible link). Old repos stay published indefinitely,
   because older app versions and caches will keep the old URLs.

## DNS changes (Squarespace → Domains → hkutluay.com → DNS)

| Action | Type | Host | Value |
|---|---|---|---|
| Delete | A | @ | `15.197.142.173` |
| Delete | A | @ | `3.33.152.147` |
| Add | A | @ | `185.199.108.153` |
| Add | A | @ | `185.199.109.153` |
| Add | A | @ | `185.199.110.153` |
| Add | A | @ | `185.199.111.153` |
| Add | AAAA | @ | `2606:50c0:8000::153` |
| Add | AAAA | @ | `2606:50c0:8001::153` |
| Add | AAAA | @ | `2606:50c0:8002::153` |
| Add | AAAA | @ | `2606:50c0:8003::153` |
| Change | CNAME | www | `hakankutluay.github.io.` |
| Add | TXT | `_github-pages-challenge-hakankutluay` | value shown by GitHub (Settings → Pages → verified domains) |
| **Keep** | MX / TXT | @ | All Zoho records, unchanged |

If Squarespace has domain forwarding or a "Squarespace Defaults" preset enabled for the domain,
it must be turned off so it doesn't re-add the parking records.

## Responsibilities

- **Claude:** build the site locally, preview it, verify links/assets, write the workflow, write the
  redirect stubs, run post-launch checks.
- **Hakan:** create/authorize the GitHub repo push (Claude will ask before any push), edit DNS in
  Squarespace, set the custom domain + "Enforce HTTPS" in GitHub Pages settings, update App Store Connect.

## Verification

- **Local:** serve `site/` with `python3 -m http.server`; check every page in the browser pane at
  375px and desktop widths, and home in light + dark.
- **Link check:** a small script crawls `site/` and fails on any internal link or asset that 404s.
- **Content check:** privacy/support body text diffed against the originals (whitespace-normalized)
  to prove it was carried over verbatim.
- **Post-launch:** `curl` every URL on `https://hkutluay.com` (expect 200), `http://` and `www`
  (expect 301 → `https://hkutluay.com`), the four old `github.io` URLs (expect redirect, then 200),
  and `dig MX hkutluay.com` still returns Zoho.

## Out of scope

Localization, blog, contact form, analytics, press kit, Android, a CMS. Each can be added later
without changing this structure.
