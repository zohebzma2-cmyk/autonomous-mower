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
- [ ] **Hero GIF/video** in the first screenful of the README (lap-bar actuating or a sim run).
- [ ] Seed 3–5 `good first issue`s — especially "add a params profile for a Toro / Bad Boy / Spartan deck".
- [ ] Tag a **v0.1 release** so awesome-lists and HN have a version to point at.
- [ ] **awesome-list PRs:** [awesome-robotics](https://github.com/ahundt/awesome-robotics), [kiloreux/awesome-robotics](https://github.com/kiloreux/awesome-robotics), [awesome-agriculture](https://github.com/brycejohnston/awesome-agriculture).

## Launch sequence (warm → cold → aggregators)

1. **ArduPilot Discourse (Rover)** build thread — seeds technical credibility.
2. **OpenMower + ArduPilot Discord** show-off channels (read pinned rules first).
3. **Reddit** r/robotics + r/arduino — native writeup + GIF.
4. **Show HN** — repo link, be online for comments.
5. **Hackaday tip + Hackaday.io + Hackster.io** project write-up.
6. **Weekly Robotics tip + LinkedIn + X/Mastodon** with the GIF, tag @ArduPilot.
7. **Week 2:** awesome-list PRs (once there's a release + a few stars).

### Ready-to-post hooks (draft — post as yourself)

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
