// ============================================================================
//  MOWER MOCK-UP  —  parametric zero-turn body (reference: Gravely ZT X 52)
//  VISUALIZATION CONTEXT ONLY — not printed. Lets us place every retrofit
//  component on the machine and check clearance, reach, and sightlines.
//
//  Published envelope (allmachines, ZT X 52 / Kohler 915256):
//    overall 1968 L x 1610 W x 1039 H mm · deck 1321 (52") · rear 20x10-8 ·
//    front 11x6-5 · 615 lb.  Tyres, deck, seat height and overall W/H below
//    match those figures; the WHEELBASE is a [MEASURE] approximation, so the
//    model reads ~270 mm shorter overall than the spec sheet until measured.
//  Retrofit reference points (frame rails, seat origin, lap-bar pivot/clamp)
//  are UNCHANGED from prototype-v1 — every bracket still aligns.
// ============================================================================
include <utils.scad>

// ---- Mower envelope (ZT X 52) ----------------------------------------------
M_DECK_W      = 1321;   // 52" cutting deck width (spec)
M_DECK_D      = 720;    // deck front-back
M_DECK_Z      = 90;     // ground clearance of deck shell
M_DECK_H      = 110;    // deck shell height
M_FRAME_L     = 1500;   // main frame rail length
M_FRAME_W     = 560;    // rail centre-centre  (~ lap bar spacing)
M_RAIL        = 50;     // square tube size
M_REAR_WHEEL_D= 508;    // ZT X 52: 20x10-8 → 20" dia (spec)
M_REAR_WHEEL_W= 254;    // 10" wide (spec)
M_FRONT_CASTER_D = 279; // 11x6-5 → 11" dia (spec)
M_FRONT_CASTER_W = 152; // 6" wide (spec)
M_WHEELBASE   = 1170;   // derived: tail + wheelbase + caster radius = published 1968
                        // overall length (was 900, which jammed the deck into the
                        // tyres). Confirm with a tape measure on the real machine.
M_SEAT_Z      = 580;    // seat pan height off ground
M_ENGINE      = [430, 480, 360];
M_HAS_ROPS    = false;  // ZT X 52 has NO factory ROPS (residential) → GPS mast mounts to seat frame
M_ROPS_H      = 1100;   // (only used if a ROPS is fitted)

M_TAIL        = -658.5; // rear guard-hoop extreme (engine overhang behind axle)
M_DECK_X      = 620;    // deck centre — rear edge clears the 508 tyres (254+6mm),
                        // front edge + rollers clear the caster swing by ~50mm
M_DECK_SHELL  = 1400;   // deck SHELL width (wider than the 1321 cutting width)
M_CHUTE_L     = 264;    // discharge deflector length; shell + deflector = 1610 spec width
M_SEATBACK_TOP= 1039;   // spec overall height = top of the seat back

// Blades — 52" triple spindle: 3 x 18" (460mm) blades, 63.5 wide, 5.2 thick
BLADE_L = 460; BLADE_W = 63.5; BLADE_T = 5.2; BLADE_HOLE = 15.9;
function blade_pos(i) = [M_DECK_X, i*M_DECK_W*0.3, 112];   // i in -1/0/1

// Ground = z0. Rear axle centred at x=0; front casters forward (+X).

// ---- envelope self-check (echoed on every render) ---------------------------
ENV_L = (M_WHEELBASE + M_FRONT_CASTER_D/2) - M_TAIL;               // guard tail → caster front
ENV_W = M_DECK_SHELL/2 + (M_DECK_SHELL/2 - 6 + M_CHUTE_L*cos(35)); // shell edge → deflector tip
echo(str("ENVELOPE  L=", ENV_L, " (spec 1968; wheelbase derived — tape-measure to confirm)",
         "  W=", ENV_W, " (spec 1610)",
         "  H=", M_SEATBACK_TOP, " (spec 1039)",
         "  deck=", M_DECK_W, " (spec 1321)"));

// ---- smooth bent tube through a point list ---------------------------------
module bent_tube(pts, d) {
    for (i=[0:len(pts)-2]) hull() {
        translate(pts[i])   sphere(d=d);
        translate(pts[i+1]) sphere(d=d);
    }
}

