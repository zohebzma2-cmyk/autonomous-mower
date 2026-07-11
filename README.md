# Autonomous Zero-Turn Retrofit Kit

[![License: MIT](https://img.shields.io/badge/License-MIT-3fb950.svg)](LICENSE)
[![Status: active build](https://img.shields.io/badge/status-active%20build-f0883e.svg)](#status--honest-limitations)
[![Tests](https://img.shields.io/badge/tests-25%2F25-3fb950.svg)](software/tests)
[![Autopilot: ArduPilot Rover](https://img.shields.io/badge/autopilot-ArduPilot%20Rover-5ab0ff.svg)](https://ardupilot.org/rover)
[![Discussions](https://img.shields.io/badge/community-Discussions-3fb950.svg)](https://github.com/zohebzma2-cmyk/autonomous-mower/discussions)

> **Most open-source mowers convert a toy robot-mower. This retrofits a 615 lb commercial gas zero-turn.**

Turn a seated zero-turn mower into a self-driving, iPad-controlled robot — **RTK GPS + LiDAR + cameras + on-device AI** — weatherproofed to live outdoors, and **reproducible on any ZTR** by re-measuring a handful of dimensions.

> **Status: 🔧 in active build.** Design, CAD, firmware, control software, and docs are complete and verified (25/25 tests). The machine is currently being built in person — parts on order, brackets printing, wiring the kill-chain first. This is a multi-month, safety-gated build, documented as it happens — not a plug-and-play kit.

**Confirmed reference machine:** Gravely **ZT X 52** · ~2021 · **Kohler 7000** (24 hp, 725 cc) · electric PTO clutch.

> 🏁 **New here? Start with [`docs/00-BUILD-MANUAL.md`](docs/00-BUILD-MANUAL.md)** — the end-to-end build sequence.
>
> 🌐 **Interactive writeup:** [zohebalvi.com/projects/autonomous-mower](https://zohebalvi.com/projects/autonomous-mower.html) — 3D model, live control-UI demo, architecture, and the full parts list with order links.

> ⚠️ **A 52″ mower deck can kill.** Read [`docs/BUILD.md` §0 Safety](docs/BUILD.md) before powering anything. **Blades stay disconnected until drive + navigation + every failsafe is proven.**

---

## The architecture in one line

**ArduPilot Rover** on a Pixhawk 6C owns drive + RTK navigation + the failsafe chain (skid-steer fits a ZTR natively); a **Raspberry Pi 5 + Hailo-8L** (13 TOPS) rides shotgun for LiDAR obstacle-stop and camera AI, talking to the FC over MAVLink; an **ESP32** closes the lap-bar position loop the autopilot can't drive directly. One web UI serves both an iPad over WiFi and an on-unit touchscreen.

```
        ┌───────────── SENSE ─────────────┐   ┌────── THINK ──────┐   ┌──── ACT ────┐
  Dual RTK GPS (±2 cm, ~0.4° heading) ─────┼──► Pixhawk 6C ────────┼──► lap-bar L/R
  360° LiDAR ──────────────┐               │   (ArduPilot Rover)   │   (via ESP32)
  Front + rear cameras ────┼──► Pi 5 + Hailo├── MAVLink ───────────┤
  Overhead ultrasonic ─────┘   (vision/UI) │   ESP32 (lap-bar PID) ├──► PTO relay
                                           └───────────────────────┘   (blades)
```

---

## The machine — down to the millimetre

| | Gravely ZT X 52 (Kohler 915256) |
|---|---|
| Overall | **1968 × 1610 × 1039 mm** (L×W×H) |
| Curb weight | 615 lb (279 kg) |
| Cutting deck | **1321 mm** (52″), 11-ga fabricated |
| Rear drive wheels | 20×10-8 → **Ø 508 mm**, 254 mm wide |
| Front casters | 11×6-5 → **Ø 279 mm** |
| Seat pan height | 580 mm off ground (**no factory ROPS**) |
| Frame rail | 50.8 mm square tube |
| Lap-bar tube | **Ø 25.4 mm** round steel (MIC to confirm), 560 mm spacing, ~90 mm throw |
| Powertrain | 24 hp Kohler 7000 (725 cc) · Hydro-Gear ZT-2200 · 7 mph · **electric PTO** |

Retrofit parts are modeled to their datasheets — e.g. the **PA-14P actuator** (retracted 241.6 mm, Ø38.1 mm body, 6.35 mm clevis pin), **simpleRTK2B** (68.58 × 53.34 mm, Arduino-Uno footprint), **RPLidar A1M8** (teardrop 96.74 × 70.28 mm base). See [`cad/params.scad`](cad/params.scad).

---

## What's in the repo

```
autonomous-mower/
├── docs/
│   ├── 00-BUILD-MANUAL.md   ← START HERE — Phase 0–6 build sequence
│   ├── BUILD.md             ← full build & SAFETY spec (architecture, training, go/no-go)
│   ├── WIRING.md            ← power distribution, kill-chain, per-module pinouts
│   ├── PRINT_GUIDE.md       ← per-part orientation, brim, supports, plate batching
│   └── wiring-diagram.svg
├── cad/                     ← parametric OpenSCAD — 24 print-ready parts
│   ├── params.scad          ← ★ MASTER PARAMETERS — edit SECTION 1 to fit any ZTR
│   ├── assembly.scad        ← whole machine; SHOW=all|body|black|retro for multi-material export
│   ├── mower.scad           ← parametric mower mock (context)
│   ├── {enclosure,actuator_brackets,gps_mast,lidar_mount,camera_mount,controls_bracket,badge}.scad
│   ├── export_stl.sh        ← export every PRINT_* part + bed-fit gate (rejects > 145 mm)
│   ├── bake_brims.sh        ← welds a bed-adhesion brim onto every part
│   └── stl/ · renders/ · vendor/
├── software/
│   ├── companion/           ← Python: app.py (HTTP+SSE), safety.py, vision.py, missions.py, mav.py
│   ├── ui/                  ← the control UI (iPad + on-unit kiosk)
│   ├── tests/               ← 25 stdlib tests (safety, coverage, vision, mission encoding)
│   └── deploy/              ← systemd service + Chromium kiosk autostart
├── firmware/
│   ├── lapbar_controller/   ← ESP32: FC-PWM → pot → BTS7960 position loop, fail-to-neutral
│   └── ardupilot/           ← rover_params.parm (skid-steer, RTK, geofence, moving-baseline)
├── hardware/pcb/            ← ★ MowerCarrier: power + kill-chain + ESP32 carrier board
│   ├── schematic.svg · layout.svg   ← generated (gen_schematic.py / gen_layout.py)
│   └── README.md · netlist.md · BOM.md · FABRICATION.md
└── cart/                    ← ORDER.md (real BOM + links), order.html
```

---

## Quickstart

### CAD → STL
```bash
cd cad
# 1. Edit params.scad SECTION 1 to your machine (lap-bar OD, spacing, frame tube, seat)
openscad assembly.scad          # see the whole machine
./export_stl.sh                 # export all printable parts + bed-fit check
./bake_brims.sh                 # weld brims for adhesion
# slice cad/stl/brim/*.stl in FlashPrint for the Adventurer 3 (ASA or PETG)
```

### Control software (runs today, no hardware)
```bash
python3 software/companion/app.py --sim --port 8080
# open http://localhost:8080 — arm, draw a zone, run a coverage mission in simulation
python3 -m pytest software/tests -q         # 25/25
```

### Firmware
- **ESP32:** flash `firmware/lapbar_controller/lapbar_controller.ino` (Arduino IDE / arduino-cli).
- **ArduPilot:** load `firmware/ardupilot/rover_params.parm` in Mission Planner (skid-steer + RTK + failsafes; moving-baseline block commented for the dual-antenna heading upgrade).

---

## Training — all three, built in order

1. **Teach-and-repeat** — drive the path once, it repeats the RTK track.
2. **Boundary → auto-coverage** — drive the perimeter, a boustrophedon planner fills the rows and uploads them as an ArduPilot AUTO mission.
3. **AI learns the yard** — the camera/LiDAR model refines a semantic map over runs (Hailo).

---

## Precision

The upgrade that matters is **dual-antenna moving-baseline heading**. One RTK antenna gives a great position but a noisy heading at a standstill; a second antenna on a ≥ 500 mm baseline fixes heading geometrically (~0.4°), turning ~10 cm cross-track into a few cm. Config in `firmware/ardupilot/rover_params.parm`.

| | |
|---|---|
| Position | **±2 cm** RTK-fixed (u-blox ZED-F9P) |
| Heading | **~0.4°** moving-baseline (dual antenna) |
| Cross-track | few cm, row to row |
| On-device AI | **13 TOPS** (Hailo-8L), INT8, < 30 ms, no cloud |

---

## Safety — a layered kill chain (wire & test this FIRST)

No single failure leaves the machine moving. Blades stay disconnected until every layer is proven.

1. **Physical e-stop** (normally-closed) — in series with the drive relay + PTO relay; cuts power independent of any code.
2. **RC kill** — an independent FlySky channel → ArduPilot RC failsafe → HOLD + disarm.
3. **Software interlock** (`safety.py`) — evaluates incline (15° cutoff), overhead (1.6 m), and obstacle every cycle; priority `e-stop > slope > overhead > obstacle`.
4. **Fail-to-neutral** — on e-stop or signal loss the ESP32 drives the lap bars to center, then coasts; ArduPilot failsafes (GPS loss, geofence, low battery) hold.

Full pinout + kill-chain wiring in [`docs/WIRING.md`](docs/WIRING.md).

---

## Bill of materials

Real, in-stock parts — verified against live listings, no fabricated SKUs. Two tiers: **functional ≈ $1,644**, or **precision ≈ $1,812** with the dual-antenna heading kit. Full itemized sheet with links in [`cart/ORDER.md`](cart/ORDER.md).

- **Navigation / compute:** Pixhawk 6C ([Holybro](https://holybro.com/products/pixhawk-6c)) · simpleRTK2B + ANN-MB-00 ([ArduSimple](https://www.ardusimple.com/product/simplertk2b/)) · Pi 5 + Hailo AI HAT+ ([PiShop](https://www.pishop.us/product/raspberry-pi-ai-hat-13-tops/))
- **Perception:** RPLidar A1M8 · 2× Pi Camera 3 · JSN-SR04T ultrasonic
- **Steering / drive:** 2× Progressive Automations PA-14P · 2× BTS7960 · ESP32
- **Safety / power:** IP65 NC e-stop · 40 A relays · PM02 power module · fuse block · bucks

---

## Adapting to another zero-turn

Open [`cad/params.scad`](cad/params.scad) → **SECTION 1**, re-measure the lap bars / frame / seat, re-render, re-slice. That's the whole port — the mounts, brackets, and masts regenerate around your numbers. Toro, Bad Boy, Spartan, Ferris, Scag, etc.

---

## Status & honest limitations

Design + CAD + firmware + control software + docs are complete and verified (25/25 tests). The build is **in progress in person**. Remaining work is hardware-gated: SITL/on-FC validation of the MAVLink handshake, training the Hailo `.hef` model, and the future fleet/RaaS layer. See [`docs/BUILD.md §12`](docs/BUILD.md).

## Related open-source mowers & rovers

This project stands on the shoulders of a great open community — go star these too:

- **[OpenMower](https://github.com/ClemensElflein/OpenMower)** (Clemens Elflein) — the flagship: retrofits *consumer* robot mowers with a custom mainboard + RTK + ROS. Same RTK/Pi/vision philosophy; we take it to a full-size gas ZTR.
- **[Ardumower / Sunray](https://github.com/Ardumower/Sunray)** — the original DIY-mower ecosystem; Sunray pioneered RTK-without-a-perimeter-wire.
- **[ArduPilot Rover](https://ardupilot.org/rover)** — the autopilot this build runs. The [robot-mower threads](https://discuss.ardupilot.org/t/robot-mower-based-on-ardurover/61999) on their Discourse are the best place to talk shop.
- **[Twisted Fields — Acorn](https://github.com/Twisted-Fields/acorn-precision-farming-rover)** & **[FarmBot](https://github.com/farmbot)** — adjacent open outdoor-autonomy / ag-robotics done well.

## Community & contributing

- 💬 **[GitHub Discussions](https://github.com/zohebzma2-cmyk/autonomous-mower/discussions)** — *Show & Tell* your ZTR build, ask in *Q&A*, propose *Ideas*, follow *Build logs*.
- 🔧 **Adapting to a different zero-turn?** That's the whole point — a new machine profile is the most valuable contribution you can make. See [`Adapting to another zero-turn`](#adapting-to-another-zero-turn) and open a PR with your `params.scad` SECTION 1.
- 🛠️ **Custom carrier PCB** — the power/kill-chain/ESP32 board lives in [`hardware/pcb/`](hardware/pcb/) (schematic, placement, netlist, BOM). Remix it for your machine.
- See [`CONTRIBUTING.md`](CONTRIBUTING.md) for the safety-gated workflow. Good first issues are labeled `good first issue`.

## License & safety

Open source under the [MIT License](LICENSE). ⚠️ **This drives a machine with large blades that can kill** — it's released for education/research; you are solely responsible for safe construction, testing, supervision, and local-law compliance. Keep blades disconnected until every failsafe is proven.

*A personal robotics project by [Zoheb Alvi](https://zohebalvi.com).*
