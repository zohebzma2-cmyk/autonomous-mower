# SPDX-License-Identifier: MIT
"""Project footprints that KiCad's libraries don't have (-> MowerCarrier.pretty).

Relay_SPST_Songle_SLA-xxVDC-SL-A — from Songle's own SLA-series drawing
("Outline dimensions, wiring diagram and PC board layout", bottom view B, tolerance
±0.1 mm). Pin positions relative to COM, as drawn from the BOTTOM:
    NO   (+17.8, -2.5)      NC (+17.8, -10.1, Form C only — absent on Form A)
    coil (+3.8, +12.7) and (+14.0, +12.7)
Holes: power pins "3-φ2", coil pins "2-φ1". Body 27.6 x 31.8 (32 MAX); COM sits 4.4
from the body's left edge and 12.6 below its top edge.
KiCad footprints are drawn from the TOP, so X is mirrored below.
NOTE: KiCad's Relay_SPST_RAYEX-L90A is a different T90 pinout — do not substitute it.
"""
import os
import uuid

HERE = os.path.dirname(os.path.abspath(__file__))


def _u():
    return str(uuid.uuid4())


def relay_sla_form_a():
    m = -1.0                                        # bottom view -> top view: mirror X
    pads = [("13", 0.0, 0.0, 2.0, 3.5), ("14", 17.8, -2.5, 2.0, 3.5),
            ("A1", 3.8, 12.7, 1.0, 2.0), ("A2", 14.0, 12.7, 1.0, 2.0)]
    x_l, x_r = sorted([m * -4.4, m * 23.2])        # body (bottom-view x -4.4..23.2)
    y_t, y_b = -12.6, 19.2
    pad_s = ""
    for name, x, y, drill, size in pads:
        shape = "rect" if name == "13" else "circle"
        pad_s += f'''
	(pad "{name}" thru_hole {shape} (at {m * x:.2f} {y:.2f}) (size {size} {size}) (drill {drill})
		(layers "*.Cu" "*.Mask") (remove_unused_layers no) (uuid "{_u()}"))'''

    def rect(layer, grow, width):
        return (f'\n\t(fp_rect (start {x_l - grow:.2f} {y_t - grow:.2f}) (end {x_r + grow:.2f} {y_b + grow:.2f}) '
                f'(stroke (width {width}) (type solid)) (fill no) (layer "{layer}") (uuid "{_u()}"))')

    return f'''(footprint "Relay_SPST_Songle_SLA-xxVDC-SL-A"
	(version 20241229)
	(generator "gen_footprints.py")
	(layer "F.Cu")
	(descr "Songle SLA-xxVDC-SL-A, SPST-NO 30A (Form A), PCB layout per Songle SLA series drawing (bottom view B), mirrored to top view")
	(tags "relay songle SLA 30A T90")
	(property "Reference" "REF**" (at {x_l + 2:.2f} {y_t - 2:.2f} 0) (layer "F.SilkS") (uuid "{_u()}")
		(effects (font (size 1 1) (thickness 0.15)) (justify left)))
	(property "Value" "SLA-12VDC-SL-A" (at {(x_l + x_r) / 2:.2f} {(y_t + y_b) / 2:.2f} 0) (layer "F.Fab") (uuid "{_u()}")
		(effects (font (size 1 1) (thickness 0.15))))
	(property "Datasheet" "https://www.songlerelay.com" (at 0 0 0) (layer "F.Fab") (hide yes) (uuid "{_u()}")
		(effects (font (size 1 1) (thickness 0.15))))
	(attr through_hole){rect("F.Fab", 0, 0.1)}{rect("F.SilkS", 0.12, 0.12)}{rect("F.CrtYd", 0.5, 0.05)}
	(fp_text user "30A NO ONLY" (at {(x_l + x_r) / 2:.2f} {y_b - 2:.2f} 0) (layer "F.SilkS") (uuid "{_u()}")
		(effects (font (size 1 1) (thickness 0.15)))){pad_s}
)
'''


def write_all():
    d = os.path.join(HERE, "MowerCarrier.pretty")
    os.makedirs(d, exist_ok=True)
    open(os.path.join(d, "Relay_SPST_Songle_SLA-xxVDC-SL-A.kicad_mod"), "w").write(relay_sla_form_a())
    return d


if __name__ == "__main__":
    print(write_all())
