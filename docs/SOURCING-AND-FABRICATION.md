# Sourcing & Fabrication

Where to get the CAD, drawings, and parts — and how to have the retrofit brackets **machined in metal** instead of (or in addition to) 3D-printed. Every link below was verified live (July 2026); items that couldn't be byte-verified are flagged.

> **The honest state of the base-machine CAD:** nobody publishes a downloadable 3D model of the exact Gravely ZT X 52. What *does* exist is (a) generic zero-turn CAD you can use as a visual/proportional proxy, and (b) rich **exploded parts diagrams + manuals** that give exact part numbers, geometry, and dimensioned drawings. For a retrofit, (b) is far more useful. The **retrofit components**, by contrast, mostly *do* have official STEP files — see §2.
>
> Model-number note: the Kohler-engine ZT X 52 is Gravely **915256** (older) / **918010** (later 24 HP Kohler 7000). **915280** is the Limited Edition; **915257 / 918011** are the Kawasaki siblings (same frame/deck, different engine).

---

## 1. Base machine — Gravely ZT X 52

### 1a. Illustrated Parts Lists / exploded diagrams (best for exact geometry + part numbers)
| Resource | Link | Notes |
|---|---|---|
| Jack's Small Engines — ZT X model index | https://www.jackssmallengines.com/jacks-parts-lookup/manufacturer/gravely/zero-turn-lawn-mowers/ztx | Pick **915256** + your SN range |
| Jack's — 915256 ZT X 52 (SN 060000+) deck/spindles/blades | https://www.jackssmallengines.com/jacks-parts-lookup/manufacturer/gravely/zero-turn-lawn-mowers/ztx/915256-060000-ztx-52 | Exact deck, spindle, idler geometry with callouts |
| PartsTree — 918011 ZT X 52 (same frame/deck) | https://www.partstree.com/models/918011-ztx-52-gravely-52-zero-turn-mower-23hp-kawasaki-fr-sn-000101-above | Alternate OEM diagram set |
| BW Machinery — ZT X series parts list (PDF) | https://bwmachinery.com.au/wp-content/uploads/2020/02/Spare-Parts-list-for-Gravely-ZT-X-series.pdf | Full downloadable exploded manual (10 MB+) |
| Gravely official parts lookup | https://www.gravely.com/en-us/parts | OEM source of truth for part numbers |

### 1b. Manuals (dimensioned drawings + specs)
| Resource | Link | Notes |
|---|---|---|
| ZT X Operator's Manual (covers 915256) | https://www.manualslib.com/manual/3102541/Gravely-Zt-X.html | View/download, no login; spec section + assembly figures |
| Ariens/Gravely official portal (serial-gated) | https://www.ariens.com/en-us/manualsDownload | Enter serial for the exact OEM operator + parts manual |

### 1c. Kohler 7000 (KT735 / 24 HP) engine
| Resource | Link | Notes |
|---|---|---|
| Kohler 7000 Service Manual (32 690 03) — **best free dimensional source** | https://resources.kohler.com/power/kohler/enginesUS/pdf/32_690_03_EN.pdf | 8.2 MB, verified; sectional/dimensional drawings + torque specs |
| Kohler 7000 spec/brochure | https://resources.kohler.com/power/kohler/enginesUS/pdf/7000_Series.pdf | Overall envelope, mounting, shaft |
| Jack's — KT735 exploded diagrams | https://www.jackssmallengines.com/jacks-parts-lookup/manufacturer/kohler-engine/7000-series-kt715-kt725-kt730-kt735-kt740-kt745/kt735 | Exact engine geometry |

### 1d. Generic zero-turn CAD (visual proxy only — NOT dimensionally the ZT X 52)
| Resource | Link | Format |
|---|---|---|
| Zero-turn mower (GrabCAD) | https://grabcad.com/library/zero-turn-mower-1 | CAD (free login) |
| Zero Turn Mower v1 (Free3D) | https://free3d.com/3d-model/zero-turn-mower-v1--617446.html | .obj / .stl |
| Mower models (CGTrader) | https://www.cgtrader.com/3d-models/mower | mixed free/paid |

> **How to use these for bracket design:** work from the Jack's / PartsTree exploded diagrams + the BW Machinery PDF for frame-rail, spindle, and transaxle geometry; confirm the few critical dims (lap-bar tube OD, frame tube, seat) by **measuring the actual machine** (they're already the SECTION 1 params in `cad/params.scad`). The generic CAD is for renders and mock-ups, not manufacturing.

---

## 2. Retrofit components — official CAD & drawings (mostly free STEP!)

Run `cad/vendor/fetch_vendor_cad.sh` to download the verified free files into `cad/vendor/`.

