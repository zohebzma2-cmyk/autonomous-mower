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

module mower_wheels() mower_mat() {
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

module mower_seat() mower_mat() {
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
module mower_lapbar(side=1, angle=0) mower_mat() {
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

module mower(lap_angle=0) {
    mower_frame();
    mower_wheels();
    mower_deck();
    mower_engine();
    mower_seat();
    if (M_HAS_ROPS) mower_rops();
    mower_lapbar(side=+1, angle=lap_angle);
    mower_lapbar(side=-1, angle=lap_angle);
}

// preview when opened standalone (suppressed when included by assembly.scad)
if (is_undef(ASSEMBLY)) mower(lap_angle=8);
