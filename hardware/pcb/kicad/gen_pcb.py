# SPDX-License-Identifier: MIT
"""PCB stage: place design.py's parts on a 120 x 100 mm 2-layer board, autoroute with
Freerouting, pour GND, and leave a DRC-clean mowercarrier.kicad_pcb. Needs pcbnew.

Placement (board mm, origin = top-left corner, y down) follows ../layout.svg's zoning:
power column on the left (XT60 -> Q1 -> F0 -> branch fuses with their output
terminals on the left edge), relays in the middle, ESP32 socket pair on the right,
field terminals + logic headers along the bottom and right.
"""
import json
import os
import shutil
import subprocess

import pcbnew

import design

OX, OY = 50.0, 50.0                        # board origin on the KiCad page (mm)
BW, BH = 120.0, 100.0
KFP = os.environ.get("KICAD9_FOOTPRINT_DIR",
                     os.path.expanduser("~/Applications/KiCad/KiCad.app/Contents/SharedSupport/footprints"))

# ref: (x, y, rotation°, side) — footprint origin in board mm
P = design.ESP_ROW_PITCH
PLACE = {
    # top edge: XT60 mating face flush with the edge (body -16.35..+2.55 from its pads)
    "J1": (14.0, 16.35, 0, "F"),
    "Q1": (31.0, 18.0, 0, "F"), "R1": (44.0, 9.0, 0, "F"), "D5": (42.6, 17.5, 0, "F"),   # D5 cathode pad lands in the +12V_RP pour
    "F0": (36.0, 27.5, 180, "F"),       # flipped: +12V_RP pads beside Q1, +12V_BUS pads on the bus pour
    "D1": (24.0, 34.0, 0, "F"), "C1": (40.0, 35.0, 0, "F"),
    # left edge: branch fuse + its output terminal per row, wire entry facing the edge (270°)
    "F1": (28.7, 43.5, 180, "F"), "TB1": (5.1, 38.5, 270, "F"),
    "F2": (28.7, 55.5, 180, "F"), "TB2": (5.1, 50.5, 270, "F"),
    "F3": (28.7, 67.5, 180, "F"), "TB3": (5.1, 62.5, 270, "F"),
    "F4": (16.0, 77.0, 0, "F"), "F5": (16.0, 89.0, 0, "F"),
    # relays (origin = COM pin; body spans x-23.2..+4.4, y-12.6..+19.2)
    "K1": (74.0, 24.0, 0, "F"), "K2": (74.0, 64.0, 0, "F"),
    "Q2": (44.0, 44.0, 0, "F"), "D2": (46.5, 49.5, 0, "F"), "R2": (39.0, 43.0, 0, "F"), "R3": (39.0, 47.0, 0, "F"),
    "Q3": (44.0, 64.0, 0, "F"), "D3": (46.5, 69.5, 0, "F"), "R4": (39.0, 63.0, 0, "F"), "R5": (39.0, 67.0, 0, "F"),
    "R8": (40.0, 80.0, 0, "F"), "LED2": (45.0, 80.0, 0, "F"),
    # bottom edge field terminals (wire entry toward the edge, 0°)
    "TB4": (38.0, 94.9, 0, "F"), "TB5": (50.0, 94.9, 0, "F"), "TB6": (62.0, 94.9, 0, "F"),
    "TB8": (74.0, 94.9, 0, "F"), "TB9": (86.0, 94.9, 0, "F"),
    # top edge e-stop terminal (180°: entry faces up), pull-up beside it
    "TB7": (100.0, 5.1, 180, "F"), "R6": (104.0, 13.0, 0, "F"),
    # ESP32-DevKitC socket pair + logic headers
    "H1": (92.0, 18.0, 0, "F"), "H2": (92.0 + P, 18.0, 0, "F"),
    "J4": (82.0, 40.0, 0, "F"), "J5": (86.0, 40.0, 0, "F"),
    "J2": (82.0, 62.0, 0, "F"), "J3": (86.0, 62.0, 0, "F"),
    "C2": (97.0, 74.0, 0, "F"), "C3": (97.0, 78.0, 0, "F"), "C4": (97.0, 82.0, 0, "F"),
    "R7": (106.0, 74.0, 0, "F"), "LED1": (106.0, 78.0, 0, "F"),
    "MH1": (4.5, 4.5, 0, "F"), "MH2": (115.5, 4.5, 0, "F"),
    "MH3": (4.5, 95.5, 0, "F"), "MH4": (115.5, 95.5, 0, "F"),
}


