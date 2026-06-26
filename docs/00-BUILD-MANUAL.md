# Autonomous ZT X 52 — Build Manual (start here)

The single entry point. This turns a **2021 Gravely ZT X 52 (Kohler)** into a self-driving,
iPad-controlled robot mower. Follow the phases in order. **Do not skip the safety gates.**

> ⚠️ A 52″ deck can kill. The blades stay **physically disconnected** until drive + navigation +
> every failsafe is proven (Phase 6). Read [`BUILD.md §0`](BUILD.md) before powering anything.

## Document map
| You want to… | Read |
|---|---|
| Understand the design + **safety** | [`BUILD.md`](BUILD.md) |
| **Buy the parts** | [`../cart/ORDER.md`](../cart/ORDER.md) · `../cart/order.html` |
| **Print** the brackets | [`PRINT_GUIDE.md`](PRINT_GUIDE.md) · STLs in `../cad/stl/brim/` |
| **Wire** it (pinouts, kill chain) | [`WIRING.md`](WIRING.md) · [`wiring-diagram.svg`](wiring-diagram.svg) |
| **Flash** firmware | `../firmware/ardupilot/rover_params.parm` · `../firmware/lapbar_controller/` |
| **Run** the control software | [`../software/README.md`](../software/README.md) |
| The exact machine specs | [`../cart/research/gravely-specs.md`](../cart/research/gravely-specs.md) |
| Adapt to a different ZTR | [`../cad/params.scad`](../cad/params.scad) SECTION 1 |

## Build sequence

**Phase 0 — Measure your machine.** Read the serial plate (under seat). Caliper the **lap-bar tube OD**
(unpublished, ~25–32 mm) and the lever travel. Put those into `cad/params.scad` SECTION 1.

**Phase 1 — Order.** Place the Amazon cart + the vendor-direct orders (Holybro / ArduSimple / PiShop)
from `cart/order.html`, including the **PM02, ESP32, ultrasonic, drive-relay** (ORDER §A4) and the
**2nd camera + display**. ≈ $1,565–1,615 total.

**Phase 2 — Print.** Slice everything in `cad/stl/brim/` (brims baked in — slicer brim OFF) per
`PRINT_GUIDE.md`. ASA/PETG. Includes the **logo nameplate** (`badge.scad` — set your brand name).

**Phase 3 — Bench-build the brain box.** Mount Pi 5 + Hailo + Pixhawk + RTK + bucks on the printed
equipment plate inside the IP67 box. Wire power per `WIRING.md §2`. **Wire & TEST the e-stop kill
chain (§3) FIRST.** Confirm: FC boots, RTK gets a fix (NTRIP), RC link + kill work, e-stop drops
drive power — **with no actuators connected**.

**Phase 4 — Flash + configure.** Flash ArduPilot Rover to the Pixhawk; load `rover_params.parm`;
flash `lapbar_controller.ino` to the ESP32. Bring up the companion: `python3 software/companion/app.py`
(sim first, then `--mav` to SITL, then the real FC). Open the UI on the iPad.

**Phase 5 — Mechanical, wheels on jack stands, ENGINE OFF, BLADES OFF.** Mount actuators + yokes
(drill the lap-bar through-pin). Calibrate the ESP32 pot endpoints + actuator direction. Verify
**fail-to-neutral** (cut e-stop / FC → bars center, machine would coast).

**Phase 6 — Commission (the go/no-go).** Follow `BUILD.md §11` exactly: jack-stands drive test →
blades-OFF open-area teach-and-repeat with a spotter on the RC kill → tune RTK/incline/overhead →
**blades last**, in an open area, supervised. Geofence with hard margins from house/road/people/water.

## Current status
Design ✅ (exact-spec, 24 printable parts incl. badge, all fit the 150 mm bed) · Parts ✅ (Amazon cart
loaded; vendor orders queued) · Firmware ✅ (ESP32 controller + ArduPilot params) · Software ✅
(companion + Tesla UI, teach/coverage, safety: incline/overhead/obstacle, cameras — **18/18 tests**) ·
Wiring ✅ (full pinouts + kill chain + diagram). **Not yet physically built** — Phases 0–6 above.
