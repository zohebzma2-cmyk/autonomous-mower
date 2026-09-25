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
# Optional (flags): --kicad   KiCad 9 for the MowerCarrier PCB gates (macOS, ~1.3 GB)
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
fi

say "done — now run:  PATH=\"$BIN:\$PATH\" ./scripts/check.sh --full"
case ":$PATH:" in *":$BIN:"*) ;; *) echo "(add $BIN to PATH in your shell profile)";; esac
