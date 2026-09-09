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
# Two takes. The reel is cut from the 15:59:53 one, but its reading of the
# opening sentence smiles the whole way through and that sentence is said only
# once in it. The other take says the same sentence, in the same place, in the
# same shirt, and says it straight. Same camera position too, so the join
# dissolves as movement rather than as a second shoot.
GB = os.path.join(os.path.dirname(HERE), "gb")
TAKES = {
    "main": (os.path.join(HERE, "full.MOV"), 0.09, "transcript_155953.json"),
    "open": (os.path.join(GB, "src.mp4"),    0.10, "transcript.json"),
}
OFFSET = 0.09
XF = 0.35

GRADE = ("scale=1152:2048:flags=lanczos+accurate_rnd,"
         "eq=contrast=1.03:saturation=1.02:gamma=0.99,"
         "colorbalance=rs=-0.04:bs=0.06:rm=0.00:bm=0.02:rh=0.04:gh=0.01:bh=-0.03")

# (role, in, out, take)
#
# "אז פוליטי אמרתם" used to sit second. It carries no evidence, and with the
# thesis before it that put the first figure 17.5s in, which is late for a
# reel. It now lands just before "ואתם לא תוכלו להגיד שלא ידעתם", where the
# retort answers numbers the viewer has already seen and the closing line
# answers it seconds later instead of two minutes later.
#
# "רק כמה דוגמאות קטנות" is gone: 2.7s for four words, the slowest line in the
# reel that is not a punch line, and it delivers nothing.
BEATS = [
    ("הטענה",         2.00,  12.10, "open"),   # מקצצת מיליונים ושופכת על קבלנים
    ("הראיות",        31.55,  56.90, "main"),   # הנדסה, תברואה, ניהול מערכות, קריסה
    ("המציאות",       60.11,  96.74, "main"),   # הפחים, הכביש, האחריות, מי משלם
    ("הפנייה",        98.30, 120.27, "main"),   # בית המשפט, משה נגה איציק רויטל
    ("פחות",         124.80, 128.50, "main"),   # פחות פיקוח, פחות ניקיון
    ("אז פוליטי",      3.95,   9.18, "main"),   # ביקורת על מיליונים היא פוליטית?
    ("מנהיגות",      133.20, 156.73, "main"),   # לא ידעתם, זו מנהיגות, תתנגדו
]

if __name__ == "__main__":
    segd = os.path.join(HERE, "s6"); os.makedirs(segd, exist_ok=True)
    durs = []
    for i, (role, a, b, take) in enumerate(BEATS):
        src, off, _ = TAKES[take]
        v = os.path.join(segd, "v%02d.mp4" % i)
        subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % (a + off),
            "-t", "%.3f" % (b - a), "-i", src,
            "-vf", "%s,fps=30,setsar=1" % GRADE,
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "14",
            "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2", v], check=True)
        d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries",
            "format=duration", "-of", "csv=p=0", v], capture_output=True, text=True).stdout)
        durs.append(d)
        print("%-10s %-5s %6.2f-%6.2f  %.3fs" % (role, take, a, b, d), flush=True)

    starts, acc = [], 0.0
    for d in durs:
        starts.append(acc); acc += d - XF
    total = acc + XF
    json.dump({"beats": [[a, b] for _, a, b, _ in BEATS],
               "roles": [r for r, _, _, _ in BEATS],
               "takes": [t for _, _, _, t in BEATS],
               "sources": {k: {"path": v[0], "offset": v[1], "transcript": v[2]}
                           for k, v in TAKES.items()},
               "durs": durs, "starts": starts, "total": total, "xf": XF},
              open(os.path.join(HERE, "map6.json"), "w"), indent=1)
    print("\n%d beats, %.2fs dissolves, the cut runs %.2fs" % (len(BEATS), XF, total))
