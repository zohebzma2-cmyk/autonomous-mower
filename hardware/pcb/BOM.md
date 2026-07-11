# MowerCarrier Rev A — Bill of Materials

Real, in-stock **LCSC / JLCPCB** part numbers. Nothing here is invented — where a
part or its assembly tier couldn't be verified this is flagged explicitly.
**Re-check Basic/Extended tier and stock at order time** (JLCPCB rotates its
library). Every through-hole (THT) part needs JLCPCB's separate hand/wave-solder
assembly billed per joint — or hand-solder them yourself (usually cheaper).

## 1 · 12 V power input (high current)

| Ref | Function | LCSC | MPN | Package | ~$ | Tier |
|-----|----------|------|-----|---------|----|------|
| J1 | XT60 power in, right-angle | **C98732** | XT60PW-M (AMASS) | R/A THT | 0.39 | Ext · needs fixture — hand-solder |
| F0 | Blade-fuse holder (ATO), 30 A | **C352820** | 3557-2 (Keystone) | THT | 1.40 | Ext (single-clip alt C3205403 ×2) |
| TB (2P) | Screw terminal 5.08 mm 2-pole | **C474952** | KF128-5.08-2P | THT ~24 A | 0.08 | verify |
| TB (3P) | Screw terminal 5.08 mm 3-pole | **C474953** | KF128-5.08-3P | THT ~24 A | 0.16 | verify (alt C474941) |

## 2 · Reverse-polarity + load-dump protection

| Ref | Function | LCSC | MPN | Package | ~$ | Tier |
|-----|----------|------|-----|---------|----|------|
| Q1 | Reverse-polarity P-FET | **C2564** | IRF4905 (Infineon) | TO-220 | 1.00 | Ext ✓ |
| D1 | TVS load-dump 16 V | **C151254** | SMBJ16A (Littelfuse) | SMB | 0.07 | (15 V alt C135046) |

> **Q1 heat:** one 20 mΩ P-FET at 30 A dissipates ~18 W — give it big copper, or
> **parallel two IRF4905**. For a full ISO-7637 load-dump use a 1500 W **SMCJ**
> TVS instead of the 600 W SMBJ (fine for ESD/transient).

## 3 · Safety relays + coil drivers

| Ref | Function | LCSC | MPN | Package | ~$ | Tier |
|-----|----------|------|-----|---------|----|------|
| K1,K2 | Power relay 30 A SPDT, 12 V coil | **C125736** | SLA-12VDC-SL-C (Songle) | THT | 0.79 | verify |
| K1,K2 (alt) | 40 A SPST-NO, 12 V coil | **C86668** | SLD-12VDC-1A (Songle) | THT | 0.61 | 40 A but NO-only |
| Q2,Q3 | Coil low-side driver N-FET | **C20917** | AO3400A (AOS) | SOT-23 | 0.04 | **Basic** ✓ |
| D2,D3 | Flyback (Schottky, high-margin) | **C8678** | SS34 (MDD) | SMA | 0.013 | **Basic** ✓ (or 1N4148W C81598) |

> A **40 A SPDT** (SLD-12VDC-1C) is a real Songle part but no LCSC C-number was
> confirmed — verify directly, or use the 30 A SPDT (C125736) / 40 A SPST-NO
> (C86668). The DRIVE relay only needs NO (switches motor V+ on), so the 40 A
> SPST-NO is fine there.

## 4 · ESP32-DevKitC carrier

| Ref | Function | LCSC | MPN | Package | ~$ | Tier |
|-----|----------|------|-----|---------|----|------|
| H1,H2 | Female header 2.54 mm 1×19 | **C319202** | 2.54-1×19P | THT | 0.06 | (alt 1×20 C50984 / cut 1×40 C9811) |

> **⚠ Highest-risk footprint:** ESP32-DevKit row spacing is **not** universal —
> genuine Espressif V4 = **1.0″ / 25.4 mm**, most clones = **0.9″ / 22.86 mm**.
> **Caliper your actual board before committing the footprint.** Two independent
> 1×19 strips let you set the measured pitch.

## 5 · I/O breakout

| Ref | Function | LCSC | MPN | Package | ~$ | Tier |
|-----|----------|------|-----|---------|----|------|
| J_* | Male pin header 2.54 mm 1×40 (cut) | **C2337** | 2.54-1×40P | THT | 0.08 | likely Basic |
| TB_POT/ESTOP | Screw terminal 5.08 3-pole | C474953 | KF128-5.08-3P | THT | 0.16 | (§1) |

## 6 · Indicators & passives (0805, all JLCPCB **Basic**)

| Function | Value | LCSC | ~$ |
|----------|-------|------|----|
| Gate resistors | 100 Ω | **C17408** | 0.002 |
| LED series | 220 Ω | **C17557** | 0.001 |
| General | 1 kΩ | **C17513** | 0.002 |
| General | 2 kΩ | **C17604** | 0.001 |
| Pulldowns/pullups | 10 kΩ | **C17414** | 0.0014 |
| Decoupling | 100 nF 50 V X7R | **C49678** | 0.002 |
| Local bulk | 10 µF 25 V | **C15850** | 0.012 |
| Status LED (green) | 0805 | **C2297** | 0.017 |
| Status LED (red) | 0805 | **C84256** | 0.019 |
| Rail bulk | 470 µF 25 V | **C43839** (radial TH) / **C72518** (SMD) | 0.02–0.04 · Ext |

## Rough cost — 5 boards, JLCPCB

| Line | Estimate |
|------|----------|
| PCB fab (2-layer, 2 oz, 120×100, ×5) | $25–40 |
| SMD PCBA (all Basic passives + AO3400 + LEDs) | $13–25 |
| Components (BOM) ×5 | $25–40 |
| **You hand-solder THT (XT60/fuse/relays/terminals)** | **≈ $70–110 total** |
| JLCPCB does full SMD **+ THT** assembly | ≈ $130–190 total |

**Cost lever:** let JLCPCB place only the cheap **SMD Basic** parts and
hand-solder the THT connectors/relays yourself — this roughly **halves** assembly
cost and dodges the XT60 wave-solder fixture fee.

### Verified-tier summary
- **Confirmed Extended:** IRF4905 (C2564), XT60 (C98732), fuse holder (C352820), 470 µF caps.
- **Confirmed Basic:** all §6 passives/LEDs, AO3400A (C20917), 1N4148W (C81598), SS34 (C8678).
- **Verify at order (page fetch was blocked):** both terminal blocks, both relays, both TVS, both headers.
- **Not found:** 40 A **SPDT** relay C-number, a Basic 470 µF/25 V electrolytic, a sub-10 mΩ 40 V+ P-FET.
