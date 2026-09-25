# MowerCarrier Rev A.1 — KiCad 9 project (generated)

![3D render](../render-iso.png)

Power input + reverse-polarity protection + 30 A main fuse + five fused branches, the
hardware kill chain (E-stop NC contacts in series with FET-switched relay coils), and the
ESP32-DevKitC carrier for the lap-bar controller. 120 × 100 mm, 2 layers, 2 oz copper.

**The `.kicad_*` files are generated. Edit `design.py` (parts + nets) or `gen_pcb.py`
(placement, pours, routing), then regenerate** — don't hand-edit the outputs, they'd be
overwritten.

```bash
./scripts/setup-dev.sh --kicad          # once: KiCad 9, Java 25 JRE, Freerouting 1.9.0, arduino-cli
hardware/pcb/kicad/gen_kicad.sh         # schematic -> placement -> pours -> autoroute -> GND pour
./scripts/check.sh                      # runs ERC + DRC (errors, schematic parity) on the result
```

| File | What |
|---|---|
| `design.py` | single source of truth: every part (symbol, footprint, LCSC/MPN) and every pin's net; the Rev A → A.1 corrections are listed at the top |
| `gen_schematic.py` | writes `mowercarrier.kicad_sch` from KiCad's own library symbols (net labels on every pin, no-connect flags on the rest) |
| `gen_footprints.py` | `MowerCarrier.pretty/` — the Songle SLA relay footprint, from Songle's drilling drawing |
| `gen_pcb.py` | placement table, trunk pours + track keepouts, Q1 heatsink keepout, Freerouting (DRC-verified, retried), fuse-clip + GND pours |
| `gen_kicad.py` | runs it all, then exports `fab/`, `../schematic.svg`, `../layout.svg`, `../render-*.png` |
| `mowercarrier.kicad_dru` | the two scoped DRC exceptions, with the reasons |
| `fab/` | Gerbers + drill (zip for JLCPCB), pick-and-place CSV, grouped BOM with LCSC numbers |
| `REVIEW.md` | **read before ordering** — what's verified, what isn't, and the items a human must sign off |

## Verified (by the tools, on every regeneration)

- **ERC: 0 violations.** The exported KiCad netlist matches `design.py` net for net.
- **DRC: 0 violations of any severity, 0 unconnected, 0 schematic-parity issues.** Two scoped
  exceptions live in `mowercarrier.kicad_dru` (Q1 inside its heatsink; edge-connector silk).
- Footprint pads == symbol pins for every part (asserted by the generator). The route is
  verified with KiCad's DRC inside the generator, which retries with other pass budgets if
  anything is left open.
- **Deterministic:** an unchanged design regenerates byte-identically (`check.sh --full` gates it).

## Not verified by tools — see REVIEW.md

The ESP32 row pitch of *your* DevKit, Q1's insulating kit (required: its heatsink is grounded),
and a human look at the autorouted logic nets.
