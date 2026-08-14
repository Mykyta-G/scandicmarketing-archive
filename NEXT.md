# Where we left off

**2026-08-14, kväll.** Everything is committed and pushed to `main`. Dev server is stopped.

```bash
npm run dev        # http://localhost:4321
```

---

## Built and working

- **Hero** — full-viewport film, the wordmark knocked out of it (multiply panel + screen lift), his two buttons, trust line, scroll cue, pause control
- **Client row** — full colour, right-to-left marquee, his exact per-logo widths, Foodtel SVG included
- **Nav** — full bleed to both corners, accent CTA with navy glow, logo cross-fades light→dark past the hero
- **Button system** — one set of variants, fill sweeps in on a 14° skew, same object on every surface

Measured against the live site: HTML 19.9 KB empty shell → **7.4 KB with content**, JS 673 KB → **1 KB**, CSS 82 KB → **13 KB**. Critical path 102 KB, video streams after.

---

## Next up — sections 3 to 9

Order is agreed. All copy already lives in `src/data/site.ts`.

```
3  Siffrorna      18M+ / 353% / 7+  — moved out of the hero, each needs a source line
4  Arbetet        the four cases — proof before explanation
5  Tjänster       the four services
6  Hemsida        499 / 1499 — brought up from the subpage
7  Process        four steps
8  Kontakt        phone, address, hours, a named person
9  Footer         + the legally required company block
```

---

## The Kebnekaise idea — his, and worth building

**"Resultat som är på topp"** with a 3D Kebnekaise you fly around.

Why it works: "på topp" reads twice — top results, and a mountain peak. And it shows *Nordic* through geography rather than through a client claim the site can't cash. That was the blocker on the "through the Nordics" concept.

**Verified feasible.** `api.opentopodata.org` returns real elevation for the massif, free and without a key (1703 m and 1935 m at the summit coordinates, which checks out). A 64×64 grid is ~41 requests at 1/sec.

Three ways to render it, cheapest first:

| | Approach | Cost |
|---|---|---|
| **A** | Pre-rendered turntable of a contour-line terrain, scroll-scrubbed | ~500 KB–1 MB, no WebGL, works on mobile |
| **B** | Three.js terrain from a heightmap, one mesh, no PBR | ~200–300 KB gz |
| **C** | Igloo-class WebGL | 423 KB gz *for the 3D chunk alone*, plus months of specialist work |

**Recommendation: A.** Gets the orbit and the 3D read, costs a fraction, works everywhere, and contour hairlines in navy on the light surface are exactly the design system we already have.

For reference, measured from igloo.inc: 1.49 MB raw / 423 KB compressed for the 3D app, Three.js with Draco + KTX2 + EffectComposer + Bloom, and **140 hand-written fragment shaders**. That is realtime graphics work, not web design.

Note on the phrase: "på topp" is soft enough to read as puffery rather than a measurable claim, so it does not carry the substantiation problem that "353% ROI" does.

---

## Blocked on him

1. **The personnummer must come off the live site.** See [PLAN.md §0.1](./PLAN.md) — it is published as an "Organisationsnummer".
2. **Is the price 499/1499 or 1299/2999?** His own code says both.
3. **CrossFit's logo** is not in the bundle — still missing.
4. **Documentation for every number**, or they get rewritten as attributed results.
5. **Written permission** to name clients.
6. His real deliverables list, and his actual story for the narrative section.

---

## Decisions locked

Light base · brand hue 215° · ink `#001529` · accent `#E2622A` for actions only · Montserrat · no icon library, inline SVG only · Astro static · Swedish at `/`, English later at `/en/`