def knet(n):
    """KiCad names a root-sheet local-label net "/NAME" — match it exactly (schematic parity)."""
    return "/" + n


def mm(v):
    return pcbnew.FromMM(v)


def write_pro(here, project):
    """Net classes + rules live in the .kicad_pro (read by pcbnew, DRC and the DSN export)."""
    path = os.path.join(here, project + ".kicad_pro")
    pro = json.load(open(path)) if os.path.exists(path) else {}
    classes = [{"name": "Default", "clearance": design.DEFAULT_CLEAR, "track_width": design.DEFAULT_TRACK,
                "via_diameter": 0.8, "via_drill": 0.4, "priority": 2147483647}]
    patterns = []
    for i, (name, (w, clr, nets)) in enumerate(design.NETCLASSES.items()):
        classes.append({"name": name, "clearance": clr, "track_width": w,
                        "via_diameter": 1.2 if w >= 1 else 0.8, "via_drill": 0.6 if w >= 1 else 0.4,
                        "priority": i})
        patterns += [{"netclass": name, "pattern": knet(n)} for n in nets]
    pro.setdefault("meta", {"filename": project + ".kicad_pro", "version": 3})
    pro["net_settings"] = {"classes": classes, "meta": {"version": 4}, "netclass_patterns": patterns}
    pro.setdefault("board", {})["design_settings"] = {
        "rules": {"min_clearance": 0.2, "min_track_width": 0.2, "min_via_diameter": 0.6,
                  "min_through_hole_diameter": 0.3, "min_hole_clearance": 0.25,
                  "min_copper_edge_clearance": 0.5, "min_hole_to_hole": 0.25},
        "defaults": {"board_outline_line_width": 0.1}}
    json.dump(pro, open(path, "w"), indent=2)


def load_fp(fpid, here):
    lib, name = fpid.split(":")
    d = os.path.join(here, "MowerCarrier.pretty") if lib == "MowerCarrier" else os.path.join(KFP, lib + ".pretty")
    fp = pcbnew.FootprintLoad(d, name)
    assert fp is not None, fpid
    fp.SetFPID(pcbnew.LIB_ID(lib, name))
    return fp


