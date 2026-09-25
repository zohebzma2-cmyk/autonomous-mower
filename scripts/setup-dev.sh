#!/usr/bin/env bash
# SPDX-License-Identifier: MIT
# One-shot dev setup: everything needed to run every gate in this repo locally.
#   ./scripts/setup-dev.sh            # idempotent — re-run any time
#
# Installs (user-level, no sudo, no Homebrew):
#   uv            -> ~/.local/bin/uv           (Python manager)
#   Python 3.12   -> .venv/ with requirements-dev.txt (GLB/GIF/docs/mypy/pymavlink)
#   OpenSCAD      -> macOS: ~/Applications/OpenSCAD.app + ~/.local/bin/openscad
#                    (a dev snapshot — it has the Manifold backend; the 2021 stable
#                    release takes ~55 min on the tyre group vs seconds here)
#                    Linux: prints the AppImage/apt route
# Optional (flags): --kicad   KiCad 9 + Java 25 + Freerouting + arduino-cli/ESP32 core:
#                             the MowerCarrier PCB generator/gates and the firmware compile gate
set -euo pipefail
cd "$(dirname "$0")/.."
BIN="$HOME/.local/bin"; mkdir -p "$BIN"
export PATH="$BIN:$PATH"

say() { printf '\n== %s\n' "$*"; }

say "uv"
if ! command -v uv >/dev/null; then
  curl -LsSf https://astral.sh/uv/install.sh | env UV_NO_MODIFY_PATH=1 UV_INSTALL_DIR="$BIN" sh
fi
uv --version

say "Python 3.12 venv (.venv) + requirements-dev.txt"
uv python install 3.12 >/dev/null
[ -x .venv/bin/python ] || uv venv -q --python 3.12 .venv
uv pip install -q --python .venv/bin/python -r requirements-dev.txt
.venv/bin/python --version

say "OpenSCAD"
if ! command -v openscad >/dev/null; then
  case "$(uname -s)" in
    Darwin)
      url=$(curl -sL https://files.openscad.org/snapshots/ | grep -oE 'OpenSCAD-[0-9.]+\.dmg' | sort -uV | tail -1)
      tmp=$(mktemp -d); curl -sL -o "$tmp/o.dmg" "https://files.openscad.org/snapshots/$url"
      hdiutil attach -nobrowse -quiet -mountpoint "$tmp/mnt" "$tmp/o.dmg"
      mkdir -p "$HOME/Applications"; rm -rf "$HOME/Applications/OpenSCAD.app"
      ditto "$tmp/mnt/OpenSCAD.app" "$HOME/Applications/OpenSCAD.app"
      hdiutil detach -quiet "$tmp/mnt"; rm -rf "$tmp"
      printf '#!/bin/sh\nexec "$HOME/Applications/OpenSCAD.app/Contents/MacOS/OpenSCAD" "$@"\n' > "$BIN/openscad"
      chmod +x "$BIN/openscad" ;;
    *) echo "Install an OpenSCAD dev snapshot (AppImage: https://openscad.org/downloads.html#snapshots)"
       echo "and put 'openscad' on PATH. Distro packages are often the 2021 release (slow, no Manifold)." ;;
  esac
fi
command -v openscad >/dev/null && openscad --version

if [ "${1:-}" = "--kicad" ]; then
  say "KiCad 9 (macOS)"
  if [ ! -x "$HOME/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli" ] && [ "$(uname -s)" = Darwin ]; then
    dmg=$(curl -sL https://downloads.kicad.org/kicad/macos/explore/stable | grep -oE 'kicad-unified-universal-9\.[0-9]+\.[0-9]+\.dmg' | sort -uV | tail -1)
    tmp=$(mktemp -d); curl -sL -o "$tmp/k.dmg" "https://downloads.kicad.org/kicad/macos/explore/stable/download/$dmg"
    hdiutil attach -nobrowse -quiet -mountpoint "$tmp/mnt" "$tmp/k.dmg"
    mkdir -p "$HOME/Applications"; ditto "$tmp/mnt/KiCad" "$HOME/Applications/KiCad"
    hdiutil detach -quiet "$tmp/mnt"; rm -rf "$tmp"
  fi
  printf '#!/bin/sh\nexec "$HOME/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli" "$@"\n' > "$BIN/kicad-cli"
  chmod +x "$BIN/kicad-cli"; kicad-cli version

  say "Java 25 JRE + Freerouting 1.9.0 (autorouter for hardware/pcb/kicad/gen_kicad.sh)"
  JDIR="$HOME/.local/share/java"; mkdir -p "$JDIR" "$HOME/.local/share/freerouting"
  if ! ls -d "$JDIR"/jdk-25*/ >/dev/null 2>&1; then
    arch=$(uname -m | sed 's/arm64/aarch64/; s/x86_64/x64/'); os=$([ "$(uname -s)" = Darwin ] && echo mac || echo linux)
    curl -sL "https://api.adoptium.net/v3/binary/latest/25/ga/$os/$arch/jre/hotspot/normal/eclipse" | tar -xz -C "$JDIR"
  fi
  J=$( (ls -d "$JDIR"/jdk-25*/Contents/Home/bin/java "$JDIR"/jdk-25*/bin/java 2>/dev/null || true) | head -1)  # macOS | Linux layout
  FRJ="$HOME/.local/share/freerouting/freerouting-1.9.0.jar"
  [ -f "$FRJ" ] || curl -sL -o "$FRJ" https://github.com/freerouting/freerouting/releases/download/v1.9.0/freerouting-1.9.0.jar
  # 1.9.0 on purpose: 2.x intermittently writes an empty .ses when run headless
  printf '#!/bin/sh\nexec "%s" -jar "%s" "$@"\n' "$J" "$FRJ" > "$BIN/freerouting"; chmod +x "$BIN/freerouting"
  "$J" -version 2>&1 | head -1

  say "arduino-cli + ESP32 core (firmware compile gate)"
  command -v arduino-cli >/dev/null || curl -fsSL https://raw.githubusercontent.com/arduino/arduino-cli/master/install.sh | BINDIR="$BIN" sh
  arduino-cli config init --overwrite >/dev/null
  arduino-cli config add board_manager.additional_urls https://espressif.github.io/arduino-esp32/package_esp32_index.json
  arduino-cli core update-index >/dev/null && arduino-cli core install esp32:esp32 >/dev/null
  CT="$HOME/Library/Arduino15/packages/builtin/tools/ctags/5.8-arduino11/ctags"
  if [ "$(uname -m)" = arm64 ] && [ -f "$CT" ] && file "$CT" | grep -q x86_64 && ! arch -x86_64 /usr/bin/true 2>/dev/null; then
    # Arduino's ctags is x86_64-only and needs Rosetta; our sketches declare functions before use,
    # so a no-op stub is enough (original kept alongside)
    mv "$CT" "$CT.x86_64"; printf '#!/bin/sh\nexit 0\n' > "$CT"; chmod +x "$CT"
  fi
  arduino-cli core list
fi

say "done — now run:  PATH=\"$BIN:\$PATH\" ./scripts/check.sh --full"
case ":$PATH:" in *":$BIN:"*) ;; *) echo "(add $BIN to PATH in your shell profile)";; esac
