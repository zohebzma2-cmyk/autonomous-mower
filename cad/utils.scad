// SPDX-License-Identifier: MIT
// ============================================================================
//  SHARED UTILITY MODULES  —  used by every component file
//  include <params.scad> before using these.
// ============================================================================
include <params.scad>

EPS = 0.01;
inf = 1000;

// ---- Rounded primitives ----------------------------------------------------
module rrect(size, r) {           // 2D rounded rectangle, centered
    w = size[0]; h = size[1];
    offset(r) offset(-r) square([w, h], center = true);
}
module rbox(size, r) {            // 3D rounded box (vertical edges), centered XY
    w = size[0]; h = size[1]; d = size[2];
    linear_extrude(d) rrect([w, h], r);
}
module rbox_full(size, r) {       // 3D box rounded on all edges (minkowski)
    w = size[0]-2*r; h = size[1]-2*r; d = size[2]-2*r;
    minkowski() { cube([w, h, d], center=true); sphere(r); }
}

// ---- Fastener features -----------------------------------------------------
// Heat-set insert boss: a pillar with a pilot hole for a brass threaded insert.
module heatset_boss(d_pilot=HEATSET_M3_D, l=HEATSET_M3_L, boss_d=7, h=10) {
    difference() {
        cylinder(d=boss_d, h=h);
        translate([0,0,h-l]) cylinder(d=d_pilot, h=l+EPS);
    }
}
// Countersunk / counterbored through hole punched downward from z=h.
module screw_hole(d=M3_CLEAR, head_d=M3_HEAD, head_h=3, h=20, counterbore=true) {
    translate([0,0,-EPS]) cylinder(d=d, h=h+2*EPS);
    if (counterbore) translate([0,0,h-head_h]) cylinder(d=head_d, h=head_h+EPS);
}
// Hex nut trap (for captive M3/M4 nuts), opening upward.
module nut_trap(af=M3_NUT_AF, th=M3_NUT_TH, h=20) {
    cylinder(d=af/cos(30)+SLOP, h=th+EPS, $fn=6);
    cylinder(d=M3_CLEAR, h=h);
}
// Rectangular hole pattern: place children at 4 corners of dx x dy.
module hole_grid(dx, dy) {
    for (x=[-dx/2, dx/2], y=[-dy/2, dy/2]) translate([x,y,0]) children();
}
// Bolt-circle pattern.
module bolt_circle(pcd, n) {
    for (i=[0:n-1]) rotate([0,0,i*360/n]) translate([pcd/2,0,0]) children();
}

// ---- Tube clamp  (THE key reusable piece for ANY ZTR lap bar) ---------------
// A two-piece split clamp. `half`: "top" or "bottom". Handles round OR oval.
// Produces a clamp body of given block size with a bore matching the tube,
// plus two M4 ears to bolt the halves together.
module tube_clamp_profile() {
    if (LAP_BAR_IS_OVAL)
        resize([LAP_BAR_OVAL_W+SLOP, LAP_BAR_OVAL_H+SLOP]) circle(d=10);
    else
        circle(d=LAP_BAR_TUBE_OD+SLOP);
}
module tube_clamp(half="bottom", block=[40,40], ear=14, t=8) {
    bore_w = LAP_BAR_IS_OVAL ? LAP_BAR_OVAL_W : LAP_BAR_TUBE_OD;
    bw = block[0]; bl = block[1];
    sign = (half=="top") ? 1 : -1;
    difference() {
        union() {
            // main block
            linear_extrude(t) rrect([bw, bl], 3);
            // bolt ears on both sides
            for (s=[-1,1]) translate([s*(bw/2+ear/2-2),0,0])
                linear_extrude(t) rrect([ear, bl], 3);
        }
        // tube bore (only the half on this piece's side of centerline)
        translate([0,0,-EPS])
            linear_extrude(t+2*EPS)
                intersection() {
                    tube_clamp_profile();
                    translate([-bw, (sign<0?-bl:0), 0]) square([2*bw, bl]); // half
                }
        // full bore relief so the two halves clear the tube
        translate([0,0,-EPS]) linear_extrude(t+2*EPS) tube_clamp_profile();
        // clamp bolts through the ears
        for (s=[-1,1]) translate([s*(bw/2+ear/2-2),0,t/2]) rotate([90,0,0])
            cylinder(d=M4_CLEAR, h=bl+2*EPS, center=true);
    }
}

// ---- Bed-split joinery  (parts bigger than 145mm) --------------------------
// Dovetail tongue (add to piece A) / pocket (subtract from piece B) + bolt.
module dovetail_tongue(w=SPLIT_DOVETAIL_W, h=SPLIT_DOVETAIL_H, t=10) {
    linear_extrude(t)
        polygon([[-w/2,0],[w/2,0],[w/2-h*0.4,h],[-w/2+h*0.4,h]]);
}
module split_bolt_hole(t=10) {           // through-bolt joining two halves
    rotate([90,0,0]) cylinder(d=SPLIT_BOLT_D, h=inf, center=true);
}

// ---- Enclosure features ----------------------------------------------------
module gasket_groove(path_w, path_l) {   // square-path groove for cord gasket
    difference() {
        rrect([path_w, path_l], 5);
        offset(-GASKET_GROOVE_W) rrect([path_w, path_l], 5);
    }
}
module cable_gland_hole(d=CABLE_GLAND_D) { cylinder(d=d, h=inf, center=true); }

// ---- Standoff (PCB mount pillar with heat-set top) -------------------------
module standoff(h=PI5_STANDOFF, d=6, pilot=HEATSET_M3_D, pilot_l=4) {
    difference() {
        cylinder(d=d, h=h);
        translate([0,0,h-pilot_l]) cylinder(d=pilot, h=pilot_l+EPS);
    }
}

// ---- A simple ghost() wrapper to show vendor meshes faintly -----------------
module ghost() { color([0.6,0.6,0.65,0.35]) children(); }
module proxy() { color([0.30,0.55,0.85,0.85]) children(); }   // our printed parts
module mower_mat() { color([0.70,0.11,0.10]) children(); }     // Gravely red body
module mower_blk() { color([0.09,0.09,0.10]) children(); }     // black — wheels, seat, lap bars

// import a vendor STL if present, else render a labelled proxy box of dims.
module vendor_or_proxy(file, dims, label="part") {
    // OpenSCAD can't test file existence; pass use_vendor=true once downloaded.
    proxy() cube(dims, center=true);
}

// ---- BRIM (baked bed-adhesion flange) --------------------------------------
// Drops a part so its base sits at z=0 (caller passes the part's true min-z),
// then welds a single-layer brim of width `w` around its first-layer footprint.
// Output STL is print-ready WITH a brim — do NOT also enable a slicer brim.
BRIM_LAYER = 0.2;     // one layer tall (matches a 0.2mm print)
module add_brim(w=5, minz=0, layer=BRIM_LAYER) {
    translate([0,0,-minz]) children();                       // part, base on bed
    linear_extrude(layer)                                    // the brim ring/flange
        offset(w)
            projection(cut=true)                             // cut=true slices at global z=0
                translate([0,0,-(minz + layer/2)]) children(); // base sits 0.1 BELOW z=0 -> slice ~mid first layer
}
