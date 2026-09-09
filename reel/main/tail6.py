# -*- coding: utf-8 -*-
"""The held beat after her last word.

She stops speaking at 156.63 in the take and holds; the reel needs that hold
so the card can dissolve in on silence rather than over her last word. These frames
continue straight on from the last frame of the cut, so the join is not a cut
at all, and the push in comes to rest instead of stopping dead."""
import os, sys, json, subprocess
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
# same grade beats6.py cuts its segments with
GRADE = ("scale=1152:2048:flags=lanczos+accurate_rnd,"
         "eq=contrast=1.03:saturation=1.02:gamma=0.99,"
         "colorbalance=rs=-0.04:bs=0.06:rm=0.00:bm=0.02:rh=0.04:gh=0.01:bh=-0.03")
W, H, SW, SH, FPS = 1080, 1920, 1152, 2048, 30
# picks up on the frame after the last beat, computed rather than typed
_m = json.load(open(os.path.join(HERE, "map6.json")))
_take = _m["sources"][_m["takes"][-1]]      # the last beat's own take
SRC = _take["path"]
START = _m["beats"][-1][0] + _take["offset"] + _m["durs"][-1]
DUR = 0.85
Z, ANCH = 1.0667, 0.35

scrim = Image.open(os.path.join(HERE, "scrim.png")).convert("RGBA")
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.44) / (H / 2)) ** 2)
vig = np.clip(1.0 - 0.20 * np.clip((r - 0.55) / 0.75, 0, 1) ** 2 * 3.0, 0.80, 1.0)[..., None]

src = subprocess.Popen(["ffmpeg", "-v", "error", "-ss", "%.3f" % START, "-t", "%.3f" % DUR,
    "-i", SRC,
    "-vf", "%s,fps=30,setsar=1" % GRADE,
    "-an", "-f", "rawvideo", "-pix_fmt", "rgb24", "-"], stdout=subprocess.PIPE)
enc = subprocess.Popen(["ffmpeg", "-y", "-v", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
    "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-c:v", "libx264", "-preset", "slow",
    "-crf", "16", "-pix_fmt", "yuv420p", "-color_primaries", "bt709", "-color_trc", "bt709",
    "-colorspace", "bt709", os.path.join(HERE, "tail6.mp4")], stdin=subprocess.PIPE)

cw, ch = SW / Z, SH / Z
x0, y0 = (SW - cw) / 2.0, (SH - ch) * ANCH
n, npx = 0, SW * SH * 3
while True:
    buf = src.stdout.read(npx)
    if len(buf) < npx: break
    im = Image.frombuffer("RGB", (SW, SH), buf, "raw", "RGB", 0, 1)
    im = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))
    a = (np.asarray(im, np.float32) * vig).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(a, "RGB").convert("RGBA")
    im.alpha_composite(scrim)
    enc.stdin.write(im.convert("RGB").tobytes()); n += 1
enc.stdin.close(); enc.wait(); src.wait()
print("tail frames %d (%.2fs)" % (n, n / FPS))