// ============================================================================
//  WHEELS — moulded turf tyres (rounded carcass + chevron lugs) on red rims
// ============================================================================
module tire(d, w, lugs=0) {                 // axis = local Z
    R = w*0.16;  ri = d*0.30;
    rotate_extrude($fn=64)                                     // rounded carcass
        translate([0, -w/2]) offset(R)
            translate([ri+R, R]) square([d/2 - ri - 2*R, w - 2*R]);
    if (lugs>0) for (i=[0:lugs-1]) rotate([0,0,i*360/lugs])    // chevron lugs
        for (s=[-1,1]) translate([d/2-7, 0, s*w*0.22])
            rotate([s*28,0,0]) cube([10, 15, w*0.42], center=true);
    if (lugs==0) for (k=[-1,0,1])                              // caster ribs
        translate([0,0,k*w*0.28]) rotate_extrude($fn=48)
            translate([d/2-2, 0]) circle(d=7);
}

module mower_wheel(d, w, lugs=0) rotate([90,0,0]) tire(d, w, lugs);

module mower_wheels() mower_blk() {
    // rear drive tyres — turf tread
    for (y=[-(M_FRAME_W/2+M_REAR_WHEEL_W/2+30), (M_FRAME_W/2+M_REAR_WHEEL_W/2+30)])
        translate([0, y, M_REAR_WHEEL_D/2]) mower_wheel(M_REAR_WHEEL_D, M_REAR_WHEEL_W, lugs=22);
    // front caster tyres — smooth ribbed
    for (y=[-(M_FRAME_W/2-40), (M_FRAME_W/2-40)])
        translate([M_WHEELBASE, y, M_FRONT_CASTER_D/2])
            mower_wheel(M_FRONT_CASTER_D, M_FRONT_CASTER_W, lugs=0);
}

// Gravely-red pressed-steel rims + hubs + lug bolts  [red]
module rim(d, w) rotate([90,0,0]) {
    cylinder(d=d*0.52, h=w*0.62, center=true);                 // rim barrel
    cylinder(d=d*0.24, h=w*0.72, center=true);                 // hub
    for (i=[0:4]) rotate([0,0,i*72]) translate([d*0.16,0,0])   // 5 lug bolts
        cylinder(d=16, h=w*0.76, center=true);
}
module mower_rims() mower_mat() {
    for (y=[-(M_FRAME_W/2+M_REAR_WHEEL_W/2+30), (M_FRAME_W/2+M_REAR_WHEEL_W/2+30)])
        translate([0, y, M_REAR_WHEEL_D/2]) rim(M_REAR_WHEEL_D, M_REAR_WHEEL_W);
    for (y=[-(M_FRAME_W/2-40), (M_FRAME_W/2-40)])
        translate([M_WHEELBASE, y, M_FRONT_CASTER_D/2]) rim(M_FRONT_CASTER_D, M_FRONT_CASTER_W);
}

// ============================================================================
//  FRAME — rails, cross members, caster arms, nose plate, rear guard hoop
// ============================================================================
module mower_frame() mower_mat() {
    // two main rails — rear datum to just behind the caster posts
    for (y=[-M_FRAME_W/2, M_FRAME_W/2])
        translate([-550, y, M_REAR_WHEEL_D/2])
            cube([M_WHEELBASE+640, M_RAIL, M_RAIL]);
    // rear cross member (engine deck / actuator anchor rail)
    translate([-500, 0, M_REAR_WHEEL_D/2])
        cube([M_RAIL, M_FRAME_W+M_RAIL, M_RAIL], center=false);
    // front cross member
    translate([M_WHEELBASE-100, 0, M_REAR_WHEEL_D/2])
        cube([M_RAIL, M_FRAME_W+M_RAIL, M_RAIL], center=false);
    // caster arms — rail nose down to each swivel-post top plate
    for (s=[-1,1]) bent_tube([[M_WHEELBASE+45, s*(M_FRAME_W/2-40), M_REAR_WHEEL_D/2+20],
                              [M_WHEELBASE,    s*(M_FRAME_W/2-40), M_FRONT_CASTER_D/2+150]], 44);
    // nose plate between the arms
    translate([M_WHEELBASE-12, 0, M_FRONT_CASTER_D/2+165])
        rotate([0,14,0]) rbox_full([90, M_FRAME_W-60, 18], 8);
    // rear engine-guard hoop
    bent_tube([[-560,-260,M_REAR_WHEEL_D/2], [M_TAIL,-260,430], [M_TAIL,260,430], [-560,260,M_REAR_WHEEL_D/2]], 34);
}

