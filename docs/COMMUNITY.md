# Promotion & community playbook

A concrete plan to grow this project and connect with the people building adjacent
things. **The one framing that wins everywhere:** most open mowers convert a
*toy* robot-mower — this retrofits a **615 lb commercial gas zero-turn**. Lead
with that, and always foreground **safety** (blades-disconnected-until-proven);
this niche has a strong safety culture that rewards it.

## Where the audience already is

| Community | Link | Why |
|-----------|------|-----|
| **ArduPilot Rover Discourse** | https://discuss.ardupilot.org (Rover) | Warmest, most technical audience — we run their exact stack. Start a build thread here first. |
| **OpenMower Discord** | via https://openmower.de | 2000+ people doing exactly this (at toy scale). |
| **ArduPilot Discord** | via https://ardupilot.org | Dev + user help. |
| **DIY Robocars** | https://www.diyrobocars.com | Publishes community builds; has featured ArduRover mowers. |
| **Twisted Fields forum** | https://community.twistedfields.com | Friendly outdoor-autonomy crowd. |
| **Reddit** | r/robotics · r/arduino · r/diyelectronics · r/lawncare · r/ROS | Native writeup + GIF, link in body. Respect the 9:1 self-promo etiquette. |
| **Hacker News** | Show HN | Calm title, repo link (not marketing page), be online to reply. |
| **Hackaday** | tips@hackaday.com + Hackaday.io build log | The gas-ZTR angle is their catnip. |
| **Weekly Robotics** | mat@weeklyrobotics.com | ~14k robotics engineers; one-paragraph tip. |

## GitHub-native (done / to-do)

