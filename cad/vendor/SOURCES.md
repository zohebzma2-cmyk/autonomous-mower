# Vendor CAD Models — Autonomous Mower Retrofit

Sourced 2026-06-25. STEP files are AP203/AP214 ISO-10303-21 text — importable into FreeCAD/Fusion;
**OpenSCAD cannot read STEP natively** (use `import()` of an STL, or convert STEP→STL in FreeCAD first).
Dimensions are from manufacturer datasheets/product briefs unless marked "approx".

## Summary table

| # | Component | Status | Local file | Format | License | Real dims (mm) | URL |
|---|-----------|--------|-----------|--------|---------|----------------|-----|
| 1 | Raspberry Pi 5 Model B | **downloaded** | `pi5.stp` (37 MB) | STEP (ISO-10303-21, Creo assembly) | RPi mechanical model, free redistribution (rehosted by Elecrow, no login) | PCB 85 × 56 × ~1.6 (board); mounting holes 58 × 49 grid | https://www.elecrow.com/download/rasp/raspberry_pi_5.stp · Official (portal, JS-gated): https://pip.raspberrypi.com/categories/1099-raspberry-pi-5 |
| 2 | Raspberry Pi M.2 HAT+ (= AI Kit base; Hailo-8L is a separate M.2 2242 module) | **dims-only** | — | (STEP needs login on GrabCAD/Printables) | RPi product brief (PDF, free) | Board 65.1 × 56.7 × 5.6, 13 g; +16 mm GPIO stacking header. Hailo-8L = M.2 2242 (22 × 42) | Brief: https://datasheets.raspberrypi.com/m2-hat-plus/raspberry-pi-m2-hat-plus-product-brief.pdf · Free STEP (login): https://www.printables.com/model/1558288-raspberry-pi-hat-m2-reference-model |
| 3 | Holybro Pixhawk 6C flight controller | **needs-login** (GitBook file gate) | — | STEP (Pixhawk 6C case CAD 3D file) | Holybro, free | 84.8 × 44 × 12.4; weight 34.6 g (plastic case) / 59.3 g (alu) | Download page: https://docs.holybro.com/autopilot/pixhawk-6c/download · Dims/specs: https://docs.holybro.com/autopilot/pixhawk-6c/technical-specification |
| 4 | ArduSimple simpleRTK2B (u-blox ZED-F9P) | **dims-only** | — | (STEP on GrabCAD = login) | board, vendor docs | Arduino-UNO form factor **69 × 53**; mounting per Uno footprint | Product/datasheet: https://www.ardusimple.com/product/simplertk2b/ · Datasheet PDF: https://www.mouser.com/datasheet/2/1042/ArduSimple_11162020_AS_RTK2B_F9P_L1L2_NH_02-1923617.pdf · GrabCAD (login): https://grabcad.com/library/ardusimple-simplertk2b-and-simplertk2b-lite-1 |
| 5 | Slamtec RPLIDAR A1M8 | **dims-only** | — | (TraceParts STEP/STL = login) | Slamtec, datasheet free | Scanner core ø **96.8** (diameter), height ~**41**, ~190 g (kit). (55 mm = internal scan-core width) | Datasheet: https://bucket.download.slamtec.com/b90ae0a89feba3756bc5aaa0654c296dc76ba3ff/LD108_SLAMTEC_rplidar_datasheet_A1M8_v2.2_en.pdf · Free STEP/STL (login): https://www.traceparts.com/en/product/shanghai-slamtec-co-ltd-laser-radar-rplidar-a1m8?Product=90-28042022-033870 |
| 6 | Raspberry Pi Camera Module 3 (Standard + Wide) | **downloaded** | `cam_module3_step/Camera_module_3_std_model_simple.stp` (31 MB) + `..._wide_model_simple.stp` (30 MB) | STEP AP214 | Raspberry Pi official, free | PCB 25 × 24 × ~11.5 tall (std); body ~23.86 × 19.61; mount holes ø2.2 on 21 × 12.5 grid | https://datasheets.raspberrypi.com/camera/camera-module-3-step.zip · Mech drawing: https://datasheets.raspberrypi.com/camera/camera-module-3-standard-mechanical-drawing.pdf |
| 7 | 12V linear actuator ~100 mm stroke — **Actuonix L16-100** | **dims-only** | — | (STEP via Actuonix site form) | Actuonix datasheet free | Stroke **100**; closed length (hole-to-hole) **168**; body cross-section ~12.7 × 22.5; mass ~74 g; 12 V | Product: https://www.actuonix.com/l16 · Datasheet: https://www.actuonix.com/assets/images/datasheets/ActuonixL16Datasheet.pdf |
| 8 | GPS survey / helical antenna puck (generic) | **dims-only** | — | (GrabCAD STEP/STL = login) | community | Typical survey puck ø **60–66**, height **18–25** (e.g. ArduSimple/u-blox ANN-MB ø ~60). Helical (e.g. Harxon) ø ~50, h ~50 | GrabCAD GPS antenna models: https://grabcad.com/library/gps-antenna-3 · helical: https://grabcad.com/library/tag/helical%20antenna |
| 9 | 22 mm industrial mushroom E-stop button (generic) | **needs-login** (GrabCAD) | — | STEP | community, free w/ GrabCAD login | Panel cutout ø **22.5**; mushroom head ø **40**; body depth ~**50–65** behind panel (incl. 1NC block) | https://grabcad.com/library/22mm-emergency-stop-button-1 · https://grabcad.com/library/starelo-22mm-1nc-red-mushroom-emergency-stop-metal-latching-push-button-switch-1 · Siemens (TraceParts, login): https://www.traceparts.com/en/product/siemens-22mm-metal-round-complete-unit-combinationemergencystop-mushroom-pushbutton |
| 10 | DC-DC buck converter module (generic, LM2596) | **needs-login** (GrabCAD) | — | STEP | community, free w/ login | LM2596 module ~**44 × 21 × 13.65** (typical) | https://grabcad.com/library/lm2596-dc-dc-buck-converter-module-1 · STEP listing: https://marathon-os.com/library/lm2596-dcdc-buck-converter-module-3d-6811d70143b4d50b11a59159 |

## Notes / caveats

- **OpenSCAD note:** all three downloaded files are STEP. To use as visual context in OpenSCAD,
  convert STEP→STL in FreeCAD (`Part workbench → import → export mesh`) and `import("...stl")`.
  Three.js can load STL directly; for STEP use a converter or occt-import-js.
- **GrabCAD / Printables / TraceParts / 3Dfindit** all require a free account login to download —
  could not fetch programmatically. URLs recorded for manual download.
- **Holybro Pixhawk 6C** CAD is served through a GitBook file gate (`/files/<id>` 404s to anonymous
  curl); download manually from the docs "Download" page. The CAD provided is the **case** model.
- **Pi 5 official STEP** lives behind the JS-rendered Product Information Portal (pip.raspberrypi.com).
  The Elecrow copy downloaded here is the genuine RPi Creo-exported `00-RASPBERRY-PI-5-SBC-SIMPLE_ASM`
  STEP (verified header), rehosted with no login required.
- **Hailo-8L / AI Kit:** the "AI Kit" is the M.2 HAT+ board (#2) populated with a Hailo-8L M.2 2242
  module (22 × 42 mm). No separate official Hailo STEP found without login.
- Dimensions marked "approx"/"typical" for generic parts (#8, #9, #10) are representative datasheet
  values, NOT measured from a downloaded model — verify against the specific part chosen.
