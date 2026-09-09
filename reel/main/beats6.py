# -*- coding: utf-8 -*-
"""Beat list for the full strength main reel.

Same take and same measured offset as beats5.py. What changed is how much of
her argument survives: the reel now keeps the analysis ("מי שמבין אפילו קצת
בניהול מערכות ... קריסה"), the bins and the road, the petition and the
hearing, the four council members by name, and the leadership close. The only
things dropped are the passages that say a thing the reel has already said.

"לאסון" is out at the client's request, and with it the sentence it completes
("ואתם אמורים לראות בדיוק כמונו לאן המהלך הזה מוביל,"), which dangles without
its ending. The reel goes from "הסתירו מכם מידע שאנחנו מגלים לכם אותו" to
"פחות פיקוח, פחות ניקיון ופחות שירות לתושבים" instead, and both cut points
fall inside real silences (119.92-120.31 and 124.54-125.13).

One join needs care. She false starts at 57.11 ("מציאות הזויה שבה התושבים,")
and restarts at 60.21 after saying "סליחה". There is exactly 100ms of silence
between the apology and the restart, which is less than the crossfade, so the
audio crossfade uses c2=nofade: the outgoing beat ends in silence and fades
out, the incoming beat enters at full level and is not attenuated on
"מציאות"."""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "raw.mov")
OFFSET = 0.09
XF = 0.35

GRADE = ("hqdn3d=3:2:6:6,scale=1152:2048:flags=lanczos+accurate_rnd,"
         "unsharp=7:7:0.9:5:5:0.0,"
         "eq=contrast=1.06:saturation=1.05:gamma=0.99,"
         "colorbalance=rs=-0.04:bs=0.06:rm=0.00:bm=0.02:rh=0.04:gh=0.01:bh=-0.03")

BEATS = [
    ("הטענה",         10.70,  19.99),   # מקצצת מיליונים ושופכת על קבלנים
    ("אז פוליטי",      3.95,   9.18),   # ביקורת על מיליונים היא פוליטית?
    ("הראיות",        29.28,  56.90),   # דוגמאות, הנדסה, תברואה, ניהול מערכות, קריסה
    ("המציאות",       60.11,  96.74),   # הפחים, הכביש, האחריות, מי משלם
    ("הפנייה",        98.30, 120.27),   # בית המשפט, משה נגה איציק רויטל, הסתירו מכם
    ("פחות",         124.80, 128.50),   # פחות פיקוח, פחות ניקיון ופחות שירות
    ("מנהיגות",      133.20, 156.73),   # לא ידעתם, זו מנהיגות, תתנגדו, מוסרית וגם פוליטית
]

if __name__ == "__main__":
    segd = os.path.join(HERE, "s6"); os.makedirs(segd, exist_ok=True)
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
              open(os.path.join(HERE, "map6.json"), "w"), indent=1)
    print("\n%d beats, %.2fs dissolves, the cut runs %.2fs" % (len(BEATS), XF, total))
