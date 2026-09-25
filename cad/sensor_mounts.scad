// SPDX-License-Identifier: MIT
// ============================================================================
//  SENSOR + SCREEN MOUNTS  —  autonomous zero-turn mower retrofit
//  The three BOM items that had no printed home yet. Every interface below is
//  driven by a datasheet number in params.scad and checked by assert() at the
//  bottom of this file (scripts/check.sh evaluates it, so a bad edit fails CI).
//
//  1) OVERHEAD SONAR (JSN-SR04T) — a collar on the 20 mm GPS mast with a raised
//     arm that holds the probe face-UP, outside the Ø120 antenna ground plane and
//     level with the antenna top, so the mast (the tallest point) sees a low
//     branch before it hits it.
//       PRINT_sonar_collar_a()  collar half + riser arm + probe cup
//       PRINT_sonar_collar_b()  plain collar half
//
//  2) DUAL-ANTENNA MOVING BASELINE — a tee on the mast top carries a horizontal
//     20 mm crossbar; an ANN-MB-00 plate caps each end. Replaces gps_top_plate
//     on the dual-RTK build. BASELINE_L = ARP-to-ARP spacing.
//       PRINT_baseline_tee()        mast socket + crossbar through-bore
//       PRINT_baseline_ant_plate()  x2 — Ø96 antenna plate + crossbar end socket
//
//  3) ON-UNIT TOUCHSCREEN HOOD (Raspberry Pi Touch Display 2, 7") — a sun hood
//     that captures the 189.32 x 120.24 display by its border; the window clears
//     the 154.56 x 86.94 active area. Wider than the bed, so it prints as two
//     halves bolted at the seam, held from behind by two braces that also carry
//     the tilt pivot into a U-yoke bolted to the brain-box lid.
//       PRINT_display_hood_l()  PRINT_display_hood_r()
//       PRINT_display_brace()   x2
//       PRINT_display_yoke()    bolt-down tilt yoke (4x M5)
//
//  USER-SUPPLIED: 20 mm OD aluminium tube (crossbar — length echoed below),
//    2x Ø120 x 1.5 aluminium ground-plane discs (dual build; 1 on single),
//    4x M4 x 16 + nuts (antenna ears), M4 x 30 + nyloc (sonar collar, x2),
//    M4 set screws (x4), M3 x 20 + nuts (hood seam, x2), M3 x 8 into heat-set
//    inserts (braces, x8), M5 x 70 + nyloc + washers (tilt pivots, x2),
//    M5 bolts to the brain-box lid (x4).
//
//  PRINT: ASA (UV — these all live in the sun), 4 walls, 40% infill.
//  Hood halves print BACK-DOWN; enable "supports touching build plate" for the
//  front lip. Everything else prints support-free in the orientation shown.
// ============================================================================
include <utils.scad>

MAST_OD    = 20;                      // [BUY] same tube as gps_mast / lidar mast
MAST_BORE  = MAST_OD + CLEAR_FIT;

// teardrop bore along Y, point toward +Z (prints round holes without support)
module teardrop_y(d, l) {
    rotate([90,0,0]) linear_extrude(l, center=true)
        hull() { circle(d=d); r=d/2; polygon([[-r*0.7071, r*0.7071], [r*0.7071, r*0.7071], [0, r*1.4142]]); }
}

// ============================================================================
//  1) OVERHEAD SONAR COLLAR
// ============================================================================
SON_WALL    = 6;
SON_H       = SONAR_COLLAR_H;         // collar height along the mast
SON_EAR     = 12;                     // bolt-ear width
SON_GAP     = 0.8;                    // squeeze gap between halves
SON_OFFSET  = SONAR_OFFSET;           // probe axis from mast axis
CUP_OD      = JSN_FLANGE_D + 8;       // 33
FLANGE_SEAT = 2;                      // flange recess depth
COL_OD      = MAST_OD + 2*SON_WALL;
// Stack-up, z relative to the MAST TOP (single antenna): collar sits 2 mm under the
// gps_top_plate cap socket; the probe face lands level with the antenna top.
SON_COLLAR_TOP = -(GPS_CAP_DEPTH + 2);
ANT_TOP_Z      = GPS_PLATE_TH + ANT_GROUND_PLANE_T + ANT_H;          // 30.0
SON_RISE       = ANT_TOP_Z - SON_COLLAR_TOP;                          // 50.0
SON_FACE_Z     = SON_COLLAR_TOP + SON_RISE;                           // == ANT_TOP_Z

