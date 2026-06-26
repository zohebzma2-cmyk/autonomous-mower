# Autonomous ZTR Retrofit — Final Order Sheet

**Status:** Design COMPLETE · Amazon cart LOADED · 5 vendor-direct items to place.
Reference machine: Gravely ZT 52" · Date: 2026-06-26 · Prices verified live this session unless noted.

> This file supersedes the earlier estimate-based `cart.html` / `amazon_cart.html`. These are the
> actual products added/sourced, with real prices read off the live pages.

---

## A. In your Amazon cart now (24 units, verified in-stock + spec) — ≈ $908.90

| # | Product (as added) | ASIN | Qty | Price |
|---|--------------------|------|----:|------:|
| 1 | Progressive Automations 12V actuator, 4″/100 mm, 169 lbs, **pot. feedback**, IP65 | (search "Progressive Automations 4\" 169lbs feedback") | 2 | 310.78 |
| 2 | dstfuy E-stop, 22 mm, **IP65, 1 NC** | B0BHQ6JQS4 | 1 | 9.96 |
| 3 | BTS7960 (IBT-2) 43 A dual H-bridge (2-pack) | B0BGR92TCD | 1 | 13.37 |
| 4 | FlySky FS-i6X + iA6B receiver | B0744DPPL8 | 1 | 59.99 |
| 5 | Recoil 40 A 5-pin SPDT relays + sockets + fuse holders (2-pack) | B08BHR2RM7 | 1 | 13.99 |
| 6 | ANNIMOS 25 kg metal-gear waterproof servo | B07GK1G5FV | 1 | 17.99 |
| 7 | DC-DC buck 12→5 V 5 A (2-pack) | B0DQL5HFQP | 1 | 16.59 |
| 8 | Maxmoral LM2596 adjustable buck (2-pack) | B07MKQXNWG | 1 | 7.99 |
| 9 | Slamtec RPLidar A1M8 360° 2D | B07TJW5SXF | 1 | 99.00 |
| 10 | XINYIELE IP67 enclosure 221×170×114 mm (incl. glands + plate) | B0C5TKF5CN | 1 | 19.88 |
| 11 | 10/2 AWG tinned marine duplex, 50 ft | B00MI5I98K | 1 | 65.95 |
| 12 | 14/2 AWG tinned marine duplex, 50 ft | B00MI59JD4 | 1 | 32.95 |
| 13 | NAOEVO 22 AWG 6-color silicone, 60 ft ea | B0CMLGS4YG | 1 | 24.48 |
| 14 | MG Chemicals 422B silicone conformal coating | B008O9YGQI | 1 | 49.99 |
| 15 | Permatex 22058 dielectric grease | B000AL8VD2 | 1 | 10.49 |
| 16 | XT60 connectors, 20 pairs + 80 pc heat-shrink | B0GYZ6M37R | 1 | 9.99 |
| 17 | Anyongora waterproof inline fuse holders + 40 fuses | B0CL7MLY6T | 1 | 7.99 |
| 18 | 1220-pc 304 SS M3/M4/M5/M6 socket-head kit | (search "1220pcs 304 stainless M3 M4 M5 M6") | 1 | 21.99 |
| 19 | Snlazp 12-circuit fuse block **w/ negative bus**, waterproof | B0CP7NLFVD | 1 | 29.95 |
| 20 | Kadrick 520-pc M2–M5 brass heat-set inserts (3D printing) | B0D5V3TZLB | 1 | 13.59 |
| 21 | uxcell 20 mm OD aluminium tube (4×200 mm) | B09FNX7BRX | 1 | 17.19 |
| 22 | BEST CONNECTIONS split wire loom 3-pack | B07JR7727L | 1 | 19.95 |
| 23 | SanDisk Extreme 64 GB microSDXC A2 V30 | SDSQXAH-064G | 1 | 34.85 |
| | **Amazon subtotal** | | | **≈ 908.90** |

Already selected in the cart (Zohebzma@gmail.com) — review and place when ready. Nothing checked out.

**Swap-to-save options before you order:** microSD $34.85 and conformal $49.99 are 3rd-party/large-can —
cheaper equivalents exist (1-pack microSD ~$13, 55 ml brush-on 422B ~$15) if you want to trim ~$55.

---

## A2. On-unit display (touchscreen) — pick one, ~$60–110  *(not yet in cart)*

The same control UI (`software/`) runs full-screen on this, mounted on the unit; your iPad shows the
same screen over WiFi.

| Option | What | ~$ | Notes |
|--------|------|---:|-------|
| **Raspberry Pi Touch Display 2** (DSI) | 7″ official touchscreen | $60 | cleanest integration; **hard to read in direct sun** |
| 7″ HDMI capacitive touchscreen (1024×600) | generic HDMI+USB-touch | $55–75 | works on any Pi; same sunlight caveat |
| Sunlight-readable HDMI panel (~1000 nit) | high-brightness 7″ | $130–200 | **daytime-visible** upgrade if the screen must be read outside |

