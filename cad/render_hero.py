#!/usr/bin/env python3
# SPDX-License-Identifier: MIT
"""Re-shoot the README hero orbit GIF and the 1200x630 social card from the CAD.

    python3 cad/render_hero.py          (needs openscad on PATH + Pillow)

Frames: assembly.scad with SHOW="hero" (base machine + every retrofit subsystem,
no Phase-3 attachments), 24 steps of 15 deg at a 62 deg tilt, 640x400, 100 ms,
looping — the same framing as the original hero, re-rendered so it never goes
stale against the CAD again.
"""
import os
import subprocess
import sys
import tempfile

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "renders")
FRAMES, TILT, SIZE, MS = 24, 62, (640, 400), 100


CENTER = (250, 0, 620)                # mm — middle of the machine incl. the GPS mast


def shot(path, size, rot_z, tilt=TILT, dist=5600, extra=()):
    cx, cy, cz = CENTER
    cmd = ["openscad", "-o", path, f"--imgsize={size[0]},{size[1]}", "--colorscheme=Tomorrow",
           f"--camera={cx},{cy},{cz},{tilt},0,{rot_z},{dist}",
           "-D", 'SHOW="hero"', *extra, os.path.join(HERE, "assembly.scad")]
    subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def font(size, bold=False):
    for f in ("/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
              if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"):
        if os.path.exists(f):
            return ImageFont.truetype(f, size, index=1 if (bold and f.endswith(".ttc")) else 0)
    return ImageFont.load_default()


def main():
    with tempfile.TemporaryDirectory() as tmp:
        frames = []
        for i in range(FRAMES):
            p = os.path.join(tmp, f"f{i:02d}.png")
            shot(p, SIZE, 25 + i * 360 / FRAMES)
            frames.append(Image.open(p).convert("RGB").quantize(colors=128, method=Image.MEDIANCUT))
            sys.stdout.write(f"\rframe {i + 1}/{FRAMES}"); sys.stdout.flush()
        gif = os.path.join(OUT, "hero-orbit.gif")
        frames[0].save(gif, save_all=True, append_images=frames[1:], duration=MS, loop=0, optimize=True)
        print(f"\nwrote {gif} ({os.path.getsize(gif) // 1024} KB)")

        # social card: 1200x630, render in the top 546 px, caption strip below
        p = os.path.join(tmp, "card.png")
        shot(p, (1200, 546), 25, tilt=62, dist=4700)
        card = Image.new("RGB", (1200, 630), (248, 248, 248))
        card.paste(Image.open(p).convert("RGB"), (0, 0))
        d = ImageDraw.Draw(card)
        d.rectangle([0, 546, 1200, 630], fill=(14, 17, 22))
        title = "Autonomous Zero-Turn Retrofit"
        d.text((28, 588), title, font=font(30, True), fill=(63, 185, 80), anchor="lm")
        x = 28 + d.textlength(title, font=font(30, True)) + 14
        d.text((x, 590), "open-source ArduPilot kit for a 615 lb Gravely ZT X 52",
               font=font(20), fill=(175, 184, 193), anchor="lm")
        out = os.path.join(OUT, "social-card.png")
        card.save(out, optimize=True)
        print(f"wrote {out}")


if __name__ == "__main__":
    main()
