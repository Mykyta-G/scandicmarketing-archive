"""
A sharp, dramatic peak — generated, not scanned.

Terrain comes from spectral synthesis: a random field filtered by 1/f^beta,
inverse-FFT'd into fractal noise, then ridged (1 - |n|) so the flanks form
knife edges instead of rolling dunes. A radial cone mask isolates one summit
and pushes the surrounding massif down, which is what makes it read as a lone
pyramid rather than a mountain range.

Run headless:
    blender -b --python blender/mountain.py -- --res 960 --samples 24 --out render/peak
"""

import bpy
import sys
import math
import numpy as np
from mathutils import Vector

# ---------------------------------------------------------------- args
argv = sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else []


def arg(name, default):
    return argv[argv.index(name) + 1] if name in argv else default


RES = int(arg('--res', 960))
SAMPLES = int(arg('--samples', 24))
OUT = arg('--out', '//render/peak')
SEED = int(arg('--seed', 7))
ENGINE = arg('--engine', 'EEVEE')
EROSION = int(arg('--erode', 1))
DEM = arg('--dem', '')            # path to a real heightfield; empty = procedural
DEMRES = int(arg('--demres', 0))  # downsample the DEM for faster iteration

N = 512          # heightfield resolution
SIZE = 20.0      # world units across
PEAK_H = 7.4     # summit height in world units

# ---------------------------------------------------------------- clean slate
bpy.ops.wm.read_factory_settings(use_empty=True)
rng = np.random.default_rng(SEED)


# ---------------------------------------------------------------- terrain
def fractal(n, beta=2.25):
    """Spectral synthesis: white noise shaped by a 1/f^beta falloff."""
    fx = np.fft.fftfreq(n)[:, None]
    fy = np.fft.fftfreq(n)[None, :]
    f = np.sqrt(fx ** 2 + fy ** 2)
    f[0, 0] = 1.0
    spec = np.fft.fft2(rng.normal(size=(n, n))) / (f ** beta)
    spec[0, 0] = 0
    out = np.real(np.fft.ifft2(spec))
    return out / (np.abs(out).max() + 1e-9)


def ridged(n, octaves=8):
    """Layered ridge noise — the (1 - |n|) fold is what creates sharp crests."""
    total = np.zeros((n, n))
    amp, w = 1.0, 0.0
    for o in range(octaves):
        layer = fractal(n, beta=2.0 + o * 0.06)
        layer = 1.0 - np.abs(layer)
        total += (layer ** 3) * amp
        w += amp
        amp *= 0.58
    return total / w


USE_DEM = bool(DEM)

if USE_DEM:
    """
    Real elevation instead of noise.

    Procedural terrain is self-similar by construction: the same statistics
    at every scale. Real mountains are not — they carry drainage networks,
    glacial cirques, ridgeline continuity and bedding planes that noise has
    no way to invent. Starting from a scan fixes all of it at once, and the
    erosion and shading stack still runs on top.

    Source: ArcticDEM v4.1 mosaic, 2 m posting, PGC/University of Minnesota,
    tile 29_62_2_1. Stetind, Norway — 68.16153 N, 16.59967 E.
    """
    d = np.load(DEM)
    q = d['h'].astype(np.float32)
    lo_m, hi_m, span_m, _n = [float(v) for v in d['meta']]
    h = lo_m + (q / 65535.0) * (hi_m - lo_m)          # back to metres

    if DEMRES and DEMRES < h.shape[0]:
        step_ds = h.shape[0] // DEMRES
        h = h[::step_ds, ::step_ds][:DEMRES, :DEMRES]

    N = h.shape[0]
    # Keep true proportions: the box is SIZE units wide and represents
    # span_m metres, so vertical scale follows from the same ratio.
    M_PER_UNIT = span_m / SIZE
    # Vertical exaggeration. Standard practice in terrain visualisation:
    # real mountains are wider than they are tall, and a true-scale render
    # of a broad massif reads as a hill. 1.3-1.6 stays believable.
    VEX = float(arg('--vex', 1.0))
    h = (h - h.min()) / M_PER_UNIT * VEX
    PEAK_H = float(h.max())
    RELIEF_M = hi_m - lo_m
    print('DEM %dx%d  %.0f-%.0f m  %.0f m across  -> peak %.2f units'
          % (N, N, lo_m, hi_m, span_m, PEAK_H))
    ys, xs = np.mgrid[0:N, 0:N]
