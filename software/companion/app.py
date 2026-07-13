#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Autonomous ZTR — companion control server.

ONE web UI, served here, drives both the iPad (Safari over WiFi) and the on-unit
touchscreen (Chromium kiosk). Pure Python stdlib so it runs with zero installs —
telemetry is pushed via Server-Sent Events (SSE), controls via JSON POST.

Modes:
  --sim   (default) generate plausible telemetry, no hardware needed — build/demo today.
  --mav udp:127.0.0.1:14550   talk to ArduPilot via MAVLink (SITL or real Pixhawk).
                              (requires `pip install pymavlink`; see dev/SITL.md)

SAFETY: this is development scaffolding. The real machine's safety lives in the
hardware kill chain (e-stop, RC kill, ArduPilot failsafes) per docs/BUILD.md §0.
The web E-STOP here is a convenience that commands HOLD + disarm + blade-off; it is
NOT a substitute for the physical e-stop.
"""
import argparse, json, os, threading, time, math, queue, random, urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import missions, safety, vision, attachments

UI_DIR = os.path.join(os.path.dirname(__file__), "..", "ui")

# ---------------------------------------------------------------- shared state
class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.subscribers = []                  # list[queue.Queue] for SSE fan-out
        self.recording = []                    # taught waypoints being recorded
        self.active_route = []                 # waypoints currently being followed
        self.route_idx = 0
        self.mav_cmd = None                    # set by mav.py in --mav mode → forwards drive cmds
        self.d = dict(
            connected=True, mode="MANUAL", armed=False, mission="idle",
            blade=False, estop=False,
            gps_fix="rtk_fixed", sats=22, hdop=0.6,
            battery_v=12.9, battery_pct=92, speed=0.0, heading=0.0,
            lat=39.8283, lon=-98.5795,          # demo default (recenters on the real GPS fix)
            obstacle=False, obstacle_range=None,
            roll=0.0, pitch=0.0, slope=0.0,     # IMU tilt (deg) → incline safety
            overhead_m=5.0,                     # upward sensor: branch clearance (m)
            objects=[], grass_pct=0,            # camera-AI: detected objects + grass coverage
            cameras=["front", "rear"],          # camera feeds available
            mode_options=["MANUAL", "HOLD", "AUTO"],
            taught_points=0, route_id=None, progress=0,   # active route id + % complete
            fence=[], fence_enabled=False, fence_breach=False,   # geofence polygon [[lat,lon],..]
            xte_m=None,                                          # live cross-track error (m)
            engine_hours=0.0, oil_due_h=None, blade_due_h=None,  # maintenance counters
            weather=None,                                        # {temp_c, precip_prob} when --weather
            engine="run", engine_rpm=2800, choke=0.0,            # ignition state machine (off|crank|run)
            tires={"rl": 12.1, "rr": 11.9, "fl": 20.2, "fr": 19.8}, tire_warnings=[],   # TPMS (psi)
            bagger={"attached": True, "fill_pct": 0.0, "state": "idle"},                # power bagger
            boom={"angle": 0.0, "blower": False, "trimmer": False},                     # blower/trimmer boom
            sprayer={"attached": False, "tank_pct": 100.0, "pump_duty": 0.0, "spraying": False, "applied_l": 0.0},
            msg="sim: ready",
        )
        self.d.update(_load_fence())               # restore a persisted fence
        self.d.update(_load_service())             # restore engine-hours / service history

    def snapshot(self):
        with self.lock:
            return dict(self.d)

    def update(self, **kw):
        with self.lock:
            self.d.update(kw)
        self.broadcast()

    def broadcast(self):
        snap = self.snapshot()
        data = "data: " + json.dumps(snap) + "\n\n"
        for q in list(self.subscribers):
            try: q.put_nowait(data)
            except queue.Full: pass

    def subscribe(self):
        q = queue.Queue(maxsize=20)
        with self.lock: self.subscribers.append(q)
        return q

    def unsubscribe(self, q):
        with self.lock:
            if q in self.subscribers: self.subscribers.remove(q)

# ---------------------------------------------------------------- geofence
def _fence_path():
    return os.path.join(missions.DATA, "fence.json")

def _load_fence():
    try:
        with open(_fence_path()) as f:
            j = json.load(f)
        poly = j.get("fence") or []
        if len(poly) >= safety.FENCE_MIN_POINTS:
            return dict(fence=poly, fence_enabled=bool(j.get("enabled", True)))
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        pass
    return {}

def set_fence(polygon):
    """Set (>=3 points) or clear (empty) the geofence. Returns (ok, msg)."""
    poly = [[float(p[0]), float(p[1])] for p in (polygon or [])]
    if poly and len(poly) < safety.FENCE_MIN_POINTS:
        return False, f"fence needs at least {safety.FENCE_MIN_POINTS} points"
    enabled = bool(poly)
    try:
        os.makedirs(missions.DATA, exist_ok=True)
        with open(_fence_path(), "w") as f:
            json.dump({"fence": poly, "enabled": enabled}, f)
    except OSError:
        pass                                       # persistence is best-effort
    S.update(fence=poly, fence_enabled=enabled,
             fence_breach=safety.fence_breach({**S.snapshot(), "fence": poly, "fence_enabled": enabled}),
             msg=(f"geofence set ({len(poly)} points)" if enabled else "geofence cleared"))
    return True, ("set" if enabled else "cleared")

# ---------------------------------------------------------------- maintenance
# Service intervals (hours). Defaults follow the Kohler 7000 / mower-shop norms:
# oil every 100 h (25 h first break-in), blades inspected/sharpened ~25 mowing h.
# Confirm against YOUR engine manual; history lives in data/service.json.
OIL_INTERVAL_H   = 100.0
BLADE_INTERVAL_H = 25.0

def _service_path():
    return os.path.join(missions.DATA, "service.json")

def _service_fields(hours, last_oil, last_blade):
    return dict(engine_hours=round(hours, 2),
                oil_due_h=round(last_oil + OIL_INTERVAL_H - hours, 1),
                blade_due_h=round(last_blade + BLADE_INTERVAL_H - hours, 1),
                _last_oil_h=last_oil, _last_blade_h=last_blade)

def _load_service():
    try:
        with open(_service_path()) as f:
            j = json.load(f)
        return _service_fields(float(j.get("engine_hours", 0.0)),
                               float(j.get("last_oil_h", 0.0)),
                               float(j.get("last_blade_h", 0.0)))
    except (FileNotFoundError, json.JSONDecodeError, OSError, ValueError):
        return _service_fields(0.0, 0.0, 0.0)

def _save_service(d):
    try:
        os.makedirs(missions.DATA, exist_ok=True)
        with open(_service_path(), "w") as f:
            json.dump({"engine_hours": d["engine_hours"],
                       "last_oil_h": d.get("_last_oil_h", 0.0),
                       "last_blade_h": d.get("_last_blade_h", 0.0)}, f)
    except OSError:
        pass

def reset_service(item):
    """Operator serviced the machine: restart that counter from now."""
    d = S.snapshot()
    if item == "oil":
        S.update(**_service_fields(d["engine_hours"], d["engine_hours"], d.get("_last_blade_h", 0.0)))
    elif item == "blade":
        S.update(**_service_fields(d["engine_hours"], d.get("_last_oil_h", 0.0), d["engine_hours"]))
    else:
        return False, "unknown service item " + str(item)
    _save_service(S.snapshot())
    return True, item + " service logged at %.1f h" % d["engine_hours"]

# ---------------------------------------------------------------- weather gate
WEATHER_HOLD_PROB = 60      # refuse to start when rain probability (next 2 h) >= this

def weather_gate(weather, threshold=WEATHER_HOLD_PROB):
    """True = hold (rain likely). Fails OPEN when weather is unknown."""
    if not weather or weather.get("precip_prob") is None:
        return False
    return weather["precip_prob"] >= threshold

def weather_loop():
    """Poll open-meteo (no API key) every 15 min for rain probability at the
    machine's position. Best-effort: failures leave weather=None (gate opens)."""
    while True:
        d = S.snapshot()
        url = ("https://api.open-meteo.com/v1/forecast?latitude=%.4f&longitude=%.4f"
               "&current=temperature_2m&hourly=precipitation_probability&forecast_hours=2"
               % (d["lat"], d["lon"]))
        try:
            with urllib.request.urlopen(url, timeout=10) as r:
                j = json.load(r)
            prob = max(j["hourly"]["precipitation_probability"] or [0])
            S.update(weather={"temp_c": j["current"]["temperature_2m"], "precip_prob": prob})
        except Exception:
            S.update(weather=None)
        time.sleep(900)

