#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate the MowerCarrier board placement / outline drawing (SVG, top view).

Dimensioned component-placement drawing for a 120 x 100 mm 2-layer board:
connector/module positions, mounting holes, high-current keepout, silk labels.
Run:  python3 gen_layout.py   ->   layout.svg
"""
BW, BH = 120.0, 100.0          # board mm
S = 6.0                         # px per mm
M = 70                          # margin px
W = int(BW * S + 2 * M)
H = int(BH * S + 2 * M) + 60
C = dict(bg="#0d1117", board="#0b3d2e", boardln="#1f7a52", ink="#e6edf3",
         dim="#9aa7b4", grn="#3fb950", silk="#d7e6dd", cu="#c98a3a",
         hole="#0d1117", pwr="#ff5c5c", warn="#ff9f43")
P = []


def esc(s): return s.replace("&", "&amp;").replace("<", "&lt;")


def mm(x, y): return (M + x * S, M + y * S)


def box(xmm, ymm, wmm, hmm, label, fill="#0e5540", stroke=None, sub="", txtc=None):
    x, y = mm(xmm, ymm)
    w, h = wmm * S, hmm * S
    P.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="4" '
             f'fill="{fill}" stroke="{stroke or C["boardln"]}" stroke-width="1.3"/>')
    P.append(f'<text x="{x+w/2:.1f}" y="{y+h/2-1:.1f}" font-family="\'JetBrains Mono\',monospace" '
             f'font-size="11" font-weight="600" fill="{txtc or C["silk"]}" text-anchor="middle">{esc(label)}</text>')
    if sub:
        P.append(f'<text x="{x+w/2:.1f}" y="{y+h/2+13:.1f}" font-family="sans-serif" '
                 f'font-size="9" fill="{C["dim"]}" text-anchor="middle">{esc(sub)}</text>')


def hole(xmm, ymm):
    x, y = mm(xmm, ymm)
    P.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="6" fill="none" stroke="{C["cu"]}" stroke-width="1.6"/>')
    P.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="2.6" fill="{C["hole"]}"/>')


def dimline(x1mm, y1mm, x2mm, y2mm, label, off=22, vert=False):
    x1, y1 = mm(x1mm, y1mm); x2, y2 = mm(x2mm, y2mm)
    if vert:
        xx = x1 - off
        P.append(f'<line x1="{xx}" y1="{y1}" x2="{xx}" y2="{y2}" stroke="{C["grn"]}" stroke-width="1"/>')
        P.append(f'<line x1="{xx-4}" y1="{y1}" x2="{xx+4}" y2="{y1}" stroke="{C["grn"]}" stroke-width="1"/>')
        P.append(f'<line x1="{xx-4}" y1="{y2}" x2="{xx+4}" y2="{y2}" stroke="{C["grn"]}" stroke-width="1"/>')
        P.append(f'<text x="{xx-8}" y="{(y1+y2)/2+3}" font-family="\'JetBrains Mono\',monospace" font-size="11" '
                 f'fill="{C["grn"]}" text-anchor="end" transform="rotate(-90 {xx-8} {(y1+y2)/2})">{esc(label)}</text>')
    else:
        yy = y1 - off
        P.append(f'<line x1="{x1}" y1="{yy}" x2="{x2}" y2="{yy}" stroke="{C["grn"]}" stroke-width="1"/>')
        P.append(f'<line x1="{x1}" y1="{yy-4}" x2="{x1}" y2="{yy+4}" stroke="{C["grn"]}" stroke-width="1"/>')
        P.append(f'<line x1="{x2}" y1="{yy-4}" x2="{x2}" y2="{yy+4}" stroke="{C["grn"]}" stroke-width="1"/>')
        P.append(f'<text x="{(x1+x2)/2}" y="{yy-6}" font-family="\'JetBrains Mono\',monospace" font-size="11" '
                 f'fill="{C["grn"]}" text-anchor="middle">{esc(label)}</text>')


P.append(f'<rect width="{W}" height="{H}" fill="{C["bg"]}"/>')
P.append(f'<text x="{M}" y="40" font-family="sans-serif" font-size="20" font-weight="700" fill="{C["ink"]}">MowerCarrier Rev A — placement (top)</text>')
P.append(f'<text x="{W-M}" y="40" font-family="\'JetBrains Mono\',monospace" font-size="12" fill="{C["grn"]}" text-anchor="end">120 × 100 mm · 2-layer · 2oz Cu</text>')

# board outline
bx, by = mm(0, 0)
P.append(f'<rect x="{bx}" y="{by}" width="{BW*S}" height="{BH*S}" rx="10" '
         f'fill="{C["board"]}" stroke="{C["boardln"]}" stroke-width="2"/>')

# mounting holes (M3, 5mm from corners)
for hx, hy in [(5, 5), (BW - 5, 5), (5, BH - 5), (BW - 5, BH - 5)]:
    hole(hx, hy)

# --- POWER ZONE (left, high current) — shaded keepout for 2oz pours
kx, ky = mm(0, 0)
P.append(f'<rect x="{kx}" y="{ky}" width="{42*S}" height="{BH*S}" rx="10" fill="{C["pwr"]}" opacity="0.05"/>')
P.append(f'<text x="{kx+8}" y="{ky+BH*S-8}" font-family="\'JetBrains Mono\',monospace" font-size="9.5" '
         f'fill="{C["pwr"]}">POWER ZONE · wide 2oz pours · &gt;=3mm</text>')

# placements (xmm, ymm, w, h)
box(4, 8, 20, 14, "XT60", "#3a1214", stroke=C["pwr"], sub="12V IN", txtc=C["pwr"])
box(4, 26, 34, 10, "F0 30A", "#111a12", sub="main fuse")
box(4, 40, 16, 16, "Q1", "#111a12", sub="revP")
box(22, 40, 16, 16, "TVS+C", "#111a12", sub="clamp")
box(4, 60, 34, 30, "FUSE BLOCK", "#111a12", sub="F1-F4 branches")
box(46, 8, 30, 24, "K1 DRIVE", "#3a1f10", stroke=C["warn"], sub="40A relay", txtc=C["warn"])
box(46, 36, 30, 24, "K2 PTO", "#3a1f10", stroke=C["warn"], sub="40A relay", txtc=C["warn"])
box(46, 64, 30, 12, "Q2/Q3 drv", "#111a12", sub="coil FETs")
box(84, 8, 32, 84, "ESP32", "#10251a", stroke=C["grn"], sub="DevKitC socket", txtc=C["grn"])
box(46, 80, 30, 12, "J_FC", "#0e1c28", sub="Pixhawk PWM")
# right-edge I/O terminals
for i, (lab) in enumerate(["MOTOR V+", "PTO OUT", "J_M1", "J_M2", "J_POT_L", "J_POT_R", "J_5V"]):
    box(84, 8 + 0, 0, 0, "", fill="none")  # noop keep numbering
# screw-terminal strip along bottom
labels = ["MOTOR V+", "PTO", "POT_L", "POT_R", "M1", "M2", "5V"]
for i, lab in enumerate(labels):
    box(4 + i * 16, 92, 15, 6, lab, "#0e1c28", sub="")

# dimensions
dimline(0, 0, BW, 0, "120 mm")
dimline(0, 0, 0, BH, "100 mm", vert=True)

# legend
ly = M + BH * S + 30
items = [("board / GND pour", C["board"]), ("power zone (2oz)", C["pwr"]),
         ("relay / driver", C["warn"]), ("ESP32 / logic", C["grn"]), ("M3 mount hole", C["cu"])]
for i, (lab, c) in enumerate(items):
    x = M + i * 200
    P.append(f'<rect x="{x}" y="{ly-10}" width="16" height="12" rx="2" fill="{c}" opacity="0.5" stroke="{c}"/>')
    P.append(f'<text x="{x+22}" y="{ly}" font-family="sans-serif" font-size="11.5" fill="{C["dim"]}">{esc(lab)}</text>')

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}">'
       + "".join(P) + "</svg>")
open("layout.svg", "w").write(svg)
print(f"layout.svg written ({len(svg)} bytes, {W}x{H})")
