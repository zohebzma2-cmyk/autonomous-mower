# SPDX-License-Identifier: MIT
"""Write mowercarrier.kicad_sch from design.py using KiCad's own library symbols.

Each symbol is placed on a grid; every connected pin gets a 2.54 mm wire stub and a
local net label, every unused pin a no-connect flag. It is a flat, net-labelled
schematic: dull to look at, but every connection is explicit and ERC-checkable.
Pure stdlib (runs under any Python 3.9+). Returns {ref: symbol uuid} for PCB linking.
"""
import os
import re
import uuid

KSYM = os.environ.get("KICAD9_SYMBOL_DIR",
                      os.path.expanduser("~/Applications/KiCad/KiCad.app/Contents/SharedSupport/symbols"))
GRID = 2.54


def _u():
    return str(uuid.uuid4())


def _block(text, start):
    """Return the balanced s-expression starting at text[start] == '('."""
    depth, i, n = 0, start, len(text)
    while i < n:
        c = text[i]
        if c == '"':                        # skip strings (may contain parens)
            i += 1
            while text[i] != '"':
                i += 2 if text[i] == "\\" else 1
        elif c == "(":
            depth += 1
        elif c == ")":
            depth -= 1
            if depth == 0:
                return text[start:i + 1]
        i += 1
    raise ValueError("unbalanced")


def _find_symbol(libtext, name):
    m = re.search(r'\n\t\(symbol "%s"\n' % re.escape(name), libtext)
    if not m:
        raise KeyError(name)
    return _block(libtext, m.start() + 2)


_libcache = {}


def lib_symbol(lib_id):
    """Flattened library symbol block renamed to 'Lib:Name' (derived symbols resolved)."""
    lib, name = lib_id.split(":")
    if lib not in _libcache:
        _libcache[lib] = open(os.path.join(KSYM, lib + ".kicad_sym"), encoding="utf-8").read()
    text = _libcache[lib]
    blk = _find_symbol(text, name)
    ext = re.search(r'\(extends "([^"]+)"\)', blk)
    if ext:                                           # derived: parent graphics + child properties
        parent = _find_symbol(text, ext.group(1))
        props = re.findall(r'\n\t\t\(property "[^"]+"[\s\S]*?\n\t\t\)', blk)
        body = re.sub(r'\n\t\t\(property "[^"]+"[\s\S]*?\n\t\t\)', "", parent)
        head_end = body.index("\n", body.index("(symbol"))
        body = body[:head_end] + "".join(props) + body[head_end:]
        body = body.replace('(symbol "%s_' % ext.group(1), '(symbol "%s_' % name)
        body = body.replace('(symbol "%s"' % ext.group(1), '(symbol "%s"' % name, 1)
        blk = body
    return blk.replace('(symbol "%s"' % name, '(symbol "%s"' % lib_id, 1)


def pins_of(blk):
    """{number: (x, y, angle)} in symbol coordinates (y up)."""
    out = {}
    for m in re.finditer(r'\(pin \w+ \w+\s*\(at ([-\d.]+) ([-\d.]+) ([-\d.]+)\)[\s\S]*?\(number "([^"]+)"', blk):
        out[m.group(4)] = (float(m.group(1)), float(m.group(2)), float(m.group(3)))
    return out


def _snap(v):
    return round(round(v / 1.27) * 1.27, 4)


