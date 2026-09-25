# SPDX-License-Identifier: MIT
"""MowerCarrier Rev A.1 — the single source of truth for the KiCad project.

Every part: reference, KiCad library symbol, value, footprint, LCSC/MPN, and a
pin -> net map using the SYMBOL's pin numbers (which equal the footprint pad
numbers for every part chosen here — gen_kicad.py asserts it). gen_kicad.py turns
this into mowercarrier.kicad_sch (ERC) and mowercarrier.kicad_pcb (DRC).

Rev A -> A.1 corrections to ../netlist.md (each found while turning it into copper):
  1. Q1 was drawn source-to-battery: its body diode would CONDUCT on reverse polarity
     (no protection at all). Now drain = battery, source = load, gate pulled to GND
     through R1 with a 15 V zener (D5) clamping gate-source for load-dump.
  2. E-stop had no supply: its NC contacts feed the relay coils but nothing fed the
     switch. TB_ESTOP is now 5-pole: +12 V feed (from the 3 A F2 branch), NC1, NC2,
     SIG, GND.
  3. K1.COM was on two nets (+12V_BUS and +12V_DRIVE). It is +12V_DRIVE (F4, 10 A) only.
  4. The PTO clutch hung off the 30 A main fuse with no branch fuse: new F5 7.5 A.
  5. R_LEN was on GPIO12, an ESP32 boot strapping pin (MTDI: pulled high at reset ->
     1.8 V flash -> boot loop). Moved to GPIO33. DRIVE_EN (Q2 gate) had no ESP32 pin
     assigned: GPIO32. firmware/lapbar_controller + docs/WIRING.md follow.
  6. Relay: the Songle SLA *Form C* NO contact is rated 20 A @ 28 VDC (datasheet);
     only Form A (SPST-NO) carries 30 A. Both relays only switch NO -> SLA-12VDC-SL-A.
  7. Footprint facts the netlist didn't carry: SLA pinout from Songle's own drawing
     (not pin-compatible with the Rayex L90 footprint in KiCad's library); ATO holder =
     Littelfuse FLR 178.6165 (KiCad's "Keystone 3555-2" is a MAXI holder).
"""

ESP_ROW_PITCH = 25.4   # [MEASURE] genuine Espressif DevKitC V4 = 25.4 mm; most clones = 22.86 mm

# ESP32-DevKitC V4 headers (Espressif user guide): J2 = H1, J3 = H2, pin 1 at the antenna end
H1_PINS = ["3V3", "EN", "VP", "VN", "IO34", "IO35", "IO32", "IO33", "IO25", "IO26",
           "IO27", "IO14", "IO12", "GND", "IO13", "D2", "D3", "CMD", "5V"]
H2_PINS = ["GND", "IO23", "IO22", "TX", "RX", "IO21", "GND", "IO19", "IO18", "IO5",
           "IO17", "IO16", "IO4", "IO0", "IO2", "IO15", "D1", "D0", "CLK"]
ESP_NET = {  # DevKit pin name -> board net (anything absent is a no-connect)
    "3V3": "+3V3", "5V": "+5V_BUS", "GND": "GND",
    "IO34": "PWM_L", "IO35": "PWM_R", "VP": "POT_L", "VN": "POT_R", "IO25": "ESTOP_SIG",
    "IO16": "L_RPWM", "IO17": "L_LPWM", "IO18": "L_REN", "IO19": "L_LEN",
    "IO26": "R_RPWM", "IO27": "R_LPWM", "IO14": "R_REN", "IO33": "R_LEN",
    "IO32": "DRIVE_EN", "IO2": "STATUS",
}


def esp(pins):
    return {str(i + 1): ESP_NET.get(p) for i, p in enumerate(pins)}


