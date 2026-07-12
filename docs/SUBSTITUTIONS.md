# Substitution guide — approved alternates per part

For builders outside the US or when a listing dies (ASIN rot is real — see the
design log). Rule of thumb: substitute on SPEC, then update `cad/params.scad`
SECTION 2 if a dimension changed.

| Part | Safe substitutes | What must match | What breaks if you cheap out |
|---|---|---|---|
| **Pixhawk 6C** | Pixhawk 6X, Cube Orange, any ArduPilot-supported FC with ≥2 UARTs + CAN | ArduPilot Rover support, UART count | eBay clones: bad IMU calibration = wandering lines |
| **simpleRTK2B** | any u-blox **ZED-F9P** carrier (SparkFun GPS-RTK2, Drotek) | the F9P chip itself | non-F9P "RTK" modules that only do float — you need FIXED |
| **ANN-MB-00 antenna** | any multiband (L1/L2) survey-style antenna with ground plane | multiband + IP67 | single-band patch antennas: slow/fragile fix |
| **PA-14P actuator** | any 12 V linear actuator ≥150 N, ~100 mm stroke, **with potentiometer feedback** | feedback pot + force + stroke | no-feedback actuators: the ESP32 loop is blind |
| **BTS7960 (IBT-2)** | Cytron MD13S, VNH5019 | ≥30 A peak, PWM+DIR | brushed ESCs without braking: lap bars coast past neutral |
| **Raspberry Pi 5** | Pi 4 (reduced vision FPS), any SBC with 2×CSI + USB3 | CSI ports for the two cameras | Pi Zero class: the UI + vision won't keep up |
| **AI HAT+ (Hailo-8L)** | Coral USB (different model format), or **skip it** — LiDAR-only obstacle stop works | — | nothing breaks; you lose camera AI, keep LiDAR stop |
| **RPLidar A1M8** | RPLidar C1, LD19/LD06 (adjust `lidar_mount` params — different base!) | 360° 2D, ≥8 m range | ultrasonic-only: no reliable obstacle stop |
| **IP67 enclosure** | any ≥ 200×150×100 inner, glanded | inner dims (equipment plate is 140×140) | "resistant" boxes: electronics die the first wet week |
| **E-stop** | any 22 mm **NC** mushroom, IP65+ | NC contact (fail-open kills) | NO-contact stops: a broken wire = no stop. NC or nothing |
| **FS-i6X RC** | any SBUS/PPM RX with failsafe (ELRS, Crossfire) | failsafe-capable receiver | RXs without failsafe defeat the RC-loss kill |
| **Marine duplex wire** | equivalent tinned copper, same AWG | tinned + AWG | automotive primary wire corrodes at the crimps outdoors |
| **Kohler-specific bits** | your engine's manual wins | oil spec/interval, choke type (Smart-Choke vs manual) | — |
| **DeWalt 60V trimmer** | any cordless trimmer with a removable head + fixed-line spool | fixed-line (no bump-feed — the machine can't bump) | bump-feed heads: the line never advances |
| **FIMCO pump** | any 12 V diaphragm pump 1–3 GPM | PWM-tolerant motor | pumps with built-in pressure switches fight the duty control |

**Never substitute:** the NC e-stop topology, RTK-fixed GPS, or feedback actuators.
Those three are the difference between a robot and a runaway.
