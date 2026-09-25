#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Draw the coverage planner on example yards -> docs/coverage-plan.svg.

    python3 scripts/plan_figure.py

Three panels, all from the real planner in software/companion/missions.py:
  1. U-shaped yard, the old row-stitching (legs across the notch, red)
  2. the same yard now: cells, no-rut turns, routed transits, perimeter laps
  3. a square lawn with a flower bed as a keep-out
Stats under each panel come from the plan itself.
"""
import math
import os
import sys
import tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "software", "companion"))
import missions  # noqa: E402

missions.DATA = tempfile.mkdtemp()
missions.FILE = os.path.join(missions.DATA, "missions.json")

M = 111320.0
MLON = M * math.cos(math.radians(42.806))


def ll(x, y):
    return [42.806 + y / M, -71.367 + x / MLON]


U_YARD = [ll(0, 0), ll(40, 0), ll(40, 30), ll(30, 30), ll(30, 10), ll(10, 10), ll(10, 30), ll(0, 30)]
SQUARE = [ll(0, 0), ll(40, 0), ll(40, 40), ll(0, 40)]
BED = [ll(15, 15), ll(25, 15), ll(25, 22), ll(15, 22)]
SPACING = 1.15

W, H, PAD, SCALE = 300, 330, 20, 6.5          # px per panel, px per metre


def local(pts):
    return [((p[1] + 71.367) * MLON, (p[0] - 42.806) * M) for p in pts]


def px(x, y, ox):
    return ox + PAD + x * SCALE, PAD + (40 - y) * SCALE


def path_d(pts, ox, close=False):
    s = " ".join(("M" if i == 0 else "L") + "%.1f %.1f" % px(x, y, ox) for i, (x, y) in enumerate(pts))
    return s + (" Z" if close else "")


def old_stitch(polygon, spacing):
    """What the planner did before cell decomposition: every span of a row, in order."""
    poly, ref = missions._to_xy(polygon)
    ys = [p[1] for p in poly]
    y, out, flip = min(ys) + spacing / 2, [], False
    while y <= max(ys) - spacing / 2:
        row = []
        for xa, xb in missions._row_spans(poly, y):
            row += [(xa, y), (xb, y)]
        out += row[::-1] if flip else row
        flip = not flip
        y += spacing
    return [missions._to_ll(p, ref) for p in out]


def panel(ox, title, boundary, pts, keepouts=(), stats=None, bad=None):
    b = local(boundary)
    parts = [f'<text x="{ox + W / 2}" y="{H - 38}" text-anchor="middle" class="t">{title}</text>',
             f'<path d="{path_d(b, ox, True)}" class="yard"/>']
    for k in keepouts:
        parts.append(f'<path d="{path_d(local(k), ox, True)}" class="ko"/>')
    P = local(pts)
    parts.append(f'<path d="{path_d(P, ox)}" class="route"/>')
    if bad:
        for a, c in bad:
            parts.append(f'<path d="{path_d([a, c], ox)}" class="bad"/>')
    if stats:
        parts.append(f'<text x="{ox + W / 2}" y="{H - 20}" text-anchor="middle" class="s">{stats}</text>')
    return "\n".join(parts)


def crossing_legs(boundary, pts):
    poly, ref = missions._to_xy(boundary)
    P = missions._xy(pts, ref)
    off = local(boundary)[0]
    base = missions._xy(boundary, ref)[0]
    shift = (off[0] - base[0], off[1] - base[1])
    return [((a[0] + shift[0], a[1] + shift[1]), (b[0] + shift[0], b[1] + shift[1]))
            for a, b in zip(P, P[1:]) if not missions._clear(a, b, poly, [])]


def fmt(st):
    return f"{st['lawn_m2']:,} m² · ~{st['minutes']:g} min · {st['coverage_pct']:g}% covered"


def main():
    old = old_stitch(U_YARD, SPACING)
    bad = crossing_legs(U_YARD, old)
    rid_u, new_u = missions.plan_coverage_turns("u", U_YARD, SPACING)
    rid_b, new_b = missions.plan_coverage_turns("bed", SQUARE, SPACING, keepouts=[BED])
    st_u = missions.get_route(rid_u)["stats"]
    st_b = missions.get_route(rid_b)["stats"]
    body = "\n".join([
        panel(0, "before: rows stitched across the notch", U_YARD, old,
              stats=f"{len(bad)} of {len(old) - 1} legs leave the yard", bad=bad),
        panel(W, "now: cells, no-rut turns, perimeter laps", U_YARD, new_u, stats=fmt(st_u)),
        panel(2 * W, "keep-out: a flower bed", SQUARE, new_b, [BED], stats=fmt(st_b)),
    ])
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {3 * W} {H}" font-family="-apple-system,Segoe UI,Helvetica,Arial,sans-serif">
<style>
.yard{{fill:#2ecd8a14;stroke:#2ecd8a;stroke-width:2}}
.ko{{fill:#e0525a33;stroke:#e0525a;stroke-width:1.5}}
.route{{fill:none;stroke:#3e6ae1;stroke-width:1;stroke-linejoin:round}}
.bad{{fill:none;stroke:#e0525a;stroke-width:2.2}}
.t{{font-size:13px;font-weight:600;fill:#1f2328}}
.s{{font-size:11.5px;fill:#57606a}}
</style>
<rect width="100%" height="100%" fill="#ffffff"/>
{body}
</svg>
'''
    out = os.path.join(ROOT, "docs", "coverage-plan.svg")
    with open(out, "w") as f:
        f.write(svg)
    print(out, f"(old: {len(bad)} bad legs; U: {st_u}; bed: {st_b})")


if __name__ == "__main__":
    main()
