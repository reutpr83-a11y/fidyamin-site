# -*- coding: utf-8 -*-
"""Beat list for the main reel, and the segments cut from the take.

The take is the 15:59:53 recording (159s). Its transcript is
video/work/transcript_155953.json, whose clock runs OFFSET earlier than this
file; the value was measured by correlating the transcript's word mask against
the recording's speech envelope (peak 0.555 at +0.09s, against 0.379 for the
only other candidate take).

The order is argued, not chronological: the charge first, then the dismissal
it will meet, then the two budget lines that prove it, then what that buys you
on your own street, then the principle, then the ask. It closes on
"מוסרית וגם פוליטית", which answers the "אז פוליטי אמרתם?" the reel put second.

Beats are contiguous stretches of the take, so every cut inside a beat is no
cut at all; only the jumps between beats need a dissolve."""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "raw.mov")
OFFSET = 0.09                  # transcript clock -> this file's clock
XF = 0.35                      # dissolve between beats

# the source is 576x1024; 1152x2048 is a clean 2x, and is also 1.0667x the
# 1080x1920 output, so the push in ends at 1:1 instead of upscaling further
GRADE = ("hqdn3d=3:2:6:6,scale=1152:2048:flags=lanczos+accurate_rnd,"
         "unsharp=7:7:0.9:5:5:0.0,"
         "eq=contrast=1.06:saturation=1.05:gamma=0.99,"
         "colorbalance=rs=-0.04:bs=0.06:rm=0.00:bm=0.02:rh=0.04:gh=0.01:bh=-0.03")

# (role, in, out) on the transcript clock
BEATS = [
    ("הטענה",        10.70,  19.99),   # segs 3-4  מקצצת מיליונים ושופכת על קבלנים
    ("אז פוליטי",     3.95,   9.18),   # segs 0-2  ביקורת על מיליונים היא פוליטית?
    ("הראיות",       32.15,  48.42),   # segs 8-10 הנדסה ותברואה, מול הפאנלים
    ("הכביש",        68.10,  78.66),   # segs 15-17 הקבלן, החלטורה, הבורות
    ("העיקרון",      84.15,  96.74),   # segs 19-23 האחריות נשארת בפנים, מי משלם
    ("לא ידענו",    133.20, 138.26),   # segs 35-36 לא תוכלו להגיד, לא לשבת על הגדר
    ("הדרישה",      145.90, 156.73),   # segs 40-44 תתנגדו, מוסרית וגם פוליטית
]

if __name__ == "__main__":
    segd = os.path.join(HERE, "s5"); os.makedirs(segd, exist_ok=True)
    durs = []
    for i, (role, a, b) in enumerate(BEATS):
        v = os.path.join(segd, "v%02d.mp4" % i)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % (a + OFFSET),
            "-t", "%.3f" % (b - a), "-i", SRC,
            "-vf", "%s,fps=30,setsar=1" % GRADE,
            "-c:v", "libx264", "-preset", "medium", "-crf", "16",
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", v], check=True)
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "csv=p=0", v], capture_output=True, text=True).stdout)
        durs.append(d)
        print("%-10s %6.2f-%6.2f  %.3fs" % (role, a, b, d), flush=True)

    starts, acc = [], 0.0
    for d in durs:
        starts.append(acc); acc += d - XF
    total = acc + XF
    json.dump({"beats": [[a, b] for _, a, b in BEATS], "roles": [r for r, _, _ in BEATS],
               "durs": durs, "starts": starts, "total": total, "xf": XF, "offset": OFFSET},
              open(os.path.join(HERE, "map5.json"), "w"), indent=1)
    print("\n%d beats, %.2fs dissolves, the cut runs %.2fs" % (len(BEATS), XF, total))
