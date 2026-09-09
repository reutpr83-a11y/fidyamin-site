# -*- coding: utf-8 -*-
"""Where does each pre cut segment sit inside the take, matched on picture.

The segments carry no audio track, so the usual audio cross correlation is out.
Instead every frame of the take is reduced to a small grayscale thumbnail, and
each segment is probed at three points against all of them. Three probes that
agree on the same offset is a match; three that disagree means the segment is
from a different recording."""
import os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TW, TH, OFFSET, FPS = 48, 85, 0.09, 30

def thumbs(path, ss=None, n=None):
    a = ["ffmpeg", "-v", "error"]
    if ss is not None: a += ["-ss", "%.3f" % ss]
    if n is not None:  a += ["-frames:v", str(n)]
    a += ["-i", path, "-vf", "scale=%d:%d,format=gray" % (TW, TH),
          "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    # -ss before -i needs the input first; rebuild in the right order
    a = ["ffmpeg", "-v", "error"]
    if ss is not None: a += ["-ss", "%.3f" % ss]
    a += ["-i", path]
    if n is not None:  a += ["-frames:v", str(n)]
    a += ["-vf", "scale=%d:%d,format=gray" % (TW, TH),
          "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    raw = subprocess.run(a, capture_output=True).stdout
    k = TW * TH
    x = np.frombuffer(raw[:len(raw) // k * k], np.uint8).reshape(-1, k).astype(np.float32)
    x -= x.mean(1, keepdims=True)
    n_ = np.linalg.norm(x, axis=1, keepdims=True); n_[n_ == 0] = 1
    return x / n_

take = thumbs(os.path.join(HERE, "raw.mov"))
print("take: %d frames (%.1fs)\n" % (len(take), len(take) / FPS))
print("%-16s %6s   %-15s %s" % ("segment", "len", "in the take", "agreement"))
rows = []
for d in sys.argv[1:]:
    for f in sorted(os.listdir(os.path.join(HERE, d))):
        if not f.endswith(".mp4"): continue
        p = os.path.join(HERE, d, f)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
        probes = [t for t in (0.5, dur / 2, dur - 0.7) if 0 <= t < dur]
        hits = []
        for t in probes:
            q = thumbs(p, t, 1)
            if not len(q): continue
            sim = take @ q[0]
            j = int(np.argmax(sim))
            hits.append((j / FPS - t, float(sim[j])))       # implied segment start
        if not hits:
            print("%-16s %5.1fs   no frames" % (d + "/" + f, dur)); continue
        starts = np.array([h[0] for h in hits]); sims = np.array([h[1] for h in hits])
        spread = float(starts.max() - starts.min())
        a = float(np.median(starts)) - OFFSET
        ok = "MATCH" if spread < 0.5 and sims.min() > 0.80 else \
             ("partial" if sims.max() > 0.80 else "no")
        print("%-16s %5.1fs   %6.2f-%6.2f   %-8s spread %.2fs  sim %.2f/%.2f/%.2f"
              % (d + "/" + f, dur, a, a + dur, ok, spread, *(list(sims) + [0, 0, 0])[:3]))
        if ok == "MATCH": rows.append((a, a + dur, d + "/" + f))

if rows:
    rows.sort()
    print("\ncoverage of the take, transcript clock:")
    for a, b, n in rows: print("   %6.2f - %6.2f   %s" % (a, b, n))