| Component | 3D CAD | Drawing / datasheet | Login? |
|---|---|---|---|
| **Pixhawk 6C** (Holybro) | STEP — https://docs.holybro.com/autopilot/pixhawk-6c/download | Dims (84.8×44×12.4 mm) — https://docs.holybro.com/autopilot/pixhawk-6c/dimensions | No |
| **simpleRTK2B** (ZED-F9P) | **STEP 8.35 MB** — https://www.ardusimple.com/wp-content/uploads/2026/04/AS-RTK2B-F9P-L1L2-NH-03-R00.step | PCB PDF — https://raw.githubusercontent.com/ardusimple/simpleRTK2B/master/Mechanical/simpleRTK2B_PCB.PDF | No |
| **RPLidar A1M8** (Slamtec) | **IGES 19 MB** — https://download-en.slamtec.com/api/download/rplidar-core-a1m8-r1-model-3d-igs/2.0?lang=netural | 2D drawing PDF — https://download-en.slamtec.com/api/download/rplidar-core-a1m8-r1-model-2d-pdf/2.0?lang=en · Datasheet — https://download-en.slamtec.com/api/download/rplidar-a1m8-datasheet/3.2?lang=en | No |
| **PA-14P actuator** (Progressive Automations) | **STEP** — https://cdn.shopify.com/s/files/1/0061/7735/7891/files/PA-14P.stp | DWG — https://cdn.shopify.com/s/files/1/0061/7735/7891/files/PA-14P.DWG · Datasheet — https://f.hubspotusercontent40.net/hubfs/7717445/PDFs/Actuator%20datasheets/PA-14P%20datasheet.pdf | No |
| **Raspberry Pi 5** | **STEP (zip)** — https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-010083-CA-1-rpi-5%203D%20STEP%20-%20No%20Graphics%20small%20file.zip | Mech drawing — https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf | No |
| **Pi Camera Module 3** | **STEP (zip)** — https://pip-assets.raspberrypi.com/categories/1207-design-files/documents/RP-008154-DS-1-camera-module-3-step.zip | Mech drawing — https://datasheets.raspberrypi.com/camera/camera-module-3-standard-mechanical-drawing.pdf | No |
| **AI HAT+** (Hailo-8L) | *(no official 3D — GrabCAD only)* | Product brief — https://datasheets.raspberrypi.com/ai-hat-plus/raspberry-pi-ai-hat-plus-product-brief.pdf (≈66×56.5 mm) | No |
| **u-blox ANN-MB-00** antenna | *(no official 3D)* | Datasheet (82×60×22.5 mm) — https://content.u-blox.com/sites/default/files/documents/ANN-MB_DataSheet_UBX-18049862.pdf | No |
| **ESP32-DevKitC V4** | **DXF** — https://dl.espressif.com/dl/schematics/esp32_devkitc_v4_dimensions.dxf | Dims PDF — https://dl.espressif.com/dl/schematics/esp32_devkitc_v4_dimensions.pdf | No |
| **BTS7960 / IBT-2** | *(generic clone, no CAD)* | Chip DS — https://www.infineon.com/assets/row/public/documents/10/57/infineon-bts7960-ds-en.pdf ; board ≈50×50×43 mm | No |
| **JSN-SR04T** ultrasonic | *(generic, no CAD)* | PCB ≈41×28.5 mm, transducer Ø23 mm (datasheet is image-based) | No |

**Gaps → GrabCAD** (free account) for community STEP of the Pixhawk 6C, RPLidar, AI HAT+, and the generic modules. TraceParts / 3DFindIt are alternates.

---

## 3. Machining the brackets in metal

The 24 brackets are designed as 3D prints (ASA/PETG). To make them in **6061 aluminum** (or 304/316 stainless), split them by geometry:

### 3a. Which part → which process (from `cad/stl/MANIFEST.csv`)
- **Flat / thin plates → laser-cut sheet (+ bend)** — deliver **DXF**: `estop_face` (4 mm), `relay_lid` (6 mm), `badge` (4 mm), `upper_shelf` (10 mm), `lapbar_yoke_top/bottom` (10 mm), `lidar_top_plate` (14 mm), `gps_top_plate` (24 mm).
- **3D geometry (pockets, bosses, contours) → CNC milled** — deliver **STEP**: the clamps (`gps_clamp_a/b`, `rail_anchor_*`), masts (`lidar_mast_*`), `estop_pedestal_a/b`, `camera_base/cradle`, `relay_box`, `throttle_servo_bracket`, `box_foot`, `equipment_plate`.

Flat DXFs for the sheet-metal parts are exported to `cad/dxf/` by `cad/export_dxf.sh`.

