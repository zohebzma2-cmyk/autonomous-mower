#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Local CI — the same gates the hosted workflow would run (GitHub Actions is
# unavailable on this account per the zero-budget policy; run this before push).
#   ./scripts/check.sh            # tests, mypy, CAD asserts, envelope, docs, (KiCad when present)
#   ./scripts/check.sh --full     # + re-render the gallery and fail if it drifted from the CAD
#   ./scripts/check.sh --sitl     # + ArduPilot SITL end-to-end (needs a SITL build, see SITL.md)
set -euo pipefail
cd "$(dirname "$0")/.."
FULL=0; SITL=0
for a in "$@"; do case "$a" in --full) FULL=1;; --sitl) SITL=1;; *) echo "unknown flag $a"; exit 2;; esac; done

# .venv from scripts/setup-dev.sh when present, else the system python3 (stdlib is enough)
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python

echo "== software test suite ($($PY --version))"
$PY software/tests/test_backend.py

if $PY -m mypy --version >/dev/null 2>&1; then
  echo "== mypy (typed policy modules, mypy.ini)"
  $PY -m mypy
fi

echo "== every model file parses + evaluates"
cd cad
for f in mower.scad assembly.scad enclosure.scad actuator_brackets.scad \
         gps_mast.scad lidar_mount.scad camera_mount.scad controls_bracket.scad badge.scad \
         attachments_brackets.scad sensor_mounts.scad; do
  echo "   $f"
  # openscad exits 0 on a failed assert() — fail on any ERROR line instead
  if openscad -o /tmp/check.csg "$f" 2>&1 | grep -E "^(ERROR|WARNING: Assertion)"; then
    echo "FAIL: $f"; exit 1
  fi
done

echo "== envelope self-check vs the published spec"
openscad -o /tmp/check.csg assembly.scad 2>&1 | grep "ENVELOPE" | tee /tmp/env.txt
grep -q "L=1968" /tmp/env.txt && grep -q "W=1610" /tmp/env.txt && grep -q "H=1039" /tmp/env.txt
if [ "$FULL" = 1 ]; then
  echo "== renders fresh vs CAD (--full)"
  ./render_gallery.sh >/dev/null 2>&1
  cd ..
  if ! $PY scripts/renders_match.py cad/renders; then      # perceptual, not byte-exact (see script)
    echo "STALE RENDERS: cad/renders changed after re-render — commit the fresh ones"; exit 1
  fi
  cd cad
fi
# MowerCarrier PCB gates (#39): ERC clean, DRC with zero errors + schematic parity
if ls ../hardware/pcb/kicad/*.kicad_sch >/dev/null 2>&1 && command -v kicad-cli >/dev/null; then
  echo "== KiCad ERC + DRC (MowerCarrier: errors + schematic parity)"
  for f in ../hardware/pcb/kicad/*.kicad_sch; do
    kicad-cli sch erc --severity-all --exit-code-violations -o /tmp/erc.rpt "$f" 2>&1 | grep -E "violation" || true
    kicad-cli sch erc --severity-all --exit-code-violations -o /tmp/erc.rpt "$f" >/dev/null 2>&1 || { cat /tmp/erc.rpt; exit 1; }
  done
  for f in ../hardware/pcb/kicad/*.kicad_pcb; do
    kicad-cli pcb drc --severity-error --schematic-parity --exit-code-violations -o /tmp/drc.rpt "$f" >/dev/null 2>&1 \
      || { cat /tmp/drc.rpt; exit 1; }
    grep -E "^\*\* Found" /tmp/drc.rpt | sed 's/^/   /'
  done
fi
# ESP32 lap-bar firmware compiles (current Arduino-ESP32 core) — when the toolchain is installed
if command -v arduino-cli >/dev/null && arduino-cli core list 2>/dev/null | grep -q "^esp32:esp32"; then
  echo "== firmware: lapbar_controller compiles (esp32:esp32)"
  arduino-cli compile --fqbn esp32:esp32:esp32 --warnings default ../firmware/lapbar_controller 2>&1 \
    | grep -E "error|warning|Sketch uses" | sed 's/^/   /'
  arduino-cli compile --fqbn esp32:esp32:esp32 ../firmware/lapbar_controller >/dev/null 2>&1 || exit 1
fi
if [ -x ../.venv/bin/mkdocs ]; then
  echo "== docs site builds clean (mkdocs --strict)"
  (cd .. && NO_MKDOCS_2_WARNING=1 .venv/bin/mkdocs build --strict -q -d "$(mktemp -d)")
fi
if [ "$FULL" = 1 ] && [ -x ../hardware/pcb/kicad/gen_kicad.sh ] && command -v freerouting >/dev/null; then
  echo "== MowerCarrier regenerates byte-identically from design.py (--full)"
  ../hardware/pcb/kicad/gen_kicad.sh all >/dev/null 2>&1
  if ! git -C .. diff --quiet -- hardware/pcb/kicad/*.kicad_sch hardware/pcb/kicad/*.kicad_pcb; then
    echo "STALE PCB: the committed KiCad files differ from what design.py/gen_pcb.py generate — commit them"; exit 1
  fi
fi
if [ "$SITL" = 1 ]; then
  echo "== ArduPilot SITL end-to-end (scripts/sitl.sh + sitl_smoke.py)"
  cd ..
  PORT=8099 ./scripts/sitl.sh > /tmp/check_sitl.log 2>&1 &
  SITLPID=$!
  until grep -qE "safety switch|PROBLEM|Traceback|no SITL" /tmp/check_sitl.log; do
    kill -0 $SITLPID 2>/dev/null || { cat /tmp/check_sitl.log; exit 1; }; sleep 1; done
  if grep -qE "PROBLEM|Traceback|no SITL" /tmp/check_sitl.log; then cat /tmp/check_sitl.log; kill $SITLPID; exit 1; fi
  $PY scripts/sitl_smoke.py http://localhost:8099 || { kill $SITLPID; exit 1; }
  kill $SITLPID; wait $SITLPID 2>/dev/null || true
  cd cad
fi
echo "ALL CHECKS PASSED"
