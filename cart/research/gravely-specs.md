# Gravely 52" Seated Zero-Turn — Real Published Specs (for CAD retrofit)

Research date: 2026-06-26. Purpose: replace nominal CAD parameters with published
manufacturer/dealer numbers for the owner's "Gravely 52 inch" twin-lap-bar seated ZT.

> **Rule followed:** every value below is tagged with the source page it was actually
> fetched from. Anything not on a fetched page is marked **NOT PUBLISHED → MUST MEASURE**.
> Do not promote any "must-measure" value to "verified" without calipers on the real machine.

---

## 0. Which model is it? (identify before trusting a column)

"Gravely 52 inch" seated ZT with twin lap bars maps to one of these. They share the same
basic operator station / lap-bar architecture but differ in frame, transaxle, tires, weight.

| Likelihood | Model | Tier | Tells on the machine |
|---|---|---|---|
| **Most likely** | **ZT X 52** or **ZT XL 52** | Residential / prosumer | Stamped-rail frame, EZT or ZT-2800 transaxles, 20" rear tires, plastic floor pan |
| Likely (if heavier) | **ZT HD 52** | Premium residential | Tubular frame, ZT-3100 transaxles, 22" rear tires, ~810 lb |
| Less likely (commercial) | **Pro-Turn 152 / 252** | Commercial | ROPS bar, suspension seat, 10 gal fuel, ZT-3400/5400 |

**Action:** read the model + serial off the plate (usually under the seat or on the LH frame
rail). The number (e.g. `918015`, `991069`, `991083`, `991129`) pins the exact column. Until
then, treat ZT X / ZT XL 52 as the working assumption.

---

## 1. Spec tables (per model)

### ZT X 52 (Kawasaki) — *most likely candidate*
Source: https://www.allmachines.com/mowers/gravely-zt-x-52-kawasaki

| Spec | Value | Notes |
|---|---|---|
| Engine | Kawasaki FR691V, 23 hp, 726 cc | |
| Deck width | **52 in (1321 mm)** ✅ | 11 ga. steel, fabricated X-Factor |
| Deck cut-height | 1.5–4.5 in | |
| Length | 74.5 in | |
| Width | 55.6 in (no chute) / 66.7 in (chute down) | |
| Height | 46 in | |
| Weight | 695 lb | |
| Front caster tire | 11 × 6-5 (smooth pneumatic) | |
| Rear tire | 20 × 10-8 (aggressive turf) | |
| Fuel | 3.5 gal | |
| Speed | 7 mph fwd / 3 mph rev | |
| Transaxle | Hydro-Gear serviceable EZT | |
| **Electric PTO clutch** | **YES — "Electric Warner"** ✅ | relay-switchable, as your design assumes |
| Battery | 12 V, U1 group (see §4) | |
| Wheelbase | NOT PUBLISHED → MUST MEASURE | |

### ZT XL 52 (Kawasaki, model 918015)
Sources: https://www.allmachines.com/mowers/gravely-zt-xl-52-kawasaki ·
https://www.gravely.com/en-us/power-equipment/zero-turn-mowers/zt-xl/zt-xl-52-kawasaki (spec tab; live page renders specs client-side)

| Spec | Value | Notes |
|---|---|---|
| Engine | Kawasaki FR691V, 23 hp, 726 cc | Kohler variant = model 918014 |
| Deck width | **52 in (1321 mm)** ✅ | 11 ga. steel, fabricated X-Factor, 4.5 in deep |
| Deck cut-height | 1.5–4.5 in, 13 positions | |
| Length | 74.5 in | |
| Width | 55.6 in (no chute) / 66.7 in (chute) | |
| Height | 47 in | |
| Weight | 705 lb | |
| Front caster tire | 11 × 6-5 (smooth pneumatic) | |
| Rear tire | 20 × 10-10 (aggressive turf) | |
| Fuel | 3.5 gal | |
| Speed | 7 mph fwd / 3 mph rev | |
| Transaxle | Hydro-Gear ZT-2800 | |
| **Electric PTO clutch** | **YES — "Electric Warner"** ✅ | |
| Seat | 22 in plush high-back, padded arm rests, seat isolation | dims not published — §3 |
| Battery | 12 V, U1 group (see §4) | |
| Wheelbase | NOT PUBLISHED → MUST MEASURE | |

