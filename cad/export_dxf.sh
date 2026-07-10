#!/usr/bin/env bash
# Export flat/sheet-metal parts as DXF outlines for laser-cut quoting (SendCutSend, OSH Cut...).
# 3D parts need STEP instead (re-model in FreeCAD/CadQuery) — see docs/SOURCING-AND-FABRICATION.md.
set -u
DIR="$(cd "$(dirname "$0")" && pwd)"; cd "$DIR"; mkdir -p dxf
FLAT="PRINT_estop_face PRINT_relay_lid PRINT_badge PRINT_upper_shelf PRINT_lapbar_yoke_top PRINT_lapbar_yoke_bottom PRINT_lidar_top_plate PRINT_gps_top_plate"
for p in $FLAT; do
  [ -f "stl/$p.stl" ] || { echo "skip $p (no STL)"; continue; }
  echo "projection(cut=false) import(\"$DIR/stl/$p.stl\");" > "/tmp/_pj_$p.scad"
  openscad -o "dxf/$p.dxf" "/tmp/_pj_$p.scad" >/dev/null 2>&1 \
    && echo "  dxf/$p.dxf ($(du -h dxf/$p.dxf|cut -f1))" || echo "  FAILED: $p"
done
