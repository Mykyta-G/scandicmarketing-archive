# Where we left off

**2026-08-16.** Everything committed and pushed to `main`.

```bash
npm run dev                      # site → localhost:4321, journey at /resa/

# Matterhorn — ~70s at 1600px on Cycles/Metal
/Applications/Blender.app/Contents/MacOS/Blender -b --python blender/mountain.py -- \
  --dem "$PWD/blender/matterhorn_dem.npz" --demres 1600 --erode 0 \
  --res 1600 --samples 64 --engine CYCLES --lens 56 --orbit 60 --radius 26 --camz 5.6 \
  --snowline 0.58 --slope 0.36 --pblend 0.6 --rocksat 0.9 --rockval 0.6 \
  --aim 1.0 --aimz 0.68 --cdens 1.05 --cz 1.4 --az 208 --el 9 --amb 0.6 \
  --out //render/MATTERHORN
```

---

## The concept, as he framed it

Two separate pieces, in sequence:

1. **The mountain.** You see it, fly past and rotate into it. Pre-rendered frame sequence — maximum quality, zero runtime cost.
2. **The map.** You arrive and it's live 3D, descending into Helsingborg. MapLibre.

Neither should do the other's job. The frame-sequence-over-video insight came from the Higgsfield skill and is correct: video scrubbing is janky on scroll, frame sequences are smooth. It's what Apple does. ~240 frames at 25–30 fps for 8–10 s. At ~20 s/frame that's roughly 80 minutes of rendering — entirely doable.

---

## 🔴 Open decisions

1. **Finish the Matterhorn, test Higgsfield, or fix the map source?** All three are ready to start.
2. **Camera angle** — 60° is the iconic Matterhorn silhouette. Confirmed by orbit render.

---

## The mountain — where it actually stands

**Matterhorn from swissALTI3D lidar.** `blender/matterhorn_dem.npz` — 2000×2000 over 4 km, 2 m per sample, 2192 m relief, 6.5 MB. The shape is genuine: it *is* the Matterhorn, not an interpretation.

Four research tracks converged on this. Of six candidate peaks it's the only one clearing all four bars:

| | Matterhorn | The other five |
|---|---|---|
| Sub-metre elevation | **0.5 m lidar** | 8–30 m |
| Sub-metre imagery | **25 cm** | 0.4–1.2 m |
| No registration | **none anywhere** | account required |
| Plain-language commercial licence | **yes** | unclear or no |

Artesonraju in Peru is Paramount's actual reference and fails all four.

### Three things left, in order of impact

1. **Slope-masked triplanar blend.** Top-down imagery stretches by `1/cos θ`, so near-vertical faces smear — visible on the shadow side of the current render. This is the gap between the render and a photograph, *not* source resolution. Detail texture where slope is steep, ortho where it's flat.
2. **Aerial perspective.** World-sized cube, Principled Volume, density ~0.0001 on a Z gradient. Ridgelines receding into lighter, lower-contrast haze is the strongest single photographic cue for scale. ~15 minutes of nodes.
3. **Subsurface scattering in the snow.** A slope-threshold blend without SSS reads as white plastic — which is exactly what earlier renders looked like.

### Use the 2024 vintage

swissALTI3D **2019 is 57.5% void** (stereo-derived). **2024 is lidar, 100% valid, 4× rougher.** Filter the STAC by `&datetime=2024-01-01T00:00:00Z/2024-12-31T00:00:00Z`.

- DEM: `https://data.geo.admin.ch/api/stac/v0.9/collections/ch.swisstopo.swissalti3d/items?bbox=<W,S,E,N>`
- Imagery: SWISSIMAGE 2023, 25 cm native over the Alps. Native LV95 WMTS matrix set `2056_28`.
- Attribution: `©swisstopo`. Free commercial use, no registration.

---

## The site

Hero + client marquee live. Seven components built and disconnected at his request, ready to reconnect one at a time: `Stats`, `Work`, `Services`, `Pricing`, `Process`, `Contact`, `Footer`, `SectionHead`, `Mountain`.

Against the live site: HTML 19.9 KB empty shell → **7.4 KB with content**, JS 673 KB → **1 KB**, CSS 82 KB → 13 KB.

### The journey page — `/resa/`

MapLibre GL flying from Stetind down to Helsingborg. Real terrain, real imagery, one camera.

Performance was designed in: the library is dynamically imported and only when the section is near, the map is destroyed once it's well past, rendering pauses off-screen, tile sources are capped below max zoom, no labels or vector layers or 3D buildings, pixel ratio halved. **Homepage ships zero maplibre; `/resa` loads 3.6 KB eagerly and the 957 KB chunk only on approach.**