// ============================================================================
//  DECK — tapered shell + top plate + hinged discharge deflector  [red]
// ============================================================================
module mower_deck() mower_mat() {
    dx = M_DECK_X;
    difference() {                                                 // tapered shell…
        hull() {
            translate([dx-70, 0, M_DECK_Z+M_DECK_H/2]) rbox_full([M_DECK_D-140, M_DECK_SHELL, M_DECK_H], 20);
            translate([dx+M_DECK_D/2-45, 0, M_DECK_Z+M_DECK_H*0.36]) rbox_full([90, M_DECK_SHELL*0.86, M_DECK_H*0.72], 20);
        }
        hull() {                                                   // …hollowed underneath (blades live here)
            translate([dx-70, 0, M_DECK_Z+M_DECK_H/2-16]) rbox_full([M_DECK_D-176, M_DECK_SHELL-36, M_DECK_H], 20);
            translate([dx+M_DECK_D/2-45, 0, M_DECK_Z+M_DECK_H*0.36-16]) rbox_full([64, M_DECK_SHELL*0.86-36, M_DECK_H*0.72], 20);
        }
    }
    // hinged discharge deflector (down position) — sets overall width to spec
    translate([dx, M_DECK_SHELL/2-6, M_DECK_Z+M_DECK_H-14]) rotate([-35,0,0])
        translate([0, M_CHUTE_L/2, -5]) rbox([300, M_CHUTE_L, 10], 14);
}

// Cutting-deck hardware: spindles, belt cover, anti-scalp rollers  [black]
module mower_deck_details() mower_blk() {
    dz = M_DECK_Z + M_DECK_H;  dx = M_DECK_X;
    for (y=[-M_DECK_W*0.3, 0, M_DECK_W*0.3]) translate([dx, y, dz]) {  // spindle housings
        cylinder(d=72, h=42);
        translate([0,0,42]) cylinder(d=30, h=10);                      // grease cap
    }
    for (i=[-1,0,1]) {                                                  // spindle shafts + blade bolts
        p = blade_pos(i);
        translate([p[0], p[1], p[2]]) cylinder(d=25.4, h=dz-p[2]+2);
        translate([p[0], p[1], p[2]-10]) cylinder(d=32, h=10, $fn=6);   // hex blade bolt
    }
    translate([dx-M_DECK_D*0.32, 0, dz+10])                            // belt / pulley cover
        rbox_full([100, M_DECK_W*0.78, 26], 12);
    for (y=[-M_DECK_W*0.34, M_DECK_W*0.34])                            // anti-scalp rollers
        translate([dx+M_DECK_D*0.46, y, M_DECK_Z-6]) rotate([90,0,0]) cylinder(d=54,h=26,center=true);
}

// ============================================================================
//  BLADES — one 18" high-lift blade, modeled CENTERED AT ORIGIN so the GLB
//  can place three instances as separate nodes and spin them about local Z.
// ============================================================================
module mower_blade() {
    difference() {
        union() {
            hull() for (s=[-1,1]) translate([s*(BLADE_L/2-BLADE_W/2), 0, 0])   // bar
                cylinder(d=BLADE_W, h=BLADE_T);
            for (s=[-1,1]) translate([s*(BLADE_L/2-42), -s*(BLADE_W/2-9), BLADE_T])  // lift wings
                rotate([s*38,0,0]) translate([0,0,1]) rbox([84, 26, 14], 6);
        }
        translate([0,0,-EPS]) cylinder(d=BLADE_HOLE, h=BLADE_T+2*EPS);          // centre hole
        for (s=[-1,1]) translate([s*(BLADE_L/2-30), s*(BLADE_W/2-2), BLADE_T*0.45])  // cutting-edge bevels
            rotate([s*28,0,0]) translate([0,0,10]) cube([140, 30, 20], center=true);
    }
}
module blade_steel() color([0.72,0.73,0.76]) children();
module mower_blades_placed()                       // static preview placement
    for (i=[-1,0,1]) translate(blade_pos(i)) rotate([0,0, i*38+18])
        blade_steel() mower_blade();

