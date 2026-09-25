# SPDX-License-Identifier: MIT
"""
Missions: saved routes (teach-and-repeat) + coverage planning (boundary → rows).

A route is an ordered list of [lat, lon] waypoints the rover follows in AUTO.
  - "taught"   : recorded by driving the perimeter/path once.
  - "coverage" : auto-generated boustrophedon rows that fill a boundary polygon
                 at the deck spacing (52" ≈ 1.32 m, with overlap).

Persisted to data/missions.json. Planning is done in a local metric frame
(equirectangular about the polygon centroid) — fine for property-scale areas.
"""
import json, math, os, time

DATA = os.path.join(os.path.dirname(__file__), "data")
FILE = os.path.join(DATA, "missions.json")
DECK_M = 1.32                 # 52" deck width
DEFAULT_SPACING = 1.15        # row spacing (deck minus overlap)
CRUISE_MPS = 1.4              # firmware/ardupilot/rover_params.parm CRUISE_SPEED/WP_SPEED

# ---------------------------------------------------------------- persistence
def _load():
    try:
        with open(FILE) as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"routes": []}

def _save(db):
    os.makedirs(DATA, exist_ok=True)
    tmp = FILE + ".tmp"
    with open(tmp, "w") as f:
        json.dump(db, f, indent=1)
    os.replace(tmp, FILE)

def list_routes():
    return [{k: r[k] for k in ("id", "name", "type", "n", "created")} for r in _load()["routes"]]

def get_route(rid):
    return next((r for r in _load()["routes"] if r["id"] == rid), None)

def delete_route(rid):
    db = _load()
    db["routes"] = [r for r in db["routes"] if r["id"] != rid]
    _save(db)

def _add(route):
    db = _load()
    taken = {r["id"] for r in db["routes"]}
    ms = int(time.time() * 1000)
    while "r%d" % ms in taken:          # two saves in the same ms must not share an id
        ms += 1
    route["id"] = "r%d" % ms
    route["created"] = int(time.time())
    route["n"] = len(route["points"])
    db["routes"].append(route)
    _save(db)
    return route["id"]

def add_taught(name, points):
    return _add({"name": name or "Taught route", "type": "taught", "points": points})

# ---------------------------------------------------------------- geo helpers
def _frame(lat0):
    mlat = 111320.0
    mlon = 111320.0 * math.cos(math.radians(lat0))
    return mlat, mlon

def _to_xy(poly):
    lat0 = sum(p[0] for p in poly) / len(poly)
    lon0 = sum(p[1] for p in poly) / len(poly)
    mlat, mlon = _frame(lat0)
    return [((p[1] - lon0) * mlon, (p[0] - lat0) * mlat) for p in poly], (lat0, lon0, mlat, mlon)

def _to_ll(pt, ref):
    lat0, lon0, mlat, mlon = ref
    x, y = pt
    return [round(lat0 + y / mlat, 7), round(lon0 + x / mlon, 7)]

# ---------------------------------------------------------------- coverage planner
# Yards are rarely convex, and a sweep row through an L or U yard is cut into
# several spans. Stitching a row's spans together drives the leg between them
# straight across whatever fills the gap — in a real yard, the bed or the house
# in the notch. So the rows are grouped into CELLS first (boustrophedon cell
# decomposition): a span continues the cell above it only when the two overlap
# one-to-one. Each cell is a simple lane mowed back and forth; cells are joined
# by transit legs that are checked against the yard and, when blocked, routed
# around (shortest path over the yard's corners and the keep-outs' corners).
# Keep-outs — beds, trees, the shed, a spot the sonar keeps hitting — are holes
# in the sweep, so they get the same treatment.
EDGE_TOL_M = 0.05             # a point this close to an edge counts as on it
KEEPOUT_MARGIN_M = 0.6        # how wide a transit leg swings around a keep-out corner

def _xy(poly, ref):
    lat0, lon0, mlat, mlon = ref
    return [((p[1] - lon0) * mlon, (p[0] - lat0) * mlat) for p in poly]

def _crossings(poly_xy, y):
    xs = []
    n = len(poly_xy)
    for i in range(n):
        x1, y1 = poly_xy[i]
        x2, y2 = poly_xy[(i + 1) % n]
        if (y1 <= y < y2) or (y2 <= y < y1):
            xs.append(x1 + (y - y1) / (y2 - y1) * (x2 - x1))
    return xs

