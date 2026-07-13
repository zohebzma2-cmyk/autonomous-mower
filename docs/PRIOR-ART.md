# Prior-art & invention notebook — the practice

The design log already timestamps every design decision in git (signed commits on a public
repo = strong prior-art evidence). This file formalizes it:

1. **Anything that feels novel gets a dated entry here** the day it's conceived, with a
   sketch or the commit hash that embodies it.
2. Git history is the authoritative timeline; this file is the index.

## Entries
- **2026-06-26** — ESP32 fail-to-neutral lap-bar position loop between an FC's PWM and hydro
  lap bars (commit cf700c1). Watchdog-loss → spring-to-neutral behavior.
- **2026-07-12** — No-pivot coverage planning for heavy ZTRs: headland-inset rows with
  smooth-U / 3-point-K waypoint generation sized to hydro-holdable arc radius (commit 40ce7d5).
- **2026-07-12** — Speed-proportional tow-sprayer dosing slaved to RTK ground speed with
  yaw-rate application pause (commit 40ce7d5).

*(Defensive publication: all of this is public + MIT — that's the strategy: nobody can patent
it out from under the project.)*
