// SPDX-License-Identifier: MIT
// ============================================================================
//  BRAIN ENCLOSURE — internal equipment plate + seat mounting feet
//  We DO NOT print a waterproof box (FDM layer lines leak). We print an
//  organizer plate that bolts inside a COTS IP65 ABS box (in the cart), plus
//  feet/straps to lock that box to the mower seat.
//  Two-level layout keeps footprint <= bed:  lower deck = Pi5+Hailo;
//  upper shelf (on tall standoffs) = Pixhawk FC + simpleRTK2B; bucks on rail.
//  PRINT: PETG/ASA, 3 walls, 25% infill.
// ============================================================================
include <utils.scad>

PLATE = [140, 140];      // fits 150 bed with margin
PLATE_T = 4;
SHELF_Z = 34;            // upper shelf height above plate (clears Pi+Hailo)
POST_D = 8;

// generic standoff-post with heat-set pilot top, M3
module post(h) standoff(h=h, d=POST_D, pilot=HEATSET_M3_D, pilot_l=4.5);

// ---- LOWER DECK: equipment plate -------------------------------------------
module equipment_plate() {
    difference() {
        union() {
            // base plate
            linear_extrude(PLATE_T) rrect(PLATE, 6);
            // Pi5 standoffs — cluster CENTERED so bosses stay on the plate.
            // (holes span PI5_HOLE_DX x PI5_HOLE_DY about this point)
            translate([-30, -32, PLATE_T])
                hole_grid(PI5_HOLE_DX, PI5_HOLE_DY) post(PI5_STANDOFF);
            // 4 tall posts carrying the upper shelf (corners of a 110x110 sq)
            for (x=[-1,1], y=[-1,1]) translate([x*55, y*55, PLATE_T]) post(SHELF_Z);
            // buck-converter standoffs (2 stacked on the right, fully inside)
            for (i=[0,1]) translate([36, -28+i*56, PLATE_T])
                hole_grid(BUCK_L-2*BUCK_HOLE_INSET, BUCK_W-2*BUCK_HOLE_INSET)
                    post(8);
        }
        // 4 corner mount holes to the COTS box floor
        for (x=[-1,1], y=[-1,1]) translate([x*(PLATE[0]/2-8), y*(PLATE[1]/2-8), -EPS])
            cylinder(d=M4_CLEAR, h=PLATE_T+2*EPS);
        // cable routing slots
        for (i=[-1,0,1]) translate([i*30, 0, -EPS])
            linear_extrude(PLATE_T+2*EPS) rrect([8, 40], 4);
    }
}

// ---- UPPER SHELF: FC + RTK --------------------------------------------------
module upper_shelf() {
    difference() {
        union() {
            linear_extrude(PLATE_T) rrect([124,124], 6);
            // FC standoffs (left) — slotted so it fits varied FC hole patterns
            translate([-30, 0, PLATE_T]) hole_grid(FC_HOLE_DX, FC_HOLE_DY)
                post(6);
            // RTK standoffs (right)
            translate([34, 0, PLATE_T]) hole_grid(RTK_L-10, RTK_W-10) post(6);
        }
        // holes that drop onto the 4 tall posts (M3 clearance + counterbore)
        for (x=[-1,1], y=[-1,1]) translate([x*55, y*55, 0])
            screw_hole(d=M3_CLEAR, head_d=M3_HEAD, head_h=3, h=PLATE_T);
        // ventilation/lightening + cable holes
        for (a=[0:45:359]) rotate([0,0,a]) translate([44,0,-EPS])
            cylinder(d=8, h=PLATE_T+2*EPS);
    }
}

// ---- SEAT MOUNTING: box feet with ratchet-strap slots ----------------------
module box_foot() {
    // an L-foot that bolts to the COTS box corner and provides a strap slot +
    // a rubber-pad pocket so the box grips the seat pan.
    difference() {
        union() {
            cube([40, 40, 6]);                       // base pad
            translate([0,0,0]) cube([6, 40, 26]);    // upstand to box wall
        }
        // bolt to box wall
        translate([3, 20, 16]) rotate([0,90,0]) cylinder(d=M4_CLEAR, h=20, center=true);
        // strap slot
        translate([14, -EPS, -EPS]) cube([12, 42, 4.5]);
        // anti-slip pad pocket (for stick-on rubber)
        translate([12, 8, -EPS]) cube([26, 24, 1.6]);
    }
}

// ---- print plates ----------------------------------------------------------
module PRINT_equipment_plate() equipment_plate();
module PRINT_upper_shelf()     upper_shelf();
module PRINT_box_foot()        box_foot();

// preview: exploded stack
if (is_undef(PREVIEW_OFF)) {
    equipment_plate();
    translate([0,0,SHELF_Z+PLATE_T]) %upper_shelf();
    translate([90,-60,0]) box_foot();
}
