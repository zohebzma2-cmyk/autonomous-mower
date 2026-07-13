// SPDX-License-Identifier: MIT
// ============================================================================
//  RPLidar A1M8 FRONT MAST MOUNT  —  autonomous zero-turn mower retrofit
//  ----------------------------------------------------------------------------
//  Puts a 2D 360° scanner up on a short, stiff mast at the FRONT of the mower,
//  clamped to the front cross member (50.8 mm square tube). The mast is a
//  printed triangular truss (rigid + light, vibration-resistant for clean
//  scans) SPLIT into two bed-sized sections that bolt together. The lidar
//  bolts to a top plate via its 3-hole bolt circle; a clear dome can be added
//  later (lidar is NOT weatherproof).
//
//  >>> RECOMMENDED SCAN-PLANE HEIGHT: ~250 mm above the frame cross member <<<
//      That clears the mower deck / front bumper so the beam sees obstacles,
//      not its own machine. The default mast (clamp + 2x100 mm truss + plate)
//      lands the lidar's scan plane ~255 mm above the frame top. Drop one
//      truss bay (MAST_BAYS) or trim MAST_SEC_H to fine-tune for YOUR deck.
//
//  PIECES (all fit the 150x150x150 bed, <145 mm/axis):
//    PRINT_lidar_base_a()      bottom clamp half (grips square tube)
//    PRINT_lidar_base_b()      top clamp half + mast mounting platform
//    PRINT_lidar_mast_lower()  lower truss section (bolts to clamp + upper)
//    PRINT_lidar_mast_upper()  upper truss section (bolts to lower + plate)
//    PRINT_lidar_top_plate()   lidar plate (3 mount holes + cable hole + dome)
//
//  PRINT: ASA or PETG, 4+ walls. Truss sections stand flange-down on the bed;
//  light tree support under the horizontal ring struts. Mast joins use M4
//  bolts + nuts; lidar uses M3 into tapped plate holes; clamp uses M5.
// ============================================================================
include <utils.scad>

// ---- Frame interface -------------------------------------------------------
RAIL      = FRAME_TUBE_W;          // 50.8 mm square front cross member [param]
CW        = ENC_WALL;              // clamp wall thickness around the tube
CL        = 60;                    // clamp length along the tube axis (X)
LUG       = 16;                    // M5 bolt-lug width (each side of the tube)

// ---- Mast (triangular truss) -----------------------------------------------
MAST_R    = 30;                    // truss leg circumradius (triangle "size")
LEG_D     = 7;                     // vertical leg strut diameter
BR_D      = 5;                     // ring + diagonal brace diameter
MAST_BAYS = 3;                     // truss bays per section
MAST_SEC_H= 100;                   // truss height per section (x2 sections)
FL        = 82;                    // square flange plate side
FT        = 6;                     // flange plate thickness

// ---- Bolt patterns (square, driven through hole_grid) -----------------------
P_BASE    = 40;                    // clamp-platform  <-> lower-mast flange (M4)
P_JOINT   = 50;                    // mast<->mast joint AND upper-mast<->plate (M4)

// ---- Clamp platform (top of base_b) ----------------------------------------
PLAT      = 64;                    // platform plate side
PT        = 6;                     // platform plate thickness
CABLE_D   = 12;                    // central cable pass-through

// ---- Top plate -------------------------------------------------------------
TOP_D     = LIDAR_DIA + 27;        // ~97.6 mm disk, a bit larger than the lidar
TP        = 6;                     // plate thickness
DOME_PCD  = 88;                    // 3x M3 bosses for a future clear dome
DOME_BOSS_D = 8;
DOME_BOSS_H = 8;

// ============================================================================
//  Low-level helpers
// ============================================================================

// A round strut between two 3D points (hull of two low-poly spheres).
module strut(a, b, d = BR_D) {
    hull() {
        translate(a) sphere(d/2, $fn = 16);
        translate(b) sphere(d/2, $fn = 16);
    }
}

// Square flange plate with a square bolt pattern; optional center cable hole.
module flange(side = FL, pattern = P_JOINT, hole_d = M4_CLEAR, th = FT,
              center_hole = false) {
    difference() {
        linear_extrude(th) rrect([side, side], 6);
        hole_grid(pattern, pattern)
            translate([0, 0, -EPS]) cylinder(d = hole_d, h = th + 2*EPS);
        if (center_hole)
            translate([0, 0, -EPS]) cylinder(d = CABLE_D, h = th + 2*EPS);
    }
}

// The open triangular truss, sitting on z=0 and rising to z=H.
module truss(H = MAST_SEC_H) {
    bay = H / MAST_BAYS;
    cor = [for (i = [0:2]) [MAST_R*cos(90 + 120*i), MAST_R*sin(90 + 120*i)]];
    // vertical legs
    for (c = cor) translate([c[0], c[1], 0]) cylinder(d = LEG_D, h = H, $fn = 24);
    // horizontal ring braces at every bay boundary (incl. top + bottom)
    for (j = [0:MAST_BAYS]) for (i = [0:2])
        strut([cor[i][0], cor[i][1], j*bay],
              [cor[(i+1)%3][0], cor[(i+1)%3][1], j*bay]);
    // diagonal braces (one per face per bay) for shear stiffness
    for (j = [0:MAST_BAYS-1]) for (i = [0:2])
        strut([cor[i][0], cor[i][1], j*bay],
              [cor[(i+1)%3][0], cor[(i+1)%3][1], (j+1)*bay]);
}