# ---------------------------------------------------------------- obstacle memory
def _obstacles_path():
    return os.path.join(missions.DATA, "obstacles.json")

def obstacle_log(prev_obstacle, d):
    """On a rising obstacle edge, remember where — repeated hits at one spot
    suggest a permanent geofence cut. Returns the (possibly grown) list."""
    if not d.get("obstacle") or prev_obstacle:
        return None
    try:
        with open(_obstacles_path()) as f:
            hits = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError, OSError):
        hits = []
    hits.append({"lat": d["lat"], "lon": d["lon"], "range_m": d.get("obstacle_range")})
    hits = hits[-200:]
    try:
        os.makedirs(missions.DATA, exist_ok=True)
        with open(_obstacles_path(), "w") as f:
            json.dump(hits, f)
    except OSError:
        pass
    return hits

S = State()

# ---------------------------------------------------------------- command handling
def handle_command(cmd, args=None):
    """Apply a control command to state. Returns (ok, message)."""
    d = S.snapshot()
    if cmd == "estop":
        S.active_route = []
        boom = {**d["boom"], "blower": False, "trimmer": False}
        spr = {**d["sprayer"], "pump_duty": 0.0, "spraying": False}
        bag = {**d["bagger"], "state": "idle"}
        S.update(estop=True, blade=False, armed=False, mode="HOLD", mission="idle",
                 speed=0.0, route_id=None, progress=0,
                 engine="off", engine_rpm=0,                    # kill chain grounds the magneto
                 boom=boom, sprayer=spr, bagger=bag,
                 msg="E-STOP — ignition, drive, blade + attachments killed")
        return True, "E-STOP engaged"
    if d["estop"] and cmd != "clear_estop":
        return False, "E-STOP is engaged — clear it first"
    if cmd == "clear_estop":
        S.update(estop=False, msg="e-stop cleared (still disarmed)")
        return True, "cleared"
    if cmd == "engine_start":
        ok, why = attachments.can_crank(d)
        if not ok:
            return False, why
        temp = (d.get("weather") or {}).get("temp_c")
        S.update(engine="crank", engine_rpm=350, choke=attachments.choke_for(temp),
                 msg="cranking (choke %.0f%%)" % (attachments.choke_for(temp) * 100))
        return True, "cranking"
    if cmd == "engine_stop":
        S.update(engine="off", engine_rpm=0, blade=False, armed=False, mission="idle",
                 speed=0.0, msg="engine stopped")
        return True, "engine off"
    if cmd == "bagger_dump":
        ok, why = attachments.can_dump(d)
        if not ok:
            return False, why
        S.update(bagger={**d["bagger"], "state": "raising", "t": 0.0}, msg="bagger: raising bins")
        return True, "dumping"
    if cmd == "boom":
        b = dict(d["boom"])
        if "angle" in (args or {}):
            b["angle"] = attachments.clamp_boom(args["angle"])
        if "blower" in (args or {}):
            b["blower"] = bool(args["blower"]) and not d["estop"]
        if "trimmer" in (args or {}):
            if args["trimmer"]:
                ok, why = attachments.can_run_trimmer(d)
                if not ok:
                    return False, why
            b["trimmer"] = bool(args["trimmer"])
        S.update(boom=b, msg="boom @ %.0f° · blower %s · trimmer %s" %
                 (b["angle"], "on" if b["blower"] else "off", "on" if b["trimmer"] else "off"))
        return True, "boom"
    if cmd == "sprayer":
        spr = dict(d["sprayer"])
        if "attached" in (args or {}):
            spr["attached"] = bool(args["attached"])
        if "spraying" in (args or {}):
            if args["spraying"]:
                ok, why = attachments.can_spray({**d, "sprayer": spr})
                if not ok:
                    return False, why
            spr["spraying"] = bool(args["spraying"])
        S.update(sprayer=spr, msg="sprayer %s" % ("ON — rate follows ground speed" if spr["spraying"] else "off"))
        return True, "sprayer"
    if cmd == "arm":
        if d.get("engine") != "run":
            return False, "engine not running — start it first"
        if d["gps_fix"] not in ("rtk_fixed", "rtk_float", "3d"):
            return False, "no GPS fix — refusing to arm"
        ok, why = safety.can_arm(d)          # refuse to arm on a dangerous slope
        if not ok:
            return False, why
        S.update(armed=True, msg="armed")
        return True, "armed"
    if cmd == "disarm":
        S.active_route = []
        S.update(armed=False, mission="idle", speed=0.0, blade=False,
                 route_id=None, progress=0, msg="disarmed")
        return True, "disarmed"
    if cmd == "mode":
        m = (args or {}).get("mode", "")
        if m not in d["mode_options"]:
            return False, f"unknown mode {m}"
        S.update(mode=m, msg=f"mode → {m}")
        return True, m
    if cmd == "blade":
        on = bool((args or {}).get("on"))
        # GATE: blade only with the operator's explicit on + armed (mirrors PTO interlock)
        if on and not d["armed"]:
            return False, "arm first before engaging blade"
        S.update(blade=on, msg=("blade ON" if on else "blade off"))
        return True, "blade " + ("on" if on else "off")
    if cmd in ("start", "resume"):
        if not d["armed"]:
            return False, "arm first"
        if d["mode"] != "AUTO":
            return False, "set mode AUTO to run a mission"
        if weather_gate(d.get("weather")) and not (args or {}).get("override_weather"):
            return False, ("rain likely (%s%% next 2h) - weather hold (override to force)"
                           % d["weather"]["precip_prob"])
        S.update(mission="running", msg="mission running")
        return True, "running"
    if cmd == "pause":
        S.update(mission="paused", speed=0.0, msg="mission paused")
        return True, "paused"
    if cmd == "teach_start":
        S.recording = [[d["lat"], d["lon"]]]
        S.update(mission="teaching", taught_points=1, msg="teach: recording path")
        return True, "teaching"
    if cmd == "teach_stop":
        name = (args or {}).get("name") or "Taught route"
        rid = missions.add_taught(name, list(S.recording)) if len(S.recording) > 1 else None
        S.recording = []
        S.update(mission="idle", msg=f"teach: saved '{name}' ({d['taught_points']} pts)")
        return True, rid or "discarded"
    if cmd == "run_route":
        r = missions.get_route((args or {}).get("id", ""))
        if not r:
            return False, "route not found"
        if not d["armed"]:
            return False, "arm first"
        S.active_route = list(r["points"]); S.route_idx = 0
        lat0, lon0 = r["points"][0]
        S.update(mode="AUTO", mission="running", lat=lat0, lon=lon0,
                 route_id=r["id"], progress=0,
                 msg=f"running '{r['name']}' ({len(r['points'])} wpts)")
        return True, "running"
    return False, f"unknown command {cmd}"

