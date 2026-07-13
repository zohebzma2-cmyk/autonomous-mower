// SPDX-License-Identifier: MIT
// ============================================================================
//  AUTONOMOUS ZERO-TURN RETROFIT  —  MASTER PARAMETER FILE
//  Everything is driven from here. To adapt this kit from the reference
//  Gravely ZT 52" to ANY other zero-turn (Toro, Bad Boy, Spartan, Ferris,
//  Scag, etc.), measure your machine and change the numbers in SECTION 1.
//  Units: millimetres (mm). Angles: degrees.
// ============================================================================

// ---- GLOBAL PRINT CONSTRAINT -----------------------------------------------
// FlashForge Adventurer 3 build volume = 150 x 150 x 150 mm.
// We design to a SAFE envelope (margin for warp/skirt/first-layer).
PRINT_MAX_X = 145;
PRINT_MAX_Y = 145;
PRINT_MAX_Z = 145;
PRINT_MARGIN = 5;     // keep parts this far inside the bed edge

// Quality / facets. Bump $fn up for final STL export, keep low for fast preview.
$fn = $preview ? 48 : 120;

// ============================================================================
//  SECTION 1 — MACHINE-SPECIFIC ("ANY ZTR") MEASUREMENTS
//  >>> THESE ARE THE ONLY NUMBERS YOU MUST RE-MEASURE PER MACHINE <<<
//  CONFIRMED machine: Gravely ZT X 52, ~2021, KOHLER engine (model 915256/918010-class).
//    PTO = ELECTRIC clutch (Ogura GT, 12V, relay-switched) -> our design is correct.
//    24 hp Kohler 7000 Pro Twin (725cc); Hydro-Gear EZT / ZT-2200 transaxles; 7 mph fwd.
//    deck 52"=1321mm 11-ga fabricated; rear 20x10-8 (508mm); front 11x6-5 (279mm);
//    weight 615 lb; overall (KOHLER model 915256) L 77.5"/1968 · W 63.4"/1610 · H 40.9"/1039.
//    (the 695 lb / 74.5x55.6 numbers belong to the Kawasaki 918011 variant — NOT this machine.)
//    lap bars = ROUND tubular steel; return-to-neutral is SPRING/DAMPER loaded
//    -> actuator must overcome a centering force (the 169-lbf unit is ample).
//  *** ZT X has NO factory ROPS *** -> the GPS mast cannot clamp a roll-bar post;
//      mount it to the seat-frame upright or a fabricated post (see gps_mast.scad).
//  Lap-bar tube OD is NOT published -> MIC it. Serial plate (under seat): ZT X = 915xxx / 918011-class.
// ============================================================================

// --- Lap bars (the twin steering levers) ---
// VERIFIED round steel (not oval). OD NOT published (confirmed via Gravely IPL) -> MIC IT.
// Realistic range 25-32mm (1.0-1.25"); design the clamp band adjustable. Handle part #s:
// 05107153 (LH) / 05107053 (RH) "HANDLE, STEERING" for model 915256.
LAP_BAR_TUBE_OD      = 25.4;   // [MEASURE] 1.00" round nominal; verified round
LAP_BAR_IS_OVAL      = false;  // VERIFIED round on Gravely; true only on other ZTRs
LAP_BAR_OVAL_W       = 31.8;   // [MEASURE] oval major axis (if oval)
LAP_BAR_OVAL_H       = 19.0;   // [MEASURE] oval minor axis (if oval)

// Lateral spacing between the two lap-bar tubes at the clamp point (centre-centre)
LAP_BAR_SPACING      = 560;    // [MEASURE]

// Lever throw: linear distance the clamp point travels from full-reverse to
// full-forward (arc flattened to the chord the actuator pushes). Drives stroke.
LAP_BAR_TRAVEL       = 90;     // [MEASURE] typical 70-110 mm

// Height of the clamp point above the frame rail the actuator anchors to.
LAP_BAR_CLAMP_HEIGHT = 230;    // [MEASURE]

// --- Frame anchor rail (where the actuator's fixed end bolts down) ---
FRAME_TUBE_W         = 50.8;   // [MEASURE] 2" square tube nominal
FRAME_TUBE_H         = 50.8;   // [MEASURE]
FRAME_TUBE_WALL      = 3.0;    // [MEASURE] used only for bolt length notes

