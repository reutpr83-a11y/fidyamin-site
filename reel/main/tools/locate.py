# -*- coding: utf-8 -*-
"""Where does each pre cut segment sit inside the take we are editing?

The segments were exported from an earlier edit, so their own clock means
nothing. Each one's audio is cross correlated against raw.mov to find the
offset that matches, and the normalised peak says whether it is the same
recording at all. Everything is reported on the transcript clock, which is
what beats6.py is written in."""
import os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR, OFFSET = 8000, 0.09

def pcm(path, ss=None, d=None):
    a = ["ffmpeg", "-v", "error"]
    if ss is not None: a += ["-ss", "%.3f" % ss]
    if d is not None:  a += ["-t", "%.3f" % d]
    a += ["-i", path, "-vn", "-f", "s16le", "-ar", str(SR), "-ac", "1", "-"]
    x = np.frombuffer(subprocess.run(a, capture_output=True).stdout, "<i2").astype(np.float32) / 32768
    return x - x.mean() if len(x) else x

big = pcm(os.path.join(HERE, "raw.mov"))
print("take: %.1fs\n" % (len(big) / SR))
print("%-16s %6s %10s   %-15s %s" % ("segment", "len", "res", "in the take", "match"))
for d in sys.argv[1:]:
    for f in sorted(os.listdir(os.path.join(HERE, d))):
        if not f.endswith(".mp4"): continue
        p = os.path.join(HERE, d, f)
        info = subprocess.run(["ffprobe", "-v", "error", "-show_entries",
            "stream=width,height", "-show_entries", "format=duration",
            "-of", "csv=p=0", p], capture_output=True, text=True).stdout.split()
        res = info[0] if info else "?"
        ref = pcm(p, 0.4, 3.0)
        if len(ref) < SR:
            print("%-16s %6s %10s   too short" % (d + "/" + f, "-", res)); continue
        c = np.correlate(big, ref, "valid")
        i = int(np.argmax(c))
        peak = c[i] / (np.linalg.norm(ref) * np.linalg.norm(big[i:i+len(ref)]) + 1e-9)
        dur = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "csv=p=0", p], capture_output=True, text=True).stdout)
        a = i / SR - 0.4 - OFFSET          # transcript clock
        ok = "yes" if peak > 0.45 else ("weak" if peak > 0.25 else "NO")
        print("%-16s %5.1fs %10s   %6.2f-%6.2f   %.3f %s"
              % (d + "/" + f, dur, res, a, a + dur, peak, ok))