⚠️ **Blocking for production:** Esri's terms say their tiles are "not intended to be used to export tiles for offline". Needs a different imagery source — Sentinel-2 is open EU data and commercially clean.

---

## Higgsfield — connected and idle

CLI 1.1.23, authenticated, workspace *Private* selected, **free plan with 10 credits**. Eight skills installed under `.agents/skills/` (gitignored, reinstall with `npx skills add higgsfield-ai/skills`).

Commands: `generate`, `preset`, `model`, `workflow`, `soul-id`, `marketing-studio`, `product-photoshoot`, `website`.

Not yet used. **Check cost per generation before spending** — 10 credits is not much. Plan: one image first, not video. If the form and light are right, animating is cheap; if not, one credit is lost.

⚠️ Their terms page 404'd. Verify commercial-use terms before anything ships.

---

## Licence traps found (don't re-litigate)

- **Pexels forbids using their material as part of a trademark, design mark or business name.** A full-bleed hero photo is fine; the mountain *becoming the identity* is not.
- **Esri World Imagery** — not for offline tile export. Affects `/resa`.
- **Norway's 10 cm orthophoto** — needs written permission from Kartverket plus Geovekst partners and municipalities.
- **A whole family of Sketchfab "mountain" models is licence-laundered** — one account has ~70 named peaks marked CC-BY that are QGIS exports draping Esri imagery. The uploader can't relicense that.
- **Depth Anything V2 Base and Large are CC-BY-NC.** Only Small is Apache-2.0. Every tutorial uses the non-commercial ones.
- **Megascans' free era ended** with the move to Fab.
- **No CC0 mountains exist on Sketchfab.** Verified by filtered sweep.

---

## Findings worth keeping

**A scroll push-in as CSS `scale()` is exact, not an approximation.** Scaling a photograph is a crop of the same projection — precisely what a longer lens would have captured. Zero parallax error. And a peak at 20 km under a 100 m dolly changes its internal shape by **0.51 px**. The mountain is flat, to the pixel. So the whole 2.5D depth-map route buys ~25 px of cloud slide for a multi-gigabyte toolchain — skip it.

**The exact Paramount composition does not exist as a free photograph.** ~500 candidates searched, 60 inspected visually. You get any two of *lone pyramid*, *cloud sea*, *warm low sun*. That's why the Paramount logo is an illustration.

**Procedural materials contain no photographic information.** Real snow micro-structure and rock staining are *measured*, not generated. More samples will never close that gap — real imagery will.

### Blender traps already paid for

- `prefs.refresh_devices()` is mandatory — `prefs.devices` is empty until called, so the GPU enable loop silently no-ops and Cycles falls back to CPU. Measured 2.7×. Use `d.use = (d.type == 'METAL')`, not `True`.
- A world volume scatter **blacks the entire frame** in EEVEE. Object volumes are fine.
- Object texture coordinates gave no variation across a large slab; world position does.
- A cloud slab reading as a solid plane is **density saturating**, not missing noise.
- `sky_type='NISHITA'` no longer exists in 5.2; `dust_density` is now `aerosol_density`.
- `subdivision_type` must be `SIMPLE` — Catmull-Clark smooths away the heightfield and is slower (328 s vs 185 s).
- Blender parses `--cy` as its own flag even after `--`. Camera args are `--camx/--camy/--camz`.
- A stray `inspect.py` in a working directory shadows the stdlib and breaks numpy imports.

---

## Blocked on the client

1. **The personnummer must come off the live site** — [PLAN.md §0.1](./PLAN.md). Published as an "Organisationsnummer".
2. **Is the price 499/1499 or 1299/2999?** His own code says both.
3. **CrossFit's logo** isn't in the bundle.
4. Documentation for every performance number, or they get rewritten as attributed results.
5. Written permission to name clients.
6. His real deliverables list, and his actual story for the narrative section.

---

## Attribution owed at launch

- **swissALTI3D / SWISSIMAGE** — ©swisstopo
- **ArcticDEM** — CC BY 4.0, Polar Geospatial Center, University of Minnesota
- **ambientCG** textures — CC0
- Hero film — Pexels, to be replaced with his own footage

---

## Decisions locked

Light base · brand hue 215° · ink `#001529` · accent `#E2622A` for actions only · Montserrat · no icon library, inline SVG only · Astro static · Swedish at `/`, English later at `/en/` · frame sequence over video for scroll

## Housekeeping

A research agent installed five Blender extensions unasked — `Bagapie`, `scatter_objects`, `srtm_terrain_importer`, `terrainmixer`, `BlenderGIS`. Harmless, but not requested. Remove if you want a clean Blender.