module sonar_collar_block(with_arm=false) {
    difference() {
        union() {
            cylinder(d=COL_OD, h=SON_H);
            for (s=[-1,1]) translate([0, s*(COL_OD/2 + SON_EAR/2 - 3), 0])
                linear_extrude(SON_H) rrect([16, SON_EAR], 3);
            if (with_arm) {
                // arm out along +X, then a riser column up to the cup
                translate([COL_OD/2 - 4, -8, 0]) cube([SON_OFFSET - COL_OD/2 + 4, 16, SON_H*0.6]);
                translate([SON_OFFSET, 0, 0]) cylinder(d=CUP_OD, h=SON_H + SON_RISE);
                // gusset between arm and riser
                translate([SON_OFFSET, 0, 0]) rotate([90,0,0])
                    linear_extrude(8, center=true) polygon([[-CUP_OD/2, SON_H*0.6], [-CUP_OD/2-30, SON_H*0.6], [-CUP_OD/2, SON_H*0.6+30]]);
            }
        }
        // mast bore
        translate([0,0,-EPS]) cylinder(d=MAST_BORE, h=SON_H + 2*EPS);
        // two M4 clamp bolts along X through the ears
        for (s=[-1,1]) translate([0, s*(COL_OD/2 + SON_EAR/2 - 3), SON_H/2])
            rotate([0,90,0]) cylinder(d=M4_CLEAR, h=inf, center=true);
        if (with_arm) {
            // probe bore (vendor mounting hole), full length — cable exits the bottom, also drains
            translate([SON_OFFSET, 0, -EPS]) cylinder(d=JSN_HOLE_D, h=SON_H + SON_RISE + 2*EPS);
            // flange seat at the top so the probe face sits flush, face-up
            translate([SON_OFFSET, 0, SON_H + SON_RISE - FLANGE_SEAT]) cylinder(d=JSN_FLANGE_D + CLEAR_FIT, h=FLANGE_SEAT + EPS);
            // cable-tie slot through the arm
            translate([COL_OD/2 + 14, 0, SON_H*0.3]) cube([4, 30, 6], center=true);
        }
    }
}
// split at x=0: half A (+X) carries the arm
module sonar_half(half="a") {
    g = SON_GAP/2;
    intersection() {
        sonar_collar_block(with_arm = (half=="a"));
        if (half=="a") translate([g, -inf/2, -inf/2]) cube(inf);
        else           translate([-g - inf, -inf/2, -inf/2]) cube(inf);
    }
}

// ============================================================================
//  2) MOVING-BASELINE TEE + ANTENNA PLATES
// ============================================================================
TEE_W     = MAST_OD + 16;             // block X
TEE_L     = 64;                       // block length along the crossbar (Y)
TEE_SOCK  = 30;                       // mast engagement depth
TEE_H     = TEE_SOCK + MAST_OD + 12;  // socket + crossbar bore + roof
BAR_Z     = TEE_SOCK + 4 + MAST_OD/2; // crossbar axis height in the tee

module baseline_tee() {
    difference() {
        translate([0,0,TEE_H/2]) cube([TEE_W, TEE_L, TEE_H], center=true);
        // vertical mast socket from below (blind — mast butts the crossbar web)
        translate([0,0,-EPS]) cylinder(d=MAST_BORE, h=TEE_SOCK + EPS);
        // horizontal crossbar through-bore (teardrop, prints support-free)
        translate([0,0,BAR_Z]) teardrop_y(MAST_BORE, TEE_L + 2);
        // M4 set screws: one into the mast, one down onto the crossbar
        translate([0, 0, TEE_SOCK/2]) rotate([0,90,0]) cylinder(d=M4_TAP, h=TEE_W);
        translate([0, TEE_L/2 - 12, BAR_Z]) cylinder(d=M4_TAP, h=TEE_H);
        // drain
        translate([0, -TEE_L/2 + 12, BAR_Z]) cylinder(d=M4_TAP, h=TEE_H);
    }
}

