# Print Guide — every part, brim-ready

Printer: **FlashForge Adventurer 3** (150×150×150 mm) · Slicer: **FlashPrint 5**
All 23 parts fit the bed (see `cad/stl/MANIFEST.csv`). Two ways to get a brim on every part:

- **Easiest — use the brim-baked STLs in `cad/stl/brim/`.** Each already has a one-layer brim welded on. Print these with **slicer brim OFF** (don't double up). Peel the brim off after printing.
- **Or — print the plain STLs in `cad/stl/` and enable FlashPrint's brim:** Expert mode → *Additions* → **Brim** on, width = the value in the table below, **Raft off**.

## Material & why
- **ASA** for anything that lives outside in sun/heat or carries load (UV-stable, strong). ASA warps the most → it *needs* the brim.
- **PETG** is fine for internal/low-stress parts (tough, easy).
- **Avoid PLA outdoors** — sags in summer heat, goes UV-brittle.
- Print temps per your setup; ASA wants an enclosure/no draft to stop warping (the brim is your backup).

## Brim width logic
`4 mm` thin flat plates (curl-prone edges) · `5 mm` default · `6 mm` load-bearing clamps · `8 mm` tall / small-footprint / vibration parts (highest tip risk).

## Per-part table

| Part | Qty | Orient (face DOWN) | Brim | Supports | Material | Walls / Infill |
|------|----:|--------------------|-----:|----------|----------|----------------|
| **Brain enclosure** |||||||
| equipment_plate | 1 | plate flat, standoffs up | 5 | no | PETG | 3 / 25% |
| upper_shelf | 1 | plate flat, standoffs up | 5 | no | PETG | 3 / 25% |
| box_foot | 4 | base pad down | 5 | no | PETG | 3 / 30% |
| **Actuator brackets — STRUCTURAL** |||||||
| lapbar_yoke_bottom | 2 | clamp split-face down | 6 | under clevis | **ASA** | **4 / 40%** |
| lapbar_yoke_top | 2 | clamp split-face down | 6 | no | **ASA** | **4 / 40%** |
| rail_anchor_bottom | 2 | largest flat face down | 6 | light | **ASA** | **4 / 40%** |
| rail_anchor_top | 2 | largest flat face down | 6 | no | **ASA** | **4 / 40%** |
| **GPS mast** |||||||
| gps_clamp_a | 1 | clamp face down, socket up | 6 | under socket | ASA | 3 / 30% |
| gps_clamp_b | 1 | clamp face down | 6 | no | ASA | 3 / 30% |
| gps_top_plate | 1 | disc flat, socket up | 5 | no | ASA | 3 / 30% |
| **LiDAR mast** |||||||
| lidar_base_a | 1 | clamp flat face down | 6 | no | ASA | 3 / 30% |
| lidar_base_b | 1 | clamp flat, platform up | 6 | under platform | ASA | 3 / 30% |
| lidar_mast_lower | 1 | **flange down, truss up** | **8** | minimal (truss) | ASA | 4 / 30% |
| lidar_mast_upper | 1 | **flange down, truss up** | **8** | minimal (truss) | ASA | 4 / 30% |
| lidar_top_plate | 1 | disc flat down | 5 | no | ASA | 3 / 30% |
| **Camera** |||||||
| camera_cradle | 1 | back/faceplate down | 5 | hood overhang | PETG | 3 / 25% |
| camera_base | 1 | **foot down (tall)** | **8** | no | PETG | 3 / 25% |
| **Controls / safety** |||||||
| estop_pedestal_a | 1 | **clamp+base down, post up (139 mm TALL)** | **8** | leaning-post overhang | **ASA** | 4 / 30% |
| estop_pedestal_b | 1 | clamp flat face down | 6 | no | ASA | 3 / 30% |
| estop_face | 1 | flat (thin) | 4 | no | ASA | 3 / 30% |
| relay_box | 1 | open-top up, base down | 5 | no | ASA | 3 / 30% |
| relay_lid | 1 | flat (thin) | 4 | no | ASA | 3 / 30% |
| throttle_servo_bracket | 1 | base down | 5 | light | ASA | 3 / 30% |

## Batching (fit several per bed job)
The Adventurer 3 bed is 150 mm, so you can gang small parts. Suggested plates (leave ~8 mm between parts; each part keeps its own brim):
- **Plate A (ASA):** lapbar_yoke ×4 (both halves ×2 sides) + rail_anchor ×4 — print the steering set together.
- **Plate B (ASA):** gps_clamp_a + gps_clamp_b + gps_top_plate + lidar_base_a + lidar_base_b.
- **Plate C (ASA, tall — print alone or pairs):** lidar_mast_lower + lidar_mast_upper (both 112 mm; OK side by side).
- **Plate D (ASA):** estop_pedestal_a (TALL — alone), then pedestal_b + face + relay_box + relay_lid + throttle_servo_bracket as a second job.
- **Plate E (PETG):** equipment_plate, then upper_shelf, then box_foot ×4 + camera parts.

## Print order (match the build phases)
1. **Steering first** (Plate A) — you'll bench-test actuators before anything else.
2. Brain enclosure (Plate E) — to mount and bench-test the electronics.
3. Masts + sensors (Plates B, C) once drive works.
4. Controls/safety (Plate D) — but the **e-stop hardware itself goes in from day one** even before its pretty pedestal is printed.

> Reminder from `docs/BUILD.md`: the lap-bar yokes and rail anchors are load-bearing — ASA, 4 walls, ≥40% infill, and a through-pin on final install. A brim alone won't save an under-built structural part.
