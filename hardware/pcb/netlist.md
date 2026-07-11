# MowerCarrier Rev A — netlist (authoritative connectivity)

The schematic SVG is for review; **this table is the source of truth** for
routing. Pin names match `firmware/lapbar_controller/lapbar_controller.ino` and
`docs/WIRING.md`. Color key: **+12V**, **+5V**, **+3V3**, GND, signal.

## Power nets

| Net | Members |
|-----|---------|
| **+12V_IN** | XT60.+ → Q1(P-FET) source |
| **+12V_BUS** | Q1 drain → F0(30A) → F1/F2/F3/F4 in, K1.COM, K2.COM, TVS(cathode), C_bulk(+) |
| **+12V_BUCK1** | F1(5A) out → TB_BUCK1.1  *(→ off-board buck → Pi 5)* |
| **+12V_BUCK2** | F2(3A) out → TB_BUCK2.1  *(→ off-board buck → ESP32/servo/sensors)* |
| **+12V_PM02** | F3(2A) out → TB_PM02.1  *(→ Holybro PM02 → Pixhawk POWER1)* |
| **+12V_DRIVE** | F4(10A) out → K1.COM  *(switched motor supply)* |
| **MOTOR_V+** | K1.NO → TB_MOTOR.1  *(→ BTS7960 ×2 B+)* |
| **PTO_OUT** | K2.NO → TB_PTO.1  *(→ PTO clutch)* |
| **+5V_BUS** | TB_5VIN.1 *(from Buck #2)* → ESP32.5V, TB_SERVO.+, TB_ULTRA.VCC |
| **+3V3** | ESP32.3V3 → TB_POT_L.1, TB_POT_R.1, R_pullup(estop) |
| **GND** | bottom pour: XT60.−, all F/K/Q returns, TVS anode, C_bulk(−), ESP32.GND, every TB/J GND |

## Safety kill-chain nets

| Net | Members | Notes |
|-----|---------|-------|
| **ESTOP_NC1** | TB_ESTOP.NC1 → K1.coil+ | hardware kill (drive) |
| **ESTOP_NC2** | TB_ESTOP.NC2 → K2.coil+ | hardware kill (PTO) |
| **K1_COIL_LO** | K1.coil− → Q2(N-FET) drain; D2 flyback across K1 coil | software enable |
| **K2_COIL_LO** | K2.coil− → Q3(N-FET) drain; D3 flyback across K2 coil | |
| **DRIVE_EN** | ESP32/FC → R_g(100Ω) → Q2 gate; R_pd(10k) gate→GND | FC/ESP32 arms drive |
| **PTO_EN** | Pixhawk SERVO6 → R_g(100Ω) → Q3 gate; R_pd(10k) | blade engage |
| **ESTOP_SIG** | TB_ESTOP.SIG(NC→GND) → ESP32.GPIO25; R_pu(10k)→+3V3 | HIGH = tripped |

> Relay energises **only** when E-STOP is closed (coil+ powered) **and** the
> driver FET is on (coil− grounded). Losing either instantly de-energises. This
> is the AND-gate that makes both a physical button press and a software fault
> cut power.

## ESP32-DevKitC pin map (socket H1/H2)

| ESP32 | Net | Off-board destination |
|-------|-----|-----------------------|
| GPIO34 | PWM_L | J_FC ← Pixhawk SERVO1 |
| GPIO35 | PWM_R | J_FC ← Pixhawk SERVO3 |
| GPIO36 | POT_L | TB_POT_L wiper (PA-14P) |
| GPIO39 | POT_R | TB_POT_R wiper |
| GPIO25 | ESTOP_SIG | TB_ESTOP.SIG |
| GPIO16 | L_RPWM | J_M1 → IBT-2 #1 |
| GPIO17 | L_LPWM | J_M1 |
| GPIO18 | L_REN | J_M1 |
| GPIO19 | L_LEN | J_M1 |
| GPIO26 | R_RPWM | J_M2 → IBT-2 #2 |
| GPIO27 | R_LPWM | J_M2 |
| GPIO14 | R_REN | J_M2 |
| GPIO12 | R_LEN | J_M2 |
| GPIO2 | STATUS | onboard LED + LED_ARMED |
| 5V | +5V_BUS | ← Buck #2 |
| 3V3 | +3V3 | → pot +ref |
| GND | GND | pour |

## Connectors (silk reference)

| Ref | Type | Pins | Function |
|-----|------|------|----------|
| J1 (XT60) | XT60 R/A | 2 | 12 V battery in (30 A) |
| TB_MOTOR/PTO | screw 5.08 2P | 2 | switched motor V+ / PTO out |
| TB_BUCK1/2, TB_PM02, TB_5VIN | screw 5.08 2P | 2 | power branches |
| TB_POT_L/R | screw 5.08 3P | 3 | actuator pot (3V3 / wiper / GND) |
| TB_ESTOP | screw 5.08 3P | 3 | NC1 / NC2 / SIG (+GND common) |
| J_FC | header 1×6 | 6 | Pixhawk SERVO1/3/5/6 + 5V + GND |
| J_M1 / J_M2 | header 1×6 | 6 | IBT-2 logic (RPWM/LPWM/REN/LEN/3V3/GND) |
| J_5V | header 1×4 | 4 | servo + ultrasonic + spare 5 V |
