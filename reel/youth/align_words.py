# -*- coding: utf-8 -*-
"""Puts every caption word on a real acoustic onset.

The transcript's word times average right but scatter badly, which is what
makes the captions feel out of step. This aligns each caption's words to
onsets detected in the audio, in order, with the expected spacing coming from
how long each word is rather than from the transcript."""
import json, os, numpy as np, statistics as st

HERE = os.path.dirname(os.path.abspath(__file__))
peaks = np.load(os.path.join(HERE, "onset_peaks.npy"))
tk = json.load(open(os.path.join(HERE, "caption-track.json"), encoding="utf-8"))

def expected(words, t0, t1):
    """Spread the span over the words, weighted by length; every word gets a floor."""
    w = np.array([max(2.0, len(x)) for x in words], dtype=float)
    frac = np.concatenate([[0.0], np.cumsum(w)[:-1]]) / w.sum()
    return t0 + frac * (t1 - t0)

def assign(cands, want):
    """Monotonic least-cost assignment of len(want) onsets out of cands."""
    n, m = len(cands), len(want)
    if n < m:
        return None
    INF = 1e9
    cost = np.abs(cands[:, None] - want[None, :])
    dp = np.full((n + 1, m + 1), INF); dp[:, 0] = 0.0
    back = np.zeros((n + 1, m + 1), dtype=int)
    for i in range(1, n + 1):
        for j in range(1, min(m, i) + 1):
            skip = dp[i - 1, j]
            take = dp[i - 1, j - 1] + cost[i - 1, j - 1]
            if take <= skip: dp[i, j], back[i, j] = take, 1
            else:            dp[i, j], back[i, j] = skip, 0
    out, i, j = [], n, m
    while j > 0:
        if back[i, j] == 1: out.append(cands[i - 1]); j -= 1
        i -= 1
    return np.array(out[::-1])

moved = []
for ci, c in enumerate(tk):
    words, times = c["words"], c["times"]
    t0, t1 = times[0], times[-1]
    span = max(t1 - t0, 0.35 * len(words))
    lo, hi = t0 - 0.22, t0 + span + 0.30
    cands = peaks[(peaks >= lo) & (peaks <= hi)]
    want = expected(words, t0, t0 + span)
    got = assign(cands, want)
    if got is None:
        continue
    # never let a word land before the one before it, or run past the caption
    got = np.maximum.accumulate(got)
    if ci + 1 < len(tk) and got[-1] > tk[ci + 1]["times"][0] - 0.15:
        continue
    moved.append(float(np.abs(got - np.array(times)).max()))
    c["times"] = [round(float(t), 3) for t in got]
    c["start"] = round(float(got[0]) - 0.06, 3)
    c["end"]   = round(float(got[-1]) + 1.10, 3)

for i in range(len(tk) - 1):
    tk[i]["end"] = round(min(tk[i]["end"], tk[i + 1]["start"] - 0.02), 3)
tk[-1]["end"] = min(tk[-1]["end"], 71.90)
for i, c in enumerate(tk):
    if c["end"] <= c["start"]:
        nxt = tk[i + 1]["start"] if i + 1 < len(tk) else 71.90
        c["end"] = round(max(c["start"] + 0.50, nxt - 0.02), 3)

json.dump(tk, open(os.path.join(HERE, "caption-track.json"), "w"), ensure_ascii=False, indent=1)
allw = [t for c in tk for t in c["times"]]
err = [float(np.min(np.abs(peaks - w))) for w in allw]
print("captions realigned: %d of %d (largest single word move %.2fs)" % (len(moved), len(tk), max(moved)))
print("words vs onsets now: mean %.3fs  median %.3fs  worst %.3fs" % (st.mean(err), st.median(err), max(err)))
print("within 0.10s: %d of %d" % (sum(1 for e in err if e < 0.10), len(err)))
print("overlapping captions: %d" % sum(1 for i in range(len(tk)-1) if tk[i]["end"] > tk[i+1]["start"]))
