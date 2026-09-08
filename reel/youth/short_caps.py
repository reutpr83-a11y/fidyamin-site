# -*- coding: utf-8 -*-
"""Captions for the short cut. A word is only kept if the whole of it lies
inside a beat; taking words that merely start inside one let the first
syllable of the next figure leak in after the cut."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
m  = json.load(open(os.path.join(HERE, "short_map.json")))
tr = json.load(open(os.path.join(HERE, "youth-transcript.json"), encoding="utf-8"))
beats, durs, starts, LAST = m["beats"], m["durs"], m["starts"], round(m["total"], 3)

def to_out(a, b):
    for i, (x, _) in enumerate(beats):
        if x - 1e-6 <= a and b <= x + durs[i] + 1e-6:
            return starts[i] + (a - x)
    return None

FIX = {"והשארתם": "ואישרתם"}
raw = []
for seg in tr:
    for w in seg["words"]:
        o = to_out(w["s"], w["e"])
        if o is not None:
            raw.append((FIX.get(w["w"].strip(), w["w"].strip()), round(o, 3)))
ws = []
for w, t in raw:
    if ws and w.startswith(",") and ws[-1][0][-1:].isdigit():
        ws[-1] = (ws[-1][0] + w, ws[-1][1])
    else:
        ws.append((w, t))
out = []
for i, (w, t) in enumerate(ws):
    if w == "השתגעתם": w = "השתגעתם?"
    if w == "שהיה" and i + 1 < len(ws) and ws[i+1][0] == "לנו":
        out.append(("שלנו", t)); continue
    if w == "לנו" and out and out[-1][0] == "שלנו": continue
    out.append((w, t))
ws = out

MAXW, MAXCH, PAUSE = 8, 46, 0.80
groups, cur = [], []
for i, (w, t) in enumerate(ws):
    cur.append((w, t))
    gap = ws[i+1][1] - t if i + 1 < len(ws) else 9.9
    if (w.endswith((".", "?", "!")) or gap >= PAUSE or len(cur) >= MAXW
            or sum(len(x)+1 for x, _ in cur) >= MAXCH or i == len(ws) - 1):
        groups.append(cur); cur = []
if cur: groups.append(cur)

tk = []
for g in groups:
    a = [w for w, _ in g]; t = [x for _, x in g]; n = len(a); h = (n + 1) // 2
    tk.append({"start": round(t[0]-0.06, 3), "end": 0.0,
               "style": "emphasis" if "653,000" in " ".join(a) else "regular",
               "words": a, "times": t, "lines": [n] if n <= 3 else [h, n - h]})
for i, c in enumerate(tk):
    nxt = tk[i+1]["start"] if i + 1 < len(tk) else LAST
    c["end"] = round(min(nxt - 0.02, c["times"][-1] + 1.15), 3)
    if c["end"] < c["times"][-1] + 0.18:
        c["end"] = round(c["times"][-1] + 0.18, 3)
        if i + 1 < len(tk): tk[i+1]["start"] = round(c["end"] + 0.02, 3)
tk[0]["start"] = max(0.0, tk[0]["start"]); tk[-1]["end"] = LAST
json.dump(tk, open(os.path.join(HERE, "caption-track.json"), "w"), ensure_ascii=False, indent=1)
print("short cut: %.2fs  captions: %d  words: %d  truncated: %d  overlaps: %d"
      % (LAST, len(tk), sum(len(c["words"]) for c in tk),
         sum(1 for c in tk if c["end"] < c["times"][-1] + 0.17),
         sum(1 for i in range(len(tk)-1) if tk[i]["end"] > tk[i+1]["start"] + 1e-6)))
for i, c in enumerate(tk, 1):
    print("%2d. [%5.2f-%5.2f] %-9s %s" % (i, c["start"], c["end"], c["style"], " ".join(c["words"])))
