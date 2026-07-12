"""
Safety policy — incline, overhead clearance, and obstacle checks.

Pure, testable functions. The real sensor drivers write live values into the shared
state; THIS module is the single place that decides whether the machine may move:
  - incline      : IMU roll/pitch (from the Pixhawk) → refuse above the side-slope limit
  - overhead     : upward-facing ToF/ultrasonic → stop before the GPS mast hits a low branch
  - obstacle     : horizontal RPLidar stop-zone → stop for things in the path

This is the *software* interlock layer; it sits ON TOP of the hardware kill chain
(physical e-stop, RC kill, ArduPilot failsafes) — see docs/BUILD.md §0.
"""

# --- incline (rollover) ---
MAX_SLOPE_DEG  = 15.0     # refuse to move above this — ZTR side-slope rating / rollover risk
WARN_SLOPE_DEG = 12.0     # caution band (still moves, UI warns)

# --- overhead clearance (tree limbs) ---
# The tallest point of the machine is the GPS mast/antenna. Stop before a branch
# lower than this (plus margin) can strike it.
MAST_HEIGHT_M  = 1.45     # top of GPS mast above ground (tune to the built mast)
OVERHEAD_MARGIN_M = 0.15
MIN_OVERHEAD_M = MAST_HEIGHT_M + OVERHEAD_MARGIN_M    # 1.60 m

# --- horizontal obstacle ---
OBSTACLE_STOP_M = 2.0     # RPLidar stop-zone radius ahead

# --- geofence ---
# The operator draws a boundary polygon on the map; the machine must never move
# while outside it. Mirrors ArduPilot's inclusion fence (FENCE_TYPE polygon) —
# in --mav mode the same polygon is what gets pushed to the FC, this is the
# companion-side belt to the FC's suspenders.
FENCE_MIN_POINTS = 3

def point_in_polygon(lat, lon, poly):
    """Ray-casting point-in-polygon. poly = [[lat,lon], ...]; returns bool.
    Even-odd rule; points exactly on an edge count as inside (safe side)."""
    if not poly or len(poly) < FENCE_MIN_POINTS:
        return False
    inside = False
    j = len(poly) - 1
    for i in range(len(poly)):
        yi, xi = poly[i][0], poly[i][1]
        yj, xj = poly[j][0], poly[j][1]
        if (xi > lon) != (xj > lon):
            t = (lon - xi) / (xj - xi)
            if lat < yi + t * (yj - yi):
                inside = not inside
        j = i
    return inside

def fence_breach(s):
    """True when a fence is set+enabled and the machine is outside it."""
    poly = s.get("fence") or []
    if not s.get("fence_enabled") or len(poly) < FENCE_MIN_POINTS:
        return False
    return not point_in_polygon(s.get("lat"), s.get("lon"), poly)

def slope_of(roll, pitch):
    """Worst-case tilt magnitude (deg) from roll & pitch."""
    return round(max(abs(roll or 0.0), abs(pitch or 0.0)), 1)

def evaluate(s):
    """Given a state dict, return (allow_move: bool, reason: str|None).
    Reason is the single most important blocker, checked in priority order."""
    if s.get("estop"):
        return False, "E-STOP"
    if fence_breach(s):
        return False, "outside geofence — holding"
    slope = slope_of(s.get("roll"), s.get("pitch"))
    if slope > MAX_SLOPE_DEG:
        return False, f"too steep ({slope:.0f}°) — rollover risk"
    oh = s.get("overhead_m")
    if oh is not None and oh < MIN_OVERHEAD_M:
        return False, f"low branch ({oh:.1f} m) — mast clearance"
    if s.get("obstacle"):
        return False, "obstacle ahead — holding"
    return True, None

def can_arm(s):
    """Refuse to arm while already on a dangerous slope."""
    slope = slope_of(s.get("roll"), s.get("pitch"))
    if slope > MAX_SLOPE_DEG:
        return False, f"on a {slope:.0f}° slope — too steep to arm"
    return True, None

def slope_band(roll, pitch):
    """UI helper: 'ok' | 'warn' | 'bad'."""
    slope = slope_of(roll, pitch)
    return "bad" if slope > MAX_SLOPE_DEG else ("warn" if slope >= WARN_SLOPE_DEG else "ok")
