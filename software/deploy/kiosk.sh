#!/usr/bin/env bash
# On-unit touchscreen: wait for the companion server, then open the control UI
# full-screen in Chromium (kiosk). Autostart this on the Pi desktop session.
set -u
URL="http://localhost:8080/"

# wait for the companion to come up (systemd service mower-companion)
until curl -fsS "$URL" >/dev/null 2>&1; do sleep 1; done

# stop the screen blanking / power management on the kiosk display
xset s off -dpms s noblank 2>/dev/null || true
unclutter -idle 2 &     # hide the cursor (apt install unclutter)

exec chromium-browser \
  --kiosk --incognito --noerrdialogs --disable-infobars \
  --disable-session-crashed-bubble --disable-pinch \
  --check-for-update-interval=31536000 \
  --app="$URL"