PL_TH   = GPS_PLATE_TH;               // antenna disc thickness (same as the single plate)
END_OD  = MAST_OD + 10;               // crossbar end-socket OD
END_L   = 34;                         // socket length (tube engages END_L - 3)
END_FLOOR = 3;
BAR_CUT = BASELINE_L + 2*(END_L/2 - END_FLOOR);   // crossbar tube cut length

// Built INSTALLED (disc up at z = END_OD/2, socket below along Y, open toward -Y
// = the tee). The ANN-MB ears sit on X, so the M4 nut traps clear the socket.
module baseline_ant_plate() {
    difference() {
        union() {
            translate([0,0,END_OD/2]) ann_mb_plate(PL_TH);
            rotate([90,0,0]) cylinder(d=END_OD, h=END_L, center=true);
            // web between socket and disc
            translate([0, 0, END_OD/4]) cube([END_OD*0.7, END_L, END_OD/2], center=true);
        }
        // blind crossbar bore, open at -Y, END_FLOOR at +Y; teardrop points -Z (up when printed)
        translate([0, -END_FLOOR/2 - EPS, 0]) mirror([0,0,1]) teardrop_y(MAST_BORE, END_L - END_FLOOR + 2*EPS);
        // M4 set screw from the side into the crossbar
        rotate([0,90,0]) cylinder(d=M4_TAP, h=END_OD);
    }
}

// ============================================================================
//  3) TOUCH DISPLAY 2 SUN HOOD (two halves) + braces + tilt yoke
//  Hood frame in PRINT orientation: z=0 is the BACK plane (on the bed), the
//  display drops in from the back, the lip + visor face up (= forward).
// ============================================================================
HW      = 4;                          // hood wall
PK_L    = TD2_L + 0.8;                // pocket (sliding fit around the display)
PK_W    = TD2_W + 0.8;
PK_D    = TD2_H + 1;                  // pocket depth (back plane -> lip)
LIP     = 2.4;                        // front lip thickness
WIN_L   = TD2_ACTIVE_L + 2*TD2_WINDOW_MARGIN;   // viewing window (160.56)
WIN_W   = TD2_ACTIVE_W + 2*TD2_WINDOW_MARGIN;   //                (92.94)
VISOR   = 35;                         // sun visor depth beyond the lip (top + sides)
HOOD_L  = PK_L + 2*HW;
HOOD_W  = PK_W + 2*HW;
EAR_OUT = 7.5;                        // ears/tabs stick out this far (keeps Y <= 145)
EAR_Y   = HOOD_W/2 + EAR_OUT/2 - 0.5; // centre-line of every seam bolt / insert
BR_X    = 35;                         // brace centre-lines at x = +/-BR_X
BR_W    = 28;                         // brace width
BR_T    = 6;                          // brace thickness
BR_L    = HOOD_W + 2*EAR_OUT;         // brace length (spans tab to tab)
BR_HOLE_DX = 8;                       // insert / screw offsets either side of a brace centre

module hood_full() {
    difference() {
        union() {
            // shell: pocket walls + lip
            linear_extrude(PK_D + LIP) rrect([HOOD_L, HOOD_W], 4);
            // visor: top (+Y) and both sides, open at the bottom so rain + glare escape
            translate([0,0,PK_D + LIP]) linear_extrude(VISOR) difference() {
                rrect([HOOD_L, HOOD_W], 4);
                translate([0, -HW/2]) square([HOOD_L - 2*HW, HOOD_W - HW + EPS], center=true);
            }
            // seam ears at the front (top + bottom walls), bolt along X
            for (s=[-1,1]) translate([0, s*(HOOD_W/2 + EAR_OUT/2 - 1), PK_D + LIP - 6])
                linear_extrude(16) rrect([20, EAR_OUT + 2], 2);
            // brace tabs at the back plane (heat-set inserts), both walls, both halves
            for (x=[-BR_X, BR_X], s=[-1,1]) translate([x, s*(HOOD_W/2 + EAR_OUT/2 - 1), 0])
                linear_extrude(8) rrect([BR_W, EAR_OUT + 2], 2);
        }
        // display pocket (open at the back)
        translate([0,0,-EPS]) linear_extrude(PK_D + EPS) square([PK_L, PK_W], center=true);
        // viewing window through the lip
        translate([0,0,PK_D - EPS]) linear_extrude(LIP + 2*EPS) rrect([WIN_L, WIN_W], 2);
        // seam bolts (M3 along X through both halves' ears)
        for (s=[-1,1]) translate([0, s*EAR_Y, PK_D + LIP + 2])
            rotate([0,90,0]) cylinder(d=M3_CLEAR, h=40, center=true);
        // heat-set pilots in the brace tabs: 2 per tab
        for (x=[-BR_X, BR_X], s=[-1,1], dx=[-BR_HOLE_DX, BR_HOLE_DX])
            translate([x + dx, s*EAR_Y, -EPS]) cylinder(d=HEATSET_M3_D, h=HEATSET_M3_L + 1);
        // cable notch in the bottom wall (DSI ribbon + power exit downward)
        translate([0, -HOOD_W/2, PK_D/2 - EPS]) cube([60, 3*HW, PK_D + EPS], center=true);
    }
}
module hood_half(side="l") {
    g = 0.3;
    intersection() {
        hood_full();
        if (side=="r") translate([g, -inf/2, -inf/2]) cube(inf);
        else           translate([-g - inf, -inf/2, -inf/2]) cube(inf);
    }
}

