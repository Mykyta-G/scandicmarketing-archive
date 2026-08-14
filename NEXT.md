# Where we left off

**2026-08-14.** Everything committed and pushed to `main`. Dev server stopped.

```bash
npm run dev        # site → http://localhost:4321

# mountain — renders in ~12s at 1280px, ~15min at 4K
/Applications/Blender.app/Contents/MacOS/Blender -b --python blender/mountain.py -- \
  --dem "$PWD/blender/stetind_dem.npz" --demres 800 --erode 0 \
  --res 1280 --samples 48 --engine CYCLES \
  --lens 50 --orbit 90 --radius 30 --camz 7.5 --snowline 0.55 \
  --cdens 0.9 --cz 1.6 --az 264 --el 6 --amb 0.55 --out //render/hero
```

---

## 🔴 One decision waiting

**Which camera angle for Stetind.** Eight are rendered in `~/Downloads/scandic-berg/STETIND-vinklar.png`.

- **90°** — recommended. Clean triangular silhouette, dark shadow side, cloud sea. Closest to the Paramount reference.
- **135°** — jagged twin peaks, more aggressive.
- 45° works too. 270°/315° read too broad — the peak stops looking alone.

Once picked: tune the snow line to Nordic proportions, add haze between peak and clouds, swap the procedural sky for a Poly Haven HDRI, then render 4K.

---

## The site

Live at hero + client marquee only. Everything else was built and then pulled back out at your request — the components still exist in `src/components/` but are disconnected from `src/pages/index.astro`.

Parked and ready to reconnect one at a time: `Stats`, `Work`, `Services`, `Pricing`, `Process`, `Contact`, `Footer`, `SectionHead`, `Mountain`.

Measured against the live site: HTML 19.9 KB empty shell → **7.4 KB with content**, JS 673 KB → **1 KB**, CSS 82 KB → 13 KB.

---

## The mountain — how it works now

**Real elevation, not noise.** ArcticDEM v4.1 at 2 m posting (PGC/University of Minnesota, tile `29_62_2_1`), windowed over Stetind's summit at **68.16153 N, 16.59967 E**. 1600×1600 samples across 3.2 km, 74–1345 m, quantised to uint16 → 4.4 MB in `blender/stetind_dem.npz`.

Procedural generation still works — omit `--dem` and it falls back to spectral synthesis with a cone mask.

**Material** is scanned CC0 PBR from ambientCG, box-projected (the mesh has no UVs), layered at two scales so the macro pattern doesn't tile visibly.

**Erosion** via `bpy.ops.mesh.eroder` (ships with A.N.T. Landscape, free, already installed) returns ten vertex groups — `flowrate`, `scour`, `deposit`, `scree` — which drive the snow instead of a slope threshold. Not needed on the real DEM, which already carries its own erosion; use `--erode 0`.

### Things that cost me time, so they don't cost it again

- **`prefs.refresh_devices()` is mandatory** — `prefs.devices` is empty until it's called, so the GPU enable loop silently no-ops and Cycles falls back to CPU. Measured 2.7×. Also `d.use = (d.type == 'METAL')`, not `True`, or the CPU comes along too.
- **A world volume scatter blacks the entire frame** in EEVEE. Object volumes are fine.
- **Object texture coordinates gave no variation** across the cloud slab; world position does.
- The cloud slab looked like a solid plane because the density was **saturating**, not because the noise was missing.
- **`sky_type='NISHITA'` no longer exists** in Blender 5.2, and `dust_density` is now `aerosol_density`. Every tutorial online crashes on this.
- **`subdivision_type` must be `SIMPLE`** if adaptive subdivision is added later — Catmull-Clark smooths away the heightfield and is slower (328 s vs 185 s).
- Blender parses `--cy` as its own flag even after `--`. Camera args are `--camx/--camy/--camz`.

### The sampling rule that changed the approach

> Samples across the mountain must meet or exceed pixels across it.

