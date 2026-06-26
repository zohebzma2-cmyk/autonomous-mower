#!/usr/bin/env python3
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
import argparse, json, os, threading, time, math, queue
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import missions, safety

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
            lat=42.8062, lon=-71.3673,          # Windham NH-ish
            obstacle=False, obstacle_range=None,
            roll=0.0, pitch=0.0, slope=0.0,     # IMU tilt (deg) → incline safety
            overhead_m=5.0,                     # upward sensor: branch clearance (m)
            cameras=["front", "rear"],          # camera feeds available
            mode_options=["MANUAL", "HOLD", "AUTO"],
            taught_points=0, route_id=None, progress=0,   # active route id + % complete
            msg="sim: ready",
        )

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

S = State()

# ---------------------------------------------------------------- command handling
def handle_command(cmd, args=None):
    """Apply a control command to state. Returns (ok, message)."""
    d = S.snapshot()
    if cmd == "estop":
        S.active_route = []
        S.update(estop=True, blade=False, armed=False, mode="HOLD", mission="idle",
                 speed=0.0, route_id=None, progress=0, msg="E-STOP — drive + blade killed")
        return True, "E-STOP engaged"
    if d["estop"] and cmd != "clear_estop":
        return False, "E-STOP is engaged — clear it first"
    if cmd == "clear_estop":
        S.update(estop=False, msg="e-stop cleared (still disarmed)")
        return True, "cleared"
    if cmd == "arm":
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
        obstacle = (int(t) % 41) < 3
        upd.update(roll=roll, pitch=pitch, slope=safety.slope_of(roll, pitch),
                   overhead_m=round(overhead, 2), obstacle=obstacle,
                   obstacle_range=(round(1.2 + 0.5*math.sin(t), 2) if obstacle else None))

        if d["mission"] == "running":
            allow, reason = safety.evaluate({**d, **upd})            # incline/overhead/obstacle/estop
            if not allow:
                upd.update(speed=0.0, msg=reason)                    # software safety HOLD
            elif S.active_route and S.route_idx < len(S.active_route):
                tgt = S.active_route[S.route_idx]
                lat, lon, hdg, reached = missions.step_towards(d["lat"], d["lon"], tgt, STEP)
                upd.update(lat=lat, lon=lon, heading=hdg, speed=SPD,
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
            upd.update(speed=0.0, obstacle=False)
        S.update(**upd)
        time.sleep(0.2)

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
            self._send(200 if ok else 409, json.dumps({"ok": ok, "msg": msg})); return

        if self.path == "/api/zones/plan":
            try:
                rid, pts = missions.plan_coverage(p.get("name"), p.get("polygon", []),
                                                  float(p.get("spacing") or missions.DEFAULT_SPACING))
                self._send(200, json.dumps({"ok": True, "id": rid, "points": pts,
                                            "msg": f"planned {len(pts)} waypoints"}))
            except Exception as e:
                self._send(409, json.dumps({"ok": False, "msg": str(e)}))
            return

        if self.path == "/api/missions/delete":
            missions.delete_route(p.get("id", ""))
            self._send(200, json.dumps({"ok": True, "msg": "deleted"})); return

        self._send(404, json.dumps({"ok": False, "msg": "not found"}))

# ---------------------------------------------------------------- main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--sim", action="store_true", default=True)
    ap.add_argument("--mav", help="MAVLink endpoint, e.g. udp:127.0.0.1:14550 (needs pymavlink)")
    args = ap.parse_args()

    if args.mav:
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

    srv = ThreadingHTTPServer(("0.0.0.0", args.port), H)
    print(f"[companion] open  http://localhost:{args.port}/   (on iPad: http://<this-mac-LAN-ip>:{args.port}/ )")
    srv.serve_forever()

if __name__ == "__main__":
    main()
