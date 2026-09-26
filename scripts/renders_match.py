#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Exit 1 if any re-rendered image in cad/renders visibly differs from the committed one.

OpenSCAD's rasterizer isn't bit-stable (coplanar faces anti-alias differently run to run),
so a byte diff flags noise. A render counts as changed when > 0.1 % of its pixels differ by
more than 40/255 in any channel — far below any real geometry/colour change, far above noise.
Without Pillow it falls back to the byte diff. Usage: renders_match.py [dir]  (default cad/renders)
"""
import io
import subprocess
import sys

d = sys.argv[1] if len(sys.argv) > 1 else "cad/renders"
changed = subprocess.run(["git", "diff", "--name-only", "--", d], capture_output=True, text=True).stdout.split()
new = subprocess.run(["git", "ls-files", "--others", "--exclude-standard", "--", d],
                     capture_output=True, text=True).stdout.split()
try:
    from PIL import Image, ImageChops
except ImportError:
    bad = changed + new
else:
    bad = list(new)
    for f in changed:
        if not f.endswith(".png"):
            bad.append(f)
            continue
        old = Image.open(io.BytesIO(subprocess.run(["git", "show", "HEAD:" + f], capture_output=True).stdout)).convert("RGB")
        cur = Image.open(f).convert("RGB")
        if old.size != cur.size:
            bad.append(f)
            continue
        diff = ImageChops.difference(old, cur).convert("L").point(lambda v: 255 if v > 40 else 0)
        if diff.histogram()[255] > 0.001 * cur.size[0] * cur.size[1]:
            bad.append(f)
        else:
            subprocess.run(["git", "checkout", "--", f])      # noise only: keep the committed file
for f in bad:
    print("  stale:", f)
sys.exit(1 if bad else 0)
