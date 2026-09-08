# -*- coding: utf-8 -*-
"""Renders the whole youth caption track as transparent frames.
The scrim is a single static image composited later in ffmpeg, so each frame
here carries only the text."""
import json, os, sys
from PIL import Image
import caps

HERE  = os.path.dirname(os.path.abspath(__file__))
OUT   = os.path.join(HERE, "cap5"); os.makedirs(OUT, exist_ok=True)
FPS   = 30
track = json.load(open(os.path.join(HERE, "caption-track.json"), encoding="utf-8"))
DUR   = 67.94
blank = Image.new("RGBA", (1080, 1920), (0, 0, 0, 0))

n = int(DUR * FPS)
last_key, reuse = None, 0
for i in range(n):
    t = i / FPS
    live = [c for c in track if c["start"] - 0.05 <= t <= c["end"]]
    # a frame is fully determined by which words are out and how far into their
    # 140ms entrance they are; quantise that so identical frames are hard linked
    key = tuple((c["start"], min(len(c["times"]),
                 sum(1 for x in c["times"] if t >= x)),
                 round(min(1.0, max(0.0, (t - max([x for x in c["times"] if t >= x],
                      default=c["start"])) / 0.14)), 2)) for c in live)
    path = os.path.join(OUT, "f%05d.png" % i)
    if key == last_key and last_key is not None:
        os.link(os.path.join(OUT, "f%05d.png" % (i - 1)), path); reuse += 1; continue
    img = blank.copy()
    for c in live:
        caps.draw_cue(img, c["words"], c["times"], t, c["style"], lines_spec=c["lines"])
    img.save(path)
    last_key = key
print("frames %d (hard linked duplicates: %d)" % (n, reuse))
