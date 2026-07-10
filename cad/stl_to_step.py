#!/usr/bin/env python3
"""Convert the 3D (CNC) part STLs -> solid STEP for machining quotes.
STEP from a mesh is FACETED (curves become polygons) — a valid machinable solid
that instant CNC quoters accept, but a clean parametric re-model is better for
production. Flat parts use DXF instead (see export_dxf.sh). Deps: cadquery (py3.10-3.12).
  python stl_to_step.py   ->   cad/step/<part>.step"""
import os, sys, cadquery as cq
from OCP.RWStl import RWStl
from OCP.BRepBuilderAPI import BRepBuilderAPI_Sewing, BRepBuilderAPI_MakeFace, BRepBuilderAPI_MakePolygon, BRepBuilderAPI_MakeSolid
from OCP.TopoDS import TopoDS
HERE=os.path.dirname(os.path.abspath(__file__)); os.chdir(HERE); os.makedirs("step",exist_ok=True)
CNC="""PRINT_box_foot PRINT_equipment_plate PRINT_rail_anchor_bottom PRINT_rail_anchor_top
PRINT_gps_clamp_a PRINT_gps_clamp_b PRINT_lidar_base_a PRINT_lidar_base_b PRINT_lidar_mast_lower
PRINT_lidar_mast_upper PRINT_camera_base PRINT_camera_cradle PRINT_estop_pedestal_a
PRINT_estop_pedestal_b PRINT_relay_box PRINT_throttle_servo_bracket""".split()
def convert(part):
    tri=RWStl.ReadFile_s(f"stl/{part}.stl"); nb=tri.NbTriangles()
    sew=BRepBuilderAPI_Sewing(1e-3)
    for i in range(1,nb+1):
        n1,n2,n3=tri.Triangle(i).Get()
        w=BRepBuilderAPI_MakePolygon(tri.Node(n1),tri.Node(n2),tri.Node(n3),True).Wire()
        sew.Add(BRepBuilderAPI_MakeFace(w).Face())
    sew.Perform()
    solid=BRepBuilderAPI_MakeSolid(TopoDS.Shell_s(sew.SewedShape())).Solid()
    cq.exporters.export(cq.Workplane("XY").add(cq.Solid(solid)), f"step/{part}.step")
    return nb
for p in CNC:
    if not os.path.exists(f"stl/{p}.stl"): print("skip",p); continue
    try: n=convert(p); print(f"  step/{p}.step ({n} tris, {os.path.getsize(f'step/{p}.step')//1024} KB)")
    except Exception as e: print(f"  FAIL {p}: {e}")
