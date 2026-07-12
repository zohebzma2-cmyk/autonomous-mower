# Tool checklist — everything the build manual assumes

Nothing exotic. ✅ = most home garages already have it. The two starred items are
the ones people actually end up buying.

## Measure & mark
- ✅ Tape measure (the wheelbase + mast placements)
- ★ **Digital caliper** — SECTION 1 of `params.scad` lives and dies by the lap-bar OD
  measurement; a $20 caliper is the single most important tool in this build
- ✅ Permanent marker / centre punch

## Mechanical
- ✅ Socket set (SAE — the Gravely is imperial) + combination wrenches
- ✅ Hex/Allen keys (metric — every printed bracket uses M3–M6)
- ✅ Screwdrivers, pliers, utility knife (brim removal)
- ✅ Drill + bits (frame-rail pilot holes for the rail anchors and boom base)
- ✅ **Jack stands / ramps** — commissioning REQUIRES wheels-off-ground testing
  (BUILD.md §11); never skip this
- Torque wrench (nice-to-have for the spindle/blade bolts — the manual's specs apply)

## Electrical
- ✅ Wire strippers + ★ **ratcheting crimper** (marine heat-shrink connectors — a bad
  crimp in a vibrating, wet machine is a future no-start in tall grass)
- ✅ Soldering iron (ESP32 headers, pot leads) + heat gun / lighter for heat-shrink
- ✅ Multimeter — the kill-chain checkout in WIRING.md is continuity + voltage checks
- Zip ties, split loom, dielectric grease (already on the order sheet)

## Printing
- FlashForge Adventurer 3 (or any ≥150 mm bed) · PETG or ASA
- Deburring blade / flush cutters for brim edges
- Heat-set insert tip for the soldering iron (M3 inserts in several parts)

## What you do NOT need
- No welding (everything clamps or bolts to the frame)
- No machining for the prototype (printed brackets first; the DXF/STEP package in
  `docs/SOURCING-AND-FABRICATION.md` is for the aluminium upgrade later)
- No engine work beyond the dipstick (the retrofit touches throttle, choke lever,
  key circuit, and PTO wire — all external)
