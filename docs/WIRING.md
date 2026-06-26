# Wiring, Pinout & Kill-Chain — Autonomous ZT X 52

Build reference. Every connection, gauge, fuse, and solder/connector call for the prototype.
Read **§3 Safety kill chain first** — it must be wired and tested before anything moves.
Visual diagram: [`wiring-diagram.svg`](wiring-diagram.svg). Pin maps match `firmware/lapbar_controller/`.

> Color convention below: **RED = +12 V**, **BLK = GND**, **5V = orange**, **3V3 = yellow**, signal = blue.

---

## 1. System overview

```
 12V BATTERY ─[MAIN 30A]─► FUSE BLOCK (+bus) ─┬─[5A]─► Buck 12→5V #1 ─► Pi 5 (5V/5A)
   (Group U1, on mower)        (GND bus)       ├─[3A]─► Buck 12→5V #2 ─► ESP32 / servo / sensors
        │                                       ├─[2A]─► PM02 ─► Pixhawk 6C (POWER1, 5V + V/I sense)
        │                                       ├─[10A via DRIVE RELAY]─► BTS7960 ×2 motor V+ ─► actuators
        └─[existing]── PTO clutch ◄─[PTO RELAY]─┘   (DRIVE RELAY + PTO RELAY both dropped by E-STOP)

 Pixhawk 6C ──PWM──► ESP32 lap-bar controller ──► BTS7960 ×2 ──► L/R actuators ──(pot feedback)──► ESP32
            ──PWM──► throttle servo      ──relay──► PTO clutch
            ──UART/USB──► Pi 5 (MAVLink)         ◄──GPS1── simpleRTK2B ◄─coax─ RTK antenna
            ──RCIN──► FlySky iA6B
 Pi 5 ──USB──► RPLidar A1   ──CSI0/CSI1──► front/rear cameras   ──GPIO──► overhead ultrasonic
```

---

## 2. Power distribution

All power comes from the mower's existing **12 V Group-U1 battery** (alternator charges it while the
engine runs). Main fuse at the battery; everything branches off the **fuse block** (+bus) with its
own fuse; all grounds to the fuse block **ground bus** → battery (−).

| Branch | Fuse | Wire | Feeds |
|--------|-----:|------|-------|
| Battery → fuse block main | 30 A | **10 AWG** red/blk | the whole system |
| Buck #1 (12→5 V 5 A) | 5 A | 14 AWG | Raspberry Pi 5 (5 V via USB-C or GPIO 5V/GND) |
| Buck #2 (12→5 V) | 3 A | 16 AWG | ESP32, throttle servo (5–6 V), JSN-SR04T |
| PM02 → Pixhawk POWER1 | 2 A | (PM02 leads) | Pixhawk 6C (clean 5 V + battery V/I sensing) |
| **Drive relay** → BTS7960 ×2 motor V+ | 10 A | **14 AWG** | both lap-bar actuators (high-current) |
| PTO relay → PTO clutch | (OEM) | OEM gauge | engages the deck blades (existing clutch) |

**PM02 is required** — the Pixhawk 6C is powered through its POWER1 port by a Holybro **PM02 power
module** (also gives battery voltage/current to ArduPilot). Buy the Pixhawk 6C **+PM02** variant, or
add a PM02 (~$25). Do **not** back-feed 5 V into POWER1 from a generic buck without the sense leads.

---

## 3. ⚠️ Safety kill chain (wire & test this FIRST)

The **22 mm latching e-stop has two contact blocks** (1 NC minimum; add a 2nd block for the signal).
Pressing it must do **all** of the following at once:

1. **Cut drive power** — the e-stop **NC** contact carries the coil of the **DRIVE RELAY** (a 40 A
   automotive relay). E-stop closed → relay energised → BTS7960 motor V+ live. E-stop pressed (NC
   opens) → relay drops → **actuators lose power instantly**.
2. **Disengage blades** — the same NC also opens the **PTO RELAY** path → PTO clutch de-energises →
   blades stop.
3. **Signal the controllers** — a 2nd e-stop contact (NC to GND) → **ESP32 `PIN_ESTOP` (GPIO25)** so
   the controller commands **fail-to-neutral**, and (optionally) → a Pi GPIO + the engine kill wire.

```
        +12V ──[fuse]──► E-STOP NC ──► DRIVE RELAY coil ──► GND
                                │
                                └─(also in series with)─► PTO RELAY enable
        E-STOP 2nd NC ──► ESP32 GPIO25  (and engine kill / Pi GPIO)
```

Layer this **on top of**, not instead of: the **RC kill switch** (FlySky channel → ArduPilot RC
failsafe → HOLD + disarm) and **ArduPilot failsafes** (GPS loss, geofence, low battery). See
`docs/BUILD.md §0`. **Blades stay disconnected entirely** until drive + nav + every failsafe is proven.

---

## 4. Pinout tables

