#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# One command: ArduPilot Rover SITL (skid-steer, like the ZTR) + this repo's params +
# the companion UI talking MAVLink to it.
#
#   ./scripts/sitl.sh                      # UI on http://localhost:8080
#   ARDUPILOT=~/src/ardupilot ./scripts/sitl.sh
#
# Needs a native SITL build once (see software/dev/SITL.md):
#   git clone --recurse-submodules --branch Rover-4.7.1 https://github.com/ArduPilot/ardupilot
#   cd ardupilot && ./waf configure --board sitl && ./waf rover
# Home = the sim "Yard" field (42.80620, -71.36725) so the saved coverage route is local.
# SITL serial ports: 5760 = companion, 5762 = spare (check_parm.py / Mission Planner / QGC).
set -euo pipefail
cd "$(dirname "$0")/.."
AP="${ARDUPILOT:-$HOME/Developer/ardupilot}"
BIN="$AP/build/sitl/bin/ardurover"
PY=python3; [ -x .venv/bin/python ] && PY=.venv/bin/python
[ -x "$BIN" ] || { echo "no SITL build at $BIN — see software/dev/SITL.md"; exit 1; }

RUN=$(mktemp -d)                                   # eeprom/logs stay out of the repo
DEF="$AP/Tools/autotest/default_params"
echo "== SITL (rover-skid) in $RUN"
( cd "$RUN" && exec "$BIN" --model rover-skid --speedup 1 -I0 \
    --defaults "$DEF/rover.parm,$DEF/rover-skid.parm" \
    --home 42.80620,-71.36725,50,0 < /dev/null > sitl.log 2>&1 ) &
SITL=$!
trap 'kill $SITL ${APP:-} 2>/dev/null || true' EXIT INT TERM
# SITL blocks on SERIAL0 (5760) until a client connects, and only then opens 5762 —
# so the companion goes first, then the params load over the spare port.
until lsof -iTCP:5760 -sTCP:LISTEN >/dev/null 2>&1; do sleep 0.5; done
echo "== companion UI → http://localhost:${PORT:-8080}   (Ctrl-C stops both)"
$PY software/companion/app.py --mav tcp:127.0.0.1:5760 --port "${PORT:-8080}" &
APP=$!
until lsof -iTCP:5762 -sTCP:LISTEN >/dev/null 2>&1; do sleep 0.5; done

echo "== loading this repo's rover params over 5762 (validated against the live firmware)"
$PY scripts/check_parm.py firmware/ardupilot/rover_params.parm --mav tcp:127.0.0.1:5762 --load \
  | grep -vE "^  SET" || true

# rover_params keeps BRD_SAFETY_DEFLT=1 (the real Pixhawk's safety button must be pressed
# before arming). SITL has no button, so "press" it over MAVLink — same effect, param unchanged.
$PY - <<'PY'
from pymavlink import mavutil
m = mavutil.mavlink_connection("tcp:127.0.0.1:5762"); m.wait_heartbeat(timeout=10)
m.mav.command_long_send(m.target_system, m.target_component,
    mavutil.mavlink.MAV_CMD_DO_SET_SAFETY_SWITCH_STATE, 0,
    mavutil.mavlink.SAFETY_SWITCH_STATE_DANGEROUS, 0, 0, 0, 0, 0, 0)   # DANGEROUS = safety OFF
ack = m.recv_match(type="COMMAND_ACK", blocking=True, timeout=5)
print("== safety switch pressed (SITL):", "ok" if ack and ack.result == 0 else f"result={getattr(ack, 'result', None)}")
PY
wait $APP
