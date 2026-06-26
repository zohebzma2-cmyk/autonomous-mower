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

# ArduPilot Rover mode numbers (custom_mode)
ROVER_MODES = {"MANUAL": 0, "HOLD": 4, "AUTO": 10, "GUIDED": 15, "RTL": 11}
FIX_NAME = {0: "no", 1: "no", 2: "2d", 3: "3d", 4: "dgps", 5: "rtk_float", 6: "rtk_fixed"}

MAV_FRAME_GLOBAL_REL_ALT = 3
MAV_CMD_NAV_WAYPOINT = 16


def to_mission_items(waypoints):
    """PURE (unit-tested). [[lat,lon],...] → mission-item dicts for MISSION_ITEM_INT
    (NAV_WAYPOINT). lat/lon are scaled to 1e7 ints as MAVLink requires."""
    items = []
    for i, (lat, lon) in enumerate(waypoints):
        items.append(dict(seq=i, frame=MAV_FRAME_GLOBAL_REL_ALT, command=MAV_CMD_NAV_WAYPOINT,
                          current=1 if i == 0 else 0, autocontinue=1,
                          lat=int(round(lat * 1e7)), lon=int(round(lon * 1e7)), alt=0.0))
    return items


def upload_mission(m, waypoints, timeout=5):
    """Push a route to ArduPilot via the MAVLink mission protocol (SITL/Pixhawk)."""
    items = to_mission_items(waypoints)
    if not items:
        return False
    m.mav.mission_count_send(m.target_system, m.target_component, len(items))
    for _ in range(len(items)):
        req = m.recv_match(type=["MISSION_REQUEST_INT", "MISSION_REQUEST"], blocking=True, timeout=timeout)
        if req is None:
            return False
        it = items[req.seq]
        m.mav.mission_item_int_send(m.target_system, m.target_component, it["seq"], it["frame"],
            it["command"], it["current"], it["autocontinue"], 0, 0, 0, 0,
            it["lat"], it["lon"], it["alt"])
    ack = m.recv_match(type="MISSION_ACK", blocking=True, timeout=timeout)
    return ack is not None


def run_mavlink(endpoint, S, _handle_command):
    from pymavlink import mavutil

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
            if upload_mission(m, pts):
                set_mode("AUTO")
                m.mav.command_long_send(m.target_system, m.target_component,
                    mavutil.mavlink.MAV_CMD_MISSION_START, 0, 0, 0, 0, 0, 0, 0, 0)
        # blade / GPIO relay → wired to the safety MCU on the real build

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
        if t == "HEARTBEAT":
            S.update(connected=True,
                     armed=bool(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED),
                     mode=next((k for k, v in ROVER_MODES.items() if v == msg.custom_mode), str(msg.custom_mode)))
        elif t == "GPS_RAW_INT":
            S.update(gps_fix=FIX_NAME.get(msg.fix_type, "no"), sats=msg.satellites_visible,
                     hdop=round(msg.eph / 100.0, 2))
        elif t == "GLOBAL_POSITION_INT":
            S.update(lat=msg.lat / 1e7, lon=msg.lon / 1e7, heading=msg.hdg / 100.0)
        elif t == "VFR_HUD":
            S.update(speed=round(msg.groundspeed, 1))
        elif t == "SYS_STATUS":
            S.update(battery_v=round(msg.voltage_battery / 1000.0, 2),
                     battery_pct=max(0, msg.battery_remaining))
        elif t == "STATUSTEXT":
            S.update(msg=msg.text)
