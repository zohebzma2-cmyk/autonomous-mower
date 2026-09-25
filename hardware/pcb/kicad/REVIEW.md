# MowerCarrier Rev A.1 — pre-fab review

Status: **DRC/ERC-clean and generated end to end, not yet reviewed by a person.** This board
switches 30 A and is the hardware half of the kill chain. Treat everything below as the
checklist a second pair of eyes signs off before the Gerber zip goes to JLCPCB.

## Must do before ordering

1. **Q1 needs a heatsink (or a better FET).** IRF4905 R<sub>DS(on)</sub> is 20 mΩ max, so
   2.0 W at 10 A, 4.5 W at 15 A (a realistic mowing load), 8 W at 20 A and 18 W at 30 A. A
   bare TO-220 is ~62 °C/W: 4.5 W would be ~280 °C above ambient. Fit a clip-on TO-220
   heatsink of ≤ 10 °C/W; Q1 stands vertical with open space toward the top edge. Better:
   a sub-5 mΩ P-FET, or an ideal-diode controller driving an N-FET.
2. **Caliper your ESP32-DevKitC.** The two 1×19 sockets are 25.4 mm apart (genuine
   Espressif V4). Most clones are 22.86 mm. Set `ESP_ROW_PITCH` in `design.py` and regenerate.
3. **Confirm the fuse-holder rating.** F0 carries the whole board. The footprint is the
   Littelfuse FLR 178.6165 ATO holder; confirm its rating is ≥ 30 A (or use a
   direct-solder ATO fuse) and order the matching part. LCSC number not yet verified.
4. **Look at the autorouted layout** in KiCad (`mowercarrier.kicad_pcb`). Freerouting
   produced it; the trunk pours are placed deliberately, the rest is the router's.

## Current capacity (IPC-2221, 2 oz outer copper)

| Path | Copper | Capacity | Fuse |
|---|---|---|---|
| XT60 → Q1 → F0 → bus (+12V_IN, +12V_RP, +12V_BUS) | solid pours: top for IN/RP, **bottom** for the bus under the whole fuse column; ~15–20 mm wide, necking only at the XT60/TO-220/fuse-clip pads | 30 A needs 16.1 mm @ 10 °C rise, 10.6 mm @ 20 °C | 30 A |
| F4 → K1 → MOTOR V+, F5 → K2 → PTO (+12V_DRIVE, MOTOR_V+, +12V_PTO, PTO_OUT) | 2.5 mm tracks + solid pours on the fuse clips | 7.8 A @ 10 °C, 10.5 A @ 20 °C | 10 A / 7.5 A |
| F1–F3 branch outputs, +5 V, GND tracks | 1.2 mm tracks + clip pours | 4.6 A @ 10 °C, 6.2 A @ 20 °C | 5 / 3 / 2 A |
| GND return | solid pour on **both** layers, solid (not thermal) pad connections | — | — |

The pours are generous, but the 30 A path still necks through TO-220 legs and fuse-clip
pads: that's the same as any board using those parts. Measure the narrowest pour neck in
KiCad (Inspect → Measure) if you plan to run near 30 A continuously.

## Rev A → A.1: design errors found while turning the netlist into copper

1. **Q1 was backwards.** Source to battery means the body diode *conducts* on reverse
   polarity, so there was no protection at all. Now drain → battery, source → load, R1 10k
   gate pulldown, D5 15 V zener gate-source clamp.
2. **The XT60 was reversed.** The footprint's silkscreen puts "−" on pad 1. The netlist had
   +12 V on pad 1.
3. **The E-stop had no supply.** Its NC contacts feed the relay coils, but nothing fed the
   switch. TB7 is now 5-pole: +12 V feed (F2, 3 A), NC1, NC2, SIG, GND.
4. **K1.COM was on two nets.** It is now +12V_DRIVE (F4, 10 A) only.
5. **The PTO clutch was unfused below the 30 A main fuse.** New F5, 7.5 A.
6. **R_LEN was on GPIO12,** an ESP32 boot strapping pin (pulled high at reset → 1.8 V flash
   → boot loop). Moved to GPIO33. **DRIVE_EN had no pin:** GPIO32. The firmware follows:
   K1 stays off until the ESP32 has configured its outputs.
7. **The relay rating was wrong.** Songle SLA *Form C* NO is rated 20 A @ 28 VDC; only
   *Form A* is rated 30 A. Now SLA-12VDC-SL-**A**, with the footprint drawn from Songle's
   drilling drawing. KiCad's Rayex L90 footprint is a different T90 pinout, so don't substitute it.

## Safety architecture notes (unchanged, restated for the reviewer)

- **E-stop.** It opens both relay coils in hardware (drive + PTO) *and* grounds the magneto
  (engine off). Motor power to the actuators drops with K1, so the lap bars are *not*
  driven to neutral on E-stop; the engine kill is what stops the machine. On a *software*
  failsafe (lost PWM), K1 stays energised so the ESP32 can centre the bars.
- **Relay coils.** Each needs E-stop closed **and** its FET on. The 10k gate pulldowns keep
  both relays off while the ESP32 or Pixhawk is booting, reset or absent.

## Cosmetic (DRC warnings, not errors)

13 × silkscreen within the board-edge clearance (edge-mounted XT60 + terminal outlines)
and 3 × overlapping reference labels. Fab houses clip silk at the edge; fix the labels in
KiCad if you care.
