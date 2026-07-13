// SPDX-License-Identifier: MIT
// ============================================================================
//  CONTROLS / SAFETY BRACKETS  —  autonomous zero-turn mower retrofit
//  Three independent 3D-printable parts (all fit the 150mm FlashForge bed):
//    1) E-STOP pedestal   — 22mm mushroom button on a reachable, slap-able post
//                           that split-clamps (M5) to the 50.8mm frame tube.
//    2) PTO relay box      — weather-resistant box (gasket groove + glands) for
//                           a standard 5-pin automotive relay + spade blocks.
//    3) Throttle servo bracket — holds a hobby servo so its horn pulls the
//                           engine throttle lever.
//  PRINT: ASA or PETG, 3+ walls. The e-stop & relay box are SAFETY hardware.
// ============================================================================
include <utils.scad>

// ---- Standard off-the-shelf parts (datasheet-nominal) ----------------------
SERVO         = [40.5, 20.0, 38.0];   // body L x W x H (mounting tabs span ~54mm)
SERVO_TAB_DX  = 49;                    // centre-centre of the two tab-hole ends
SERVO_HOLE_D  = M3_CLEAR;              // servo tab screw clearance
RELAY         = [28, 28, 35];          // standard 5-pin automotive relay (L W H)

// ---- Local design constants (new — not redefining params/utils) ------------
CL_WALL   = 5;                         // frame-tube clamp wall thickness
CL_LEN    = 50;                        // clamp length along the tube axis (Y)
CL_BW     = FRAME_TUBE_W + 2*CL_WALL;  // clamp block outer width (X)
CL_EAR    = 16;                        // bolt-ear width each side
POST_H    = 94;                        // pedestal post height (keeps part <145mm bed)
POST_LEAN = 18;                        // post lean angle (toward the operator)

ESTOP_FACE       = [ESTOP_BEZEL_DIA+18, ESTOP_BEZEL_DIA+18]; // panel plate (~58 sq)
ESTOP_FACE_HOLES = ESTOP_BEZEL_DIA+8;  // M4 corner-mount hole spacing (~48)

// ============================================================================
//  1) E-STOP PEDESTAL
//  THE HARDWARE KILL. The red mushroom must be wired so pressing it cuts
//  ACTUATOR power AND drops the PTO/ignition relay (see relay box below) —
//  it is a physical interlock, independent of the companion computer.
//  Two-piece split clamp (M5) grips the 50.8mm frame tube; an angled post
//  stands the button up where a person beside the mower can SLAP it.
// ============================================================================

// One half of the square frame-tube split clamp. Tube axis runs along Y.
// Bottom half occupies z[-(FT/2+wall), 0]; top half z[0, FT/2+wall].
module estop_clamp_half(half="bottom") {
    hh = FRAME_TUBE_W/2 + CL_WALL;          // height of this half-shell
    z0 = (half=="top") ? 0 : -hh;           // base z of this half block
    bz = (half=="top") ? 0 : -FRAME_TUBE_W/2; // base z of the half-bore
    difference() {
        union() {
            // main half block (centred X & Y)
            translate([-CL_BW/2, -CL_LEN/2, z0]) cube([CL_BW, CL_LEN, hh]);
            // bolt ears (full half-height columns) on both X sides
            translate([-CL_BW/2-CL_EAR, -CL_LEN/2, z0]) cube([CL_EAR, CL_LEN, hh]);
            translate([ CL_BW/2,        -CL_LEN/2, z0]) cube([CL_EAR, CL_LEN, hh]);
        }
        // half-bore for the square frame tube
        translate([-(FRAME_TUBE_W+SLOP)/2, -CL_LEN/2-EPS, bz-SLOP/2])
            cube([FRAME_TUBE_W+SLOP, CL_LEN+2*EPS, FRAME_TUBE_W/2+SLOP]);
        // M5 clamp bolts through the ears (2 per side, along Z)
        for (s=[-1,1], y=[-1,1])
            translate([s*(CL_BW/2+CL_EAR/2), y*CL_LEN/4, 0])
                cylinder(d=M5_CLEAR, h=inf, center=true);
    }
}

