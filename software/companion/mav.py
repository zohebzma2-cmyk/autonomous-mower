# SPDX-License-Identifier: MIT
"""
MAVLink bridge — connects the companion UI to ArduPilot Rover (SITL or real Pixhawk).
Kept separate from app.py so `--sim` runs dependency-free. Enable with:
    python3 app.py --mav udp:127.0.0.1:14550     # SITL
    python3 app.py --mav /dev/serial0            # Pixhawk TELEM (Pi)
Needs: pip install pymavlink   (see requirements.txt / dev/SITL.md)

This is a working skeleton: it streams real telemetry into the shared State and maps
the UI's commands to MAVLink. Mission record/upload (teach-and-repeat) and the LiDAR
safety override are wired as TODOs against the same command surface.
"""
import time

from safety import slope_of

# ArduPilot Rover mode numbers (custom_mode)
ROVER_MODES = {"MANUAL": 0, "HOLD": 4, "AUTO": 10, "GUIDED": 15, "RTL": 11}
FIX_NAME = {0: "no", 1: "no", 2: "2d", 3: "3d", 4: "dgps", 5: "rtk_float", 6: "rtk_fixed"}

MAV_FRAME_GLOBAL_REL_ALT = 3
MAV_CMD_NAV_WAYPOINT = 16


def to_mission_items(waypoints):
    """PURE (unit-tested). [[lat,lon],...] → mission-item dicts for MISSION_ITEM_INT.
    ArduPilot reserves seq 0 for HOME (it overwrites it with the real home on upload),
    so seq 0 is a placeholder at the first waypoint and the route starts at seq 1.
    lat/lon are scaled to 1e7 ints as MAVLink requires."""
    if not waypoints:
        return []
    items = []
    for i, (lat, lon) in enumerate([waypoints[0]] + list(waypoints)):
        items.append(dict(seq=i, frame=MAV_FRAME_GLOBAL_REL_ALT, command=MAV_CMD_NAV_WAYPOINT,
                          current=0, autocontinue=1,
                          lat=int(round(lat * 1e7)), lon=int(round(lon * 1e7)), alt=0.0))
    return items


MAV_CMD_NAV_FENCE_POLYGON_VERTEX_INCLUSION = 5001
MAV_FRAME_GLOBAL = 0
MISSION_TYPE_MISSION, MISSION_TYPE_FENCE = 0, 1


def to_fence_items(polygon):
    """PURE (unit-tested). [[lat,lon],...] → inclusion-polygon vertices for the FENCE
    mission type. param1 = vertex count (ArduPilot groups vertices into one polygon by it)."""
    n = len(polygon)
    if n < 3:
        return []
    return [dict(seq=i, frame=MAV_FRAME_GLOBAL, command=MAV_CMD_NAV_FENCE_POLYGON_VERTEX_INCLUSION,
                 current=0, autocontinue=0, p1=float(n),
                 lat=int(round(lat * 1e7)), lon=int(round(lon * 1e7)), alt=0.0)
            for i, (lat, lon) in enumerate(polygon)]


def upload_items(m, items, replies, mission_type=MISSION_TYPE_MISSION, timeout=5):
    """MAVLink mission protocol (MISSION / FENCE): COUNT, then answer each request, then ACK.
    `replies` is a queue the telemetry pump feeds with MISSION_REQUEST(_INT)/MISSION_ACK:
    the pump owns recv_match, so reading the link here would race it and lose requests."""
    import queue
    if not items:
        return False
    while not replies.empty():                    # drop stale replies from an earlier upload
        replies.get_nowait()
    m.mav.mission_count_send(m.target_system, m.target_component, len(items), mission_type)
    sent = set()
    while True:
        try:
            msg = replies.get(timeout=timeout)
        except queue.Empty:
            return False
        if getattr(msg, "mission_type", mission_type) != mission_type:
            continue                              # a reply for the other list type
        if msg.get_type() == "MISSION_ACK":
            return msg.type == 0 and len(sent) == len(items)    # MAV_MISSION_ACCEPTED
        it = items[msg.seq]
        m.mav.mission_item_int_send(m.target_system, m.target_component, it["seq"], it["frame"],
            it["command"], it["current"], it["autocontinue"], it.get("p1", 0.0), 0, 0, 0,
            it["lat"], it["lon"], it["alt"], mission_type)
        sent.add(msg.seq)


def upload_mission(m, waypoints, replies, timeout=5):
    """Push a route to ArduPilot (SITL/Pixhawk) as the AUTO mission."""
    return upload_items(m, to_mission_items(waypoints), replies, MISSION_TYPE_MISSION, timeout)


