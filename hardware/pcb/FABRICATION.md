# MowerCarrier Rev A — how to fabricate

This is a **design package** (schematic + placement + netlist + BOM), not a set
of Gerbers yet — the Rev A step is to open it in KiCad, drop the BOM parts onto
the placement, route the two layers, and export. Here's the path end-to-end.

## 1. Route it in KiCad (free)

1. New KiCad project → draw the schematic from **[netlist.md](netlist.md)**
   (it's the authoritative connectivity) using the **[BOM.md](BOM.md)** parts.
2. Assign footprints — mind the two flagged risks:
   - **ESP32 header pitch** — measure your DevKit (25.4 mm genuine vs 22.86 mm clone).
   - **Q1 thermal** — TO-220 with a big top-copper pour, or two IRF4905 in parallel.
3. Board setup: 2-layer, 1.6 mm, **2 oz copper**; net-classes with a wide
   **POWER** class (poured, ≥3 mm) and a normal **SIGNAL** class (6/6 mil).
4. Place per **layout.svg**; pour GND on the bottom, power + signal on top.
5. DRC clean → **Export Gerbers + drill + centroid (.pos) + BOM (.csv)**.

## 2. Order at JLCPCB

- Upload the Gerber zip. Set: **2 layers, 1.6 mm, 2 oz outer copper**, HASL or
  ENIG, any soldermask (green is cheapest).
- For assembly (PCBA): upload the BOM.csv + centroid. Choose **Economic** SMT for
  the Basic passives. **Uncheck the THT parts** (XT60, fuse holder, relays, screw
  terminals, headers) and hand-solder those yourself to save the per-joint + XT60
  fixture fees. See the BOM cost table.
- 5 pcs is the sweet spot (~$70–110 with self-soldered THT).

## 3. Bring-up order (do NOT skip)

1. **Power tree first, no modules.** Apply 12 V through a current-limited bench
   supply. Verify reverse-polarity protection (briefly reverse — Q1 should block),
   fuse continuity, and that +12/+5/+3V3 rails read correct with nothing plugged.
2. **Kill-chain second.** With a meter on the relay contacts, confirm the relay
   only closes when **both** E-STOP is released **and** the driver FET is
   commanded on. Press E-STOP → contacts open instantly. Command FET off →
   contacts open. This is the safety gate; prove it before a motor is ever wired.
3. **Then modules**, one at a time: socket the ESP32, verify `GPIO25` reads the
   e-stop, then pots, then (bench, wheels off ground) the BTS7960 logic.
4. Conformal-coat after test; dielectric-grease every connector.

## 4. Roadmap

- **Rev A** — this package: get boards, hand-populate, bench-validate the power
  tree + kill-chain.
- **Rev B** — fold in whatever the build teaches (connector choices, Q1 thermal,
  a real load-dump TVS), add board-mount status OLED / CAN, and publish Gerbers +
  a JLCPCB "order these exact boards" link so anyone can one-click fab it.

> Everything here is MIT — fork the board, adapt the footprints to your ZTR, and
> send a PR with your machine's profile.