FP_R = "Resistor_SMD:R_0805_2012Metric"
FP_C = "Capacitor_SMD:C_0805_2012Metric"
FP_FUSE = "Fuse:FuseHolder_Blade_ATO_Littelfuse_FLR_178.6165"
FP_TB2 = "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-2-5.08_1x02_P5.08mm_Horizontal"
FP_TB3S = "TerminalBlock_Phoenix:TerminalBlock_Phoenix_PT-1,5-3-3.5-H_1x03_P3.50mm_Horizontal"
FP_TB5 = "TerminalBlock_Phoenix:TerminalBlock_Phoenix_MKDS-1,5-5-5.08_1x05_P5.08mm_Horizontal"
FP_RELAY = "MowerCarrier:Relay_SPST_Songle_SLA-xxVDC-SL-A"
HOLDER = "Littelfuse 178.6165 ATO holder (verify LCSC)"

# Silk/ref names from netlist.md live in the value: TB7 = TB_ESTOP, TB8/9 = TB_POT_L/R,
# J2 = J_FC, J3 = J_5V, J4/J5 = J_M1/J_M2 (KiCad annotation needs prefix+number).
# ref, lib_id, value, footprint, part (LCSC / MPN), {pin: net or None (= no-connect)}
PARTS = [
    # --- 12 V input, reverse polarity, main fuse, bulk + TVS ---
    ("J1", "Connector_Generic:Conn_01x02", "XT60PW-M 12V IN",
     "Connector_AMASS:AMASS_XT60PW-M_1x02_P7.20mm_Horizontal", "C98732 XT60PW-M",
     {"1": "GND", "2": "+12V_IN"}),          # footprint silk: pad 1 = "-", pad 2 = "+"
    ("Q1", "Transistor_FET:IRF4905", "IRF4905", "Package_TO_SOT_THT:TO-220-3_Vertical",
     "C2564 IRF4905", {"1": "Q1_G", "2": "+12V_IN", "3": "+12V_RP"}),
    ("R1", "Device:R", "10k", FP_R, "C17414", {"1": "Q1_G", "2": "GND"}),
    ("D5", "Device:D_Zener", "BZT52C15 (15V)", "Diode_SMD:D_SOD-123", "BZT52C15 (verify LCSC)",
     {"1": "+12V_RP", "2": "Q1_G"}),
    ("F0", "Device:Fuse", "30A ATO", FP_FUSE, HOLDER, {"1": "+12V_RP", "2": "+12V_BUS"}),
    ("D1", "Device:D_Zener", "SMBJ16A TVS", "Diode_SMD:D_SMB", "C151254 SMBJ16A",
     {"1": "+12V_BUS", "2": "GND"}),
    ("C1", "Device:C_Polarized", "470u 25V", "Capacitor_THT:CP_Radial_D10.0mm_P5.00mm",
     "C43839", {"1": "+12V_BUS", "2": "GND"}),
    # --- branch fuses -> outputs ---
    ("F1", "Device:Fuse", "5A ATO (Pi buck)", FP_FUSE, HOLDER, {"1": "+12V_BUS", "2": "+12V_BUCK1"}),
    ("F2", "Device:Fuse", "3A ATO (logic buck, e-stop)", FP_FUSE, HOLDER, {"1": "+12V_BUS", "2": "+12V_BUCK2"}),
    ("F3", "Device:Fuse", "2A ATO (PM02)", FP_FUSE, HOLDER, {"1": "+12V_BUS", "2": "+12V_PM02"}),
    ("F4", "Device:Fuse", "10A ATO (drive)", FP_FUSE, HOLDER, {"1": "+12V_BUS", "2": "+12V_DRIVE"}),
    ("F5", "Device:Fuse", "7.5A ATO (PTO)", FP_FUSE, HOLDER, {"1": "+12V_BUS", "2": "+12V_PTO"}),
    ("TB1", "Connector_Generic:Conn_01x02", "BUCK1 (Pi 5)", FP_TB2, "C474952", {"1": "+12V_BUCK1", "2": "GND"}),
    ("TB2", "Connector_Generic:Conn_01x02", "BUCK2 (logic)", FP_TB2, "C474952", {"1": "+12V_BUCK2", "2": "GND"}),
    ("TB3", "Connector_Generic:Conn_01x02", "PM02 (Pixhawk)", FP_TB2, "C474952", {"1": "+12V_PM02", "2": "GND"}),
    # --- kill chain: E-stop NC contacts AND coil-driver FETs ---
    ("TB7", "Connector_Generic:Conn_01x05", "TB_ESTOP: 12V,NC1,NC2,SIG,GND", FP_TB5,
     "KF128-5.08-5P (verify LCSC)",
     {"1": "+12V_BUCK2", "2": "ESTOP_NC1", "3": "ESTOP_NC2", "4": "ESTOP_SIG", "5": "GND"}),
    ("K1", "Relay:Relay_SPST-NO", "SLA-12VDC-SL-A DRIVE", FP_RELAY, "SLA-12VDC-SL-A (verify LCSC)",
     {"A1": "ESTOP_NC1", "A2": "K1_COIL_LO", "13": "+12V_DRIVE", "14": "MOTOR_V+"}),
    ("K2", "Relay:Relay_SPST-NO", "SLA-12VDC-SL-A PTO", FP_RELAY, "SLA-12VDC-SL-A (verify LCSC)",
     {"A1": "ESTOP_NC2", "A2": "K2_COIL_LO", "13": "+12V_PTO", "14": "PTO_OUT"}),
    ("D2", "Device:D_Schottky", "SS34 flyback", "Diode_SMD:D_SMA", "C8678", {"1": "ESTOP_NC1", "2": "K1_COIL_LO"}),
    ("D3", "Device:D_Schottky", "SS34 flyback", "Diode_SMD:D_SMA", "C8678", {"1": "ESTOP_NC2", "2": "K2_COIL_LO"}),
    ("Q2", "Transistor_FET:AO3400A", "AO3400A", "Package_TO_SOT_SMD:SOT-23", "C20917",
     {"1": "Q2_G", "2": "GND", "3": "K1_COIL_LO"}),
    ("Q3", "Transistor_FET:AO3400A", "AO3400A", "Package_TO_SOT_SMD:SOT-23", "C20917",
     {"1": "Q3_G", "2": "GND", "3": "K2_COIL_LO"}),
    ("R2", "Device:R", "100", FP_R, "C17408", {"1": "DRIVE_EN", "2": "Q2_G"}),
    ("R3", "Device:R", "10k", FP_R, "C17414", {"1": "Q2_G", "2": "GND"}),
    ("R4", "Device:R", "100", FP_R, "C17408", {"1": "PTO_EN", "2": "Q3_G"}),
    ("R5", "Device:R", "10k", FP_R, "C17414", {"1": "Q3_G", "2": "GND"}),
    ("R6", "Device:R", "10k", FP_R, "C17414", {"1": "ESTOP_SIG", "2": "+3V3"}),
    ("TB4", "Connector_Generic:Conn_01x02", "MOTOR V+ (IBT-2 B+)", FP_TB2, "C474952", {"1": "MOTOR_V+", "2": "GND"}),
    ("TB5", "Connector_Generic:Conn_01x02", "PTO clutch", FP_TB2, "C474952", {"1": "PTO_OUT", "2": "GND"}),
    ("R8", "Device:R", "2k", FP_R, "C17604", {"1": "MOTOR_V+", "2": "LED2_A"}),
    ("LED2", "Device:LED", "red: DRIVE LIVE", "LED_SMD:LED_0805_2012Metric", "C84256", {"1": "GND", "2": "LED2_A"}),
    # --- ESP32 carrier + I/O ---
    ("H1", "Connector_Generic:Conn_01x19", "ESP32 DevKitC J2",
     "Connector_PinSocket_2.54mm:PinSocket_1x19_P2.54mm_Vertical", "C319202", esp(H1_PINS)),
    ("H2", "Connector_Generic:Conn_01x19", "ESP32 DevKitC J3",
     "Connector_PinSocket_2.54mm:PinSocket_1x19_P2.54mm_Vertical", "C319202", esp(H2_PINS)),
    ("TB6", "Connector_Generic:Conn_01x02", "5V IN (buck #2)", FP_TB2, "C474952", {"1": "+5V_BUS", "2": "GND"}),
    ("C2", "Device:C", "100n", FP_C, "C49678", {"1": "+5V_BUS", "2": "GND"}),
    ("C3", "Device:C", "10u 25V", FP_C, "C15850", {"1": "+5V_BUS", "2": "GND"}),
    ("C4", "Device:C", "100n", FP_C, "C49678", {"1": "+3V3", "2": "GND"}),
    ("J2", "Connector_Generic:Conn_01x06", "J_FC: Pixhawk SERVO1/3/6/5",
     "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical", "C2337",
     {"1": "PWM_L", "2": "PWM_R", "3": "PTO_EN", "4": "THR_SERVO", "5": "GND", "6": "GND"}),
    ("J3", "Connector_Generic:Conn_01x04", "J_5V: servo + ultrasonic",
     "Connector_PinHeader_2.54mm:PinHeader_1x04_P2.54mm_Vertical", "C2337",
     {"1": "+5V_BUS", "2": "GND", "3": "THR_SERVO", "4": "+5V_BUS"}),
    ("J4", "Connector_Generic:Conn_01x06", "J_M1: IBT-2 #1 (left)",
     "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical", "C2337",
     {"1": "L_RPWM", "2": "L_LPWM", "3": "L_REN", "4": "L_LEN", "5": "+3V3", "6": "GND"}),
    ("J5", "Connector_Generic:Conn_01x06", "J_M2: IBT-2 #2 (right)",
     "Connector_PinHeader_2.54mm:PinHeader_1x06_P2.54mm_Vertical", "C2337",
     {"1": "R_RPWM", "2": "R_LPWM", "3": "R_REN", "4": "R_LEN", "5": "+3V3", "6": "GND"}),
    ("TB8", "Connector_Generic:Conn_01x03", "TB_POT_L: 3V3,wiper,GND", FP_TB3S, "PT-1,5-3-3.5-H",
     {"1": "+3V3", "2": "POT_L", "3": "GND"}),
    ("TB9", "Connector_Generic:Conn_01x03", "TB_POT_R: 3V3,wiper,GND", FP_TB3S, "PT-1,5-3-3.5-H",
     {"1": "+3V3", "2": "POT_R", "3": "GND"}),
    ("R7", "Device:R", "220", FP_R, "C17557", {"1": "STATUS", "2": "LED1_A"}),
    ("LED1", "Device:LED", "green: STATUS", "LED_SMD:LED_0805_2012Metric", "C2297", {"1": "GND", "2": "LED1_A"}),
    # --- M3 mounting holes, bonded to GND ---
] + [("MH%d" % i, "Mechanical:MountingHole_Pad", "M3", "MountingHole:MountingHole_3.2mm_M3_Pad", "-",
      {"1": "GND"}) for i in range(1, 5)]

# Net classes: track width (mm) for the autorouter. Current in brackets = design current.
NETCLASSES = {
    "POWER30": (5.0, 0.5, ["+12V_IN", "+12V_RP", "+12V_BUS"]),                       # 30 A trunk
    "POWER10": (2.5, 0.4, ["+12V_DRIVE", "MOTOR_V+", "+12V_PTO", "PTO_OUT"]),         # ≤10 A
    "POWER3":  (1.2, 0.3, ["+12V_BUCK1", "+12V_BUCK2", "+12V_PM02", "+5V_BUS", "GND"]),
}
DEFAULT_TRACK, DEFAULT_CLEAR = 0.3, 0.2
