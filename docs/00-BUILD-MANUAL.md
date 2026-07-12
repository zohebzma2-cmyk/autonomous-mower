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

## Build time & effort

Realistic for a competent maker (comfortable with electronics, basic fabrication, ArduPilot).
First-timers add learning-curve time; the safety-gated commissioning should **not** be rushed.

| Phase | Hands-on | Elapsed | Notes |
|------|---------:|---------|-------|
| 0 · Measure machine | ~0.5 h | — | gates the **actuator-bracket** print; do first |
| Parts procurement | — | **1–2 wk** | Amazon ~2 days; **ArduSimple (EU/customs) is the long pole** |
| Print 24 core parts (+8 Phase-3 attachment brackets) | ~1 h setup | **~1 wk** printer | ~50 h printer time, ~250–300 g ASA/PETG — mostly unattended; overlaps procurement |
| 3 · Bench brain box + **kill chain** | 6–10 h | | wire power, e-stop FIRST, test FC/RTK/RC with **no actuators** |
| 4 · Flash + configure | 3–5 h | | ArduPilot Rover + ESP32 firmware + companion bring-up |
| 5 · Mechanical + harness + calibrate | 10–16 h | | actuators/yokes + through-pin, masts, sensors, run the harness, fail-to-neutral test |
| 6 · Commission (go/no-go) | 10–20 h | **2–3 wk** | jack-stands → blades-off teach → tune RTK/incline/overhead → **blades last**; iterative |
| **TOTAL** | **≈ 50–80 person-hours** | **≈ 4–8 weeks calendar** | calendar gated by parts shipping + the deliberately-slow commissioning |

**Headline:** ~**50–80 hours of hands-on work** over ~**4–8 weeks** of calendar time. The printing and
parts-waiting are mostly passive; the variable is **Phase 6 commissioning** (RTK tuning, actuator
calibration, and safety validation take as long as they take — that's a feature, not a delay).

## Current status
Design ✅ (exact-spec, 32 printable parts incl. badge + Phase-3 attachment brackets, all fit the 150 mm bed) · Parts ✅ (Amazon cart
loaded; vendor orders queued) · Firmware ✅ (ESP32 controller + ArduPilot params) · Software ✅
(companion + Tesla UI, teach/coverage, safety: incline/overhead/obstacle, cameras — **18/18 tests**) ·
Wiring ✅ (full pinouts + kill chain + diagram). **Not yet physically built** — Phases 0–6 above.
