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
module px_brain_box() c_brain()                          // COTS IP65 ~200x150x100
    rbox_full([210,160,105], 8);

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
module retrofit() {
    // 1) brain box on the seat pan
    translate([M_WHEELBASE*0.18, 0, M_SEAT_Z+25+52]) px_brain_box();

    // 2) actuators: from frame rail up to each lap-bar clamp point
    for (s=[-1,1]) {
        cp = lapbar_clamp_pos(s);                 // clamp point (world)
        anchor = [cp[0]-ACT_RETRACTED_L*0.6, cp[1], M_REAR_WHEEL_D/2+M_RAIL+40];
        translate(anchor)
            rotate([0,0, s*4])
                rotate([0, -atan2(cp[2]-anchor[2], ACT_RETRACTED_L), 0])
                    px_actuator();
    }

    // 3) GPS mast on the LEFT ROPS post, antenna high & clear
    rops_x = M_WHEELBASE*0.18 - SEAT_DEPTH/2 - 40 + 30;
    translate([rops_x, -M_FRAME_W/2, M_SEAT_Z+200]) {
        px_mast(560);
        translate([0,0,560]) px_gps_ant();
    }

    // 4) LiDAR on a front mast above the front cross member
    translate([M_WHEELBASE-60, 0, M_REAR_WHEEL_D/2+M_RAIL]) {
        px_mast(255);
        translate([0,0,255]) px_lidar();
    }

    // 5) camera just below the LiDAR, looking forward
    translate([M_WHEELBASE-30, 0, M_REAR_WHEEL_D/2+M_RAIL+180])
        rotate([0,15,0]) px_camera();

    // 6) e-stop on the right frame rail, slap-reachable
    translate([M_WHEELBASE*0.05, M_FRAME_W/2+30, M_REAR_WHEEL_D/2+M_RAIL]) px_estop();
}

mower(lap_angle=6);
retrofit();
