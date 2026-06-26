# CAD-Precision Research — Actuation, Safety & Power Components

Mower retrofit. Goal: exact mm dimensions + mounting + downloadable CAD so OpenSCAD brackets are exact.
Compiled 2026-06-26. Rule: **never guess** — values not published are marked `UNPUBLISHED — MEASURE`.
Inch→mm conversions are exact (×25.4) and labelled. Downloaded CAD lives in `cad/vendor/`.

---

## TL;DR — the two bracket-driving numbers

1. **Actuator clevis/pin (PA-14P):** both ends are an eye/clevis with a **Ø0.25 in = 6.35 mm mounting hole** → use a **1/4 in (6.35 mm) clevis pin**. Retracted **pin-to-pin = 9.51 in = 241.6 mm**, extended **= 13.51 in = 343.2 mm** (4″ stroke). Motor/gearbox round section **Ø1.50 in = 38.1 mm**; barrel tube **Ø1.17 in = 29.7 mm**; end-bracket overall width **1.57 in = 39.9 mm**. **All from the manufacturer dimensional drawing** (datasheet p.4) and a downloaded STEP — bracket pin bores can be cut to exact mm.
   ⚠️ **"169 lbs" is NOT a PA-14P rating.** PA-14P 4″ comes in 35/50/75/110/150 lbs only. Force options share one body, so brackets are unaffected — but confirm the actual part (150 lb PA-14P is the closest real SKU; 169 lb ≈ 750 N points to a different/generic actuator).

