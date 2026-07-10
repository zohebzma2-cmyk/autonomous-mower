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

## B. 3D parts — CNC milled (send a STEP)  ✅ STEP solids generated
These have pockets/bosses/contours → CNC from billet. **STL is not machinable**, so each has been converted to a **solid STEP** with `../stl_to_step.py` (CadQuery/OCP mesh-sew). The STEP files are faceted-but-valid closed solids that instant CNC quoters (SendCutSend, OSH Cut, Xometry) accept for upload. Regenerate locally with `python stl_to_step.py` → `../step/*.step` (gitignored, ~173 MB). For threaded/critical parts also send the dimensioned PDF.

| Part | STEP (regenerate → `step/`) | Envelope (X × Y × Z) | Qty |
|---|---|---|---|
| Enclosure foot | `step/PRINT_box_foot.step` | 40 × 40 × 26 mm | 1 |
| Equipment plate | `step/PRINT_equipment_plate.step` | 140 × 140 × 38 mm | 1 |
| Frame-rail anchor (lower) | `step/PRINT_rail_anchor_bottom.step` † | 57 × 71 × 46 mm | 1 |
| Frame-rail anchor (upper) | `step/PRINT_rail_anchor_top.step` † | 57 × 28 × 46 mm | 1 |
| GPS mast clamp A | `step/PRINT_gps_clamp_a.step` | 104 × 58 × 50 mm | 1 |
| GPS mast clamp B | `step/PRINT_gps_clamp_b.step` | 104 × 38 × 50 mm | 1 |
| LiDAR base A | `step/PRINT_lidar_base_a.step` | 60 × 89 × 28 mm | 1 |
| LiDAR base B | `step/PRINT_lidar_base_b.step` | 64 × 89 × 34 mm | 1 |
| LiDAR mast (lower) | `step/PRINT_lidar_mast_lower.step` | 82 × 82 × 112 mm | 1 |
| LiDAR mast (upper) | `step/PRINT_lidar_mast_upper.step` | 82 × 82 × 112 mm | 1 |
| Camera base | `step/PRINT_camera_base.step` | 44 × 44 × 50 mm | 1 |
| Camera cradle | `step/PRINT_camera_cradle.step` | 31 × 50 × 30 mm | 1 |
| E-stop pedestal A | `step/PRINT_estop_pedestal_a.step` | 93 × 83 × 139 mm | 1 |
| E-stop pedestal B | `step/PRINT_estop_pedestal_b.step` | 93 × 50 × 30 mm | 1 |
| Relay box | `step/PRINT_relay_box.step` | 76 × 56 × 45 mm | 1 |
| Throttle-servo bracket | `step/PRINT_throttle_servo_bracket.step` | 57 × 44 × 42 mm | 1 |

† The two rail-anchor meshes don't sew into a single closed shell, so their STEP is exported as a sewn surface solid (still uploads/quotes; re-model in FreeCAD if the shop wants a watertight B-rep).

*Regenerate the DXFs with `./export_dxf.sh`, the STEP solids with `python stl_to_step.py`, the drawing PDFs with `python export_drawings.py`. Bounding boxes auto-measured by `export_stl.sh` (MANIFEST.csv).*
