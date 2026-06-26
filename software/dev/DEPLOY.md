# Deploy on the Raspberry Pi 5 (on-unit)

Make the unit **boot straight into the control screen** on its touchscreen, with the companion
running as a service. The iPad just opens the same URL over WiFi — no install on the iPad.

## 1. One-time setup (on the Pi)
```bash
sudo apt update && sudo apt install -y python3-pip chromium-browser unclutter
pip3 install pymavlink                       # for the real Pixhawk / SITL
git clone <your-repo> ~/autonomous-mower     # or copy the software/ folder over
# enable the two CSI cameras + the serial port to the Pixhawk:
sudo raspi-config        # Interface: Camera ON, Serial Port: login-shell OFF / hardware ON
```
Wire the Pixhawk TELEM2 ↔ Pi UART (or just USB) per `docs/WIRING.md`. `/dev/serial0` is the Pi UART;
if you use USB instead, change the service `--mav` to e.g. `udp:127.0.0.1:14550` or the ACM device.

## 2. Companion as a service (auto-starts, auto-restarts)
```bash
sudo cp ~/autonomous-mower/software/deploy/mower-companion.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now mower-companion
systemctl status mower-companion             # should be active (running)
journalctl -u mower-companion -f             # live logs
```
Now `http://<pi-ip>:8080/` works from the **iPad** (same WiFi).

## 3. On-unit touchscreen kiosk
```bash
chmod +x ~/autonomous-mower/software/deploy/kiosk.sh
mkdir -p ~/.config/autostart
cat > ~/.config/autostart/mower-kiosk.desktop <<'EOF'
[Desktop Entry]
Type=Application
Name=Mower Kiosk
Exec=/home/pi/autonomous-mower/software/deploy/kiosk.sh
X-GNOME-Autostart-enabled=true
EOF
```
Reboot — the touchscreen comes up full-screen on the control UI; the companion service is already
running underneath. (Raspberry Pi OS **with desktop**; for Lite, add a minimal X/wayland + chromium.)

## 4. RTK corrections (NTRIP)
Stream RTCM3 to the Pixhawk for the cm-level fix: either inject via QGroundControl's NTRIP client on
the iPad/laptop, or run an NTRIP client on the Pi that forwards to the FC. Use a free state-DOT CORS
mount within ~20 km, or add your own base station later.

## Update / rollback
`git pull && sudo systemctl restart mower-companion` (the kiosk just reloads the page). The companion
is pure-stdlib, so updates are instant; only the `--mav` path needs pymavlink.
