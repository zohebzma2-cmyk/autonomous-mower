#!/usr/bin/env python3
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

import app, safety

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