def kicad_netlist(here, project):
    """{(ref, pin): net name} from `kicad-cli sch export netlist` — including KiCad's own
    unconnected-(...) nets for no-connect pins, so the PCB matches the schematic exactly."""
    import re
    out = os.path.join(here, "." + project + ".net")
    subprocess.run(["kicad-cli", "sch", "export", "netlist", "-o", out, os.path.join(here, project + ".kicad_sch")],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    txt = open(out).read()
    os.remove(out)
    pinnet = {}
    for chunk in txt.split('(net (code "')[1:]:          # one record per net (last one has no trailing newline)
        name = re.search(r'\(name "([^"]*)"\)', chunk).group(1)
        for ref, pin in re.findall(r'\(node \(ref "([^"]+)"\) \(pin "([^"]+)"\)', chunk):
            pinnet[(ref, pin)] = name
    return pinnet


def place(board, here, root, placed):
    pinnet = kicad_netlist(here, "mowercarrier")
    nets = {}
    for name in sorted(set(pinnet.values())):
        ni = pcbnew.NETINFO_ITEM(board, name)
        board.Add(ni)
        nets[name] = ni
    for (ref, pin), name in pinnet.items():          # design.py and KiCad must agree
        want = dict((r, p) for r, *_x, p in design.PARTS)[ref].get(pin)
        assert (want is None and name.startswith("unconnected-")) or knet(want or "") == name, (ref, pin, want, name)
    for ref, lib_id, value, fpid, part, pins in design.PARTS:
        fp = load_fp(fpid, here)
        fp.SetReference(ref)
        fp.SetValue(value)
        x, y, rot, side = PLACE[ref]
        board.Add(fp)
        fp.SetPosition(pcbnew.VECTOR2I(mm(OX + x), mm(OY + y)))
        fp.SetOrientationDegrees(rot)
        fp.SetPath(pcbnew.KIID_PATH("/" + placed[ref]))
        fp.SetSheetname("/")
        fp.SetSheetfile(os.path.basename(here) and "mowercarrier.kicad_sch")
        pads = {p.GetNumber() for p in fp.Pads() if p.GetNumber()}
        extra = set(pins) - pads
        assert not extra, f"{ref}: symbol pins {extra} have no pad in {fpid} ({sorted(pads)})"
        for p in fp.Pads():
            n = pinnet.get((ref, p.GetNumber()))
            if n:
                p.SetNet(nets[n])
    # board outline
    rect = pcbnew.PCB_SHAPE(board, pcbnew.SHAPE_T_RECTANGLE)
    rect.SetStart(pcbnew.VECTOR2I(mm(OX), mm(OY)))
    rect.SetEnd(pcbnew.VECTOR2I(mm(OX + BW), mm(OY + BH)))
    rect.SetLayer(pcbnew.Edge_Cuts)
    rect.SetWidth(mm(0.1))
    board.Add(rect)
    return nets


def _zone(board, net, layer, pts, prio, solid):
    z = pcbnew.ZONE(board)
    z.SetLayer(layer)
    z.SetNet(net)
    z.SetAssignedPriority(prio)
    z.SetLocalClearance(mm(0.5))
    z.SetMinThickness(mm(0.25))
    if solid:
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)          # power: no thermal necking
    else:
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_THERMAL)
        z.SetThermalReliefGap(mm(0.4))
        z.SetThermalReliefSpokeWidth(mm(0.8))
    ol = z.Outline()
    ol.NewOutline()
    for px, py in pts:
        ol.Append(mm(OX + px), mm(OY + py))
    board.Add(z)
    return z


# 30 A trunk as solid pours (board mm). Different-net pads inside are cleared by the fill.
POWER_ZONES = [
    ("+12V_IN", "F", [(17.5, 10.5), (34.4, 10.5), (34.4, 19.6), (17.5, 19.6)]),                 # XT60 + -> Q1 drain
    ("+12V_RP", "F", [(34.9, 16.3), (41.0, 16.3), (41.0, 29.2), (31.4, 29.2), (31.4, 23.2), (34.9, 23.2)]),  # Q1 source -> F0
    ("+12V_BUS", "B", [(11.4, 21.0), (37.6, 21.0), (37.6, 30.5), (42.0, 30.5), (42.0, 39.5),
                       (37.6, 39.5), (37.6, 93.5), (11.4, 93.5)]),                                # F0 -> branch fuses + C1
]
# each branch fuse's 4-leg output clip joined solidly on top — added AFTER routing, so the
# router still runs each output to its load (it treats pads inside a pour as connected)
OUTPUT_ZONES = [
    ("+12V_BUCK1", "F", [(14.6, 39.7), (20.7, 39.7), (20.7, 44.8), (14.6, 44.8)]),
    ("+12V_BUCK2", "F", [(14.6, 51.7), (20.7, 51.7), (20.7, 56.8), (14.6, 56.8)]),
    ("+12V_PM02", "F", [(14.6, 63.7), (20.7, 63.7), (20.7, 68.8), (14.6, 68.8)]),
    ("+12V_DRIVE", "F", [(24.0, 75.7), (30.1, 75.7), (30.1, 80.8), (24.0, 80.8)]),
    ("+12V_PTO", "F", [(24.0, 87.7), (30.1, 87.7), (30.1, 92.8), (24.0, 92.8)]),
]
# the three trunk pours are also track keepouts (vias allowed) so the autorouter can't cut them
KEEPOUT_NETS = ("+12V_IN", "+12V_RP", "+12V_BUS")


