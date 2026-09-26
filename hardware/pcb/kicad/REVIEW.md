# MowerCarrier Rev A.1 — pre-fab review

Status: **DRC/ERC-clean and generated end to end, not yet reviewed by a person.** This board
carries up to 20 A (main fuse; the trunk copper is sized for 30 A) and is the hardware half of the kill chain. Treat everything below as the
checklist a second pair of eyes signs off before the Gerber zip goes to JLCPCB.

## Must do before ordering

1. **Caliper your ESP32-DevKitC.** The two 1×19 sockets are 25.4 mm apart (genuine
   Espressif V4). Most clones are 22.86 mm. Set `ESP_ROW_PITCH` in `design.py` and regenerate.
2. **Order Q1's insulating kit.** Q1 (IRF4905) clips into **HS1, a Fischer SK 104 50,8 STC
   (9 K/W)**. That keeps it at ~46 °C over ambient at 15 A (4.5 W) and ~82 °C at the 20 A fuse
   limit (8 W), inside the 175 °C junction limit. The tab is the drain (+12 V), and HS1 is tied
   to GND, so a **TO-220 insulating pad + bushing is required**. Skipping it shorts the battery
   through the heatsink.
3. **Look over the autorouted signal layout** in KiCad. The power trunk is placed
   deliberately; the logic nets are Freerouting's. It's DRC-clean, but a human eye is worth it
   on a safety board.

### Resolved since the first review
- **Fuse-holder rating.** The Littelfuse 178.6165.0002 ATO holder is **22.5 A continuous /
  30 A max**, so the main fuse is now **F0 = 20 A** (realistic peak ~17.5 A: Pi ~2, logic ~1,
  PM02 0.5, both actuators ~10, PTO clutch ~4). Branch fuses are unchanged.
- **Q1 heat.** The heatsink is in the design (above), not left as a note.

## Current capacity (IPC-2221, 2 oz outer copper)

| Path | Copper | Capacity | Fuse |
|---|---|---|---|
| XT60 → Q1 → F0 → bus (+12V_IN, +12V_RP, +12V_BUS) | solid pours: +12V_IN **bottom**, +12V_RP top (L-shape out of the heatsink mouth), +12V_BUS **bottom** under the whole fuse column; ~10–20 mm wide, necking only at the XT60/TO-220/fuse-clip pads | 20 A needs 9.2 mm @ 10 °C rise, 6.0 mm @ 20 °C | 20 A |
| F4 → K1 → MOTOR V+, F5 → K2 → PTO (+12V_DRIVE, MOTOR_V+, +12V_PTO, PTO_OUT) | 2.5 mm tracks + solid pours on the fuse clips | 7.8 A @ 10 °C, 10.5 A @ 20 °C | 10 A / 7.5 A |
| F1–F3 branch outputs, +5 V, GND tracks | 1.2 mm tracks + clip pours | 4.6 A @ 10 °C, 6.2 A @ 20 °C | 5 / 3 / 2 A |
| GND return | solid pour on **both** layers, solid (not thermal) pad connections | — | — |

The pours are generous, but the main path still necks through TO-220 legs and fuse-clip
pads: that's the same as any board using those parts. Measure the narrowest pour neck in
KiCad (Inspect → Measure) if you plan to run near the 20 A fuse rating continuously.

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

## Checks (every regeneration)

- **ERC: 0. DRC: 0 violations of any severity, 0 unconnected, schematic parity 0.**
  `mowercarrier.kicad_dru` holds two scoped exceptions: Q1 sits inside HS1 (their courtyards
  and silk overlap by design), and the edge-mounted connector outlines reach the board edge.
- **Deterministic.** Name-based schematic UUIDs plus a seeded KiCad UUID generator mean an
  unchanged `design.py` regenerates the board byte for byte. `check.sh --full` fails if the
  committed files are stale. (Random UUIDs reordered the autorouter's input between runs,
  which made the route differ run to run.)
