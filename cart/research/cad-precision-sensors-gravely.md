# CAD Precision — Sensors + Gravely ZT X 52 (Job A + Job B)

Compiled 2026-06-25. Every number below is tied to a manufacturer/official source URL.
**Never design to a "rounded" distributor number** where an official drawing dimension exists.
Vendor CAD downloaded to `/Users/zohebalvi2/autonomous-mower/cad/vendor/`.

---

# JOB A — SENSOR MECHANICAL SPECS + CAD

## A1. Slamtec RPLidar A1M8 — base-diameter dispute RESOLVED

**Verdict: there is no single "base diameter," because the A1M8 base is a teardrop / water-drop
shape, NOT a circle.** The three conflicting numbers are three *different* features:

| Cited "diameter" | What it actually is | Authoritative value | Notes |
|---|---|---|---|
| **~70 mm** | the **rotating scan-core turret/cap** (round spinning top) **AND** the round end of the teardrop body | turret **⌀70.04 mm (+0.20/0)**; body round-end width **70.28 mm (+0.20/0)** | this is why "70" shows up for two features |
| **~96.8 mm** | the **body footprint LENGTH** (long axis of the teardrop) — misread as a "diameter" | **96.74 mm (+0.20/0)** | this is a length, not a diameter |
| **~98.5 mm** | distributor "overall size" rounding (often 98.5 × 70 × 55 packaging spec) | NOT an official drawing dimension | do NOT design to it |

**Definitive geometry — from Slamtec official LD108 datasheet, Fig 5-2 "Mechanical Dimensions of RPLIDAR A1":**

| Spec | Value | Notes |
|---|---|---|
| Base/body footprint (teardrop, NOT round) | **96.74 mm (L) × 70.28 mm (W)**, both +0.20/0 | long axis × round-end width |
| Rotating scan-core turret ⌀ | **⌀70.04 mm (+0.20/0)** | the spinning cap above the plate |
| Bottom centering boss ⌀ | **⌀32 mm** | central hub on underside — use as a register feature |
| Overall height (to top of cap) | **51 mm (±0.20)** | dim chain 21 / 26.50 / 31.50 / 42 / 51. Distributors round to ~55 |
| Scan/laser plane height | ~35–42 mm band (callout 35.14) | the laser exit window sits below the cap top |
| **Mounting holes** | **4 × ⌀3.4 mm** — callout reads literally "4-⌀3.4" | **NOT 3 holes.** ⌀3.4 clears M3 (resellers say "M2.5") |
| Hole pattern (trapezoid, symmetric about long axis) | **top pair 56 mm apart; bottom pair 40 mm apart; 70 mm between the two rows** | all ±0.05 |
| Hole coords vs turret axis (X across, Y along) | top holes **(±28, +28)**; bottom holes **(±20, −42)** | 56→±28, 40→±20 |
| Cable/connector exit | at the **narrow (pointed) tip** of the teardrop, on the bottom PCB above the motor | motor PH1.25-3P (5V/CTRL/GND) + core PH1.25-4P; faces down/out |
| Weight | **170 g** typical | MISC table (dev-kit-with-USB ~190 g per resellers) |

### Printed top-plate design summary (copy-ready)
- 4 × ⌀3.4 mm clearance holes (M3), **trapezoid** pattern: top edge 56 mm apart, bottom edge
  40 mm apart, **70 mm between rows**, symmetric about the long axis.
- Optional ⌀32 mm boss recess at the turret axis as a register.
- Keep a clearance slot for connector + cable at the **pointed/motor end**.
- Body envelope to clear: **96.74 × 70.28 mm**; the ⌀70.04 cap spins above the plate (height 51).

**Datasheet:** `https://bucket.download.slamtec.com/.../LD108_SLAMTEC_rplidar_datasheet_A1M8_v2.2_en.pdf`
(host blocks automated fetch). Byte-identical official mirrors used to read Fig 5-2:
Seeed v3.0 `https://files.seeedstudio.com/products/114992561/LD108_SLAMTEC_rplidar_datasheet_A1M8_v3.0_en.pdf` ·
Farnell `https://www.farnell.com/datasheets/3176118.pdf`