def _row_spans(poly_xy, y, holes=()):
    """x-intervals where the horizontal line at `y` is inside the polygon and
    outside every hole (even-odd over all edges; holes must lie inside)."""
    xs = _crossings(poly_xy, y)
    for h in holes:
        xs += _crossings(h, y)
    xs.sort()
    return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]

def _inside(pt, poly):
    x, y = pt
    c = False
    n = len(poly)
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) / (y2 - y1) * (x2 - x1):
            c = not c
    return c

def _edge_dist(pt, poly):
    px, py = pt
    best = float("inf")
    n = len(poly)
    for i in range(n):
        ax, ay = poly[i]
        bx, by = poly[(i + 1) % n]
        dx, dy = bx - ax, by - ay
        L2 = dx * dx + dy * dy
        t = 0.0 if L2 == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / L2))
        best = min(best, math.hypot(px - ax - t * dx, py - ay - t * dy))
    return best

def _ok(pt, poly, holes):
    """Inside the yard (edges count) and not inside any keep-out (edges count)."""
    if not _inside(pt, poly) and _edge_dist(pt, poly) > EDGE_TOL_M:
        return False
    return all(not _inside(pt, h) or _edge_dist(pt, h) <= EDGE_TOL_M for h in holes)

def _clear(a, b, poly, holes, step=0.25):
    n = max(2, int(math.hypot(b[0] - a[0], b[1] - a[1]) / step))
    return all(_ok((a[0] + (b[0] - a[0]) * k / n, a[1] + (b[1] - a[1]) * k / n), poly, holes)
               for k in range(1, n))

def _route(a, b, poly, holes):
    """Points to pass through between a and b (both excluded) so every leg stays
    in the yard and out of the keep-outs. Raises ValueError if there is none."""
    if _clear(a, b, poly, holes):
        return []
    m = KEEPOUT_MARGIN_M
    nodes = []
    ring = list(poly)
    for i, v in enumerate(ring):             # yard corners, nudged inward
        u = ring[i - 1]
        w = ring[(i + 1) % len(ring)]
        e1 = (u[0] - v[0], u[1] - v[1])
        e2 = (w[0] - v[0], w[1] - v[1])
        l1, l2 = math.hypot(*e1) or 1, math.hypot(*e2) or 1
        bx, by = e1[0] / l1 + e2[0] / l2, e1[1] / l1 + e2[1] / l2
        lb = math.hypot(bx, by) or 1
        for sgn in (1, -1):
            nodes.append((v[0] + sgn * m * bx / lb, v[1] + sgn * m * by / lb))
    for h in holes:                          # keep-out corners, swung wide
        xs = [p[0] for p in h]
        ys = [p[1] for p in h]
        nodes += [(min(xs) - m, min(ys) - m), (max(xs) + m, min(ys) - m),
                  (max(xs) + m, max(ys) + m), (min(xs) - m, max(ys) + m)]
    nodes = [a, b] + [q for q in nodes if _ok(q, poly, holes)]
    dist = {0: 0.0}
    prev = {}
    todo = set(range(len(nodes)))
    while todo:                              # Dijkstra, edges tested lazily
        i = min(todo, key=lambda k: dist.get(k, float("inf")))
        if i not in dist:
            break
        todo.discard(i)
        if i == 1:
            break
        for j in todo:
            d = dist[i] + math.hypot(nodes[j][0] - nodes[i][0], nodes[j][1] - nodes[i][1])
            if d < dist.get(j, float("inf")) and _clear(nodes[i], nodes[j], poly, holes):
                dist[j] = d
                prev[j] = i
    if 1 not in prev:
        raise ValueError("no clear path between mowing areas — is a keep-out touching the boundary?")
    path, k = [], prev[1]
    while k != 0:
        path.append(nodes[k])
        k = prev[k]
    return path[::-1]

def _safe_spans(poly, holes, y, reach, ylo, yhi, samples=8):
    """Row spans at `y`, each narrowed to what stays inside the yard across
    y ± reach — the band a row-end turn sweeps. On a slanted edge the yard is
    narrower one row over, and a turn sized from its own row pokes out."""
    spans = _row_spans(poly, y, holes)
    if reach <= 0:
        return spans
    out = []
    for xa, xb in spans:
        for k in range(samples + 1):
            y2 = min(yhi, max(ylo, y - reach + 2 * reach * k / samples))
            over = [(a, b) for a, b in _row_spans(poly, y2, holes) if a < xb and xa < b]
            if not over:
                continue
            xa = max(xa, min(a for a, _ in over))
            xb = min(xb, max(b for _, b in over))
        if xb > xa:
            out.append((xa, xb))
    return out

