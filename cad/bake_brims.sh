#!/usr/bin/env bash
# Bake a bed-adhesion brim into every printable part. For each PRINT_* module:
#   1) read the part's true min-z from its plain STL,
#   2) drop it to z=0 and weld a single-layer brim of a per-part width,
#   3) export to stl/brim/<part>.stl and verify the XY footprint grew (brim present).
set -uo pipefail
cd "$(dirname "$0")"
mkdir -p stl/brim renders/brim
FILES=(enclosure.scad actuator_brackets.scad gps_mast.scad lidar_mount.scad camera_mount.scad controls_bracket.scad badge.scad attachments_brackets.scad)

# per-part brim width (mm). default 5; tall/warp-prone 8; structural 6; thin plates 4.
brim_w(){ case "$1" in
  PRINT_equipment_plate|PRINT_upper_shelf) echo 2;;   # big flat plates: huge bed contact, keep clear of 150mm edge
  PRINT_lidar_mast_lower|PRINT_lidar_mast_upper|PRINT_estop_pedestal_a|PRINT_camera_base) echo 8;;
  PRINT_lapbar_yoke_bottom|PRINT_lapbar_yoke_top|PRINT_rail_anchor_bottom|PRINT_rail_anchor_top|\
  PRINT_gps_clamp_a|PRINT_gps_clamp_b|PRINT_lidar_base_a|PRINT_lidar_base_b) echo 6;;
  PRINT_estop_face|PRINT_relay_lid) echo 4;;
  PRINT_duct_adapter) echo 3;;   # 136mm part: keep brim clear of the 150mm bed edge
  *) echo 5;; esac; }

minz_of(){ python3 - "$1" <<'PY'
import sys
mn=1e9
for line in open(sys.argv[1],errors='ignore'):
    s=line.split()
    if len(s)>=4 and s[0]=='vertex':
        z=float(s[3]); mn=min(mn,z)
print(f"{mn:.3f}")
PY
}
foot_x(){ python3 - "$1" <<'PY'
import sys
mn=1e9;mx=-1e9
for line in open(sys.argv[1],errors='ignore'):
    s=line.split()
    if len(s)>=4 and s[0]=='vertex':
        x=float(s[1]);mn=min(mn,x);mx=max(mx,x)
print(f"{mx-mn:.1f}")
PY
}
facets(){ grep -c "facet normal" "$1" 2>/dev/null || echo 0; }

printf "%-30s %5s %8s %8s %9s  %s\n" part brim plainXY brimXY facets+ OK > stl/brim/REPORT.txt
echo "Baking brims..."
for f in "${FILES[@]}"; do
  mods=$(grep -oE 'module[[:space:]]+PRINT_[A-Za-z0-9_]+' "$f" | awk '{print $2}' | sort -u)
  for m in $mods; do
    plain="stl/${m}.stl"; [ -f "$plain" ] || { echo "  skip $m (no plain STL)"; continue; }
    W=$(brim_w "$m"); MZ=$(minz_of "$plain")
    tmp="./.brim_$$.scad"
    { echo "PREVIEW_OFF=1;"; echo "include <${f}>"; echo "add_brim(w=${W}, minz=${MZ}) ${m}();"; } > "$tmp"
    out="stl/brim/${m}.stl"
    openscad -o "$out" "$tmp" >/dev/null 2>&1 || { echo "  FAIL $m"; rm -f "$tmp"; continue; }
    openscad -o "renders/brim/${m}.png" --imgsize=560,440 --colorscheme=Tomorrow "$tmp" >/dev/null 2>&1 || true
    rm -f "$tmp"
    px=$(foot_x "$plain"); bx=$(foot_x "$out")
    pf=$(facets "$plain"); bf=$(facets "$out")
    df=$((bf-pf))
    ok=$(python3 -c "print('YES' if $df>0 else 'FAIL')")   # brim must add facets
    printf "%-30s %5s %8s %8s %9s  %s\n" "$m" "$W" "$px" "$bx" "$df" "$ok" | tee -a stl/brim/REPORT.txt
  done
done
echo "---- brim report (XY footprint should grow ~2x brim width) ----"
column -t stl/brim/REPORT.txt
