// SPDX-License-Identifier: MIT
// ============================================================================
//  FORWARD-FACING CAMERA MOUNT  —  Raspberry Pi Camera Module 3
//  Tilt-adjustable cradle for the autonomous zero-turn mower's vision camera.
//  Two printed parts:
//    A) camera_cradle — faceplate the Pi Cam 3 bolts behind, sun hood + drip
//                        lip, ribbon slot, and a serrated tilt knuckle.
//    B) camera_base   — base bracket with the mating serrated knuckle; mounts
//                        to a flat surface (M4 slots) OR a 20mm tube (clamp).
//  The two knuckles clamp together on a single M4 bolt: loosen, set pitch
//  (+/-30 deg in 15 deg detents via the meshing radial serrations), retighten.
//  PRINT: PETG/ASA (UV + heat tolerant outdoors), 3+ walls, 30%+ infill.
//
//  WEATHERPROOFING NOTE  -------------------------------------------------------
//  The Pi Camera Module 3 is NOT waterproof. This cradle only shades and aims
//  it. For wet-weather running, pair the cradle with a clear film / printed
//  visor over the lens window (the hood lip is sized to capture a stick-on
//  protector), and keep the small drip lip below the window so rain running
//  down the faceplate sheds clear of the lens instead of beading on it.
// ----------------------------------------------------------------------------
include <utils.scad>

// ---- Mount-option flag -----------------------------------------------------
TUBE_MOUNT = false;   // false = flat foot w/ M4 slots (default); true = 20mm tube half-clamp

// ---- Cradle dimensions -----------------------------------------------------
WALL       = 3;                 // shroud / structural wall
FACE_T     = 3;                 // faceplate thickness (lens window pierces this)
PW         = CAM_L + 2*WALL;    // faceplate width  (X)
PH         = CAM_W + 2*WALL;    // faceplate height (Y)
WINDOW     = 14;                // square lens window opening (Pi Cam 3 lens ~ 12.4mm)
RIBBON_W   = 16;                // ribbon-cable exit slot width (bottom of pocket)

// ---- Sun hood + drip lip ---------------------------------------------------
HOOD_LEN   = 16;                // how far the hood projects forward (+Z)
HOOD_T     = 2.5;               // hood / fin wall thickness
LIP_T      = 2;                 // drip lip thickness
LIP_LEN    = 4;                 // drip lip forward projection

// ---- Tilt knuckle (serrated face-spline hinge) -----------------------------
HINGE_OD   = 18;                // knuckle disc diameter
HT         = 6;                 // each knuckle disc thickness
SERR_N     = 48;                // serration teeth count -> 15 deg mesh detents
SERR_D     = 0.7;              // serration tooth height (shallow radial teeth)
SERR_ID    = M4_CLEAR + 3;      // inner dia of the serration ring (clears the bolt)
ARM        = 26;                // pivot-to-faceplate-centre distance (sets tilt axis)

// ---- Base bracket / foot ---------------------------------------------------
FOOT_W     = 44;                // flat foot width  (X)
FOOT_L     = 50;                // flat foot length (Z, fore-aft)
FOOT_T     = 5;                 // flat foot thickness (Y)
FOOT_Y     = -30;              // foot top plane below the pivot
SLOT_LEN   = 12;                // M4 mounting-slot travel

// ============================================================================
//  SHARED:  serrated face-spline knuckle
//  Radial castellated teeth on one disc face. Two identical discs pressed
//  together by the M4 bolt interlock and resist rotation -> holds tilt angle.
// ============================================================================
module serration_ring(od, id, n, depth) {
    a = 360/n;
    linear_extrude(depth)
        difference() {
            union() {
                for (i = [0 : 2 : n-1]) rotate([0, 0, i*a])
                    polygon([[0, 0],
                             [od/2*cos(-a/2), od/2*sin(-a/2)],
                             [od/2*cos( a/2), od/2*sin( a/2)]]);
            }
            circle(d = id);
        }
}

// Knuckle disc: axis = local +Z, body z=0..HT, serrations raised on the +Z face,
// M4 bolt bore through the centre.
module hinge_disc() {
    difference() {
        union() {
            cylinder(d = HINGE_OD, h = HT);
            translate([0, 0, HT - EPS]) serration_ring(HINGE_OD, SERR_ID, SERR_N, SERR_D);
        }
        translate([0, 0, -EPS]) cylinder(d = M4_CLEAR, h = HT + SERR_D + 2*EPS);
    }
}

// ============================================================================
//  A) CAMERA CRADLE
// ============================================================================

// Forward sun hood: a 3-sided shade (roof + two side fins) open at the front
// and bottom so the lens sees forward but is shaded from overhead + side glare.
module hood() {
    ww     = WINDOW + 2*WALL + 4;        // hood span (X)
    side_h = WINDOW/2 + WALL + 2;        // how far the side fins drop from the top edge
    topy   = PH/2;                       // top edge of the faceplate
    // roof
    translate([-ww/2, topy - HOOD_T, FACE_T - EPS]) cube([ww, HOOD_T, HOOD_LEN]);
    // side fins
    for (s = [-1, 1])
        translate([s*ww/2 - (s > 0 ? HOOD_T : 0), topy - side_h, FACE_T - EPS])
            cube([HOOD_T, side_h, HOOD_LEN*0.8]);
}

// Small drip lip below the window: rain running down the face drips off here
// instead of crossing the lens.
module drip_lip() {
    lw = WINDOW + 4;
    translate([-lw/2, -(WINDOW/2 + 2) - LIP_T, FACE_T - EPS]) cube([lw, LIP_T, LIP_LEN]);
}

