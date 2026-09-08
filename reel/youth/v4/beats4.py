# -*- coding: utf-8 -*-
"""Beat list for the cold-open cut, and the segments cut from the take.

Opens on the outrage rather than the charge: the viewer is a parent in
Harish, not one of the four council members, and "מהנוער שלנו לקחת?" is the
only line in the take that speaks to them directly in the first second.
Every join is a dissolve, not a cut - the beats come from moments minutes
apart and a hard cut between them reads as a jump."""
import json, os, subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
CROP  = "crop=1152:2048:144:472"
GRADE = ("eq=contrast=0.95:saturation=0.90:gamma=1.03,"
         "colorbalance=rs=-0.05:bs=0.07:rm=0.00:bm=0.03:rh=0.05:gh=0.02:bh=-0.03,"
         "unsharp=5:5:0.4")
XF = 0.35                      # dissolve length between beats

BEATS = [
    ("הוק",            39.64, 43.20),
    ("האשמה",           3.80,  7.24),
    ("המילים שלכם",     7.24, 11.20),
    ("ההיפוך",         11.22, 14.70),
    ("סמכות",          14.72, 18.62),
    ("ראיה",           22.80, 27.00),
    ("ראיה",           27.00, 31.14),
    ("שותפות בשתיקה",  57.40, 61.34),
    ("אין אמצע",       71.68, 74.40),
    ("דרישה",          74.38, 79.08),
    ("חותם",           79.04, 81.30),
]

segd = os.path.join(HERE, "s4"); os.makedirs(segd, exist_ok=True)
durs = []
for i, (role, a, b) in enumerate(BEATS):
    v = os.path.join(segd, "v%02d.mp4" % i)
    subprocess.run(["ffmpeg","-y","-v","error","-ss","%.3f"%a,"-t","%.3f"%(b-a),
        "-i", os.path.join(HERE,"youth.mp4"),
        "-vf","%s,%s,fps=30,setsar=1"%(CROP,GRADE),
        "-c:v","libx264","-preset","medium","-crf","16",
        "-c:a","pcm_s16le","-ar","48000","-ac","2", v], check=True)
    d=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0",v],capture_output=True,text=True).stdout)
    durs.append(d)
    print("%-16s %6.2f-%6.2f  %.3fs"%(role,a,b,d), flush=True)

# where each beat lands once the dissolves overlap them
starts, acc = [], 0.0
for d in durs:
    starts.append(acc); acc += d - XF
total = acc + XF
json.dump({"beats":[[a,b] for _,a,b in BEATS],"roles":[r for r,_,_ in BEATS],
           "durs":durs,"starts":starts,"total":total,"xf":XF},
          open(os.path.join(HERE,"map4.json"),"w"), indent=1)
print("\nsegments %d   with %.2fs dissolves the cut runs %.2fs"%(len(BEATS),XF,total))
