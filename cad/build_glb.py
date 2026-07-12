#!/usr/bin/env python3
"""Build the site's multi-material assembly.glb from the colour-group STLs.

Pipeline:  openscad -D SHOW='"<group>"' -o assembly_<group>.stl assembly.scad
           python3 build_glb.py <stl_dir> <out.glb>

Groups: body, black, accent (static) + six retro_* subsystem nodes + one
origin-centred blade instanced three times. Two baked animations:
  - "blade-spin": each blade node rotates about its local vertical axis
    (played on hover on the site)
  - "explode":   each retrofit subsystem (and the blades) translates out
    along its install axis over 1s (the site scrubs currentTime as a slider)

The model is centred on the FIXED prototype-v1 full-assembly centroid so the
<model-viewer> hotspot positions on zohebalvi.com stay aligned across CAD
revisions — do NOT recompute the centroid from the mesh.
Needs: pip install trimesh numpy fast-simplification pygltflib
"""
import sys
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
import pygltflib

CENTROID = np.array([180.7, 9.7, 320.1])   # mm, FIXED (prototype-v1 datum)

STATIC_GROUPS = {
    #  name     baseColorRGBA               metallic rough  max_faces (web budget)
    "body":   ([0.72, 0.11, 0.10, 1.0],      0.15,   0.34,  180_000),  # glossy Gravely-red paint
    "black":  ([0.055, 0.055, 0.06, 1.0],    0.00,   0.88,  260_000),  # matte rubber / vinyl
    "accent": ([0.93, 0.76, 0.13, 1.0],      0.10,   0.55,   30_000),  # yellow service touch-points
}
RETRO_MAT = ([0.35, 0.37, 0.40, 1.0], 0.75, 0.35)    # brushed-metal retrofit
BLADE_MAT = ([0.72, 0.73, 0.76, 1.0], 0.90, 0.40)    # bare steel

# Phase-3 attachments: name -> (material, explode offset). Bagger pair shares an
# offset (it explodes as one assembly); sprayer frame/tank separate vertically.
ATTACH_GROUPS = {
    "bagger_frame":  (([0.72, 0.11, 0.10, 1.0], 0.15, 0.34), (-0.40, 0.28, 0.00)),
    "bagger_bins":   (([0.09, 0.09, 0.10, 1.0], 0.05, 0.75), (-0.40, 0.28, 0.00)),
    "boom_asm":      (RETRO_MAT,                              ( 0.28, 0.22, 0.30)),
    "sprayer_frame": (([0.09, 0.09, 0.10, 1.0], 0.05, 0.75), (-0.60, 0.05, 0.00)),
    "sprayer_tank":  (([0.93, 0.76, 0.13, 1.0], 0.10, 0.55), (-0.60, 0.35, 0.00)),
}

# subsystem -> explode offset in GLB metres (X fwd, Y up, Z = world -Y/right)
RETRO_SUBS = {
    "retro_brain":     ( 0.00, 0.55,  0.00),
    "retro_actuators": ( 0.00, 0.30,  0.00),
    "retro_gps":       ( 0.00, 0.45,  0.18),   # up + out over the left side
    "retro_lidar":     ( 0.22, 0.40,  0.00),
    "retro_camera":    ( 0.35, 0.15,  0.00),
    "retro_estop":     ( 0.00, 0.18, -0.35),   # out over the right side
}
BLADE_EXPLODE = (0.0, -0.30, 0.0)                    # blades drop out of the deck
# blade_pos() from mower.scad: [M_DECK_X, i*M_DECK_W*0.3, 112] for i in -1/0/1 (mm)
BLADE_POS_MM = [np.array([620.0, i * 1321 * 0.3, 112.0]) for i in (-1, 0, 1)]
SPIN_PERIOD = 0.6                                    # seconds per revolution
EXPLODE_T = 1.0                                      # explode timeline length (s)

ROT = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])  # Z-up -> Y-up

def pbr(rgba, metallic, rough, name):
    return trimesh.visual.TextureVisuals(material=PBRMaterial(
        baseColorFactor=rgba, metallicFactor=metallic, roughnessFactor=rough, name=name))

def world_to_glb(p_mm):
    """OpenSCAD world mm -> GLB metres (fixed-centroid + Z-up->Y-up)."""
    q = p_mm - CENTROID
    return np.array([q[0], q[2], -q[1]]) / 1000.0

def load_group(stl_dir, name, max_faces=None):
    mesh = trimesh.load(f"{stl_dir}/assembly_{name}.stl")
    if max_faces and len(mesh.faces) > max_faces:
        n0 = len(mesh.faces)
        mesh = mesh.simplify_quadric_decimation(face_count=max_faces)
        print(f"{name}: decimated {n0} -> {len(mesh.faces)} faces")
    mesh.apply_translation(-CENTROID)
    mesh.apply_transform(ROT)
    mesh.apply_scale(0.001)
    return mesh

