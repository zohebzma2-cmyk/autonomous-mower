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

UI_DIR = os.path.join(os.path.dirname(__file__), "..", "ui")

# ---------------------------------------------------------------- shared state
class State:
    def __init__(self):
        self.lock = threading.Lock()
        self.subscribers = []                  # list[queue.Queue] for SSE fan-out
        self.t0 = None                         # set lazily (no Date.now at import)
        self.d = dict(
            connected=True, mode="MANUAL", armed=False, mission="idle",
            blade=False, estop=False,
            gps_fix="rtk_fixed", sats=22, hdop=0.6,
            battery_v=12.9, battery_pct=92, speed=0.0, heading=0.0,
            lat=42.8062, lon=-71.3673,          # Windham NH-ish
            obstacle=False, obstacle_range=None,
            mode_options=["MANUAL", "HOLD", "AUTO"],
            taught_points=0, msg="sim: ready",
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
def handle_command(cmd, args):
    """Apply a control command to state. Returns (ok, message)."""
    d = S.snapshot()
    if cmd == "estop":
        S.update(estop=True, blade=False, armed=False, mode="HOLD",
                 mission="idle", speed=0.0, msg="E-STOP — drive + blade killed")
        return True, "E-STOP engaged"
    if d["estop"] and cmd != "clear_estop":
        return False, "E-STOP is engaged — clear it first"
    if cmd == "clear_estop":
        S.update(estop=False, msg="e-stop cleared (still disarmed)")
        return True, "cleared"
    if cmd == "arm":
        if d["gps_fix"] not in ("rtk_fixed", "rtk_float", "3d"):
            return False, "no GPS fix — refusing to arm"
        S.update(armed=True, msg="armed")
        return True, "armed"
    if cmd == "disarm":
        S.update(armed=False, mission="idle", speed=0.0, blade=False, msg="disarmed")
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
        S.update(mission="teaching", taught_points=0, msg="teach: recording path")
        return True, "teaching"
    if cmd == "teach_stop":
        S.update(mission="idle", msg=f"teach: saved {d['taught_points']} pts")
        return True, "saved"
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
        # motion when running a mission
        if d["mission"] == "running" and not d["estop"]:
            spd = 1.4                                   # m/s
            # occasional simulated obstacle → safety stop
            obstacle = (int(t) % 37) in (0, 1, 2)
            if obstacle:
                upd.update(obstacle=True, obstacle_range=round(1.2 + 0.5*math.sin(t), 2),
                           speed=0.0, msg="LiDAR: obstacle — holding")
            else:
                upd.update(obstacle=False, obstacle_range=None, speed=spd)
                upd["heading"] = round((d["heading"] + 2) % 360, 1)
                # creep the position along heading
                hx = math.cos(math.radians(d["heading"]))
                upd["lat"] = round(d["lat"] + hx * 1e-6, 7)
                upd["lon"] = round(d["lon"] + 1e-6, 7)
        elif d["mission"] == "teaching":
            upd["taught_points"] = d["taught_points"] + 1
            upd["speed"] = 1.0
        else:
            upd["speed"] = 0.0
            upd["obstacle"] = False
        S.update(**upd)
        time.sleep(0.2)

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
        if self.path == "/api/state":
            self._send(200, json.dumps(S.snapshot())); return
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
        if self.path != "/api/command":
            self._send(404, "not found"); return
        n = int(self.headers.get("Content-Length", 0))
        try:
            payload = json.loads(self.rfile.read(n) or b"{}")
        except json.JSONDecodeError:
            self._send(400, json.dumps({"ok": False, "msg": "bad json"})); return
        ok, msg = handle_command(payload.get("cmd", ""), payload.get("args"))
        self._send(200 if ok else 409, json.dumps({"ok": ok, "msg": msg}))

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
