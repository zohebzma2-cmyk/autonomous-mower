# Autonomous Zero-Turn Mower — Project Spec (zohebalvi.com)

**One line:** A ~$1.8k reproducible retrofit that turns a commercial gas zero-turn mower into a
self-driving, iPad-controlled robot — RTK GPS, LiDAR, cameras, on-device AI — built end-to-end
across hardware, firmware, control software, and parametric CAD.

**Status:** Design + firmware + control software + documentation **complete and verified (25/25 tests)**.
Next phase: physical build + on-hardware bring-up.

## Why
Commercial autonomous mowers (e.g. Greenzie) are ~$25k professionally-installed B2B systems. This
project achieves the same capability as a parametric retrofit kit that bolts onto a Gravely ZT X 52
and adapts to any zero-turn by re-measuring ~6 dimensions.

## Capabilities
- **Teach-and-repeat** — drive the path once, it records the RTK route and repeats it.
- **Draw-a-zone coverage** — outline a boundary on the map → auto-planned mow rows + live % mowed.
- **Obstacle avoidance** — 360° LiDAR + camera AI stop for obstacles/people.
- **Overhead / tree-limb detection** — upward sensor stops before the mast strikes a low branch.
- **Hill safety** — IMU rollover-slope cutoff + mow up/down strategy.
- **Fail-to-neutral** — loss of e-stop/control signal returns steering to neutral and cuts power.
- **One UI, two screens** — identical web control on the iPad (WiFi) and the on-unit touchscreen.

## Specifications
| | |
|---|---|
| Base machine | Gravely ZT X 52 (2021, 24 hp Kohler), 52″ fabricated deck, electric PTO |
| Autonomy core | Pixhawk 6C · ArduPilot Rover (skid-steer, RTK, geofence, failsafes) |
| Companion / AI | Raspberry Pi 5 (8 GB) + Hailo-8L (13 TOPS) |
| Positioning | RTK GPS ±2 cm; dual-antenna moving-baseline heading ~0.4°; ~few-cm tracking |
| Perception | 360° 2D LiDAR · front + rear cameras · forward-up ultrasonic · IMU |
| Actuation | 2× feedback linear actuators · ESP32 PID + BTS7960 · relay PTO · throttle servo |
| Safety | Physical e-stop + RC kill + ArduPilot failsafes + tested software interlock |
| Control | Responsive web UI (iPad + 7″ touchscreen) · OpenStreetMap · teach/coverage/% |
| Mechanical | Parametric OpenSCAD · 24 printable parts · exact-to-datasheet · any-ZTR |
| Power | Mower 12 V battery · fused distribution · DC-DC · drive-power relay |
| Cost | ~$1,644 functional / ~$1,812 precision build |

## Stack
ArduPilot Rover · MAVLink · Raspberry Pi 5 · Hailo-8L · u-blox ZED-F9P RTK · RPLidar ·
ESP32/C++ · Python · OpenSCAD · Leaflet/OpenStreetMap · FDM 3D printing.

## Engineering highlights
- Parametric exact-spec CAD (every part to its real datasheet; six numbers adapt it to any mower).
- Multi-layer safety kill chain documented to the pin + a tested software safety policy.
- Pure-Python control companion with a 25-case test suite (coverage geometry, mission encoding,
  full safety state machine) — all green.
- Complete build package: wiring/pinout/kill-chain diagrams, ArduPilot params, ESP32 firmware,
  printable parts manifest, phase-by-phase build manual.

---
*Add to zohebalvi.com: `web/index.html` is a self-contained page; drop it + `web/assets/` into the
portfolio repo and deploy per the usual Netlify flow.*