def build(path, project, parts, footprint_lib_prefix_ok=True):
    root = _u()
    lib_blocks, placed, items = {}, {}, []
    cols, cw, ch = 7, 76.2, 58.42                     # grid cells (multiples of 2.54)
    x0, y0 = 30.48, 38.1
    for i, (ref, lib_id, value, fp, part, pinmap) in enumerate(parts):
        if lib_id not in lib_blocks:
            lib_blocks[lib_id] = lib_symbol(lib_id)
        pins = pins_of(lib_blocks[lib_id])
        missing = set(pinmap) - set(pins)
        assert not missing, f"{ref}: pins {missing} not in symbol {lib_id} ({sorted(pins)})"
        sx = x0 + (i % cols) * cw + cw / 2
        sy = y0 + (i // cols) * ch + ch / 2
        sx, sy = _snap(sx), _snap(sy)
        su = _u()
        placed[ref] = su
        pin_uuids = "".join(f'\n\t\t(pin "{n}"\n\t\t\t(uuid "{_u()}")\n\t\t)' for n in pins)
        items.append(f'''
	(symbol
		(lib_id "{lib_id}")
		(at {sx} {sy} 0)
		(unit 1)
		(exclude_from_sim no)
		(in_bom {"no" if ref.startswith("MH") else "yes"})
		(on_board yes)
		(dnp no)
		(uuid "{su}")
		(property "Reference" "{ref}"
			(at {sx} {_snap(sy - 16.51)} 0)
			(effects (font (size 1.27 1.27)))
		)
		(property "Value" "{value}"
			(at {sx} {_snap(sy + 16.51)} 0)
			(effects (font (size 1.27 1.27)))
		)
		(property "Footprint" "{fp}"
			(at {sx} {sy} 0)
			(effects (font (size 1.27 1.27)) (hide yes))
		)
		(property "Datasheet" "~"
			(at {sx} {sy} 0)
			(effects (font (size 1.27 1.27)) (hide yes))
		)
		(property "LCSC/MPN" "{part}"
			(at {sx} {sy} 0)
			(effects (font (size 1.27 1.27)) (hide yes))
		){pin_uuids}
		(instances
			(project "{project}"
				(path "/{root}"
					(reference "{ref}")
					(unit 1)
				)
			)
		)
	)''')
        for num, (px, py, ang) in pins.items():
            ex, ey = _snap(sx + px), _snap(sy - py)       # pin connection point (schematic y down)
            net = pinmap.get(num)
            if net is None:
                items.append(f'\n\t(no_connect (at {ex} {ey}) (uuid "{_u()}"))')
                continue
            a = int(round(ang)) % 360                       # pin points from the end toward the body
            dx, dy = {0: (-1, 0), 180: (1, 0), 90: (0, 1), 270: (0, -1)}[a]
            lx, ly = _snap(ex + dx * GRID), _snap(ey + dy * GRID)
            items.append(f'\n\t(wire (pts (xy {ex} {ey}) (xy {lx} {ly})) (stroke (width 0) (type default)) (uuid "{_u()}"))')
            lang, just = {(-1, 0): (180, "right"), (1, 0): (0, "left"), (0, -1): (90, "left"), (0, 1): (270, "right")}[(dx, dy)]
            items.append(f'\n\t(label "{net}" (at {lx} {ly} {lang}) (effects (font (size 1.27 1.27)) (justify {just} bottom)) (uuid "{_u()}"))')

    title = ('\n\t(text "MowerCarrier Rev A.1 — generated by hardware/pcb/kicad/gen_kicad.py from design.py. '
             'Nets are joined by label name; see design.py for the Rev A -> A.1 corrections." '
             f'(exclude_from_sim no) (at 30.48 25.4 0) (effects (font (size 2.54 2.54)) (justify left bottom)) (uuid "{_u()}"))')
    libs = "".join("\n\t\t" + b.replace("\n", "\n\t") for b in lib_blocks.values())
    sch = f'''(kicad_sch
	(version 20250114)
	(generator "eeschema")
	(generator_version "9.0")
	(uuid "{root}")
	(paper "A1")
	(title_block
		(title "MowerCarrier — power + kill-chain + ESP32 carrier")
		(rev "A.1")
		(company "autonomous-mower (MIT)")
	)
	(lib_symbols{libs}
	){title}{"".join(items)}
	(sheet_instances
		(path "/"
			(page "1")
		)
	)
	(embedded_fonts no)
)
'''
    open(path, "w", encoding="utf-8").write(sch)
    return root, placed