else:
    ys, xs = np.mgrid[0:N, 0:N]

if not USE_DEM:
    u = (xs / (N - 1) - 0.5) * 2.0
    v = (ys / (N - 1) - 0.5) * 2.0

    r = np.sqrt(u ** 2 + v ** 2)

# The main cone. The exponent is the single most important number here:
# below ~1.2 it reads as a hill, above ~1.7 it turns into a spike.
    cone = np.clip(1.0 - r / 0.86, 0.0, 1.0) ** 1.62

# Two lower shoulders so the summit has something to rise out of.
    def bump(cx, cy, rad, power):
        d = np.sqrt((u - cx) ** 2 + (v - cy) ** 2)
        return np.clip(1.0 - d / rad, 0.0, 1.0) ** power


    shoulders = 0.30 * bump(-0.52, 0.30, 0.62, 1.7) + 0.24 * bump(0.55, -0.22, 0.58, 1.8)

    ridge = ridged(N)
    ridge = (ridge - ridge.min()) / (ridge.max() - ridge.min())

# Ridges scale with the cone so the crests converge on the summit and the
# skirt stays calm — detail where the eye goes, quiet everywhere else.
    h = cone * (0.30 + 1.05 * ridge) + shoulders * (0.35 + 0.65 * ridge) * 0.48

# A little large-scale warp so the silhouette is not symmetrical.
    h *= 0.86 + 0.28 * (fractal(N, beta=3.0) * 0.5 + 0.5)

    h = np.clip(h, 0.0, None)
    h /= h.max()
    h = h ** 1.18
    h *= PEAK_H

# ---------------------------------------------------------------- mesh
step = SIZE / (N - 1)
vx = (xs * step - SIZE / 2).ravel()
vy = (ys * step - SIZE / 2).ravel()
verts = np.stack([vx, vy, h.ravel()], axis=1).tolist()

idx = np.arange(N * N).reshape(N, N)
a = idx[:-1, :-1].ravel()
b = idx[:-1, 1:].ravel()
c = idx[1:, 1:].ravel()
d = idx[1:, :-1].ravel()
faces = np.stack([a, b, c, d], axis=1).tolist()

mesh = bpy.data.meshes.new('Peak')
mesh.from_pydata(verts, [], faces)
mesh.update()
mesh.shade_smooth()

peak = bpy.data.objects.new('Peak', mesh)
bpy.context.collection.objects.link(peak)

# ---------------------------------------------------------------- erosion
# Procedural noise has no history. Real mountains are cut by water and
# frost, which is what produces drainage networks, talus fans at the base
# and slopes bounded by the angle of repose. Without it the silhouette can
# be perfect and the eye still reads "generated".
#
# A.N.T. Landscape ships a hydraulic + thermal eroder that operates on any
# grid mesh, so it runs directly on the one built above.
if EROSION > 0:
    import addon_utils
    addon_utils.enable('bl_ext.blender_org.antlandscape', default_set=True)
    bpy.context.view_layer.objects.active = peak
    peak.select_set(True)
    bpy.ops.mesh.eroder(
        Iterations=EROSION,
        IterRiver=30,      # hydraulic passes — carves the gullies
        IterAva=6,         # avalanche/thermal — enforces the angle of repose
        IterDiffuse=4,
        Kt=math.radians(58),   # talus angle
        Kr=0.012,              # rainfall
        Ks=0.55,               # scour
        Kdep=0.12,             # deposition
        Kz=0.32,
        Kc=0.92,               # carrying capacity
        Kev=0.5,
        numexpr=False,         # measured slower when present, and unneeded
        smooth=True,
    )
    # The eroder hands back the masks we would otherwise fake with noise.
    print('EROSION groups:', [g.name for g in peak.vertex_groups])
    h = np.array([v.co.z for v in peak.data.vertices]).reshape(N, N)

summit_i = int(np.argmax(h))
summit = Vector((peak.data.vertices[summit_i].co.x, peak.data.vertices[summit_i].co.y, peak.data.vertices[summit_i].co.z))
print(f'SUMMIT at {summit.x:.2f}, {summit.y:.2f}, {summit.z:.2f}')

