// ============================================================================
//  GPS ANTENNA MAST MOUNT  —  autonomous zero-turn mower retrofit
//  Clamps to the vertical ROPS (roll-over bar) post and carries a tall
//  aluminium mast so the RTK GPS antenna sits HIGH and clear of the metal
//  frame (metal near a survey antenna kills multipath / sky view).
//
//  PRINTED PIECES (each fits the 150x150x150 bed, < 145 mm every axis):
//    A) PRINT_gps_clamp_a()  — front clamp half + vertical mast socket
//    B) PRINT_gps_clamp_b()  — rear clamp half
//    C) PRINT_gps_top_plate() — antenna plate that caps the mast top
//
//  USER-SUPPLIED (not printed):
//    - 60 mm SQUARE steel ROPS post (the thing we clamp to)
//    - 20 mm OD aluminium tube = the mast (cut to the height you want)
//    - 2x M5 clamp bolts + nuts, 1x M4 set screw, 1x 1/4"-20 antenna stud
//
//  GROUND-PLANE NOTE:  Most survey / helical RTK antennas want a metal
//  ground plane under them. Add a ~100 mm steel or aluminium-foil-faced disc
//  sandwiched between this plate and the antenna for best fix quality.
//
//  PRINT: ASA or PETG, 4+ walls, 40%+ infill. Clamp + thru-bolts carry load;
//  for safety also drill the ROPS post and add a thru-pin on final install.
// ============================================================================
include <utils.scad>

// ---- TOP-LEVEL PARAMETERS (re-measure / re-size here) ----------------------
ROPS_POST   = 60;     // [MEASURE] ROPS post is 60 mm SQUARE steel
MAST_OD     = 20;     // [BUY] aluminium mast tube outside diameter

// ---- DERIVED / DESIGN CONSTANTS --------------------------------------------
CLAMP_WALL  = 8;                          // wall around the steel post
CLAMP_H     = 50;                         // clamp height up the post (Z)
EAR_W       = 16;                         // bolt-ear width (each side)
CLAMP_GAP   = 0.8;                        // gap between halves so bolts squeeze
BX          = ROPS_POST + 2*CLAMP_WALL;   // clamp block X
BY          = ROPS_POST + 2*CLAMP_WALL;   // clamp block Y (split at y=0)

SOCKET_WALL = 4;                          // wall of the printed mast socket
SOCKET_OD   = MAST_OD + 2*SOCKET_WALL;    // mast socket outside diameter
MAST_BORE   = MAST_OD + CLEAR_FIT;        // sliding fit for the mast tube
SOCK_Y      = BY/2 + SOCKET_OD/2 - 8;     // socket sits on the front face

PLATE_TH    = 6;                          // antenna plate thickness
CAP_DEPTH   = 18;                         // how deep the mast enters the cap
DRAIN_PCD   = GPS_ANT_DIA * 0.66;         // drain/weight-hole bolt circle
DRAIN_D     = 4;

// ============================================================================
//  SPLIT CLAMP  —  grips the 60 mm SQUARE ROPS post, two M5 bolts pull together
// ============================================================================
// Full clamp block (both halves) BEFORE the split. `with_socket` adds the
// vertical mast socket (only printed on half A).
module clamp_block(with_socket=false) {
    difference() {
        union() {
            // main body
            linear_extrude(CLAMP_H) rrect([BX, BY], 4);
            // bolt ears on +X / -X faces
            for (s=[-1,1])
                translate([s*(BX/2 + EAR_W/2 - 2), 0, 0])
                    linear_extrude(CLAMP_H) rrect([EAR_W, BY], 3);
            // vertical mast socket on the front (+Y) face
            if (with_socket)
                translate([0, SOCK_Y, 0]) cylinder(d=SOCKET_OD, h=CLAMP_H);
        }
        // square bore for the ROPS post (vertical)
        translate([0,0,-EPS])
            linear_extrude(CLAMP_H + 2*EPS)
                square([ROPS_POST + SLOP, ROPS_POST + SLOP], center=true);
        // two M5 clamp bolts (along Y), one through each ear
        for (s=[-1,1])
            translate([s*(BX/2 + EAR_W/2 - 2), 0, CLAMP_H/2])
                rotate([90,0,0]) cylinder(d=M5_CLEAR, h=inf, center=true);
        if (with_socket) {
            // mast bore (sliding fit)
            translate([0, SOCK_Y, -EPS])
                cylinder(d=MAST_BORE, h=CLAMP_H + 2*EPS);
            // M4 set-screw, tapped, radial from the front into the mast bore
            translate([0, SOCK_Y + SOCKET_WALL + MAST_OD/2, CLAMP_H/2])
                rotate([90,0,0])
                    cylinder(d=M4_TAP, h=SOCKET_WALL + MAST_OD/2 + 2);
        }
    }
}

// One printed half. half="a" keeps y>=gap (front, gets the socket);
// half="b" keeps y<=-gap (rear).
module clamp_half(half="a") {
    g = CLAMP_GAP/2;
    intersection() {
        clamp_block(with_socket = (half=="a"));
        if (half=="a") translate([-inf/2,  g,        -inf/2]) cube(inf);
        else           translate([-inf/2, -g - inf,  -inf/2]) cube(inf);
    }
}

// ============================================================================
//  TOP ANTENNA PLATE  —  disc sized to the antenna, caps the mast top.
//  Built in INSTALLED orientation (disc up, cap socket hanging below).
//  PRINT_gps_top_plate() flips it so it prints disc-down / socket-up.
// ============================================================================
module top_plate() {
    difference() {
        union() {
            // antenna disc
            cylinder(d=GPS_ANT_DIA, h=PLATE_TH);
            // cap socket underneath (receives the mast top)
            translate([0,0,-CAP_DEPTH]) cylinder(d=SOCKET_OD, h=CAP_DEPTH + EPS);
        }
        // center clearance hole for the 1/4"-20 antenna stud (GPS_ANT_BOLT)
        translate([0,0,-EPS])
            cylinder(d=GPS_ANT_BOLT + CLEAR_FIT, h=PLATE_TH + 2*EPS);
        // blind mast bore in the cap (mast butts the plate underside)
        translate([0,0,-CAP_DEPTH])
            cylinder(d=MAST_BORE, h=CAP_DEPTH + EPS);
        // M4 set-screw into the cap socket (locks the mast top)
        translate([0, SOCKET_OD/2 + EPS, -CAP_DEPTH/2])
            rotate([90,0,0]) cylinder(d=M4_TAP, h=SOCKET_WALL + MAST_OD/2 + 2);
        // 3 drainage / weight-saving holes through the disc
        bolt_circle(DRAIN_PCD, 3)
            translate([0,0,-EPS]) cylinder(d=DRAIN_D, h=PLATE_TH + 2*EPS);
    }
}

// ============================================================================
//  EXPOSED PRINT PLATES
// ============================================================================
module PRINT_gps_clamp_a()  proxy() clamp_half("a");   // front half + socket
module PRINT_gps_clamp_b()  proxy() clamp_half("b");   // rear half
module PRINT_gps_top_plate()                            // flipped to print flat
    proxy() translate([0,0,PLATE_TH]) rotate([180,0,0]) top_plate();

// ============================================================================
//  PREVIEW  —  all three printed pieces laid out side by side
// ============================================================================
if (is_undef(PREVIEW_OFF)) {
    translate([-90, 0, 0]) PRINT_gps_clamp_a();
    translate([  0, 0, 0]) PRINT_gps_clamp_b();
    translate([ 95, 0, 0]) PRINT_gps_top_plate();
}
