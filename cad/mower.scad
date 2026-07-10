// ============================================================================
//  MOWER MOCK-UP  —  parametric zero-turn body (reference: Gravely ZT 52")
//  VISUALIZATION CONTEXT ONLY — not printed. Lets us place every retrofit
//  component on the machine and check clearance, reach, and sightlines.
//  All dims approximate-to-class; tune the block below to match your unit.
// ============================================================================
include <utils.scad>

// ---- Mower envelope (approx, ZT 52" class) ---------------------------------
M_DECK_W      = 1321;   // 52" cutting deck width
M_DECK_D      = 720;    // deck front-back
M_DECK_Z      = 90;     // ground clearance of deck shell
M_DECK_H      = 110;    // deck shell height
M_FRAME_L     = 1500;   // main frame rail length
M_FRAME_W     = 560;    // rail centre-centre  (~ lap bar spacing)
M_RAIL        = 50;     // square tube size
M_REAR_WHEEL_D= 508;    // ZT X 52: 20x10-8 → 20" dia
M_REAR_WHEEL_W= 254;    // 10" wide
M_FRONT_CASTER_D = 279; // 11x6-5 → 11" dia
M_FRONT_CASTER_W = 152; // 6" wide
M_WHEELBASE   = 900;
M_SEAT_Z      = 580;    // seat pan height off ground (ZT X, no ROPS, H 46")
M_ENGINE      = [430, 480, 360];
M_HAS_ROPS    = false;  // ZT X 52 has NO factory ROPS (residential) → GPS mast mounts to seat frame
M_ROPS_H      = 1100;   // (only used if a ROPS is fitted)

// Ground = z0. Rear axle centred at x=0; front casters forward (+X).

module mower_wheel(d, w) rotate([90,0,0]) cylinder(d=d, h=w, center=true);

module mower_frame() mower_mat() {
    // two main rails
    for (y=[-M_FRAME_W/2, M_FRAME_W/2])
        translate([-M_FRAME_L/2+200, y, M_REAR_WHEEL_D/2])
            cube([M_FRAME_L, M_RAIL, M_RAIL]);
    // rear cross member (engine deck / actuator anchor rail)
    translate([-M_FRAME_L/2+250, 0, M_REAR_WHEEL_D/2])
        cube([M_RAIL, M_FRAME_W+M_RAIL, M_RAIL], center=false);
    // front cross member
    translate([M_WHEELBASE-100, 0, M_REAR_WHEEL_D/2])
        cube([M_RAIL, M_FRAME_W+M_RAIL, M_RAIL], center=false);
}

module mower_wheels() mower_blk() {
    // rear drive wheels
    for (y=[-(M_FRAME_W/2+M_REAR_WHEEL_W/2+30), (M_FRAME_W/2+M_REAR_WHEEL_W/2+30)])
        translate([0, y, M_REAR_WHEEL_D/2]) mower_wheel(M_REAR_WHEEL_D, M_REAR_WHEEL_W);
    // front casters
    for (y=[-(M_FRAME_W/2-40), (M_FRAME_W/2-40)])
        translate([M_WHEELBASE, y, M_FRONT_CASTER_D/2])
            mower_wheel(M_FRONT_CASTER_D, M_FRONT_CASTER_W);
}

module mower_deck() mower_mat()
    translate([M_WHEELBASE*0.45, 0, M_DECK_Z + M_DECK_H/2])
        rbox_full([M_DECK_D, M_DECK_W, M_DECK_H], 18);

module mower_engine() mower_mat()
    translate([-M_FRAME_L/2+200+M_ENGINE[0]/2, 0, M_REAR_WHEEL_D/2+M_RAIL+M_ENGINE[2]/2])
        rbox_full(M_ENGINE, 12);

module mower_seat() mower_blk() {
    // seat pan
    translate([M_WHEELBASE*0.18, 0, M_SEAT_Z])
        rbox_full([SEAT_DEPTH, SEAT_WIDTH, 50], 20);
    // seat back
    translate([M_WHEELBASE*0.18-SEAT_DEPTH/2+30, 0, M_SEAT_Z+220])
        rotate([0,-12,0]) rbox_full([60, SEAT_WIDTH, 420], 20);
}

module mower_rops() mower_mat() {
    bx = M_WHEELBASE*0.18 - SEAT_DEPTH/2 - 40;
    for (y=[-M_FRAME_W/2, M_FRAME_W/2])
        translate([bx, y, M_SEAT_Z]) cube([60, 60, M_ROPS_H]);
    translate([bx, 0, M_SEAT_Z+M_ROPS_H]) cube([60, M_FRAME_W+60, 60], center=false);
}

// Twin lap bars. angle: 0 = neutral; +fwd. Pivot near the seat front.
module mower_lapbar(side=1, angle=0) mower_blk() {
    px = M_WHEELBASE*0.18 + SEAT_DEPTH/2 - 40;     // pivot x
    py = side*LAP_BAR_SPACING/2;
    pz = M_SEAT_Z - 60;                            // pivot z
    translate([px, py, pz]) rotate([0, -angle, 0]) {
        // upright arm
        cylinder(d=LAP_BAR_TUBE_OD, h=LAP_BAR_CLAMP_HEIGHT);
        // forward grip elbow
        translate([0,0,LAP_BAR_CLAMP_HEIGHT]) rotate([0,90,0])
            cylinder(d=LAP_BAR_TUBE_OD, h=180);
    }
}
// returns the world position of a lap-bar clamp point (for placing actuators)
function lapbar_clamp_pos(side) = [
    M_WHEELBASE*0.18 + SEAT_DEPTH/2 - 40,
    side*LAP_BAR_SPACING/2,
    (M_SEAT_Z - 60) + LAP_BAR_CLAMP_HEIGHT*0.75
];

