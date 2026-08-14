# Scandic Marketing — Plan

**Status:** planning. Nothing is being built yet.
**Updated:** 2026-08-14

This document consolidates the audit, four parallel research tracks, and the decisions taken so far. Everything with a number behind it is sourced; where evidence is absent, it says so instead of guessing.

---

## 0. Do these before anything else

These are independent of design and shouldn't wait for it.

### 0.1 🔴 A personnummer is published on the live site

The integritetspolicy renders:

> Organisationsnummer: 20000228-…

That is not an organisationsnummer. Swedish org numbers are ten digits and begin with 5 (AB), 7, or 9. This is twelve digits in `ÅÅÅÅMMDD-NNNN` form — **a personnummer**, published on the open web.

It almost certainly means the business runs as an **enskild firma**, where the personnummer *is* the legal identifier — so it was published in good faith. It should still come down today. It is the raw material for identity fraud.

**Structural fix:** run the client-facing business through an **AB**. That makes the org number publishable and solves §0.2 at the same time.

### 0.2 Legally required company information is missing

| Requirement | Source | Status |
|---|---|---|
| Company name, **säte** (board's kommun), org.nr on the website | **ABL 28 kap. 5 §** — Bolagsverket may issue *vite* | ❌ säte missing, org.nr is a personnummer |
| Name, address, email, org.nr, VAT number, easily and permanently accessible | **E-handelslagen 8 §** | ❌ partial |
| Prices "klart och otvetydigt"; added tax stated separately | **E-handelslagen 9 §** | ✅ already says "exkl. moms" |
| Cookie consent before non-essential cookies; reject as easy as accept | **LEK 9 kap. 28 §**, PTS guidance | ⚠️ a cookie *policy* page exists; no consent mechanism found in the bundle, and no "Avvisa"/"Neka" control |

Missing §8–9 information is treated as **väsentlig** under MFL 10 § (e-handelslagen 15 §) — i.e. a misleading omission.

**F-skatt** is not legally required on a website, but it is the highest leverage-to-effort trust signal available. If a supplier lacks F-skatt approval, the *buyer* becomes liable for 30% withholding (SFL 10:11) and, for a fysisk person, arbetsgivaravgifter (~31.42%, SAL 2:5). Experienced Swedish buyers check. One footer line removes the risk.

### 0.3 🔴 The performance claims are a live legal exposure

The site currently advertises **353% genomsnittlig ROI**, **18M+ omsättning genererad**, **+500% trafik**, **+340% försäljning**.

Swedish marketing law applies a **reverse burden of proof**. Marknadsdomstolen, MD 2012:2:

> *"En näringsidkare som i sin näringsverksamhet använder sig av ett visst påstående ska kunna styrka att påståendet är riktigt. Om näringsidkaren inte kan det ska påståendet anses vara ovederhäftigt och vilseledande."*

Three things sharpen this:

- **MFL 47 §** gives a *competing agency* standing to sue directly. MD 2012:2 was exactly that — a small B2B vendor, sued by a competitor over one website claim, conceded immediately, and still received a prohibition **at 1,000,000 kr vite** plus the other side's costs.
- Taking the claim down afterwards **does not prevent a prohibition**. The court said so explicitly.
- **Reklamombudsmannen** is the fast route to damage: anyone may complain, decisions are published by name, turnaround is weeks. The ICC code it applies covers B2B explicitly, and Article 6 requires documentation to be producible *utan dröjsmål*.

**MFL 4 §** also makes the EU black list apply **even when marketing targets businesses** — so displaying a certification or membership you don't hold is a *per se* violation with no defence. Audit every badge.

**The fix is not deletion — it's attribution.** See §3.4; the attributed version is also more persuasive.

### 0.4 The immediate list

1. Remove the personnummer.
2. Add: registered name, org.nr (once an AB exists), säte, VAT number, street address, email, phone, "Godkänd för F-skatt".
3. Pull every number that can't be documented **today**. Start a substantiation folder.
4. Fix the cookie banner: reject as easy as accept, first layer, same view, no pre-ticks.
5. Remove any badge not actually held.

---

## 1. What's wrong with the current site

Full detail in [AUDIT.md](./AUDIT.md). The root cause: the site was built in **Lovable** (all assets sit under `/lovable-uploads/`), which generates a client-only React SPA.

Consequences, all verified from raw HTTP:

- Every route returns the **same 19,882-byte empty shell**. `<div id="root">` is empty; an `<!--ssr-outlet-->` placeholder is never filled.
- Therefore every page shares one title, one description, and a canonical pointing at the homepage — telling Google not to index the service pages.
- 404s return **HTTP 200**.
- A **11.4 KB keyword-stuffing meta tag** is 58% of the homepage.
- One **673 KB** JS bundle, no code splitting.
- Content is hidden (`opacity: 0`) until React hydrates.
- `og:image` is a 1080×314 logo declared as 1200×630 — every share preview is cropped.
- A **placeholder phone number** (`+46 70 123 45 67`) is live on the contact section.

**One consequence for the plan:** he probably edits the site *in Lovable* today. Moving off it removes his editing method. That is a feature to replace, not a bonus to drop. See §6.

---

## 2. Decisions taken

| Decision | Status |
|---|---|
| Keep his light, navy monochrome base | ✅ locked |
| Brand hue **215°**, ink `#001529` (measured from his logo) | ✅ locked |
| No `lucide-react` or any icon library — hand-written inline SVG | ✅ locked |
| Swedish at `/`, English at `/en/`. Demote "Norden" | ✅ locked |
| Video as **click-to-play showreel**, not autoplay background | ⏳ proposed, see §4 |
| Server-rendered / statically generated | ⏳ proposed |
| Stack and editing model | ❓ open, see §6 |

**Rejected:** five colourful directions (A–E) and `signature.html`, all archived under `mockups/archive/`. They read as template — rounded corners, drop shadows, gradient cards. `scandic.html` is also rejected: it is a near-copy of the Perfume-Website system rather than an identity derived from Scandic.

---

## 3. The page

### 3.1 What the best sites actually do

Section order extracted from live markup, not guessed:

- **[Instrument](https://www.instrument.com)** — Work → Client Roster → **Services** → Recognition → Purpose → News → Contact. **Proof before explanation.** Services are third, not first.
- **[Designjoy](https://designjoy.co)** — the closest analogue: one person, productized subscription, price on the homepage, and **three risk cards directly under the price**.
- **[BUCK](https://buck.co)** — CSS is `#ffffff` ×197, `#000000` ×146, colour ×45. Monochrome frame; **colour arrives from the work**.
- **[Pear](https://pear.no)** — leads with a business model, chapter navigation, CTA is "Apply". Every divider is ink at 14% alpha, never a grey hex.
- **[Anti](https://anti.as)** — hero CTA is **`Watch full showreel`**, not "Contact us".
- **[HEY](https://hey.com)** — microcopy welded to the button: *"No obligation, no CC required."* And `Pricing` is a top-level nav item.

### 3.2 Skeleton

| # | Section | Job | Evidence |
|---|---|---|---|
| — | **Nav** | `Priser` included; phone number visible | Price ranked **#1 of 28** information types, 29% above the next (NNG, 79 participants, 179 B2B sites) |
| 01 | **Hero** | Still poster + click-to-play reel. Front-loaded headline, 5th–7th grade reading level. Something visible below the fold line | 57% of viewing time above the fold, 81% in the first three screenfuls (NNG, 130k fixations). 6 of 8 users didn't realise a hero-video page scrolled |
| 02 | **Client row** | Borrowed trust — but weighted low | Client logos score **+0.67**, awards **+0.31**, vs phone number **+1.56** and physical address **+1.67** (Stanford, n=1,481, 57% Nordic) |
| 03 | **The turn** | His real story, ~40 words, with a turn in it | Concrete language beats abstract for perceived truth (Hansen & Wänke 2010). Two-sided messages raise source credibility (Eisend meta-analysis) |
| 04 | **Arbetet** | 3 cases. Client (h2) / project (h3) / capability chips. Dual `Spela` + `Case` affordance | Gentleman Scholar + Aggressive. Attributed numbers only — see §3.4 |
| 05 | **Tjänster** | Four rows, max three abreast | Paragraph readership falls **81 → 71 → 63 → 32%** (NNG, 1.5M fixations) |
| 06 | **Invändningar** | Objections answered in the customer's voice | Jeton: *"Contactless payments? Sure. Spending limits? Check."* |
| **07** | **Kapacitetsmatris** | 25–30 named deliverables in a grid | Bakken & Bæck. **Makes 499 kr/mån look like a lot rather than a little** |
| 08 | **Hemsida 499** | Monthly + **first-year total**. Three risk cards. `Ingen bindningstid` under the button | Partitioned pricing works without hiding the total (Abraham & Hamilton, N=12,878) |
| 09 | **Process** | Four steps, removes risk | |
| 10 | **Kontakt** | Sentence, phone, address, hours, **named person**. No form-first | Business buyers prefer phoning a person; contact forms draw suspicion (NNG, 20 business professionals) |

Mobile-first, not responsive-after: **mobile is 81% of professional-services traffic and converts ~40% worse** (Unbounce, 41k pages).

### 3.3 What the research killed

Worth recording so we don't reintroduce it:

- **"Attention ratio 1:1"** — Unbounce glossary, no data, no citation.
- **"Multiple offers reduce conversion 266%"** — untraceable, and arithmetically impossible.
- **"First-person button copy +90%"** — single site, three weeks, sample size never disclosed; a sibling test from the same source found the opposite by 24.91%.
- **"Red button +21%"** — a contrast test wearing a colour costume.
- **"Three pricing tiers is optimal"** — no published test, anywhere.
- **"Video lifts conversion 80%"** — traces to a video-advertising vendor with no methodology.
- **"Respond in 5 minutes, 21× more likely to qualify"** — funded by a company selling speed-to-lead software, n = 6 companies.
- **"53% abandon after 3 seconds"** — real source says *visits*, not users; never replicated; a decade old.

Baseline for scepticism: A/A tests with daily peeking "win" **41% of the time** (Goodson/Qubit). Detecting a 5% lift at 80% power needs ~6,000 conversions per arm.

### 3.4 The numbers, rewritten

Three independent lines of evidence say the same thing.

**Legal** — undocumented claims are misleading by default (MD 2012:2).
**Psychological** — excessive precision **backfires with experts** (Loschelder, 5 experiments, n=1,320) and does nothing for sceptics (Xie & Kronrod). A direct replication in a **Danish sample of 1,505** found no precision effect at all (Olsen 2018).
**Cultural** — Sweden's Hofstede uncertainty-avoidance score is **29**, the lowest in the comparison set and below the USA's 46; masculinity is **5**. Badge walls and "353% ROI" read as a warning sign here, not reassurance.

| ❌ Now | ✅ Instead |
|---|---|
| "353% genomsnittlig ROI" | *"Hantverkskollen: organisk trafik +512% mellan mars 2024 och mars 2025, uppmätt i Google Search Console."* |
| "340% ökad försäljning" | *"Deras förfrågningar gick från två i veckan till nio."* |
| "18M+ omsättning genererad" | Drop unless every krona is documented |

Same information. Legal, more credible, and it survives an expert reader.

**Reviews are the strongest lever available** — Spiegel/Northwestern: purchase likelihood **+270% at five reviews**, and **+380% for high-priced items**. But ratings **peak at 4.0–4.7 and decline toward 5.0**; in no category was 5.0 optimal. Target 4.2–4.7 and get to five fast.

**Photograph the work and the process, not the testifier.** Faces in testimonials had no effect on trust and *reduced* participants' ability to tell good vendors from bad (Riegelsberger, CHI '03, n=115, incentivised).

---

## 4. Video

He asked for a video hero. The evidence says autoplay background video is the wrong form of that instinct:

- **Obama 2008, n = 310,382**, 24 variants: **all six video variants lost to all three image variants.** The winner was a still photo. Three orders of magnitude larger than any CRO case study.
- A looping hero >5s with no pause control is a **WCAG 2.2.2 failure at Level A** — not AAA. The **European Accessibility Act** has been enforceable since **28 June 2025** and reaches private Swedish commercial sites via EN 301 549.
- **Stripe, Vercel, Linear, Attio and Clerk ship zero `<video>` elements.**

**Proposal: a still poster with a click-to-play showreel.** For a video agency the reel is the product, not the wallpaper. Anti does exactly this with `Watch full showreel` as the primary CTA.

### Technical budget

- **Poster is the LCP element**, not the video. `<picture>` AVIF → WebP, **15–35 KB** at 1×, `fetchpriority="high"`.
- **≤1.5 MB desktop / ≤600 KB mobile**, 5–7 seconds, 1,200–1,800 kbps.
- **H.264 is mandatory** — Apple has no AV1 software decoder; M1/M2 and iPhone 14 cannot decode it. AV1 is only ~1% smaller on filmed footage anyway.

```bash
ffmpeg -i in.mov -an \
  -c:v libx264 -preset slow -crf 24 \
  -profile:v high -level:v 4.0 -pix_fmt yuv420p \
  -g 999 -keyint_min 999 -sc_threshold 0 \
  -movflags +faststart hero-1080.mp4
```

- `-an` — Resend ships a muted video where **48.4% of the bytes are an unused audio track**.
- `+faststart` — **6 of 9 production files audited got this wrong**, costing two extra round trips before decode.
- `preload="none"` plus a preloaded poster. `autoplay` fetches anyway.
- iOS: `muted` must be in the markup. Low Power Mode and thermal throttling both block autoplay and neither is detectable — catch `NotAllowedError` and leave the poster up.

---

## 5. Design system

### 5.1 Tokens — light base, his hue

Computed from his own `--brand-navy` (hue 215°) and logo ink `#001529`. Contrast measured against `--paper`.

```css
--paper:   #FCFCFD;   /* page ground */
--surface: #F6F7F9;   /* raised sections */
--sunken:  #EFF1F3;   /* wells, quiet blocks */

--ink:   #001529;  /* 17.98:1  headings — his logo ink        */
--ink-2: #1F3451;  /* 12.28:1  body copy                      */
--ink-3: #546783;  /*  5.62:1  captions, labels               */
--ink-4: #8391A5;  /*  3.12:1  DECORATIVE ONLY — never body   */

/* hairlines are ink at alpha, never a separate grey */
--rule-8:  color-mix(in srgb, var(--ink)  8%, transparent);
--rule-12: color-mix(in srgb, var(--ink) 12%, transparent);
--rule-18: color-mix(in srgb, var(--ink) 18%, transparent);
```

**No pure `#000` or `#FFF` anywhere.** No top-tier site ships them — Linear uses `#08090a`, Vercel's maximum foreground is `#ffffffeb`.

**The logo's light blue `#78CCFE` scores 1.73:1 on paper — it fails on light and is dark-background-only.** So on a light page with navy ink, **action is signalled by form, not colour**: filled button, hairline, motion. Adding a signal colour here would reintroduce the template look.

### 5.2 Motion — measured from production CSS

| Use | Duration |
|---|---|
| Hover / colour feedback | **80–150 ms** |
| Enter / reveal | **200–300 ms** |
| Exit | **~⅔ of enter** (150–200 ms) |
| Anything over 600 ms | reads sluggish |

```css
--ease-out-quart: cubic-bezier(.25, 1, .5, 1);   /* default for reveals */
--ease-signature: cubic-bezier(.32, .72, 0, 1);  /* Linear, Vercel and Resend, independently */
```

- **Reveal translate: 4–24 px.** Not 40–60 px. This is where cheap gives itself away.
- **Hover scale 0.97–1.01.** Press states `translateY(±1px)`.
- **Stagger 50–75 ms.**
- **No overshoot.** Bounce easing on interface elements reads as dated.
- Animate `transform` and `opacity` only. Gate hover behind `@media (hover: hover)`.

Scroll reveals have **no supporting evidence and mild negative qualitative evidence** — NNG explicitly recommends against them on B2B. If used: fire once, downward only, 100–400 ms.

### 5.3 Type

**Tracking scales negatively with size** — three tiers: `-0.02em` body, `-0.04em` mid, `-0.06em` display. Micro/uppercase labels take **positive** tracking, `+0.04` to `+0.1em`.

Line height: 1.5–1.6 body, 1.2–1.3 subheads, **0.9–1.0 at display sizes**. Measure capped at 40–42ch.

Ship `text-wrap: balance` on headings and `text-wrap: pretty` on prose.

**A typo costs −1.26 in credibility — about the same as a company having legal or financial trouble (−1.08).** Proofreading is a conversion activity.

### 5.4 The tells to stay clear of

Purple→blue gradients · coloured glows on dark · a thick coloured strip on one side of a card · hairline *and* diffuse shadow on the same element · uniform 16px radius everywhere · identical icon+heading+text cards in a 3-up grid · rounded-square icon containers · everything centred and symmetric on an unbroken 8px grid · ungraded stock photography · continuous auto-scroll marquees · 40–60px fly-up reveals · em-dash-heavy copy · *streamline, empower, supercharge*.

Real craft breaks its own grid where the eye demands it — measured paddings in production include 7px, 11px, 15px, 17px, 26px.

> **The expensive-looking decisions are almost all subtractive.**

### 5.5 Accessibility floor

WCAG 2.1 AA is now the **legal** floor via the EAA. 2.2 AA is the craft floor.

- `prefers-reduced-motion`: **gate motion in, don't strip it out.** Never `* { animation: none !important }` — `transitionend` stops firing and modals hang open forever.
- Focus: use **`outline`, not `box-shadow`** — box-shadow is dropped entirely in Windows High Contrast mode.
- On a light base we avoid the APCA trap that catches "elegant greys" on dark backgrounds. `--ink-4` is still decorative-only.
- Tap targets ≥24px (SC 2.5.8). Skip link. `scroll-padding-top` for sticky headers.

---

## 6. Stack and editing — the open question

He currently edits in Lovable. Whatever we build has to replace that.

| Option | Trade |
|---|---|
| **Supabase + a small admin page** | Scandic already has Supabase provisioned, and this pattern already exists in Perfume-Website (`/admin`, typed data, dashboard). He logs in and edits cases, prices, copy. Most work up front; best outcome; nothing new to learn. |
| **Git-based CMS** (Keystatic / Decap) | Free admin UI, content as files. Less to build; needs a GitHub account; clunkier. |
| **Typed data files only** | Cheapest — but then *you* are his CMS forever, and every price change is a message to you. For an unpaid favour, that's the trap. |

Recommendation: the first. Rendering must be server-side or static either way — that alone fixes audit items 2, 3, 5 and 6 by construction.

---

## 7. Market position

### 7.1 The openings

- **`videoproduktion Helsingborg` is close to unguarded.** The top organic result is based in **Halmstad**, with no testimonials, no review counts, no client logos.
- **`webbyrå Helsingborg`** — the entire organic top 5 are agencies *not based in Helsingborg*; one is in Trosa, 500 km away. "Physical address in the city of search" is a **top-5 local-pack factor**, and none of them qualify.
- **`företagsfotograf Helsingborg`** is a softer flank than `fotograf Helsingborg`, where an exact-match domain owns organic.
- **Avoid `marknadsföringsbyrå Helsingborg`** as a primary target — vaguest term, lowest intent, entrenched incumbents.

### 7.2 Pricing reality

499 kr/mån sits in **the most crowded price point in the market**. Range 299–2,995; dense cluster at 429–999. Minis is 299 with no start fee. **He cannot win on price.**

But there is a real gap. Almost no competitor answers *"what happens if I stop paying?"* on the sales page. Dig into their terms and it's harsh — one provider whose homepage says "Ingen bindningstid · Avsluta när du vill" states in its villkor:

> *"Kunden erhåller inte källkod, designfiler eller teknisk dokumentation. Domäner som registrerats och betalats av [oss] kvarstår hos [oss]."*

And **companies have no ångerrätt in Sweden** — distansavtalslagen is consumer-only, and Riksdagen explicitly declined to extend it to småföretagare in 2018. Svensk Handel's Varningslistan grew **+125% in 2025**.

**So: grant contractually what the law refuses.** Domain in the customer's name from day one. Content exportable. No bindningstid, or a short one in plain type. A voluntary cooling-off window — which no competitor can match, because the law gives it to nobody.

That's a trust position, not a price position, and it's his to take.

---

## 8. What's needed from him

Blocking real work, and none of it is code:

1. **His own footage and photography.** Stock in a video agency's hero is where trust quietly leaks.
2. **Logo as vector** (SVG), not the 70 KB PNG.
3. **Written permission** to name clients — Excite, Hantverkskollen, Prima El, Saunavant, Solna, Walleye are the real ones found in his asset paths. (Foodtel appears in his copy. Everything else in the current mockups is placeholder and must go.)
4. **Documentation for every number**, or they get rewritten per §3.4.
5. **His real deliverables** — 25–30 concrete lines for the capabilities matrix.
6. **His actual story** for section 03.
7. Whether we get the **existing source**, or start clean.

---

## 9. Sequence

1. **Legal fixes** (§0) — today, independent of everything else.
2. **Identity exploration** — the logo's *cut/slot* motif as a design language, explored as fragments (a hero, a case tile, a price block), not full pages.
3. **Agree direction**, then structure and routes.
4. **Stack + editing decision** (§6).
5. **Build**, server-rendered.
6. **Local SEO**: GBP with a visible Helsingborg address, deliberate primary category, review engine at 3–5 text reviews/month.

Currently at step 2.

---

## Appendix — research provenance

Four parallel tracks, all with primary sources:

- **Landing-page conversion evidence** — graded `[SOLID]` / `[THIN]` / `[FOLKLORE]` / `[ABSENT]`; most industry canon did not survive.
- **Teardowns of 14 live sites** — section orders extracted from served markup, palettes from their own CSS.
- **Nordic B2B, Swedish law, and the local market** — statutes quoted verbatim, case law cited, 14 competing subscription providers priced.
- **Craft vs template** — ~4.6 MB of production CSS from Linear, Stripe, Vercel, Resend, Attio and Clerk; 12 hero videos `ffprobe`'d.
