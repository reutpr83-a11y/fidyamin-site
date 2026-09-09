# -*- coding: utf-8 -*-
"""Body + held tail, then a dissolve into the card.

Nothing in the reel is a hard cut: the beats dissolve, the tail is frame
continuous with the last beat, and the card fades up on silence. The numbers
come out of map6.json and the finished parts rather than being typed, so a
change to the beat list cannot leave a stale offset behind."""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))

def dur(p):
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
        "format=duration", "-of", "csv=p=0", os.path.join(HERE, p)],
        capture_output=True, text=True).stdout)

body, tail, card = dur("body6.mp4"), dur("tail6.mp4"), dur("endcard6.mp4")
XF, FADE = 0.50, 0.70
picture = body + tail
total = picture + card - XF
print("body %.4f + tail %.4f = %.4f   card %.4f   total %.4f"
      % (body, tail, picture, card, total))

subprocess.run(["ffmpeg", "-y", "-v", "error",
    "-i", os.path.join(HERE, "body6.mp4"), "-i", os.path.join(HERE, "tail6.mp4"),
    "-i", os.path.join(HERE, "endcard6.mp4"), "-i", os.path.join(HERE, "audio6.wav"),
    "-filter_complex",
    "[0:v]fps=30,settb=1/15360[b0];[1:v]fps=30,settb=1/15360[b1];"
    "[2:v]fps=30,settb=1/15360[b2];"
    "[b0][b1]concat=n=2:v=1:a=0,settb=1/15360[bd];"
    "[bd][b2]xfade=transition=fade:duration=%.3f:offset=%.4f[v];"
    "[3:a]afade=t=out:st=%.4f:d=%.2f,apad,atrim=0:%.4f,asetpts=N/SR/TB[a]"
    % (XF, picture - XF, picture - FADE - 0.15, FADE, total),
    "-map", "[v]", "-map", "[a]",
    "-c:v", "libx264", "-preset", "slow", "-crf", "18", "-pix_fmt", "yuv420p",
    "-color_primaries", "bt709", "-color_trc", "bt709", "-colorspace", "bt709",
    "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-ac", "2", "-movflags", "+faststart",
    os.path.join(HERE, "harish-main-reel-v2.mp4")], check=True)
print("master %.4fs" % dur("harish-main-reel-v2.mp4"))