// One bed-sized mast section: bottom flange + truss + top flange.
module mast_section(bottom_pattern, top_pattern) {
    union() {
        flange(FL, bottom_pattern, M4_CLEAR, FT, center_hole = true);
        translate([0, 0, FT - EPS]) truss(MAST_SEC_H);
        translate([0, 0, FT + MAST_SEC_H - 2*EPS])
            flange(FL, top_pattern, M4_CLEAR, FT, center_hole = true);
    }
}

// ============================================================================
//  BASE CLAMP  —  two-piece split clamp on the 50.8 mm square front rail
//  Tube runs along X. Split is on the horizontal (Z) plane: bottom + top half.
//  M5 bolts run vertically (Z) through lugs on each side of the tube.
// ============================================================================
module base_clamp(half = "bottom") {
    top = (half == "top");
    zc  = RAIL/2 + CW;                 // thickness of each half
    zmid = top ? zc/2 : -zc/2;         // center of this half's block
    body_w = RAIL + 2*CW;              // outer width across the tube (Y)
    lug_y  = RAIL/2 + CW + LUG/2;      // lug center offset in Y

    difference() {
        union() {
            // body wrapping its half of the tube
            translate([0, 0, zmid]) cube([CL, body_w, zc], center = true);
            // bolt lugs on +Y and -Y
            for (s = [-1, 1])
                translate([0, s*lug_y, zmid]) cube([CL, LUG, zc], center = true);
            // top half carries the mast mounting platform
            if (top)
                translate([0, 0, zc]) linear_extrude(PT) rrect([PLAT, PLAT], 5);
        }
        // square tube bore (full square; only this half's portion is removed)
        cube([CL + 2*EPS, RAIL + SLOP, RAIL + SLOP], center = true);
        // vertical M5 clamp bolts through the lugs
        for (s = [-1, 1]) for (x = [-1, 1])
            translate([x*(CL/2 - 9), s*lug_y, 0])
                cylinder(d = M5_CLEAR, h = 4*zc, center = true);
        // mast mounting holes + cable pass-through in the platform
        if (top) translate([0, 0, zc]) {
            hole_grid(P_BASE, P_BASE)
                translate([0, 0, -EPS]) cylinder(d = M4_CLEAR, h = PT + 2*EPS);
            translate([0, 0, -EPS]) cylinder(d = CABLE_D, h = PT + 2*EPS);
        }
    }
}

// ============================================================================
//  TOP PLATE  —  lidar bolts here (3-hole bolt circle), cable hole, dome bosses
//  RAIN NOTE: the RPLidar A1M8 is NOT waterproof. Leave the 3 rim M3 bosses
//  (DOME_PCD) so a printed/clear acrylic dome can cap the unit. Add a small
//  rain-lip by printing the dome with a downward skirt over this plate edge.
// ============================================================================
module top_plate() {
    difference() {
        union() {
            cylinder(d = TOP_D, h = TP);
            // 3 dome-mount bosses around the rim
            translate([0, 0, TP])
                bolt_circle(DOME_PCD, 3) cylinder(d = DOME_BOSS_D, h = DOME_BOSS_H);
        }
        // 4x lidar mount holes — EXACT trapezoid (Slamtec LD108 datasheet): two rows
        // 70mm apart along the long axis; wide-end pair 56mm, narrow-end pair 40mm; Ø3.4.
        for (sy = [-1, 1]) {
            translate([ LIDAR_HOLE_ROW/2, sy*LIDAR_HOLE_TOP/2, -EPS]) cylinder(d=LIDAR_HOLE_D, h=TP+2*EPS);
            translate([-LIDAR_HOLE_ROW/2, sy*LIDAR_HOLE_BOT/2, -EPS]) cylinder(d=LIDAR_HOLE_D, h=TP+2*EPS);
        }
        // central 12 mm cable pass-through
        translate([0, 0, -EPS]) cylinder(d = CABLE_D, h = TP + 2*EPS);
        // 4x mounting holes down to the upper-mast flange (M4 clearance)
        hole_grid(P_JOINT, P_JOINT)
            translate([0, 0, -EPS]) cylinder(d = M4_CLEAR, h = TP + 2*EPS);
        // dome-boss pilot holes — M3 tap
        translate([0, 0, TP])
            bolt_circle(DOME_PCD, 3) cylinder(d = M3_TAP, h = DOME_BOSS_H + EPS);
    }
}

// ============================================================================
//  PRINT PLATES  (each = one printable piece, flat on the bed)
// ============================================================================
module PRINT_lidar_base_a()     proxy() base_clamp("bottom");
module PRINT_lidar_base_b()     proxy() base_clamp("top");
module PRINT_lidar_mast_lower() proxy() mast_section(P_BASE, P_JOINT);
module PRINT_lidar_mast_upper() proxy() mast_section(P_JOINT, P_JOINT);
module PRINT_lidar_top_plate()  proxy() top_plate();

// ============================================================================
//  PREVIEW  —  the five printable pieces laid out side by side on the "bed"
// ============================================================================
if (is_undef(PREVIEW_OFF)) {
    translate([-150, 0, 0])  PRINT_lidar_base_a();
    translate([ -75, 0, 0])  PRINT_lidar_base_b();
    translate([   0, 0, 0])  PRINT_lidar_mast_lower();
    translate([  90, 0, 0])  PRINT_lidar_mast_upper();
    translate([ 190, 0, 0])  PRINT_lidar_top_plate();
}