// ============================================================================
//  ENGINE — rounded hood + louvres, pull start, muffler, air filter
// ============================================================================
module mower_engine() mower_mat() {
    ex = -M_FRAME_L/2+200+M_ENGINE[0]/2; ez = M_REAR_WHEEL_D/2+M_RAIL;
    translate([ex, 0, ez]) hull() {                               // tapered hood
        translate([0,0,M_ENGINE[2]*0.30]) rbox_full([M_ENGINE[0], M_ENGINE[1], M_ENGINE[2]*0.60], 26);
        translate([-18,0,M_ENGINE[2]*0.88]) rbox_full([M_ENGINE[0]*0.72, M_ENGINE[1]*0.72, 70], 30);
    }
}
module mower_engine_detail() mower_blk() {
    ex = -M_FRAME_L/2+200+M_ENGINE[0]/2; ez = M_REAR_WHEEL_D/2+M_RAIL;
    // cooling louvres across the hood top
    for (x=[-3:3]) translate([ex-18+x*36, 0, ez+M_ENGINE[2]*0.88+38])
        rbox_full([16, M_ENGINE[1]*0.58, 14], 5);
    // recoil pull-start housing + rope handle (rear face, low right)
    translate([ex-M_ENGINE[0]/2-2, 130, ez+M_ENGINE[2]*0.18]) rotate([0,-90,0]) {
        cylinder(d=110, h=16);
        translate([0,0,10]) cylinder(d=34, h=8);
    }
    translate([ex-M_ENGINE[0]/2-16, 130, ez+M_ENGINE[2]*0.18+66]) rbox_full([14, 60, 24], 6);
    // muffler + heat shield
    translate([ex, M_ENGINE[1]/2+22, ez+M_ENGINE[2]*0.4]) rotate([90,0,0]) cylinder(d=62,h=95);
    translate([ex, M_ENGINE[1]/2+30, ez+M_ENGINE[2]*0.4+40]) rbox([120, 90, 8], 12);
    // air-filter canister + intake elbow (Kohler 7000 style)
    translate([ex, 0, ez+M_ENGINE[2]+26]) rbox_full([120,150,56],22);
    translate([ex, -70, ez+M_ENGINE[2]+8]) rotate([90,0,0]) cylinder(d=40, h=50);
    // spin-on oil filter, low on the left flank
    translate([ex+60, -M_ENGINE[1]/2-14, ez+70]) rotate([90,0,0]) cylinder(d=76, h=90);
    // dipstick tube (the yellow ring handle is in the accent group)
    translate([ex-80, -M_ENGINE[1]/2-8, ez+90]) rotate([12,0,0]) cylinder(d=14, h=170);
}

// Yellow service touch-points — the bits a Kohler owner actually grabs  [accent]
module mower_accents() color([0.93,0.76,0.13]) {
    ex = -M_FRAME_L/2+200+M_ENGINE[0]/2; ez = M_REAR_WHEEL_D/2+M_RAIL;
    // dipstick ring handle atop its tube
    translate([ex-80, -M_ENGINE[1]/2-8, ez+90]) rotate([12,0,0]) translate([0,0,170])
        rotate([0,90,0]) rotate_extrude($fn=32) translate([16,0]) circle(d=9);
    // oil-fill cap beside the tube
    translate([ex-30, -M_ENGINE[1]/2+30, ez+M_ENGINE[2]*0.72]) cylinder(d=34, h=14);
    // PTO knob on the dash (yellow pull-up knob, like the real one)
    translate([M_WHEELBASE*0.34, 86, M_SEAT_Z+26]) { cylinder(d=26, h=16); translate([0,0,16]) cylinder(d=34, h=12); }
}

// ============================================================================
//  BRANDING — raised lettering (geometry, so it survives STL→GLB)  [black]
// ============================================================================
BRAND_FONT = "Helvetica:style=Bold";
module raised_text(t, size, h=2.2) linear_extrude(h) text(t, size=size, font=BRAND_FONT, halign="center", valign="center");

module mower_branding() mower_blk() {
    ex = -M_FRAME_L/2+200+M_ENGINE[0]/2; ez = M_REAR_WHEEL_D/2+M_RAIL;
    // rear badge plate + GRAVELY wordmark (sits proud of the curved hood)
    translate([ex-M_ENGINE[0]/2-8, 0, ez+M_ENGINE[2]*0.55]) rotate([0,90,0]) rbox([84, 340, 10], 10);
    translate([ex-M_ENGINE[0]/2-8, 0, ez+M_ENGINE[2]*0.55]) rotate([90,0,-90]) raised_text("GRAVELY", 40);
    // GRAVELY along both deck side skirts (rear full-width band of the shell)
    for (s=[-1,1]) translate([M_DECK_X-180, s*(M_DECK_SHELL/2-0.5), M_DECK_Z+M_DECK_H*0.52])
        rotate([0,0, s>0 ? 180 : 0]) rotate([90,0,0]) raised_text("GRAVELY", 42);
    // ZT X 52 on the deck nose
    translate([M_DECK_X+M_DECK_D/2+0.5, 0, M_DECK_Z+M_DECK_H*0.40]) rotate([90,0,90]) raised_text("ZT X 52", 30);
}

