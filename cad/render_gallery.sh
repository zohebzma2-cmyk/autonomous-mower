#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Regenerate the whole-machine gallery renders (cad/renders/assembly_*.png +
# mower_mock.png) from the current CAD. Preview-mode export keeps the per-part
# colour() groups (Gravely-red body, black wheels/seat, graphite retrofit).
# Component/part renders are produced by export_stl.sh; brims by bake_brims.sh.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p renders

SIZE=1500,1050
SCHEME=Tomorrow

render() { # name  rotx,roty,rotz  file
    local name="$1" rot="$2" file="$3"
    echo "render ${name}"
    openscad -o "renders/${name}.png" --imgsize=$SIZE --colorscheme=$SCHEME \
        --camera=0,0,0,${rot},0 --viewall --autocenter "$file" >/dev/null 2>&1
}

render assembly_iso   55,0,25   assembly.scad
render assembly_front 90,0,90   assembly.scad
render assembly_side  90,0,0    assembly.scad
render assembly_rear  90,0,270  assembly.scad
render assembly_top   0,0,0     assembly.scad
render mower_mock     55,0,205  mower.scad
# dual-antenna RTK upgrade (crossbar + two antennas on the mast)
echo "render assembly_dual_rtk"
openscad -o renders/assembly_dual_rtk.png --imgsize=$SIZE --colorscheme=$SCHEME \
    --camera=0,0,0,70,0,300,0 --viewall --autocenter -D 'DUAL_ANTENNA=true' assembly.scad >/dev/null 2>&1
# close-ups of the Weekend-4 hardware
echo "render closeup_sonar_baseline"
openscad -o renders/closeup_sonar_baseline.png --imgsize=$SIZE --colorscheme=$SCHEME \
    --camera=-14,-280,1300,70,0,330,1300 -D 'DUAL_ANTENNA=true' assembly.scad >/dev/null 2>&1
echo "render closeup_display"
openscad -o renders/closeup_display.png --imgsize=$SIZE --colorscheme=$SCHEME \
    --camera=230,0,760,60,0,70,1700 assembly.scad >/dev/null 2>&1
echo "render sensor_mounts_layout"
openscad -o renders/sensor_mounts.png --imgsize=$SIZE --colorscheme=$SCHEME \
    --camera=0,0,0,55,0,25,0 --viewall --autocenter sensor_mounts.scad >/dev/null 2>&1

echo "done → cad/renders/"
