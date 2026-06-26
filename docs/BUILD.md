# Autonomous Zero-Turn Retrofit — Build & Safety Spec

**Machine (confirmed):** Gravely **ZT X 52, ~2021, Kohler** (residential seated ZTR, twin lap bars) —
24 hp **Kohler 7000 Pro Twin** (725 cc), **electric PTO clutch** (Ogura GT, 12 V, relay-switched ✓),
Hydro-Gear EZT/ZT-2200 transaxles, 11-ga 52″ fabricated deck, 695 lb, **no factory ROPS**. → The PTO relay
design is correct; the engine brand is irrelevant to us (throttle servo + ignition-kill are brand-agnostic);
the GPS mast mounts to the **seat-frame upright / fabricated square post** (no roll-bar to clamp).
**Goal:** a seat-mountable retrofit that makes a gas ZTR drive itself, with GPS + LiDAR + camera + AI, trainable by driving it once, reproducible on any zero-turn by re-measuring a handful of dimensions.
**Status:** design + CAD + cart. Not yet built. Read the Safety chapter before powering anything.

---

## 0. The one thing that matters most: SAFETY

A 52" deck spins ~3 lb of steel at ~18,000 fpm tip speed. An autonomous bug here is not a crash — it's an amputation or a fatality. Every design choice below is subordinate to the kill chain.

### The kill chain (defense in depth — any ONE stops the blades + drive)
1. **Physical E-stop** (latching 22 mm mushroom) — cuts the actuator power bus *and* opens the PTO relay *and* grounds the engine kill wire. Independent of all software.
2. **RC kill switch** — a channel on the FlySky transmitter held by a human spotter. Loss of RC link = failsafe (ArduPilot RC failsafe → HOLD + disarm). Range ~300 m.
3. **ArduPilot failsafes** — GPS-loss, low-battery, geofence breach, watchdog → configurable to HOLD (stop) and disengage PTO.
4. **Companion watchdog** — the Pi sends a heartbeat; if the Pi (LiDAR/vision) dies, the FC stops. If the FC dies, a hardware watchdog relay drops the actuator bus.
5. **Seat / presence override** — keep the OEM seat switch in the interlock during all early testing so a human can kill it by standing up.

### Non-negotiable rules
- **PTO (blades) stays OFF for every test until drive + navigation + all failsafes are proven** over many hours with blades removed or deck disengaged.
- First motion tests: **engine off, rear wheels on jack stands**, verify lap-bar actuators move correctly and e-stop cuts them.
- Then: **blades removed**, low-speed yard laps.
- Blades come on **last**, in an open area, spotter on the RC kill, after a written go/no-go checklist (see §11).
- Geofence the property with a hard margin from the house, road, people, and water.

---

## 1. Architecture

```
                ┌──────────────────────────── BRAIN BOX (IP65, on seat) ───────────────────────────┐
   RTK antenna ─┤  simpleRTK2B ── UART ─► Pixhawk 6C (ArduPilot Rover)  ◄─ MAVLink ─► Raspberry Pi 5 │
   (on mast)    │                          │  │  │                                   │  + Hailo-8L   │
                │                 PWM/relay │  │  └─ RC receiver (override + kill)    │  + Pi Cam 3   │
                │                           │  └──── analog feedback (actuator pots)  │   │           │
                └───────────────────────────┼──────────────────────────────────────-─┼───┼───────────┘
                                            ▼                                         ▼   ▼
                          ┌─────────────────┴─────────────┐                  RPLidar A1 (front mast)
                  L actuator   R actuator   PTO relay   throttle servo
                   │            │            │            │
              left lap bar  right lap bar  blade clutch  engine throttle
```

- **Pixhawk 6C + ArduPilot Rover** = the autonomy core. It owns drive, RTK navigation, missions, and failsafes. Battle-tested; we do not write our own low-level control.
- **Raspberry Pi 5 + Hailo-8L** = companion. Owns LiDAR obstacle detection and camera AI. Talks to the FC over MAVLink; its main authority is "STOP / slow / clear."
- **Skid steering:** ArduPilot's `Frame Type = skid-steer`. Left/right throttle channels map to the two lap-bar actuators. The mower already does differential drive via its hydros — we just position the levers.

---

## 2. Drive control — lap-bar actuators

- **Actuators:** 2× 12 V linear actuators, **100 mm (4″) stroke**, **position-feedback pot**. Reference unit = **Progressive Automations PA-14P** (exact CAD dims in `params.scad`): body Ø38.1 mm, retracted 241.6 / extended 343.2 mm pin-to-pin, **1/4″ (6.35 mm) clevis pin both ends**, 6-pin Molex feedback (0–10 kΩ).
  **⚠ Weatherproofing gap:** the genuine PA-14P is **IP54 (splash only), NOT IP66** — for an outdoor mower add a **rubber rod boot + a shield over the rod/gland**, or source a true IP66 actuator. (The Amazon listing claims "IP65/169 lb"; PA-14P 4″ datasheet is 35–150 lb / IP54 — verify the actual unit on arrival.)
  **Force:** a hydrostatic lap bar + return-to-neutral spring needs ~**100–220 N**; the 150 lb (≈667 N) SKU is ample. Do not use hobby micro-actuators (Actuonix L16). Confirm force on YOUR machine with a fish scale.
