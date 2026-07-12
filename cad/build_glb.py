#!/usr/bin/env python3
"""Build the site's multi-material assembly.glb from the 3 colour-group STLs.

Pipeline:  openscad -D SHOW='"body"|"black"|"retro"' -o assembly_<g>.stl assembly.scad
           python3 build_glb.py <stl_dir> <out.glb>

The model is centred on the FIXED prototype-v1 full-assembly centroid so the
<model-viewer> hotspot positions on zohebalvi.com stay aligned across CAD
revisions — do NOT recompute the centroid from the mesh.
Needs: pip install trimesh numpy
"""
import sys
import numpy as np
import trimesh
from trimesh.visual.material import PBRMaterial

CENTROID = np.array([180.7, 9.7, 320.1])   # mm, FIXED (prototype-v1 datum)

GROUPS = {
    #  name    baseColorRGBA               metallic rough
    "body":  ([0.72, 0.11, 0.10, 1.0],      0.15,   0.34),  # glossy Gravely-red paint
    "black": ([0.055, 0.055, 0.06, 1.0],    0.00,   0.88),  # matte rubber / vinyl
    "retro": ([0.35, 0.37, 0.40, 1.0],      0.75,   0.35),  # brushed-metal retrofit
}

def main(stl_dir, out_path):
    rot = trimesh.transformations.rotation_matrix(-np.pi/2, [1, 0, 0])
    scene = trimesh.Scene()
    for name, (rgba, metallic, rough) in GROUPS.items():
        mesh = trimesh.load(f"{stl_dir}/assembly_{name}.stl")
        mesh.apply_translation(-CENTROID)
        mesh.apply_transform(rot)                 # Z-up (OpenSCAD) -> Y-up (glTF)
        mesh.apply_scale(0.001)                   # mm -> m
        mesh.visual = trimesh.visual.TextureVisuals(material=PBRMaterial(
            baseColorFactor=rgba, metallicFactor=metallic, roughnessFactor=rough,
            name=f"mower_{name}"))
        scene.add_geometry(mesh, node_name=name, geom_name=name)
    scene.export(out_path)
    ext = scene.extents
    print(f"wrote {out_path}  extents {ext[0]:.2f} x {ext[1]:.2f} x {ext[2]:.2f} m")

if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "stl",
         sys.argv[2] if len(sys.argv) > 2 else "assembly.glb")