// brace: flat bar across the back, 2 screws each end, pivot ear on its outer edge
PIV_BACK = 25;                        // pivot axis distance behind the brace
PIV_EAR_T = 6;
module display_brace() {
    difference() {
        union() {
            linear_extrude(BR_T) rrect([BR_W, BR_L], 3);
            // pivot ear on the +X (outer) edge, rising from the bar
            translate([BR_W/2 - PIV_EAR_T, -18, 0]) cube([PIV_EAR_T, 36, BR_T + PIV_BACK]);
            translate([BR_W/2 - PIV_EAR_T, 0, BR_T + PIV_BACK]) rotate([0,90,0]) cylinder(d=36, h=PIV_EAR_T);
        }
        // counterbored M3 through-holes on the tab inserts (slotted +/-1.5 in X for fit-up)
        for (s=[-1,1], dx=[-BR_HOLE_DX, BR_HOLE_DX]) translate([dx, s*EAR_Y, 0])
            hull() for (sx=[-1.5,1.5]) translate([sx,0,0]) screw_hole(h=BR_T, head_h=2.5);
        // FPC relief window — the DSI connector sits behind the display's centre band
        translate([0,0,-EPS]) linear_extrude(BR_T + 2*EPS) rrect([BR_W - 12, 40], 3);
        // pivot bore (M5)
        translate([0, 0, BR_T + PIV_BACK]) rotate([0,90,0]) cylinder(d=M5_CLEAR, h=inf, center=true);
    }
}

// yoke: U-bracket, uprights embrace the two brace ears
YK_IN   = 2*(BR_X + BR_W/2) + 0.6;    // inside width between uprights (98.6)
YK_T    = 6;
YK_H    = 96;
YK_D    = 40;
PIV_Z   = 82;
module display_yoke() {
    difference() {
        union() {
            linear_extrude(YK_T) rrect([YK_IN + 2*YK_T, YK_D], 4);
            for (s=[-1,1]) translate([s*(YK_IN/2 + YK_T/2), 0, 0]) {
                translate([0,0,YK_H/2]) cube([YK_T, YK_D*0.6, YK_H], center=true);
                translate([0,0,PIV_Z]) rotate([0,90,0]) cylinder(d=YK_D*0.6, h=YK_T, center=true);
            }
            // gussets
            for (s=[-1,1]) translate([s*(YK_IN/2 - 6), 0, YK_T]) rotate([90,0,0])
                linear_extrude(6, center=true) polygon([[s*6,0],[s*-14,0],[s*6,20]]);
        }
        // pivot bores
        translate([0,0,PIV_Z]) rotate([0,90,0]) cylinder(d=M5_CLEAR, h=inf, center=true);
        // 4x M5 mounting holes in the base
        for (x=[-30, 30], y=[-11, 11]) translate([x, y, -EPS]) cylinder(d=M5_CLEAR, h=YK_T + 2*EPS);
    }
}