2. **Enclosure internal dims (XINYIELE 221×170×114 outer):** the exact internal cavity + mounting-boss numbers are **UNPUBLISHED by every vendor of this mold (QILIPSU/YETLEBOX/Gratury/Otdorpatio = same part); only a non-dimensioned photo is shown.** Best-anchored estimate (from Saipwell's own family + the included-plate ratio): **mounting plate ≈ 204 × 154 mm**, internal cavity ≈ **208–211 × 158–161 × ~100 mm**. **MEASURE before committing the equipment plate.** Construction confirmed from product photos: 4 corner threaded brass bosses (lid screws) + a gridded mounting plate raised on standoff posts, secured by 2 center screws.

---

## 1. Progressive Automations PA-14P linear actuator (4″/100 mm stroke, 12 V, potentiometer feedback)

**Exact model:** **PA-14P** (the "P" = potentiometer-feedback variant of the PA-14 Mini). This is the correct match for "4″ stroke, 12 V, pot feedback." `Source:` https://www.progressiveautomations.com/products/linear-actuator-with-potentiometer and datasheet V1.03 https://f.hubspotusercontent40.net/hubfs/7717445/PDFs/Actuator%20datasheets/PA-14P%20datasheet.pdf

### Force / electrical (datasheet p.3)
| Spec | Value |
|---|---|
| Force options (Dynamic = Static) | **35 / 50 / 75 / 110 / 150 lbs** — *no 169 lb option* |
| 4″ @ 150 lb: speed | 0.37 in/s no-load, **0.28 in/s** full-load |
| Current @ 12 V | 1.0 A no-load → **5.0 A** full-load |
| Voltage | 12 VDC (24/36/48 also offered) |
| Duty cycle | **25 %** (5 min on / 15 min off) |
| Screw / motor | ACME screw, brushed DC |
| Housing | 6062 aluminum |
| **IP rating** | **IP54 standard** (IP65 customizable) — *datasheet p.3; note an earlier web blurb said IP65, datasheet is authoritative* |
| Limit switches | internal, non-adjustable |

### Mechanical dimensions — from the datasheet dimensional drawing (p.4), all inch values are on the drawing; mm = ×25.4
| Dimension | inch | **mm** | Notes |
|---|---|---|---|
| **Retracted pin-to-pin** (A), 4″ stroke | 9.51 | **241.6** | A = stroke + 5.51″ |
| **Extended pin-to-pin** (B), 4″ stroke | 13.51 | **343.2** | B = stroke×2 + 5.51″ |
| Added length per stroke inch | — | — | A = L+5.51″, B = 2L+5.51″ |
| **Mounting hole Ø, both ends** (clevis/eye pin) | 0.25 | **6.35** | → **1/4″ clevis pin**; confirmed by spec text "0.25″ mounting holes" |
| Motor/gearbox round section Ø | 1.50 | **38.10** | the wide cylindrical drive section |
| Barrel / main tube Ø | 1.17 | **29.72** | extending-tube housing barrel |
| End bracket (clevis) overall width | 1.57 | **39.88** | eye-tab block width at each end |
| Eye boss radius (around hole) | R0.59 | **15.0** | rounded clevis/eye tab |
| Hole-center vertical offset (eye) | 0.81 / 0.59 | 20.6 / 15.0 | from drawing end-views |
| Motor+gearbox body length (retracted) | 3.49 | **88.65** | |
| Retracted overall body block | 5.16 | **131.06** | excludes extended rod |
| Drive section length callouts | 2.58 / 1.40 | 65.5 / 35.6 | |

> The clevis at **each end** is a flat eye/blade with a **Ø6.35 mm** through-hole. Design bracket pin bores to **6.35 mm (+ clearance)** and a **1/4″ pin**; the tab is ~**39.9 mm** wide. For exact eye geometry, pull it straight from the downloaded STEP (the drawing dimensions the holes but not every fillet).

### Feedback wiring (datasheet p.6) — 6-pin Molex Mini-Fit Jr (housing PN 39012060, mating 39013063)
| Pin | Function | Wire color |
|---|---|---|
| 1 | Potentiometer +5 VDC | **Yellow** |
| 2 | Potentiometer GND | **White** |
| 3 | Unused | — |
| 4 | Potentiometer wiper / signal | **Blue** |
| 5 | Motor + | **Black** |
| 6 | Motor − | **Red** |

Pot: **0–10 kΩ, 10-turn, ±5 %** (voltage-divider: +5 V — wiper(signal) — GND).

### CAD — DOWNLOADED (free, no login)
Progressive Automations publishes 3D files directly on its Resources page (https://www.progressiveautomations.com/pages/resources):
- `cad/vendor/PA-14.stp` — **STEP AP214, ISO-10303-21, units = INCHES.** Header = `PA-14-6.STEP` (SolidWorks 2017) → this is the **6″-stroke** body; cross-section + both clevis ends are identical to the 4″, only the barrel length differs (scale per A/B formula). Direct: https://cdn.shopify.com/s/files/1/0061/7735/7891/files/PA-14.stp
- `cad/vendor/PA-14P.SLDPRT` — SolidWorks native part (PA-14**P**). https://cdn.shopify.com/s/files/1/0061/7735/7891/files/PA-14P.SLDPRT
- `cad/vendor/PA-14.DWG` — 2D AutoCAD. https://cdn.shopify.com/s/files/1/0061/7735/7891/files/PA-14.DWG
- **License:** vendor-provided for design integration, no login, no explicit open-source license stated.
- **OpenSCAD:** STEP not natively importable — convert `PA-14.stp`→STL in FreeCAD, or cut brackets straight from the mm table above (the pin bore + tab width are the only critical features).

---

## 2. BTS7960 / IBT-2 dual H-bridge module

Best source = Handsontec dimensional drawing (p.2): https://www.handsontec.com/dataspecs/module/BTS7960%20Motor%20Driver.pdf

| Spec | Value | Source |
|---|---|---|
| PCB L × W | **49.66 × 49.40 mm** (nominal 50 × 50) | Handsontec drawing p.2 |
| **Mounting holes** | **4 corner holes on a 40.0 × 40.0 mm rectangle** (center-to-center, both axes) | Handsontec drawing |
| Hole Ø | `UNPUBLISHED — MEASURE` (vendors: "4× M3" → ~Ø3.2 bore, inferred) | listings |
| Total height incl. heatsink | **43 mm** (finned heatsink hangs *below* PCB; cap + terminals above) | Handsontec |
| PCB thickness | `UNPUBLISHED — MEASURE` (~1.6 mm FR4 typ.) | — |
| Connectors | 4-pos screw terminal **5.08 mm pitch** (B+/B-/M+/M-) one edge; 2×4 **2.54 mm** header (8 logic pins) opposite | Handsontec |

**Bracket guidance:** 40.0 × 40.0 mm 4-hole grid, 50 × 50 envelope, ≥43 mm vertical clearance (heatsink below plane), verify screw bore on the physical board.
**CAD:** community STEP on GrabCAD (`grabcad.com/library/tag/bts7960`) — free but login-gated, GrabCAD community terms. Infineon ships a verified 3D for the **BTS7960B chip** (not the module) at SnapEDA: https://www.snapeda.com/parts/BTS7960B/Infineon/view-part/

---

## 3. 22 mm latching mushroom E-stop (red plastic, 1NC, IP65)

Dimensional standard = IEC 60947-5-1 / Schneider Harmony XB2-ZB2 format that the cheap clones copy.

| Spec | Value | Source |
|---|---|---|
| **Panel cutout Ø** | **22.5 mm (+0.4 / −0.0)** — *your 22.5 confirmed* | Schneider XB2/ZB2 drawing |
| Mushroom head OD | **40 mm** (1.57″) | Schneider XB2/ZB2 |
| Max panel thickness clamped | **1–6 mm** | Schneider mounting spec |
| Min spacing to next 22 mm device | **30 mm** c-c | Schneider |
| Mounting collar | M22×1 thread (plastic types) / Ø~21.8–22 bushing | generic plastic |
| Behind-panel depth | `UNPUBLISHED — MEASURE` (~50–64 mm with 1NC block; overall body ~70–73 mm) | vendor, approx |
| Contact block L×W×H | `UNPUBLISHED — MEASURE` (~30 H × ~18–20 W × ~30 D mm) | vendor, approx |

**Bracket guidance:** cut panel hole **Ø22.5 mm**, allow 1–6 mm panel clamp, head boss 40 mm. Measure your unit's behind-panel depth + block.
**CAD:** GrabCAD `22mm emergency stop` (login, community terms). No manufacturer STEP for the generic plastic part.
`Sources:` https://www.artisantg.com/info/Schneider_Electric_Telemecanique_ZB2_BE102_Datasheet_2016222131837.pdf · https://www.se.com/us/en/product/ZB4BS844/

---

## 4. ANNIMOS / DSSERVO DS3225 (25 kg standard servo, 25T)

Body/IP/gearing from official datasheet; tab pattern + spline are shown only as an **un-dimensioned image** → flagged.
Datasheet: http://myosuploads3.banggood.com/products/20220907/20220907032153DS3225datasheet.pdf

| Spec | Value | Source |
|---|---|---|
| **Body L × W × H (no tabs)** | **40 × 20 × 40.5 mm** | Official DS3225 datasheet |
| Weight | 60 g (some vendors 67 g) | datasheet |
| Gearing / bearing / IP | 275:1, double bearing, **IP66** | datasheet |
| Total length incl. tabs | `UNPUBLISHED — MEASURE` (std-servo ≈ 54 mm) | convention |
| **Mounting-hole spacing, long axis** | `UNPUBLISHED — MEASURE` (std ≈ 49.5 mm c-c) | convention |
| Mounting-hole spacing, short axis | `UNPUBLISHED — MEASURE` (std ≈ 10 mm c-c) | convention |
| Mounting-tab hole Ø | `UNPUBLISHED — MEASURE` (std ≈ 4.6 mm, takes M3 + grommet) | convention |
| Tab thickness | `UNPUBLISHED — MEASURE` (std ≈ 2.5–3 mm) | convention |
| **Output spline** | **25T (25-tooth), Futaba-3F style** — confirmed (ships 25T arm) | datasheet pkg list |
| Spline Ø | ~**5.92 mm** major Ø (Futaba 25T) — *your 5.92 matches* | spline-standard refs |

**25T horn:** not dimensioned by DS3225; aftermarket 25T metal single-arm horns run ~24–35 mm arm length, hub Ø ~8–9 mm, M3 holes — pick the specific horn and use its listing.
Reference standard-size body w/ dimensioned tabs: Hitec HS-645MG 40.6 × 19.8 × 37.8 mm (https://media.digikey.com/pdf/Data%20Sheets/Hi-Tech/HS-645MG.pdf) — same screw pattern.
**CAD:** GrabCAD DS3225 / DS3225MG (STEP/STL, login, community terms); Cults3D printable STL.

---

## 5. LM2596 DC-DC buck module (12→5 V)

| Spec | Value | Source |
|---|---|---|
| PCB L × W | **43 (–43.2) × 21 mm** | ProtoSupplies / Addicore |
| Height | **13–14 mm** (over trimmer) | same |
| Mounting holes | **2 holes, diagonally opposite corners**, fit M3 | vendor |
| Hole spacing / Ø / inset | `UNPUBLISHED — MEASURE` | — |

⚠️ **5 A flag:** the **LM2596 IC is 3 A max** (TI/onsemi). There is **no genuine 5 A LM2596 module**. A board sold as "12→5 V 5 A buck" is almost always **XL4015** (real 5 A) — *different, larger footprint ~52 × 27 mm with its own holes.* **Verify the chip marking; do NOT design the bracket to the 43×21 LM2596 outline if the real part is an XL4015.** (LM2596**HV** = higher input V, NOT higher current.)
`Sources:` https://protosupplies.com/product/lm2596s-adjustable-dc-dc-step-down-module/ · https://www.ti.com/lit/ds/symlink/lm2596.pdf
**CAD:** GrabCAD / 3DContentCentral LM2596 module STEP (login, community terms).

---

## 6. Snlazp 12-circuit fuse block (ATC/ATO, neg bus, cover)

Identical clone family (JOYHO/SOYOND/Nilight) → factory = DAIER FB-1714.

| Spec | Value | Source |
|---|---|---|
| Footprint L × W | **140 × 85 mm** (5.512 × 3.346 in); some clones 138.2 × 85 | Snlazp listing / Nilight |
| Height incl. cover | **36 mm** (one clone 36.5) | listing |
| Mounting holes | 4 corner ears (ships 4 screws) | images |
| **Hole Ø + c-c spacing** | `UNPUBLISHED — MEASURE` (no vendor publishes it) | — |
| Main / + input stud | **M5** (DAIER spec) — *some resellers claim M6, verify* | DAIER |
| Ground / neg-bus studs | **M4** | DAIER |
| Wire gauge | #4–6 AWG main, #12–16 AWG branch | DAIER |
| Rating | 30 A/circuit, 100 A total | all listings |

**Bracket guidance:** use **slotted** mounting holes — ~2 mm length variance (138–140) + unpublished hole spacing between batches. **No CAD published** (only a raster drawing on DAIER's page).
`Sources:` https://amazon.com/Snlazp-Waterproof-Indicator-Damp-Proof-Circuits/dp/B0CP7NLFVD · https://www.daierswitches.com/products/12-way-12v-24v-atc-ato-blade-fuse-block-holder-with-led-indicator

---

## 7. XINYIELE IP67 enclosure 8.7×6.7×4.5″ (221×170×114 mm OUTER) — **CRITICAL for the equipment plate**

This is the ubiquitous "220×170×110" ABS IP67 box with hinged clear lid + stainless latch. **XINYIELE / QILIPSU / YETLEBOX / Gratury / Otdorpatio / Zulkit = the same mold** (QILIPSU = manufacturer YUEQING QILI). The 114 vs 110 / 221 vs 220 is the clear-lid + latch.

| Spec | Value | Source / confidence |
|---|---|---|
| **OUTER L × W × H** | **221 × 170 × 114 mm** (user) ≈ the 220 × 170 × 110 family | listings, confirmed |
| **INTERNAL cavity (usable)** | **`UNPUBLISHED — MEASURE`.** Best estimate **≈ 208–211 × 158–161 × ~100 mm** | *derived, not published — see below* |
| **Included mounting plate** | **`UNPUBLISHED — MEASURE`.** Best estimate **≈ 204 × 154 × ~2 mm** | *derived from Saipwell family ratio* |
| Internal mounting-boss pattern | **4 corner threaded brass bosses** (lid screws) + plate sits on **raised standoff posts**, secured by **2 center screws** | confirmed from QILIPSU product photos |
| Plate-to-floor offset | `UNPUBLISHED — MEASURE` (plate is raised a few mm on standoffs, gridded) | photos |

**Why no exact numbers:** every vendor of this exact mold shows only a non-dimensioned photo/render; QILIPSU's and Saipwell's published size **tables do not carry the 220×170×110 row** (Saipwell DS-AG / SP-CAG jump from 200×200 to 250×170). No fetchable dimensioned drawing or CAD exists for this box.

**How the estimate was anchored (so you can sanity-check your measurement):**
- Saipwell **DS-AG-2020-S**: external **200×200×95** → mounting plate **184×184×2** ⇒ plate = external − 16 mm in-plane. Apply to 220×170 ⇒ **≈ 204 × 154 mm plate.**
- uxcell **200×150×100** → internal **192×141×96** (wall ~4 mm/side, depth −4). Apply to 220×170×110 ⇒ internal **≈ 211 × 161 × 106** (uxcell mold; this box's clear lid eats more depth → use ~100).
- LeMotech **125×125×75** → internal **119×119×54** (clear-lid depth loss is large) — corroborates trimming interior depth to ~100 mm.

> **ACTION:** print the equipment plate to a conservative **≤ 200 × 150 mm** footprint and **measure the actual box** (internal L/W/depth, the 4 corner-boss positions, and the 2 center standoff screw spacing) before finalizing. The included gridded plate is the safest datum — copy its hole pattern, or mount your printed plate to the same 2 center standoffs.

`Sources:` https://www.amazon.com/YETLEBOX-Waterproof-Electrical-220x170x110mm-Electronics/dp/B09N7LB65M · https://qilipsu.com/product-183.html (mold photos) · https://www.saipwell.com/waterproof-electrical-junction-box/ (DS-AG plate ratio) · https://www.amazon.com/uxcell-200mmx150mmx100mm-Junction-Universal-Enclosure/dp/B07BFBX6QN (wall-thickness anchor)

---

## CAD download status summary

| # | Part | CAD obtained | File |
|---|------|--------------|------|
| 1 | PA-14P actuator | **YES — free, no login** | `cad/vendor/PA-14.stp` (STEP, in), `PA-14P.SLDPRT`, `PA-14.DWG` |
| 2 | BTS7960/IBT-2 | login-gated (GrabCAD) | — |
| 3 | 22 mm E-stop | login-gated (GrabCAD) | — |
| 4 | DS3225 servo | login-gated (GrabCAD/Cults3D) | — |
| 5 | LM2596 buck | login-gated (GrabCAD) | — |
| 6 | Snlazp fuse block | **none exists** (raster only) | — |
| 7 | XINYIELE enclosure | **none exists** | — |

Only the actuator has a freely-fetchable manufacturer CAD; everything else is either community-CAD behind a free login, or no CAD at all → dimensions above + measurement.
