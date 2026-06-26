# Autonomous Zero-Turn Retrofit — Bill of Materials (Cart)

**Reference machine:** Gravely ZT 52" (seated ZTR, twin lap bars)
**Architecture:** ArduPilot Rover core + Raspberry Pi 5 / Hailo companion
**Budget target:** under $1,000 — *honest total with Hailo included ≈ $1,015–1,055* (trim levers at bottom)
**Prices are ESTIMATES** (not live-verified). Buy used where the "Source" says eBay; buy **new** for anything safety-critical.

> Safety rule baked into sourcing: **never buy used** the RTK GPS, actuators, e-stop, or motor driver. Those failing = a 52" blade runs away. Used is fine for compute (flight controller, Pi).

---

## Phase 1 — Drive + RTK + Safety (a working autonomous mower)

| # | Part | Spec / why | Qty | Source | Est $ |
|---|------|-----------|-----|--------|------:|
| 1 | Flight controller (Pixhawk 6C class) | Runs ArduPilot Rover: skid-steer, RTK nav, failsafes | 1 | **eBay (used OK)** | 90 |
| 2 | RTK GPS kit (ArduSimple simpleRTK2B + antenna) | ±2 cm positioning via free NTRIP corrections | 1 | ArduSimple / Amazon (new) | 190 |
| 3 | Linear actuator 12V, 100 mm stroke, w/ position feedback, IP66 | Pulls each lap bar | 2 | Amazon (new) | 140 |
| 4 | Dual H-bridge motor driver (BTS7960 ×2 or Cytron) | FC drives actuators; reads feedback pot | 1 | Amazon (new) | 35 |
| 5 | RC transmitter + receiver (FlySky FS-i6X + iA6B) | **Manual override + wireless kill** (safety) | 1 | Amazon (new) | 60 |
| 6 | E-stop, 22 mm waterproof mushroom, latching | Hardware kill: cuts actuator power + PTO/ignition | 1 | Amazon (new) | 14 |
| 7 | Automotive relay + socket (40 A) | Switches the existing PTO blade clutch | 2 | Amazon (new) | 12 |
| 8 | Throttle servo (metal gear) | Sets engine RPM | 1 | Amazon (new) | 18 |
| 9 | DC-DC buck converters (12→5 V 5 A, 12→reg) | Clean power off mower battery | 2 | Amazon (new) | 20 |
| 10 | Fuse block + fuses + wiring + connectors (XT60, terminal blocks) | Power distribution + protection | 1 lot | Amazon | 45 |
| 11 | IP65 ABS enclosure (~200×150×100 mm) | The sealed "brain box" (our printed plate goes inside) | 1 | Amazon (new) | 30 |
| 12 | Cable glands PG9 assortment | Sealed wire entries | 1 lot | Amazon | 12 |
| 13 | Conformal coating + dielectric grease | Weatherproof the boards/connectors | 1 | Amazon | 15 |
| 14 | 20 mm aluminium tube (masts: GPS + LiDAR) | Raises antenna/LiDAR clear of metal | 1 | Amazon / hardware store | 18 |
| 15 | Stainless M3/M4/M5 fastener kit + brass heat-set inserts | For all printed brackets | 1 lot | Amazon | 30 |
| 16 | Rubber pads, ratchet straps, wire loom, zip ties | Mounting + vibration | 1 lot | Amazon | 22 |

**Phase 1 subtotal ≈ $751**

---

## Phase 2 — Perception (obstacle stop + auto-coverage)

| # | Part | Spec / why | Qty | Source | Est $ |
|---|------|-----------|-----|--------|------:|
| 17 | Raspberry Pi 5, 8 GB | Companion computer: LiDAR + vision, talks MAVLink to FC | 1 | Amazon (new) | 80 |
| 18 | microSD 64 GB (A2) | Pi OS | 1 | Amazon | 12 |
| 19 | RPLidar A1M8 (360° 2D) | Obstacle detection → emergency stop | 1 | Amazon (new) | 100 |

**Phase 2 subtotal ≈ $192**

---

## Phase 3 — AI vision

| # | Part | Spec / why | Qty | Source | Est $ |
|---|------|-----------|-----|--------|------:|
| 20 | Raspberry Pi AI Kit (Hailo-8L, 13 TOPS, M.2 HAT+) | Real-time grass/obstacle vision AI on the Pi | 1 | Amazon / RPi reseller (new) | 70 |
| 21 | Raspberry Pi Camera Module 3 | Wide-FOV camera for vision | 1 | Amazon (new) | 35 |

**Phase 3 subtotal ≈ $105**

---

## Grand total ≈ **$1,048**  *(Phase 1+2+3, Hailo included)*

### Trim levers to get under $1,000
- **Defer Hailo + Camera to later** → −$105 → **$943**. (You already have a Pi 5; AI vision is the least time-critical phase.)
- **Single-band RTK** (Waveshare LC29H ~$50 instead of ArduSimple ~$190) → −$140. Lower reliability/heading; acceptable for first trials, upgrade later.
- **Skip conformal coating** (use the sealed box + glands only) → −$15.
- Any one of these puts you under $1k with everything else intact.

### Not in cart (you already have / fabricate)
- 3D-printed brackets, mounts, enclosure plate — printed on your FlashForge (filament: **ASA or PETG**, ~250 g total).
- Mower's existing 12 V battery powers everything.
- Lap-bar through-pin: drill + clevis pin on final install (don't trust the clamp alone).
- Optional: small 12 V→USB-C PD board if you prefer powering the Pi separately.

### Free / subscription
- **ArduPilot Rover** firmware — free.
- **Mission Planner / QGroundControl** (GCS) — free.
- **RTK corrections (NTRIP)** — often free via your state DOT CORS network; else a base station (add ~$150 later for true independence).
