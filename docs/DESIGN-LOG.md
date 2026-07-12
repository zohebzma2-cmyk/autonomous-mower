# Design Log — how this project actually evolved

Every entry below maps to real commits in this repo (`git log --reverse`). This is the
honest record of the iterative loop: **model → render → measure against the spec sheet →
find what's wrong → fix → re-export**. Nothing was right the first time; that's the point
of logging it.

## Phase 0 — one-day design sprint (2026-06-25 → 26)

| Iteration | What happened | What forced it |
|---|---|---|
| v0 CAD kit (`38e0386`) | 23 printable parts, parametric off `params.scad` SECTION 1 | reproducibility on ANY zero-turn, not just this one |
| Bed-fit fix (`9f75bc7`) | equipment_plate → 140 mm, e-stop pedestal → 139 mm | FlashForge Adventurer 3 bed is 150 mm — two parts didn't fit; added an automated bbox gate so it can't regress |
| Baked brims (`80480d3`) | every STL ships with a bed-adhesion brim | ASA/PETG outdoors parts warp; slicer brims kept being forgotten |
| Real carts (`6532a8d`, `94f3641`) | live-verified Amazon cart ($909) + vendor-direct ($596) | agent-sourced ASINs rot — both actuator ASINs 404'd; every link re-verified on its live page |
| Software v0 (`db062fa` →) | one web UI for iPad + on-unit kiosk, sim-first, then MAVLink | can't test on hardware that isn't built yet; sim → SITL → real FC, same code |
| Machine confirmed (`91940a6`, `88c8fa9`) | Gravely **ZT X 52**, 2021 **Kohler** 7000, electric PTO | owner read the serial plate — killed two wrong assumptions (Kawasaki variant, factory ROPS) |
| Exact-spec pass (`0187902`) | RPLidar base is a **teardrop with a trapezoid bolt pattern**, not a circle; PA-14P clevis pin is ¼″ | three research agents against real datasheets — the "obvious" circular lidar plate was wrong |
| Prototype-v1 (`cf700c1`, `a0db0af`) | ESP32 lap-bar firmware (fail-to-neutral), ArduPilot params, wiring + kill-chain diagram, build manual | the actuator-control gap: ArduPilot can't close a position loop on a lap bar by itself |
| Precision + QA (`84c8782`) | dual-antenna moving-baseline heading (~0.4°) | single-GPS heading wanders at low speed and pivots — unacceptable for stripe-straight mowing |
| Open-sourced (`12494f6`) | MIT, safety README, genericized coords | decided the R&D vehicle should be public even though the commercial path is RaaS |

## Phase 1 — fabrication reality (2026-07-09 → 10)

| Iteration | What happened | What forced it |
|---|---|---|
| Real colours + export groups (`0568c4f`) | multi-material GLB (red/black/graphite) | the site's grey model didn't look like the machine in the garage |
| Higher-fidelity mock (`2958154`) | casters, fenders, deck detail, tanks | the placement mock was too crude to judge clearances visually |
| Sourcing package (`4571088`…`7db66d3`) | DXF flat parts + dimensioned PDFs + STL→STEP converter | **OpenSCAD cannot export STEP** and machinists cannot cut STL — every flat part re-exported as DXF, 3D parts mesh-sewn to STEP via CadQuery/OCP |
| MowerCarrier PCB (`26f15d2`) | 2-layer 120×100 carrier board: power tree + kill-chain + ESP32 | the hand-wired harness was the least reproducible, most safety-critical part of the build |

## Phase 2 — down to the millimetre (2026-07-11 → 12)

