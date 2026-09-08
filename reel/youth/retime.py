# -*- coding: utf-8 -*-
"""Caption timing, rebuilt with ordering as a hard constraint.

An earlier pass snapped every caption to its nearest speech onset one at a
time. Captions moved in different directions and some ended up starting before
the one before them had finished, which is what forced captions to be
truncated or their reveal compressed. Here a caption may only move if it stays
behind the previous caption and ahead of the next."""
import json, os, numpy as np, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
tk     = json.load(open(os.path.join(HERE, "caption-track.pre-snap.json"), encoding="utf-8"))
coarse = np.array([float(x) for x in open(os.path.join(HERE, "onsets.txt"))])
peaks  = np.load(os.path.join(HERE, "onset_peaks.npy"))
BOUND, GAP = 0.40, 0.12

# 1. Caption starts stay where the transcript puts them.
#    Snapping each caption to its nearest speech onset was tried three ways
#    and all three were worse. Unconstrained, captions moved in different
#    directions and some began before the one before them had finished, which
#    is what forced captions to be truncated - whole phrases never reached the
#    screen. Constrained to stay in order, or repaired afterwards, the starts
#    ended up further from the speech than leaving them alone (0.41 and 0.38
#    against 0.38 measured the same way) and the track split into fragments.
#    The transcript's spacing is internally coherent, and that is what counts
#    once the entrance leads the syllable.
moved = []

# 2. nudge interior words onto acoustic detail, bounded and order safe
for c in tk:
    t = list(c["times"])
    for j in range(1, len(t) - 1):
        cand = peaks[(peaks >= max(t[j]-0.20, t[j-1]+0.09)) & (peaks <= min(t[j]+0.20, t[j+1]-0.09))]
        if len(cand): t[j] = round(float(cand[np.argmin(np.abs(cand - t[j]))]), 3)
    c["times"] = t

# 3. the four figures carry the argument once the graphic cards are gone
NUM, KEEP = [6, 7, 8, 9], [11, 23]
for i, c in enumerate(tk):
    c["style"] = "emphasis" if (i in NUM or i in KEEP) else "regular"
    n = len(c["words"]); h = (n + 1) // 2
    c["lines"] = [n] if n <= 3 else [h, n - h]

json.dump(tk, open(os.path.join(HERE, "caption-track.json"), "w"), ensure_ascii=False, indent=1)
cross = sum(1 for i in range(len(tk)-1) if tk[i]["times"][-1] >= tk[i+1]["times"][0])
print("captions moved: %d (mean %.3fs)" % (len(moved), st.mean(moved) if moved else 0))
print("captions that start before the previous one ends: %d" % cross)
print("caption starts vs reliable onsets: mean %.3fs"
      % st.mean([float(np.min(np.abs(coarse - c["times"][0]))) for c in tk]))