def add_power_zones(board):
    for net, side, pts in POWER_ZONES:
        layer = pcbnew.F_Cu if side == "F" else pcbnew.B_Cu
        _zone(board, board.FindNet(knet(net)), layer, pts, 10, True)
        if net in KEEPOUT_NETS:  # noqa: E501 — trunk pours double as track keepouts
            k = pcbnew.ZONE(board)
            k.SetIsRuleArea(True)
            k.SetLayer(layer)
            k.SetDoNotAllowTracks(True)
            k.SetDoNotAllowVias(False)
            k.SetDoNotAllowPads(False)
            k.SetDoNotAllowCopperPour(False)
            k.SetDoNotAllowFootprints(False)
            k.SetZoneName("no tracks: " + net + " pour")
            ol = k.Outline()
            ol.NewOutline()
            for px, py in pts:
                ol.Append(mm(OX + px), mm(OY + py))
            board.Add(k)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


def add_gnd_zones(board, nets):
    for layer, prio in ((pcbnew.B_Cu, 0), (pcbnew.F_Cu, 0)):
        z = pcbnew.ZONE(board)
        z.SetLayer(layer)
        z.SetNet(nets["GND"])
        z.SetAssignedPriority(prio)
        z.SetLocalClearance(mm(0.4))
        z.SetMinThickness(mm(0.25))
        z.SetPadConnection(pcbnew.ZONE_CONNECTION_FULL)          # GND carries the 30 A return
        ol = z.Outline()
        ol.NewOutline()
        for px, py in ((0.5, 0.5), (BW - 0.5, 0.5), (BW - 0.5, BH - 0.5), (0.5, BH - 0.5)):
            ol.Append(mm(OX + px), mm(OY + py))
        board.Add(z)
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())


def autoroute(board, here, project):
    fr = shutil.which("freerouting")
    assert fr, "freerouting not on PATH (scripts/setup-dev.sh --kicad)"
    dsn = os.path.join(here, project + ".dsn")
    ses = os.path.join(here, project + ".ses")
    if os.path.exists(ses):
        os.remove(ses)
    assert pcbnew.ExportSpecctraDSN(board, dsn), "DSN export failed"
    subprocess.run([fr, "-de", dsn, "-do", ses, "-mp", "120"],
                   check=True, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, timeout=900)
    assert os.path.exists(ses), "freerouting produced no .ses"
    assert pcbnew.ImportSpecctraSES(board, ses), "SES import failed"
    os.remove(dsn)
    os.remove(ses)


def build(here, project, root, placed, route=True):
    write_pro(here, project)
    path = os.path.join(here, project + ".kicad_pcb")
    board = pcbnew.NewBoard(path)
    board.SetCopperLayerCount(2)
    place(board, here, root, placed)
    add_power_zones(board)
    board.Save(path)
    board = pcbnew.LoadBoard(path)                     # reload: picks up .kicad_pro rules + net classes
    pcbnew.ZONE_FILLER(board).Fill(board.Zones())      # refill under the real clearance rules
    board.Save(path)
    if route:
        autoroute(board, here, project)
        for net, side, pts in OUTPUT_ZONES:
            _zone(board, board.FindNet(knet(net)), pcbnew.F_Cu if side == "F" else pcbnew.B_Cu, pts, 10, True)
        nets = {"GND": board.FindNet(knet("GND"))}
        add_gnd_zones(board, nets)
        board.Save(path)
    print("pcb:", path)