// ============================================================================
//  HIGHER-FIDELITY DETAIL — real features, curves + fillets (visualization).
//  Reference points (frame, seat, lap-bar clamp) are UNCHANGED so the retrofit
//  parts still align. A spec-perfect twin needs the OEM CAD / a 3D scan; this
//  is a faithful placement mock, not a manufacturing model of the base machine.
// ============================================================================

// Front caster forks — swivel post + a fork plate each side of the wheel  [black]
module mower_casters() mower_blk()
    for (y=[-(M_FRAME_W/2-40), (M_FRAME_W/2-40)]) translate([M_WHEELBASE, y, 0]) {
        translate([0,0,M_FRONT_CASTER_D/2]) cylinder(d=24, h=140);        // swivel post
        translate([0,0,M_FRONT_CASTER_D/2+140]) rbox_full([60,70,16],6);  // top plate
        for (s=[-1,1]) translate([0, s*(M_FRONT_CASTER_W/2+5), M_FRONT_CASTER_D/2])
            rotate([90,0,0]) cylinder(d=M_FRONT_CASTER_D*0.66, h=6, center=true); // fork arm
    }

// Operator foot deck / floor pan (rounded)  [red]
module mower_footdeck() mower_mat()
    translate([M_WHEELBASE*0.55, 0, M_REAR_WHEEL_D/2+M_RAIL-4])
        rbox_full([340, M_FRAME_W+130, 16], 26);

// Dual fuel tanks flanking the seat (rounded)  [black]
module mower_fueltanks() mower_blk()
    for (y=[-(M_FRAME_W/2+42), (M_FRAME_W/2+42)])
        translate([M_WHEELBASE*0.04, y, M_SEAT_Z-30]) rbox_full([190,96,150],34);

// Rear tyre fenders — curved half-arch guards over the drive wheels  [red]
module mower_fenders() mower_mat()
    for (y=[-(M_FRAME_W/2+M_REAR_WHEEL_W/2+30), (M_FRAME_W/2+M_REAR_WHEEL_W/2+30)])
        translate([0, y, M_REAR_WHEEL_D/2]) rotate([90,0,0])
            rotate_extrude(angle=180) translate([M_REAR_WHEEL_D/2+18,0,0])
                offset(4) square([M_REAR_WHEEL_W+8, 6], center=true);

// Cutting-deck detail: 3 spindle housings, belt cover, side discharge, rollers
module mower_deck_details() {
    dz = M_DECK_Z + M_DECK_H;  dx = M_WHEELBASE*0.45;
    mower_blk() for (y=[-M_DECK_W*0.3, 0, M_DECK_W*0.3])                    // spindle housings
        translate([dx, y, dz]) cylinder(d=72, h=42);
    mower_blk() translate([dx-M_DECK_D*0.32, 0, dz+10])                     // belt / pulley cover
        rbox_full([100, M_DECK_W*0.78, 26], 12);
    mower_mat() translate([dx, M_DECK_W/2+30, M_DECK_Z+M_DECK_H*0.4])       // side-discharge chute
        rotate([0,0,28]) rbox_full([130, 110, 64], 14);
    mower_blk() for (y=[-M_DECK_W*0.34, M_DECK_W*0.34])                     // anti-scalp rollers
        translate([dx+M_DECK_D*0.46, y, M_DECK_Z-6]) rotate([90,0,0]) cylinder(d=54,h=26,center=true);
}

// Control panel / dash by the seat  [black]
module mower_dash() mower_blk()
    translate([M_WHEELBASE*0.34, 0, M_SEAT_Z+12]) rbox_full([44,230,30],12);

// Engine detail: muffler + air-filter box  [black]
module mower_engine_detail() mower_blk() {
    ex = -M_FRAME_L/2+200+M_ENGINE[0]/2; ez = M_REAR_WHEEL_D/2+M_RAIL;
    translate([ex, M_ENGINE[1]/2+22, ez+M_ENGINE[2]*0.4]) rotate([90,0,0]) cylinder(d=62,h=95); // muffler
    translate([ex, 0, ez+M_ENGINE[2]+26]) rbox_full([120,150,56],22);                          // air filter
}

// Seat-back support frame (ZT X has no ROPS, but the seat frame stands)  [black]
module mower_seatframe() mower_blk() {
    bx = M_WHEELBASE*0.18 - SEAT_DEPTH/2 - 26;
    for (y=[-SEAT_WIDTH/2+22, SEAT_WIDTH/2-22]) translate([bx, y, M_SEAT_Z]) rbox_full([38,30,300],8);
}

module mower(lap_angle=0) {
    mower_frame();
    mower_footdeck();
    mower_fenders();
    mower_wheels();
    mower_casters();
    mower_deck();
    mower_deck_details();
    mower_engine();
    mower_engine_detail();
    mower_fueltanks();
    mower_seat();
    mower_seatframe();
    mower_dash();
    if (M_HAS_ROPS) mower_rops();
    mower_lapbar(side=+1, angle=lap_angle);
    mower_lapbar(side=-1, angle=lap_angle);
}

// preview when opened standalone (suppressed when included by assembly.scad)
if (is_undef(ASSEMBLY)) mower(lap_angle=8);