def _cells(poly, holes, spacing, inset=0.0, min_len=0.0, reach=0.0):
    """Swept rows grouped into cells: [[(y, xa, xb), ...], ...], rows in sweep order.
    reach > 0 narrows each row to what fits a turn that far above/below it."""
    ys = [p[1] for p in poly]
    y, ymax = min(ys) + spacing / 2, max(ys) - spacing / 2
    lo, hi = min(ys) + 1e-6, max(ys) - 1e-6
    cells: list = []
    prev: list = []
    while y <= ymax + 1e-9:
        spans = [(xa + inset, xb - inset) for xa, xb in _safe_spans(poly, holes, y, reach, lo, hi)
                 if (xb - xa) - 2 * inset > max(min_len, 0.0)]
        cur = []
        for sp in spans:
            over = [(ci, ps) for ci, ps in prev if ps[0] < sp[1] and sp[0] < ps[1]]
            one_to_one = len(over) == 1 and sum(
                1 for s2 in spans if over[0][1][0] < s2[1] and s2[0] < over[0][1][1]) == 1
            if one_to_one:
                ci = over[0][0]
            else:
                ci = len(cells)
                cells.append([])
            cells[ci].append((y, sp[0], sp[1]))
            cur.append((ci, sp))
        prev = cur
        y += spacing
    return cells

def _orient(rows, rev, right):
    """Row list for one cell as [(start, end)], alternating direction."""
    rows = rows[::-1] if rev else rows
    out = []
    for k, (y, xa, xb) in enumerate(rows):
        seg = ((xb, y), (xa, y)) if (k % 2 == 0) == right else ((xa, y), (xb, y))
        out.append(seg)
    return out

def _plan(polygon, keepouts, spacing, inset=0.0, min_len=0.0, reach=0.0):
    """Shared core: cells ordered nearest-next, each as oriented rows, plus the frame."""
    if len(polygon) < 3:
        raise ValueError("need >= 3 boundary points")
    poly, ref = _to_xy(polygon)
    holes = []
    for k in keepouts or []:
        if len(k) < 3:
            raise ValueError("each keep-out needs >= 3 points")
        h = _xy(k, ref)
        if not all(_inside(p, poly) for p in h):
            raise ValueError("keep-outs must lie inside the boundary")
        holes.append(h)
    cells = [c for c in _cells(poly, holes, spacing, inset, min_len, reach) if c]
    order = [_orient(cells.pop(0), False, False)] if cells else []
    while cells:                             # nearest next cell, best entry corner
        here = order[-1][-1][1]
        best = min(((math.hypot(rows[0][0][0] - here[0], rows[0][0][1] - here[1]), ci, rows)
                    for ci, c in enumerate(cells)
                    for rows in (_orient(c, rev, right) for rev in (False, True) for right in (False, True))),
                   key=lambda t: t[0])
        order.append(best[2])
        cells.pop(best[1])
    return order, poly, holes, ref

def _area(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1]
                   for i in range(len(poly)))) / 2

def _stats(order, wpts, poly, holes, spacing, laps=()):
    """What the plan will take: shown before the machine moves."""
    mow = sum(math.hypot(b[0] - a[0], b[1] - a[1]) for rows in order for a, b in rows)
    mow += sum(math.hypot(q[0] - p[0], q[1] - p[1]) for lap in laps for p, q in zip(lap, lap[1:]))
    path = sum(math.hypot(q[0] - p[0], q[1] - p[1]) for p, q in zip(wpts, wpts[1:]))
    lawn = max(_area(poly) - sum(_area(h) for h in holes), 1e-9)
    return {"lawn_m2": round(lawn), "mow_m": round(mow), "path_m": round(path),
            "cells": len(order), "turns": sum(max(len(rows) - 1, 0) for rows in order),
            "coverage_pct": round(min(100.0, 100 * mow * spacing / lawn), 1),
            "minutes": round(path / CRUISE_MPS / 60, 1)}

