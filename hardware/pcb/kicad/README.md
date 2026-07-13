# KiCad project — Rev A route-up (gated on a KiCad install)

The complete design package is one level up: `netlist.md` (authoritative net-by-net),
`BOM.md` (LCSC part numbers), `schematic.svg` / `layout.svg` (reference placement),
`FABRICATION.md` (board spec: 120×100 mm, 2-layer, 2 oz Cu).

Route-up procedure:
1. `kicad` → new project here (`mowercarrier.kicad_pro`)
2. Recreate the schematic from `../netlist.md` (it is written net-by-net for exactly this)
3. Footprints per `../BOM.md` (pitfalls flagged there: ESP32 header pitch, P-FET thermals)
4. Import `../layout.svg` as a placement underlay; route power pours first (30 A paths)
5. DRC with JLCPCB 2-oz rules, then `kicad-cli sch erc` + `kicad-cli pcb drc` — these two
   commands are the #39 CI gate; they join scripts/check.sh the moment .kicad_* files exist.

Why not generated here: KiCad is a multi-GB install and hand-written .kicad_sch files
without ERC verification would be worse than none — see docs/DESIGN-LOG.md (honesty rule).