- **Linkage:** the printed `lapbar_yoke` clamps the bar; a clevis + pushrod ties to the actuator rod. The actuator body anchors to the frame rail via the printed `rail_anchor`. **Drill the lap bar and add a through-pin** — a clamp alone can creep under vibration.
- **Closed loop:** the feedback pot tells the FC the true lever position → ArduPilot servo output drives the H-bridge until position matches command. Calibrate full-fwd / neutral / full-rev endpoints in Mission Planner.
- **Neutral safety:** spring return + actuator default-to-center; on power loss the bars must fall to neutral (machine coasts to stop), never stick in gear. Verify this mechanically.

---

## 3. Localization — RTK GPS

- **±2 cm** with RTK vs ±3 m plain GPS — the difference between mowing rows and driving into the house.
- **Corrections (NTRIP):** stream RTCM3 from a base. Cheapest: a free public **CORS / state-DOT NTRIP** mount within ~20 km, over a phone hotspot. If none nearby, add a second simpleRTK2B as your own base (~+$150) for full independence.
- **Heading:** a single antenna gives position but heading comes from motion (bad at low speed / pivot turns). Upgrade path: **moving-baseline dual antenna** for true heading — strongly recommended before trusting tight zero-turn pivots. Budget allows single now, dual later.
- Antenna goes **high on a mast, on a ground plane**, clear of the engine and ROPS steel (multipath).

---

## 4. Perception & safety sensors — obstacle, height, incline, cameras

- **RPLidar A1 (2D, 360°) — horizontal obstacle:** Pi reads the scan; anything inside a stop-zone (~2 m) in the path → HOLD. Simple, reliable, runs first.
- **Overhead clearance — tree-limb / height detection:** the horizontal LiDAR **cannot see overhead**, so a **forward/up-facing JSN-SR04T waterproof ultrasonic** (or VL53L1X ToF) watches the height above/ahead. If clearance drops below the machine's tallest point (the **GPS mast**, ~1.6 m incl. margin) → STOP, so the mast/antenna never strikes a low branch. (`safety.MIN_OVERHEAD_M`.)
- **Incline / hill safety — IMU (no new hardware):** the Pixhawk IMU gives roll/pitch. A **max-slope cutoff (~15°, the ZTR side-slope rollover limit)** refuses to arm or move above it (`safety.MAX_SLOPE_DEG`), with a 12° caution band. **Mowing strategy on slopes: drive up/down the fall line, not across** (side-slope is the rollover axis) — the coverage planner orients rows accordingly on graded zones.
- **Cameras (front + rear):** 2× Pi Camera 3 (Pi 5 has two CSI ports), shown as **live feeds in the control UI**. Front feeds Hailo vision (grass-vs-not, obstacle classification, row-edge following); rear is situational. Phase-3 AI runs on the Hailo so the Pi CPU stays free.
- **Sensor-fusion order of authority:** physical E-stop > RC kill > **incline cutoff** > **overhead stop** > LiDAR obstacle > ArduPilot nav > camera-AI hints. AI never *adds* motion authority; it only refines or vetoes. This policy lives in `software/companion/safety.py` (unit-tested).

---

## 5. Software stack

| Layer | Software | Role |
|------|----------|------|
| Flight controller | **ArduPilot Rover** (latest stable) | drive, RTK nav, missions, failsafes |
| Ground station | **Mission Planner** or **QGroundControl** | setup, calibration, mission upload, live monitor |
| Companion | **Pi OS + Python + MAVSDK/pymavlink** | LiDAR stop logic, MAVLink bridge |
| AI | **Hailo runtime + a segmentation model** | vision inference |
| Corrections | **NTRIP client** (in Mission Planner or on Pi) | RTK RTCM3 |

Key ArduPilot params (starting point, tune on machine): `FRAME_CLASS=2` (rover), skid steering enabled, `SERVO1/SERVO3` = left/right throttle to the H-bridge, `GPS_TYPE`=RTK, `FENCE_ENABLE=1`, `FS_*` failsafes → HOLD, `RC_OPTIONS` kill switch, `MOT_PWM` for actuator endpoints.

---

## 6. Training — the three modes you asked for

All three ride on the same hardware; build them in order.

