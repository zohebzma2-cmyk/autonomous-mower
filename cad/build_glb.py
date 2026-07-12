#!/usr/bin/env python3
"""Build the site's multi-material assembly.glb from the colour-group STLs.

Pipeline:  openscad -D SHOW='"body"|"black"|"retro"|"accent"|"blade"' -o assembly_<g>.stl assembly.scad
           python3 build_glb.py <stl_dir> <out.glb>

- The model is centred on the FIXED prototype-v1 full-assembly centroid so the
  <model-viewer> hotspot positions on zohebalvi.com stay aligned across CAD
  revisions — do NOT recompute the centroid from the mesh.
- The single origin-centred blade mesh is instanced as THREE nodes at the real
  spindle positions, and a looping "blade-spin" glTF animation (rotation about
  each node's vertical axis) is injected — the site plays it on hover.
Needs: pip install trimesh numpy fast-simplification pygltflib
"""
import sys
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial
import pygltflib

CENTROID = np.array([180.7, 9.7, 320.1])   # mm, FIXED (prototype-v1 datum)

GROUPS = {
    #  name     baseColorRGBA               metallic rough  max_faces (web budget)
    "body":   ([0.72, 0.11, 0.10, 1.0],      0.15,   0.34,  180_000),  # glossy Gravely-red paint
    "black":  ([0.055, 0.055, 0.06, 1.0],    0.00,   0.88,  260_000),  # matte rubber / vinyl
    "retro":  ([0.35, 0.37, 0.40, 1.0],      0.75,   0.35,   80_000),  # brushed-metal retrofit
    "accent": ([0.93, 0.76, 0.13, 1.0],      0.10,   0.55,   30_000),  # yellow service touch-points
}
BLADE_MAT = ([0.72, 0.73, 0.76, 1.0], 0.90, 0.40)   # bare steel
# blade_pos() from mower.scad: [M_DECK_X, i*M_DECK_W*0.3, 112] for i in -1/0/1 (mm)
BLADE_POS_MM = [np.array([620.0, i * 1321 * 0.3, 112.0]) for i in (-1, 0, 1)]
SPIN_PERIOD = 0.6                                    # seconds per revolution

ROT = trimesh.transformations.rotation_matrix(-np.pi / 2, [1, 0, 0])  # Z-up -> Y-up

def pbr(rgba, metallic, rough, name):
    return trimesh.visual.TextureVisuals(material=PBRMaterial(
        baseColorFactor=rgba, metallicFactor=metallic, roughnessFactor=rough, name=name))

def world_to_glb(p_mm):
    """OpenSCAD world mm -> GLB metres (fixed-centroid + Z-up->Y-up)."""
    q = p_mm - CENTROID
    return np.array([q[0], q[2], -q[1]]) / 1000.0

def inject_spin(path, node_names):
    """Bake a looping rotation-about-local-Y animation onto the named nodes."""
    glb = pygltflib.GLTF2().load(path)
    idx = [i for i, n in enumerate(glb.nodes) if n.name in node_names]
    assert len(idx) == len(node_names), f"blade nodes not found: {[n.name for n in glb.nodes]}"
    times = np.array([0, 0.25, 0.5, 0.75, 1.0], dtype=np.float32) * SPIN_PERIOD
    quats = np.array([[0, np.sin(a / 2), 0, np.cos(a / 2)] for a in
                      np.radians([0, 90, 180, 270, 360])], dtype=np.float32)
    blob = glb.binary_blob()
    pad = (-len(blob)) % 4
    blob += b"\x00" * pad
    off_t = len(blob); data = times.tobytes()
    off_q = off_t + len(data); data += quats.tobytes()
    glb.bufferViews.append(pygltflib.BufferView(buffer=0, byteOffset=off_t, byteLength=times.nbytes))
    glb.bufferViews.append(pygltflib.BufferView(buffer=0, byteOffset=off_q, byteLength=quats.nbytes))
    bv_t, bv_q = len(glb.bufferViews) - 2, len(glb.bufferViews) - 1
    glb.accessors.append(pygltflib.Accessor(bufferView=bv_t, componentType=pygltflib.FLOAT,
        count=len(times), type=pygltflib.SCALAR, min=[float(times.min())], max=[float(times.max())]))
    glb.accessors.append(pygltflib.Accessor(bufferView=bv_q, componentType=pygltflib.FLOAT,
        count=len(quats), type=pygltflib.VEC4))
    acc_t, acc_q = len(glb.accessors) - 2, len(glb.accessors) - 1
    sampler = pygltflib.AnimationSampler(input=acc_t, output=acc_q, interpolation="LINEAR")
    anim = pygltflib.Animation(name="blade-spin", samplers=[sampler],
        channels=[pygltflib.AnimationChannel(sampler=0,
                  target=pygltflib.AnimationChannelTarget(node=i, path="rotation")) for i in idx])
    glb.animations.append(anim)
    glb.set_binary_blob(bytes(blob) + data)
    glb.buffers[0].byteLength = len(blob) + len(data)
    glb.save(path)

def main(stl_dir, out_path):
    scene = trimesh.Scene()
    for name, (rgba, metallic, rough, max_faces) in GROUPS.items():
        mesh = trimesh.load(f"{stl_dir}/assembly_{name}.stl")
        if len(mesh.faces) > max_faces:                # decimate for the web
            n0 = len(mesh.faces)
            mesh = mesh.simplify_quadric_decimation(face_count=max_faces)
            print(f"{name}: decimated {n0} -> {len(mesh.faces)} faces")
        mesh.apply_translation(-CENTROID)
        mesh.apply_transform(ROT)                      # Z-up (OpenSCAD) -> Y-up (glTF)
        mesh.apply_scale(0.001)                        # mm -> m
        mesh.visual = pbr(rgba, metallic, rough, f"mower_{name}")
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    # one blade mesh (already origin-centred in the CAD), three animatable nodes
    blade = trimesh.load(f"{stl_dir}/assembly_blade.stl")
    blade.apply_transform(ROT)
    blade.apply_scale(0.001)
    blade.visual = pbr(*BLADE_MAT, "mower_blade")
    names = []
    for k, pos in enumerate(BLADE_POS_MM):
        T = np.eye(4); T[:3, 3] = world_to_glb(pos)
        names.append(f"blade_{k}")
        scene.add_geometry(blade, node_name=names[-1], geom_name="blade", transform=T)
    scene.export(out_path)
    inject_spin(out_path, set(names))
    ext = scene.extents
    print(f"wrote {out_path}  extents {ext[0]:.2f} x {ext[1]:.2f} x {ext[2]:.2f} m  (+blade-spin anim)")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "stl",
         sys.argv[2] if len(sys.argv) > 2 else "assembly.glb")
