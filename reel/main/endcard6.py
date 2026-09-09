# -*- coding: utf-8 -*-
"""End card for the main reel.

The two figures were already delivered by the panels, at 112px, over her; a
card that repeated them would be the third time. So this one states what they
add up to, and carries the ask in the brand gold. The source line is the one
the budget document puts on its own pages."""
import os, subprocess
import numpy as np
from PIL import Image, ImageDraw
import caps

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, DUR = 1080, 1920, 30, 4.9
NAVY, MID = (11, 43, 68), (18, 61, 96)
GOLD, CREAM = (245, 176, 74), (251, 250, 246)
RIGHT = 890                       # text right edge, RTL
RULE = 922

def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def ground():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    k = np.clip(0.30 * (xx / W) + 0.70 * (1 - yy / H), 0, 1)[..., None]
    g = np.array(NAVY, np.float32) + (np.array(MID, np.float32) - np.array(NAVY, np.float32)) * k
    r = np.sqrt(((xx - W * 0.30) / (W * 1.05)) ** 2 + ((yy - H * 0.34) / (H * 0.62)) ** 2)
    g = g + (14.0 * np.clip(1 - r, 0, 1) ** 2)[..., None]
    return Image.fromarray(g.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")

BG = ground()

# (segments, font, colour, y, appear time). A segment is (text, size, weight)
# so the figure can be laid out left to right inside a right to left line.
BLOCKS = [
    ([("פחות לאנשי המקצוע", 84, 800)],   CREAM, 470, 0.10),
    ([("של העיר.", 84, 800)],             CREAM, 582, 0.10),
    ([("יותר לקבלנים מבחוץ.", 84, 800)],  CREAM, 694, 0.62),
    ([("ב-15 באוקטובר נדון", 56, 500)],   CREAM, 882, 1.20),
    ([("בעתירה שהגשנו.", 56, 500)],       CREAM, 958, 1.20),
    ([("דרשו לעצור את עדכון התקציב.", 62, 800)], GOLD, 1126, 1.85),
    ([("מקור: מסמך עדכון תקציב 2026, עיריית חריש", 32, 400)], (168, 190, 210), 1362, 2.45),
]

def frame(t):
    img = BG.copy()
    d = ImageDraw.Draw(img)
    k = ease((t - 0.10) / 0.55)
    if k > 0:
        d.rectangle([RULE, 470, RULE + 5, 470 + int(736 * k)],
                    fill=(*GOLD, int(230 * k)))
    for segs, col, y, t0 in BLOCKS:
        a = ease((t - t0) / 0.45)
        if a <= 0: continue
        rise = int((1 - a) * 14)
        x = RIGHT
        for s, size, weight in segs:
            f = caps.F(size, weight)
            w = caps.tw(d, s, f)
            d.text((x - w, y + rise), s, font=f, fill=(*col, int(255 * a)),
                   direction="ltr" if caps.is_num(s) else "rtl")
            x -= w
    return img

if __name__ == "__main__":
    out = os.path.join(HERE, "ec6"); os.makedirs(out, exist_ok=True)
    n = int(DUR * FPS)
    for i in range(n):
        frame(i / FPS).convert("RGB").save(os.path.join(out, "e%05d.png" % i))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
        "-i", os.path.join(out, "e%05d.png"), "-c:v", "libx264", "-preset", "slow",
        "-crf", "16", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-colorspace", "bt709",
        os.path.join(HERE, "endcard6.mp4")], check=True)
    print("end card %d frames (%.1fs)" % (n, DUR))
