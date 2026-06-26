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