**Decision (auto-mode):** add the **Pi Touch Display 2 to the PiShop order** (§B) — it's ~$60 direct vs
$102.76 marked-up on Amazon, and it bundles shipping with the Pi 5 / Hailo / Camera you're already
buying there. Move to a sunlight-readable panel later only if field daytime visibility matters.

---

## B. Vendor-direct — must order from these sites (NOT on Amazon) — ≈ $596

| Item | Vendor | URL | Price |
|------|--------|-----|------:|
| **Pixhawk 6C** flight controller (genuine — avoid eBay clones) | Holybro | https://holybro.com/products/pixhawk-6c | $165.99 |
| **simpleRTK2B Budget** (u-blox ZED-F9P) RTK board | ArduSimple | https://www.ardusimple.com/product/simplertk2b/ | €172 (~$186) |
| **ANN-MB-00** multiband GNSS antenna (IP67) | ArduSimple | https://www.ardusimple.com/product/ann-mb-00-ip67/ | €53.80 (~$58) |
| **Raspberry Pi AI HAT+** (Hailo-8L, 13 TOPS) | PiShop | https://www.pishop.us/product/raspberry-pi-ai-hat-13-tops/ | $76.95 |
| **Raspberry Pi 5, 8 GB** (board) | PiShop / CanaKit / Adafruit | https://www.pishop.us/product/raspberry-pi-5-8gb/ | ~$80 |
| **Pi Camera Module 3** (FRONT — obstacle + vision) | PiShop | https://www.pishop.us/product/raspberry-pi-camera-module-3/ | $29.25 |
| **Pi Camera Module 3** (REAR feed) | PiShop | https://www.pishop.us/product/raspberry-pi-camera-module-3/ | $29.25 |
| **Raspberry Pi Touch Display 2** (7″ DSI, on-unit screen) | PiShop | https://www.pishop.us/product/raspberry-pi-touch-display-2/ | ~$60 |
| | | **Vendor subtotal** | **≈ 685** |

### A3. Perception / safety sensors (added for camera view + overhead + incline)
- **Front + rear cameras** — 2× Pi Camera 3 (above), shown as live feeds in the UI; front does obstacle + grass vision (Hailo). Pi 5 has 2 CSI ports.
- **Overhead clearance sensor (tree-limb / height detection)** — **JSN-SR04T waterproof ultrasonic** (~$10, Amazon) mounted forward/up; stops the machine before the GPS mast strikes a low branch. *(add to Amazon cart — exact part being finalized by research)*
- **Incline safety** — uses the **Pixhawk IMU** (no new hardware): max-slope cutoff (~15° rollover limit) + mow up/down, not across. See `docs/BUILD.md`.

### A4. Control electronics (required by the wiring — `docs/WIRING.md`)
| Item | Where | ~$ | Why |
|------|-------|---:|-----|
| **Holybro PM02 power module** (or buy Pixhawk 6C **+PM02** variant) | Holybro | $25 | clean 5V to Pixhawk POWER1 + battery V/I sensing (do NOT skip) |
| **ESP32 DevKit** | Amazon | $8 | lap-bar **position controller** — closes the loop FC→pot→BTS7960 (`firmware/lapbar_controller`) |
| **JSN-SR04T waterproof ultrasonic** | Amazon | $10 | overhead/tree-limb clearance (forward-up) |
| **+1 40 A relay** (DRIVE-RELAY for the kill chain) | Amazon | $7 | e-stop drops actuator motor power; the Recoil 2-pack covers PTO + drive |
| | | **+ ≈ $50** | |

Notes: ArduSimple ships from the EU — expect EUR→USD conversion + import shipping/duties. Tip: order the
Pixhawk 6C from Holybro and both ArduSimple items together to save on shipping; PiShop covers the 3 Pi items.

---

## C. Grand total & status

| | |
|---|------:|
| Amazon cart (parts) | ≈ $909 |
| Vendor-direct | ≈ $596 |
| On-unit touchscreen (A2) | + ~$60 |
| **Full genuine build** | **≈ $1,565** |
| Optional later: dual-antenna heading +~$100 · own RTK base +~$150 · sunlight display +~$120 | |

**Design:** ✅ complete — `docs/BUILD.md`, `docs/PRINT_GUIDE.md`, `cad/` (23 parts, brim-baked, bed-fit), `viewer/`.
**Filament/printer/mower:** you already have. **Software** (ArduPilot, Mission Planner, NTRIP): free.

## D. Build-readiness checklist (what happens after parts land)
1. **Print** all brackets/enclosure plate from `cad/stl/brim/` per `docs/PRINT_GUIDE.md` (ASA/PETG).
2. **Read the model/serial plate** under the seat; **measure** lap-bar OD/travel → set `cad/params.scad` SECTION 1 → re-slice the actuator brackets.
3. **Bench-build** the brain box; verify FC + RTK fix + RC + e-stop with **no actuators**.
4. Follow `docs/BUILD.md §11` go/no-go sequence: jack stands → blades OFF → open-area teach-and-repeat → blades last.