### 3b. Instant-quote suppliers (US, verified)
| Supplier | Processes | Files | Materials | Best for |
|---|---|---|---|---|
| **SendCutSend** (sendcutsend.com) | Laser, **CNC mill**, bend, tap, weld | STEP, DXF | 6061, 7075, 304, 316 | **Best all-rounder — one vendor for flat + CNC** |
| **OSH Cut** (oshcut.com) | Laser (sheet+tube), bend, tap | DXF, STEP | 6061, 7075, 304, 316 | Flat/bent, cheap nested batches (no anodize) |
| **Protolabs** (protolabs.com) | **CNC mill/turn**, sheet, weld | STEP, IGES | 6061, 7075, 304, 316 | Fastest CNC (1-day, in-house) |
| **Xometry** (xometry.com) | Laser, waterjet, **CNC**, bend, weld | STEP, DXF | 6061, 7075, 304, 316 | Broad marketplace |
| **Protolabs Network** (hubs.com) | CNC + sheet via 250+ shops | STEP; DXF (sheet) | CNC 6061/7075/304/316; sheet Al skews 5052 | Often cheapest mixed batch |
| **eMachineShop** (emachineshop.com) | CNC, laser, waterjet, bend, tap | STEP, DXF, native | 6061, 7075, 304, 316 | No-minimum US one-stop, free US ground |
| **Ponoko** (ponoko.com) | Laser, bend, tap | STEP, DXF, SVG | 6061, 304 | Flat parts needing **anodize** |
| **PCBWay** (pcbway.com) | CNC 3/5-axis, sheet | STEP | 6061, 7075, 304, 316 | Cheap small-qty CNC (China → slower ship) |

*None publish a hard per-part minimum (effectively no MOQ). Ponoko's ~$50/part is the one published single-part floor. OSH Cut has no anodize. Protolabs Network / RapidDirect sheet-aluminum skews to 5052/5754 — confirm 6061 sheet if required (5052 actually bends better).*

**Recommended prototype plan:** flat brackets as **DXF at OSH Cut** (nested, cheap, 1–2 day US) + 3D mounts as **STEP at SendCutSend or Protolabs**. Or run the whole 24-part mixed order through **SendCutSend / eMachineShop** (both do flat + CNC, US, no min). Scale past ~100 pcs → re-quote at PCBWay/RapidDirect for volume.

### 3c. What a shop needs to quote a CNC part
1. **STEP (.step/.stp)** — the universal solid CAD format (exact surfaces/holes). IGES / Parasolid / native also fine. Instant platforms price + DFM-check from STEP alone.
2. **A 2D dimensioned drawing (PDF)** — required when the part has **threads/tapped holes** (callout + fit class), tolerances tighter than default, surface-finish callouts, or GD&T/inspection needs. Encodes what a 3D model can't (tolerances, roughness, material, finish, revision, title block).
3. **Spell out:** material (e.g. 6061-T6), finish (as-machined ≈ Ra 3.2 µm baseline), quantity, threads, and which dims are critical.
4. **Tolerances:** default is **±0.005 in (±0.127 mm)** / ISO 2768-m. Leave general dims there for the cheapest/fastest parts; only tighten the few that matter (bearing bores, mating faces) — tighter = pricier + slower.

### 3d. STL → machinable — the important gotcha
**STL is wrong for CNC.** It's a triangle *mesh* — no true curves, no dimensions, no tolerances; a circle becomes a polygon. Converting STL→STEP just wraps the faceted blob; CAM can't cleanly machine it. To get a real solid:
- **OpenSCAD cannot export STEP natively** (only STL/OFF/AMF/3MF in 3D; **DXF/SVG in 2D**). So:
  - **Flat parts →** export **DXF** straight from OpenSCAD (`projection()`) — done in `cad/export_dxf.sh`. Sheet-metal shops take DXF directly.
  - **3D parts →** re-model the load-bearing features natively in **FreeCAD** or **CadQuery** (using the OpenSCAD dims as reference) and export **STEP**. FreeCAD's mesh→solid works but is faceted/imprecise — re-modeling parametrically is strongly preferred.

---

## 4. Our fabrication package (what we send a supplier)
For each part: **STEP** (CNC) or **DXF** (sheet) + a **dimensioned drawing PDF** (material 6061-T6, finish, qty, threads, critical dims, ISO 2768-m general tolerance). Aluminum brackets should be **anodized** (type II) or bead-blasted for outdoor corrosion resistance; stainless where fasteners thread directly into the part.

*Sources verified July 2026. Vendor prices/lead times are typical ranges, not guarantees. GrabCAD community files were not byte-verified (login-gated) — confirm in-browser.*
