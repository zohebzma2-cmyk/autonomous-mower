// ============================================================================
//  PHASE-3 ATTACHMENT MOUNTING HARDWARE — printable brackets (7 parts)
//  Same rules as the original kit: every part fits the 150 mm bed (gated by
//  export_stl.sh), prints in ASA/PETG, and ships brim-baked via bake_brims.sh.
//  Placement context in mower.scad (mower_attachments); policy/interlocks in
//  software/companion/attachments.py; spec in docs/ATTACHMENTS.md.
// ============================================================================
include <utils.scad>

BOOM_TUBE_OD   = 40.0;   // boom arm tube (matches cad boom + slew kit bore)
DUMP_PIN_D     = 6.5;    // 1/4" clevis pin, PA-14 family (same as lap-bar units)
DUCT_HOSE_ID   = 100.0;  // bagger duct hose inner dia
DECK_OUTLET    = [110, 70];  // deck discharge outlet the duct adapter flanges onto
TPMS_RX        = [52, 20, 10];  // USB TPMS receiver dongle envelope
PWM_MODULE     = [62, 42];      // sprayer PWM relay module bolt pattern envelope

// ---- 1) boom base plate — bolts the slew-ring turntable to the frame nose --
module PRINT_boom_base_plate() proxy() difference() {
    linear_extrude(8) rrect([110, 110], 10);
    translate([0,0,-EPS]) cylinder(d=62, h=8+2*EPS);                 // slew bore
    for (a=[0:90:270]) rotate([0,0,a+45]) translate([40,0,0])        // M5 slew bolts
        translate([0,0,-EPS]) cylinder(d=M5_CLEAR, h=8+2*EPS);
    for (x=[-1,1], y=[-1,1]) translate([x*46, y*46, 0])              // M6 frame slots
        hull() for (dy=[-4,4]) translate([0,dy,-EPS]) cylinder(d=6.5, h=8+2*EPS);
}

// ---- 2+3) blower cradle — two-piece saddle clamping the boom tube ----------
module _cradle_half(half) {
    tube_d = BOOM_TUBE_OD + SLOP;
    difference() {
        union() {
            linear_extrude(16) rrect([58, 50], 5);
            for (s=[-1,1]) translate([s*(29+7), 0, 0]) linear_extrude(16) rrect([14, 50], 3);
        }
        translate([0, 0, -EPS]) linear_extrude(16+2*EPS)
            intersection() {
                circle(d=tube_d);
                translate([-40, (half=="top" ? 0 : -50)]) square([80, 50]);
            }
        for (s=[-1,1]) translate([s*(29+7), 0, 8]) rotate([90,0,0])
            cylinder(d=M4_CLEAR, h=60, center=true);
    }
    if (half=="bottom")                              // blower band seat on the lower half
        translate([0, -34, 0]) difference() {
            linear_extrude(16) rrect([46, 20], 4);
            translate([0, -2, 8]) rotate([0,90,0]) cylinder(d=M4_CLEAR, h=60, center=true);
        }
}
module PRINT_blower_cradle_top()    proxy() _cradle_half("top");
module PRINT_blower_cradle_bottom() proxy() _cradle_half("bottom");

// ---- 4) trimmer motor plate — motor face + boom-tube U-seat -----------------
module PRINT_trimmer_motor_plate() proxy() difference() {
    linear_extrude(8) rrect([92, 92], 8);
    translate([0,0,-EPS]) cylinder(d=26, h=8+2*EPS);                 // shaft bore
    for (a=[0:90:270]) rotate([0,0,a]) translate([33,0,0])           // motor bolt slots
        hull() for (dr=[-3,3]) translate([dr,0,-EPS]) cylinder(d=M4_CLEAR, h=8+2*EPS);
    translate([0, 46+ -8, -EPS]) linear_extrude(8+2*EPS)             // boom-tube U-seat
        intersection() { circle(d=BOOM_TUBE_OD+SLOP); translate([-25,0]) square([50,30]); }
}