The old 512 grid over a 4 km peak was 7.8 m per sample, so by Nyquist it **could not represent anything below ~16 m** — incapable of carrying the metre-scale relief that reads as rock, no matter how it was shaded. 2 m posting fixes it.

### Nordic scale signal, still unapplied

Tree line at 68° N is around **500 m**; in the Alps it's 2,200 m. Stetind is 1345 m, so the rock/snow proportion should look nothing like an Alpine peak of the same height. Cheapest available signal that it *is* Nordic. Currently `--snowline 0.55` is a guess.

---

## Two assets he downloaded, worth using next time

Both are in `~/Downloads/`, and `Mount hood` is extracted to `blender/assets/`.

**`Mount+hood.zip`** — FBX terrain, 97k verts over 8 km, so 25 m per sample: ten times coarser than the ArcticDEM Stetind data. But it ships a **real orthophoto** (2816x2560) with genuine glacial ice, crevasses and snow. That texture is the photographic information procedural material cannot invent. Rendered fine; see `render/hood.png`.

**`Procedural+Mountains+and+Clouds.blend`** — the more useful of the two, but not as a mountain. It solves clouds properly: seven separate volumetric shapes driven by node groups `CloudBase`, `DistortCenteredNoise`, `TriLerp`, `RelativeToBounds`, `OffsetNoise`. Node groups are appendable, so they can be lifted into our scene without rebuilding them. Terrain there is displacement-driven with adaptive subdivision rather than a fixed grid.

⚠️ **It is very expensive to render.** One frame at 1280px/40 samples had not finished after 6.5 minutes on the M4 GPU. Its own 250-frame animation would be 20+ hours. Render it small (480px, 8 samples) just to study the clouds.

### The synthesis these point at

Stetind's real 2 m geometry (already fetched) + **real satellite imagery draped on it** (ESRI World Imagery tiles are already verified accessible — see the earlier Kebnekaise test) + **these cloud node groups**. That combination gives photographic surface, real high-resolution form, and believable clouds — rather than inventing all three procedurally.

---

## Tooling verdicts (researched, don't re-litigate)

- **Gaea cannot run on this Mac** — Windows only, and QuadSpinner has said no Mac version is planned. Same for World Creator and Instant Terra. Terragen is Rosetta-only.
- **Houdini** is the only paid tool that's Apple Silicon native and genuinely headless — $299/yr Indie.
- **Blender MCP would be a downgrade.** It needs the GUI running plus a socket, and its main capability is running Python inside Blender — which `blender -b --python` already does, with version-controlled files and a render-and-inspect loop.
- **Poly Haven and ambientCG are CC0**, fetchable with plain curl, fine for commercial client work. Megascans needs an Epic session per asset and has no API — skip it.

---

## Blocked on the client

1. **The personnummer must come off the live site** — see [PLAN.md §0.1](./PLAN.md). It's published as an "Organisationsnummer".
2. **Is the price 499/1499 or 1299/2999?** His own code says both.
3. **CrossFit's logo** isn't in the bundle.
4. **Documentation for every performance number**, or they get rewritten as attributed results.
5. Written permission to name clients.
6. His real deliverables list, and his actual story for the narrative section.

---

## Attribution owed at launch

- **ArcticDEM** — CC BY 4.0, Polar Geospatial Center, University of Minnesota
- **ambientCG** textures — CC0, no attribution required but courteous
- Hero film — Pexels, to be replaced with his own footage before launch

---

## Decisions locked

Light base · brand hue 215° · ink `#001529` · accent `#E2622A` for actions only · Montserrat · no icon library, inline SVG only · Astro static · Swedish at `/`, English later at `/en/`

## Housekeeping

A research agent installed five Blender extensions unasked — `Bagapie`, `scatter_objects`, `srtm_terrain_importer`, `terrainmixer`, `BlenderGIS`. Harmless and terrain-related, but not requested. Remove if you want a clean Blender.
