#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate the MowerCarrier board interconnect schematic (SVG).

A block/net-level schematic of the power-distribution + safety-kill-chain + ESP32
carrier board. Colors follow the project wiring convention:
  RED = +12V   ORANGE = +5V   YELLOW = +3V3   BLUE = signal   GREY = GND
Run:  python3 gen_schematic.py   ->   schematic.svg
"""

W, H = 1480, 1060
COL = dict(bg="#0d1117", panel="#141b24", panel2="#11171f", line="#243040",
           ink="#e6edf3", dim="#9aa7b4", grn="#3fb950",
           v12="#ff5c5c", v5="#ff9f43", v3="#ffd23f", sig="#5ab0ff", gnd="#6b7684")
P = []  # svg fragments


def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def rect(x, y, w, h, fill=COL["panel"], stroke=COL["line"], sw=1.4, rx=10):
    P.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
             f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def txt(x, y, s, size=13, fill=COL["ink"], anchor="start", weight="400",
        mono=False, italic=False):
    fam = "'JetBrains Mono',monospace" if mono else "'Space Grotesk','Segoe UI',sans-serif"
    st = "italic" if italic else "normal"
    P.append(f'<text x="{x}" y="{y}" font-family="{fam}" font-size="{size}" '
             f'font-weight="{weight}" font-style="{st}" fill="{fill}" '
             f'text-anchor="{anchor}">{esc(s)}</text>')


def wire(pts, color=COL["sig"], w=2.2, dash=None):
    d = "M " + " L ".join(f"{x},{y}" for x, y in pts)
    da = f' stroke-dasharray="{dash}"' if dash else ""
    P.append(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="{w}" '
             f'stroke-linejoin="round" stroke-linecap="round"{da}/>')


def dot(x, y, color=COL["ink"], r=3.2):
    P.append(f'<circle cx="{x}" cy="{y}" r="{r}" fill="{color}"/>')


def pin(x, y, label, color=COL["sig"], side="left", size=10.5):
    dot(x, y, color, 2.6)
    if side == "left":
        txt(x + 8, y + 3.5, label, size, COL["dim"], "start", mono=True)
    else:
        txt(x - 8, y + 3.5, label, size, COL["dim"], "end", mono=True)


def chip(x, y, w, h, title, sub="", accent=COL["grn"]):
    rect(x, y, w, h)
    P.append(f'<rect x="{x}" y="{y}" width="{w}" height="30" rx="10" '
             f'fill="{accent}" opacity="0.14"/>')
    P.append(f'<rect x="{x}" y="{y+18}" width="{w}" height="12" fill="{COL["panel"]}"/>')
    txt(x + 14, y + 20, title, 13.5, COL["ink"], weight="600")
    if sub:
        txt(x + w - 12, y + 20, sub, 10, accent, "end", mono=True)


# ---- frame / title ---------------------------------------------------------
P.append(f'<rect width="{W}" height="{H}" fill="{COL["bg"]}"/>')
txt(40, 46, "MowerCarrier — Rev A", 26, COL["ink"], weight="700")
txt(40, 70, "Power distribution · safety kill-chain · ESP32 carrier · interconnect",
    14, COL["dim"])
txt(W - 40, 46, "autonomous-mower", 15, COL["grn"], "end", weight="600", mono=True)
txt(W - 40, 68, "2-layer FR4 · 2oz Cu · 120 × 100 mm · JLCPCB", 11.5, COL["dim"], "end", mono=True)

# legend
lx, ly = 40, 92
for i, (lbl, c) in enumerate([("+12V", COL["v12"]), ("+5V", COL["v5"]),
                              ("+3V3", COL["v3"]), ("SIGNAL", COL["sig"]),
                              ("GND", COL["gnd"])]):
    x = lx + i * 118
    P.append(f'<line x1="{x}" y1="{ly}" x2="{x+26}" y2="{ly}" stroke="{c}" stroke-width="3.5"/>')
    txt(x + 34, ly + 4, lbl, 11, COL["dim"], mono=True)

# ============================================================ SECTION 1: POWER IN
chip(40, 130, 300, 250, "1 · 12 V input & protection", "XT60")
txt(60, 178, "XT60  (12 V battery, 30 A)", 12, COL["v12"], mono=True)
dot(60, 196, COL["v12"]); dot(60, 214, COL["gnd"])
txt(74, 200, "+12", 11, COL["dim"], mono=True); txt(74, 218, "GND", 11, COL["dim"], mono=True)
# reverse-polarity P-FET
rect(150, 186, 70, 40, COL["panel2"]); txt(185, 204, "Q1", 11, COL["ink"], "middle", mono=True)
txt(185, 218, "P-FET", 9.5, COL["dim"], "middle", mono=True)
wire([(60, 196), (150, 196), (150, 200)], COL["v12"])
wire([(220, 200), (250, 200)], COL["v12"])
# TVS + bulk
txt(250, 196, "TVS", 10, COL["v12"], mono=True)
wire([(258, 206), (258, 250), (60, 250), (60, 214)], COL["gnd"], 2)
txt(150, 246, "D_TVS 15V · C_bulk 470µF/25V", 10, COL["dim"], mono=True, italic=True)
# 30A fuse -> bus
rect(150, 296, 90, 34, COL["panel2"]); txt(195, 317, "F0 30A", 11, COL["v12"], "middle", mono=True)
wire([(60, 250), (60, 313), (150, 313)], COL["v12"])
wire([(240, 313), (300, 313)], COL["v12"])
txt(300, 309, "→ +12V BUS", 11, COL["v12"], mono=True, weight="600")
txt(60, 360, "Q1 blocks reverse polarity; TVS clamps load-dump.", 10.5, COL["dim"], italic=True)

# ============================================================ +12V BUS (spine)
bus_x = 360
wire([(bus_x, 300), (bus_x, 940)], COL["v12"], 4)
txt(bus_x - 6, 296, "+12V BUS", 11, COL["v12"], "end", weight="600", mono=True)
gnd_x = 384
wire([(gnd_x, 320), (gnd_x, 960)], COL["gnd"], 4)
txt(gnd_x + 8, 316, "GND", 11, COL["gnd"], mono=True)

# ============================================================ SECTION 2: FUSED BRANCHES
chip(430, 130, 300, 250, "2 · Fused branches", "buck / PM02")
branches = [("F1 5A", "BUCK1 12V → Pi 5", COL["v12"], 178),
            ("F2 3A", "BUCK2 12V → ESP32/servo", COL["v12"], 214),
            ("F3 2A", "PM02 → Pixhawk POWER1", COL["v12"], 250),
            ("F4 10A", "DRIVE relay → motor V+", COL["v12"], 286)]
for fz, dst, c, y in branches:
    wire([(bus_x, y), (450, y)], c, 2.4)
    rect(450, y - 15, 74, 28, COL["panel2"]); txt(487, y + 3, fz, 10.5, c, "middle", mono=True)
    wire([(524, y), (556, y)], c, 2.4)
    dot(556, y, c, 3)
    txt(566, y + 4, dst, 11, COL["dim"], mono=True)
# 5V rail return from buck2
txt(450, 330, "5V IN (from Buck2) → +5V BUS", 11, COL["v5"], mono=True, weight="600")
wire([(556, 344), (700, 344), (700, 360)], COL["v5"], 3)
txt(566, 348, "screw term", 9.5, COL["dim"], mono=True, italic=True)

# ============================================================ SECTION 3: KILL CHAIN
chip(430, 410, 460, 300, "3 · Safety kill chain", "hardware AND software", COL["v12"])
txt(450, 452, "E-STOP  (22 mm latching, 2× NC)", 12, COL["ink"], mono=True, weight="600")
# estop terminal
rect(450, 462, 130, 60, COL["panel2"])
for i, (lb, yy) in enumerate([("NC1", 480), ("NC2", 500), ("SIG", 516)]):
    dot(462, yy, COL["v12"] if i < 2 else COL["sig"], 2.6)
    txt(472, yy + 4, lb, 10, COL["dim"], mono=True)
# DRIVE relay
def relay(x, y, name, enlabel, contact_label, color):
    rect(x, y, 150, 96, COL["panel2"])
    txt(x + 75, y + 20, name, 12, COL["ink"], "middle", weight="600")
    txt(x + 12, y + 42, "coil+", 10, COL["dim"], mono=True)
    txt(x + 12, y + 60, "coil−", 10, COL["dim"], mono=True)
    txt(x + 138, y + 42, "COM", 10, COL["dim"], "end", mono=True)
    txt(x + 138, y + 60, "NO", 10, COL["dim"], "end", mono=True)
    txt(x + 75, y + 86, contact_label, 9, color, "middle", mono=True, italic=True)
    # low-side driver mosfet
    rect(x + 30, y + 112, 90, 34, COL["panel2"])
    txt(x + 75, y + 133, "M-FET", 10, COL["ink"], "middle", mono=True)
    txt(x + 75, y + 168, enlabel, 9.5, COL["sig"], "middle", mono=True)
    txt(x + 135, y + 128, "flyback D", 9, COL["dim"], mono=True, italic=True)

relay(620, 462, "K1 DRIVE 40A", "DRIVE_EN (GPIO/FC)", "COM=+12(F4) · NO→MOTOR V+", COL["v12"])
relay(620, 600, "K2 PTO 40A", "PTO_EN (SERVO6)", "COM=+12 · NO→PTO clutch", COL["v12"])
# estop NC feeds coil+ (hardware kill), mosfet pulls coil- (software enable)
wire([(580, 480), (600, 480), (600, 504), (620, 504)], COL["v12"], 2.2)   # NC1->K1 coil+
wire([(580, 500), (605, 500), (605, 642), (620, 642)], COL["v12"], 2.2)   # NC2->K2 coil+
wire([(620, 520), (695, 520), (695, 574)], COL["gnd"], 2)                  # K1 coil-  -> mosfet
wire([(620, 658), (695, 658), (695, 712)], COL["gnd"], 2)                  # K2 coil-  -> mosfet
wire([(710, 594), (710, 574)], COL["gnd"], 2); wire([(710, 732), (710, 712)], COL["gnd"], 2)
# contacts from bus
wire([(bus_x, 500), (620, 500)], COL["v12"], 0.0001)  # (visual only; real path via F4)
wire([(770, 504), (860, 504)], COL["v12"], 2.6); dot(860, 504, COL["v12"]); txt(866, 508, "MOTOR V+", 10.5, COL["v12"], mono=True)
wire([(770, 642), (860, 642)], COL["v12"], 2.6); dot(860, 642, COL["v12"]); txt(866, 646, "PTO OUT", 10.5, COL["v12"], mono=True)
# estop signal to ESP32
wire([(580, 516), (600, 516), (600, 690), (905, 690)], COL["sig"], 2)
txt(450, 690, "SIG(NC)→GPIO25 (10k↑3V3)", 10, COL["sig"], mono=True)
txt(450, 540, "AND-gate: relay energises only if E-STOP closed (coil+)", 10, COL["dim"], italic=True)
txt(450, 556, "AND driver ON (coil−). Either drop → instant power cut.", 10, COL["dim"], italic=True)

# ============================================================ SECTION 4: ESP32 CARRIER + I/O
ex, ey = 940, 130
chip(ex, ey, 500, 800, "4 · ESP32-DevKitC carrier & I/O", "38-pin socket")
rect(ex + 150, ey + 50, 200, 470, COL["panel2"])
txt(ex + 250, ey + 74, "ESP32-DevKitC", 13, COL["ink"], "middle", weight="600")
txt(ex + 250, ey + 90, "(2× 1×19 female hdr)", 9.5, COL["dim"], "middle", mono=True)
# left pins (inputs / feedback)
left = [("34", "PWM_L ← SERVO1", COL["sig"]), ("35", "PWM_R ← SERVO3", COL["sig"]),
        ("36", "POT_L wiper", COL["v3"]), ("39", "POT_R wiper", COL["v3"]),
        ("25", "E-STOP sense", COL["sig"]), ("3V3", "→ pot +ref", COL["v3"]),
        ("5V", "← Buck2", COL["v5"]), ("GND", "", COL["gnd"])]
for i, (p_, lb, c) in enumerate(left):
    yy = ey + 120 + i * 46
    dot(ex + 150, yy, c, 3); txt(ex + 142, yy + 4, p_, 10, COL["dim"], "end", mono=True)
    if lb:
        txt(ex + 20, yy + 4, lb, 10.5, c, mono=True)
        wire([(ex + 120, yy), (ex + 150, yy)], c, 1.8)
# right pins (H-bridge control)
right = [("16", "L_RPWM"), ("17", "L_LPWM"), ("18", "L_REN"), ("19", "L_LEN"),
         ("26", "R_RPWM"), ("27", "R_LPWM"), ("14", "R_REN"), ("12", "R_LEN"),
         ("2", "STATUS LED")]
for i, (p_, lb) in enumerate(right):
    yy = ey + 120 + i * 42
    c = COL["grn"] if p_ == "2" else COL["sig"]
    dot(ex + 350, yy, c, 3); txt(ex + 358, yy + 4, p_, 10, COL["dim"], mono=True)
    txt(ex + 480, yy + 4, lb, 10.5, c, "end", mono=True)
    wire([(ex + 350, yy), (ex + 470, yy)], c, 1.8)
txt(ex + 250, ey + 545, "→ IBT-2 #1 / #2 (BTS7960) headers", 10, COL["dim"], "middle", mono=True, italic=True)

# I/O connector strip (bottom of section 4)
chip(ex, ey + 590, 500, 320, "  I/O headers & screw terminals", "", COL["sig"])
conns = [
    ("J_FC", "Pixhawk PWM", "SERVO1/3/5/6 + GND → PWM_L/R, throttle, PTO_EN", COL["sig"]),
    ("J_POT_L", "Actuator pot L", "3V3 · wiper→36 · GND  (PA-14P Molex)", COL["v3"]),
    ("J_POT_R", "Actuator pot R", "3V3 · wiper→39 · GND", COL["v3"]),
    ("J_M1", "IBT-2 #1 logic", "RPWM17 LPWM16 REN18 LEN19 +3V3 GND", COL["sig"]),
    ("J_M2", "IBT-2 #2 logic", "RPWM27 LPWM26 REN14 LEN12 +3V3 GND", COL["sig"]),
    ("J_5V", "5V sensors", "servo · JSN-SR04T · spare", COL["v5"]),
    ("LED", "PWR / ARMED", "green=5V rail · amber=GPIO2", COL["grn"]),
]
for i, (j, nm, d, c) in enumerate(conns):
    yy = ey + 630 + i * 38
    dot(ex + 24, yy, c, 3.4)
    txt(ex + 38, yy + 4, j, 11, COL["ink"], mono=True, weight="600")
    txt(ex + 130, yy + 4, nm, 11, c)
    txt(ex + 250, yy + 4, d, 9.5, COL["dim"], mono=True)

# footer
txt(40, H - 26, "Interconnect schematic — exact pin nets in netlist.md. Modules (Pixhawk, Pi, buck, IBT-2) are off-board and connectorized.",
    11.5, COL["dim"], italic=True)
txt(W - 40, H - 26, "rev A · 2026-07 · MIT", 11, COL["dim"], "end", mono=True)

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" '
       f'width="{W}" height="{H}" font-family="sans-serif">' + "".join(P) + "</svg>")
open("schematic.svg", "w").write(svg)
print(f"schematic.svg written ({len(svg)} bytes)")