// Angled post + button mounting pad, growing off the TOP clamp half.
module estop_post() {
    z0 = FRAME_TUBE_W/2 + CL_WALL;          // top face of the top clamp half
    dy = POST_H*tan(POST_LEAN);             // lean offset in +Y
    // leaning tapered column (hull of a base slab and a top slab)
    hull() {
        translate([0, 0, z0])           linear_extrude(2) rrect([44, 34], 5);
        translate([0, dy, z0+POST_H]) rotate([POST_LEAN,0,0])
            linear_extrude(2) rrect([ESTOP_FACE[0], 16], 5);
    }
    // top mounting pad (perpendicular to the slap axis) with M4 tap holes
    difference() {
        translate([0, dy, z0+POST_H]) rotate([POST_LEAN,0,0])
            translate([0,0,-EPS]) linear_extrude(6) rrect(ESTOP_FACE, 6);
        translate([0, dy, z0+POST_H]) rotate([POST_LEAN,0,0])
            hole_grid(ESTOP_FACE_HOLES, ESTOP_FACE_HOLES)
                translate([0,0,-EPS]) cylinder(d=M4_TAP, h=20);
    }
}

// The button face plate: clean 22.5mm device cutout + bezel relief + M4 corners.
module estop_face() {
    difference() {
        linear_extrude(4) rrect(ESTOP_FACE, 6);
        // 22mm device cutout (ESTOP_PANEL_HOLE)
        translate([0,0,-EPS]) cylinder(d=ESTOP_PANEL_HOLE, h=4+2*EPS);
        // bezel seat relief on the front face
        translate([0,0,4-1.5]) cylinder(d=ESTOP_BEZEL_DIA, h=1.5+EPS);
        // corner M4 clearance holes (match the post pad)
        hole_grid(ESTOP_FACE_HOLES, ESTOP_FACE_HOLES)
            translate([0,0,-EPS]) cylinder(d=M4_CLEAR, h=4+2*EPS);
    }
}

// ============================================================================
//  2) PTO RELAY BOX  (weather-resistant)
//  Houses a 5-pin automotive relay (drives the blade-clutch / PTO and shares
//  the e-stop kill leg) plus a couple of spade-terminal blocks. Base carries a
//  gasket groove on its rim + two cable glands; lid compresses the gasket.
// ============================================================================
BOX_IN = [70, 50];                       // internal footprint
BOX_H  = 45;                             // internal-ish height (>= relay 35 + slack)
BOX_EXT = [BOX_IN[0]+2*ENC_WALL, BOX_IN[1]+2*ENC_WALL];
BOX_SDX = BOX_EXT[0]-11;                  // lid/boss screw spacing X
BOX_SDY = BOX_EXT[1]-11;                  // lid/boss screw spacing Y

module relay_box() {
    difference() {
        union() {
            // outer shell
            linear_extrude(BOX_H) rrect(BOX_EXT, 4);
            // internal corner bosses for the lid screws
            hole_grid(BOX_SDX, BOX_SDY) cylinder(d=8, h=BOX_H);
            // relay locating collar (open-top, holds the relay base)
            translate([-12,0,ENC_FLOOR]) difference() {
                linear_extrude(8) rrect([RELAY[0]+4, RELAY[1]+4], 2);
                translate([0,0,-EPS])
                    linear_extrude(8+2*EPS) rrect([RELAY[0]+CLEAR_FIT, RELAY[1]+CLEAR_FIT], 1);
            }
            // two spade-terminal-block pads
            for (y=[-1,1]) translate([24, y*14, ENC_FLOOR]) cylinder(d=8, h=6);
        }
        // main cavity
        translate([0,0,ENC_FLOOR]) linear_extrude(BOX_H) rrect(BOX_IN, 3);
        // gasket groove cut into the top rim
        translate([0,0,BOX_H-GASKET_GROOVE_D])
            linear_extrude(GASKET_GROOVE_D+EPS)
                gasket_groove(BOX_EXT[0]-ENC_WALL, BOX_EXT[1]-ENC_WALL);
        // re-cut cavity through the bosses' inner faces is not needed; tap them:
        hole_grid(BOX_SDX, BOX_SDY)
            translate([0,0,ENC_FLOOR]) cylinder(d=M3_TAP, h=BOX_H);
        // terminal-block screw taps
        for (y=[-1,1]) translate([24, y*14, ENC_FLOOR+1])
            cylinder(d=M3_TAP, h=6);
        // two cable glands — constrained to the front (-Y) wall ONLY
        intersection() {
            translate([0,-BOX_EXT[1]/2, BOX_H*0.45])
                cube([BOX_EXT[0]+EPS, 2*ENC_WALL+4, BOX_H], center=true);
            for (x=[-1,1]) translate([x*16, 0, BOX_H*0.45])
                rotate([90,0,0]) cable_gland_hole(CABLE_GLAND_D);
        }
    }
}

