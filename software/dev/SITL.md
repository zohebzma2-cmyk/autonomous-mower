# ArduPilot SITL — develop against a simulated rover (no hardware)

SITL (Software-In-The-Loop) runs the *real* ArduPilot Rover firmware on your computer as a
simulated mower — real modes, RTK-grade GPS, missions, and failsafes. This is the best way to
build teach-and-repeat, coverage, and the safety logic before the Pixhawk arrives.

## Quick start (native — one command, verified on macOS arm64)
```bash
# once: build Rover SITL (~40 s on an M-series Mac)
git clone --recurse-submodules --shallow-submodules --depth 1 --branch Rover-4.7.1 \
    https://github.com/ArduPilot/ardupilot ~/Developer/ardupilot
cd ~/Developer/ardupilot && uv venv --python 3.12 .venv && source .venv/bin/activate
uv pip install empy==3.3.4 pexpect future setuptools
./waf configure --board sitl && ./waf rover

# every time: SITL (skid-steer) + this repo's params + the companion UI
cd ~/Developer/autonomous-mower && ./scripts/sitl.sh      # → http://localhost:8080
```
`scripts/sitl.sh` puts home on the sim "Yard" field, so the saved coverage route runs as-is:
arm → Run → the route uploads as an AUTO mission and the skid rover mows it. E-STOP disarms
and HOLDs the vehicle. `scripts/check_parm.py` validates every name in a `.parm` file against the
live firmware (typos and renamed params fail loudly instead of being silently skipped).

## Quick start (Docker)
```bash
docker run --rm -it -p 14550:14550/udp radarku/ardupilot-sitl \
  sim_vehicle.py -v Rover --out=udp:0.0.0.0:14550
```
(or build ArduPilot SITL natively: https://ardupilot.org/dev/docs/sitl-simulator-software-in-the-loop.html)

Then run the companion against it:
```bash
cd software/companion
pip install pymavlink
python3 app.py --mav udp:127.0.0.1:14550
# open http://localhost:8080/  — the UI now reflects the simulated rover
```

## Make it behave like our mower
In SITL set the skid-steer frame and RTK so it matches the real config in `docs/BUILD.md §5`:
```
param set FRAME_CLASS 2
param set SERVO1_FUNCTION 73   # throttle-left
param set SERVO3_FUNCTION 74   # throttle-right
param set FENCE_ENABLE 1
param set FS_GCS_ENABLE 1
```
Arm, switch to AUTO, load a simple mission from Mission Planner/QGC, and watch it run in the UI + map.

## Why this matters
Every line of `app.py` / `mav.py` / the UI you write against SITL is the *same code* that runs on the
real machine — you just change `--mav udp:...` to `--mav /dev/serial0`. Zero rewrite, fully de-risked.
