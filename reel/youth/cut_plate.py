# -*- coding: utf-8 -*-
"""Cuts the take to the edit, corrects the camera angle and grades to the
brand palette. Video and audio are cut separately with identical ranges so a
dropped frame can never drift the two apart."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "youth.mp4")
OUT  = os.path.join(HERE, "cutsegs")
os.makedirs(OUT, exist_ok=True)

# The camera sat below her eye line. v3-youth-fix.md answers that with a
# keystone, a 3 percent vertical stretch and a sky crop rescaled to full
# height - which together made her face 13.7 percent taller than life.
# This is a crop and nothing else: 307 rows of sky come off the top, and the
# width is cropped with it so the frame stays exactly 9:16. Raising her eye
# line into the upper third is what kills the shot-from-below read; no pixel
# is ever stretched.
FIX = "crop=1260:2240:90:307"
# shadows toward navy, highlights toward cream, contrast reined in, sky pulled back
GRADE = ("eq=contrast=0.95:saturation=0.90:gamma=1.03,"
         "colorbalance=rs=-0.05:bs=0.07:rm=0.00:bm=0.03:rh=0.05:gh=0.02:bh=-0.03,"
         "unsharp=5:5:0.4")

cuts = json.load(open(os.path.join(HERE, "cuts.json")))
for i, (a, b) in enumerate(cuts):
    d = b - a
    v = os.path.join(OUT, "c%02d.mp4" % i)
    w = os.path.join(OUT, "a%02d.wav" % i)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % a, "-t", "%.3f" % d,
                    "-i", SRC, "-vf", "%s,%s,fps=30" % (FIX, GRADE), "-an",
                    "-c:v", "libx264", "-preset", "medium", "-crf", "16", v], check=True)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % a, "-t", "%.3f" % d,
                    "-i", SRC, "-vn", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", w],
                   check=True)
    print("cut %2d  %7.3f -> %7.3f  (%.3fs)" % (i, a, b, d), flush=True)

for tag, ext, out in (("c", "mp4", "plate_v.mp4"), ("a", "wav", "plate_a.wav")):
    lst = os.path.join(HERE, tag + "list.txt")
    with open(lst, "w") as f:
        for i in range(len(cuts)):
            f.write("file '%s'\n" % os.path.join(OUT, "%s%02d.%s" % (tag, i, ext)))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", os.path.join(HERE, out)], check=True)
print("plate built")
