#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Validate (and optionally load) an ArduPilot .parm file against a live autopilot.

    .venv/bin/python scripts/check_parm.py firmware/ardupilot/rover_params.parm \
        --mav tcp:127.0.0.1:5762 [--load]

Every NAME in the file is read back from the vehicle (SITL or Pixhawk). A name the
firmware doesn't know is a typo or a removed parameter — it would be silently ignored
by Mission Planner's "Load", so this fails loudly instead. --load also writes the
values and verifies each one reads back. Exit code 1 on any unknown/failed param.
Needs pymavlink (requirements-dev.txt). Use a spare SITL port (5762) if the
companion already holds 5760.
"""
import argparse
import re
import sys
import time


def parse_parm(path):
    out = []
    for n, line in enumerate(open(path), 1):
        line = line.split("#", 1)[0].strip()
        if not line:
            continue
        name, value = re.split(r"[,\s]+", line, maxsplit=1)
        out.append((n, name, float(value.split()[0])))
    return out


def read_param(m, name, timeout=2.0):
    m.mav.param_request_read_send(m.target_system, m.target_component, name.encode(), -1)
    end = time.time() + timeout
    while time.time() < end:
        msg = m.recv_match(type="PARAM_VALUE", blocking=True, timeout=0.3)
        if msg and msg.param_id == name:
            return msg.param_value
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("parm", nargs="+")
    ap.add_argument("--mav", default="tcp:127.0.0.1:5762")
    ap.add_argument("--load", action="store_true", help="also set each value and verify it")
    a = ap.parse_args()

    from pymavlink import mavutil
    m = mavutil.mavlink_connection(a.mav)
    m.wait_heartbeat(timeout=10)
    bad = 0
    for path in a.parm:
        rows = parse_parm(path)
        print(f"== {path}: {len(rows)} params")
        for n, name, value in rows:
            cur = read_param(m, name)
            if cur is None:
                print(f"  UNKNOWN  line {n}: {name}")
                bad += 1
                continue
            if a.load and abs(cur - value) > 1e-4:
                m.mav.param_set_send(m.target_system, m.target_component, name.encode(), value,
                                     mavutil.mavlink.MAV_PARAM_TYPE_REAL32)
                got = read_param(m, name)
                ok = got is not None and abs(got - value) < 1e-3 * max(1.0, abs(value))
                print(f"  {'SET ' if ok else 'FAIL'}     {name} {cur:g} -> {value:g}" + ("" if ok else f" (reads {got})"))
                bad += 0 if ok else 1
    print("ALL PARAMS KNOWN" + (" + LOADED" if a.load else "") if not bad else f"{bad} PROBLEM(S)")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
