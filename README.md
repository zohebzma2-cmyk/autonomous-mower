# Autonomous Zero-Turn Retrofit Kit

Turn a seated zero-turn mower (reference: **Gravely ZT 52"**) into a self-driving, trainable robot mower with **RTK GPS + LiDAR + camera + AI**, built from a **~$1k** parts budget, weatherproofed to live outdoors, and **reproducible on any ZTR** by re-measuring a handful of dimensions.

> ⚠️ A 52" mower deck can kill. Read [`docs/BUILD.md` §0 Safety](docs/BUILD.md) before powering anything. Blades stay OFF until drive + navigation + every failsafe is proven.

## What's here

```
autonomous-mower/
├── README.md                  ← you are here
├── docs/BUILD.md              ← full build & SAFETY spec (architecture, wiring, training, go/no-go)
├── cart/
│   ├── BOM.md                 ← bill of materials (~$1,048 w/ Hailo) + trim levers
│   └── cart.html              ← branded shopping page: search links + copy buttons
├── cad/
│   ├── params.scad            ← ★ MASTER PARAMETERS — change SECTION 1 to fit any ZTR
│   ├── utils.scad             ← shared modules (tube clamps, bosses, bed-splits, gaskets)
│   ├── mower.scad             ← parametric mower mock (context)
│   ├── assembly.scad          ← everything placed on the mower
│   ├── enclosure.scad         ← brain-box equipment plate + shelf + seat feet
│   ├── actuator_brackets.scad ← lap-bar yokes + frame anchors (the steering parts)
│   ├── gps_mast.scad          ← RTK antenna mast mount
│   ├── lidar_mount.scad       ← RPLidar front-mast mount
│   ├── camera_mount.scad      ← tilt camera cradle w/ sun hood
│   ├── controls_bracket.scad  ← e-stop pedestal, PTO relay box, throttle servo bracket
│   ├── export_stl.sh          ← exports every PRINT_* part to STL + checks bed-fit
│   ├── stl/                   ← exported STLs + MANIFEST.csv (bed-fit report)
│   ├── renders/               ← PNG renders of parts + full assembly
│   └── vendor/                ← real vendor STEP models (Pi 5, Cam 3) + SOURCES.md
├── viewer/                    ← interactive 3D web viewer (rotate the whole machine)
└── firmware/                  ← ArduPilot params + Pi companion notes (phase 1+)
```

## The architecture in one line

**ArduPilot Rover** on a Pixhawk owns drive + RTK navigation + failsafes (skid-steer fits a ZTR natively); a **Raspberry Pi 5 + Hailo-8L** rides shotgun for LiDAR obstacle-stop and camera AI, talking to the FC over MAVLink. See [`docs/BUILD.md §1`](docs/BUILD.md).

## Training (all three, built in order)
1. **Teach-and-repeat** — drive it once, it repeats the RTK path.
2. **Boundary → auto-coverage** — drive the perimeter, software fills the rows.
3. **AI learns the yard** — camera/LiDAR semantic map refines over runs (Hailo).

## How to work the CAD

```bash
# edit cad/params.scad SECTION 1 to your machine, then:
cd cad
openscad assembly.scad                 # see the whole machine
./export_stl.sh                        # export all printable parts + bed-fit check
# slice the stl/*.stl in FlashPrint for the Adventurer 3 (ASA or PETG)
```

**Adapting to another zero-turn:** open `cad/params.scad` → SECTION 1, re-measure the lap bars / frame / seat, re-render, re-slice. That's the whole port.

## Status
Design + CAD + cart complete. **Not built yet.** This is a multi-month build requiring fabrication and careful, safety-gated commissioning — not plug-and-play. See [`docs/BUILD.md §12`](docs/BUILD.md) for honest limitations.
