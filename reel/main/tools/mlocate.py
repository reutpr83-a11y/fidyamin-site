# -*- coding: utf-8 -*-
"""Where does each pre cut segment sit inside the take, matched on motion.

Appearance matching fails on a locked off talking head: every frame looks like
every other frame, so the peak lands anywhere. Motion does not. Each frame is
reduced to a thumbnail, the absolute difference from the previous frame is
summed into a single number, and that 1D curve of how much the picture is
moving is cross correlated against the take's, exactly the way the audio
envelope was used to identify the transcript."""
import os, subprocess, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
TW, TH, OFFSET, FPS = 64, 114, 0.09, 30

def motion(path):
    a = ["ffmpeg", "-v", "error", "-i", path,
         "-vf", "scale=%d:%d,format=gray" % (TW, TH), "-r", str(FPS),
         "-f", "rawvideo", "-pix_fmt", "gray", "-"]
    raw = subprocess.run(a, capture_output=True).stdout
    k = TW * TH
    x = np.frombuffer(raw[:len(raw)//k*k], np.uint8).reshape(-1, k).astype(np.float32)
    if len(x) < 3: return np.zeros(0, np.float32)
    m = np.abs(np.diff(x, axis=0)).mean(1)
    return m - m.mean()

take = motion(os.path.join(HERE, "raw.mov"))
tn = np.linalg.norm(take)
print("take: %d frames (%.1fs)\n" % (len(take) + 1, (len(take) + 1) / FPS))
print("%-16s %6s   %-15s %s" % ("segment", "len", "in the take", "peak"))
rows = []
for d in sys.argv[1:]:
    for f in sorted(os.listdir(os.path.join(HERE, d))):
        if not f.endswith(".mp4"): continue
        p = os.path.join(HERE, d, f)
        q = motion(p)
        if len(q) < 30:
            print("%-16s   too short" % (d + "/" + f)); continue
        c = np.correlate(take, q, "valid")
        j = int(np.argmax(c))
        peak = c[j] / (np.linalg.norm(q) * np.linalg.norm(take[j:j+len(q)]) + 1e-9)
        a = j / FPS - OFFSET
        dur = len(q) / FPS
        ok = "MATCH" if peak > 0.55 else ("weak" if peak > 0.35 else "no")
        print("%-16s %5.1fs   %6.2f-%6.2f   %.3f  %s" % (d + "/" + f, dur, a, a + dur, peak, ok))
        if peak > 0.55: rows.append((a, a + dur, d + "/" + f, peak))
if rows:
    rows.sort()
    print("\ncoverage of the take, transcript clock:")
    for a, b, n, pk in rows: print("   %6.2f - %6.2f   %s  (%.2f)" % (a, b, n, pk))
    tot = 0.0; last = -1
    for a, b, _, _ in rows:
        s = max(a, last); 
        if b > s: tot += b - s; last = b
    print("\n   total distinct coverage: %.1fs of %.1fs" % (tot, (len(take)+1)/FPS))
