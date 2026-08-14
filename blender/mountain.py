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


ys, xs = np.mgrid[0:N, 0:N]
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

summit_i = int(np.argmax(h))
summit = Vector((verts[summit_i][0], verts[summit_i][1], verts[summit_i][2]))
print(f'SUMMIT at {summit.x:.2f}, {summit.y:.2f}, {summit.z:.2f}')

# ---------------------------------------------------------------- material
mat = bpy.data.materials.new('Rock')
mat.use_nodes = True
nt = mat.node_tree
nt.nodes.clear()

out = nt.nodes.new('ShaderNodeOutputMaterial')
bsdf = nt.nodes.new('ShaderNodeBsdfPrincipled')
geo = nt.nodes.new('ShaderNodeNewGeometry')
sep = nt.nodes.new('ShaderNodeSeparateXYZ')
pos = nt.nodes.new('ShaderNodeNewGeometry')
sep_p = nt.nodes.new('ShaderNodeSeparateXYZ')
noise = nt.nodes.new('ShaderNodeTexNoise')
ramp_slope = nt.nodes.new('ShaderNodeValToRGB')
ramp_h = nt.nodes.new('ShaderNodeValToRGB')
mul = nt.nodes.new('ShaderNodeMath')
mix_col = nt.nodes.new('ShaderNodeMix')
mix_rough = nt.nodes.new('ShaderNodeMix')

# Snow lies where the ground is flat-ish AND high — the product of the two.
nt.links.new(geo.outputs['Normal'], sep.inputs['Vector'])
nt.links.new(sep.outputs['Z'], ramp_slope.inputs['Fac'])
ramp_slope.color_ramp.elements[0].position = 0.50
ramp_slope.color_ramp.elements[1].position = 0.80

nt.links.new(pos.outputs['Position'], sep_p.inputs['Vector'])
nt.links.new(sep_p.outputs['Z'], ramp_h.inputs['Fac'])
ramp_h.color_ramp.elements[0].position = 0.20
ramp_h.color_ramp.elements[1].position = 0.34

mul.operation = 'MULTIPLY'
nt.links.new(ramp_slope.outputs['Color'], mul.inputs[0])
nt.links.new(ramp_h.outputs['Color'], mul.inputs[1])

# Break the snow line with noise so it is not a clean contour.
noise.inputs['Scale'].default_value = 5.2
noise.inputs['Detail'].default_value = 5.0
sub = nt.nodes.new('ShaderNodeMath')
sub.operation = 'SUBTRACT'
nt.links.new(mul.outputs[0], sub.inputs[0])
fac_noise = nt.nodes.new('ShaderNodeMath')
fac_noise.operation = 'MULTIPLY'
fac_noise.inputs[1].default_value = 0.34
nt.links.new(noise.outputs['Fac'], fac_noise.inputs[0])
nt.links.new(fac_noise.outputs[0], sub.inputs[1])

snow_ramp = nt.nodes.new('ShaderNodeValToRGB')
snow_ramp.color_ramp.elements[0].position = 0.34
snow_ramp.color_ramp.elements[1].position = 0.52
nt.links.new(sub.outputs[0], snow_ramp.inputs['Fac'])

mix_col.data_type = 'RGBA'
mix_col.inputs['A'].default_value = (0.020, 0.021, 0.025, 1)   # near-black wet rock
mix_col.inputs['B'].default_value = (0.94, 0.955, 0.98, 1)     # snow
nt.links.new(snow_ramp.outputs['Color'], mix_col.inputs['Factor'])

mix_rough.data_type = 'FLOAT'
mix_rough.inputs[2].default_value = 0.88   # rock
mix_rough.inputs[3].default_value = 0.34   # snow
nt.links.new(snow_ramp.outputs['Color'], mix_rough.inputs['Factor'])

nt.links.new(mix_col.outputs['Result'], bsdf.inputs['Base Color'])
nt.links.new(mix_rough.outputs['Result'], bsdf.inputs['Roughness'])
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
sun_data.color = (1.0, 0.82, 0.60)
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
cam.location = Vector((float(arg('--camx', 1.6)), float(arg('--camy', -19.5)), float(arg('--camz', 3.1))))
target = Vector((summit.x * 0.3, summit.y * 0.3, summit.z * 0.80))
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
        for d in prefs.devices:
            d.use = True
        scene.cycles.device = 'GPU'
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