// ============================================================================
//  OPERATOR STATION — contoured seat, frame, dash, tanks, foot deck
// ============================================================================
module mower_seat() mower_blk() {
    sx = M_WHEELBASE*0.18;
    // pan cushion (waterfall front) + side bolsters
    translate([sx, 0, M_SEAT_Z-5]) rbox_full([SEAT_DEPTH, SEAT_WIDTH, 80], 30);
    for (s=[-1,1]) translate([sx-20, s*(SEAT_WIDTH/2-48), M_SEAT_Z+26])
        rbox_full([SEAT_DEPTH*0.78, 92, 64], 26);
    // high back cushion + bolsters + headrest (top = spec height 1039)
    translate([sx-SEAT_DEPTH/2+42, 0, M_SEAT_Z+238]) rotate([0,-12,0]) rbox_full([82, SEAT_WIDTH-70, 420], 30);
    for (s=[-1,1]) translate([sx-SEAT_DEPTH/2+58, s*(SEAT_WIDTH/2-62), M_SEAT_Z+220])
        rotate([0,-12,0]) rbox_full([72, 100, 330], 24);
    translate([sx-SEAT_DEPTH/2-8, 0, M_SEATBACK_TOP-36]) rotate([0,-12,0]) rbox_full([72, 250, 80], 26);
    // armrest pads on posts
    for (s=[-1,1]) translate([sx+16, s*(SEAT_WIDTH/2+42), M_SEAT_Z+168]) {
        rbox_full([250, 76, 42], 18);
        translate([-70, 0, -70]) rbox_full([26, 26, 110], 8);
    }
}

module mower_seatframe() mower_blk() {
    bx = M_WHEELBASE*0.18 - SEAT_DEPTH/2 - 26;
    for (y=[-SEAT_WIDTH/2+22, SEAT_WIDTH/2-22]) translate([bx, y, M_SEAT_Z]) rbox_full([38,30,300],8);
}

// Control panel by the seat: panel, throttle + choke levers, key, PTO knob
module mower_dash() mower_blk() {
    dxp = M_WHEELBASE*0.34;
    translate([dxp, 0, M_SEAT_Z+12]) rbox_full([44,230,30],12);
    for (i=[-1,1]) translate([dxp, i*38, M_SEAT_Z+30]) rotate([0,-18,0]) {   // levers
        cylinder(d=8, h=54);
        translate([0,0,54]) sphere(d=18);
    }
    translate([dxp, -86, M_SEAT_Z+28]) cylinder(d=16, h=10);                 // key switch
    // (yellow PTO knob lives in mower_accents)
}

// Dual fuel tanks flanking the seat, with filler caps  [black]
module mower_fueltanks() mower_blk()
    for (y=[-(M_FRAME_W/2+42), (M_FRAME_W/2+42)]) translate([M_WHEELBASE*0.04, y, M_SEAT_Z-30]) {
        rbox_full([190,96,150],34);
        translate([46, 0, 78]) cylinder(d=52, h=18);
        translate([46, 0, 96]) cylinder(d=58, h=8);
    }

// Operator foot deck / floor pan (rounded)  [red]
module mower_footdeck() mower_mat()
    translate([M_WHEELBASE*0.55, 0, M_REAR_WHEEL_D/2+M_RAIL-12])
        rbox([340, M_FRAME_W+130, 16], 26);

// Rear tyre fenders — curved half-arch guards over the drive wheels  [red]
module mower_fenders() mower_mat()
    for (y=[-(M_FRAME_W/2+M_REAR_WHEEL_W/2+30), (M_FRAME_W/2+M_REAR_WHEEL_W/2+30)])
        translate([0, y, M_REAR_WHEEL_D/2]) rotate([90,0,0]) rotate([0,0,45])
            rotate_extrude(angle=115) translate([M_REAR_WHEEL_D/2+18,0,0])
                offset(4) square([M_REAR_WHEEL_W+8, 6], center=true);

// Front caster forks — swivel post + fork yoke each side of the wheel  [black]
module mower_casters() mower_blk()
    for (y=[-(M_FRAME_W/2-40), (M_FRAME_W/2-40)]) translate([M_WHEELBASE, y, 0]) {
        translate([0,0,M_FRONT_CASTER_D/2]) cylinder(d=24, h=140);        // swivel post
        translate([0,0,M_FRONT_CASTER_D/2+140]) rbox_full([60,70,16],6);  // top plate
        for (s=[-1,1]) hull() {                                           // fork yokes
            translate([0, s*(M_FRONT_CASTER_W/2+8), M_FRONT_CASTER_D/2+130]) sphere(d=34);
            translate([0, s*(M_FRONT_CASTER_W/2+8), M_FRONT_CASTER_D/2])   sphere(d=44);
        }
    }