def plan_coverage(name, polygon, spacing=DEFAULT_SPACING, keepouts=None):
    """polygon: [[lat,lon],...] (>=3); keepouts: optional list of polygons to
    leave unmowed. Returns (route_id, waypoints[[lat,lon]...])."""
    order, poly, holes, ref = _plan(polygon, keepouts, spacing)
    wpts: list = []
    for rows in order:
        if wpts:
            wpts += _route(wpts[-1], rows[0][0], poly, holes)
        for a, b in rows:
            wpts += [a, b]
    pts = [_to_ll(p, ref) for p in wpts]
    rid = _add({"name": name or "Coverage zone", "type": "coverage", "points": pts,
                "boundary": polygon, "keepouts": keepouts or [], "spacing": spacing,
                "stats": _stats(order, wpts, poly, holes, spacing)})
    return rid, pts

# ---------------------------------------------------------------- obstacle hotspots
# The companion logs where the sonar/vision stop fired (app.obstacle_log). One
# hit is a dog or a kid; the same spot again and again is a stump, a post or a
# low branch. Those clusters are offered as keep-outs — a suggestion the user
# confirms, never added silently.
def obstacle_hotspots(hits, radius_m=1.5, min_hits=3, pad_m=0.5):
    """hits: [{"lat","lon",...}] -> [{"lat","lon","hits","keepout":[[lat,lon]x4]}],
    densest first. A hotspot is >= min_hits within radius_m of one another."""
    pts = [(h["lat"], h["lon"]) for h in hits
           if isinstance(h, dict) and h.get("lat") is not None and h.get("lon") is not None]
    if not pts:
        return []
    mlat, mlon = _frame(pts[0][0])
    xy = [((lon - pts[0][1]) * mlon, (lat - pts[0][0]) * mlat) for lat, lon in pts]
    left = list(range(len(xy)))
    out = []
    while left:
        best: list = []
        for i in left:
            near = [j for j in left if math.hypot(xy[j][0] - xy[i][0], xy[j][1] - xy[i][1]) <= radius_m]
            if len(near) > len(best):
                best = near
        if len(best) < min_hits:
            break
        cx = sum(xy[j][0] for j in best) / len(best)
        cy = sum(xy[j][1] for j in best) / len(best)
        half = max(0.75, max(math.hypot(xy[j][0] - cx, xy[j][1] - cy) for j in best) + pad_m)

        def ll(x, y):
            return [round(pts[0][0] + y / mlat, 7), round(pts[0][1] + x / mlon, 7)]
        out.append({"lat": ll(cx, cy)[0], "lon": ll(cx, cy)[1], "hits": len(best),
                    "keepout": [ll(cx - half, cy - half), ll(cx + half, cy - half),
                                ll(cx + half, cy + half), ll(cx - half, cy + half)]})
        left = [j for j in left if j not in best]
    return out

# ---------------------------------------------------------------- nav helper
def step_towards(lat, lon, target, dist_m):
    """Move dist_m from (lat,lon) toward target [lat,lon]; returns (lat,lon,heading,reached)."""
    mlat, mlon = _frame(lat)
    dx = (target[1] - lon) * mlon
    dy = (target[0] - lat) * mlat
    d = math.hypot(dx, dy)
    hdg = (math.degrees(math.atan2(dx, dy))) % 360
    if d <= dist_m or d == 0:
        return target[0], target[1], hdg, True
    f = dist_m / d
    return round(lat + dy * f / mlat, 7), round(lon + dx * f / mlon, 7), round(hdg, 1), False


def cross_track_m(pos, a, b):
    """Perpendicular distance (m) from pos to the segment a->b (all [lat,lon]).
    Clamped to the segment ends — this is the live RTK tracking-quality number."""
    mlat, mlon = _frame(a[0])
    px, py = (pos[1] - a[1]) * mlon, (pos[0] - a[0]) * mlat
    bx, by = (b[1] - a[1]) * mlon, (b[0] - a[0]) * mlat
    L2 = bx * bx + by * by
    if L2 == 0:
        return round(math.hypot(px, py), 3)
    t = max(0.0, min(1.0, (px * bx + py * by) / L2))
    return round(math.hypot(px - t * bx, py - t * by), 3)