# ---------------------------------------------------------------- material
"""
The flat matte surface was the single biggest reason the render read as
animated rather than photographed. Rock has structure at three scales at
once — strata and fracture, weathering, grain — and a single base colour
has none of them.

So: real scanned CC0 PBR from ambientCG, box-projected because the mesh has
no UVs, layered at two scales so the macro pattern does not visibly tile,
and mixed by the erosion masks rather than by slope alone. Snow that sits
where water actually collected reads as snow; snow on a slope threshold
reads as a mask.
"""
import os

TEXDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'textures')


def load_img(path, non_color=False):
    img = bpy.data.images.load(path, check_existing=True)
    if non_color:
        img.colorspace_settings.name = 'Non-Color'
    return img


def tex_node(nt, path, coord, scale, non_color=False, label=''):
    """Box-projected image sampler at a given world scale."""
    mapn = nt.nodes.new('ShaderNodeMapping')
    mapn.inputs['Scale'].default_value = (scale, scale, scale)
    nt.links.new(coord, mapn.inputs['Vector'])
    t = nt.nodes.new('ShaderNodeTexImage')
    t.image = load_img(path, non_color)
    t.projection = 'BOX'
    t.projection_blend = float(arg('--pblend', 0.55))
    t.extension = 'REPEAT'
    t.label = label
    nt.links.new(mapn.outputs['Vector'], t.inputs['Vector'])
    return t


mat = bpy.data.materials.new('Rock')
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

out = nt.nodes.new('ShaderNodeOutputMaterial')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
geo = nt.nodes.new('ShaderNodeNewGeometry')

# Rock058: measured #4E545A, hue 210 deg, 7% saturation — cold granite.
# Rock030 was warm sandstone; no amount of desaturation fixed it. Fighting
# a wrong texture is slower than picking the right one.
R = os.path.join(TEXDIR, 'Rock058', 'Rock058_2K-JPG_')
S = os.path.join(TEXDIR, 'Snow010A', 'Snow010A_2K-JPG_')

# --- rock at two scales: macro strata plus fine grain ---
rock_a = tex_node(nt, R + 'Color.jpg', geo.outputs['Position'], 0.22, label='rock macro')
rock_b = tex_node(nt, R + 'Color.jpg', geo.outputs['Position'], 1.35, label='rock detail')
rock_mix = nt.nodes.new('ShaderNodeMix')
rock_mix.data_type = 'RGBA'
rock_mix.blend_type = 'OVERLAY'
rock_mix.inputs['Factor'].default_value = 0.45
nt.links.new(rock_a.outputs['Color'], rock_mix.inputs['A'])
nt.links.new(rock_b.outputs['Color'], rock_mix.inputs['B'])

# Cool and darken the scan — quarried rock scans read too warm at altitude.
rock_hsv = nt.nodes.new('ShaderNodeHueSaturation')
rock_hsv.inputs['Saturation'].default_value = float(arg('--rocksat', 0.85))
rock_hsv.inputs['Value'].default_value = float(arg('--rockval', 0.62))
nt.links.new(rock_mix.outputs['Result'], rock_hsv.inputs['Color'])

rock_r = tex_node(nt, R + 'Roughness.jpg', geo.outputs['Position'], 0.22, True, 'rock rough')
rock_n = tex_node(nt, R + 'NormalGL.jpg', geo.outputs['Position'], 0.22, True, 'rock nrm')
rock_nd = tex_node(nt, R + 'NormalGL.jpg', geo.outputs['Position'], 1.35, True, 'rock nrm detail')

# --- snow ---
snow_c = tex_node(nt, S + 'Color.jpg', geo.outputs['Position'], 0.30, label='snow col')
snow_r = tex_node(nt, S + 'Roughness.jpg', geo.outputs['Position'], 0.30, True, 'snow rough')
snow_n = tex_node(nt, S + 'NormalGL.jpg', geo.outputs['Position'], 0.30, True, 'snow nrm')

# --- where snow sits -----------------------------------------------------
sep = nt.nodes.new('ShaderNodeSeparateXYZ')
nt.links.new(geo.outputs['Normal'], sep.inputs['Vector'])
ramp_slope = nt.nodes.new('ShaderNodeValToRGB')
SLOPEGATE = float(arg('--slope', 0.18))
ramp_slope.color_ramp.elements[0].position = SLOPEGATE
ramp_slope.color_ramp.elements[1].position = SLOPEGATE + 0.42
nt.links.new(sep.outputs['Z'], ramp_slope.inputs['Fac'])

