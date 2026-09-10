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
# This is the edit the client approved. Nothing is reordered, trimmed or added:
# the in points are hers exactly, and the only change is that the frames now
# come from the camera original instead of a WhatsApp export.
#
# The out points are extended, and that is a fix rather than an edit. A 0.35s
# dissolve takes the last 0.35s of the outgoing beat, and five of these beats
# ended 0.10s after their last word, so the picture began changing 0.25s before
# the sentence had finished and the transition read as trampling the line. Each
# out point now sits far enough past the last word for the whole dissolve to
# fall in silence. Everything added is silence.
#
# הפנייה is the one that cannot be fixed: only 0.06s separates its last word
# from the sentence that was cut after it, so there is no silence to move into.
# Its overlap is 0.02s, under one frame, and it stays as approved.
BEATS = [
    ("הטענה",         10.70,  20.36, "main"),   # מקצצת מיליונים ושופכת על קבלנים
    ("אז פוליטי",      3.95,   9.55, "main"),   # ביקורת על מיליונים היא פוליטית?
    ("הראיות",        29.28,  56.90, "main"),   # דוגמאות, הנדסה, תברואה, קריסה
    ("המציאות",       60.11,  97.11, "main"),   # הפחים, הכביש, האחריות, מי משלם
    ("הפנייה",        98.30, 120.27, "main"),   # בית המשפט, משה נגה איציק רויטל
    ("פחות",         124.80, 128.86, "main"),   # פחות פיקוח, פחות ניקיון
    ("מנהיגות",      133.20, 157.10, "main"),   # לא ידעתם, זו מנהיגות, תתנגדו
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