module mower_rops() mower_mat() {
    bx = M_WHEELBASE*0.18 - SEAT_DEPTH/2 - 40;
    for (y=[-M_FRAME_W/2, M_FRAME_W/2])
        translate([bx, y, M_SEAT_Z]) cube([60, 60, M_ROPS_H]);
    translate([bx, 0, M_SEAT_Z+M_ROPS_H]) cube([60, M_FRAME_W+60, 60], center=false);
}

// ============================================================================
//  LAP BARS — bent tube with foam grip. angle: 0 = neutral; +fwd.
//  The vertical section below LAP_BAR_CLAMP_HEIGHT is IDENTICAL to prototype-v1
//  (straight Ø LAP_BAR_TUBE_OD) so the actuator clamps still land correctly.
// ============================================================================
module mower_lapbar(side=1, angle=0) mower_blk() {
    px = M_WHEELBASE*0.18 + SEAT_DEPTH/2 - 40;     // pivot x
    py = side*LAP_BAR_SPACING/2;
    pz = M_SEAT_Z - 60;                            // pivot z
    d  = LAP_BAR_TUBE_OD;
    translate([px, py, pz]) rotate([0, -angle, 0]) {
        cylinder(d=d, h=LAP_BAR_CLAMP_HEIGHT);                       // straight clamp section
        bent_tube([[0,0,LAP_BAR_CLAMP_HEIGHT],                       // inward + forward bends
                   [0,-side*62,LAP_BAR_CLAMP_HEIGHT+78],
                   [140,-side*62,LAP_BAR_CLAMP_HEIGHT+112]], d);
        hull() {                                                     // foam grip
            translate([48,-side*62,LAP_BAR_CLAMP_HEIGHT+90])  sphere(d=d+16);
            translate([140,-side*62,LAP_BAR_CLAMP_HEIGHT+112]) sphere(d=d+16);
        }
    }
}
// returns the world position of a lap-bar clamp point (for placing actuators)
function lapbar_clamp_pos(side) = [
    M_WHEELBASE*0.18 + SEAT_DEPTH/2 - 40,
    side*LAP_BAR_SPACING/2,
    (M_SEAT_Z - 60) + LAP_BAR_CLAMP_HEIGHT*0.75
];


// ============================================================================
//  ATTACHMENTS (Phase 3 — additive; see docs/DESIGN-LOG.md + docs/ATTACHMENTS.md)
//  Proxy-fidelity like the base machine: accurate envelopes + placements so
//  clearances and reach are honest. The base-machine envelope echo above is
//  UNCHANGED — attachments extend the machine and are echoed separately.
// ============================================================================
module attach_blk() color([0.10,0.10,0.11]) children();      // attachment steel/plastic
module attach_gray() color([0.35,0.37,0.40]) children();     // boom hardware
module attach_tank() color([0.93,0.76,0.13]) children();     // FIMCO poly tank (yellow)

