# -*- coding: utf-8 -*-
"""The short cut: the strongest beats only, about 44 seconds with the end card.

Only the headline figure survives of the four. In forty seconds a single
number lands harder than a list, because a list asks the viewer to do
arithmetic they will not do. The rest of the selection keeps the spine:
the accusation, the court, the number, the confrontation, what the children
are carrying, the demand."""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
HEAD_FIX = "crop=1170:2080:135:359"
GRADE = ("eq=contrast=0.95:saturation=0.90:gamma=1.03,"
         "colorbalance=rs=-0.05:bs=0.07:rm=0.00:bm=0.03:rh=0.05:gh=0.02:bh=-0.03,"
         "unsharp=5:5:0.4")
FPS = 30

BEATS = [
    (3.86,  7.20),   # הרמתם יד ואישרתם את עדכון התקציב בלי לדעת.
    (11.22, 14.70),  # אז הנה, עכשיו אתם מבינים שדווקא אתם לא ידעתם.
    (14.72, 18.60),  # וזה לא אני אומרת את זה, בית המשפט אמר את זה.
    (22.84, 27.05),  # קיצצו 653,000 שקלים משישה סעיפי נוער,
    (39.64, 43.06),  # תגידו, השתגעתם? מהנוער שלנו לקחת?
    (46.84, 51.85),  # כשהם מתמודדים... ונשירה גבוהה מאוד בחריש,
    (57.45, 61.30),  # אתם באמת רואים את המספרים האלה עכשיו ופשוט שותקים?
    (68.52, 71.70),  # זה בנפשנו, אל הילדים שלנו.
    (71.72, 74.36),  # אי אפשר להמשיך לשבת על הגדר.
    (74.38, 79.04),  # תתנגדו לזה ותצטרפו אלינו לדרישה לבטל את עדכון התקציב.
    (79.06, 81.28),  # ככה. פשוט.
]

segd = os.path.join(HERE, "sc"); os.makedirs(segd, exist_ok=True)
durs = []
for i, (a, b) in enumerate(BEATS):
    v = os.path.join(segd, "v%02d.mp4" % i)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.3f" % a, "-t", "%.3f" % (b - a),
        "-i", os.path.join(HERE, "youth.mp4"),
        "-vf", "%s,%s,fps=%d" % (HEAD_FIX, GRADE, FPS), "-an",
        "-c:v", "libx264", "-preset", "medium", "-crf", "16", v], check=True)
    d = float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
        "-of", "csv=p=0", v], capture_output=True, text=True).stdout)
    durs.append(d)
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "%.4f" % a, "-t", "%.4f" % d,
        "-i", os.path.join(HERE, "youth.mp4"), "-vn",
        "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2",
        os.path.join(segd, "a%02d.wav" % i)], check=True)
    print("beat %2d  %6.2f-%6.2f  %.3fs" % (i, a, b, d), flush=True)

for tag, ext, out in (("v", "mp4", "plate_s.mp4"), ("a", "wav", "plate_sa.wav")):
    lst = os.path.join(HERE, tag + "s_list.txt")
    with open(lst, "w") as f:
        for i in range(len(BEATS)):
            f.write("file '%s'\n" % os.path.join(segd, "%s%02d.%s" % (tag, i, ext)))
    subprocess.run(["ffmpeg", "-y", "-v", "error", "-f", "concat", "-safe", "0",
                    "-i", lst, "-c", "copy", os.path.join(HERE, out)], check=True)

starts, acc = [], 0.0
for d in durs:
    starts.append(acc); acc += d
json.dump({"beats": BEATS, "durs": durs, "starts": starts, "total": acc},
          open(os.path.join(HERE, "short_map.json"), "w"), indent=1)
print("short cut plate: %.2fs" % acc)