### Pixhawk 6C (Holybro) — all connectors on the two 44 mm short ends
| Port | To | Notes |
|------|----|-------|
| POWER1 (6-pin) | **PM02** → battery | 5 V in + V/I sense |
| GPS1 (10-pin/UART) | **simpleRTK2B** (TX↔RX, RX↔TX, 5V, GND) | RTK position |
| TELEM2 (or USB-C) | **Pi 5** (MAVLink) | UART: T2-TX↔Pi-RX, T2-RX↔Pi-TX, GND; or just Pixhawk USB → Pi USB (simplest) |
| RC IN | **FlySky iA6B** (SBUS/PPM) | manual override + kill |
| FMU PWM **SERVO1** | ESP32 `PIN_PWM_L` (GPIO34) | throttle-LEFT (skid-steer) |
| FMU PWM **SERVO3** | ESP32 `PIN_PWM_R` (GPIO35) | throttle-RIGHT |
| FMU PWM **SERVO5** | throttle servo signal | engine RPM |
| FMU PWM **SERVO6** | PTO relay coil (set fn = Relay) | blade engage |
| (internal) | IMU / compass | used for **incline safety** |

### ESP32 lap-bar controller (matches `lapbar_controller.ino`)
| ESP32 pin | Net | To |
|-----------|-----|----|
| GPIO34 | PWM in L | Pixhawk SERVO1 |
| GPIO35 | PWM in R | Pixhawk SERVO3 |
| GPIO36 (VP) | pot L wiper | LEFT actuator feedback (yellow) |
| GPIO39 (VN) | pot R wiper | RIGHT actuator feedback |
| GPIO25 | e-stop sense | E-STOP 2nd NC → GND (pullup) |
| GPIO16/17 | L_RPWM/L_LPWM | BTS7960 #1 RPWM/LPWM |
| GPIO18/19 | L_REN/L_LEN | BTS7960 #1 R_EN/L_EN |
| GPIO26/27 | R_RPWM/R_LPWM | BTS7960 #2 RPWM/LPWM |
| GPIO14/12 | R_REN/R_LEN | BTS7960 #2 R_EN/L_EN |
| 5V / GND | power | Buck #2 |
| GPIO2 | status LED | onboard |

Actuator feedback pot (each): **+end → 3V3**, **wiper → ESP32 ADC**, **−end → GND** (0–10 kΩ, from the
PA-14P 6-pin Molex: Yellow=+V, Blue=wiper, White=GND; Black/Red = motor → BTS7960 M+/M−).

### BTS7960 (IBT-2) ×2 — one per actuator
| Pin | To |
|-----|----|
| B+ / B− | **DRIVE-RELAY-switched 12 V** / GND (14 AWG) |
| M+ / M− | actuator motor leads (Black/Red) |
| RPWM / LPWM | ESP32 (see above) |
| R_EN / L_EN | ESP32 (tie-able together) |
| VCC / GND | ESP32 3V3 / GND (logic) |

### Other modules
| Module | Connection |
|--------|-----------|
| **RPLidar A1** | its USB adapter → **Pi 5 USB** |
| **Front / rear cameras** | Pi 5 **CSI0 / CSI1** ribbon |
| **Overhead ultrasonic (JSN-SR04T)** | VCC→5V, GND, **TRIG→Pi GPIO23**, **ECHO→Pi GPIO24 via 1k/2k divider** (5V→3V3) |
| **Throttle servo** | signal→Pixhawk SERVO5, V+→Buck #2 (5–6 V), GND |
| **PTO relay** | coil: Pixhawk SERVO6 (+ e-stop interlock) ; contacts: 12 V ↔ PTO clutch |
| **simpleRTK2B** | UART→Pixhawk GPS1 ; SMA→RTK antenna (coax) ; 5 V/GND |
| **FlySky iA6B** | SBUS→Pixhawk RCIN ; 5 V/GND |

---

## 5. Solder vs. connector

- **Solder + heat-shrink** (vibration-critical, permanent): actuator motor leads ↔ BTS7960 M±; pot
  leads ↔ ESP32; battery main lug; ground-bus rings; ultrasonic divider.
- **Connectorized** (serviceable): XT60 on each power branch; Pixhawk JST-GH ports (use the supplied
  cables — do NOT cut these); ESP32 on a screw-terminal shield or Dupont (then conformal-coat); USB
  for RPLidar + Pi↔Pixhawk; CSI ribbons.
- **Crimp ring/spade + heat-shrink** at the fuse block and relays.
- Conformal-coat all PCBs after testing; dielectric grease every connector/gland.

---

## 6. Order additions (this wiring requires)
Add to the order (`cart/ORDER.md`): **Holybro PM02 power module** (or buy the Pixhawk 6C +PM02
variant), **ESP32 DevKit** (~$8), **JSN-SR04T** waterproof ultrasonic (~$10), one extra **40 A relay**
for the DRIVE-RELAY (the Recoil 2-pack already covers PTO + drive if you don't also kill ignition;
add a 3rd if you do). Total ≈ +$45.
