# -*- coding: utf-8 -*-
"""Decides the framing for every caption, so a locked-off take reads as a
three camera edit. Framing changes only on an idea boundary - a gap between
captions - never mid sentence."""
import json, os, sys

GAP = 0.30          # a pause this long or longer is an idea boundary
MAX_CUES = 2        # never hold one framing for more than this many captions
CYCLE = ["wide", "mid", "close"]

def plan(track):
    out, k, since = [], 0, 0
    for i, c in enumerate(track):
        gap = c["start"] - track[i-1]["end"] if i else 99
        if i and (gap >= GAP or since >= MAX_CUES):
            k = (k + 1) % len(CYCLE)
            since = 0
        since += 1
        out.append({"start": c["start"], "end": c["end"], "shot": CYCLE[k]})
    # merge neighbours that share a framing
    merged = []
    for s in out:
        if merged and merged[-1]["shot"] == s["shot"]:
            merged[-1]["end"] = s["end"]
        else:
            merged.append(dict(s))
    return merged

if __name__ == "__main__":
    HERE = os.path.dirname(os.path.abspath(__file__))
    track = json.load(open(os.path.join(HERE, "caption-track.json"), encoding="utf-8"))
    p = plan(track)
    json.dump(p, open(os.path.join(HERE, "shot-plan.json"), "w"), indent=1)
    from collections import Counter
    print("shots: %d   %s" % (len(p), Counter(s["shot"] for s in p)))
    print("mean shot length: %.1fs" % (sum(s["end"]-s["start"] for s in p)/len(p)))
    for s in p[:6]:
        print("  %6.2f-%6.2f  %s" % (s["start"], s["end"], s["shot"]))

# Framing table: zoom, and the vertical anchor of the crop (0.5 = centred,
# lower = more headroom kept). Tuned so the step between framings reads as a
# cut rather than a wobble; 12 percent was too subtle to register.
# Re-check these on the real take, whose wide is genuinely wider than the
# 1080p plate they were first tried on.
# The angle crop is tight now, so these steps are small: any more would mean
# scaling past the source width and softening the picture.
FRAMING = {
    "wide":  (1.00, 0.50),
    "mid":   (1.06, 0.45),
    "close": (1.12, 0.40),
}

def vf(shot, w=1080, h=1920):
    z, y = FRAMING[shot]
    return ("scale=iw*%.3f:ih*%.3f,crop=%d:%d:(iw-%d)/2:(ih-%d)*%.3f"
            % (z, z, w, h, w, h, y))
