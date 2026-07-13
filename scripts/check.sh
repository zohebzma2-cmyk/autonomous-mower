#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# Local CI — the same gates the hosted workflow would run (GitHub Actions is
# unavailable on this account per the zero-budget policy; run this before push).
#   ./scripts/check.sh
set -euo pipefail
cd "$(dirname "$0")/.."

echo "== software test suite"
python3 software/tests/test_backend.py

echo "== every model file parses + evaluates"
cd cad
for f in mower.scad assembly.scad enclosure.scad actuator_brackets.scad \
         gps_mast.scad lidar_mount.scad camera_mount.scad controls_bracket.scad badge.scad \
         attachments_brackets.scad; do
  echo "   $f"
  openscad -o /tmp/check.csg "$f" 2>/dev/null
done

echo "== envelope self-check vs the published spec"
openscad -o /tmp/check.csg assembly.scad 2>&1 | grep "ENVELOPE" | tee /tmp/env.txt
grep -q "L=1968" /tmp/env.txt && grep -q "W=1610" /tmp/env.txt && grep -q "H=1039" /tmp/env.txt
echo "ALL CHECKS PASSED"