// ============================================================================
//  FIT CHECKS — evaluated on every render/export and by scripts/check.sh
// ============================================================================
BED = PRINT_MAX_X;
// sonar: cup clears the Ø120 ground plane, probe face >= antenna top, and the
// ±37.5° cone clears the antenna body (nearest body point = SON_OFFSET - ANT_L/2).
assert(SON_OFFSET - CUP_OD/2 >= ANT_GROUND_PLANE_D/2 + 5, "sonar cup hits the ground plane");
assert(SON_FACE_Z >= ANT_TOP_Z - EPS, "sonar face below the antenna top");
assert((SON_OFFSET - ANT_L/2) / tan(JSN_HALF_ANGLE) > ANT_TOP_Z - SON_FACE_Z, "antenna inside sonar cone");
// dual build: collar under the tee; cone clears the tee block + crossbar
SON_FACE_Z_DUAL = -(TEE_SOCK + 2) + SON_RISE;
assert((SON_OFFSET - TEE_W/2) / tan(JSN_HALF_ANGLE) > (TEE_H - TEE_SOCK) - SON_FACE_Z_DUAL, "tee inside sonar cone");
// antenna plate: M4 nut traps clear the crossbar socket; ears fit on the disc
assert(ANT_HOLE_PITCH/2 - (M4_NUT_AF/cos(30))/2 > END_OD/2 + 2, "antenna nut trap collides with the socket");
assert(ANT_PLATE_D/2 - ANT_HOLE_PITCH/2 - (M4_NUT_AF/cos(30))/2 >= 8, "antenna holes too close to the rim");
// hood: window shows the whole active area, lip keeps >= 5 mm of bite on the border
assert(WIN_L >= TD2_ACTIVE_L && WIN_W >= TD2_ACTIVE_W, "window crops the active area");
assert((PK_L - WIN_L)/2 >= 5 && (PK_W - WIN_W)/2 >= 5, "lip bite on the display border < 5 mm");
// brace + yoke: pivot ears sit just inside the uprights; hood swings clear of the base
assert(abs((BR_X + BR_W/2) - (YK_IN/2 - 0.3)) < EPS, "brace ears don't meet the yoke uprights");
assert(PIV_Z - YK_T > HOOD_W/2 + EAR_OUT, "hood hits the yoke base");
// every part on the bed
assert(BR_L <= BED && HOOD_W + 2*EAR_OUT <= BED && HOOD_L/2 <= BED, "hood/brace exceeds the bed");
echo(str("SENSOR_MOUNTS  crossbar cut=", BAR_CUT, " mm  window=", WIN_L, "x", WIN_W,
         "  lip bite=", (PK_L - WIN_L)/2, "/", (PK_W - WIN_W)/2,
         "  sonar face z=", SON_FACE_Z, " above mast top (antenna top ", ANT_TOP_Z, "; dual-RTK ", SON_FACE_Z_DUAL,
         ")  hood=", HOOD_L, "x", HOOD_W));

// ============================================================================
//  EXPOSED PRINT PLATES
// ============================================================================
module PRINT_sonar_collar_a()     proxy() sonar_half("a");
module PRINT_sonar_collar_b()     proxy() sonar_half("b");
module PRINT_baseline_tee()       proxy() baseline_tee();
module PRINT_baseline_ant_plate() proxy()                 // disc-down, socket up
    translate([0,0,END_OD/2 + PL_TH]) rotate([180,0,0]) baseline_ant_plate();
module PRINT_display_hood_l()     proxy() translate([HOOD_L/4, 0, 0]) hood_half("l");
module PRINT_display_hood_r()     proxy() translate([-HOOD_L/4, 0, 0]) hood_half("r");
module PRINT_display_brace()      proxy() display_brace();
module PRINT_display_yoke()       proxy() display_yoke();

// ============================================================================
//  PREVIEW  —  every printed piece laid out
// ============================================================================
if (is_undef(PREVIEW_OFF)) {
    translate([-120, 120, 0]) PRINT_sonar_collar_a();
    translate([-180, 120, 0]) PRINT_sonar_collar_b();
    translate([  20, 120, 0]) PRINT_baseline_tee();
    translate([ 110, 120, 0]) PRINT_baseline_ant_plate();
    translate([ 220, 120, 0]) PRINT_baseline_ant_plate();
    translate([-110, -60, 0]) PRINT_display_hood_l();
    translate([   0, -60, 0]) PRINT_display_hood_r();
    translate([ 100, -60, 0]) PRINT_display_brace();
    translate([ 150, -60, 0]) PRINT_display_brace();
    translate([ 260, -60, 0]) PRINT_display_yoke();
}
