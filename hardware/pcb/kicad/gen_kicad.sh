#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Run gen_kicad.py under KiCad's bundled Python (pcbnew). Stage: all | sch | place
set -euo pipefail
cd "$(dirname "$0")"
KAPP="${KICAD_APP:-$HOME/Applications/KiCad/KiCad.app}"
export KICAD9_SYMBOL_DIR="$KAPP/Contents/SharedSupport/symbols"
export KICAD9_FOOTPRINT_DIR="$KAPP/Contents/SharedSupport/footprints"
PY=$(ls -d "$KAPP"/Contents/Frameworks/Python.framework/Versions/3.*/bin/python3 | head -1)
exec "$PY" gen_kicad.py "${1:-all}"