# ---------------------------------------------------------------- sim physics
def sim_loop():
    t = 0.0
    while True:
        t += 0.2
        d = S.snapshot()
        upd = {}
        # battery slow drain
        upd["battery_v"] = round(max(11.0, 12.9 - t * 0.0005), 2)
        upd["battery_pct"] = max(0, int((upd["battery_v"] - 11.0) / (12.9 - 11.0) * 100))
        SPD = 1.4; STEP = SPD * 0.2                      # cruise m/s, metres/tick
        # --- simulated sensor suite (always live so UI gauges have data) ---
        roll = round(8*math.sin(t*0.07), 1)
        pitch = round(6*math.sin(t*0.05 + 1.0), 1)
        if (int(t) % 53) < 4: roll = round(roll + 11, 1)             # occasional steep side-slope
        overhead = 1.35 if (int(t) % 47) < 2 else 5.0               # occasional low tree limb
        upd.update(roll=roll, pitch=pitch, slope=safety.slope_of(roll, pitch),
                   overhead_m=round(overhead, 2))                   # obstacle now comes from vision.py
        upd["fence_breach"] = safety.fence_breach(d)                # live geofence status for the UI
        # --- powertrain + attachment dynamics ---
        if d["engine"] == "crank":
            upd.update(engine="run", engine_rpm=2800, choke=max(0.0, d["choke"] - 0.5),
                       msg="engine running")
        tires = {k: round(v + random.gauss(0, 0.02), 2) for k, v in d["tires"].items()}
        upd["tires"] = tires
        upd["tire_warnings"] = attachments.tpms_warnings(tires)
        bag = dict(d["bagger"])
        if bag.get("attached"):
            if bag.get("state") in ("raising", "dumping", "lowering"):
                bag["t"] = bag.get("t", 0.0) + 0.2
                if bag["state"] == "raising" and bag["t"] >= attachments.DUMP_RAISE_S:
                    bag.update(state="dumping", t=0.0)
                elif bag["state"] == "dumping" and bag["t"] >= attachments.DUMP_HOLD_S:
                    bag.update(state="lowering", t=0.0, fill_pct=0.0)
                elif bag["state"] == "lowering" and bag["t"] >= attachments.DUMP_LOWER_S:
                    bag.update(state="idle", t=0.0)
                    upd["msg"] = "bagger: bins emptied ✓"
            else:
                bag["fill_pct"] = attachments.bagger_fill_step(
                    bag.get("fill_pct", 0.0), d["blade"], d.get("grass_pct"), 0.2)
            upd["bagger"] = bag
        spr = dict(d["sprayer"])
        if spr.get("attached") and spr.get("spraying"):
            turn_rate = abs(d["heading"] - getattr(sim_loop, "_last_hdg", d["heading"])) / 0.2
            if turn_rate > 180 / 0.2: turn_rate = 0                    # wrap
            duty = attachments.sprayer_duty(d["speed"], turn_rate)
            spr["pump_duty"] = duty
            used = duty * attachments.PUMP_MAX_LPM * (0.2 / 60.0)
            spr["applied_l"] = round(spr.get("applied_l", 0.0) + used, 3)
            spr["tank_pct"] = max(0.0, round(spr["tank_pct"] - used / 113.6 * 100, 3))  # 30 gal = 113.6 L
            upd["sprayer"] = spr
        sim_loop._last_hdg = d["heading"]

        if d["mission"] == "running":                                # engine-hour meter (sim: runs while mowing)
            upd["engine_hours"] = round(d["engine_hours"] + 0.2/3600.0, 4)
            upd.update(oil_due_h=round(d.get("_last_oil_h",0.0)+OIL_INTERVAL_H-upd["engine_hours"],1),
                       blade_due_h=round(d.get("_last_blade_h",0.0)+BLADE_INTERVAL_H-upd["engine_hours"],1))
            if int(t*5) % 150 == 0: _save_service({**d, **upd})

        if d["mission"] == "running":
            allow, reason = safety.evaluate({**d, **upd})            # incline/overhead/obstacle/estop
            if not allow:
                upd.update(speed=0.0, msg=reason)                    # software safety HOLD
            elif S.active_route and S.route_idx < len(S.active_route):
                tgt = S.active_route[S.route_idx]
                lat, lon, hdg, reached = missions.step_towards(d["lat"], d["lon"], tgt, STEP)
                # model RTK fix noise (~1.5 cm sigma) so tracking numbers are honest
                lat = round(lat + random.gauss(0, 0.015)/111320.0, 8)
                lon = round(lon + random.gauss(0, 0.015)/(111320.0*math.cos(math.radians(lat))), 8)
                prev = S.active_route[S.route_idx-1] if S.route_idx > 0 else [d["lat"], d["lon"]]
                upd.update(lat=lat, lon=lon, heading=hdg, speed=SPD,
                           xte_m=missions.cross_track_m([lat, lon], prev, tgt),
                           progress=round(S.route_idx / len(S.active_route) * 100))
                if reached:
                    S.route_idx += 1
                    if S.route_idx >= len(S.active_route):
                        upd.update(mission="idle", speed=0.0, progress=100, msg="mission complete ✓")
                        S.active_route = []
            else:                                                    # manual start, no route → wander
                upd.update(speed=SPD, heading=round((d["heading"]+2) % 360, 1))
                hx = math.cos(math.radians(d["heading"]))
                upd.update(lat=round(d["lat"]+hx*1e-6, 7), lon=round(d["lon"]+1e-6, 7))
        elif d["mission"] == "teaching":
            hdg = (d["heading"] + math.sin(t*0.3)*6) % 360   # operator-ish wander
            hx, hy = math.sin(math.radians(hdg)), math.cos(math.radians(hdg))
            mlat = 111320.0; mlon = 111320.0*math.cos(math.radians(d["lat"]))
            lat = round(d["lat"] + hy*STEP/mlat, 7); lon = round(d["lon"] + hx*STEP/mlon, 7)
            upd.update(lat=lat, lon=lon, heading=round(hdg, 1), speed=1.0)
            if int(t*5) % 5 == 0:                        # record ~1 pt/sec
                S.recording.append([lat, lon]); upd["taught_points"] = len(S.recording)
        else:
            upd.update(speed=0.0)                 # vision.py owns obstacle/obstacle_range
        obstacle_log(d.get("obstacle"), {**d, **upd})
        S.update(**upd)
        if RECORD:
            try: RECORD.write(json.dumps(S.snapshot()) + "\n"); RECORD.flush()
            except OSError: pass
        time.sleep(0.2)

