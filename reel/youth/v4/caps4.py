# -*- coding: utf-8 -*-
"""Captions for the cold-open cut. Beats overlap by the dissolve length, so a
word's place on the timeline comes from its beat's start, not from a running
sum of durations."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
m  = json.load(open(os.path.join(HERE, "map4.json")))
tr = json.load(open(os.path.join(HERE, "youth-transcript.json"), encoding="utf-8"))
beats, durs, starts, XF = m["beats"], m["durs"], m["starts"], m["xf"]
LAST = round(m["total"], 3)

def place(a, b):
    for i, (x, _) in enumerate(beats):
        if x - 1e-6 <= a and b <= x + durs[i] + 1e-6:
            return starts[i] + (a - x), i
    return None, None

FIX = {"והשארתם": "ואישרתם"}
raw = []
for seg in tr:
    for w in seg["words"]:
        o, bi = place(w["s"], w["e"])
        if o is not None:
            raw.append((FIX.get(w["w"].strip(), w["w"].strip()), round(o, 3), bi))
raw.sort(key=lambda x: x[1])

ws = []
for w, t, bi in raw:
    if ws and w.startswith(",") and ws[-1][0][-1:].isdigit():
        ws[-1] = (ws[-1][0] + w, ws[-1][1], ws[-1][2])
    else:
        ws.append((w, t, bi))
out = []
for i, (w, t, bi) in enumerate(ws):
    if w == "השתגעתם": w = "השתגעתם?"
    if w == "שהיה" and i + 1 < len(ws) and ws[i+1][0] == "לנו":
        out.append(("שלנו", t, bi)); continue
    if w == "לנו" and out and out[-1][0] == "שלנו": continue
    out.append((w, t, bi))
ws = out

MAXW, MAXCH, PAUSE = 8, 46, 0.80
groups, cur = [], []
for i, (w, t, bi) in enumerate(ws):
    cur.append((w, t, bi))
    gap = ws[i+1][1] - t if i + 1 < len(ws) else 9.9
    beat_ends = i + 1 >= len(ws) or ws[i+1][2] != bi
    if (beat_ends or w.endswith((".", "?", "!")) or gap >= PAUSE
            or len(cur) >= MAXW or sum(len(x)+1 for x, _, _ in cur) >= MAXCH):
        groups.append(cur); cur = []
if cur: groups.append(cur)

# A trailing scrap - the last word or two of a sentence pushed into its own
# caption by the word limit - can end up with almost no time once the
# dissolves overlap the beats. Fold it back into the caption it belongs to.
merged = []
for g in groups:
    prev = merged[-1] if merged else None
    same_beat = prev is not None and prev[-1][2] == g[0][2]
    fits = prev is not None and sum(len(x)+1 for x, _, _ in prev + g) <= MAXCH + 8
    if prev and len(g) <= 2 and same_beat and fits \
       and (g[0][1] - prev[-1][1]) < 0.85 and len(prev) + len(g) <= MAXW + 2:
        prev.extend(g)
    else:
        merged.append(g)
groups = merged

tk = []
for g in groups:
    a = [w for w, _, _ in g]; t = [x for _, x, _ in g]; n = len(a); h = (n + 1) // 2
    tk.append({"start": round(max(0.0, t[0]-0.06), 3), "end": 0.0,
               "style": "emphasis" if any(x in " ".join(a) for x in ("653,000","365,000")) else "regular",
               "words": a, "times": t, "lines": [n] if n <= 3 else [h, n - h]})
for i, c in enumerate(tk):
    nxt = tk[i+1]["start"] if i + 1 < len(tk) else LAST
    c["end"] = round(min(nxt - 0.02, c["times"][-1] + 1.15), 3)
    if c["end"] < c["times"][-1] + 0.18:
        c["end"] = round(c["times"][-1] + 0.18, 3)
        if i + 1 < len(tk): tk[i+1]["start"] = round(c["end"] + 0.02, 3)
tk[-1]["end"] = min(tk[-1]["end"], LAST)
json.dump(tk, open(os.path.join(HERE, "caption-track.json"), "w"), ensure_ascii=False, indent=1)
print("cut %.2fs   captions %d   words %d   truncated %d   overlaps %d"
      % (LAST, len(tk), sum(len(c["words"]) for c in tk),
         sum(1 for c in tk if c["end"] < c["times"][-1] + 0.17),
         sum(1 for i in range(len(tk)-1) if tk[i]["end"] > tk[i+1]["start"] + 1e-6)))
for i, c in enumerate(tk, 1):
    print("%2d. [%5.2f-%5.2f] %-9s %s" % (i, c["start"], c["end"], c["style"], " ".join(c["words"])))
