# -*- coding: utf-8 -*-
"""Caption track for the uncut take.

Every earlier version cut the take into 17 pieces and mapped the transcript's
word times through that edit. The mapping was correct and the cuts all landed
in silence, but it is a layer that can only lose accuracy. Left uncut, a word's
caption time IS its transcript time minus the head trim. Nothing to drift."""
import json, os

HERE = os.path.dirname(os.path.abspath(__file__))
HEAD, TAIL_PAD = 3.50, 0.90          # first word lands at 3.92
tr = json.load(open(os.path.join(HERE, "youth-transcript.json"), encoding="utf-8"))

FIX = {"והשארתם": "ואישרתם"}         # corrections the client made
words = []
for seg in tr:
    for w in seg["words"]:
        t = w["s"] - HEAD
        if t < -0.05: continue
        words.append((FIX.get(w["w"].strip(), w["w"].strip()), round(t, 3)))

# the transcript splits "653,000" into "653" and ",000"; glue them back
joined = []
for w, t in words:
    if joined and w.startswith(",") and joined[-1][0][-1:].isdigit():
        joined[-1] = (joined[-1][0] + w, joined[-1][1])
    else:
        joined.append((w, t))
words = joined

# the client's rewrites, applied to the words themselves so that grouping,
# emphasis and line breaking all see the final text
fixed = []
for i, (w, t) in enumerate(words):
    if w == "השתגעתם": w = "השתגעתם?"
    if w == "שהיה" and i + 1 < len(words) and words[i+1][0] == "לנו":
        fixed.append(("שלנו", t)); continue
    if w == "לנו" and fixed and fixed[-1][0] == "שלנו": continue
    fixed.append((w, t))
words = fixed

MAXW, MAXCH, PAUSE = 8, 46, 0.80
groups, cur = [], []
for i, (w, t) in enumerate(words):
    cur.append((w, t))
    gap = words[i + 1][1] - t if i + 1 < len(words) else 9.9
    chars = sum(len(x) + 1 for x, _ in cur)
    if (w.endswith((".", "?", "!")) or gap >= PAUSE
            or len(cur) >= MAXW or chars >= MAXCH or i == len(words) - 1):
        groups.append(cur); cur = []
if cur: groups.append(cur)

# "השתגעתם" and the phrase after it are one thought, and the client rewrote them
out = []
for g in groups:
    ws = [w for w, _ in g]
    if ws == ["השתגעתם"]:
        g = [("השתגעתם?", g[0][1])]
    if ws[:3] == ["מהנוער", "שהיה", "לנו"]:
        g = [("מהנוער", g[0][1]), ("שלנו", g[1][1]), *g[3:]]
    out.append(g)
groups = out

EMPH = ("653,000", "365,000", "150,000", "52,000")
LAST = round(words[-1][1] + TAIL_PAD, 3)
track = []
for g in groups:
    ws = [w for w, _ in g]; ts = [t for _, t in g]
    n = len(ws); h = (n + 1) // 2
    joined = " ".join(ws)
    track.append({"start": round(ts[0] - 0.06, 3), "end": 0.0,
                  "style": "emphasis" if any(e in joined for e in EMPH) else "regular",
                  "words": ws, "times": ts, "lines": [n] if n <= 3 else [h, n - h]})
for i, c in enumerate(track):
    nxt = track[i + 1]["start"] if i + 1 < len(track) else LAST
    c["end"] = round(min(nxt - 0.02, c["times"][-1] + 1.15), 3)
    if c["end"] < c["times"][-1] + 0.18:
        c["end"] = round(c["times"][-1] + 0.18, 3)
        if i + 1 < len(track): track[i + 1]["start"] = round(c["end"] + 0.02, 3)
track[-1]["end"] = LAST

json.dump(track, open(os.path.join(HERE, "caption-track.json"), "w"), ensure_ascii=False, indent=1)
print("uncut duration: %.2fs   captions: %d   words: %d" % (LAST, len(track), sum(len(c["words"]) for c in track)))
print("truncated: %d   overlaps: %d"
      % (sum(1 for c in track if c["end"] < c["times"][-1] + 0.17),
         sum(1 for i in range(len(track)-1) if track[i]["end"] > track[i+1]["start"] + 1e-6)))
