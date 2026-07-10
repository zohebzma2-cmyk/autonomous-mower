#!/usr/bin/env bash
# Download the free, official 3D CAD + drawings for the retrofit components.
# All URLs verified live (July 2026). Files land in cad/vendor/ (gitignored — large binaries).
# See docs/SOURCING-AND-FABRICATION.md for the full source table.
set -u
cd "$(dirname "$0")"
UA="Mozilla/5.0"
get(){ echo "→ $2"; curl -fL --retry 2 --max-time 120 -A "$UA" -o "$2" "$1" \
       && echo "  ok ($(du -h "$2" | cut -f1))" || echo "  FAILED (try in a browser): $1"; }

# component STEP / IGES / DXF (real solid/CAD)
get "https://www.ardusimple.com/wp-content/uploads/2026/04/AS-RTK2B-F9P-L1L2-NH-03-R00.step" "simpleRTK2B.step"
get "https://cdn.shopify.com/s/files/1/0061/7735/7891/files/PA-14P.stp" "PA-14P.stp"
get "https://cdn.shopify.com/s/files/1/0061/7735/7891/files/PA-14P.DWG" "PA-14P.DWG"
get "https://download-en.slamtec.com/api/download/rplidar-core-a1m8-r1-model-3d-igs/2.0?lang=netural" "rplidar_a1m8.igs"
get "https://pip-assets.raspberrypi.com/categories/892-raspberry-pi-5/documents/RP-010083-CA-1-rpi-5%203D%20STEP%20-%20No%20Graphics%20small%20file.zip" "raspberry-pi-5_step.zip"
get "https://pip-assets.raspberrypi.com/categories/1207-design-files/documents/RP-008154-DS-1-camera-module-3-step.zip" "camera-module-3_step.zip"
get "https://dl.espressif.com/dl/schematics/esp32_devkitc_v4_dimensions.dxf" "esp32_devkitc_v4.dxf"

# drawings / datasheets (dimensioned PDFs)
get "https://raw.githubusercontent.com/ardusimple/simpleRTK2B/master/Mechanical/simpleRTK2B_PCB.PDF" "simpleRTK2B_drawing.pdf"
get "https://f.hubspotusercontent40.net/hubfs/7717445/PDFs/Actuator%20datasheets/PA-14P%20datasheet.pdf" "PA-14P_datasheet.pdf"
get "https://download-en.slamtec.com/api/download/rplidar-core-a1m8-r1-model-2d-pdf/2.0?lang=en" "rplidar_a1m8_drawing.pdf"
get "https://datasheets.raspberrypi.com/rpi5/raspberry-pi-5-mechanical-drawing.pdf" "raspberry-pi-5_drawing.pdf"
get "https://datasheets.raspberrypi.com/camera/camera-module-3-standard-mechanical-drawing.pdf" "camera-module-3_drawing.pdf"
get "https://content.u-blox.com/sites/default/files/documents/ANN-MB_DataSheet_UBX-18049862.pdf" "ANN-MB-00_datasheet.pdf"
get "https://resources.kohler.com/power/kohler/enginesUS/pdf/32_690_03_EN.pdf" "kohler-7000_service-manual.pdf"

# Pixhawk 6C STEP + AI HAT+ brief are best fetched via a browser (Holybro download page / GrabCAD).
echo "Done. Pixhawk 6C STEP: https://docs.holybro.com/autopilot/pixhawk-6c/download  (browser)"
