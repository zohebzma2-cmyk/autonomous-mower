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

echo "done → cad/renders/"
