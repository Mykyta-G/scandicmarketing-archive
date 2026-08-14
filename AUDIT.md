# Scandic Marketing — Technical & SEO Audit

**Site:** https://www.scandicmarketing.se/
**Audited:** 2026-08-14
**Method:** Raw HTTP responses, production JS/CSS bundle analysis, structured-data and sitemap inspection. No access to source code or the Supabase project — everything below is observable from the public site.

---

## The headline

Scandic Marketing sells SEO. Their own site ships **zero content to search engines**.

Every URL on the domain returns the same 19,882-byte HTML file with an empty `<div id="root">`. The copy, the services, the case studies, the pricing — all of it exists only after JavaScript runs. There is an SSR placeholder in the HTML (`<!--ssr-outlet-->`) that never gets filled, which means server rendering was set up and is not actually running in production.

That single fact causes most of what follows.

---

## Stack (as deployed)

| Layer | What's there |
|---|---|
| Host | Vercel (edge cached, HSTS on) |
| Framework | Vite + React 18.3.1, client-rendered SPA |
| Styling | Tailwind CSS, Inter via Google Fonts |
| Icons | lucide-react |
| Backend | Supabase JS 2.86.0 (`anon` key — correct key type for a browser) |
| Email | Resend |

The stack is fine. The build and configuration are where the problems are.

---

## Critical — costs money right now

### 1. A placeholder phone number is live on the contact section

The contact block renders:

```
Telefon    +46 70 123 45 67
```

`070-123 45 67` is the Swedish equivalent of `555-0100`. It is a dummy number. The real number — `+46 76 929 85 01` — appears elsewhere on the site and in the LocalBusiness structured data.

So: a visitor who reaches the contact section and wants to call cannot. And Google sees two different phone numbers for the same business, which undercuts the local-SEO consistency (NAP) that a Helsingborg agency depends on to rank.

**This is the single highest-value fix on the list and it takes one line.**

### 2. Every page has the same title, description, and canonical

`/`, `/hemsida`, `/videoproduktion`, `/fotografi`, `/marknadsföring`, `/contact` — all return byte-identical HTML. Which means every page declares:

```html
<title>Scandic Marketing - Expert på Digital Marknadsföring, Marketing & SEO | Helsingborg</title>
<link rel="canonical" href="https://scandicmarketing.se/" />
```

The canonical tag on every subpage points at the homepage. That is an explicit instruction to Google: *"this page is a duplicate of the homepage, don't index it."* The service pages — the ones that should rank for "videoproduktion Helsingborg", "fotograf Helsingborg" — are telling Google to drop them.

### 3. 404s return HTTP 200

`https://www.scandicmarketing.se/this-page-does-not-exist-12345` → **HTTP 200**.

Every typo, every stale backlink, every crawler guess returns a "successful" page. Google calls these soft 404s. It wastes crawl budget and can pull down site-wide quality signals.

### 4. The canonical points at a URL that redirects

- Canonical says: `https://scandicmarketing.se/` (no www)
- The apex actually **307-redirects** to `https://www.scandicmarketing.se/`
- The sitemap lists all URLs on the apex too

So the declared canonical URL is not the URL that serves content. And the redirect is a **307 (temporary)** where it should be a **301 (permanent)** — temporary redirects don't consolidate ranking signals the way permanent ones do.

Pick one hostname, 301 to it, make canonical and sitemap agree.

---

## High — actively working against them

### 5. The `<meta name="keywords">` tag is ~11.4 KB of keyword stuffing

Of the 19,849-byte homepage, **11,452 bytes are a single keywords meta tag** — thousands of comma-separated phrases, heavily repeated: *"marketing soul, marketing heart, marketing essence, marketing DNA…"*

Two problems:

- **Google has ignored meta keywords since 2009.** It does nothing. Bing has stated it can be used as a *spam* signal.
- It's 58% of the page weight, sent on every single request.

For a company selling SEO expertise, this is the tag most likely to be noticed by a prospect who views source. It should be deleted entirely.

### 6. Content is hidden until React hydrates

There's an inline style and script that set `#root` to `opacity: 0; visibility: hidden` until a `data-hydrated` attribute appears. Combined with client-only rendering and a 673 KB JS bundle, the visitor sees a **blank white page** until the entire bundle downloads, parses, and executes.

On a mid-range phone on Swedish 4G, that's a meaningfully long stare at nothing. It also means Largest Contentful Paint can't happen until JS finishes — the metric Google uses as a ranking signal is structurally capped.

### 7. One 673 KB JavaScript bundle, no code splitting

