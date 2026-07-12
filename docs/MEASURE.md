# The 10-minute caliper session — close the last [MEASURE]s

Grab: digital caliper, tape measure, this sheet. Machine off, key out, on flat ground.
Every number below maps to ONE variable; after filling them in, run the two commands at
the bottom and the whole kit re-fits itself.

| # | Measure | How | Write it here | Variable (file) |
|---|---------|-----|---------------|-----------------|
| 1 | **Lap-bar tube OD** | caliper on the straight clamp section below the bend; check TWO spots 90° apart — if they differ ≥0.5 mm the tube is oval | ______ mm | `LAP_BAR_TUBE_OD` (`cad/params.scad` §1) — if oval: `LAP_BAR_IS_OVAL=true` + both axes |
| 2 | **Lap-bar spacing** | tape, centre-to-centre between the two bars in the operating (in) position | ______ mm | `LAP_BAR_SPACING` |
| 3 | **Lap-bar travel** | tape, tip of one bar: full-forward to full-reverse arc length ÷ 2 ≈ throw from neutral | ______ mm | `LAP_BAR_TRAVEL` |
| 4 | **Clamp height** | tape, from the bar's lower pivot to where the actuator clamp will sit (straight section, clear of the bend) | ______ mm | `LAP_BAR_CLAMP_HEIGHT` |
| 5 | **Frame rail tube** | caliper across the main frame rail (should be ~50.8 sq) | ______ mm | `M_RAIL` (`cad/mower.scad`) |
| 6 | **Wheelbase** | tape, rear axle centre to front caster PIVOT centre | ______ mm | `M_WHEELBASE` — currently DERIVED (1170); this replaces it |
| 7 | **Seat pan width / depth** | tape, usable flat cushion | ______ / ______ mm | `SEAT_WIDTH` / `SEAT_DEPTH` |
| 8 | **Tyre pressures (cold)** | gauge, all four — also the sidewall max | RL __ RR __ FL __ FR __ psi | `TIRE_NOMINAL_PSI` (`software/companion/attachments.py`) |
| 9 | **Choke type** | look at the dash/engine: separate choke lever = manual; single key-start no lever = Smart-Choke | manual / smart | manual → order the choke servo; smart → skip it |
| 10 | **Model/serial plate** (under the seat) | photo it | — | confirms the 915256 vs 918011 variant |

## Then, back at the computer

```bash
# 1. put #1–#7 into cad/params.scad SECTION 1 (+ M_WHEELBASE in cad/mower.scad)
# 2. re-generate everything:
cd cad && ./export_stl.sh && ./bake_brims.sh     # re-fits all 32 parts + brims
./scripts/check.sh                               # envelope echo should now be tape-true
```

If #6 ≠ 1170 mm the envelope echo's length line will move — that's the point: the model
stops being derived and becomes measured. Re-render the gallery (`cad/render_gallery.sh`)
and rebuild the GLB when you want the site to match.

**While you're out there:** photograph the lap-bar pivot area and the frame nose from
30 cm — the two spots where printed brackets meet steel.