module relay_lid() {
    difference() {
        union() {
            linear_extrude(ENC_FLOOR) rrect(BOX_EXT, 4);
            // centring spigot that drops into the cavity to locate the lid
            translate([0,0,-3]) linear_extrude(3+EPS) difference() {
                rrect([BOX_IN[0]-2*CLEAR_FIT, BOX_IN[1]-2*CLEAR_FIT], 3);
                rrect([BOX_IN[0]-2*CLEAR_FIT-4, BOX_IN[1]-2*CLEAR_FIT-4], 2);
            }
        }
        // corner screw clearances (match box bosses)
        hole_grid(BOX_SDX, BOX_SDY)
            translate([0,0,-3-EPS]) cylinder(d=M3_CLEAR, h=ENC_FLOOR+3+2*EPS);
    }
}

// ============================================================================
//  3) THROTTLE SERVO BRACKET
//  A standard servo drops between two end flanges; its mounting tabs screw
//  down (SERVO_HOLE_D) at the SERVO_TAB_DX hole spacing. The horn faces up and
//  is linked to the THROTTLE_LEVER_OD (8mm) throttle rod by a pushrod.
//  PUSHROD CLEVIS REFERENCE: a 2-56 / M2 ball-link or Z-bend clevis pins to the
//  servo horn and to the throttle lever; size the horn-to-lever pushrod so the
//  servo's ~120deg sweep maps to the THROTTLE_LEVER_TRAVEL (45mm) idle->full
//  throw. Bracket bolts down via the two M4 slots in the foot.
// ============================================================================
module throttle_servo_bracket() {
    bt       = ENC_FLOOR;                 // foot thickness
    bodyGap  = SERVO[0] + CLEAR_FIT;      // clear gap between flanges (X)
    flangeT  = 8;                         // flange thickness (X)
    flangeH  = SERVO[2] + 4;              // flange height (tabs sit near top)
    footW    = SERVO[1] + 2*12;           // foot width (Y), room for M4 slots
    footL    = bodyGap + 2*flangeT;       // foot length (X)
    difference() {
        union() {
            // foot
            linear_extrude(bt) rrect([footL, footW], 4);
            // two end flanges the servo bridges between
            for (s=[-1,1])
                translate([s*(bodyGap/2+flangeT/2), 0, 0])
                    linear_extrude(flangeH) rrect([flangeT, SERVO[1]+8], 2);
        }
        // servo tab screw holes (classic 4-hole pattern through the flange tops)
        hole_grid(SERVO_TAB_DX, 10)
            translate([0,0,-EPS]) cylinder(d=SERVO_HOLE_D, h=flangeH+2*EPS);
        // two M4 mounting slots in the foot
        for (y=[-1,1]) translate([0, y*(footW/2-6), 0])
            hull() for (x=[-1,1]) translate([x*8,0,-EPS])
                cylinder(d=M4_CLEAR, h=bt+2*EPS);
        // pushrod pass-through in the foot (THROTTLE_LEVER_OD rod clearance)
        translate([0, footW/2-3, -EPS])
            cylinder(d=THROTTLE_LEVER_OD+CLEAR_FIT, h=bt+2*EPS);
    }
}

// ============================================================================
//  PRINT PLATES  (exposed module API — print each individually)
// ============================================================================
module PRINT_estop_pedestal_a()        proxy() { estop_clamp_half("top"); estop_post(); }
module PRINT_estop_pedestal_b()        proxy() estop_clamp_half("bottom");
module PRINT_estop_face()              proxy() estop_face();
module PRINT_relay_box()               proxy() relay_box();
module PRINT_relay_lid()               proxy() relay_lid();
module PRINT_throttle_servo_bracket()  proxy() throttle_servo_bracket();

// ============================================================================
//  PREVIEW  —  all six print parts laid out in a grid (each fits 150mm bed)
// ============================================================================
if (is_undef(PREVIEW_OFF)) {
    translate([-90,  90, 0]) PRINT_estop_pedestal_a();
    translate([  0,  90, 0]) PRINT_estop_pedestal_b();
    translate([ 90,  90, 0]) PRINT_estop_face();
    translate([-90, -40, 0]) PRINT_relay_box();
    translate([  0, -40, 0]) PRINT_relay_lid();
    translate([ 90, -40, 0]) PRINT_throttle_servo_bracket();
}
