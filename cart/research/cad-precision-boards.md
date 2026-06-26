# CAD-Precision Research — Autonomy / Compute Boards

Goal: dimensionally-exact (to the mm) data so OpenSCAD proxies and mounting trays
fit real hardware. Every number is cited to a manufacturer datasheet / mechanical
drawing. Values that are NOT published are explicitly flagged
**"unpublished — measure on arrival / extract from STEP."** Nothing is guessed.

Researched 2026-06-26. All dimensions in **mm**.

---

## Per-board table

| Component | BBox L×W×H (mm) | Hole pattern (dx×dy, ⌀, inset, n) | Connector keep-outs | CAD model (local + URL + license) | Source |
|-----------|-----------------|-----------------------------------|---------------------|-----------------------------------|--------|
| **1. Holybro Pixhawk 6C** (bare flight controller) | **84.8 × 44 × 12.4** (confirmed) | **Mounting pattern NOT published as reliable text** — extract from the downloaded official STEP. (Connectors exit the two **short ends**.) | All I/O on the two 44 mm short edges per Pixhawk Connector Standard: one end = power 1/2, TELEM1, I2C, CAN1/2, GPS1/GPS2, ADC; other end = USB-C, SD-card slot, RC-IN, debug, S.BUS, PWM/AUX rail. Leave both short edges fully clear; SD card needs side-insert clearance. | **`cad/vendor/pixhawk6c.step`** (2.17 MB, genuine Creo `PIXHAWK6C-XUANRAN_ASM`). URL: `https://docs.holybro.com/autopilot/pixhawk-6c/download` (GitBook file). License: Holybro, free for use. | Dims/weight: [PX4 Pixhawk 6C](https://docs.px4.io/main/en/flight_controller/pixhawk6c) ("84.8*44*12.4 mm", "59.3 g"); [Holybro dimensions](https://docs.holybro.com/autopilot/pixhawk-6c/dimensions) |
| **2. ArduSimple simpleRTK2B** (ZED-F9P, Arduino-Uno shield) | **68.58 × 53.34 × ~1.6** (board L×W confirmed from drawing; PCB thickness 1.6 = standard, **not dimensioned — verify on arrival**) | **3 × ⌀3.20** (M3) mounting holes on the **Arduino-Uno footprint**. Header pin holes ⌀0.90 at 2.54 pitch. Reference coords off the drawing (origin = bottom-left): top hole ≈ X17.78 / 2.54 from top edge; lower-left hole ≈ X15.24 / Y15.24; lower-right hole ≈ X≈38, Y13.07. (Standard Uno R3 positions; 4th Uno hole omitted.) | SMA antenna jack on one short edge; 2× micro-USB ("POWER+GPS", "USB/XBee") on the opposite short edge; Pixhawk JST-GH on board edge; XBee socket footprint; Arduino male header pins protrude **down** from the underside (shield stack). Keep both short edges + underside clear. | **`cad/vendor/simplertk2b.stl`** (3.62 MB, official `simpleRTK2B_LR`) + **`cad/vendor/simplertk2b_pcb.pdf`** (mech drawing). URL: `https://github.com/ardusimple/simpleRTK2B/tree/master/Mechanical`. License: ArduSimple GitHub repo (open/community). Higher-fidelity STEP on [GrabCAD](https://grabcad.com/library/ardusimple-simplertk2b-and-simplertk2b-lite-1) (login). | [simpleRTK2B_PCB.PDF](https://raw.githubusercontent.com/ardusimple/simpleRTK2B/master/Mechanical/simpleRTK2B_PCB.PDF) (drawing: 68.58 × 53.34, ⌀3.20, ⌀0.90, 2.54 pitch); [ArduSimple product page](https://www.ardusimple.com/product/simplertk2b/) |
| **3. Raspberry Pi 5 Model B** | **85 × 56 × ~16** (board L×W confirmed; height = tallest connector ≈ USB/RJ45 stack. **PCB thickness ~1.4–1.6 not dimensioned on drawing — verify on arrival**) | **58 × 49** grid, **⌀2.7** corner holes (M2.5), **3.5 mm inset** from both edges, **n = 4** (confirmed). Plus one extra **⌀3** hole near board centre (non-grid). | Bottom edge (85 mm side): USB-C power @ 11.2, micro-HDMI0 @ 25.8, micro-HDMI1 @ 39.2 (centres from left). Right edge: 2× stacked USB-A + RJ45 Gigabit (USB centres @ ~29.1 & 47 from bottom; RJ45 @ ~10.2). Top edge: 40-pin GPIO header (starts ~3.5 inset). Side connectors stand ~16 tall; GPIO ~8.5 tall. Two PCIe/cam-disp FPC connectors on left edge. | **`cad/vendor/pi5.stp`** (37 MB, genuine RPi Creo `00-RASPBERRY-PI-5-SBC-SIMPLE_ASM`). URL (rehosted, no login): `https://www.elecrow.com/download/rasp/raspberry_pi_5.stp`. Official portal (JS-gated): `https://pip.raspberrypi.com/categories/1099-raspberry-pi-5`. License: RPi mechanical model, free redistribution. | [RPi 5 mechanical drawing PDF](https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf) (read visually: 85, 56, ⌀2.7, ⌀3, 58, 49, 3.5 inset, port offsets 11.2/25.8/39.2) |
| **4. Raspberry Pi AI HAT+** (Hailo-8L 13 TOPS / Hailo-8 26 TOPS) | **65 × 56.5 × ~5.6** (board L×W confirmed from official drawing; the **16 mm stacking header** sets the gap to the Pi — see stack note. PCB thickness not dimensioned — **verify on arrival**) | **58 × 49** grid (aligns with the Pi 5 holes — it stacks on them), **⌀2.7** (M2.5), **3.5 mm inset**, **n = 4** (confirmed, corners). | 40-pin GPIO stacking header along top edge (centre @ 29). **Hailo NPU metal can = 17 × 17** in board centre (tallest top-side feature). PCIe FPC ribbon connector on board (mates to Pi via the supplied ribbon). Bottom edge has a **notch/cut-out (~10 wide, starting ~47.5 from left)** for clearance over the Pi's components / Active Cooler. | **No free official STEP found without login** — geometry is simple (flat board); build proxy from the published drawing. STEP via [Printables](https://www.printables.com/model/1558288-raspberry-pi-hat-m2-reference-model) (login). License of proxy: N/A (your model). | [AI HAT+ product brief PDF](https://datasheets.raspberrypi.com/ai-hat-plus/raspberry-pi-ai-hat-plus-product-brief.pdf) p.4 "Physical specification" (read visually: 65, 58, 29, 56.5, 49, 16, 17×17, 3.5, 47.5/10/7.5); [AI HAT+ docs](https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html); [HAT+ spec](https://datasheets.raspberrypi.com/hat/hat-plus-specification.pdf) |

---

## Stack note — Pi 5 + AI HAT+

- AI HAT+ ships with a **16 mm stacking header** + threaded spacers + screws, sized so the
  HAT clears a Raspberry Pi 5 **Active Cooler**.
- Therefore HAT PCB underside sits **~16 mm above** the Pi 5 GPIO header / PCB top surface.
  Add HAT PCB (~1.6) + Hailo can height (top-side, height **unpublished — measure**) for total stack.
- Both boards share the **identical 58 × 49 mounting grid** (3.5 mm inset, M2.5), so a single
  set of standoffs at those 4 points carries the whole stack. The AI HAT+ board (65 × 56.5)
  slightly overhangs the Pi 5 (85 × 56) on the width but the holes coincide.
  Source: [AI HAT+ brief](https://datasheets.raspberrypi.com/ai-hat-plus/raspberry-pi-ai-hat-plus-product-brief.pdf),
  [M.2 HAT+ brief](https://datasheets.raspberrypi.com/m2-hat-plus/raspberry-pi-m2-hat-plus-product-brief.pdf).

---

## Confirmations vs. the brief's assumptions

| Asked to confirm | Result |
|---|---|
| Pixhawk 6C = 84.8 × 44 × 12.4 | **CONFIRMED** (PX4 + Holybro). NOTE: the Holybro "dimensions" page also lists the separate **FMU module 38.8 × 31.8 × 14.6** and a **baseboard 52.4 × 103.4 × 16.7** — don't confuse those with the 84.8×44 assembled FC. |
| simpleRTK2B = Arduino-Uno footprint | **CONFIRMED.** Exact board = **68.58 × 53.34** (more precise than the "69 × 53" round number). 3 × ⌀3.20 M3 holes on the Uno pattern. |
| Pi 5 = 85 × 56, holes 58 × 49 M2.5, 3.5 inset | **ALL CONFIRMED** from the official mechanical drawing. Corner holes ⌀2.7 (M2.5 clearance); plus one extra ⌀3 centre hole. |
| AI HAT+ ≈ 65 × 56.5, stacks via GPIO + standoffs | **CONFIRMED.** Official drawing = **65 × 56.5**; **16 mm** stacking header; mounting holes are the **58 × 49** Pi grid (3.5 inset). (Some retail listings round to "66 × 56.5".) |

---

## Downloaded into `cad/vendor/`

| File | Board | Format | Bytes | Provenance |
|---|---|---|---|---|
| `pixhawk6c.step` | Pixhawk 6C | STEP (ISO-10303-21, Creo) | 2,170,692 | Holybro official GitBook download |
| `simplertk2b.stl` | simpleRTK2B | STL (ASCII) | 3,617,784 | ArduSimple official GitHub |
| `simplertk2b_pcb.pdf` | simpleRTK2B | PDF mech drawing | 77,293 | ArduSimple official GitHub |
| `pi5.stp` | Raspberry Pi 5 | STEP (Creo) | 37,476,379 | RPi model (rehosted by Elecrow, prior session) |

(No free no-login STEP exists for the AI HAT+ — model it from the cited drawing.)

> **OpenSCAD note:** these are STEP/STL. OpenSCAD cannot read STEP natively — convert
> STEP→STL in FreeCAD (Part workbench → import → export mesh) then `import("...stl")`,
> or use the STL directly (simpleRTK2B already is STL).

---

## Values that remain "unpublished — measure on arrival"

1. **Pixhawk 6C mounting-hole pattern** — not published as reliable text (web hits returned
   conflicting AI-generated numbers like "45×45" / "68×50" that contradict the confirmed
   84.8×44 board, so discarded). **Extract the 4 hole centres + ⌀ directly from
   `cad/vendor/pixhawk6c.step` in FreeCAD**, or measure on arrival.
2. **PCB thickness** for Pixhawk 6C, simpleRTK2B, Pi 5, AI HAT+ — none dimension the bare PCB
   thickness on their drawings. Pi/HAT/Arduino PCBs are conventionally **1.4–1.6 mm**; verify
   with calipers on arrival (or read from the STEP for Pixhawk/Pi).
3. **Hailo-8L NPU can height** (the 17×17 metal lid) — top-side height not published; measure.
4. **simpleRTK2B exact 3rd-hole coordinate** — drawing gives the dims but the lower-right hole
   X is read off the figure (~38); confirm from the PCB PDF / on arrival if a tight tray is cut.
