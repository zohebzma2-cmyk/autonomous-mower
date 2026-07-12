# Changelog

Milestones only — the blow-by-blow (with what forced every change) lives in
[DESIGN-LOG.md](DESIGN-LOG.md).

## Unreleased
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
