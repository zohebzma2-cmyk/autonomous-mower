#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""End-to-end smoke test against ArduPilot SITL through the companion's own HTTP API.

Assumes `scripts/sitl.sh` is running (UI on :8080). Proves the whole chain the real
machine uses: UI command -> companion -> MAVLink -> ArduPilot firmware -> telemetry back.
  1. link up, RTK-grade GPS, home on the Yard field
  2. a geofence drawn around the Yard uploads to the firmware (FENCE_TYPE includes polygon,
     so ArduPilot refuses to arm without one); arm is accepted once the EKF has a position
  3. run the saved coverage route: mission uploads, AUTO engages, the rover moves
     at the configured cruise speed and its position changes
  4. E-STOP: the firmware disarms and HOLDs, the rover stops
Exit 0 = pass. Stdlib only.
"""
import json
import sys
import time
import urllib.request

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8080"


def state():
    with urllib.request.urlopen(f"{BASE}/api/state", timeout=5) as r:
        return json.load(r)


def cmd(name, args=None):
    body = json.dumps({"cmd": name, "args": args}).encode()
    req = urllib.request.Request(f"{BASE}/api/command", body, {"content-type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:           # 409 = refused by companion logic
        return json.load(e)


def wait_for(pred, what, timeout=60):
    end = time.time() + timeout
    while time.time() < end:
        s = state()
        if pred(s):
            print(f"  ok  {what}")
            return s
        time.sleep(0.5)
    raise SystemExit(f"FAIL {what} — last state: { {k: s.get(k) for k in ('mode', 'armed', 'mission', 'speed', 'msg')} }")


def main():
    print(f"== SITL smoke via {BASE}")
    s = wait_for(lambda s: s.get("connected") and s.get("gps_fix") in ("3d", "rtk_float", "rtk_fixed")
                 and abs(s.get("lat", 0) - 42.8062) < 0.001, "MAVLink link, GPS fix, home on the Yard", 90)
    with urllib.request.urlopen(f"{BASE}/api/missions", timeout=5) as r:
        routes = json.load(r)
    routes = routes["routes"] if isinstance(routes, dict) else routes
    rid = routes[0]["id"]

    fence = [[42.8058, -71.3678], [42.8058, -71.3667], [42.8066, -71.3667], [42.8066, -71.3678]]
    req = urllib.request.Request(f"{BASE}/api/fence", json.dumps({"polygon": fence}).encode(),
                                 {"content-type": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        assert json.load(r)["ok"], "FAIL fence rejected by the companion"
    wait_for(lambda s: s.get("fence_synced") is True, "geofence uploaded to the firmware (protocol ACK)", 20)

    cmd("engine_start")
    wait_for(lambda s: s.get("engine") == "run", "engine running (companion ignition sequence)", 30)
    end = time.time() + 120                      # SITL's EKF needs ~40 s for a position estimate
    while not state().get("armed"):
        if time.time() > end:
            raise SystemExit(f"FAIL firmware never armed — last: {state().get('msg')}")
        cmd("arm")
        time.sleep(3)
    print("  ok  firmware ARMED (heartbeat, not the companion's word for it)")

    # AUTO needs the EKF on GPS (~35 s after boot in SITL); until then the firmware refuses it
    # and the companion reports "AUTO refused" — press Run again, like an operator would.
    end = time.time() + 120
    while True:
        print("  ..  run_route:", cmd("run_route", {"id": rid}))
        try:
            start = wait_for(lambda s: s.get("mode") == "AUTO" and s.get("speed", 0) >= 0.5,
                             "mission uploaded, AUTO engaged, rover moving", 12)
            break
        except SystemExit as e:
            if time.time() > end:
                raise
            print(f"  ..  not yet ({state().get('msg')}) — retrying")
    time.sleep(8)
    s = state()
    moved = abs(s["lat"] - start["lat"]) + abs(s["lon"] - start["lon"])
    assert moved > 2e-5, f"FAIL rover did not move (Δ={moved:.2e} deg)"
    assert s["speed"] <= 1.6, f"FAIL speed {s['speed']} m/s above the configured cruise (≤1.4 + margin)"
    print(f"  ok  following the route at {s['speed']} m/s ({moved * 111320:.1f} m in 8 s)")

    cmd("estop")
    wait_for(lambda s: not s.get("armed") and s.get("mode") == "HOLD" and s.get("speed", 1) <= 0.2,
             "E-STOP: firmware disarmed + HOLD, rover stopped", 30)
    cmd("clear_estop")
    print("SITL SMOKE PASSED")


if __name__ == "__main__":
    main()
