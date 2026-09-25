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
  if ! git diff --quiet -- cad/renders; then
    echo "STALE RENDERS: cad/renders changed after re-render — commit the fresh ones"; exit 1
  fi
  cd cad
fi
# MowerCarrier PCB gates (#39): active as soon as a KiCad project lands in hardware/pcb/kicad
if ls ../hardware/pcb/kicad/*.kicad_sch >/dev/null 2>&1 && command -v kicad-cli >/dev/null; then
  echo "== KiCad ERC + DRC (MowerCarrier)"
  for f in ../hardware/pcb/kicad/*.kicad_sch; do kicad-cli sch erc --exit-code-violations -o /tmp/erc.rpt "$f"; done
  for f in ../hardware/pcb/kicad/*.kicad_pcb; do kicad-cli pcb drc --exit-code-violations -o /tmp/drc.rpt "$f"; done
fi
if [ -x ../.venv/bin/mkdocs ]; then
  echo "== docs site builds clean (mkdocs --strict)"
  (cd .. && NO_MKDOCS_2_WARNING=1 .venv/bin/mkdocs build --strict -q -d "$(mktemp -d)")
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