RECORD = None          # --record FILE: JSONL of every sim tick (deterministic replay)

def replay_loop(path):
    """--replay FILE: feed recorded snapshots instead of the sim (loops)."""
    while True:
        try:
            with open(path) as f:
                for line in f:
                    try: S.update(**json.loads(line))
                    except (json.JSONDecodeError, TypeError): continue
                    time.sleep(0.2)
        except OSError:
            time.sleep(1)

# ---------------------------------------------------------------- camera feeds
def _camera_svg(name, s):
    """Synthetic camera frame (sim): horizon tilts with roll; overlays obstacle &
    low-branch. Real hardware replaces this route with an MJPEG stream (picamera2)."""
    W, H = 320, 180
    roll = s.get("roll", 0) * (1 if name == "front" else -1)
    front = name == "front"
    obstacle = s.get("obstacle") and front
    low = front and (s.get("overhead_m", 9) or 9) < safety.MIN_OVERHEAD_M
    ox = W/2 + 40*math.sin(s.get("heading", 0)*0.03)
    label = name.upper()
    rec = '<circle cx="294" cy="16" r="5" fill="#e5504a"/><text x="285" y="20" text-anchor="end" fill="#e5504a" font-size="10" font-family="monospace">REC</text>'
    obs = f'<rect x="{ox-34}" y="92" width="68" height="48" fill="none" stroke="#e5504a" stroke-width="3" rx="4"/><text x="{ox}" y="86" text-anchor="middle" fill="#e5504a" font-size="11" font-family="monospace">OBSTACLE</text>' if obstacle else ''
    branch = '<rect x="0" y="0" width="320" height="26" fill="#5a3a1c" opacity=".85"/><text x="160" y="18" text-anchor="middle" fill="#ffd9a6" font-size="12" font-family="monospace">LOW BRANCH — STOP</text>' if low else ''
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<defs><linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#1b2735"/><stop offset="1" stop-color="#27333f"/></linearGradient></defs>
<rect width="{W}" height="{H}" fill="url(#sky)"/>
<g transform="rotate({-roll} {W/2} {H/2})">
  <rect x="-80" y="{H/2}" width="{W+160}" height="{H}" fill="#1d2c1d"/>
  <line x1="-80" y1="{H/2}" x2="{W+80}" y2="{H/2}" stroke="#4a7a4a" stroke-width="2" opacity=".7"/>
  <line x1="{W*0.35}" y1="{H/2}" x2="{W*0.42}" y2="{H}" stroke="#2f4a2f" stroke-width="2"/>
  <line x1="{W*0.65}" y1="{H/2}" x2="{W*0.58}" y2="{H}" stroke="#2f4a2f" stroke-width="2"/>