| Iteration | What happened | What forced it |
|---|---|---|
| Fidelity pass (`49c78d5`) | treaded tyres + red rims, contoured seat, hood + louvres, bent lap bars, **branding as raised geometry** | renders were still the old grey mock; decals had to survive STL→GLB, so lettering became geometry |
| Stray-sphere bug | thin plates rebuilt with `rbox` | `rbox_full(size, r)` with `r > min(dim)/2` leaves a lone minkowski sphere floating in space — found it hovering next to the deck in a render |
| Width fix (`bf96a92`) | deck **shell** 1400 mm + 264 mm deflector = exactly 1610 mm | first envelope check double-counted the one-sided chute; a 52″ deck's shell is wider than its cutting width |
| Wheelbase derivation | 900 → **1170 mm**, overall length exactly 1968 mm | at 900 mm the deck geometrically could not fit between the tyres — the collision the renders had been hiding; derived from the published overall length, to be confirmed by tape measure |
| Blades + hollow deck | 3 × 460 mm high-lift blades on real spindles, deck hollowed underneath | "the machine has blades" — and a solid deck hull had nowhere to put them |
| Blade-spin GLB animation | one blade mesh, three glTF nodes, baked `blade-spin` rotation | model-viewer can't animate arbitrary nodes from JS; a baked glTF animation plays on hover |
| Kohler externals | dipstick (yellow ring, accent colour group), oil filter, oil-fill cap, intake elbow, pull start | "down to the dipstick" — the service touch-points a Kohler owner actually grabs |

## Constraints A–Z (every one of these actually bit)

- **A**SIN rot — agent-sourced Amazon links 404 within days; only live-verified links count.
- **B**ed size — 150 mm FlashForge bed gates every printable part (automated bbox check).
- **C**GAL render time — the black colour group (4 treaded tyres) takes ~55 min to export; runs detached with a monitor.
- **D**eck shell ≠ cutting width — 52″ cuts, ~1400 mm of steel; the spec sheet's 1610 includes the deflector.
- **E**-stop chain — hardware-AND-software: NC mushroom on the coil+ side, MOSFET on coil−; either drop kills power.
- **F**onts — OpenSCAD `text()` needs a real installed font; branding uses Helvetica Bold as geometry.
- **G**PS mast — no factory ROPS on the ZT X (residential trim), so the mast mounts to the seat frame instead.
- **H**otspots — the site's 3D annotations only survive CAD revisions because the GLB is centred on a FIXED centroid.
- **I**P ratings — PA-14P is IP54, not the IP66 the marketing page implied; needs a rod boot outdoors.
- **J**SN-SR04T — overhead ultrasonic protects the GPS mast from tree limbs; the mast is the tallest thing on the machine.
- **K**ohler vs Kawasaki — same model name, two engine variants with different weights; the serial plate settles it.
- **L**iability — blades + autonomy = the gating business constraint; RaaS beachhead (solar farms, cemeteries), not kit sales.
- **M**inkowski degeneracy — `rbox_full` with radius > half a dimension silently emits a stray sphere.
- **N**o OEM CAD — Gravely publishes exploded parts diagrams, not STEP; the base machine is a spec-matched mock, the retrofit parts are datasheet-exact.
- **O**verlap — 3 × 460 mm blades on 396 mm spindle spacing: tip circles must overlap or you leave stripes.
- **P**PO clutch — electric Ogura-GT 12 V clutch means blade kill is one relay; a manual PTO would have needed an actuator.
- **Q**uote gates — SendCutSend/OSH Cut require accounts to quote; the site shows a labelled indicative estimate instead of a fake quote.
- **R**TK is non-negotiable — ±2 cm is the difference between "robot mower" and "lawn roulette"; ~$200 of the budget.
- **S**TL is not machinable — machinists need STEP/DXF; OpenSCAD only exports meshes. Whole export pipeline exists because of this.
- **T**ext-buried-in-hull — lettering placed on a hulled surface sinks into the curve; badges sit on proud plates.
- **U**SD/EUR — ArduSimple ships from the EU; conversion + duties are real line items on the order sheet.
- **V**endor CAD gaps — no STEP exists for the AI HAT+, ANN-MB-00, IBT-2, JSN-SR04T; those stay accurate proxy volumes.
- **W**heelbase unknown — the one number no spec sheet publishes; derived (1170 mm) from overall length until the tape measure says otherwise.
- **X**T60 everywhere — one connector standard across the power tree so nothing can be plugged in backwards.
- **Y**ellow accents — dipstick ring, oil cap, PTO knob get their own colour group; service points should look like service points.
- **Z**T-2200 hydros — the drive the lap bars command; fail-to-neutral in the ESP32 firmware exists because hydros coast.
