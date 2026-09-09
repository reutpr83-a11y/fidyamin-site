# -*- coding: utf-8 -*-
"""Chains the beats into one plate, every join a dissolve.

c2=nofade on the audio: every beat is cut so that it ends in silence, so the
outgoing side is the only one that needs a fade. Letting the incoming side
enter at full level keeps a first word from being swallowed when the silence
before it is shorter than the dissolve."""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
m = json.load(open(os.path.join(HERE, "map6.json")))
XF, starts, n = m["xf"], m["starts"], len(m["durs"])

args = ["ffmpeg", "-y", "-v", "error"]
for i in range(n):
    args += ["-i", os.path.join(HERE, "s6", "v%02d.mp4" % i)]
fc, v, a = [], "0:v", "0:a"
for i in range(1, n):
    fc.append("[%s][%d:v]xfade=transition=fade:duration=%.3f:offset=%.5f[v%d]"
              % (v, i, XF, starts[i], i))
    fc.append("[%s][%d:a]acrossfade=d=%.3f:c1=tri:c2=nofade[a%d]" % (a, i, XF, i))
    v, a = "v%d" % i, "a%d" % i
args += ["-filter_complex", ";".join(fc), "-map", "[%s]" % v, "-map", "[%s]" % a,
         "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
         "-x264-params", "keyint=30:min-keyint=30:scenecut=0", "-pix_fmt", "yuv420p",
         "-c:a", "pcm_s16le", os.path.join(HERE, "plate6.mov")]
subprocess.run(args, check=True)
out = subprocess.run(["ffprobe", "-v", "error", "-count_frames", "-select_streams", "v:0",
    "-show_entries", "stream=nb_read_frames,width,height", "-of", "csv=p=0",
    os.path.join(HERE, "plate6.mov")], capture_output=True, text=True).stdout.strip()
print("plate6.mov  %s   predicted %.2fs" % (out, m["total"]))