**CAD:** best = official Slamtec STEP on **TraceParts** (free account required):
`https://www.traceparts.com/en/product/shanghai-slamtec-co-ltd-laser-radar-rplidar-a1m8-kit?Product=90-28042022-033875`
· 3DContentCentral mirror (free account) `https://www.3dcontentcentral.com/parts/supplier/SLAMTEC/175649.aspx`.
No login-free direct STEP found. No-login community STL (fit-check only, not authoritative):
Printables `https://www.printables.com/model/95188-rplidar-a1-case`, Thingiverse `thing:4309677`.
**→ Design the plate to the datasheet numbers above, not to a community STL.**

## A2. Raspberry Pi Camera Module 3 — Standard AND Wide

Official: `https://datasheets.raspberrypi.com/camera/camera-module-3-standard-mechanical-drawing.pdf`
(downloaded → `cad/vendor/picam3_std_mech_drawing.pdf`) ·
Wide drawing `https://pip-assets.raspberrypi.com/categories/1207-design-files/documents/RP-008155-DS-1-camera-module-3-wide-mechanical-drawing.pdf` ·
Product brief `https://datasheets.raspberrypi.com/camera/camera-module-3-product-brief.pdf`.

> Product brief states: *"The PCB size and mounting holes remain the same as for Camera Module 2…
> Camera Module 3 is several millimetres taller."* → **Standard & Wide share the identical PCB,
> hole pattern, and 10.8 × 10.8 mm lens-housing footprint; they differ only in lens barrel ⌀,
> Z-height, and optics.**

| Spec | Standard | Wide | Source |
|---|---|---|---|
| PCB bounding box | **25.0 × 23.862 × 1.12 mm** (PCB) | same | mech drawing (24 = rounded 23.862) |
| Module total height (Z) | **11.5 mm** | **12.4 mm** | brief p.3 |
| Mounting holes | **4 × ⌀2.2 mm** (corner pattern) | same | drawing "ø2.2" |
| Annular pad around hole | ⌀4.75 mm | same | drawing |
| Horizontal hole pitch | **21.0 mm** (2.0 mm inset each side of 25) | same | drawing |
| Vertical hole pitch | **≈14.5 mm** (bottom row 7.3 mm above bottom edge for FPC) | same | drawing |
| Lens housing footprint | 10.8 × 10.8 mm square | same | drawing |
| **Lens barrel ⌀** | **⌀5.75 mm** | **⌀6.95 mm** | drawing |
| Optical center (horizontal) | centered, **12.5 mm from each side** | same | drawing |
| Sensor | Sony IMX708, 11.9 MP, 4608×2592 | same | brief p.5 |
| Focal length / ratio | 4.74 mm / F1.8 | 2.75 mm / F2.2 | brief p.5 |
| **FoV (diag / horiz / vert)** | **75° / 66° / 41°** | **120° / 102° / 67°** | brief p.5 |
| Ribbon cable | 200 mm 15×1 mm FPC | same | brief |

> ⚠️ Prompt said "21 × 12.5 mm ⌀2.2" — horizontal **21 mm** and **⌀2.2** confirmed, but the official
> drawing's vertical hole pitch is **~14.5 mm**, not 12.5 (the "12.5" on the drawing is the optical
> half-width, 25/2). For exact hole coordinates use the official STEP.
> ⚠️ Design the lens pocket for the **Wide's larger ⌀6.95 mm barrel + 12.4 mm Z** and it fits both.

**CAD (free, no login):** official STEP zip
`https://pip-assets.raspberrypi.com/categories/1207-design-files/documents/RP-008154-DS-1-camera-module-3-step.zip`
— **already downloaded** → `cad/vendor/cam_module3_step/Camera_module_3_std_model_simple.stp`
and `..._wide_model_simple.stp`.

## A3. Overhead clearance sensors (tree-limb / GPS-mast protection)

### A3a. JSN-SR04T waterproof ultrasonic (primary pick)

Separate-transducer ultrasonic; 3 board revs (v1.0/v2.0/v3.0), v3.0 current.
Sources: ProtoSupplies v3.0 `https://protosupplies.com/product/jsn-sr04t-v3-0-waterproof-ultrasonic-range-finder/` ·
v3.0 datasheet PDF `https://shop.tavir.hu/wp-content/uploads/datasheet-sen-uh-sr04t-v3.pdf` ·
v2.0 datasheet `https://www.makerguides.com/wp-content/uploads/2019/02/JSN-SR04T-Datasheet.pdf` ·
`https://components101.com/sensors/jsnsr04t-waterproof-ultrasonic-sensor-pinout-datasheet-working-application-alternative`.