// ---- 5) duct adapter — deck outlet flange -> Ø100 bagger hose collar -------
module PRINT_duct_adapter() proxy() {
    difference() {                                                   // flange
        linear_extrude(5) rrect([DECK_OUTLET[0]+26, DECK_OUTLET[1]+26], 10);
        translate([0,0,-EPS]) linear_extrude(5+2*EPS) rrect(DECK_OUTLET, 8);
        for (x=[-1,1], y=[-1,1]) translate([x*(DECK_OUTLET[0]/2+8), y*(DECK_OUTLET[1]/2+8), -EPS])
            cylinder(d=M5_CLEAR, h=5+2*EPS);
    }
    difference() {                                                   // rect->round transition
        hull() {
            translate([0,0,5]) linear_extrude(0.1) rrect([DECK_OUTLET[0]+8, DECK_OUTLET[1]+8], 8);
            translate([0,0,42]) cylinder(d=DUCT_HOSE_ID+8, h=0.1);
        }
        hull() {
            translate([0,0,5-EPS]) linear_extrude(0.1) rrect(DECK_OUTLET, 8);
            translate([0,0,42]) cylinder(d=DUCT_HOSE_ID, h=0.1);
        }
    }
    difference() {                                                   // hose collar + clamp lip
        union() {
            translate([0,0,42]) cylinder(d=DUCT_HOSE_ID+8, h=22);
            translate([0,0,60]) cylinder(d=DUCT_HOSE_ID+12, h=4);
        }
        translate([0,0,42-EPS]) cylinder(d=DUCT_HOSE_ID, h=30);
    }
}

// ---- 6) dump clevis — anchors the bagger dump actuator (print 2) -----------
module PRINT_dump_clevis() proxy() difference() {
    union() {
        linear_extrude(8) rrect([64, 44], 6);                        // base
        for (s=[-1,1]) translate([s*14, 0, 0])                       // uprights, 21mm gap
            translate([-4+s*0, -16, 8]) cube([8, 32, 26]);
    }
    for (s=[-1,1]) translate([s*14, 0, 26]) rotate([0,90,0])         // clevis pin bore
        cylinder(d=DUMP_PIN_D+SLOP, h=40, center=true);
    for (x=[-1,1], y=[-1,1]) translate([x*24, y*14, -EPS])           // M5 base bolts
        cylinder(d=M5_CLEAR, h=8+2*EPS);
}

// ---- 7) TPMS receiver cradle — snap clip inside the brain box --------------
module PRINT_tpms_cradle() proxy() {
    difference() {
        linear_extrude(3) rrect([TPMS_RX[0]+14, TPMS_RX[1]+14], 5);  // base
        for (s=[-1,1]) translate([s*8, 0, -EPS]) cylinder(d=M3_CLEAR, h=3+2*EPS);   // M3 mounts
        for (s=[-1,1]) hull() for (y=[-4,4])                          // zip-tie slots
            translate([s*(TPMS_RX[0]/2-6), y, -EPS]) cylinder(d=3.5, h=3+2*EPS);
    }
    for (s=[-1,1]) translate([0, s*(TPMS_RX[1]/2+1.6), 0])           // snap walls w/ lead-in
        difference() {
            translate([-TPMS_RX[0]/2+6, -1.6+ (s<0?-0:0), 0]) cube([TPMS_RX[0]-12, 3.2, TPMS_RX[2]+4]);
            translate([0, s*3, TPMS_RX[2]+4]) rotate([s*35,0,0]) translate([-40,0,0]) cube([80, 6, 8]);
        }
}

// ---- 8) sprayer PWM controller mount — bosses for the relay module ---------
module PRINT_sprayer_ctrl_mount() proxy() {
    difference() {
        linear_extrude(4) rrect([PWM_MODULE[0]+22, PWM_MODULE[1]+22], 6);
        for (s=[-1,1]) translate([s*((PWM_MODULE[0]+22)/2-6), 0, -EPS])   // M5 panel bolts
            cylinder(d=M5_CLEAR, h=4+2*EPS);
        for (s=[-1,1]) hull() for (y=[-4,4])                              // harness zip slots
            translate([s*10, y + s*0, -EPS]) translate([0, (PWM_MODULE[1]+22)/2-5, 0]) cylinder(d=3.5, h=4+2*EPS);
    }
    for (x=[-1,1], y=[-1,1]) translate([x*PWM_MODULE[0]/2, y*PWM_MODULE[1]/2, 4])
        heatset_boss(h=7);                                                // M3 module bosses
}

// ---- preview layout (suppressed by export_stl.sh) ---------------------------
if (is_undef(PREVIEW_OFF)) {
    translate([-160,  90, 0]) PRINT_boom_base_plate();
    translate([   0,  90, 0]) PRINT_blower_cradle_top();
    translate([ 100,  90, 0]) PRINT_blower_cradle_bottom();
    translate([-160, -60, 0]) PRINT_trimmer_motor_plate();
    translate([   0, -80, 0]) PRINT_duct_adapter();
    translate([ 160, -60, 0]) PRINT_dump_clevis();
    translate([ 160,  30, 0]) PRINT_tpms_cradle();
    translate([   0,-220, 0]) PRINT_sprayer_ctrl_mount();
}
