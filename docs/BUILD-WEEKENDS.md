# The build, split into weekends

Each packet is self-contained: what to have on hand, what you finish with. Print queue order matches (docs/PRINT-QUEUE.md).

## Weekend 1 — the brain box (bench, indoors)
Have: enclosure + weekend-1 prints, Pi 5, Pixhawk, RTK board, fuse block, XT60s, crimper.
Do: BUILD.md §3–4 — equipment plate loadout, power tree, first boot, RTK fix on the bench.
Finish with: a box that boots, gets RTK-fixed, and serves the UI on your iPad.

## Weekend 2 — steering + kill chain (machine, blades stay off)
Have: weekend-2 prints, both actuators, ESP32, BTS7960s, e-stop, relays, marine wire.
Do: WIRING.md kill chain FIRST and prove it with a meter; then lap-bar clamps + rail anchors; ESP32 loop on stands.
Finish with: bars that center themselves and a mushroom that kills everything. **Jack stands mandatory.**

## Weekend 3 — sensors + first auto (open area)
Have: weekend-3 prints, masts, LiDAR, cameras, ultrasonic.
Do: masts on; BUILD.md §11 go/no-go — teach-and-repeat in an open area, wheels-on, BLADES STILL OFF.
Finish with: the machine re-driving your taught path within a few cm.

## Weekend 4 — sonar + on-unit screen (+ dual-RTK if ordered)
Have: weekend-4 prints (`sonar_collar_a/b`, `display_hood_l/r`, `display_brace` ×2, `display_yoke`), Ø120 × 1.5 mm aluminium ground plane(s), Touch Display 2.
Do: sonar collar 2 mm under the antenna cap, probe face-up; hood halves bolted at the seam, braces into the heat-set tabs, yoke on the brain-box lid. Dual-RTK: tee + 628 mm crossbar + both antenna plates, then the moving-baseline block in `rover_params.parm`.
Finish with: a hand held over the mast stops the machine (`LOW BRANCH`), and the screen readable in direct sun.

## Later — Phase 3 attachments
Per docs/ATTACHMENTS.md, one attachment at a time, each behind its interlock tests.
