# -*- coding: utf-8 -*-
"""Single pass compositor for the youth reel.

Everything that moves is done here rather than in ffmpeg filters so nothing
cuts: the plate arrives already dissolved between beats, this adds one slow
continuous push in across the whole reel, dims and softens the picture only
while the budget panel is up, then lays the scrim and the captions on top.
Reads rgb24 frames on stdin, writes rgb24 frames on stdout."""
import sys, os, json, numpy as np
from PIL import Image, ImageFilter, ImageEnhance

HERE = os.path.dirname(os.path.abspath(__file__))
SW, SH = 1152, 2048          # plate
W, H = 1080, 1920            # output
FPS = 30
Z0, Z1 = 1.00, 1.0667        # slow push in; ends at 1:1 with the output
ANCH = 0.35
NPX = SW * SH * 3

panel = json.load(open(os.path.join(HERE, "panel5.json")))
PDIM = {int(k): v for k, v in panel["dim"].items()}
scrim = Image.open(os.path.join(HERE, "scrim.png")).convert("RGBA")

# a whisper of a vignette so the eye settles on her and the text sits on
# something rather than floating on a flat rectangle
yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
r = np.sqrt(((xx - W / 2) / (W / 2)) ** 2 + ((yy - H * 0.44) / (H / 2)) ** 2)
vig = np.clip(1.0 - 0.20 * np.clip((r - 0.55) / 0.75, 0, 1) ** 2 * 3.0, 0.80, 1.0)[..., None]

N = int(sys.argv[1])
inp, out = sys.stdin.buffer, sys.stdout.buffer
for i in range(N):
    buf = inp.read(NPX)
    if len(buf) < NPX:
        break
    im = Image.frombuffer("RGB", (SW, SH), buf, "raw", "RGB", 0, 1)
    z = Z0 + (Z1 - Z0) * (i / max(1, N - 1))
    cw, ch = SW / z, SH / z
    x0, y0 = (SW - cw) / 2.0, (SH - ch) * ANCH
    im = im.resize((W, H), Image.LANCZOS, box=(x0, y0, x0 + cw, y0 + ch))

    dim = PDIM.get(i, 0.0)
    if dim > 0.001:
        im = im.filter(ImageFilter.GaussianBlur(5.5 * dim))
        im = ImageEnhance.Brightness(im).enhance(1.0 - 0.50 * dim)
        im = ImageEnhance.Color(im).enhance(1.0 - 0.30 * dim)

    a = (np.asarray(im, dtype=np.float32) * vig).clip(0, 255).astype(np.uint8)
    im = Image.fromarray(a, "RGB").convert("RGBA")

    if dim > 0.001:
        p = os.path.join(HERE, "panel5", "p%05d.png" % i)
        if os.path.exists(p):
            im.alpha_composite(Image.open(p).convert("RGBA"))
    im.alpha_composite(scrim)
    c = os.path.join(HERE, "cap5", "f%05d.png" % i)
    if os.path.exists(c):
        im.alpha_composite(Image.open(c).convert("RGBA"))
    out.write(im.convert("RGB").tobytes())
out.flush()
