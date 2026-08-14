# Scandic Marketing — Site Overhaul

Rebuild of [scandicmarketing.se](https://www.scandicmarketing.se/) — a digital marketing agency in Helsingborg, Sweden.

**Goal:** the best-in-class site in the Nordic marketing-agency niche. Fast, server-rendered, accessible, and structurally incapable of the SEO problems documented in the audit.

## Status

| | |
|---|---|
| Phase | Audit complete — build not yet started |
| Current site | Vite + React SPA on Vercel, client-rendered |
| Target stack | TBD (see [AUDIT.md](./AUDIT.md) → "The honest recommendation") |

## What's here

- **[AUDIT.md](./AUDIT.md)** — full technical and SEO audit of the live site. 13 findings, ranked, with the four same-day fixes separated from the structural ones.

## The short version

The live site is well-designed and well-written, but ships as a client-only React SPA: every URL returns the same empty HTML shell, so search engines get no content, every subpage's canonical tag points at the homepage, and 404s return HTTP 200. A placeholder phone number (`+46 70 123 45 67`) is live on the contact section. An 11.4 KB keyword-stuffing meta tag makes up 58% of the homepage HTML.

Full detail and fix order in [AUDIT.md](./AUDIT.md).

## Business context

**Services:** digital marketing (Google/Meta/TikTok Ads), website subscriptions, video production, photography
**Location:** Redaregatan 48, 252 30 Helsingborg
**Language:** Swedish
**Notable offer:** website rental — 499 kr/mån (Standard) and 1499 kr/mån (Premium), ex. moms, 12-month terms

## License

Private client work. Not for redistribution.
