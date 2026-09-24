# Changelog

Milestones only — the blow-by-blow (with what forced every change) lives in
[DESIGN-LOG.md](DESIGN-LOG.md).

## Unreleased
- **8 new printable parts, 40 total** (`cad/sensor_mounts.scad`), all bed-gated and brim-baked:
  overhead sonar collar with a raised probe cup (JSN-SR04T sits face-up above the antenna),
  a split sun hood + braces + tilt yoke for the 7" Touch Display 2 on the brain-box lid, and
  the dual-RTK crossbar tee + antenna plates (replaces "print 2x gps_mast")
- Assembly shows the sonar and screen; `DUAL_ANTENNA=true` shows the crossbar. New gallery
  renders: `assembly_dual_rtk`, `closeup_sonar_baseline`, `closeup_display`, `sensor_mounts`
- GLB builder gains `retro_sonar` + `retro_display` nodes; viewer lists all 40 parts and loads a
  fresh decimated full-machine STL (was a prototype-era model)
- Adapting to RC / electric-drive mowers (tracked or wheeled): `docs/ADAPT-RC-MOWER.md` + `firmware/ardupilot/profiles/rc-tracked.parm`. The Pixhawk sits in front of the stock drive controller, so no actuators or ESP32 are needed
- Companion runs on Python 3.9 again (`from __future__ import annotations`), so the test suite passes on stock macOS
- Route ids no longer collide when two routes are saved in the same millisecond (was a flaky `test_teach_records_and_saves`; `get_route` could return the wrong route)
- Print queue, tool checklist, substitution guide (this file's sibling docs)

## 2026-07-12 — Phase 3: the whole rig
- Attachments designed + policy-coded with tests (45/45): self-dumping power bagger,
  DeWalt 60V blower/trimmer boom, FIMCO 30-gal tow sprayer with speed-proportional
  dosing, TPMS, ignition + choke sequence
- No-rut turn planner: smooth-U / 3-point-K headland turns (never pivots)
- 8 printable attachment brackets — 32 parts total, all bed-gated + brim-baked
- Site: accessory bay (interchangeable attachments), dump demo, animated turn
  physics, exploded view, X-ray, guided tour, AR
- Geofence: draw-on-map boundary, persisted, pushed to ArduPilot as an inclusion fence
- Hosted CI blocked by account billing → `scripts/check.sh` runs the same gates locally

## [v0.2-design](https://github.com/zohebzma2-cmyk/autonomous-mower/releases/tag/v0.2-design) — 2026-07-12
- Spec-true machine model: all four envelope numbers match the published ZT X 52
  figures exactly (1968 × 1610 × 1039 mm, 1321 mm deck)
- Blades + spindles in a hollow deck; multi-material GLB with baked animations
- Design log + constraints A–Z + ROADMAP-75 + machine-readable order sheet

## [fabrication-2026-07-10](https://github.com/zohebzma2-cmyk/autonomous-mower/releases/tag/fabrication-2026-07-10)
- Machinist package: 8 DXF flat parts + dimensioned PDFs + 16 STEP solids (30 MB zip)
- MowerCarrier Rev A carrier-PCB design package (power tree + kill chain + ESP32)

## [prototype-v1](https://github.com/zohebzma2-cmyk/autonomous-mower/releases/tag/prototype-v1) — 2026-06-26
- One-day design sprint: 23→24 printable parts, verified order sheet (~$1.6k),
  control software with sim, ESP32 fail-to-neutral firmware, ArduPilot params,
  wiring + kill chain, build manual — then open-sourced (MIT)
