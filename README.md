# Scandic Marketing

Rebuild of [scandicmarketing.se](https://www.scandicmarketing.se/) — a marketing,
video and photography agency in Helsingborg.

## Stack

- **Astro 7**, static output — every route is a real HTML file at build time
- **Plain CSS** with custom properties (`src/styles/tokens.css`)
- **Montserrat Variable**, self-hosted via `@fontsource`
- No icon library — inline SVG only

## Commands

```bash
npm run dev      # http://localhost:4321
npm run build    # → dist/
npm run preview
npm run check
```

## Where things live

| Path | What |
|---|---|
| `src/data/site.ts` | **All copy.** Single edit point. Items marked ⚠️ need confirmation. |
| `src/styles/tokens.css` | Colour, type, motion tokens — derived from the logo ink `#001529` |
| `src/components/` | Section components |
| `public/video/` | Hero film, encoded to budget (961 KB / 390 KB) |

## Why this rebuild

The current site is a Lovable-generated client-rendered SPA. Every URL returns
the same empty 19,882-byte shell, so search engines get nothing and every page
shares one canonical. See [AUDIT.md](./AUDIT.md) for all 13 findings and
[PLAN.md](./PLAN.md) for the plan and research.

**Before launch, read [PLAN.md §0](./PLAN.md).** A personnummer is currently
published on the live site, and the performance claims are unsubstantiated under
marknadsföringslagen.
