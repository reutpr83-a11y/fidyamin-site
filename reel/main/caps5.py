# -*- coding: utf-8 -*-
"""Captions for the main reel, on the dissolve aware timeline.

Beats overlap by the dissolve length, so a word's place comes from its beat's
start rather than a running sum of durations. A word only counts as inside a
beat if the whole word is inside it, otherwise a half word leaks across a
dissolve; and a caption never spans two beats, because the picture changes
underneath it."""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__))
m = json.load(open(os.path.join(HERE, "map5.json")))
tr = json.load(open(os.path.join(HERE, "transcript_155953.json"), encoding="utf-8"))
beats, durs, starts, XF = m["beats"], m["durs"], m["starts"], m["xf"]
LAST = round(m["total"], 3)

def place(a, b):
    for i, (x, _) in enumerate(beats):
        if x - 1e-6 <= a and b <= x + durs[i] + 1e-6:
            return starts[i] + (a - x), i
    return None, None

raw = []
for seg in tr:
    for w in seg["words"]:
        o, bi = place(w["s"], w["e"])
        if o is not None:
            # the end time travels with the word: gaps are measured from where
            # a word stops, and a figure glued from two tokens stops at the
            # second of them, not the first
            raw.append((w["w"].strip(), round(o, 3), round(o + (w["e"] - w["s"]), 3), bi))
raw.sort(key=lambda x: x[1])

# the transcriber splits figures across tokens: "1" + ".3", "מ" + "-400" + ",000"
ws = []
for w, t, e, bi in raw:
    if ws and w[:1] in ".,-" and (ws[-1][0][-1:].isdigit() or w[:1] == "-"):
        ws[-1] = (ws[-1][0] + w, ws[-1][1], e, ws[-1][3])
    else:
        ws.append((w, t, e, bi))

MAXW, MAXCH, PAUSE = 9, 56, 0.80
# Break the word stream into clauses first, then fit captions inside each
# clause. Splitting a clause evenly is what keeps "אנשי" and "מקצוע" together:
# filling to the limit and letting the remainder fall through is exactly how
# a caption ends up holding one orphan word.
PIVOT = ("מול", "אבל")

def clauses(ws):
    out, cur = [], []
    for i, (w, t, e, bi) in enumerate(ws):
        nxt = ws[i + 1] if i + 1 < len(ws) else None
        starts_pivot = nxt is not None and nxt[0] in PIVOT and len(cur) >= 2
        cur.append((w, t, bi))
        gap = nxt[1] - e if nxt else 9.9
        beat_ends = nxt is None or nxt[3] != bi
        if (beat_ends or w.endswith((".", "?", "!")) or gap >= PAUSE
                or starts_pivot or (w.endswith(",") and len(cur) >= 4)):
            out.append(cur); cur = []
    if cur: out.append(cur)
    return out

def split_even(c):
    n = len(c); ch = sum(len(x) + 1 for x, _, _ in c)
    g = max(1, -(-n // MAXW), -(-ch // MAXCH))
    if g == 1: return [c]
    size = -(-n // g)
    return [c[i:i + size] for i in range(0, n, size)]

groups = [g for c in clauses(ws) for g in split_even(c)]

# every caption is regular: the two figures are carried by the data panels,
# which are on screen for exactly those lines, and a second right aligned
# element competing with them would only crowd the frame
tk = []
for g in groups:
    a = [w for w, _, _ in g]; t = [x for _, x, _ in g]; n = len(a); h = (n + 1) // 2
    tk.append({"start": round(max(0.0, t[0] - 0.06), 3), "end": 0.0,
               "style": "regular",
               "words": a, "times": t, "lines": [n] if n <= 3 else [h, n - h]})
# LEAD in caps.py starts a word 0.13s before it is spoken, so the next
# caption's first word is already on screen 0.07s before that caption's
# nominal start. Clearing the previous one only 0.02s early left the two
# overlapping for four frames; GAP covers the lead.
GAP = 0.09
for i, c in enumerate(tk):
    nxt = tk[i+1]["start"] if i + 1 < len(tk) else LAST
    c["end"] = round(min(nxt - GAP, c["times"][-1] + 1.15), 3)
    if c["end"] < c["times"][-1] + 0.18:
        c["end"] = round(c["times"][-1] + 0.18, 3)
        if i + 1 < len(tk): tk[i+1]["start"] = round(c["end"] + GAP, 3)
tk[-1]["end"] = min(tk[-1]["end"], LAST)
json.dump(tk, open(os.path.join(HERE, "caption-track.json"), "w"), ensure_ascii=False, indent=1)
print("cut %.2fs   captions %d   words %d   truncated %d   overlaps %d"
      % (LAST, len(tk), sum(len(c["words"]) for c in tk),
         sum(1 for c in tk if c["end"] < c["times"][-1] + 0.17),
         sum(1 for i in range(len(tk)-1) if tk[i]["end"] > tk[i+1]["start"] - 0.089)))
for i, c in enumerate(tk, 1):
    print("%2d. [%6.2f-%6.2f] %-9s %s" % (i, c["start"], c["end"], c["style"], " ".join(c["words"])))