sep_p = nt.nodes.new('ShaderNodeSeparateXYZ')
nt.links.new(geo.outputs['Position'], sep_p.inputs['Vector'])
div_h = nt.nodes.new('ShaderNodeMath')
div_h.operation = 'DIVIDE'
div_h.inputs[1].default_value = PEAK_H
nt.links.new(sep_p.outputs['Z'], div_h.inputs[0])
ramp_h = nt.nodes.new('ShaderNodeValToRGB')
SNOWLINE = float(arg('--snowline', 0.24))
ramp_h.color_ramp.elements[0].position = SNOWLINE
ramp_h.color_ramp.elements[1].position = SNOWLINE + 0.22
nt.links.new(div_h.outputs[0], ramp_h.inputs['Fac'])

mul = nt.nodes.new('ShaderNodeMath')
mul.operation = 'MULTIPLY'
nt.links.new(ramp_slope.outputs['Color'], mul.inputs[0])
nt.links.new(ramp_h.outputs['Color'], mul.inputs[1])
snow_mask = mul.outputs[0]

if EROSION > 0:
    # flowrate marks the drainage lines. Snow is scoured out of them, so it
    # is subtracted — that is what puts dark rock in the gullies and leaves
    # white on the ribs between, which is how real peaks read.
    flow = nt.nodes.new('ShaderNodeAttribute')
    flow.attribute_name = 'flowrate'
    flow_rm = nt.nodes.new('ShaderNodeMapRange')
    flow_rm.inputs['From Max'].default_value = 0.08   # raw means are tiny
    flow_rm.inputs['To Max'].default_value = 1.0
    nt.links.new(flow.outputs['Fac'], flow_rm.inputs['Value'])
    scour = nt.nodes.new('ShaderNodeMath')
    scour.operation = 'SUBTRACT'
    scour.use_clamp = True
    nt.links.new(mul.outputs[0], scour.inputs[0])
    nt.links.new(flow_rm.outputs['Result'], scour.inputs[1])
    snow_mask = scour.outputs[0]

snow_ramp = nt.nodes.new('ShaderNodeValToRGB')
snow_ramp.color_ramp.elements[0].position = 0.22
snow_ramp.color_ramp.elements[1].position = 0.78
nt.links.new(snow_mask, snow_ramp.inputs['Fac'])
SNOW = snow_ramp.outputs['Color']

# --- combine -------------------------------------------------------------
mix_col = nt.nodes.new('ShaderNodeMix')
mix_col.data_type = 'RGBA'
nt.links.new(SNOW, mix_col.inputs['Factor'])
nt.links.new(rock_hsv.outputs['Color'], mix_col.inputs['A'])
nt.links.new(snow_c.outputs['Color'], mix_col.inputs['B'])

mix_rough = nt.nodes.new('ShaderNodeMix')
mix_rough.data_type = 'RGBA'
nt.links.new(SNOW, mix_rough.inputs['Factor'])
nt.links.new(rock_r.outputs['Color'], mix_rough.inputs['A'])
nt.links.new(snow_r.outputs['Color'], mix_rough.inputs['B'])

nrm_mix_rock = nt.nodes.new('ShaderNodeMix')
nrm_mix_rock.data_type = 'RGBA'
nrm_mix_rock.inputs['Factor'].default_value = 0.5
nt.links.new(rock_n.outputs['Color'], nrm_mix_rock.inputs['A'])
nt.links.new(rock_nd.outputs['Color'], nrm_mix_rock.inputs['B'])

nrm_mix = nt.nodes.new('ShaderNodeMix')
nrm_mix.data_type = 'RGBA'
nt.links.new(SNOW, nrm_mix.inputs['Factor'])
nt.links.new(nrm_mix_rock.outputs['Result'], nrm_mix.inputs['A'])
nt.links.new(snow_n.outputs['Color'], nrm_mix.inputs['B'])

nmap = nt.nodes.new('ShaderNodeNormalMap')
nmap.inputs['Strength'].default_value = 1.25
nt.links.new(nrm_mix.outputs['Result'], nmap.inputs['Color'])

nt.links.new(mix_col.outputs['Result'], bsdf.inputs['Base Color'])
nt.links.new(mix_rough.outputs['Result'], bsdf.inputs['Roughness'])
nt.links.new(nmap.outputs['Normal'], bsdf.inputs['Normal'])
nt.links.new(bsdf.outputs['BSDF'], out.inputs['Surface'])
peak.data.materials.append(mat)