| Spec | Value | Source |
|---|---|---|
| Probe body (metal cylinder) ⌀ × length | **⌀21.5 mm × 19 mm** | ProtoSupplies v3.0 |
| Probe outer flange/ring ⌀ | **⌀25 mm** | ProtoSupplies |
| Recommended panel mounting-hole ⌀ | **~⌀23 mm** (rubber grommet grips it) | tavir/ProtoSupplies |
| Cable length | **2.5 m** | tavir / ProtoSupplies |
| Control board L×W×H (v3.0) | **41 × 28 × 20 mm** (height incl. transformer can) | ProtoSupplies v3.0 |
| Control board L×W×H (v2.0) | **42 × 29 × 12 mm** | v2.0 datasheet |
| Board mounting holes | **4 × M3** (corners) — exact spacing NOT published, MEASURE (~36×23 on the 41×28 board) | tavir p.8 |
| Sensing range | **23–600 cm** (v3.0); v2.0 20–600; components101 lists 25–450 | tavir / datasheets |
| Beam / cone angle | **75° total (±37.5°)** | tavir / v2.0 |
| Frequency | 40 kHz | all |
| Operating voltage | **3.0–5.5 V** (5 V recommended) | ProtoSupplies/tavir |
| Interface | Trig/Echo (HC-SR04-style, 20 µs trigger) + serial modes | tavir |

> Probe is waterproof; **the control board is NOT** — put the board in a dry housing, probe through
> a ⌀23 mm hole. No official STEP/STL from the (anonymous) maker; community models exist.

### A3b. VL53L1X Time-of-Flight (alternative)

Raw ST chip package: **4.9 × 2.5 × 1.56 mm** (ST datasheet `https://www.st.com/resource/en/datasheet/vl53l1x.pdf`).
Range up to **~4 m (400 cm)**, **FoV 27°** (programmable ROI down to ~15°), I²C, 940 nm Class-1 laser.

**Pololu #3415 carrier — best for a mount (free STEP + DXF + dimensioned drawing, all downloaded):**

