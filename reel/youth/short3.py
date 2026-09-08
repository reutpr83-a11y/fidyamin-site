# -*- coding: utf-8 -*-
"""Second short cut.

Three changes on the client's notes:
  * the setup she asked to keep is back. Dropping "באותה ישיבה אמרתם שאנחנו
    לא יודעים" left "אז הנה, עכשיו אתם מבינים שדווקא אתם לא ידעתם" with
    nothing to answer, which is the line the whole opening turns on.
  * the passage about anxiety, loneliness and dropout is out. She asked for
    the beats where she sounds determined rather than aggrieved, and that
    passage is the one that pleads.
  * no whooshes. They were her request originally and she has now heard them
    in place; BRAND.md forbids them anyway.
Framing is tighter again, eyes at 28 percent of frame height.
"""
import json, os, subprocess
HERE = os.path.dirname(os.path.abspath(__file__))
CROP  = "crop=1152:2048:144:472"
GRADE = ("eq=contrast=0.95:saturation=0.90:gamma=1.03,"
         "colorbalance=rs=-0.05:bs=0.07:rm=0.00:bm=0.03:rh=0.05:gh=0.02:bh=-0.03,"
         "unsharp=5:5:0.4")
BEATS = json.load(open(os.path.join(HERE, "beats3.json")))
segd = os.path.join(HERE, "s3"); os.makedirs(segd, exist_ok=True)
durs = []
for i, (a, b) in enumerate(BEATS):
    v = os.path.join(segd, "v%02d.mp4" % i)
    subprocess.run(["ffmpeg","-y","-v","error","-ss","%.3f"%a,"-t","%.3f"%(b-a),
        "-i",os.path.join(HERE,"youth.mp4"),
        "-vf","%s,%s,fps=30"%(CROP,GRADE),"-an",
        "-c:v","libx264","-preset","medium","-crf","16",v],check=True)
    d=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration",
        "-of","csv=p=0",v],capture_output=True,text=True).stdout); durs.append(d)
    subprocess.run(["ffmpeg","-y","-v","error","-ss","%.4f"%a,"-t","%.4f"%d,
        "-i",os.path.join(HERE,"youth.mp4"),"-vn","-c:a","pcm_s16le","-ar","48000","-ac","2",
        os.path.join(segd,"a%02d.wav"%i)],check=True)
for tag,ext,out in (("v","mp4","plate3.mp4"),("a","wav","plate3a.wav")):
    lst=os.path.join(HERE,tag+"3_list.txt")
    with open(lst,"w") as f:
        for i in range(len(BEATS)): f.write("file '%s'\n"%os.path.join(segd,"%s%02d.%s"%(tag,i,ext)))
    subprocess.run(["ffmpeg","-y","-v","error","-f","concat","-safe","0","-i",lst,"-c","copy",
                    os.path.join(HERE,out)],check=True)
starts,acc=[],0.0
for d in durs: starts.append(acc); acc+=d
json.dump({"beats":BEATS,"durs":durs,"starts":starts,"total":acc},
          open(os.path.join(HERE,"short_map.json"),"w"),indent=1)
print("plate: %.2fs"%acc)