# ---------------------------------------------------------------- no-rut turns
# A zero-turn PIVOT spins one wheel forward and one backward in place: all of
# the machine's yaw moment goes through two small contact patches as SHEAR on
# the turf, and 615 lb of scrub tears it — that's the classic ZTR rut/divot.
# Keeping BOTH wheels rolling forward (or backward) turns shear into rolling
# friction. So row ends use:
#   spacing >= 2r : smooth U — arc 90°, straight, arc 90° (never stops rolling)
#   spacing <  2r : 3-point K — forward arc 90°, REVERSE straight 2r-spacing,
#                   forward arc 90° onto the next row (the tractor headland turn)
# r is the gentlest arc the hydros hold accurately; rows are inset by r
# (a headland) so the turn never leaves the boundary.
TURN_RADIUS_M = 1.2

def _arc(cx, cy, r, a0, a1, steps=3):
    """Sample an arc (local xy, radians) — endpoints included."""
    return [(cx + r * math.sin(a0 + (a1 - a0) * i / steps),
             cy - r * math.cos(a0 + (a1 - a0) * i / steps)) for i in range(1, steps + 1)]

def turn_points(x_end, y, y_next, direction, r=TURN_RADIUS_M):
    """Local-frame waypoints for a no-rut row turn.
    direction: +1 = the finished row ran +x, -1 = ran -x.  Returns [(x,y)...]
    from just after the row end to just before the next row start."""
    s_gap = abs(y_next - y)
    up = 1 if y_next > y else -1
    pts = []
    if s_gap >= 2 * r:                       # smooth U: arc, straight, arc
        pts += _arc(x_end, y + up * r, r, math.pi, math.pi / 2)[::-1] if False else                [(x_end + direction * r * math.sin(t * math.pi / 6), y + up * r * (1 - math.cos(t * math.pi / 6)))
                for t in (1, 2, 3)]
        pts += [(x_end + direction * r, y + up * (s_gap - r))]
        pts += [(x_end + direction * r * math.cos(t * math.pi / 6), y_next - up * r * (1 - math.sin(t * math.pi / 6)))
                for t in (1, 2, 3)]
    else:                                    # 3-point K: fwd arc, reverse, fwd arc
        b = 2 * r - s_gap                    # reverse length
        pts += [(x_end + direction * r * math.sin(t * math.pi / 6), y + up * r * (1 - math.cos(t * math.pi / 6)))
                for t in (1, 2, 3)]          # fwd 90° arc, ends heading across rows
        pts += [(x_end + direction * r, y + up * (r - b / 2)),
                (x_end + direction * r, y + up * (r - b))]     # reverse straight (tail swing)
        pts += [(x_end + direction * r * math.cos(t * math.pi / 6),
                 (y + up * (r - b)) + up * r * math.sin(t * math.pi / 6)) for t in (1, 2, 3)]
    return pts

# ---------------------------------------------------------------- perimeter laps
# Rows stop a turn radius short of every edge so the no-rut turns fit; that
# strip (the headland) is 10-14% of a typical lawn. It is mowed last, as laps
# around the yard and around each keep-out — the tractor order, so the laps
# also clean up the turn marks.
def _signed_area(ring):
    return sum(ring[i][0] * ring[(i + 1) % len(ring)][1] - ring[(i + 1) % len(ring)][0] * ring[i][1]
               for i in range(len(ring))) / 2

def _offset(ring, d):
    """The ring moved d metres to the left of travel (for a CCW ring: inward)."""
    n = len(ring)
    lines = []
    for i in range(n):
        (x1, y1), (x2, y2) = ring[i], ring[(i + 1) % n]
        L = math.hypot(x2 - x1, y2 - y1) or 1
        nx, ny = -(y2 - y1) / L, (x2 - x1) / L
        lines.append(((x1 + nx * d, y1 + ny * d), (x2 + nx * d, y2 + ny * d)))
    out = []
    for i in range(n):                       # mitred corners: adjacent offset lines meet
        (p1, p2), (p3, p4) = lines[i - 1], lines[i]
        den = (p1[0] - p2[0]) * (p3[1] - p4[1]) - (p1[1] - p2[1]) * (p3[0] - p4[0])
        if abs(den) < 1e-9:
            out.append(p3)
            continue
        t = ((p1[0] - p3[0]) * (p3[1] - p4[1]) - (p1[1] - p3[1]) * (p3[0] - p4[0])) / den
        out.append((p1[0] + t * (p2[0] - p1[0]), p1[1] + t * (p2[1] - p1[1])))
    return out