// ---- power bagger (Gravely/Exmark dump-from-seat pattern) -------------------
BAG_X0 = -700;            // rack starts behind the guard hoop
BAG_X1 = -1150;           // rack rear extreme
module mower_bagger_frame() mower_mat() {                     // red rack + dump pivot
    for (y=[-200,200]) {
        bent_tube([[-560, y, M_REAR_WHEEL_D/2+20], [BAG_X0, y, 440], [BAG_X1+40, y, 440]], 36);
        bent_tube([[BAG_X1+60, y, 440], [BAG_X1+150, y, M_REAR_WHEEL_D/2+10]], 30);  // rear struts
    }
    translate([BAG_X1+40, 0, 440]) rotate([90,0,0]) cylinder(d=40, h=460, center=true); // dump torque tube
    translate([BAG_X0-10, 0, 440]) rotate([90,0,0]) cylinder(d=34, h=430, center=true); // front cross
}
module mower_bagger_bins() attach_blk() {   // Gravely Power Bagger pattern, done properly
    // deck-driven blower volute at the discharge corner (the kit belts it off the deck)
    translate([430, 770, 230]) {
        rotate([0,90,0]) cylinder(d=200, h=95, center=true);            // volute case
        translate([0, -10, 90]) rotate([14,0,0]) cylinder(d=110, h=150); // tangential outlet
    }
    // duct: volute -> over the right fender -> rear plenum
    bent_tube([[430, 760, 380], [120, 620, 720], [-420, 380, 960], [-800, 60, 1000]], 105);
    // inlet plenum between the bins, one short outlet down into each lid
    translate([-880, 0, 990]) rbox_full([190, 280, 130], 34);
    for (yy=[-1,1]) translate([-895, yy*118, 930]) rotate([yy*-24,0,0]) cylinder(d=95, h=85);
    // twin HOPPER bins: tapered bodies, domed lids, handles, rear vent louvres
    for (yy=[-180,180]) translate([(BAG_X0+BAG_X1)/2, yy, 700]) {
        hull() {                                                        // tapered hopper
            translate([0,0,-195]) rbox_full([320, 250, 90], 30);        // narrow base (sits on the rack)
            translate([10,0,80])  rbox_full([400, 330, 200], 36);       // full-width body
        }
        translate([6, 0, 215]) rotate([0,-5,0]) rbox_full([400, 330, 70], 40);  // domed lid
        translate([-150, 0, 258]) rotate([90,0,0]) cylinder(d=22, h=150, center=true); // lid handle
        for (k=[-1,0,1]) translate([202, k*82, -60]) rbox([10, 52, 110], 4);    // vent louvres
    }
    // dump actuator: rack anchor up to the bin cross-arm (tips bins over the torque tube)
    translate([BAG_X0-30, -250, 330]) rotate([0,-42,0]) cylinder(d=40, h=310);
    translate([BAG_X1+40, -250, 452]) rotate([90,0,0]) cylinder(d=26, h=60, center=true);  // arm boss
}

// ---- blower + trimmer boom (front-left, rotates for edging passes) ---------
BOOM_BASE = [0, 0, 0];  // computed inline
module mower_boom() attach_gray() {
    bx = M_WHEELBASE-70; by = -(M_FRAME_W/2-40); bz = M_FRONT_CASTER_D/2+150;
    translate([bx, by, bz]) {
        cylinder(d=46, h=230);                                 // swivel post
        translate([0,0,230]) cylinder(d=72, h=36);             // slew ring
        translate([0,0,248]) rotate([90,0,0]) cylinder(d=40, h=520);   // boom arm (out over the left edge)
        // blower volute mid-arm, nozzle angled at the ground
        translate([0,-260,248]) rotate([0,90,0]) cylinder(d=170, h=120, center=true);
        translate([30,-260,160]) rotate([18,0,0]) rbox([80, 70, 150], 18);
        // DeWalt 60V FLEXVOLT trimmer head — brushless can, gearhead, FIXED-LINE
        // spool (no bump-feed: the machine can't bump, so none is needed) + guard
        translate([0,-520,248]) {
            cylinder(d=86, h=104, center=true);                        // brushless motor can
            translate([0,0,-92]) cylinder(d1=120, d2=86, h=42);        // gearhead cone
            translate([0,0,-110]) cylinder(d=112, h=16);               // fixed-line head
            for (a=[0,180]) rotate([0,0,a]) translate([56,0,-102])
                rotate([0,90,0]) cylinder(d=4, h=120);                 // line stubs (cut circle Ø ~380)
            translate([0,0,-96]) rotate_extrude(angle=200, $fn=48)     // debris guard
                translate([150,0]) square([8,26], center=true);
        }
        // FLEXVOLT 60V pack rides the boom post (weatherproof boot on the real build)
        translate([70, 0, 300]) rbox_full([180, 84, 112], 14);
    }
}

