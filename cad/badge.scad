// ============================================================================
//  PRODUCT NAMEPLATE / LOGO BADGE  —  mounts on the brain box (the brand mark).
//  Set PRODUCT_NAME below. Print the plate in dark filament, the logo + text in a
//  contrast colour (filament swap at the raised layer) or just leave embossed.
// ============================================================================
include <utils.scad>

PRODUCT_NAME = "AUTOACRE";    // <-- PLACEHOLDER — set your own brand. (Avoid "Automower" = Husqvarna TM.)
TAGLINE      = "autonomous ZTR";

PLATE   = [114, 34];          // nameplate L x W (fits the bed)
PLATE_T = 3;
RAISE   = 1.0;                // emboss height of logo + text
HOLE    = M3_CLEAR;

// ---- the logo mark: ring + filled centre (matches the control-UI mark) ----
module logo_mark(d=22) {
    linear_extrude(RAISE) {
        difference() { circle(d=d); circle(d=d-4.5); }   // ring
        circle(d=d-11);                                  // filled centre dot
    }
}

module nameplate() {
    difference() {
        union() {
            linear_extrude(PLATE_T) rrect(PLATE, 6);                 // base plate
            translate([-PLATE[0]/2+19, 0, PLATE_T]) logo_mark(22);   // logo at left
            // product name
            translate([-PLATE[0]/2+35, 3.5, PLATE_T])
                linear_extrude(RAISE) text(PRODUCT_NAME, size=7, font="Helvetica:style=Bold",
                                           halign="left", valign="center");
            // tagline
            translate([-PLATE[0]/2+35, -7, PLATE_T])
                linear_extrude(RAISE) text(TAGLINE, size=4.2, font="Helvetica",
                                           halign="left", valign="center");
        }
        // 2 mount holes
        for (x=[-1,1]) translate([x*(PLATE[0]/2-5), 0, -EPS])
            cylinder(d=HOLE, h=PLATE_T+2*EPS);
    }
}

module PRINT_badge() nameplate();

if (is_undef(PREVIEW_OFF)) PRINT_badge();
