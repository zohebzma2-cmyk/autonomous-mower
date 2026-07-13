// SPDX-License-Identifier: MIT
// ============================================================================
//  MASTER ASSEMBLY — every retrofit subsystem placed on the mower mock.
//  Uses dimensionally-accurate PROXY volumes (real part dims from params) so
//  the whole-machine view stays fast and free of cross-file name collisions.
//  Detailed printable geometry lives in each component .scad + its STL.
//  Open standalone to see the full machine; set $vpr/$vpt via --camera to shoot.
// ============================================================================
ASSEMBLY = 1;                  // suppresses mower.scad's standalone preview
include <mower.scad>           // brings utils + params + the mower() module

// colour helpers for subsystems
module c_brain()  color([0.20,0.22,0.26]) children();   // IP65 box
module c_sensor() color([0.16,0.55,0.42]) children();   // GPS/LiDAR/cam
module c_act()    color([0.85,0.45,0.18]) children();   // actuators (orange)
module c_safety() color([0.85,0.18,0.16]) children();   // e-stop (red)
module c_mast()   color([0.55,0.57,0.60]) children();   // aluminium masts

// ---- subsystem proxies (accurate envelopes) --------------------------------
module px_brain_box() c_brain() difference() {           // COTS IP65 ~200x150x100
    rbox_full([210,160,105], 8);
    // engraved brand mark + wordmark on the lid (matches badge.scad)
    translate([0, 0, 52.5-1.4]) linear_extrude(1.6) {
        translate([-62, 0]) difference() { circle(d=34); circle(d=27); }  // ring
        translate([-62, 0]) circle(d=17);                                 // centre dot
        translate([12, 5.5]) text("AUTOACRE", size=13, font="Helvetica:style=Bold",
                                  halign="center", valign="center");
        translate([12, -12]) text("autonomous ZTR", size=7.5, font="Helvetica",
                                  halign="center", valign="center");
    }
}

module px_actuator() c_act() {                           // body + extended rod
    rotate([0,90,0]) cylinder(d=ACT_BODY_DIA, h=ACT_RETRACTED_L);
    translate([ACT_RETRACTED_L,0,0]) rotate([0,90,0]) cylinder(d=14, h=ACT_STROKE*0.6);
}
module px_gps_ant() c_sensor() cylinder(d=GPS_ANT_DIA, h=GPS_ANT_H);
module px_lidar()   c_sensor() cylinder(d=LIDAR_DIA, h=LIDAR_H);
module px_camera()  c_sensor() cube([CAM_W, CAM_L, 30], center=true);
module px_estop()   c_safety() { cylinder(d=30,h=40); translate([0,0,40]) sphere(d=ESTOP_BEZEL_DIA); }
module px_mast(h)   c_mast() cylinder(d=20, h=h);

// ---- placement on the machine ----------------------------------------------
// Each subsystem is its own module so the GLB can export them as separate
// nodes (exploded-view animation on the site). retrofit() = the whole kit.
module retro_brain()                                   // 1) brain box on the seat pan
    translate([M_WHEELBASE*0.18, 0, M_SEAT_Z+25+52]) px_brain_box();

module retro_actuators()                               // 2) rail up to each lap-bar clamp
    for (s=[-1,1]) {
        cp = lapbar_clamp_pos(s);                 // clamp point (world)
        anchor = [cp[0]-ACT_RETRACTED_L*0.6, cp[1], M_REAR_WHEEL_D/2+M_RAIL+40];
        translate(anchor)
            rotate([0,0, s*4])
                rotate([0, -atan2(cp[2]-anchor[2], ACT_RETRACTED_L), 0])
                    px_actuator();
    }

module retro_gps() {                                   // 3) GPS mast, antenna high & clear
    rops_x = M_WHEELBASE*0.18 - SEAT_DEPTH/2 - 40 + 30;
    translate([rops_x, -M_FRAME_W/2, M_SEAT_Z+200]) {
        px_mast(560);
        translate([0,0,560]) px_gps_ant();
    }
}

module retro_lidar()                                   // 4) LiDAR on a front mast
    translate([M_WHEELBASE-60, 0, M_REAR_WHEEL_D/2+M_RAIL]) {
        px_mast(255);
        translate([0,0,255]) px_lidar();
    }

module retro_camera()                                  // 5) camera below the LiDAR
    translate([M_WHEELBASE-30, 0, M_REAR_WHEEL_D/2+M_RAIL+180])
        rotate([0,15,0]) px_camera();

module retro_estop()                                   // 6) e-stop on the right rail
    translate([M_WHEELBASE*0.05, M_FRAME_W/2+30, M_REAR_WHEEL_D/2+M_RAIL]) px_estop();

module retrofit() {
    retro_brain();
    retro_actuators();
    retro_gps();
    retro_lidar();
    retro_camera();
    retro_estop();
}

// SHOW selects a colour group for multi-material export (-D SHOW='"body"' etc.)
// Default "all" renders the whole machine as before.
// "blade" exports ONE blade centered at origin — build_glb.py instances it at
// blade_pos(-1/0/1) as three nodes and bakes a spin animation on them.
SHOW = is_undef(SHOW) ? "all" : SHOW;
if (SHOW=="all")    { mower_full(lap_angle=6); mower_tpms_accent(); retrofit(); }
if (SHOW=="body")   { mower_frame(); mower_deck(); mower_engine(); mower_footdeck(); mower_fenders();
                      mower_rims(); }
if (SHOW=="black")  { mower_wheels(); mower_seat(); mower_lapbar(1,6); mower_lapbar(-1,6);
                      mower_casters(); mower_fueltanks(); mower_seatframe(); mower_dash();
                      mower_engine_detail(); mower_deck_details(); mower_branding(); }
if (SHOW=="retro")  retrofit();
if (SHOW=="accent") { mower_accents(); mower_tpms_accent(); }
if (SHOW=="blade")  mower_blade();
// per-subsystem exports for the exploded-view GLB nodes
if (SHOW=="retro_brain")     retro_brain();
if (SHOW=="retro_actuators") retro_actuators();
if (SHOW=="retro_gps")       retro_gps();
if (SHOW=="retro_lidar")     retro_lidar();
if (SHOW=="retro_camera")    retro_camera();
if (SHOW=="retro_estop")     retro_estop();
// Phase-3 attachments — each a separate GLB node (exploded-view + future anims)
if (SHOW=="bagger_frame")  mower_bagger_frame();
if (SHOW=="bagger_bins")   mower_bagger_bins();
if (SHOW=="boom_asm")      mower_boom();
if (SHOW=="sprayer_frame") mower_sprayer_frame();
if (SHOW=="sprayer_tank")  mower_sprayer_tank();