def run_mavlink(endpoint, S, _handle_command):
    import queue
    from pymavlink import mavutil

    mission_replies = queue.Queue()               # pump -> upload_mission (single link reader)
    S.update(connected=False, msg=f"connecting {endpoint}…")
    m = mavutil.mavlink_connection(endpoint, autoreconnect=True)
    m.wait_heartbeat()
    S.update(connected=True, msg="MAVLink link up")

    # request data streams
    m.mav.request_data_stream_send(m.target_system, m.target_component,
                                   mavutil.mavlink.MAV_DATA_STREAM_ALL, 5, 1)

    # ---- bind the UI command surface to MAVLink ----
    def cmd(cmd, args=None):
        args = args or {}
        if cmd == "arm":
            m.arducopter_arm()
        elif cmd in ("disarm", "estop"):
            m.arducopter_disarm()
            if cmd == "estop":
                set_mode("HOLD")
                # TODO: also drop the blade relay via the safety MCU / GPIO
        elif cmd == "mode":
            set_mode(args.get("mode", "MANUAL"))
        elif cmd in ("start", "resume"):
            set_mode("AUTO")
            m.mav.command_long_send(m.target_system, m.target_component,
                mavutil.mavlink.MAV_CMD_MISSION_START, 0, 0, 0, 0, 0, 0, 0, 0)
        elif cmd == "pause":
            set_mode("HOLD")
        elif cmd == "upload_run":                     # teach/coverage route → AUTO mission
            pts = args.get("points") or []
            # HOLD first: writing items while AUTO is running makes ArduPilot restart the
            # current command on every item ("Auto mission changed" x N) — seen in SITL
            set_mode("HOLD")
            ok = upload_mission(m, pts, mission_replies)
            S.update(msg=f"mission uploaded ({len(pts)} wpts)" if ok else "mission upload FAILED — staying in HOLD")
            if ok:
                set_mode("AUTO")
                m.mav.command_long_send(m.target_system, m.target_component,
                    mavutil.mavlink.MAV_CMD_MISSION_START, 0, 0, 0, 0, 0, 0, 0, 0)
                confirm_auto()
        elif cmd == "fence":                          # geofence polygon → ArduPilot inclusion fence
            ok = upload_items(m, to_fence_items(args.get("points") or []), mission_replies,
                              MISSION_TYPE_FENCE)
            S.update(fence_synced=ok, msg="fence uploaded to autopilot" if ok else "fence upload FAILED")
        # blade / GPIO relay → wired to the safety MCU on the real build

    def confirm_auto(timeout=4.0):
        """The firmware can refuse AUTO (e.g. no EKF position yet: 'Flight mode change failed').
        Don't let the UI claim a running mission it isn't flying: watch the heartbeat."""
        import threading
        def watch():
            end = time.time() + timeout
            while time.time() < end:
                if S.snapshot().get("mode") == "AUTO":
                    return
                time.sleep(0.2)
            S.active_route = []
            S.update(mission="idle", msg="AUTO refused by the autopilot (no position estimate yet?) — mission not started")
        threading.Thread(target=watch, daemon=True).start()

    def set_mode(name):
        mode_id = ROVER_MODES.get(name)
        if mode_id is None:
            return
        m.mav.set_mode_send(m.target_system,
            mavutil.mavlink.MAV_MODE_FLAG_CUSTOM_MODE_ENABLED, mode_id)

    S.mav_cmd = cmd     # app.py can route POSTs here when in --mav mode (TODO hook)

    # ---- telemetry pump ----
    while True:
        msg = m.recv_match(blocking=True, timeout=5)
        if msg is None:
            S.update(connected=False, msg="link timeout"); continue
        t = msg.get_type()
        if t in ("MISSION_REQUEST_INT", "MISSION_REQUEST", "MISSION_ACK"):
            mission_replies.put(msg)
        elif t == "HEARTBEAT":
            S.update(connected=True,
                     armed=bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED),
                     mode=next((k for k, v in ROVER_MODES.items() if v == msg.custom_mode), str(msg.custom_mode)))
        elif t == "GPS_RAW_INT":
            S.update(gps_fix=FIX_NAME.get(msg.fix_type, "no"), sats=msg.satellites_visible,
                     hdop=round(msg.eph / 100.0, 2))
        elif t == "GLOBAL_POSITION_INT":
            S.update(lat=msg.lat / 1e7, lon=msg.lon / 1e7, heading=msg.hdg / 100.0)
        elif t == "ATTITUDE":                   # real IMU -> the slope / rollover gate in safety.py
            import math
            roll, pitch = round(math.degrees(msg.roll), 1), round(math.degrees(msg.pitch), 1)
            S.update(roll=roll, pitch=pitch, slope=slope_of(roll, pitch))
        elif t == "VFR_HUD":
            S.update(speed=round(msg.groundspeed, 1))
        elif t == "SYS_STATUS":
            S.update(battery_v=round(msg.voltage_battery / 1000.0, 2),
                     battery_pct=max(0, msg.battery_remaining))
        elif t == "STATUSTEXT":
            S.update(msg=msg.text)