// --- Seat (the brain box straddles / sits on the seat pan) ---
SEAT_WIDTH           = 480;    // [MEASURE] usable flat width
SEAT_DEPTH           = 430;    // [MEASURE] usable flat depth

// --- PTO / blade clutch wire & throttle lever (for relay + servo brackets) ---
THROTTLE_LEVER_OD    = 8.0;    // [MEASURE] throttle rod/lever diameter
THROTTLE_LEVER_TRAVEL= 45;     // [MEASURE] idle->full lever travel

// ============================================================================
//  SECTION 2 — OFF-THE-SHELF COMPONENT DIMENSIONS
//  Datasheet-nominal. VERIFY against the exact part you receive; tolerances
//  and clone variants differ. Marked [DS]=datasheet  [V]=verify-on-arrival.
// ============================================================================

// --- Raspberry Pi 5 (companion computer: vision + LiDAR) [DS] ---
PI5_L = 85; PI5_W = 56; PI5_H_PCB = 1.6;
PI5_HOLE_DX = 58;  PI5_HOLE_DY = 49;     // mounting-hole rectangle
PI5_HOLE_INSET = 3.5;                    // hole centre from board edge
PI5_HOLE_D = 2.7;                        // M2.5 clearance
PI5_STANDOFF = 6;                        // PCB sits this high off the tray

// --- Hailo-8L AI Kit (M.2 HAT+ stacked on the Pi) [DS] ---
// Stacks on Pi via 16mm standoffs; same footprint, extra height budget.
HAILO_STACK_H = 16;                      // extra clearance above Pi for the hat

// --- Flight controller (Holybro Pixhawk 6C) — confirmed 84.8x44x12.4 [V->DS] ---
FC_L = 84.8; FC_W = 44; FC_H = 12.4;     // confirmed via Holybro docs
FC_HOLE_DX = 76; FC_HOLE_DY = 36;        // [V] varies by board; slots cover it
FC_HOLE_D = 3.2;                         // M3 clearance

// --- ArduSimple simpleRTK2B (Arduino-Uno footprint) — EXACT from PCB drawing ---
RTK_L = 68.58; RTK_W = 53.34; RTK_H = 12; // official PCB drawing (was rounded 69x53)
RTK_HOLE_D = 3.2;                         // 3x M3 on Arduino-Uno pattern; SMA + 2x microUSB on short edges

// --- GPS antenna puck (survey/helical, center-bolt mount) [V] ---
// ★ Dual-antenna moving-baseline heading: print 2x gps_mast and mount the two antennas on
//   a baseline >= 0.5 m apart (e.g. front-centre + rear-centre), both clear of metal.
GPS_ANT_DIA = 60; GPS_ANT_H = 22; GPS_ANT_BOLT = 6.4;  // 1/4"-20 center stud

// --- RPLidar A1M8 (2D 360 scanner) — EXACT from Slamtec LD108 datasheet (Fig 5-2) ---
// Base is a TEARDROP, not a circle: footprint 96.74 (L) x 70.28 (W) mm; turret Ø70.04;
// height 51; Ø32 centring boss underneath (use it to register the plate). Cable exits
// at the pointed (motor) tip. MOUNT = 4 x Ø3.4 holes in a trapezoid about the long axis:
//   top pair 56 apart, bottom pair 40 apart, 70 between the two rows.
LIDAR_L = 96.74; LIDAR_W = 70.28; LIDAR_H = 51;
LIDAR_TURRET_DIA = 70.04; LIDAR_BOSS_DIA = 32;
LIDAR_HOLE_D = 3.4;
LIDAR_HOLE_TOP = 56;   // top pair spacing (mm)
LIDAR_HOLE_BOT = 40;   // bottom pair spacing
LIDAR_HOLE_ROW = 70;   // row-to-row distance
LIDAR_DIA = 96.74; LIDAR_HOLE_N = 4;   // legacy aliases (plate sized to the long axis)

