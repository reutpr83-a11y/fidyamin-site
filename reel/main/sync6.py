# -*- coding: utf-8 -*-
"""Checks the finished reel's sound against the take, beat by beat.

The picture is cut from the take frame for frame, so if the master's audio
sits at zero lag against the same source moment for every beat, the mouth and
the voice agree. Each beat is measured on its own middle second, away from the
crossfades at its edges."""
import json, os, subprocess
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 16000
m = json.load(open(os.path.join(HERE, "map6.json")))
OFF = m["offset"]   # the beat clock is the transcript's, the file runs later

def pcm(path, ss, dur):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", "%.4f" % ss, "-t", "%.4f" % dur,
        "-i", path, "-vn", "-f", "s16le", "-acodec", "pcm_s16le",
        "-ar", str(SR), "-ac", "1", "-"], capture_output=True).stdout
    return np.frombuffer(raw, "<i2").astype(np.float32) / 32768.0

MAXLAG = int(0.30 * SR)
worst = 0.0
for i, ((a, b), st) in enumerate(zip(m["beats"], m["starts"])):
    win = min(1.5, (b - a) - 1.0)
    if win < 0.5: win = 0.5
    ref = pcm(os.path.join(HERE, "raw.mov"), a + OFF + 0.5, win)
    seg = pcm(os.path.join(HERE, "harish-main-reel-v2.mp4"), st + 0.5 - 0.30, win + 0.60)
    if len(ref) < 100 or len(seg) < len(ref): print("beat %2d: short" % i); continue
    ref = ref - ref.mean(); seg = seg - seg.mean()
    c = np.correlate(seg, ref, "valid")
    lag = (int(np.argmax(c)) - MAXLAG) / SR
    peak = c.max() / (np.linalg.norm(ref) * np.linalg.norm(seg[:len(ref)]) + 1e-9)
    worst = max(worst, abs(lag))
    print("beat %2d  source %6.2f  reel %6.2f   lag %+.3fs" % (i, a, st, lag))
print("\nworst beat lag %.3fs  (one frame is %.3fs)" % (worst, 1 / 30))
