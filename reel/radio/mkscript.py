# -*- coding: utf-8 -*-
# Writes script.txt straight from the caption track, so the text on file can
# never drift from the text on screen.
import json
NAMES = {1: "יוסי הדר · מגיש", 2: "שני גרינברג", 3: "איתמר רותם · כתב"}
caps = json.load(open("track.json"))
out, last = [], None
for c in caps:
    if c["speaker"] != last:
        t = max(0.0, c["start"])
        out.append("\n%d:%02d  %s" % (t // 60, t % 60, NAMES[c["speaker"]]))
        last = c["speaker"]
    out.append("    " + " ".join(c["words"]))
end = caps[-1]["end"]
out.append("\n%d:%02d  קלף סיום" % (end // 60, end % 60))
for line in ("תפסיקו לשתוק", "צאו נגד זה", "מתוך הראיון ביומן החדשות"):
    out.append("    " + line)
open("script.txt", "w").write("\n".join(out).lstrip() + "\n")
print("\n".join(out).lstrip())
