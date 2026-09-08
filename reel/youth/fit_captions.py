# -*- coding: utf-8 -*-
"""Splits captions that cannot fit in the time they have.

The inherited cue list packs two of the reference cut's captions into one, so
a caption often needs three or four seconds and gets one. Rather than dropping
its tail or racing the reveal, the caption is split at its own clause boundary.
Word order and word times are never touched."""
import json, os, numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
# A caption only needs to outlive its last word by enough for that word to
# render and be seen; in continuous speech the next phrase starts right after.
# 0.55 was far too strict and split the track into fragments.
MINHOLD, TAIL, LAST = 0.18, 1.15, 71.90

def windows(tk):
    for i, c in enumerate(tk):
        nxt = tk[i + 1]["times"][0] - 0.06 if i + 1 < len(tk) else LAST
        c["start"] = round(c["times"][0] - 0.06, 3)
        c["end"] = round(min(nxt - 0.02, c["times"][-1] + TAIL), 3)
    tk[-1]["end"] = min(tk[-1]["end"], LAST)

def room_short(c, nxt_start):
    return (min(nxt_start - 0.02, c["times"][-1] + TAIL) - c["times"][-1]) < MINHOLD

def split_at(c):
    """Prefer a clause boundary, else the middle."""
    n = len(c["words"])
    if n < 4: return None
    commas = [i for i in range(n - 2) if c["words"][i].endswith((",", ".", "?", "!"))]
    mid = n // 2
    k = min(commas, key=lambda i: abs(i - mid)) + 1 if commas else mid
    k = max(2, min(k, n - 2))
    a = {"style": c["style"], "words": c["words"][:k], "times": c["times"][:k]}
    b = {"style": c["style"], "words": c["words"][k:], "times": c["times"][k:]}
    for d in (a, b):
        m = len(d["words"]); h = (m + 1) // 2
        d["lines"] = [m] if m <= 3 else [h, m - h]
        d["start"] = 0.0; d["end"] = 0.0
    return a, b

tk = json.load(open(os.path.join(HERE, "caption-track.json"), encoding="utf-8"))
for _ in range(6):
    windows(tk)
    out, changed = [], False
    for i, c in enumerate(tk):
        nxt = tk[i + 1]["times"][0] - 0.06 if i + 1 < len(tk) else LAST
        if room_short(c, nxt):
            s = split_at(c)
            if s: out.extend(s); changed = True; continue
        out.append(c)
    tk = out
    if not changed: break
windows(tk)

# anything still short gets the hold it needs, pushing the next caption back
for i, c in enumerate(tk):
    need = c["times"][-1] + MINHOLD
    if c["end"] < need:
        c["end"] = round(min(need, LAST), 3)
        if i + 1 < len(tk) and tk[i + 1]["start"] < c["end"] + 0.02:
            tk[i + 1]["start"] = round(c["end"] + 0.02, 3)
tk[-1]["end"] = min(tk[-1]["end"], LAST)

json.dump(tk, open(os.path.join(HERE, "caption-track.json"), "w"), ensure_ascii=False, indent=1)
order = all(all(c["times"][j] <= c["times"][j+1] for j in range(len(c["times"])-1)) for c in tk)
bad = sum(1 for c in tk if c["end"] < c["times"][-1] + MINHOLD - 1e-3)
ov  = sum(1 for i in range(len(tk)-1) if tk[i]["end"] > tk[i+1]["start"] + 1e-6)
chars = max(sum(len(w)+1 for w in c["words"]) for c in tk)
print("captions: %d   words: %d   order intact: %s" % (len(tk), sum(len(c["words"]) for c in tk), order))
print("cut before last word: %d   overlaps: %d   longest caption: %d chars" % (bad, ov, chars))
print("shortest window: %.2fs   mean window: %.2fs"
      % (min(c["end"]-c["start"] for c in tk), sum(c["end"]-c["start"] for c in tk)/len(tk)))