# ---------------------------------------------------------------- sky + sun
world = bpy.data.worlds.new('World')
bpy.context.scene.world = world
world.use_nodes = True
wnt = world.node_tree
wnt.nodes.clear()
wout = wnt.nodes.new('ShaderNodeOutputWorld')
bg = wnt.nodes.new('ShaderNodeBackground')
sky = wnt.nodes.new('ShaderNodeTexSky')
sky.sky_type = 'MULTIPLE_SCATTERING'
AZ = float(arg('--az', 282.0))
EL = float(arg('--el', 8.0))
sky.sun_elevation = math.radians(EL)      # low sun = long shadows, warm rim
sky.sun_rotation = math.radians(AZ)
sky.altitude = 2200
sky.air_density = 1.5
sky.aerosol_density = 2.4
sky.ozone_density = 1.0
bg.inputs['Strength'].default_value = float(arg('--amb', 0.62))
wnt.links.new(sky.outputs['Color'], bg.inputs['Color'])
wnt.links.new(bg.outputs['Background'], wout.inputs['Surface'])

# NOTE: a world volume scatter blacks the frame out entirely in EEVEE —
# atmospheric perspective comes from the sky model and the mist pass
# instead, not from world volumetrics.

sun_data = bpy.data.lights.new('Sun', type='SUN')
sun_data.energy = 14.0
sun_data.angle = math.radians(1.2)
sun_data.color = (1.0, 0.93, 0.86)   # near-neutral; the sky carries the warmth
sun = bpy.data.objects.new('Sun', sun_data)
bpy.context.collection.objects.link(sun)
sun.rotation_euler = (math.radians(90.0 - EL), 0.0, math.radians(AZ))

# ---------------------------------------------------------------- clouds
# An object volume, not a world volume: EEVEE renders these correctly,
# whereas a world volume blacks the whole frame out.
bpy.ops.mesh.primitive_cube_add(size=1)
cloud = bpy.context.active_object
cloud.name = 'Clouds'
cloud.scale = (150.0, 150.0, 1.6)
cloud.location = (0.0, 0.0, float(arg('--cz', 1.55)))

cmat = bpy.data.materials.new('Cloud')
cmat.use_nodes = True
cnt = cmat.node_tree
cnt.nodes.clear()
cout = cnt.nodes.new('ShaderNodeOutputMaterial')
scat = cnt.nodes.new('ShaderNodeVolumeScatter')
cnoise = cnt.nodes.new('ShaderNodeTexNoise')
cramp = cnt.nodes.new('ShaderNodeValToRGB')
cdens = cnt.nodes.new('ShaderNodeMath')
cmap = cnt.nodes.new('ShaderNodeMapping')
cgeo = cnt.nodes.new('ShaderNodeNewGeometry')

cmap.inputs['Scale'].default_value = (1.0, 1.0, 5.0)
cnt.links.new(cgeo.outputs['Position'], cmap.inputs['Vector'])
cnt.links.new(cmap.outputs['Vector'], cnoise.inputs['Vector'])
cnoise.inputs['Scale'].default_value = 0.22
cnoise.inputs['Detail'].default_value = 12.0
cnoise.inputs['Roughness'].default_value = 0.62

# A hard ramp is what turns fog into cloud: wisps need an edge.
cramp.color_ramp.elements[0].position = 0.42
cramp.color_ramp.elements[1].position = 0.62
cnt.links.new(cnoise.outputs['Fac'], cramp.inputs['Fac'])