- `main-BevAveg5.js` — **673 KB raw / 194.5 KB compressed**
- `main-vtf0E0Kb.css` — 82 KB raw / 14.5 KB compressed

Single chunk. Someone landing on the photography page downloads the booking forms, the pricing tables, the video production page, and the entire Supabase client before anything paints. Route-level code splitting is standard in Vite and isn't being used.

### 8. Link previews are broken

```html
<meta property="og:image" content=".../scandic-marketing-logo.png" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
```

The actual file is **1080 × 314** — a wide logo strip, not a 1.91:1 social card. Declared dimensions don't match reality, so LinkedIn, Facebook, and WhatsApp will crop or letterbox it.

Every time Scandic Marketing shares their own link, the preview looks wrong. For a marketing agency this is the most visible possible own-goal.

---

## Medium

### 9. Inconsistent URL scheme

```
/marknadsföring      ← non-ASCII "ö" (encodes to /marknadsf%C3%B6ring)
/anvandarvillkor     ← ASCII-folded (no "ä")
/contact             ← English, among otherwise Swedish slugs
/booking             ← English
/hemsida/boka        ← Swedish
```

Three conventions in one site. `/marknadsföring` percent-encodes into an ugly URL in shares, analytics, and Search Console. Recommend all-ASCII Swedish slugs: `/marknadsforing`, `/kontakt`, `/boka`.

### 10. Sitemap `lastmod` is ~19 months stale

Every entry says `2025-01-22`. The site was last deployed **2026-08-11** (per `last-modified`). Sitemap dates should be generated at build time, not hand-written.

### 11. Four contact email addresses

`info@`, `kontakt@`, `foto@`, `video@` — all used in different places. Fine if deliberate and all monitored; a lead-loss risk if they're aspirational. Worth confirming each one actually receives mail.

### 12. Verify Supabase Row Level Security

The `anon` key in the bundle is **correct and expected** — that key is designed to be public, and no service-role key is exposed. But it is only safe if Row Level Security is enabled on every table the forms touch. Without RLS, a public anon key means anyone can read the contact-form submissions.

I did not test this — probing someone else's database isn't mine to do. **Ask the owner to confirm RLS is on before anything else ships.** It's a two-minute check in the Supabase dashboard.

### 13. Unverified performance claims

The site advertises 500%, 790%, 340%, 250%, 190% improvements and "100+ företag". Swedish marketing law (marknadsföringslagen) requires substantiation for measurable claims. If the data exists, cite the timeframe and metric — specifics are more persuasive than round numbers anyway. If it doesn't, soften the language.

---

## What's already good

Worth saying plainly, because it's not a bad site — it's a well-built site with a broken delivery layer:

- **Structured data is genuinely solid.** Organization, LocalBusiness, and WebSite schemas, with a real street address, geo coordinates, and opening hours. Most small agencies have none of this.
- **`robots.txt` is clean** and correctly points at the sitemap.
- **Tailwind design system** — consistent spacing and type, one typeface (Inter), coherent blue palette.
- **The copy is good.** Clear service descriptions, specific case studies, transparent pricing (499/1499 kr per month, ex-moms, 12-month terms). The "rent, don't buy a website" angle is a sharp positioning move.
- **HSTS enabled**, sane cache headers, hosted on solid infrastructure.

The content and design work is done. It's being delivered in a way that hides it from search engines and shows users a blank screen first.

---

## Recommended fix order

**Same day — no rebuild needed:**
1. Fix the placeholder phone number
2. Delete the `<meta name="keywords">` tag (removes 58% of page weight)
3. Regenerate the og:image at 1200×630
4. Confirm Supabase RLS is enabled

**Structural — needs a build change:**
5. Server-render or statically generate every route (fixes #2, #3, #6 at once)
6. Per-page title, description, and canonical
7. Real 404 status codes
8. 301 apex → www, align canonical + sitemap
9. Route-level code splitting
10. ASCII-consistent Swedish slugs with 301s from the old paths

Items 5–8 are all the same root cause. Fixing the rendering strategy fixes most of this audit in one move.

---

## The honest recommendation

Patching the current Vite SPA can fix every item above — Vite has an SSR mode, and the existing `<!--ssr-outlet-->` shows someone already started down that path.

But if the goal is a site that is structurally incapable of these problems, moving the same React components to a framework with file-based routing and static generation makes per-page metadata, real 404s, and route-split bundles the *default* rather than something to maintain. The components, Tailwind config, copy, and Supabase logic all carry over — this is a re-platform, not a rewrite.

Either path is legitimate. The four same-day fixes are worth doing regardless, today.
