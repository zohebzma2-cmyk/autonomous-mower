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
    route["id"] = "r%d" % int(time.time() * 1000)
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
def _row_spans(poly_xy, y):
    """x-intervals where horizontal line at `y` is inside the polygon."""
    xs = []
    n = len(poly_xy)
    for i in range(n):
        x1, y1 = poly_xy[i]
        x2, y2 = poly_xy[(i + 1) % n]
        if (y1 <= y < y2) or (y2 <= y < y1):
            xs.append(x1 + (y - y1) / (y2 - y1) * (x2 - x1))
    xs.sort()
    return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]

def plan_coverage(name, polygon, spacing=DEFAULT_SPACING):
    """polygon: [[lat,lon],...] (>=3). Returns (route_id, waypoints[[lat,lon]...])."""
    if len(polygon) < 3:
        raise ValueError("need >= 3 boundary points")
    poly_xy, ref = _to_xy(polygon)
    ys = [p[1] for p in poly_xy]
    ymin, ymax = min(ys) + spacing / 2, max(ys) - spacing / 2
    wpts, flip = [], False
    y = ymin
    while y <= ymax:
        spans = _row_spans(poly_xy, y)
        for (xa, xb) in spans:
            seg = [(xa, y), (xb, y)]
            if flip:
                seg.reverse()
            wpts.extend(seg)
        flip = not flip
        y += spacing
    pts = [_to_ll(p, ref) for p in wpts]
    rid = _add({"name": name or "Coverage zone", "type": "coverage",
                "points": pts, "boundary": polygon, "spacing": spacing})
    return rid, pts

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

def plan_coverage_turns(name, polygon, spacing=DEFAULT_SPACING, r=TURN_RADIUS_M):
    """Coverage rows + no-rut row turns (U or 3-point K), rows inset by the
    turn radius (headland) so every turn stays inside the boundary."""
    if len(polygon) < 3:
        raise ValueError("need >= 3 boundary points")
    poly_xy, ref = _to_xy(polygon)
    ys = [pt[1] for pt in poly_xy]
    ymin, ymax = min(ys) + spacing / 2, max(ys) - spacing / 2
    rows, flip = [], False
    y = ymin
    while y <= ymax:
        for (xa, xb) in _row_spans(poly_xy, y):
            xa, xb = xa + r, xb - r                    # headland inset
            if xb - xa < spacing:
                continue
            rows.append(((xb, y), (xa, y)) if flip else ((xa, y), (xb, y)))
            flip = not flip
        y += spacing
    wpts = []
    for i, (a, b) in enumerate(rows):
        wpts += [a, b]
        if i + 1 < len(rows):
            direction = 1 if b[0] > a[0] else -1
            wpts += turn_points(b[0], b[1], rows[i + 1][0][1], direction, r)
    pts_ll = [_to_ll(pt, ref) for pt in wpts]
    rid = _add({"name": name or "Zone (no-rut turns)", "type": "coverage", "points": pts_ll})
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