### ZT HD 52 (Kawasaki)
Source: https://www.allmachines.com/mowers/gravely-zt-hd-52-kawasaki ·
fuel cross-checked against owner's manual https://www.manualslib.com/manual/3232123/Gravely-Zt-Hd-52.html

| Spec | Value | Notes |
|---|---|---|
| Engine | Kawasaki FR691V, 23 hp, 726 cc | |
| Deck width | **52 in (1321 mm)** ✅ | 10 ga. fabricated X-Factor 3 |
| Deck cut-height | 1.5–5 in, 15 positions | |
| Length | 79 in | |
| Width | 56.2 in (no chute) / 67.3 in (chute) | |
| Height | 47 in | |
| Weight | 817 lb | |
| Front caster tire | 13 × 6.5-6 (smooth pneumatic) | |
| Rear tire | 22 × 11-10 (aggressive tread) | |
| Fuel | 5 gal (allmachines) / manual lists 6.5 gal — **reconcile by serial range** | |
| Speed | 8 mph fwd / reverse not published | |
| Transaxle | Hydro-Gear ZT-3100 | |
| **Electric PTO clutch** | **YES — "Electric Warner"**; replacement eBay listings confirm 12 V electric PTO clutch/brake | |
| Seat | High-back comfort, seat isolation, padded arm rests | dims not published — §3 |
| Battery | 12 V, U1 group (see §4) | |
| Wheelbase | NOT PUBLISHED → MUST MEASURE | |

### Pro-Turn 152 (commercial, model 991129) — *less likely for a homeowner*
Source: https://aeoutdoorpower.com/products/gravely-pro-turn-152-kawasaki-zero-turn-mower-991129

| Spec | Value | Notes |
|---|---|---|
| Engine | Kawasaki FX691V, 22 hp, 726 cc | commercial FX series |
| Deck width | **52 in (1321 mm)** ✅ | 3-blade fabricated |
| Front caster tire | 13 × 6.5-6 | |
| Rear tire | 23 × 10.5-12 | |
| Fuel | 10 gal | |
| Speed | 10 mph fwd / 5 mph rev | |
| Transaxle | Hydro-Gear ZT-3400 | |
| Seat | High-back suspension seat + ROPS | |
| Weight ~1,080 lb (search result, dealer copy — treat as approximate) | NOT on fetched spec table | verify if it turns out to be this model |
| L×W×H, wheelbase, PTO type, battery | NOT PUBLISHED on fetched page → MUST MEASURE / verify | |

> Pro-Turn 252 (model 992268): 27 hp Kawasaki FX, ZT-5400 transaxles, 52" deck — same family,
> heavier. Only pursue if the serial plate says Pro-Turn.

---

## 2. STEERING / LAP BARS — the retrofit-critical section

### VERIFIED (fetched from a source page)
- **Return-to-neutral IS sprung/damped.** Gravely sells OEM part **09282900 "Bracket, Return
  To Neutral/damper For Select Gravely Zero Turn Mowers"** ($7.99). The hydros are *not* free-
  floating; releasing the lap bars returns the levers (and pump swashplates) toward neutral via
  this damper bracket + the transaxle's internal neutral return.
  Source: https://www.gravely.com/en-us/part/gravely-zero-turn-mower-bracket-return-to-neutraldamper-09282900
- **Steering is mechanically adjustable** via an eccentric spacer on the lower control arm and
  adjustment holes / hex-bolt on the handlebar–upper-control-arm joint; each lever is set
  independently and must be matched L/R. There is also OEM **rod, steering adjustment 09235900**.
  Sources: https://www.gravely.com/en-us/part/gravely-zero-turn-mower-rod-steering-adjustment-09235900 ·
  steering-lever adjustment procedure: https://www.manualslib.com/manual/720659/Gravely-915170-Zt-42-Carb.html?page=28