// ---- FIMCO 30-gal tow-behind sprayer (12V pump, speed-proportional) --------
SPR_AXLE_X = -1780;
module mower_sprayer_frame() attach_blk() {   // FIMCO 30-gal tow — proper trailer
    // drawbar with clevis hitch plate + pin at the mower's guard hoop
    bent_tube([[-660, 0, 300], [-1250, 0, 300]], 38);
    translate([-690, 0, 300]) rbox_full([70, 70, 26], 8);                 // hitch plate
    translate([-676, 0, 268]) cylinder(d=14, h=72);                       // clevis pin
    for (y=[-1,1]) bent_tube([[-1250, 0, 300], [SPR_AXLE_X, y*300, 320]], 34);  // A-frame
    for (y=[-330,330]) translate([SPR_AXLE_X, y, 165]) {                  // treaded trailer wheels
        rotate([90,0,0]) tire(330, 100, lugs=14);
        rotate([90,0,0]) cylinder(d=130, h=106, center=true);             // hub
    }
    translate([SPR_AXLE_X, 0, 330]) rotate([90,0,0]) cylinder(d=44, h=640, center=true);  // axle
    // rear boom on drop legs, three flat-fan nozzles pointing DOWN
    translate([SPR_AXLE_X-230, 0, 430]) rotate([90,0,0]) cylinder(d=36, h=1100, center=true);
    for (y=[-380,380]) bent_tube([[SPR_AXLE_X-120, y, 380], [SPR_AXLE_X-230, y, 430]], 26); // drop legs
    for (y=[-520,0,520]) translate([SPR_AXLE_X-230, y, 384])
        cylinder(d1=44, d2=14, h=46);                                     // nozzle bodies (tip down)
    // FIMCO 12V pump on the frame + REAL plumbing: sump -> pump -> boom feed
    translate([SPR_AXLE_X+150, 200, 400]) rbox_full([130, 95, 105], 16);  // pump
    bent_tube([[SPR_AXLE_X-40, 60, 345], [SPR_AXLE_X+120, 190, 380]], 18);    // suction: tank sump -> pump
    bent_tube([[SPR_AXLE_X+180, 200, 430], [SPR_AXLE_X-180, 260, 470], [SPR_AXLE_X-230, 180, 440]], 16); // pressure -> boom
    // 12V controller on the drawbar, harness forward to the machine
    translate([-1150, 60, 330]) rbox_full([100, 70, 60], 12);
    bent_tube([[-1190, 60, 330], [-700, 40, 320]], 9);
}
module mower_sprayer_tank() attach_tank() {   // FIMCO yellow poly tank, molded features
    translate([SPR_AXLE_X-40, 0, 570]) rbox_full([520, 620, 440], 130);   // main body
    translate([SPR_AXLE_X-40, 0, 400]) rbox_full([220, 220, 110], 36);    // molded SUMP (drain low point)
    translate([SPR_AXLE_X-60, 0, 790]) rbox_full([300, 380, 100], 44);    // molded top step
    translate([SPR_AXLE_X-60, 0, 850]) cylinder(d=150, h=34);             // 5" vented filler lid
    translate([SPR_AXLE_X-60, 0, 884]) cylinder(d=44, h=14);              // vent
}

// ---- TPMS valve-cap sensors on all four wheels  [accent] --------------------
module mower_tpms_accent() color([0.93,0.76,0.13]) mower_tpms();
module mower_tpms() {
    for (y=[-(M_FRAME_W/2+M_REAR_WHEEL_W/2+30), (M_FRAME_W/2+M_REAR_WHEEL_W/2+30)])
        translate([72, y>0?y+82:y-82, M_REAR_WHEEL_D/2+72]) rotate([90,0,0]) cylinder(d=15, h=20, center=true);
    for (y=[-(M_FRAME_W/2-40), (M_FRAME_W/2-40)])
        translate([M_WHEELBASE+34, y>0?y+58:y-58, M_FRONT_CASTER_D/2+34]) rotate([90,0,0]) cylinder(d=13, h=16, center=true);
}

ENV_L_ATT = (M_WHEELBASE + M_FRONT_CASTER_D/2) - (SPR_AXLE_X - 420);
echo(str("WITH ATTACHMENTS  L≈", ENV_L_ATT, " (bagger rack to ", BAG_X1,
         "; sprayer axle at ", SPR_AXLE_X, ") — attachments extend the base machine"));

module mower_attachments() {
    mower_bagger_frame();
    mower_bagger_bins();
    mower_boom();
    mower_sprayer_frame();
    mower_sprayer_tank();
}

module mower(lap_angle=0) {
    mower_frame();
    mower_rims();
    mower_footdeck();
    mower_fenders();
    mower_wheels();
    mower_casters();
    mower_deck();
    mower_deck_details();
    mower_blades_placed();
    mower_engine();
    mower_engine_detail();
    mower_accents();
    mower_branding();
    mower_fueltanks();
    mower_seat();
    mower_seatframe();
    mower_dash();
    if (M_HAS_ROPS) mower_rops();
    mower_lapbar(side=+1, angle=lap_angle);
    mower_lapbar(side=-1, angle=lap_angle);
}

// full working rig: machine + retrofit-era accents + every attachment
module mower_full(lap_angle=0) {
    mower(lap_angle);
    mower_attachments();
}

// preview when opened standalone (suppressed when included by assembly.scad)
if (is_undef(ASSEMBLY)) mower(lap_angle=8);
