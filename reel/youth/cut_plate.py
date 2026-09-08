# -*- coding: utf-8 -*-
"""Cuts the take to the edit, corrects the camera angle and grades to the
brand palette. Video and audio are cut separately with identical ranges so a
dropped frame can never drift the two apart."""
import json, os, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC  = os.path.join(HERE, "youth.mp4")
OUT  = os.path.join(HERE, "cutsegs")
os.makedirs(OUT, exist_ok=True)

# v3-youth-fix.md, scaled from the 1080x1920 it was written for to 1440x2560
FIX = ("perspective=x0=-35:y0=0:x1=1475:y1=0:x2=0:y2=2560:x3=1440:y3=2560"
       ":sense=destination,scale=1440:2637,crop=1440:2280:0:317,scale=1440:2560")
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
