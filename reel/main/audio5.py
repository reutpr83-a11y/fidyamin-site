# -*- coding: utf-8 -*-
"""Rebuilds the reel's audio so it matches the picture frame for frame.

Each beat's video was cut to whole frames and so ran a few milliseconds
longer than the audio that came with it; chained through eleven beats that
put the sound 0.30s ahead of her mouth by the end. Here every beat's audio is
cut to exactly the length of its own video before the crossfades are made."""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
m = json.load(open(os.path.join(HERE, "map5.json")))
# the held beat after her last word is cut separately (tail4.py) but its sound
# belongs to the last segment, so the last beat's audio runs that much longer
TAIL = 26 / 30.0
m["durs"][-1] += TAIL
m["total"] += TAIL
XF = m["xf"]; segd = os.path.join(HERE, "s5")

OFF = m["offset"]
for i, ((a, b), d) in enumerate(zip(m["beats"], m["durs"])):
    w = os.path.join(segd, "a%02d.wav" % i)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.5f" % (a + OFF), "-t", "%.5f" % d,
        "-i", os.path.join(HERE, "raw.mov"), "-vn",
        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", w], check=True)
    got = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "csv=p=0", w], capture_output=True, text=True).stdout)
    print("beat %2d  video %.4f  audio %.4f  delta %+.4f" % (i, d, got, got - d))

n = len(m["durs"])
args = ["ffmpeg", "-y", "-v", "error"]
for i in range(n):
    args += ["-i", os.path.join(segd, "a%02d.wav" % i)]
fc, cur = [], "0:a"
for i in range(1, n):
    out = "x%d" % i
    fc.append("[%s][%d:a]acrossfade=d=%.3f:c1=tri:c2=tri[%s]" % (cur, i, XF, out))
    cur = out
fc.append("[%s]loudnorm=I=-14:TP=-1.5:LRA=11[out]" % cur)
args += ["-filter_complex", ";".join(fc), "-map", "[out]",
         "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2",
         os.path.join(HERE, "audio5.wav")]
subprocess.run(args, check=True)
d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
    "-of", "csv=p=0", os.path.join(HERE, "audio5.wav")],
    capture_output=True, text=True).stdout)
print("\naudio5.wav %.4fs   picture %.4fs   delta %+.4f" % (d, m["total"], d - m["total"]))