- **Lap bars are round tubular steel** (standard Gravely twin-lever weldments, e.g. RH hand-
  control 04922400, LH speed-control weldment 04944451). Round, not oval.
  Source: https://www.gravely.com/en-us/part/04922400

### MUST-MEASURE (not published anywhere fetched — use calipers on the machine)
| Quantity | Realistic range / guidance | Why not verified |
|---|---|---|
| **Lap-bar tube OD** | Field-measure. Gravely does **not** publish the control-arm tube diameter. Common Gravely/Ariens lap-bar tube is **~1 in (25.4 mm) round**, occasionally up to ~1-1/8 in. Independent data point: the aftermarket "Greater Zero" lap-bar accessory advertises fit for bar diameters **~0.8 in–2 in**, i.e. nobody assumes a single OD. **Mic it before designing any clamp.** | No spec sheet or parts page states an OD; only grip part numbers exist. |
| **Tube wall thickness** | Measure (typ. 0.083–0.120 in for this class). Matters if you drill/clamp. | Not published |
| **Neutral-to-full lever travel (arc / linear at grip)** | Measure on the machine — swing the bar from neutral detent to full-forward stop and full-reverse stop; record grip-tip travel and pivot angle separately L and R. | Not published in any manual section fetched |
| **Lap-bar pivot location / height above seat pan** | Measure | Not published |
| **Round vs oval cross-section at the clamp point** | Confirmed round from parts imagery, but **verify by eye** at your exact clamp station (some bars flatten near welds) | — |

**Design takeaway for the retrofit clamp/actuator:** assume **round ~1 in (25.4 mm) tube** as the
nominal, but make the clamp adjustable for 0.8–1.25 in and **measure the actual OD + wall + travel
arc before cutting metal.** Treat the hydros as spring/damper return-to-neutral (your actuator must
overcome a centering force and the bar will fight back toward neutral when released).

---

## 3. Seat / seat pan (for the seat-mounted brain box)

### VERIFIED
- ZT XL 52: **"22 in plush high-back"** seat with **padded arm rests and seat isolation**
  (rubber-isolation mounts between seat pan and frame — note this for vibration of the brain box).
  Source: https://www.allmachines.com/mowers/gravely-zt-xl-52-kawasaki
- ZT HD 52: **high-back comfort seat, seat isolation, padded arm rests.**
  Source: https://www.allmachines.com/mowers/gravely-zt-hd-52-kawasaki
- Pro-Turn 152: **high-back suspension seat** (sprung — more vertical travel than the isolation
  mounts; brain-box mounting must tolerate suspension travel).
  Source: https://aeoutdoorpower.com/products/gravely-pro-turn-152-kawasaki-zero-turn-mower-991129

### MUST-MEASURE
- **Seat pan bolt pattern / hole spacing, pan width × depth, pan-to-frame standoff** — NOT
  PUBLISHED. Measure. Gravely uses a standard ~bolt-on pan; pattern varies by line.
- A **seat-switch (operator-presence) interlock** is present on all of these (kills PTO/engine
  when seat is unoccupied) — relevant if your "brain box" sits where it could trip/avoid the
  switch. Confirm the connector and normally-open/closed behavior on the actual harness.

---

## 4. Electrical (relay-switch / power notes)

### VERIFIED
- **Battery: 12 V, BCI Group U1.** Gravely OEM "Zero-Turn 12 Volt Battery" 04738800; common
  replacement is a U1 12 V ~200–400 CCA sealed/AGM that explicitly lists fitment for ZT, ZT X,
  ZT XL, ZT HD 52, and Pro-Turn Z.
  Sources: https://www.gravely.com/en-us/part/zero-turn-12-volt-battery-04738800 ·
  https://www.homedepot.com/p/MIGHTY-MAX-BATTERY-ML-U1-12-Volt-200CCA-Battery-for-Gravely-ZT-XL-52-Lawn-Tractor-Mower-MAX3879686/325635759
