# Autonomous ZTR — Software

One responsive web UI drives **both** the iPad (Safari over WiFi) and the **on-unit touchscreen**
(Chromium kiosk). It's served by the companion computer (Raspberry Pi 5), which bridges to the
ArduPilot autopilot over MAVLink. Develop the whole stack today with **no hardware** via sim mode,
then point it at **ArduPilot SITL**, then the real Pixhawk — same code.

```
 iPad (Safari) ─┐
                ├─►  companion/app.py  (web server: UI + SSE telemetry + REST control)
 on-unit ───────┘            │
 touchscreen                 ├── mav.py ── MAVLink ──►  ArduPilot Rover
 (Chromium kiosk)            │                         · sim   (no hardware, default)
                             │                         · SITL  (simulated rover — dev/SITL.md)
                             │                         · real  (Pixhawk 6C)
                             └── safety.py ◄── RPLidar (obstacle stop)   [phase 2]
                                  vision  ◄── Pi Camera 3 + Hailo        [phase 3]
```

## Run it now (sim mode, zero dependencies)
```bash
cd software/companion
python3 app.py --port 8080
# laptop:  http://localhost:8080/
# iPad:    http://<computer-LAN-ip>:8080/   (same WiFi)
```
Pure Python stdlib — telemetry is pushed via Server-Sent Events, controls via JSON POST. The sim
generates plausible telemetry and honors the real control logic (arm-before-start, AUTO-to-mow,
blade gate, E-STOP → HOLD+disarm+blade-off, LiDAR obstacle hold).

## Run against ArduPilot SITL (realistic, still no hardware)
A full simulated rover with real RTK nav, modes, and failsafes. See [`dev/SITL.md`](dev/SITL.md).
```bash
python3 app.py --mav udp:127.0.0.1:14550     # needs: pip install pymavlink
```

## On the real machine
1. Flash **ArduPilot Rover** to the Pixhawk 6C; set `FRAME_CLASS=2`, skid-steer, RTK GPS, failsafes
   (params summary in `../docs/BUILD.md §5`).
2. On the Pi 5: `python3 app.py --mav /dev/serial0` (Pixhawk TELEM port).
3. iPad: open `http://<pi-ip>:8080/`.

## On-unit touchscreen (kiosk)
The display you mount on the unit shows the *same* UI full-screen. On the Pi:
```bash
# autostart Chromium kiosk pointing at the local server
chromium-browser --kiosk --noerrdialogs --disable-infobars http://localhost:8080/
```
**Full deploy** (service + kiosk autostart + cameras + NTRIP): see [`dev/DEPLOY.md`](dev/DEPLOY.md)
with the ready-to-use `deploy/mower-companion.service` and `deploy/kiosk.sh`.
**Display pick:** **Raspberry Pi Touch Display 2** (DSI, ~$60); a standard LCD is hard to read in
direct sun — a sunlight-readable HDMI panel is the daytime upgrade (`cart/ORDER.md`).

## Roadmap
- [x] **v0 control plane** — web UI (iPad + kiosk), telemetry, arm/mode/mission/blade/E-STOP
- [x] **Teach-and-repeat** — record waypoints via UI, run as a route
- [x] **Coverage planner** — boundary → boustrophedon rows + **live % mowed** overlay
- [x] **Safety** (`safety.py`) — incline cutoff, overhead/tree-limb stop, obstacle (18/19 tested)
- [x] **Map view** — live position + heading + planned vs mowed path (OpenStreetMap)
- [x] **Cameras** — front/rear feeds in the UI
- [x] **MAVLink** (`mav.py`) — command routing wired; **needs SITL/hardware validation**
- [x] **Deployment** — systemd service + kiosk autostart (`dev/DEPLOY.md`)
- [x] **Camera AI** (`vision.py`) — detector pipeline + obstacle/grass mapping (tested); the Hailo `.hef` model is trained/compiled on hardware
- [x] **MAVLink mission upload** (`mav.py`) — route → AUTO waypoint upload (encoding tested; handshake needs SITL)
- [ ] **Fleet/RaaS layer** — multi-unit dashboard (commercialization, see project notes)

## Safety
This is the *convenience* control plane. The machine's real safety is the **hardware kill chain**
(physical e-stop, RC kill, ArduPilot failsafes) per `../docs/BUILD.md §0`. The web E-STOP commands
HOLD + disarm + blade-off; it is **not** a substitute for the physical e-stop. Blades stay OFF in all
testing until drive + nav + failsafes are proven.