| Spec | Value | Source |
|---|---|---|
| Board bounding box | **12.7 × 17.8 × 1.2 mm** (PCB; ~2 mm w/ parts) | Pololu dimension diagram |
| Mounting holes | **2 × ⌀2.2 mm** (for #2 / M2), at diagonally-opposite corners | Pololu diagram |
| Hole inset | **2.5 mm from each edge** → ~7.7 mm horiz × ~12.7 mm (0.5″) vert center-to-center | Pololu diagram |
| Header | 7-pin 2.54 mm: VDD, VIN, GND, SDA, SCL, XSHUT, GPIO1 | Pololu |
| Range (this carrier) | up to **400 cm** | Pololu |

Pololu CAD (no login — **downloaded**): STEP `cad/vendor/pololu_vl53l1x_carrier.step` ·
drill DXF `cad/vendor/pololu_vl53l1x_drill.dxf` · dimension PDF `cad/vendor/pololu_vl53l1x_dimensions.pdf`
(`https://www.pololu.com/file/0J1195/...-carrier-model.step`, `.../0J1193/irs11a-drill.dxf`, `.../0J1194/...-dimension-diagram.pdf`).

Adafruit #3967 alt: board **25.5 × 17.5 × 4.6 mm**, M2.5 holes, STEMMA QT I²C
(`https://www.adafruit.com/product/3967`; CAD/EagleCAD in `https://github.com/adafruit/Adafruit-VL53L1X-PCB`,
exact hole spacing not tabulated — use the Pololu carrier for exact hole geometry).

## A — downloaded CAD inventory (`cad/vendor/`)

| File | Component | Format | Source / login |
|---|---|---|---|
| `cam_module3_step/Camera_module_3_std_model_simple.stp` | Pi Cam 3 Standard | STEP AP214 | RPi official, no login |
| `cam_module3_step/Camera_module_3_wide_model_simple.stp` | Pi Cam 3 Wide | STEP AP214 | RPi official, no login |
| `picam3_std_mech_drawing.pdf` | Pi Cam 3 mech drawing | PDF | RPi official, no login |
| `pololu_vl53l1x_carrier.step` | VL53L1X Pololu #3415 | STEP AP214 | Pololu, no login |
| `pololu_vl53l1x_drill.dxf` | VL53L1X drill guide | DXF | Pololu, no login |
| `pololu_vl53l1x_dimensions.pdf` | VL53L1X dimension diagram | PDF | Pololu, no login |
| (RPLidar A1M8) | — | STEP login-gated (TraceParts) | design to datasheet numbers above |
| (JSN-SR04T) | — | no official CAD | design to dims above |

---

# JOB B — GRAVELY ZT X 52 (Kohler, ~2021, model 915256-class)

## Model-number map (TWO different machines share the "ZT X 52" name)
- **915256 / 915257 / 915174** — the **Kohler 7000-powered ZT X 52** (~2019–2021). **THIS IS THE TARGET.**
  PartsTree splits 915256 into 3 serial breakpoints: **000101–029999 / 030000–059999 / 060000+**.
- **918010** — Kohler ZT X 52, later SKU numbering (same family).
- **918011** — the **current Kawasaki FR691V** ZT X 52, a **redesigned heavier chassis** with different
  published dimensions — do NOT use its spec sheet for a 915256 retrofit.

Sources: Jack's ZTX lookup `https://www.jackssmallengines.com/jacks-parts-lookup/manufacturer/gravely/zero-turn-lawn-mowers/ztx` ·
PartsTree 915256 (SN 060000+) `https://www.partstree.com/models/915256-ztx-52-gravely-52-zero-turn-mower-24hp-kohler-sn-060000-above`.

## B1. Dimensions / spec sheet

### Target — Kohler ZT X 52, model 915256 (PUBLISHED via dealer listings)
| Spec | Value |
|---|---|
| Overall length | 77.5 in |
| Overall width (chute down) | 63.4 in |
| Overall height | 40.9 in |
| Deck | 52 in, 3-blade, 11-ga fabricated X-Factor |
| Cutting height | 1.5–4.5 in, 13 positions |
| Front caster tires | 11 × 6-5 |
| Rear drive tires | 20 × 10-8 |
| Weight | 615 lb |
| Fuel | 2.8 gal |
| Engine | Kohler 7000 Pro Twin, 24 HP / 725 cc V-twin |
| Transaxles | Hydro-Gear ZT-2200 (some aggregations say "EZT" — confirm on unit) |
| Speed | 7 mph fwd / 3 mph rev |

Sources: AE Outdoor Power 915256 `https://aeoutdoorpower.com/products/gravely-zt-x-52-52-24hp-kohler-7000-v-twin-zero-turn-lawn-mower-915256` ·
Mowers at Jacks `https://www.mowersatjacks.com/product-details/gravely/915256`.
**Caveat:** no single clean Gravely-hosted 915256 spec PDF loaded (dealer pages JS-rendered / blocked
fetch); numbers are consistent across dealer listings — **confirm against the spec decal / operator's
manual on the machine, and measure for the retrofit.** **Wheelbase is NOT published — must be measured.**

Cross-check (DIFFERENT machine) — current Kawasaki 918011: L 74.5 / W 55.6 (chute up) 66.7 (down) /
H 46 in, 695 lb, 3.5 gal, FR691V 726 cc, EZT transaxles, 22 in plush high-back seat w/ slider
(`https://www.allmachines.com/mowers/gravely-zt-x-52-kawasaki`).

## B2. Steering / lap-bar (control arm) assembly — KEY DELIVERABLE

There is **no IPL section literally named "Steering" or "Lap Bar."** On the 915256 IPL the lap bars
live in **"Controls" (list controls-13)**; the steering rods tying them to the transaxle arms are in
**"Parking Brake" (parking-brake-8)**.
Source: `https://www.partstree.com/models/915256-ztx-52-gravely-52-zero-turn-mower-24hp-kohler-sn-060000-above/controls-13/`

| Ref | Part # | Description |
|---|---|---|
| 1 | **05107153** | HANDLE, STEERING (RED) — LH lap-bar handle (the tube you'd clamp) |
| 2 | **05107053** | HANDLE, STEERING – RH (RED) |
| 3 | **05179653** | ARM, CONTROL – UPPER (RED) |
| 4 | **09155500** | ARM, STEERING – LH LOWER (MACHINED) |
| 5 | **09155400** | ARM, STEERING – RH LOWER (MACHINED) |
| 6 | **05278900** | GRIP – HANDLEBAR (foam/rubber over the handle) |
| 8 | 05501334 | BSHG-SLV .342 × .627 × 1.331 (pivot sleeve bushing, inches) |
| 14 | 04764151 | BRKT, STEERING |
| 15 | 04990951 | BRKT, STEERING |
| 16 | 05160400 | DAMPER, STRAIGHT MOUNT |
| 17 | 05171400 | COUPLER, DAMPER MOUNT |
| 18 | 05501001 | BSHG-FLG .500 × .750 × .750 × .125 (flange pivot bushing) |

Linkage (parking-brake-8): LINKAGE STEERING RH, ROD STEERING LINKAGE LH, POST STEERING LINK MOUNTING.

### Lap-bar tube OD — is it published?
**NO. The lap-bar / steering-handle tube outer diameter is NOT published in any IPL, parts diagram,
spec sheet, or operator's manual.** The only dimensioned numbers in the Controls section are the
**pivot bushings** (sleeve .342 ID × .627 OD × 1.331 long; flange .500 × .750), which govern the
pivot pin — **not** the bar tube. Gravely treats the handle tubes as machined weldments with no
published cross-section.

**Realistic expectation (must be caliper-verified):** ZT lap-bar handle tubes in this
commercial-residential class are almost universally **round steel tube ~1.0 in (25.4 mm) OD**,
commonly **1.0–1.25 in (25–32 mm)** OD, ~0.083–0.120 in wall. → Design the actuator clamp as an
**adjustable/shimmable band in the ~25–32 mm window**, then **measure the actual 05107153/05107053
handle tube OD on the machine** (confirm round vs flattened-grip section). Note foam grip 05278900
adds diameter — decide whether to clamp over the grip or on bare tube below it.

## B3. Seat + seat-frame mounting
Source: `.../915256-...-sn-060000-above/seat-25/` and `.../frame-5/`

| Part # | Description |
|---|---|
| **05181300** | SEAT – ZTX (22 in high-back) |
| **09461053** | PLATE – SEAT – ZTX 2022 (seat mounting pan) |
| **09484351** | PLATE, ADJUSTABLE SEAT TRACK (fore/aft slider) |
| **04756451** | WLDMT, ADJUSTABLE SEAT LATCH |
| **09448000** | ROD – SEAT PIVOT |
| **03654200** | SWITCH – SEAT (operator-presence — autonomy interlock to satisfy/bypass) |
| 05501231 | BSHG-FLG .38 × .580 × .667 × .750 (seat pivot bushing) |
| 08300021 | SPRING, SEAT |

- Suspension: spring-type + foam pad; seat pivots forward on ROD 09448000, slides on track 09484351.
- **Published:** mount type + part IDs. **MUST MEASURE:** seat-pan bolt pattern / slot spacing and
  seat-track hole spacing (off plate 09461053 and track 09484351). Seat switch 03654200 = the
  interlock to address for autonomy.

## B4. Deck mounting (52")
The deck **hangs from the deck-lift system**, not a separate subframe.
Source: `.../deck-lift-12/` and `.../deck-mount-23/`

| Part # | Description | Section |
|---|---|---|
| **05246051** | DECK LIFT SHAFT WELDMENT | Deck Lift |
| **05246151** | WLDMT – REAR DECK PIVOT (rear hanger) | Deck Lift |
| **05113900** | LINK, DECK (HOLE-LONG) (front hanger link) | Deck Lift |
| 04869251 | PEDAL, DECK LIFT (foot lift) | Deck Lift |
| 06700220 | PIN, BOWTIE .091 × 1.875 (hanger retainer) | Deck Lift/Mount |
| **02004500** | LINK, DRAG (deck drag link) | Deck Mount |
| 07500327 | BSHG, DECK LIFT PIVOT | Frame |

- Deck suspended on front links (05113900) + rear pivot weldment (05246151), raised by deck-lift
  shaft (05246051) via foot pedal (04869251); pin-retained hangers; height set by HOC pin assembly.
- **Published:** part IDs + hanging arrangement. **MUST MEASURE:** all deck-attachment coordinates,
  hanger-pin spacing, deck-to-frame clearances.

## B — bottom line for the retrofit
- **Published & citable:** all part numbers / section structure (PartsTree 915256); overall L/W/H,
  weight, tire sizes, cut range, fuel, engine.
- **NOT published — must caliper/measure on the machine:** **lap-bar tube OD** (most critical for
  actuator clamps — expect ~25–32 mm round steel, verify on handles 05107153/05107053),
  **wheelbase**, **seat-pan bolt pattern & seat-track slot spacing**, **all deck-hanger coordinates**.
- **Confirm the serial number** stamped on the frame to pick the right IPL breakpoint
  (000101–029999 / 030000–059999 / 060000+) before ordering parts.
