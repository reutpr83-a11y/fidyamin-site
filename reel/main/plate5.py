# -*- coding: utf-8 -*-
"""Chains the beats into one plate, every join a dissolve."""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
m = json.load(open(os.path.join(HERE, "map5.json")))
XF, starts, n = m["xf"], m["starts"], len(m["durs"])

args = ["ffmpeg", "-y", "-v", "error"]
for i in range(n):
    args += ["-i", os.path.join(HERE, "s5", "v%02d.mp4" % i)]
fc, v, a = [], "0:v", "0:a"
for i in range(1, n):
    fc.append("[%s][%d:v]xfade=transition=fade:duration=%.3f:offset=%.5f[v%d]"
              % (v, i, XF, starts[i], i))
    fc.append("[%s][%d:a]acrossfade=d=%.3f:c1=tri:c2=tri[a%d]" % (a, i, XF, i))
    v, a = "v%d" % i, "a%d" % i
args += ["-filter_complex", ";".join(fc), "-map", "[%s]" % v, "-map", "[%s]" % a,
         "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
         "-c:a", "pcm_s16le", os.path.join(HERE, "plate5.mov")]
subprocess.run(args, check=True)
out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
    "-show_entries", "stream=nb_read_frames,width,height", "-of", "csv=p=0",
    os.path.join(HERE, "plate5.mov")], capture_output=True, text=True).stdout.strip()
print("plate5.mov  %s   predicted %.2fs" % (out, m["total"]))
