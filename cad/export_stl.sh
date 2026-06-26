#!/usr/bin/env bash
# Export every PRINT_* module across all component .scad files to STL,
# render a PNG of each, and check each part fits the 150mm bed.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p stl renders
BED=145.0

# component files (NOT mower.scad / assembly.scad / params / utils)
FILES=(enclosure.scad actuator_brackets.scad gps_mast.scad lidar_mount.scad camera_mount.scad controls_bracket.scad badge.scad)

echo "part,stl,bbox_x,bbox_y,bbox_z,fits_${BED%.*}" > stl/MANIFEST.csv

for f in "${FILES[@]}"; do
  [ -f "$f" ] || { echo "skip (missing): $f"; continue; }
  # extract PRINT_ module names
  mods=$(grep -oE 'module[[:space:]]+PRINT_[A-Za-z0-9_]+' "$f" | awk '{print $2}' | sort -u)
  for m in $mods; do
    tmp="./.exp_mod_$$.scad"  # PID-unique, in cad/ so relative include <> resolves
    echo "PREVIEW_OFF=1;" > "$tmp"          # suppress each file's standalone preview
    echo "include <${f}>" >> "$tmp"
    echo "${m}();" >> "$tmp"
    out="stl/${m}.stl"
    openscad -o "$out" "$tmp" >/dev/null 2>&1 || { echo "FAIL export $m"; continue; }
    openscad -o "renders/${m}.png" --imgsize=600,480 --colorscheme=Tomorrow "$tmp" >/dev/null 2>&1 || true
    # bounding box from STL (ascii or binary -> use openscad --info fallback: parse STL via python)
    read -r bx by bz < <(python3 - "$out" <<'PY'
import struct,sys
p=sys.argv[1]
def bbox_bin(fn):
    with open(fn,'rb') as f:
        f.read(80); n=struct.unpack('<I',f.read(4))[0]
        mn=[1e9]*3; mx=[-1e9]*3
        for _ in range(n):
            f.read(12)
            for _v in range(3):
                x,y,z=struct.unpack('<3f',f.read(12))
                for i,c in enumerate((x,y,z)):
                    mn[i]=min(mn[i],c); mx[i]=max(mx[i],c)
            f.read(2)
        return [mx[i]-mn[i] for i in range(3)]
def bbox_ascii(fn):
    mn=[1e9]*3; mx=[-1e9]*3; any=False
    for line in open(fn,'r',errors='ignore'):
        s=line.split()
        if len(s)>=4 and s[0]=='vertex':
            any=True
            for i in range(3):
                c=float(s[1+i]); mn[i]=min(mn[i],c); mx[i]=max(mx[i],c)
    return [mx[i]-mn[i] for i in range(3)] if any else [0,0,0]
with open(p,'rb') as f: head=f.read(5)
b = bbox_ascii(p) if head[:5]==b'solid' and b'facet' in open(p,'rb').read(2000) else bbox_bin(p)
print(f"{b[0]:.1f} {b[1]:.1f} {b[2]:.1f}")
PY
)
    fits=$(python3 -c "print('YES' if max($bx,$by,$bz)<=$BED else 'NO-SPLIT')")
    echo "${m},${out},${bx},${by},${bz},${fits}" >> stl/MANIFEST.csv
    printf "  %-28s %6s x %6s x %6s  %s\n" "$m" "$bx" "$by" "$bz" "$fits"
  done
  rm -f "$tmp"
done
echo "---- MANIFEST ----"
column -t -s, stl/MANIFEST.csv
