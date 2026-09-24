# Adapting to an RC / electric-drive mower (tracked or wheeled)

The reference build is a **hydrostatic ZTR driven by lap bars**, so it needs linear
actuators plus the ESP32 position loop (`firmware/lapbar_controller/`) to turn
ArduPilot's throttle outputs into lever positions.

A **remote-controlled slope mower** (tracked units like the QL-R800-class
machines, or wheeled RC flail mowers) is easier. Its drive controller already takes
servo PWM from an RC receiver, so **the Pixhawk sits between the receiver and the
drive controller**. No actuators, no ESP32, no lap-bar PID.

```
 RC transmitter ─► receiver ─(SBUS/PPM)─► Pixhawk RCIN
                                            │  MANUAL: sticks pass through
                                            │  AUTO:   ArduPilot drives
                                            ▼
                               Pixhawk MAIN OUT 1/3 ─► mower drive controller
                                                       (the plugs that used to
                                                        go to the receiver)
```

Everything above the drive layer stays the same: RTK, geofence, coverage
missions, the companion (`software/companion/`), the safety policy, and the UI.

## 1. Find out what your drive controller expects (bench, tracks off the ground)

Plug a servo tester (or a spare receiver) into the drive controller's input
channels one at a time and write down:

| Question | Why it matters |
|---|---|
| Is there **one input per track**, or **steering + throttle** mixed on the machine? | Chooses profile A or B below |
| Pulse range and neutral (usually 1000 / 1500 / 2000 µs) | `SERVOx_MIN/TRIM/MAX` |
| Signal voltage (3.3 V or 5 V logic) | Pixhawk outputs 3.3 V, which most controllers accept. If yours doesn't, use a level shifter |
| **What happens when the pulse stops?** Unplug the signal wire while a track is turning | **Most important test.** It must stop. If it keeps the last command, you need the hardware kill in §4 before anything else |
| Which channels start the engine, engage the blade clutch, or set cut height? | Keep these on the receiver or pass them through (§3). ArduPilot never drives them in AUTO |

## 2. Load a profile

Start from [`firmware/ardupilot/profiles/rc-tracked.parm`](../firmware/ardupilot/profiles/rc-tracked.parm),
then load the RTK, fence and failsafe blocks from `rover_params.parm` on top.

- **Profile A: one input per track (preferred).** Use `SERVO1_FUNCTION=73` (throttleLeft)
  and `SERVO3_FUNCTION=74` (throttleRight). ArduPilot does the skid-steer mixing, so
  pivot turns and the rate controllers work as documented.
- **Profile B: the machine mixes internally.** Use `SERVO1_FUNCTION=26` (GroundSteering)
  and `SERVO3_FUNCTION=70` (Throttle). ArduPilot then treats the machine like a car
  with very tight steering. It still works, but tune `ATC_STR_RAT_*` gently, because the
  machine's own mixer adds a lag you can't see.

`MOT_SAFE_DISARM=0` keeps sending **neutral pulses** while disarmed, instead of going
silent. That matters when a controller holds its last command on signal loss.

## 3. Engine, blades, cut height

Leave them on the transmitter. If they must go through the Pixhawk, use RC
passthrough (`SERVOn_FUNCTION = 50 + input channel`, e.g. `55` = RCIN5). ArduPilot
then copies the stick and never commands the channel itself. The project's safety
rule applies unchanged: **the blade clutch stays mechanically disconnected until drive,
navigation and every failsafe are proven** (see [`BUILD.md` §0](BUILD.md)).

## 4. Kill chain for a heavy tracked machine

A 300+ kg tracked mower on a slope is at least as dangerous as the ZTR. Make the
e-stop **independent of the Pixhawk**:

- A physical mushroom e-stop on the machine **and** a second-radio remote kill
  (separate receiver and frequency). Both open the engine ignition/kill circuit and
  the drive controller's enable or power, through the same normally-closed relay
  topology as [`WIRING.md`](WIRING.md) and the MowerCarrier board.
- Also map a transmitter switch to `RCx_OPTION=31` (Motor Emergency Stop). This is a
  software layer on top of the hardware kill and does not replace it.
- Keep the stock RC failsafe. Set the receiver to output **no pulses** (not "hold")
  on signal loss, so `FS_THR_ENABLE` trips.

## 5. Tracks and turf

Tracks tear up grass in pivot turns far more than wheels do. Two knobs:

- `WP_PIVOT_ANGLE`: above this heading error, ArduPilot pivots in place. Raise it
  (or set `0` to disable pivots) to get wider arcing turns.
- The companion's no-rut headland planner (`plan_coverage_turns` in
  `software/companion/missions.py`, smooth-U / 3-point-K turns) already generates
  arc turns. Set `TURN_RADIUS_M` to your machine's gentlest comfortable radius.

## 6. Bring-up order (same gates as the reference build)

1. Tracks off the ground: MANUAL mode passthrough, confirm direction and neutral per side.
2. Pull the signal wire, pull the RC link, press both e-stops. Each must stop the tracks.
3. On the ground, blades disconnected: MANUAL, then HOLD, then a short AUTO line at `CRUISE_SPEED≤1.0`.
4. Learn the cruise throttle (`CRUISE_SPEED`/`CRUISE_THROTTLE`), then tune the steering rate (`ATC_STR_RAT_FF`).
5. Geofence breach test, then a coverage mission in an open area.
6. Blades last, after the full go/no-go in [`BUILD.md`](BUILD.md).

Built one? Please file an
[adaptation report](https://github.com/zohebzma2-cmyk/autonomous-mower/issues/new?template=adaptation-report.md)
with your controller's answers to the §1 table, so the next person can skip the bench work.
