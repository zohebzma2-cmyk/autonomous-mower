# Attachments & Agronomy — Phase 3 design

**Status: DESIGN + SIM.** The policy layer (interlocks, control math) is implemented and
tested in `software/companion/attachments.py`; the CAD placements live in `cad/mower.scad`
(`mower_attachments()`); hardware drivers land with the physical build. Additive iteration —
nothing from Phases 0–2 changed. See `docs/DESIGN-LOG.md`.

The thesis: once a machine holds ±2 cm RTK lines at a controlled speed, **every towed or
mounted implement inherits that precision.** Mowing is the beachhead; edging, blowing,
bagging, and spraying are the same navigation stack with different payloads.

---

## 1 · Ignition + choke (the machine starts itself)

The Kohler 7000 (KT725) is electric-start. The retrofit actuates the **key circuit**, not
the recoil: a starter relay closes the solenoid circuit; the kill side is the existing
**ignition-kill line in the e-stop chain** (magneto ground — the same wire the physical
e-stop already owns).

- **Interlocks before crank** (`attachments.can_crank`, tested): e-stop clear · PTO/blade
  off · no mission running · not already running/cranking.
- **Crank limits:** ≤ 5 s per attempt, 10 s starter cool-down between attempts.
- **Choke:** many 7000s carry Kohler **Smart-Choke** (automatic — nothing to actuate).
  Manual-choke variants get a small servo on the choke lever, scheduled by temperature:
  full below 10 °C, half to 20 °C, open when warm (`attachments.choke_for`, tested; the
  weather feed supplies ambient temperature when enabled).
- **E-STOP kills ignition** along with drive, PTO, and every attachment relay — verified
  in the suite (`test_estop_kills_ignition_and_attachments`).

## 2 · TPMS (tyre pressure monitoring)

External valve-stem RF/BLE sensors on all four tyres (the cheap motorcycle/ATV kind), a
USB receiver on the Pi. Low pressure changes ride height → un-levels the deck → wavy cut,
and increases steering scrub, long before a flat is visible.

- Nominals: rear 12 psi, front 20 psi — **set to your sidewall/manual spec** in
  `attachments.TIRE_NOMINAL_PSI`.
- Warn beyond ±25% of nominal; warnings stream in telemetry (`tire_warnings`) and show in
  the UI service strip. Advisory, not a movement block.

## 3 · Power bagger (dump-from-seat → dump-from-anywhere)

Twin rear bins on a rack, blower duct off the deck discharge — the Gravely Power Bagger /
Exmark UltraVac pattern — with the manual dump lever replaced by an **electric actuator on
the dump pivot** (same 12 V actuator family as the lap-bar units).

- Fill estimated from blade-on time scaled by camera grass coverage (`bagger_fill_step`)
  until a bin-full sensor is fitted; ~18 min of heavy cut fills the bins (tune on grass).
- **Dump interlocks** (tested): machine stopped · blade off · not already dumping.
  Cycle: raise 3 s → hold 2 s → lower 3 s.
- Fall-cleanup mode is just a coverage route with the bagger fitted + a dump waypoint at
  the pile: RTK drives to the pile, dumps itself, resumes.

## 4 · Blower + string-trimmer boom (edging on the same routes)

A rotating boom on the front corner carries a 12/24 V blower volute and a string-trimmer
head. The slew ring (servo-driven) points the payload: trimmer down for edging passes
along the geofence line, blower aimed at the driveway for the cleanup lap.

- Boom angle clamped 0–270°.
- **Trimmer gates like a blade** (tested): armed only, and ≤ 1.0 m/s — edging is a
  slow-roll operation. E-stop drops both payload relays.

## 5 · FIMCO 30-gal tow sprayer (speed-perfect application)

The 12 V FIMCO pump wires into a PWM relay driven by the companion. This is where RTK
speed control pays off directly:

- **Application rate follows ground speed** (`sprayer_duty`, tested): target L/m² × swath
  × speed → pump duty. Half speed = half flow = **identical dose per square metre**.
- **Turn pause** (tested): above 25 °/s of yaw the pump stops — headlands never get the
  double dose that burns herbicide stripes into a lawn.
- Tank level, duty, and litres applied stream in telemetry; empty tank refuses to spray.
- Towing note: the planner's smooth turns (below) matter even more with a trailer — the
  no-pivot arcs keep the drawbar angle sane.

## 6 · The perfect turn (why the pivot ruts your lawn)

A zero-turn pivot spins one wheel forward and one backward **in place**. All of the yaw
moment passes through two small contact patches as **shear on the turf**: the tread
doesn't roll over the grass, it twists against it. Under a 615 lb machine (plus operator
weight in the tyres' contact pressure), dry-soil static friction gives way, the root mat
tears, and you get the classic ZTR divot at every row end. Wet soil is worse — shear
strength drops with moisture.

Keep both wheels **rolling** and the same manoeuvre transmits through the patches as
rolling friction instead of shear — orders of magnitude gentler on the root mat. So the
planner (`missions.plan_coverage_turns`, tested) never pivots:

- **Row spacing ≥ 2r → smooth U**: 90° arc, straight cross-over, 90° arc. Both wheels
  roll forward the whole time (the outside wheel just travels further).
- **Row spacing < 2r → 3-point K-turn** (the tractor headland turn): 90° arc out,
  **straight reverse** of length `2r − spacing` while the tail swings, 90° arc forward
  onto the next row. Reversing straight keeps both patches rolling — the heading change
  happens across three gentle segments instead of one violent twist.
- Rows are inset by the turn radius (a **headland**) so every turn stays inside the
  geofence; `r = 1.2 m` default — the gentlest arc the ZT-2200 hydros hold accurately.

The result on the map: teardrop row-ends instead of black semicircles of dead turf.

---

## Sourcing (search terms — verify live listings, per the ASIN-rot rule)

| Item | Search | ~$ class |
|---|---|---|
| TPMS | "motorcycle TPMS external valve cap sensor USB/BLE" | $25–45 / 4 |
| Starter relay | already in the order sheet (40 A SPDT family) | — |
| Choke servo | "25 kg waterproof metal gear servo" (spare of the throttle unit) | $18 |
| Dump actuator | Progressive Automations PA-14 family, 8″ stroke class | ~$130 |
| Blower | "12V 24V brushless blower fan high CFM" or repurposed EGO/leaf-blower head + ESC | $40–90 |
| Trimmer head | "12V string trimmer head motor" or brushless outrunner + universal head | $30–60 |
| Boom slew | "25 kg servo continuous slew ring" or worm-gear turntable kit | $25–50 |
| Sprayer | FIMCO 30-gal tow (owned) + PWM relay module for the 12 V pump | $10 (relay) |
| Bagger | Gravely Power Bagger kit for the ZT X deck (dealer) — rack + bins donor | dealer |

**Safety note:** every one of these lands on the attachment power bus, which sits behind
the same e-stop-dropped relay bank as the PTO (docs/WIRING.md). Nothing spins, blows,
sprays, or dumps with the mushroom pressed.