1. **Teach-and-repeat (do this first).** Drive the path once via RC; the FC logs RTK waypoints (`AUTO` mission record). Save it; the mower repeats that exact route. Most reliable, works today in ArduPilot.
2. **Boundary → auto-coverage.** Drive only the *perimeter* + obstacle outlines; software (ArduPilot mission planner "survey/grid" or a coverage planner on the Pi) auto-generates efficient back-and-forth rows to fill the boundary. Roomba-for-the-whole-yard.
3. **AI "learns the yard."** Camera/LiDAR build a semantic map over runs — learns grass vs beds vs obstacles, adapts row spacing, flags new objects. Most ambitious; layered last on the Hailo. Treat as assistive, not authoritative (see §4).

---

## 7. Power & wiring

- Source: the mower's existing **12 V battery** (engine alternator keeps it charged while running).
- **Buck converters:** 12→5 V 5 A (Pi + peripherals), 12→regulated (FC if needed). Fuse every branch at the battery with a **fuse block**; main breaker/kill in the E-stop path.
- Use **XT60 / Anderson** for power, locking JST/Molex for signal. Strain-relieve everything; vibration kills connectors.
- Keep actuator (noisy, high-current) wiring physically separated from GPS/signal wiring; twist + shield where they cross.

---

## 8. Weatherproofing (it lives outside, gets wet & dusty)

- **Brain box:** COTS **IP65 ABS enclosure**; our printed **equipment plate** organizes the boards inside. Glands (PG9) for every cable. **Conformal-coat** the PCBs; **dielectric grease** the connectors. Mount glands on the **bottom** face so water can't pool into them.
- **LiDAR & camera** aren't waterproof → printed hoods + a clear dome (bosses provided), and a "don't mow in rain" rule.
- **Actuators:** IP66 minimum; point the rod/gland **down**.
- Print structural parts in **ASA** (UV-stable) or **PETG**; avoid PLA outdoors (sags in heat, UV-brittle).

---

## 9. Printed parts (FlashForge Adventurer 3, 150³ mm)

| Part | File | Pieces | Notes |
|------|------|--------|-------|
| Equipment plate + shelf + feet | `enclosure.scad` | 1+1+4 | inside the IP65 box |
| Lap-bar yokes | `actuator_brackets.scad` | 2×(top+bottom) | **load-bearing — 4 walls, ≥40% infill** |
| Frame-rail anchors | `actuator_brackets.scad` | 2×(top+bottom) | load-bearing |
| GPS clamp + mast socket + top plate | `gps_mast.scad` | 3 | + user-supplied 20 mm tube |
| LiDAR base + 2 mast sections + top plate | `lidar_mount.scad` | 5 | truss mast, bolt-together |
| Camera cradle + base | `camera_mount.scad` | 2 | tilt-adjustable, sun hood |
| E-stop pedestal + face, relay box + lid, throttle bracket | `controls_bracket.scad` | 6 | safety hardware |

Print settings: ASA/PETG, 0.2 mm, 3–4 walls, 25–40% infill, brim on tall parts. ~250 g total.

---

## 10. Adapting to ANY zero-turn

Open `cad/params.scad` → **SECTION 1** and re-measure these on the target machine:
`LAP_BAR_TUBE_OD`, oval flags, `LAP_BAR_SPACING`, `LAP_BAR_TRAVEL`, `LAP_BAR_CLAMP_HEIGHT`, `FRAME_TUBE_W/H`, `SEAT_WIDTH/DEPTH`, `THROTTLE_LEVER_*`. Re-render, re-slice. Everything else is derived. That's the whole port from a Gravely to a Toro/Bad Boy/Spartan/Ferris/Scag.

---

## 11. Build sequence & go/no-go

1. Measure machine → set params → print all brackets.
2. Bench-build brain box (boards on plate, power, fuses). Bench-test FC + RTK fix + RC + e-stop with **no actuators**.
3. Mount actuators; **wheels on jack stands, engine OFF, blades OFF.** Verify lever motion, endpoints, neutral-on-power-loss, e-stop cuts power.
4. Engine on, jack stands, idle: verify drive direction & failsafes (pull RC = stop; trip fence = stop; GPS unplug = stop).
5. On ground, **blades OFF**, walking-pace teach-and-repeat in open area, spotter on RC kill.
6. Tune RTK/heading; add dual antenna if pivots wander.
7. Go/no-go checklist → blades ON in open area only, full session supervised. Expand area gradually.

**Go/no-go (all must be YES):** RTK fixed (not float)? Geofence set with house/road/people margin? E-stop test passed today? RC kill test passed today? Battery >50%? Bystanders clear? Spotter present with kill? Weather dry? If any NO → do not engage blades.

---

## 12. Honest limitations
- This is a **multi-month** build requiring fabrication (drilling/bolting brackets to your specific bars), wiring care, and patient calibration. It is not plug-and-play.
- Single-antenna RTK pivots are the weakest link until you add dual-antenna heading.
- $1k buys *parts*; it does not buy the commercial-grade redundancy of a $25k Greenzie system. Treat early runs as experimental and never leave it unsupervised near people, pets, or roads.