// --- Pi Camera Module 3 — EXACT from official mech drawing ---
CAM_L = 25; CAM_W = 24; CAM_H = 11.5;   // standard Z=11.5 (wide=12.4); lens barrel Ø5.75 std / 6.95 wide
CAM_HOLE_DX = 21; CAM_HOLE_DY = 14.5; CAM_HOLE_D = 2.2;  // vert pitch 14.5 (the "12.5" is optical half-width)

// --- DC-DC buck converter module (qty 2) [V] ---
BUCK_L = 65; BUCK_W = 37; BUCK_H = 24; BUCK_HOLE_D = 3.2; BUCK_HOLE_INSET = 4;

// --- Emergency stop (22mm industrial mushroom, panel mount) [DS] ---
ESTOP_PANEL_HOLE = 22.5;     // standard 22mm device cutout
ESTOP_BEZEL_DIA = 40;

// --- Linear actuator: Progressive Automations PA-14P, 4" (100mm) stroke, feedback ---
//   EXACT from the PA dimensional drawing + downloaded STEP (cad/vendor/PA-14.stp).
//   !! PA-14P is IP54 (splash only), NOT IP66 — for an outdoor mower add a rubber rod
//      boot + shield over the rod/gland, or source a genuinely IP66 actuator. !!
//   Force SKUs (35/50/75/110/150 lb) share ONE body, so these bracket dims hold for any.
ACT_BODY_DIA   = 38.1;  // motor/gearbox section Ø1.50" (barrel tube is Ø29.7)
ACT_STROKE     = 100;   // 4" stroke
ACT_CLEVIS_W   = 12;    // clevis tang slot
ACT_CLEVIS_PIN = 6.35;  // 1/4" clevis pin (eye hole Ø0.25")
ACT_RETRACTED_L= 241.6; // pin-to-pin retracted (4" stroke); extended 343.2

// ============================================================================
//  SECTION 3 — ENCLOSURE (the seat-mounted weatherproof "brain box")
//  Target rating IP65+. Printed shell is a MOUNT/ORGANIZER that lives inside
//  (or replaces the lid of) a sealed ABS/polycarb box; print in ASA/PETG.
// ============================================================================
ENC_WALL        = 3.0;
ENC_FLOOR       = 3.0;
ENC_CLEAR       = 2.0;    // clearance around internal trays
ENC_LID_LIP     = 6;      // tongue that meets the gasket groove
GASKET_GROOVE_W = 3.2;    // for 3mm round cord gasket
GASKET_GROOVE_D = 2.2;
CABLE_GLAND_D   = 16.5;   // PG9 gland hole (common); PG7=12.5, PG11=18.6
CABLE_GLAND_N   = 6;

// Internal footprint is derived from what must fit (Pi+Hailo, FC, RTK, bucks)
// laid out in a row+stack. Computed in enclosure.scad, but cap to print bed:
ENC_MAX_FOOTPRINT = PRINT_MAX_X - PRINT_MARGIN;  // split if exceeded

// ============================================================================
//  SECTION 4 — HARDWARE / FASTENERS
// ============================================================================
M3_CLEAR = 3.4; M3_TAP = 2.5; M3_HEAD = 6.0; M3_NUT_AF = 5.5; M3_NUT_TH = 2.4;
M4_CLEAR = 4.5; M4_TAP = 3.3; M4_HEAD = 7.0; M4_NUT_AF = 7.0; M4_NUT_TH = 3.2;
M5_CLEAR = 5.5; M5_TAP = 4.2; M5_NUT_AF = 8.0; M5_NUT_TH = 4.0;
HEATSET_M3_D = 4.2;  HEATSET_M3_L = 5.0;   // brass heat-set insert pilot
HEATSET_M4_D = 5.6;  HEATSET_M4_L = 6.0;

// Generic slop/fit
SLOP = 0.2;          // press fit
CLEAR_FIT = 0.4;     // sliding fit

// ============================================================================
//  SECTION 5 — SPLIT-FOR-BED HELPER FLAGS
//  Large parts expose a SPLIT flag so they print in bed-sized pieces that
//  bolt together with dovetail + M4 through-bolts.
// ============================================================================
SPLIT_DOVETAIL_W = 14;
SPLIT_DOVETAIL_H = 8;
SPLIT_BOLT_D = M4_CLEAR;

// ---- end params ----