cdens.operation = 'MULTIPLY'
cdens.inputs[1].default_value = float(arg('--cdens', 0.9))
cnt.links.new(cramp.outputs['Color'], cdens.inputs[0])
csep = cnt.nodes.new('ShaderNodeSeparateXYZ')
cabs = cnt.nodes.new('ShaderNodeMath')
cfall = cnt.nodes.new('ShaderNodeValToRGB')
cmul2 = cnt.nodes.new('ShaderNodeMath')
cnt.links.new(cgeo.outputs['Position'], csep.inputs['Vector'])
csub_z = cnt.nodes.new('ShaderNodeMath')
csub_z.operation = 'SUBTRACT'
csub_z.inputs[1].default_value = float(arg('--cz', 1.55))
cnt.links.new(csep.outputs['Z'], csub_z.inputs[0])
cabs.operation = 'ABSOLUTE'
cnt.links.new(csub_z.outputs[0], cabs.inputs[0])
cfall.color_ramp.elements[0].position = 0.15
cfall.color_ramp.elements[1].position = 0.70
cfall.color_ramp.elements[0].color = (1, 1, 1, 1)
cfall.color_ramp.elements[1].color = (0, 0, 0, 1)
cnt.links.new(cabs.outputs[0], cfall.inputs['Fac'])
cmul2.operation = 'MULTIPLY'
cnt.links.new(cdens.outputs[0], cmul2.inputs[0])
cnt.links.new(cfall.outputs['Color'], cmul2.inputs[1])
cnt.links.new(cmul2.outputs[0], scat.inputs['Density'])
scat.inputs['Anisotropy'].default_value = 0.42
scat.inputs['Color'].default_value = (1.0, 0.96, 0.92, 1.0)
cnt.links.new(scat.outputs['Volume'], cout.inputs['Volume'])
cloud.data.materials.append(cmat)

# ---------------------------------------------------------------- camera
cam_data = bpy.data.cameras.new('Cam')
cam_data.lens = float(arg('--lens', 74))
cam = bpy.data.objects.new('Cam', cam_data)
bpy.context.collection.objects.link(cam)
bpy.context.scene.camera = cam

# Below the summit and back, so the peak rises against sky rather than
# being looked down on.
ORBIT = arg('--orbit', '')
if ORBIT != '':
    # Place the camera on a circle around the summit — the fastest way to
    # find a mountain's iconic profile, which is always angle-specific.
    ang = math.radians(float(ORBIT))
    rad = float(arg('--radius', 26.0))
    cam.location = Vector((summit.x + rad * math.sin(ang),
                           summit.y - rad * math.cos(ang),
                           float(arg('--camz', 5.4))))
else:
    cam.location = Vector((float(arg('--camx', 1.6)), float(arg('--camy', -19.5)), float(arg('--camz', 3.1))))
# Aim at the summit itself. The old 0.3 factor pulled the aim back toward
# the origin, which is fine for a cone centred on the box but throws an
# off-centre peak — like the Matterhorn's — out to the frame edge.
AIM = float(arg('--aim', 1.0))
target = Vector((summit.x * AIM, summit.y * AIM, summit.z * float(arg('--aimz', 0.72))))
direction = target - cam.location
cam.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()

# ---------------------------------------------------------------- render
scene = bpy.context.scene
scene.render.resolution_x = RES
scene.render.resolution_y = int(RES * 9 / 16)
scene.render.resolution_percentage = 100
scene.render.image_settings.file_format = 'PNG'
scene.render.filepath = OUT
scene.view_settings.view_transform = 'AgX'
try:
    scene.view_settings.look = 'AgX - Medium High Contrast'
except Exception:
    pass  # looks are not always registered in background mode

if ENGINE.upper() == 'CYCLES':
    scene.render.engine = 'CYCLES'
    scene.cycles.samples = SAMPLES
    scene.cycles.use_denoising = True
    try:
        prefs = bpy.context.preferences.addons['cycles'].preferences
        prefs.compute_device_type = 'METAL'
        # refresh_devices() is mandatory: prefs.devices is empty until it is
        # called, so a loop over it silently does nothing and the render
        # quietly falls back to CPU. Measured 2.7x difference.
        prefs.refresh_devices()
        for d in prefs.devices:
            d.use = (d.type == 'METAL')   # not True — that re-enables the CPU
        scene.cycles.device = 'GPU'
        print('CYCLES DEVICES:', [(d.name, d.type, d.use) for d in prefs.devices])
    except Exception as e:
        print('GPU unavailable, CPU fallback:', e)
else:
    scene.render.engine = 'BLENDER_EEVEE'
    try:
        scene.eevee.taa_render_samples = SAMPLES
        scene.eevee.use_raytracing = True
        scene.eevee.volumetric_tile_size = '2'
        scene.eevee.volumetric_samples = 128
        scene.eevee.volumetric_start = 0.5
        scene.eevee.volumetric_end = 90.0
        scene.eevee.use_volumetric_shadows = True
    except Exception:
        pass

print('RENDERING', RES, 'x', scene.render.resolution_y, 'engine', scene.render.engine)
bpy.ops.render.render(write_still=True)
print('WROTE', scene.render.filepath)