// The faceplate, built centred at the origin (front face toward +Z).
module cradle_faceplate() {
    difference() {
        union() {
            // base faceplate
            rbox([PW, PH, FACE_T], 3);
            // PCB pocket / shroud behind the plate (camera body sits in here)
            translate([0, 0, -CAM_H])
                difference() {
                    rbox([PW, PH, CAM_H + EPS], 3);
                    translate([0, 0, -EPS])
                        rbox([CAM_L + CLEAR_FIT, CAM_W + CLEAR_FIT, CAM_H + 2*EPS], 1);
                }
            hood();
            drip_lip();
        }
        // lens window (through plate + pocket)
        translate([0, 0, -CAM_H - EPS])
            linear_extrude(CAM_H + FACE_T + 2*EPS) square(WINDOW, center = true);
        // 4 camera mount holes (M2.5 self-tap into the plate)
        translate([0, 0, -EPS])
            hole_grid(CAM_HOLE_DX, CAM_HOLE_DY)
                cylinder(d = CAM_HOLE_D, h = FACE_T + 2*EPS);
        // ribbon-cable exit slot through the bottom shroud wall
        translate([0, -PH/2, -CAM_H/2])
            cube([RIBBON_W, 4*WALL, CAM_H], center = true);
    }
}

// Web tying the tilt knuckles up to the bottom of the faceplate.
module cradle_neck() {
    hull() {
        translate([-13, -4, 0]) cube([26, 8, FACE_T]);                 // across the knuckles
        translate([-13, ARM - PH/2, 0]) cube([26, 8, FACE_T]);         // faceplate bottom edge
    }
}

module camera_cradle() {
    proxy() {
        translate([0, ARM, 0]) cradle_faceplate();
        // tilt knuckles, serrated faces pointing outward to meet the base ears
        translate([ 7, 0, 0]) rotate([0,  90, 0]) hinge_disc();   // right, serr toward +X
        translate([-7, 0, 0]) rotate([0, -90, 0]) hinge_disc();   // left,  serr toward -X
        cradle_neck();
    }
}

// ============================================================================
//  B) CAMERA BASE BRACKET
// ============================================================================

// Yoke connecting the two base ears and carrying the load down to the mount.
module base_post() {
    ph = 10;   // post thickness in Z
    hull() {
        translate([-19.3, -4, -ph/2]) cube([38.6, 8, ph]);                // across the ears
        translate([-FOOT_W/2 + 4, FOOT_Y, -ph/2]) cube([FOOT_W - 8, 10, ph]); // down to the foot
    }
}

// Elongated slot bored through +Y (foot thickness), running along Z.
module slot_y(d, len, th) {
    hull() {
        translate([0, 0, -len/2]) rotate([-90, 0, 0]) cylinder(d = d, h = th);
        translate([0, 0,  len/2]) rotate([-90, 0, 0]) cylinder(d = d, h = th);
    }
}

// Flat foot: bolts down to a flat deck/plate via two fore-aft M4 slots.
module flat_foot() {
    translate([0, FOOT_Y - FOOT_T, 0])
        difference() {
            translate([-FOOT_W/2, 0, -FOOT_L/2]) cube([FOOT_W, FOOT_T, FOOT_L]);
            for (s = [-1, 1])
                translate([s*FOOT_W*0.28, -EPS, 0]) slot_y(M4_CLEAR, SLOT_LEN, FOOT_T + 2*EPS);
        }
}

// 20mm tube half-clamp (saddle). The lower half; pair with a printed strap or
// U-bolt through the two flanking M4 holes to capture a 20mm tube (axis = X).
module tube_saddle() {
    td   = 20 + CLEAR_FIT;        // 20mm tube + sliding fit
    axl  = 30;                    // length along the tube axis (X)
    bodyz = td + 2*4;             // saddle body span (Z)
    earw  = 9;                    // bolt-ear width each side
    cy    = FOOT_Y - td/2 - 4;    // tube centreline Y
    difference() {
        union() {
            // central saddle body (material only above the tube centre)
            translate([-axl/2, cy - 2, -bodyz/2]) cube([axl, FOOT_Y - (cy - 2), bodyz]);
            // strap-bolt ears each side
            for (s = [-1, 1])
                translate([-axl/2, cy - 2, s > 0 ? bodyz/2 : -bodyz/2 - earw])
                    cube([axl, 8, earw]);
        }
        // half-bore for the tube
        translate([0, cy, 0]) rotate([0, 90, 0]) cylinder(d = td, h = axl + 2*EPS, center = true);
        // M4 strap bolts (axis = Y) through the ears
        for (s = [-1, 1])
            translate([0, cy - 2, s*(bodyz/2 + earw/2)])
                rotate([-90, 0, 0]) cylinder(d = M4_CLEAR, h = 20, center = true);
    }
}

module camera_base() {
    proxy() {
        // mating tilt ears, serrated faces pointing inward toward the cradle knuckles
        translate([ 19.3, 0, 0]) rotate([0, -90, 0]) hinge_disc();   // right, serr toward -X
        translate([-19.3, 0, 0]) rotate([0,  90, 0]) hinge_disc();   // left,  serr toward +X
        base_post();
        if (TUBE_MOUNT) tube_saddle(); else flat_foot();
    }
}

// ============================================================================
//  PRINT PLATES  (exposed entry points)
// ============================================================================
module PRINT_camera_cradle() camera_cradle();
module PRINT_camera_base()   camera_base();

// ---- bottom preview: both parts laid out side by side ----------------------
if (is_undef(PREVIEW_OFF)) {
    PRINT_camera_cradle();
    translate([70, 0, 0]) PRINT_camera_base();
}
