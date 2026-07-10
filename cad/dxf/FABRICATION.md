# Fabrication quote package

Send this sheet **plus the referenced files** to the shop (SendCutSend, OSH Cut, Protolabs, eMachineShop — see `../docs/SOURCING-AND-FABRICATION.md`).

## Global specs (apply to all parts unless noted)
- **Material:** 6061-T6 aluminium (use 304 stainless for any part a fastener threads directly into).
- **General tolerance:** ISO 2768-m (≈ ±0.1–0.3 mm) / ±0.005 in. Only bores + mating faces are critical.
- **Finish:** clear anodize (Type II) or bead-blast — outdoor corrosion resistance.
- **Quantity:** 1 each for the prototype (2× the `gps_*` and `lidar_*` parts if building the dual-antenna heading option).

## A. Flat parts — laser-cut sheet (send the DXF)  ✅ files ready in `dxf/`
| Part | File | Size (W × H) | Thickness | Qty |
|---|---|---|---|---|
| Upper shelf | `dxf/PRINT_upper_shelf.dxf` | 139 × 124 mm | 10 mm | 1 |
| Lap-bar yoke (lower) | `dxf/PRINT_lapbar_yoke_bottom.dxf` | 127 × 46 mm | 10 mm | 1 |
| Lap-bar yoke (upper) | `dxf/PRINT_lapbar_yoke_top.dxf` | 68 × 46 mm | 10 mm | 1 |
| GPS antenna plate | `dxf/PRINT_gps_top_plate.dxf` | 60 × 60 mm | 24 mm | 1 |
| LiDAR top plate | `dxf/PRINT_lidar_top_plate.dxf` | 124 × 124 mm | 14 mm | 1 |
| E-stop face | `dxf/PRINT_estop_face.dxf` | 58 × 58 mm | 3 mm | 1 |
| Relay lid | `dxf/PRINT_relay_lid.dxf` | 76 × 56 mm | 6 mm | 1 |
| Nameplate badge | `dxf/PRINT_badge.dxf` | 114 × 34 mm | 3 mm | 1 |

## B. 3D parts — CNC milled (send a STEP)  ⚠ STEP TODO
These have pockets/bosses/contours → CNC from billet. **STL is not machinable** — re-model each to a STEP solid in FreeCAD/CadQuery from the OpenSCAD dims (see the sourcing doc), then send the STEP + a dimensioned PDF for any threaded/critical part.

| Part | Source | Envelope (X × Y × Z) | Qty |
|---|---|---|---|
| Enclosure foot | `stl/PRINT_box_foot.stl` → STEP | 40 × 40 × 26 mm | 1 |
| Equipment plate | `stl/PRINT_equipment_plate.stl` → STEP | 140 × 140 × 38 mm | 1 |
| Frame-rail anchor (lower) | `stl/PRINT_rail_anchor_bottom.stl` → STEP | 57 × 71 × 46 mm | 1 |
| Frame-rail anchor (upper) | `stl/PRINT_rail_anchor_top.stl` → STEP | 57 × 28 × 46 mm | 1 |
| GPS mast clamp A | `stl/PRINT_gps_clamp_a.stl` → STEP | 104 × 58 × 50 mm | 1 |
| GPS mast clamp B | `stl/PRINT_gps_clamp_b.stl` → STEP | 104 × 38 × 50 mm | 1 |
| LiDAR base A | `stl/PRINT_lidar_base_a.stl` → STEP | 60 × 89 × 28 mm | 1 |
| LiDAR base B | `stl/PRINT_lidar_base_b.stl` → STEP | 64 × 89 × 34 mm | 1 |
| LiDAR mast (lower) | `stl/PRINT_lidar_mast_lower.stl` → STEP | 82 × 82 × 112 mm | 1 |
| LiDAR mast (upper) | `stl/PRINT_lidar_mast_upper.stl` → STEP | 82 × 82 × 112 mm | 1 |
| Camera base | `stl/PRINT_camera_base.stl` → STEP | 44 × 44 × 50 mm | 1 |
| Camera cradle | `stl/PRINT_camera_cradle.stl` → STEP | 31 × 50 × 30 mm | 1 |
| E-stop pedestal A | `stl/PRINT_estop_pedestal_a.stl` → STEP | 93 × 83 × 139 mm | 1 |
| E-stop pedestal B | `stl/PRINT_estop_pedestal_b.stl` → STEP | 93 × 50 × 30 mm | 1 |
| Relay box | `stl/PRINT_relay_box.stl` → STEP | 76 × 56 × 45 mm | 1 |
| Throttle-servo bracket | `stl/PRINT_throttle_servo_bracket.stl` → STEP | 57 × 44 × 42 mm | 1 |

*Regenerate the DXFs with `./export_dxf.sh`. Bounding boxes auto-measured by `export_stl.sh` (MANIFEST.csv).*