- [x] **Topics** added (robotics, ardupilot, ardurover, rtk-gps, robot-mower, lidar, esp32, open-source-hardware, …).
- [x] **Discussions** enabled — categories to set: Show & Tell, Q&A, Ideas, Build logs.
- [x] **Related-projects** section + **badges** + **CONTRIBUTING.md** in the README.
- [ ] **Social-preview image** (Settings → Social preview, 1280×640 branded card) — biggest click-through lever from Discord/HN/X shares.
- [x] **Hero GIF/video** in the first screenful of the README (orbit GIF).
- [ ] Seed 3–5 `good first issue`s — especially "add a params profile for a Toro / Bad Boy / Spartan deck".
- [x] Tagged **v0.2-design** (GLB + order sheet + media kit as assets).
- [ ] **awesome-list PRs:** [awesome-robotics](https://github.com/ahundt/awesome-robotics), [kiloreux/awesome-robotics](https://github.com/kiloreux/awesome-robotics), [awesome-agriculture](https://github.com/brycejohnston/awesome-agriculture).

## Launch sequence (warm → cold → aggregators)

1. **ArduPilot Discourse (Rover)** build thread — seeds technical credibility.
2. **OpenMower + ArduPilot Discord** show-off channels (read pinned rules first).
3. **Reddit** r/robotics + r/arduino — native writeup + GIF.
4. **Show HN** — repo link, be online for comments.
5. **Hackaday tip + Hackaday.io + Hackster.io** project write-up.
6. **Weekly Robotics tip + LinkedIn + X/Mastodon** with the GIF, tag @ArduPilot.
7. **Week 2:** awesome-list PRs (once there's a release + a few stars).


## FINAL POSTS — ready to paste (updated for Phase 3, post as yourself)

### 1 · ArduPilot Discourse — Rover category (post first)

**Title:** Build thread: autonomous 615 lb gas zero-turn (Gravely ZT X 52) — skid-steer via lap-bar actuators, dual-F9P, fence + no-pivot turns

Most autonomous-mower projects convert a small robot platform. I'm retrofitting a full-size
commercial gas zero-turn — a 615 lb Gravely ZT X 52 — with ArduPilot Rover owning drive, RTK
nav and failsafes. Design + sim are complete and open (MIT); the physical build is underway,
blades stay disconnected until every failsafe is proven on stands.

The parts I'd love this community's eyes on:

- **Lap-bar actuation**: the FC can't drive hydro lap bars directly, so an ESP32 closes the
  loop — FC PWM in, potentiometer feedback, BTS7960 out — with fail-to-neutral on e-stop or
  signal loss (firmware in the repo).
- **Heading**: dual ZED-F9P moving-baseline (~0.4° true heading) because motion-derived
  heading wanders at mowing speeds and pivots.
- **Turns**: the coverage planner never pivots (turf shear under 615 lb = ruts). Row ends are
  smooth-U or 3-point-K headland turns generated as waypoints and uploaded as AUTO missions.
- **Fence**: operator draws the boundary in a web UI; the companion enforces it AND pushes it
  to the FC as a polygon inclusion fence (MAV_MISSION_TYPE_FENCE) — belt and suspenders.
- **Kill chain**: hardware-first (NC mushroom on the relay-coil loop, magneto ground);
  software mirrors it. rover_params.parm is in the repo — critique welcome.

Repo (CAD, firmware, 45-test companion, wiring, build manual):
https://github.com/zohebzma2-cmyk/autonomous-mower
Interactive writeup (3D model, live sim UI): https://zohebalvi.com/projects/autonomous-mower.html

### 2 · OpenMower Discord — #show-off (read pinned rules first)

OpenMower is what convinced me RTK mowing is solved at robot scale — so I took the same
idea (F9P + Pi + open firmware) to the other end of the spectrum: a 615 lb commercial gas
zero-turn. The interesting new problem is actuation: hydro lap bars instead of wheel motors,
solved with feedback linear actuators + an ESP32 position loop that fails to neutral.
Everything's open (MIT): parametric CAD that re-fits any ZTR from a few measurements,
ArduPilot params, a tested companion (geofence, no-pivot headland turns, attachment
interlocks). Design+sim done, physical build in progress, blades off until failsafes prove
out. https://github.com/zohebzma2-cmyk/autonomous-mower

### 3 · r/robotics — native writeup

**Title:** Converting a 615 lb commercial gas zero-turn into an autonomous robot — open-source CAD, firmware, and a tested safety layer [build in progress]

Body:
Most open-source mowers start from a toy-class robot platform. I started from the other end:
a Gravely ZT X 52 (52″ deck, 24 hp Kohler) with the operator replaced by ArduPilot Rover,
dual-RTK GPS, LiDAR, cameras + a Hailo NPU, and an ESP32 that physically drives the hydro
lap bars through feedback linear actuators (fail-to-neutral).

Things that turned out to be the actual engineering:
- A zero-turn pivot shears turf under this weight, so the planner does 3-point headland
  turns like a tractor — physics writeup in the repo.
- A geofence the machine can't leave (companion-enforced + pushed to the flight controller
  as an inclusion fence).
- The kill chain is hardware-first: NC e-stop opens the relay-coil loop and grounds the
  magneto; software only mirrors it. 45 tests over the safety/interlock layer.
- Parametric OpenSCAD: measure ~5 things on YOUR zero-turn and the 32 printed brackets
  re-generate to fit.

Status honestly: design + simulation complete, physical build underway, blades stay
disconnected until drive/nav/failsafes are proven on stands.
Repo: https://github.com/zohebzma2-cmyk/autonomous-mower
GIF + interactive 3D: https://zohebalvi.com/projects/autonomous-mower.html

### 4 · Show HN

**Title:** Show HN: Making a 615 lb gas zero-turn mower drive itself (open-source CAD + firmware)

**URL:** https://github.com/zohebzma2-cmyk/autonomous-mower

**First comment (post immediately):**
Author here. This retrofits a commercial Gravely zero-turn with ArduPilot Rover, dual-RTK,
LiDAR/camera AI, and an ESP32 closing the position loop on the hydro lap bars. Everything is
open: parametric CAD (re-fits any ZTR from a handful of measurements), firmware, a
stdlib-Python companion with 45 tests over the safety layer, wiring + PCB design, and the
full order sheet. Design and sim are done; the physical build is in progress and blades stay
disconnected until every failsafe is proven — a 52″ deck deserves respect. Happy to answer
anything about the lap-bar actuation, the no-pivot turn planner, or why the kill chain is
hardware-first.

### 5 · Hackaday tip (email tips@hackaday.com)

**Subject:** Tip: open-source autonomy retrofit for a 615 lb commercial gas zero-turn

Most robot mowers are purpose-built and toy-sized. This project bolts autonomy onto a real
machine — a Gravely ZT X 52 — with ArduPilot Rover, dual-RTK heading, and the fun hack: an
ESP32 driving the hydraulic lap bars through feedback linear actuators, failing to neutral
on any fault. The repo has parametric OpenSCAD (32 printed parts that re-fit any zero-turn
from a few caliper measurements), a carrier-PCB design for the kill chain, a tested geofence
+ no-pivot turn planner, and an honest design log of everything that went wrong along the
way. Design+sim complete, physical build in progress, blades off until failsafes prove out.
https://github.com/zohebzma2-cmyk/autonomous-mower ·
https://zohebalvi.com/projects/autonomous-mower.html

### Original hooks (superseded by the final posts above)

- **ArduPilot Discourse:** *"Reference ArduRover build: retrofitting a 615 lb gas zero-turn (Gravely ZT X 52) — skid-steer + dual-RTK + an ESP32 closing the lap-bar loop the FC can't drive."*
- **OpenMower Discord:** *"OpenMower converts a toy mower — I took the same RTK+Pi+vision idea to a full-size commercial gas ZTR. Here's the lap-bar actuation problem and how I solved it."*
- **r/robotics:** *"Converting a commercial gas zero-turn into a self-driving robot — ArduPilot, dual RTK, LiDAR, Hailo AI, ESP32 lap-bar controller. Full open-source CAD + firmware."*
- **Show HN:** *"Show HN: Turning a 615 lb gas zero-turn mower into an autonomous robot (open-source CAD + firmware)."*

### Etiquette

Contribute before promoting — answer a lap-bar / skid-steer / RTK question or
share a datasheet-accurate CAD tip first, so your "here's my build" reads as a
member, not a drive-by ad. Reply to every comment in the first day; early
engagement is what these communities reward.

## Ongoing

Weekly devlog in Discussions → Build logs; cross-post the best one monthly.
Milestone posts drive the biggest spikes — save real footage for **first
autonomous drive (blades off)**, **first full mow**, and **first contributor's
different-brand build**. Treat every "adapt this to my ZTR" request as the growth
engine: each new machine profile is a new evangelist.

*Compiled from research on the open autonomous-mower ecosystem (OpenMower,
Ardumower/Sunray, ArduPilot Rover, DIY Robocars, FarmBot, Twisted Fields).
All links verified; niche subreddit names should be confirmed before posting.*