- **Electric PTO clutch: YES** on ZT X / ZT XL / ZT HD (Warner electric clutch/brake, 12 V).
  This is the deck-engage solenoid your design relay-switches. ZT HD replacement clutch listings
  confirm "12-Volt Maintenance Free Electric PTO Clutch/Brake."
  Source: https://www.ebay.com/itm/375682924377 (Electric PTO Clutch for Gravely ZT 52HD)

### MUST-MEASURE / CONFIRM ON MACHINE
- PTO clutch current draw (typ. ~3–5 A inrush, then ~3 A hold for Warner units) — **measure** if
  sizing the relay/MOSFET; not published per-model.

---

## VERIFIED vs MUST-MEASURE — quick index

**VERIFIED (fetched page):** 52 in deck width on every model ✅ · engine FR691V 23 hp / FX691V
22 hp ✅ · L×W×H + weight + tires + fuel + speed for ZT X / ZT XL / ZT HD ✅ · electric Warner PTO
= YES ✅ · 12 V U1 battery ✅ · return-to-neutral damper bracket exists (sprung return) ✅ · lap
bars are round tubular steel ✅ · seat = 22" high-back w/ isolation (suspension on Pro-Turn) ✅.

**MUST-MEASURE (no published value found):** lap-bar tube OD + wall ·
neutral-to-full lever travel/arc · lap-bar pivot height & location · wheelbase (all models) ·
seat-pan bolt pattern / dimensions · PTO clutch current draw · ZT HD fuel capacity (5 vs 6.5 gal
conflict — resolve by serial) · Pro-Turn 152 L×W×H/weight/PTO/battery (not on fetched spec page).

---

## Source URLs (all fetched or returned in search this session)
- ZT XL 52 (Gravely): https://www.gravely.com/en-us/power-equipment/zero-turn-mowers/zt-xl/zt-xl-52-kawasaki
- ZT XL 52 specs: https://www.allmachines.com/mowers/gravely-zt-xl-52-kawasaki
- ZT X 52 specs: https://www.allmachines.com/mowers/gravely-zt-x-52-kawasaki
- ZT HD 52 specs: https://www.allmachines.com/mowers/gravely-zt-hd-52-kawasaki
- ZT HD 52 owner's manual: https://www.manualslib.com/manual/3232123/Gravely-Zt-Hd-52.html
- Pro-Turn 152: https://aeoutdoorpower.com/products/gravely-pro-turn-152-kawasaki-zero-turn-mower-991129
- Return-to-neutral damper bracket: https://www.gravely.com/en-us/part/gravely-zero-turn-mower-bracket-return-to-neutraldamper-09282900
- Steering adjustment rod: https://www.gravely.com/en-us/part/gravely-zero-turn-mower-rod-steering-adjustment-09235900
- Steering-lever adjustment procedure: https://www.manualslib.com/manual/720659/Gravely-915170-Zt-42-Carb.html?page=28
- RH hand-control lever weldment: https://www.gravely.com/en-us/part/04922400
- 12 V OEM battery: https://www.gravely.com/en-us/part/zero-turn-12-volt-battery-04738800
- U1 battery fitment (ZT XL 52): https://www.homedepot.com/p/MIGHTY-MAX-BATTERY-ML-U1-12-Volt-200CCA-Battery-for-Gravely-ZT-XL-52-Lawn-Tractor-Mower-MAX3879686/325635759
- ZT 52HD electric PTO clutch (12 V): https://www.ebay.com/itm/375682924377
- Parts diagrams (steering controls section — 403 on direct fetch, browse manually): https://jackssmallengines.com/jacks-parts-lookup/manufacturer/gravely/zero-turn-lawn-mowers/zt-hd/991083-030000-034999-zt-52-hd
