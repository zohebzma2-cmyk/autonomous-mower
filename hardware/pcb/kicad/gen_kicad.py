#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Generate the MowerCarrier Rev A.1 KiCad project from design.py.

    ./gen_kicad.sh            # runs this under KiCad's bundled Python (needs pcbnew)

Stages: project + library tables -> footprints -> schematic (ERC) -> PCB placement ->
Freerouting autoroute -> zones -> DRC with schematic parity. Everything is regenerated
from design.py, so review design.py + this file, not the generated .kicad_* files.
"""
import json
import os
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import design                       # noqa: E402
import gen_footprints               # noqa: E402
import gen_schematic                # noqa: E402

PROJECT = "mowercarrier"
SYMLIBS = sorted({p[1].split(":")[0] for p in design.PARTS})
FPLIBS = sorted({p[3].split(":")[0] for p in design.PARTS} - {"MowerCarrier"})


def write_project_files():
    sym = "(sym_lib_table\n\t(version 7)\n" + "".join(
        f'\t(lib (name "{n}") (type "KiCad") (uri "${{KICAD9_SYMBOL_DIR}}/{n}.kicad_sym") (options "") (descr ""))\n'
        for n in SYMLIBS) + ")\n"
    fp = "(fp_lib_table\n\t(version 7)\n" + "".join(
        f'\t(lib (name "{n}") (type "KiCad") (uri "${{KICAD9_FOOTPRINT_DIR}}/{n}.pretty") (options "") (descr ""))\n'
        for n in FPLIBS) + '\t(lib (name "MowerCarrier") (type "KiCad") (uri "${KIPRJMOD}/MowerCarrier.pretty") (options "") (descr "project footprints (gen_footprints.py)"))\n)\n'
    open(os.path.join(HERE, "sym-lib-table"), "w").write(sym)
    open(os.path.join(HERE, "fp-lib-table"), "w").write(fp)
    pro = {"meta": {"filename": PROJECT + ".kicad_pro", "version": 3},
           "board": {}, "schematic": {}, "net_settings": {"classes": [], "meta": {"version": 4}}}
    path = os.path.join(HERE, PROJECT + ".kicad_pro")
    if not os.path.exists(path):
        json.dump(pro, open(path, "w"), indent=2)


def main(stage="all"):
    write_project_files()
    gen_footprints.write_all()
    root, placed = gen_schematic.build(os.path.join(HERE, PROJECT + ".kicad_sch"), PROJECT, design.PARTS)
    json.dump({"root": root, "symbols": placed}, open(os.path.join(HERE, ".sch_uuids.json"), "w"), indent=1)
    print(f"schematic: {len(design.PARTS)} symbols")
    if stage == "sch":
        return
    import gen_pcb                   # needs pcbnew (KiCad's Python)
    gen_pcb.build(HERE, PROJECT, root, placed, route=(stage != "place"))
    if stage == "all":
        export_fab()


def _cli(*args):
    subprocess.run(["kicad-cli", *args], check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def export_fab():
    """Everything downstream of the board, regenerated with it: fab package, drawings, renders."""
    sch, pcb = (os.path.join(HERE, PROJECT + ext) for ext in (".kicad_sch", ".kicad_pcb"))
    fab, up = os.path.join(HERE, "fab"), os.path.dirname(HERE)
    ger = os.path.join(fab, "gerbers")
    shutil.rmtree(fab, ignore_errors=True)
    os.makedirs(ger)
    _cli("pcb", "export", "gerbers", "--layers", "F.Cu,B.Cu,F.Paste,B.Paste,F.Silkscreen,B.Silkscreen,F.Mask,B.Mask,Edge.Cuts",
         "--subtract-soldermask", "-o", ger + "/", pcb)
    _cli("pcb", "export", "drill", "--format", "excellon", "--excellon-separate-th", "--generate-map",
         "--map-format", "gerberx2", "-o", ger + "/", pcb)
    shutil.make_archive(os.path.join(fab, PROJECT + "-gerbers"), "zip", ger)
    _cli("pcb", "export", "pos", "--format", "csv", "--units", "mm", "--side", "both", "--exclude-dnp",
         "-o", os.path.join(fab, PROJECT + "-pos.csv"), pcb)
    _cli("sch", "export", "bom", "--fields", "Reference,Value,Footprint,LCSC/MPN,${QUANTITY}",
         "--labels", "Designator,Value,Footprint,LCSC/MPN,Qty", "--group-by", "Value,Footprint,LCSC/MPN",
         "--exclude-dnp", "-o", os.path.join(fab, PROJECT + "-bom.csv"), sch)
    # drawings in hardware/pcb/ (replace the Rev A concept SVGs)
    tmp = os.path.join(fab, ".svg")
    _cli("sch", "export", "svg", "--exclude-drawing-sheet", "-o", tmp, sch)
    shutil.move(os.path.join(tmp, PROJECT + ".svg"), os.path.join(up, "schematic.svg"))
    shutil.rmtree(tmp)
    _cli("pcb", "export", "svg", "--layers", "Edge.Cuts,F.Cu,B.Cu,F.Silkscreen", "--page-size-mode", "2",
         "--exclude-drawing-sheet", "-o", os.path.join(up, "layout.svg"), pcb)
    _cli("pcb", "render", "--side", "top", "--width", "1600", "--height", "1300", "--quality", "high",
         "--background", "opaque", "-o", os.path.join(up, "render-top.png"), pcb)
    _cli("pcb", "render", "--rotate", "-45,0,-25", "--zoom", "1.1", "--width", "1600", "--height", "1200",
         "--quality", "high", "--background", "opaque", "-o", os.path.join(up, "render-iso.png"), pcb)
    print("fab: gerbers zip, pos, bom -> fab/; schematic.svg, layout.svg, renders -> hardware/pcb/")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "all")
