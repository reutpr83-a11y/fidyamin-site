# -*- coding: utf-8 -*-
"""End card for the youth reel.

The card the earlier cut ended on belonged to the budget video and its
figures were the budget's, not the youth's. This one closes on the number
the reel actually made its case with, credits the document it came from and
carries her ask in the brand gold."""
import os, subprocess
import numpy as np
from PIL import Image, ImageDraw
import caps

HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS, DUR = 1080, 1920, 30, 4.0
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
    ([("653", 96, 800), (" אלף ₪ פחות", 84, 800)], CREAM, 636, 0.10),
    ([("למערכי הנוער בחריש.", 84, 800)],           CREAM, 748, 0.10),
    ([("הרימו יד ואישרו", 60, 500)],               CREAM, 932, 0.75),
    ([("בלי לדעת על מה.", 60, 500)],               CREAM, 1012, 0.75),
    ([("דרשו לבטל את עדכון התקציב.", 60, 800)],    GOLD,  1188, 1.45),
    ([("מקור: מסמך עדכון תקציב 2026, עיריית חריש", 32, 400)], (168, 190, 210), 1428, 2.05),
]

def frame(t):
    img = BG.copy()
    d = ImageDraw.Draw(img)
    k = ease((t - 0.10) / 0.55)
    if k > 0:
        d.rectangle([RULE, 636, RULE + 5, 636 + int(612 * k)],
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
    out = os.path.join(HERE, "ec4"); os.makedirs(out, exist_ok=True)
    n = int(DUR * FPS)
    for i in range(n):
        frame(i / FPS).convert("RGB").save(os.path.join(out, "e%05d.png" % i))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-framerate", str(FPS),
        "-i", os.path.join(out, "e%05d.png"), "-c:v", "libx264", "-preset", "slow",
        "-crf", "16", "-pix_fmt", "yuv420p", "-color_primaries", "bt709",
        "-color_trc", "bt709", "-colorspace", "bt709",
        os.path.join(HERE, "endcard4.mp4")], check=True)
    print("end card %d frames (%.1fs)" % (n, DUR))
