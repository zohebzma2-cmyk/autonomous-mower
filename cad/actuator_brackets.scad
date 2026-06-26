// ============================================================================
//  LAP-BAR ACTUATOR BRACKETS  (the parts that actually steer the mower)
//  Two pieces per side:
//    A) lapbar_yoke  — split clamp on the lap bar + clevis for actuator rod
//    B) rail_anchor  — split clamp on the frame rail + clevis for actuator body
//  PRINT: ASA or PETG, 4+ walls, 40%+ infill. These take real load.
//  NOTE: clamps share load with a thru-bolt; for safety, also drill the tube
//  and use a thru-pin on final install (see build doc — clamp alone can slip).
// ============================================================================
include <utils.scad>

CLEVIS_GAP   = ACT_CLEVIS_W + CLEAR_FIT;     // slot for actuator clevis tang
CLEVIS_PIN_D = ACT_CLEVIS_PIN + CLEAR_FIT;
CLEVIS_PLATE = 8;                             // cheek thickness each side
CLEVIS_REACH = 55;                            // how far clevis stands off clamp

// ---- Shared clevis (двойная щека) ------------------------------------------
module clevis(reach=CLEVIS_REACH) {
    cheek_h = CLEVIS_PIN_D*2.4;
    difference() {
        union() {
            for (s=[-1,1]) translate([0, s*(CLEVIS_GAP/2+CLEVIS_PLATE/2), 0])
                hull() {
                    cube([CLEVIS_PLATE*2, CLEVIS_PLATE, 4], center=true);
                    translate([reach,0,0]) cylinder(d=cheek_h, h=4, center=true);
                }
        }
        translate([reach,0,0]) rotate([90,0,0])
            cylinder(d=CLEVIS_PIN_D, h=inf, center=true);
    }
}

// ---- A) Lap-bar yoke -------------------------------------------------------
module lapbar_yoke(half="bottom") {
    blk = [44, 46];
    union() {
        tube_clamp(half=half, block=blk, ear=14, t=10);
        if (half=="bottom")
            translate([blk[0]/2-2, 0, 5]) rotate([0,0,0])
                translate([0,0,-2]) linear_extrude(4) square([2,2]); // keepout marker
    }
}
// full yoke = bottom clamp + clevis arm (clevis prints with the bottom half)
module lapbar_yoke_assembly(half="bottom") {
    blk = [44, 46];
    lapbar_yoke(half=half);
    if (half=="bottom")
        translate([blk[0]/2+8, 0, 5]) clevis();
}

// ---- B) Frame-rail anchor --------------------------------------------------
// Square-tube clamp (two L-halves) hugging the frame rail, with a clevis.
module rail_clamp(half="bottom") {
    w = FRAME_TUBE_W + 2*ENC_WALL + SLOP;
    h = FRAME_TUBE_H/2 + ENC_WALL;
    difference() {
        linear_extrude(46) rrect([w, h], 3);
        // half-bore for the rail
        translate([0, (half=="bottom"? -ENC_WALL : ENC_WALL), -EPS])
            linear_extrude(46+2*EPS)
                square([FRAME_TUBE_W+SLOP, FRAME_TUBE_H+SLOP], center=true);
        // clamp bolts (corner)
        for (x=[-1,1]) translate([x*(w/2-5), 0, 12])
            rotate([0,90,0]) cylinder(d=M5_CLEAR, h=inf, center=true);
        for (x=[-1,1]) translate([x*(w/2-5), 0, 34])
            rotate([0,90,0]) cylinder(d=M5_CLEAR, h=inf, center=true);
    }
}
module rail_anchor_assembly(half="bottom") {
    w = FRAME_TUBE_W + 2*ENC_WALL + SLOP;
    rail_clamp(half=half);
    if (half=="bottom")
        translate([0, -(FRAME_TUBE_H/2+CLEVIS_REACH*0.2), 23]) rotate([0,0,90]) clevis();
}

// ---- print plates ----------------------------------------------------------
module PRINT_lapbar_yoke_top()    lapbar_yoke(half="top");
module PRINT_lapbar_yoke_bottom() lapbar_yoke_assembly(half="bottom");
module PRINT_rail_anchor_top()    rail_clamp(half="top");
module PRINT_rail_anchor_bottom() rail_anchor_assembly(half="bottom");

// preview
if (is_undef(PREVIEW_OFF)) {
    PRINT_lapbar_yoke_bottom();
    translate([0,80,0]) PRINT_rail_anchor_bottom();
}