def _laps(poly, holes, spacing, width):
    """Closed laps covering `width` metres in from the yard edge and out from
    each keep-out, innermost first. A lap that would leave the yard or clip a
    keep-out (a pinch point) is dropped rather than driven."""
    n = max(1, math.ceil(width / spacing))
    rings = []
    for ring, sign in [(h, -1) for h in holes] + [(poly, 1)]:
        ccw = ring if _signed_area(ring) > 0 else ring[::-1]
        for k in reversed(range(n)):
            lap = _offset(ccw, sign * (spacing / 2 + k * spacing))
            if _signed_area(lap) <= 0:
                continue
            lap = lap + lap[:1]
            if all(_ok(q, poly, holes) for q in lap) and \
                    all(_clear(a, b, poly, holes) for a, b in zip(lap, lap[1:])):
                rings.append(lap)
    return rings

def plan_coverage_turns(name, polygon, spacing=DEFAULT_SPACING, r=TURN_RADIUS_M, keepouts=None,
                        perimeter=True):
    """Coverage rows + no-rut row turns (U or 3-point K), rows inset by the
    turn radius (headland) from the boundary and every keep-out, so each turn
    stays in the yard. Cells are joined by routed transit legs; the headland
    is mowed last as perimeter laps (perimeter=False leaves it)."""
    # a turn climbs up to max(r, spacing) toward the next row: rows are sized for that band
    order, poly, holes, ref = _plan(polygon, keepouts, spacing, inset=r, min_len=spacing,
                                    reach=max(r, spacing))
    wpts: list = []
    for rows in order:
        rows = list(rows)
        if wpts:
            wpts += _route(wpts[-1], rows[0][0], poly, holes)
        for i, (a, b) in enumerate(rows):
            wpts += [a, b]
            if i + 1 < len(rows):
                direction = 1 if b[0] > a[0] else -1
                wpts += turn_points(b[0], b[1], rows[i + 1][0][1], direction, r)
                # The turn finishes at this row's end x. If the next row would start
                # beyond that, the machine would have to back up to reach it, so the
                # next row starts where the turn ends; the perimeter laps take the rest.
                (nsx, ny), nend = rows[i + 1]
                nsx = min(nsx, b[0]) if direction > 0 else max(nsx, b[0])
                rows[i + 1] = ((nsx, ny), nend)
    laps = _laps(poly, holes, spacing, r) if perimeter else []
    for lap in laps:
        if wpts:                             # start each lap at its corner nearest to here
            i = min(range(len(lap) - 1), key=lambda k: math.hypot(lap[k][0] - wpts[-1][0],
                                                                  lap[k][1] - wpts[-1][1]))
            lap = lap[i:-1] + lap[:i + 1]
            wpts += _route(wpts[-1], lap[0], poly, holes)
        wpts += lap
    pts_ll = [_to_ll(pt, ref) for pt in wpts]
    rid = _add({"name": name or "Zone (no-rut turns)", "type": "coverage", "points": pts_ll,
                "boundary": polygon, "keepouts": keepouts or [], "spacing": spacing,
                "stats": _stats(order, wpts, poly, holes, spacing, laps)})
    return rid, pts_ll


# ---------------------------------------------------------------- QGC .plan
def to_qgc_plan(points):
    """Waypoints -> QGroundControl/Mission Planner .plan JSON (dict)."""
    items = [{"autoContinue": True, "command": 16, "doJumpId": i + 1,
              "frame": 3, "params": [0, 0, 0, None, p[0], p[1], 0],
              "type": "SimpleItem"} for i, p in enumerate(points)]
    return {"fileType": "Plan", "version": 1, "groundStation": "autonomous-mower",
            "geoFence": {"circles": [], "polygons": [], "version": 2},
            "rallyPoints": {"points": [], "version": 2},
            "mission": {"cruiseSpeed": 1.4, "firmwareType": 10, "hoverSpeed": 1,
                        "vehicleType": 10, "version": 2,
                        "plannedHomePosition": list(points[0]) + [0] if points else [0, 0, 0],
                        "items": items}}

def from_qgc_plan(plan):
    """QGC .plan dict -> [[lat,lon],...] (NAV_WAYPOINT items only)."""
    out = []
    for it in (plan.get("mission") or {}).get("items", []):
        if it.get("command") == 16 and it.get("params") and len(it["params"]) >= 6:
            out.append([it["params"][4], it["params"][5]])
    return out