class AnimBuf:
    """Accumulates keyframe data appended to the GLB binary blob."""
    def __init__(self, glb):
        self.glb = glb
        blob = glb.binary_blob()
        self.blob = bytes(blob) + b"\x00" * ((-len(blob)) % 4)

    def accessor(self, arr, acc_type):
        off = len(self.blob); data = arr.astype(np.float32).tobytes()
        self.blob += data
        self.glb.bufferViews.append(pygltflib.BufferView(buffer=0, byteOffset=off, byteLength=len(data)))
        kw = {}
        if acc_type == pygltflib.SCALAR:
            kw = dict(min=[float(arr.min())], max=[float(arr.max())])
        self.glb.accessors.append(pygltflib.Accessor(bufferView=len(self.glb.bufferViews)-1,
            componentType=pygltflib.FLOAT, count=len(arr), type=acc_type, **kw))
        return len(self.glb.accessors) - 1

    def finish(self):
        self.glb.set_binary_blob(self.blob)
        self.glb.buffers[0].byteLength = len(self.blob)

def inject_animations(path, blade_names, blade_bases):
    glb = pygltflib.GLTF2().load(path)
    node_idx = {n.name: i for i, n in enumerate(glb.nodes)}
    buf = AnimBuf(glb)

    # ---- blade-spin: shared rotation sampler, one channel per blade node ----
    t_spin = buf.accessor(np.linspace(0, SPIN_PERIOD, 5), pygltflib.SCALAR)
    quats = np.array([[0, np.sin(a/2), 0, np.cos(a/2)] for a in np.radians([0, 90, 180, 270, 360])])
    q_spin = buf.accessor(quats, pygltflib.VEC4)
    spin = pygltflib.Animation(name="blade-spin",
        samplers=[pygltflib.AnimationSampler(input=t_spin, output=q_spin, interpolation="LINEAR")],
        channels=[pygltflib.AnimationChannel(sampler=0,
                  target=pygltflib.AnimationChannelTarget(node=node_idx[n], path="rotation"))
                  for n in blade_names])
    glb.animations.append(spin)

    # ---- explode: per-node translation from rest to offset over EXPLODE_T ----
    t_exp = buf.accessor(np.array([0.0, EXPLODE_T]), pygltflib.SCALAR)
    samplers, channels = [], []
    def add(node_name, base, off):
        out = buf.accessor(np.array([base, np.array(base) + np.array(off)]), pygltflib.VEC3)
        samplers.append(pygltflib.AnimationSampler(input=t_exp, output=out, interpolation="LINEAR"))
        channels.append(pygltflib.AnimationChannel(sampler=len(samplers)-1,
            target=pygltflib.AnimationChannelTarget(node=node_idx[node_name], path="translation")))
    for name, off in RETRO_SUBS.items():
        add(name, [0.0, 0.0, 0.0], off)
    for name, (_, off) in ATTACH_GROUPS.items():
        add(name, [0.0, 0.0, 0.0], off)
    for n, base in zip(blade_names, blade_bases):
        add(n, list(base), BLADE_EXPLODE)
    glb.animations.append(pygltflib.Animation(name="explode", samplers=samplers, channels=channels))

    buf.finish()
    glb.save(path)

def main(stl_dir, out_path):
    scene = trimesh.Scene()
    for name, (rgba, metallic, rough, max_faces) in STATIC_GROUPS.items():
        mesh = load_group(stl_dir, name, max_faces)
        mesh.visual = pbr(rgba, metallic, rough, f"mower_{name}")
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    for name in RETRO_SUBS:
        mesh = load_group(stl_dir, name, 40_000)
        mesh.visual = pbr(*RETRO_MAT, "mower_retro")
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    for name, (mat, _) in ATTACH_GROUPS.items():
        mesh = load_group(stl_dir, name, 60_000)
        mesh.visual = pbr(*mat, f"att_{name}")
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    # one blade mesh (already origin-centred in the CAD), three animatable nodes
    blade = trimesh.load(f"{stl_dir}/assembly_blade.stl")
    blade.apply_transform(ROT)
    blade.apply_scale(0.001)
    blade.visual = pbr(*BLADE_MAT, "mower_blade")
    names, bases = [], []
    for k, pos in enumerate(BLADE_POS_MM):
        T = np.eye(4); T[:3, 3] = world_to_glb(pos)
        names.append(f"blade_{k}"); bases.append(world_to_glb(pos))
        scene.add_geometry(blade, node_name=names[-1], geom_name="blade", transform=T)
    scene.export(out_path)
    inject_animations(out_path, names, bases)
    ext = scene.extents
    print(f"wrote {out_path}  extents {ext[0]:.2f} x {ext[1]:.2f} x {ext[2]:.2f} m  (+blade-spin, +explode)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "stl",
         sys.argv[2] if len(sys.argv) > 2 else "assembly.glb")
