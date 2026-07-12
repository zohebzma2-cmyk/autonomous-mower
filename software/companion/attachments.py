"""
Attachment & powertrain policy — TPMS, ignition/choke, power bagger,
blower/trimmer boom, tow-behind sprayer.

Pure, testable functions in the same spirit as safety.py: the sim (and later
the real drivers) write live values into shared state; THIS module owns the
rules — interlocks, thresholds, and control math. Nothing here replaces the
hardware kill chain; the e-stop drops every attachment relay in hardware
(docs/WIRING.md) and the software mirrors that.

Status: DESIGN + SIM. Interlocks and math are tested; hardware drivers land
with the physical build (additive iteration — see docs/DESIGN-LOG.md).
"""

# ---------------------------------------------------------------- TPMS
# External valve-stem BLE/RF sensors on all four tyres. Nominals are the
# reference machine's cold pressures — SET TO YOUR SIDEWALL / MANUAL SPEC.
TIRE_NOMINAL_PSI = {"rl": 12.0, "rr": 12.0, "fl": 20.0, "fr": 20.0}
TIRE_WARN_FRAC = 0.25          # warn beyond ±25% of nominal
TIRE_NAMES = {"rl": "rear-left", "rr": "rear-right", "fl": "front-left", "fr": "front-right"}

def tpms_warnings(tires):
    """tires: {'rl': psi, ...} -> list of human warnings (empty = all good).
    Low tyres change ride height and steering scrub; they also un-level the
    deck, so the cut goes wavy long before a flat is obvious."""
    warns = []
    for k, nominal in TIRE_NOMINAL_PSI.items():
        psi = (tires or {}).get(k)
        if psi is None:
            continue
        if abs(psi - nominal) > nominal * TIRE_WARN_FRAC:
            state = "low" if psi < nominal else "high"
            warns.append(f"{TIRE_NAMES[k]} tyre {state} ({psi:.1f} vs {nominal:.0f} psi)")
    return warns

# ---------------------------------------------------------------- ignition + choke
# Kohler 7000 (KT725): electric start via the key-switch solenoid; many 7000s
# carry Smart-Choke (auto). The retrofit actuates the KEY CIRCUIT via a
# starter relay and — on manual-choke variants — a choke servo. The kill side
# is the existing ignition-kill line in the e-stop chain.
CRANK_MAX_S = 5.0              # never crank the starter longer than this
CRANK_REST_S = 10.0            # starter cool-down between attempts
CHOKE_FULL_BELOW_C = 10.0      # cold start: full choke
CHOKE_HALF_BELOW_C = 20.0      # cool start: half choke

def choke_for(temp_c):
    """Choke position 0..1 for a MANUAL-choke engine (Smart-Choke variants
    ignore this). Fully open (0) once warm."""
    if temp_c is None or temp_c < CHOKE_FULL_BELOW_C:
        return 1.0
    if temp_c < CHOKE_HALF_BELOW_C:
        return 0.5
    return 0.0

def can_crank(d):
    """Interlocks before the starter relay may close."""
    if d.get("estop"):
        return False, "E-STOP engaged"
    if d.get("engine") == "run":
        return False, "engine already running"
    if d.get("engine") == "crank":
        return False, "already cranking"
    if d.get("blade"):
        return False, "blade engaged — PTO must be off to start"
    if d.get("mission") == "running":
        return False, "mission running"
    return True, None

# ---------------------------------------------------------------- power bagger
# Twin-bin rear bagger (Gravely/Exmark dump-from-seat pattern) with an
# electric-actuator dump pivot. Fill is estimated from blade-on time scaled
# by camera grass coverage until a bin-full sensor exists.
BAGGER_FULL_MIN = 18.0         # minutes of heavy cut to fill the bins (tune on grass)
DUMP_RAISE_S, DUMP_HOLD_S, DUMP_LOWER_S = 3.0, 2.0, 3.0

def bagger_fill_step(fill_pct, blade_on, grass_pct, dt_s):
    """Advance the fill estimate by dt_s of mowing."""
    if not blade_on:
        return fill_pct
    rate = (100.0 / (BAGGER_FULL_MIN * 60.0)) * max(0.2, (grass_pct or 0) / 100.0)
    return min(100.0, round(fill_pct + rate * dt_s, 2))

def can_dump(d):
    if d.get("estop"):
        return False, "E-STOP engaged"
    if (d.get("speed") or 0) > 0.05:
        return False, "stop before dumping"
    if d.get("blade"):
        return False, "blade off before dumping"
    if (d.get("bagger") or {}).get("state") not in (None, "idle"):
        return False, "dump already in progress"
    return True, None

# ---------------------------------------------------------------- blower / trimmer boom
# A rotating boom on the front corner carries a 12/24V blower volute and a
# string-trimmer head — edging and blowing passes on the same RTK routes.
BOOM_MIN_DEG, BOOM_MAX_DEG = 0.0, 270.0
TRIM_MAX_SPEED = 1.0           # m/s — edging is a slow-roll operation

def clamp_boom(angle):
    return max(BOOM_MIN_DEG, min(BOOM_MAX_DEG, float(angle)))

def can_run_trimmer(d):
    """String head is a cutting tool: same respect as the blades."""
    if d.get("estop"):
        return False, "E-STOP engaged"
    if not d.get("armed"):
        return False, "arm first"
    if (d.get("speed") or 0) > TRIM_MAX_SPEED:
        return False, f"too fast for trimming (> {TRIM_MAX_SPEED} m/s)"
    return True, None

# ---------------------------------------------------------------- tow sprayer
# FIMCO 30-gal tow-behind with a 12V pump. The whole point of RTK speed
# control: application rate stays constant because pump duty follows ground
# speed, and the pump pauses in sharp turns so headlands don't get a
# double dose (that's how you burn stripes into a lawn with herbicide).
SPRAY_SWATH_M = 2.1            # boom coverage width (FIMCO 30-gal boom class)
SPRAY_RATE_L_PER_M2 = 0.012    # target application (~= 1.2 L / 100 m^2); calibrate per label
PUMP_MAX_LPM = 8.3             # ~2.2 GPM class 12V diaphragm pump
TURN_PAUSE_DPS = 25.0          # pause application when yawing faster than this

def sprayer_duty(speed_ms, turn_rate_dps=0.0):
    """Pump duty 0..1 for constant area application at this ground speed.
    Returns 0 while stopped or in a sharp turn (no double-dose headlands)."""
    if speed_ms is None or speed_ms <= 0.05:
        return 0.0
    if abs(turn_rate_dps) >= TURN_PAUSE_DPS:
        return 0.0
    lpm = speed_ms * SPRAY_SWATH_M * SPRAY_RATE_L_PER_M2 * 60.0
    return round(min(1.0, lpm / PUMP_MAX_LPM), 3)

def can_spray(d):
    if d.get("estop"):
        return False, "E-STOP engaged"
    if not (d.get("sprayer") or {}).get("attached"):
        return False, "sprayer not attached"
    if ((d.get("sprayer") or {}).get("tank_pct") or 0) <= 0:
        return False, "tank empty"
    return True, None
