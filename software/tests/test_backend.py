#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""
Backend test suite — pure stdlib (no pytest), matches the companion's zero-dep design.
Run:  python3 tests/test_backend.py      (from software/, or anywhere)
Exits non-zero on any failure.
"""
import os, sys, tempfile, json

HERE = os.path.dirname(os.path.abspath(__file__))
COMP = os.path.join(HERE, "..", "companion")
sys.path.insert(0, COMP)

# isolate persistence to a temp file BEFORE importing app (app imports missions)
import missions
_tmp = tempfile.mkdtemp()
missions.DATA = _tmp
missions.FILE = os.path.join(_tmp, "missions.json")

import app, safety, vision, mav, attachments

SQUARE = [[42.8060, -71.3675], [42.8060, -71.3670],
          [42.8064, -71.3670], [42.8064, -71.3675]]   # ~44m x 41m

def reset():
    app.S = app.State()

# ---------------------------------------------------------------- coverage planner
def test_coverage_rows_fill_polygon():
    rid, pts = missions.plan_coverage("t", SQUARE, spacing=1.15)
    assert len(pts) >= 20, f"too few waypoints: {len(pts)}"
    assert len(pts) % 2 == 0, "rows should yield paired entry/exit points"
    lats = [p[0] for p in pts]; lons = [p[1] for p in pts]
    assert min(lats) >= 42.8060 - 1e-4 and max(lats) <= 42.8064 + 1e-4, "waypoint outside boundary (lat)"
    assert min(lons) >= -71.3675 - 1e-4 and max(lons) <= -71.3670 + 1e-4, "waypoint outside boundary (lon)"
    missions.delete_route(rid)

def test_coverage_is_boustrophedon():
    # each row (entry,exit) pair must reverse travel direction vs the previous row
    _, pts = missions.plan_coverage("t", SQUARE, spacing=2.0)
    rows = [(pts[i], pts[i+1]) for i in range(0, len(pts), 2)]
    dirs = [1 if b[1] >= a[1] else -1 for a, b in rows]      # sign of lon travel
    assert all(dirs[i] != dirs[i+1] for i in range(len(dirs)-1)), \
        f"rows not alternating direction: {dirs}"

def test_coverage_rejects_degenerate():
    try:
        missions.plan_coverage("t", [[0,0],[1,1]])      # <3 points
        assert False, "should reject <3 boundary points"
    except ValueError:
        pass

def test_spacing_controls_density():
    _, fine = missions.plan_coverage("t", SQUARE, spacing=0.8)
    _, coarse = missions.plan_coverage("t", SQUARE, spacing=3.0)
    assert len(fine) > len(coarse), "finer spacing must yield more rows"

# ---------------------------------------------------------------- missions persistence
def test_persistence_roundtrip():
    before = len(missions.list_routes())
    rid = missions.add_taught("My route", [[42.8,-71.3],[42.81,-71.3]])
    got = missions.get_route(rid)
    assert got and got["name"] == "My route" and got["n"] == 2
    assert len(missions.list_routes()) == before + 1
    missions.delete_route(rid)
    assert missions.get_route(rid) is None
    assert len(missions.list_routes()) == before

def test_persistence_survives_reload():
    rid = missions.add_taught("persist", [[1,1],[2,2],[3,3]])
    raw = json.load(open(missions.FILE))                # read straight off disk
    assert any(r["id"] == rid for r in raw["routes"])
    missions.delete_route(rid)

# ---------------------------------------------------------------- nav stepping
def test_step_towards_advances_and_reaches():
    tgt = [42.8010, -71.3670]
    la, lo, hdg, reached = missions.step_towards(42.8000, -71.3670, tgt, 5.0)
    assert not reached and la > 42.8000, "should advance toward target, not reach"
    la, lo, hdg, reached = missions.step_towards(42.80099, -71.3670, tgt, 5.0)
    assert reached and [la, lo] == tgt, "should snap to target when within step"

# ---------------------------------------------------------------- command state machine + safety
def test_arm_requires_gps_fix():
    reset(); app.S.update(gps_fix="no")
    ok, _ = app.handle_command("arm"); assert not ok, "must refuse to arm without GPS"
    app.S.update(gps_fix="rtk_fixed")
    ok, _ = app.handle_command("arm"); assert ok and app.S.snapshot()["armed"]

def test_mission_requires_armed_and_auto():
    reset(); app.S.update(gps_fix="rtk_fixed")
    ok, _ = app.handle_command("start"); assert not ok, "start needs armed"
    app.handle_command("arm")
    ok, _ = app.handle_command("start"); assert not ok, "start needs AUTO mode"
    app.handle_command("mode", {"mode": "AUTO"})
    ok, _ = app.handle_command("start"); assert ok and app.S.snapshot()["mission"] == "running"

def test_blade_gate():
    reset(); app.S.update(gps_fix="rtk_fixed")
    ok, _ = app.handle_command("blade", {"on": True}); assert not ok, "blade must require armed"
    app.handle_command("arm")
    ok, _ = app.handle_command("blade", {"on": True}); assert ok and app.S.snapshot()["blade"]

def test_estop_kills_everything_and_latches():
    reset(); app.S.update(gps_fix="rtk_fixed")
    app.handle_command("arm"); app.handle_command("mode", {"mode": "AUTO"})
    app.handle_command("start"); app.handle_command("blade", {"on": True})
    app.handle_command("estop")
    s = app.S.snapshot()
    assert s["estop"] and not s["armed"] and not s["blade"] and s["mode"] == "HOLD" and s["mission"] == "idle"
    ok, _ = app.handle_command("arm"); assert not ok, "must stay latched until cleared"
    ok, _ = app.handle_command("clear_estop"); assert ok and not app.S.snapshot()["estop"]

def test_teach_records_and_saves():
    reset(); app.S.update(gps_fix="rtk_fixed")
    app.handle_command("teach_start")
    app.S.recording += [[42.8061, -71.3671], [42.8062, -71.3672]]
    app.S.update(taught_points=len(app.S.recording))
    ok, rid = app.handle_command("teach_stop", {"name": "Test path"})
    assert ok and rid.startswith("r"), "teach_stop should save a route"
    r = missions.get_route(rid); assert r and r["name"] == "Test path"
    missions.delete_route(rid)

def test_run_route_requires_armed_and_valid_id():
    reset(); app.S.update(gps_fix="rtk_fixed")
    rid = missions.add_taught("r", [[42.8060, -71.3675], [42.8061, -71.3675]])
    ok, _ = app.handle_command("run_route", {"id": rid}); assert not ok, "run needs armed"
    app.handle_command("arm")
    ok, _ = app.handle_command("run_route", {"id": "nope"}); assert not ok, "bad id rejected"
    ok, _ = app.handle_command("run_route", {"id": rid})
    assert ok and app.S.snapshot()["mission"] == "running" and app.S.active_route
    missions.delete_route(rid)

def test_run_route_sets_progress_and_clears():
    reset(); app.S.update(gps_fix="rtk_fixed")
    rid = missions.add_taught("r", [[42.8060,-71.3675],[42.8061,-71.3675],[42.8062,-71.3675]])
    app.handle_command("arm")
    app.handle_command("run_route", {"id": rid})
    s = app.S.snapshot()
    assert s["route_id"] == rid and s["progress"] == 0, "run sets active route + progress 0"
    assert len(missions.get_route(rid)["points"]) == 3, "route exposes full points (for /api/route)"
    app.handle_command("disarm")
    assert app.S.snapshot()["route_id"] is None, "disarm clears the active route"
    missions.delete_route(rid)

# ---------------------------------------------------------------- safety: incline / overhead / obstacle
def test_safety_blocks_steep_incline():
    ok, why = safety.evaluate({"roll": 20, "pitch": 2})
    assert not ok and "steep" in why, "must block above max slope"
    assert safety.evaluate({"roll": 10, "pitch": 8})[0], "moderate slope is allowed"

def test_safety_blocks_low_branch():
    ok, why = safety.evaluate({"overhead_m": 1.0})
    assert not ok and "branch" in why, "must stop for overhead below mast clearance"
    assert safety.evaluate({"overhead_m": 5.0})[0], "ample overhead is allowed"

def test_safety_priority_estop_first():
    ok, why = safety.evaluate({"estop": True, "roll": 30, "overhead_m": 0.5, "obstacle": True})
    assert not ok and why == "E-STOP", "e-stop is the top-priority blocker"

def test_safety_all_clear_allows():
    assert safety.evaluate({"roll": 4, "pitch": 3, "overhead_m": 5, "obstacle": False}) == (True, None)

def test_arm_refused_on_dangerous_slope():
    reset(); app.S.update(gps_fix="rtk_fixed", roll=20.0)
    ok, why = app.handle_command("arm")
    assert not ok and "steep" in why, "must refuse to arm on a dangerous slope"

# ---------------------------------------------------------------- camera-AI vision
def test_vision_hazard_in_stop_zone_stops():
    obstacle, rng, objs, _ = vision.evaluate([{"cls": "person", "conf": 0.9, "box": [0.5, 0.7, 0.2, 0.4]}])
    assert obstacle and rng is not None and "person" in objs, "person ahead must stop the mower"

def test_vision_hazard_offside_is_clear():
    assert vision.evaluate([{"cls": "person", "conf": 0.9, "box": [0.05, 0.7, 0.1, 0.2]}])[0] is False, \
        "a person well off to the side is not in the path"

def test_vision_low_confidence_ignored():
    assert vision.evaluate([{"cls": "person", "conf": 0.2, "box": [0.5, 0.7, 0.2, 0.4]}])[0] is False

def test_vision_grass_only_clear_with_coverage():
    obstacle, _, _, grass = vision.evaluate([{"cls": "grass", "conf": 0.95, "box": [0.5, 0.8, 0.9, 0.5]}])
    assert obstacle is False and grass > 0, "grass-only frame: no stop, grass coverage reported"

# ---------------------------------------------------------------- MAVLink mission encoding
def test_mission_items_encoding():
    items = mav.to_mission_items([[42.806, -71.367], [42.807, -71.368]])
    assert len(items) == 2
    assert items[0]["lat"] == int(round(42.806 * 1e7)) and items[0]["lon"] == int(round(-71.367 * 1e7))
    assert items[0]["command"] == 16 and items[0]["frame"] == 3 and items[0]["current"] == 1
    assert items[1]["current"] == 0, "only the first item is 'current'"

def test_mission_items_empty():
    assert mav.to_mission_items([]) == []

# ---------------------------------------------------------------- geofence
FENCE = SQUARE  # reuse the ~44m x 41m square

def test_point_in_polygon():
    assert safety.point_in_polygon(42.8062, -71.36725, FENCE), "centre point should be inside"
    assert not safety.point_in_polygon(42.8070, -71.36725, FENCE), "north of the square is outside"
    assert not safety.point_in_polygon(42.8062, -71.3660, FENCE), "east of the square is outside"
    assert not safety.point_in_polygon(42.8062, -71.36725, []), "no polygon = never inside"

def test_fence_breach_blocks_movement():
    inside = dict(lat=42.8062, lon=-71.36725, fence=FENCE, fence_enabled=True)
    outside = dict(lat=42.8070, lon=-71.36725, fence=FENCE, fence_enabled=True)
    ok, _ = safety.evaluate({**inside, "roll": 0, "pitch": 0, "overhead_m": 5})
    assert ok, "inside the fence must be allowed to move"
    ok, why = safety.evaluate({**outside, "roll": 0, "pitch": 0, "overhead_m": 5})
    assert not ok and "geofence" in why, f"outside must hold, got {why!r}"

def test_fence_disabled_is_ignored():
    outside = dict(lat=42.8070, lon=-71.36725, fence=FENCE, fence_enabled=False,
                   roll=0, pitch=0, overhead_m=5)
    ok, _ = safety.evaluate(outside)
    assert ok, "a disabled fence must not block movement"

def test_estop_outranks_fence():
    s = dict(estop=True, lat=42.8070, lon=-71.36725, fence=FENCE, fence_enabled=True)
    ok, why = safety.evaluate(s)
    assert not ok and why == "E-STOP", "e-stop is always the first reason reported"

def test_set_fence_validates_and_persists():
    reset()
    ok, _ = app.set_fence([[42.0, -71.0], [42.1, -71.0]])       # 2 points
    assert not ok, "a 2-point fence must be rejected"
    ok, _ = app.set_fence(FENCE)
    assert ok
    d = app.S.snapshot()
    assert d["fence_enabled"] and len(d["fence"]) == 4
    app.S = app.State()                                          # restart -> reload from disk
    assert app.S.snapshot()["fence_enabled"], "fence must survive a companion restart"
    ok, _ = app.set_fence([])                                    # clear
    assert ok and not app.S.snapshot()["fence_enabled"]


# ---------------------------------------------------------------- cross-track
def test_cross_track_zero_on_line_and_offset():
    a, b = [42.8060, -71.3675], [42.8060, -71.3665]
    mid = [42.8060, -71.3670]
    assert missions.cross_track_m(mid, a, b) < 0.01, "point on the line must read ~0"
    off = [42.8060 + 1.0/111320.0, -71.3670]           # 1 m north of the row
    assert abs(missions.cross_track_m(off, a, b) - 1.0) < 0.02, "1 m offset must read ~1 m"

# ---------------------------------------------------------------- no-rut turns
def test_kturn_stays_within_headland():
    pts = missions.turn_points(10.0, 0.0, 1.0, +1, r=1.2)     # gap < 2r -> K-turn
    assert max(x for x, _ in pts) <= 10.0 + 1.2 + 1e-6, "K-turn must not exceed the headland radius"
    assert any(abs(y - 1.0) < 0.05 for _, y in pts[-1:]), "K-turn must end on the next row"

def test_uturn_for_wide_gap():
    pts = missions.turn_points(10.0, 0.0, 3.0, +1, r=1.2)     # gap >= 2r -> smooth U
    assert max(x for x, _ in pts) <= 10.0 + 1.2 + 1e-6
    assert abs(pts[-1][1] - 3.0) < 0.25, "U-turn must arrive at the next row height"

def test_plan_coverage_turns_within_boundary():
    rid, pts = missions.plan_coverage_turns("t", SQUARE, spacing=1.5)
    lats = [q[0] for q in pts]; lons = [q[1] for q in pts]
    assert min(lats) >= 42.8060 - 2e-5 and max(lats) <= 42.8064 + 2e-5, "turns must stay inside (lat)"
    assert min(lons) >= -71.3675 - 2e-5 and max(lons) <= -71.3670 + 2e-5, "turns must stay inside (lon)"
    missions.delete_route(rid)

# ---------------------------------------------------------------- ignition + choke
def test_choke_schedule():
    assert attachments.choke_for(2) == 1.0 and attachments.choke_for(15) == 0.5
    assert attachments.choke_for(25) == 0.0 and attachments.choke_for(None) == 1.0

def test_crank_interlocks():
    ok, why = attachments.can_crank({"estop": True}); assert not ok and "E-STOP" in why
    ok, why = attachments.can_crank({"engine": "run"}); assert not ok
    ok, why = attachments.can_crank({"engine": "off", "blade": True}); assert not ok and "PTO" in why
    ok, _ = attachments.can_crank({"engine": "off", "blade": False, "mission": "idle"}); assert ok

def test_arm_requires_engine_running():
    reset(); app.S.update(gps_fix="rtk_fixed", engine="off")
    ok, why = app.handle_command("arm")
    assert not ok and "engine" in why, "arming a dead engine must be refused"

def test_estop_kills_ignition_and_attachments():
    reset(); app.S.update(engine="run", boom={"angle": 90, "blower": True, "trimmer": True},
                          sprayer={"attached": True, "tank_pct": 50, "pump_duty": 0.4, "spraying": True, "applied_l": 0},
                          bagger={"attached": True, "fill_pct": 20, "state": "raising"})
    app.handle_command("estop")
    d = app.S.snapshot()
    assert d["engine"] == "off" and not d["boom"]["blower"] and not d["boom"]["trimmer"]
    assert not d["sprayer"]["spraying"] and d["bagger"]["state"] == "idle"

# ---------------------------------------------------------------- TPMS
def test_tpms_warnings():
    assert attachments.tpms_warnings({"rl": 12.0, "fl": 20.0}) == []
    w = attachments.tpms_warnings({"rl": 8.0})
    assert w and "rear-left" in w[0] and "low" in w[0]
    w = attachments.tpms_warnings({"fl": 27.0})
    assert w and "high" in w[0]

# ---------------------------------------------------------------- bagger
def test_bagger_fill_and_dump_gates():
    f = attachments.bagger_fill_step(0.0, True, 100, 60)
    assert 5 < f < 7, f"1 min heavy cut should be ~5.6%: {f}"
    assert attachments.bagger_fill_step(50, False, 100, 60) == 50, "no fill with blade off"
    ok, why = attachments.can_dump({"speed": 1.0}); assert not ok and "stop" in why
    ok, why = attachments.can_dump({"speed": 0, "blade": True}); assert not ok
    ok, _ = attachments.can_dump({"speed": 0, "blade": False, "bagger": {"state": "idle"}}); assert ok

# ---------------------------------------------------------------- boom
def test_trimmer_gates_like_a_blade():
    ok, why = attachments.can_run_trimmer({"armed": False}); assert not ok and "arm" in why
    ok, why = attachments.can_run_trimmer({"armed": True, "speed": 2.0}); assert not ok and "fast" in why
    ok, _ = attachments.can_run_trimmer({"armed": True, "speed": 0.5}); assert ok
    assert attachments.clamp_boom(400) == 270.0 and attachments.clamp_boom(-5) == 0.0

# ---------------------------------------------------------------- sprayer
def test_sprayer_duty_follows_speed_and_pauses_in_turns():
    assert attachments.sprayer_duty(0.0) == 0.0, "no flow while stopped"
    d1, d2 = attachments.sprayer_duty(1.0), attachments.sprayer_duty(2.0)
    assert d2 > d1 > 0, "duty must rise with ground speed"
    assert abs(d2 - min(1.0, 2*d1)) < 0.01, "application is speed-proportional"
    assert attachments.sprayer_duty(2.0, turn_rate_dps=40) == 0.0, "pause in sharp turns (no double dose)"

def test_sprayer_command_gates():
    reset()
    ok, why = app.handle_command("sprayer", {"spraying": True})
    assert not ok and "attached" in why, "cannot spray without the sprayer hitched"

# ---------------------------------------------------------------- weather + service
def test_weather_gate_fails_open():
    assert not app.weather_gate(None)
    assert not app.weather_gate({"precip_prob": None})
    assert app.weather_gate({"precip_prob": 70})
    assert not app.weather_gate({"precip_prob": 30})

def test_service_reset_restarts_counter():
    reset(); app.S.update(**app._service_fields(40.0, 0.0, 0.0))
    ok, _ = app.reset_service("oil"); assert ok
    d = app.S.snapshot()
    assert abs(d["oil_due_h"] - app.OIL_INTERVAL_H) < 0.2, "oil counter must restart from now"
    assert abs(d["blade_due_h"] - (app.BLADE_INTERVAL_H - 40.0)) < 0.2, "blade counter untouched"


# ---------------------------------------------------------------- scenario fixtures (41)
SCENARIOS = [
    # (state-overrides, allow, reason-substr)
    ({}, True, None),
    ({"estop": True}, False, "E-STOP"),
    ({"roll": 16}, False, "steep"),
    ({"overhead_m": 1.2}, False, "branch"),
    ({"obstacle": True}, False, "obstacle"),
    ({"estop": True, "roll": 20, "obstacle": True}, False, "E-STOP"),          # priority
    ({"roll": 20, "overhead_m": 1.0}, False, "steep"),                          # slope > overhead
    ({"overhead_m": 1.0, "obstacle": True}, False, "branch"),                   # overhead > obstacle
    ({"fence": SQUARE, "fence_enabled": True, "lat": 42.9, "lon": -71.36725}, False, "geofence"),
    ({"roll": 13}, True, None),                                                 # warn band still moves
]
def test_safety_scenario_table():
    base = dict(estop=False, roll=0, pitch=0, overhead_m=5.0, obstacle=False,
                lat=42.8062, lon=-71.36725, fence=[], fence_enabled=False)
    for i, (over, allow, sub) in enumerate(SCENARIOS):
        ok, why = safety.evaluate({**base, **over})
        assert ok == allow, f"scenario {i}: expected allow={allow}, got {why!r}"
        if sub: assert sub in (why or ""), f"scenario {i}: reason {why!r} missing {sub!r}"

# ---------------------------------------------------------------- QGC .plan (58)
def test_qgc_plan_roundtrip():
    pts = [[42.8060, -71.3675], [42.8061, -71.3670], [42.8062, -71.3665]]
    plan = missions.to_qgc_plan(pts)
    assert plan["fileType"] == "Plan" and len(plan["mission"]["items"]) == 3
    back = missions.from_qgc_plan(plan)
    assert back == pts, "roundtrip must preserve waypoints"
    assert missions.from_qgc_plan({"mission": {"items": []}}) == []

# ---------------------------------------------------------------- obstacle memory (63)
def test_obstacle_log_rising_edge_only():
    import os
    try: os.remove(app._obstacles_path())
    except OSError: pass
    d = {"obstacle": True, "lat": 1.0, "lon": 2.0, "obstacle_range": 1.5}
    hits = app.obstacle_log(False, d)          # rising edge -> logged
    assert hits and len(hits) == 1
    assert app.obstacle_log(True, d) is None, "held obstacle must not re-log"
    assert app.obstacle_log(False, {"obstacle": False}) is None

# ---------------------------------------------------------------- runner
def main():
    tests = sorted(n for n in globals() if n.startswith("test_"))
    passed = failed = 0
    for name in tests:
        try:
            globals()[name](); passed += 1; print(f"  \033[32mPASS\033[0m {name}")
        except AssertionError as e:
            failed += 1; print(f"  \033[31mFAIL\033[0m {name}: {e}")
        except Exception as e:
            failed += 1; print(f"  \033[31mERR \033[0m {name}: {type(e).__name__}: {e}")
    print(f"\n{passed}/{passed+failed} passed" + ("" if not failed else f"  ({failed} FAILED)"))
    sys.exit(1 if failed else 0)

if __name__ == "__main__":
    main()
