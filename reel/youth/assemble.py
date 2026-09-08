# -*- coding: utf-8 -*-
"""Punch-in, captions, sound, end card."""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
W, H, FPS = 1080, 1920, 30
PW, PH = 1260, 2240                      # plate size
# The angle crop already tightened the frame, so the punch-in steps come
# down with it; 1.45 here would have meant upscaling past the source.
FRAMING = {"wide": (1.00, 0.50), "mid": (1.15, 0.43), "close": (1.30, 0.36)}

plan  = json.load(open(os.path.join(HERE, "shot-plan.json")))
plate = os.path.join(HERE, "plate_v.mp4")
segd  = os.path.join(HERE, "shots"); os.makedirs(segd, exist_ok=True)

# the plan is derived from caption spans, so the pauses between them fall
# between shots. Close the gaps: each shot runs until the next one starts.
plan[0]["start"] = 0.0
for a, b in zip(plan, plan[1:]):
    a["end"] = b["start"]
plan[-1]["end"] = 71.933

# Work in whole frames, not seconds. Cutting by duration lets every segment
# round up and the concatenation then runs long, which slides the captions.
NFRAMES = 2158
edges = [round(s["start"] * FPS) for s in plan] + [NFRAMES]
for i, s in enumerate(plan):
    s["f0"], s["nf"] = edges[i], edges[i + 1] - edges[i]

for i, s in enumerate(plan):
    z, anch = FRAMING[s["shot"]]
    cw, ch = int(PW / z) // 2 * 2, int(PH / z) // 2 * 2
    x, y = (PW - cw) // 2, int((PH - ch) * anch)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.5f" % (s["f0"] / FPS),
        "-i", plate, "-frames:v", str(s["nf"]),
        "-vf", "crop=%d:%d:%d:%d,scale=%d:%d:flags=lanczos,fps=%d" % (cw, ch, x, y, W, H, FPS),
        "-an", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
        os.path.join(segd, "s%02d.mp4" % i)], check=True)
    print("shot %2d  frames %4d-%4d (%3d)  %-5s  crop %dx%d"
          % (i, s["f0"], s["f0"] + s["nf"], s["nf"], s["shot"], cw, ch), flush=True)

lst = os.path.join(HERE, "shotlist.txt")
with open(lst, "w") as f:
    for i in range(len(plan)):
        f.write("file '%s'\n" % os.path.join(segd, "s%02d.mp4" % i))
subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                "-i", lst, "-c", "copy", os.path.join(HERE, "punched.mp4")], check=True)
print("punched plate built")