</g>
<line x1="{W/2-9}" y1="{H/2}" x2="{W/2+9}" y2="{H/2}" stroke="#7fd6ff" stroke-width="1.5" opacity=".6"/>
<line x1="{W/2}" y1="{H/2-9}" x2="{W/2}" y2="{H/2+9}" stroke="#7fd6ff" stroke-width="1.5" opacity=".6"/>
{obs}{branch}
<text x="10" y="170" fill="#cdd6df" font-size="11" font-family="monospace">{label}</text>
<text x="310" y="170" text-anchor="end" fill="#9fb0c0" font-size="11" font-family="monospace">tilt {s.get("slope",0):.0f}°</text>
{rec}</svg>'''

# ---------------------------------------------------------------- http handler
class H(BaseHTTPRequestHandler):
    def log_message(self, *a): pass     # quiet

    def _send(self, code, body, ctype="application/json"):
        b = body.encode() if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(b)

    def _serve_static(self, urlpath):
        # serve files under ui/ (e.g. /vendor/leaflet/*), path-traversal safe
        rel = urlpath.lstrip("/").split("?")[0]
        root = os.path.realpath(UI_DIR)
        full = os.path.realpath(os.path.join(root, rel))
        if not full.startswith(root + os.sep) or not os.path.isfile(full):
            self._send(404, "not found"); return
        ext = os.path.splitext(full)[1].lower()
        ctype = {".js": "application/javascript", ".css": "text/css",
                 ".png": "image/png", ".svg": "image/svg+xml"}.get(ext, "application/octet-stream")
        with open(full, "rb") as f:
            self._send(200, f.read(), ctype)

    def do_GET(self):
        if self.path == "/" or self.path == "/index.html":
            try:
                with open(os.path.join(UI_DIR, "index.html"), "rb") as f:
                    self._send(200, f.read(), "text/html; charset=utf-8")
            except FileNotFoundError:
                self._send(404, "ui/index.html not found")
            return
        if self.path.startswith("/vendor/"):
            return self._serve_static(self.path)
        if self.path.startswith("/camera/"):
            name = self.path.split("/")[-1].split(".")[0].split("?")[0]
            if name not in ("front", "rear"):           # allowlist — name flows into SVG output
                self._send(404, "unknown camera"); return
            self._send(200, _camera_svg(name, S.snapshot()), "image/svg+xml"); return
        if self.path == "/api/state":
            self._send(200, json.dumps(S.snapshot())); return
        if self.path == "/api/missions":
            self._send(200, json.dumps(missions.list_routes())); return
        if self.path == "/api/obstacles":
            try:
                with open(_obstacles_path()) as f: hits = json.load(f)
            except (FileNotFoundError, json.JSONDecodeError, OSError): hits = []
            self._send(200, json.dumps(hits)); return
        if self.path.startswith("/api/route.plan"):
            from urllib.parse import urlparse, parse_qs
            rid = parse_qs(urlparse(self.path).query).get("id", [""])[0]
            r = missions.get_route(rid)
            if not r: self._send(404, json.dumps({"error": "not found"})); return
            self._send(200, json.dumps(missions.to_qgc_plan(r["points"])),
                       "application/json"); return
        if self.path.startswith("/api/route"):
            from urllib.parse import urlparse, parse_qs
            rid = parse_qs(urlparse(self.path).query).get("id", [""])[0]
            r = missions.get_route(rid)
            self._send(200 if r else 404, json.dumps(r or {"error": "not found"})); return
        if self.path == "/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            q = S.subscribe()
            try:
                self.wfile.write(("data: " + json.dumps(S.snapshot()) + "\n\n").encode())
                self.wfile.flush()
                while True:
                    try: msg = q.get(timeout=15)
                    except queue.Empty: msg = ": keepalive\n\n"
                    self.wfile.write(msg.encode()); self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError):
                pass
            finally:
                S.unsubscribe(q)
            return
        self._send(404, "not found")

    def do_POST(self):
        n = int(self.headers.get("Content-Length", 0))
        try:
            p = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            self._send(400, json.dumps({"ok": False, "msg": "bad json"})); return

        if self.path == "/api/command":
            cmd, args = p.get("cmd", ""), p.get("args")
            ok, msg = handle_command(cmd, args)          # companion-side logic + optimistic UI
            if S.mav_cmd and cmd in ("arm", "disarm", "mode", "start", "resume", "pause", "estop", "clear_estop"):
                try: S.mav_cmd(cmd, args)                # forward drive cmds to ArduPilot (SITL/Pixhawk)
                except Exception as e: msg += f" [mav: {e}]"
            if S.mav_cmd and ok and cmd == "run_route" and S.active_route:
                try: S.mav_cmd("upload_run", {"points": S.active_route})   # → AUTO mission upload
                except Exception as e: msg += f" [mav: {e}]"
            self._send(200 if ok else 409, json.dumps({"ok": ok, "msg": msg})); return

        if self.path == "/api/zones/plan":
            try:
                planner = missions.plan_coverage_turns if p.get("turns") == "smooth" else missions.plan_coverage
                rid, pts = planner(p.get("name"), p.get("polygon", []),
                                   float(p.get("spacing") or missions.DEFAULT_SPACING))
                self._send(200, json.dumps({"ok": True, "id": rid, "points": pts,
                                            "msg": f"planned {len(pts)} waypoints"}))
            except Exception as e:
                self._send(409, json.dumps({"ok": False, "msg": str(e)}))
            return

        if self.path == "/api/missions/delete":
            missions.delete_route(p.get("id", ""))
            self._send(200, json.dumps({"ok": True, "msg": "deleted"})); return

        if self.path == "/api/service/reset":
            ok, msg = reset_service(p.get("item", ""))
            self._send(200 if ok else 409, json.dumps({"ok": ok, "msg": msg})); return

        if self.path == "/api/missions/import-plan":
            pts = missions.from_qgc_plan(p.get("plan") or p)
            if len(pts) < 2:
                self._send(409, json.dumps({"ok": False, "msg": "no waypoints in plan"})); return
            rid = missions.add_taught(p.get("name") or "Imported .plan", pts)
            self._send(200, json.dumps({"ok": True, "id": rid, "msg": f"imported {len(pts)} wpts"})); return

        if self.path == "/api/fence":
            ok, msg = set_fence(p.get("polygon", []))
            if S.mav_cmd and ok:
                try: S.mav_cmd("fence", {"points": S.snapshot()["fence"]})   # push to ArduPilot fence
                except Exception as e: msg += f" [mav: {e}]"
            self._send(200 if ok else 409, json.dumps({"ok": ok, "msg": msg})); return

        self._send(404, json.dumps({"ok": False, "msg": "not found"}))

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--sim", action="store_true", default=True)
    ap.add_argument("--mav", help="MAVLink endpoint, e.g. udp:127.0.0.1:14550 (needs pymavlink)")
    ap.add_argument("--vision-hef", help="Hailo .hef model for real camera detection (else sim)")
    ap.add_argument("--weather", action="store_true", help="rain-hold gate via open-meteo (needs internet)")
    ap.add_argument("--record", help="write every sim tick to FILE (JSONL) for deterministic replay")
    ap.add_argument("--replay", help="feed recorded JSONL instead of the sim")
    args = ap.parse_args()

    global RECORD
    if args.record:
        RECORD = open(args.record, "a")
        print(f"[companion] recording ticks -> {args.record}")
    if args.replay:
        threading.Thread(target=replay_loop, args=(args.replay,), daemon=True).start()
        print(f"[companion] REPLAY mode <- {args.replay}")
    elif args.mav:
        # Real / SITL path lives in mav.py — kept optional so --sim runs dependency-free.
        try:
            from mav import run_mavlink
            threading.Thread(target=run_mavlink, args=(args.mav, S, handle_command),
                             daemon=True).start()
            print(f"[companion] MAVLink mode → {args.mav}")
        except Exception as e:
            print(f"[companion] MAVLink unavailable ({e}); falling back to sim")
            threading.Thread(target=sim_loop, daemon=True).start()
    else:
        threading.Thread(target=sim_loop, daemon=True).start()
        print("[companion] SIM mode (no hardware)")

    if args.weather:
        threading.Thread(target=weather_loop, daemon=True).start()
        print("[companion] weather gate armed (open-meteo)")

    # camera-AI vision loop (sim detector unless a Hailo .hef is supplied)
    threading.Thread(target=vision.run_vision,
                     args=(S, vision.make_detector(args.vision_hef)), daemon=True).start()

    srv = ThreadingHTTPServer(("0.0.0.0", args.port), H)
    print(f"[companion] open  http://localhost:{args.port}/   (on iPad: http://<this-mac-LAN-ip>:{args.port}/ )")
    srv.serve_forever()

if __name__ == "__main__":
    main()
