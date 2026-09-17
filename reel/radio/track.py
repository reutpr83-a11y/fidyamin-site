# -*- coding: utf-8 -*-
"""Turn the word list into a caption track on the reel clock.

Words carry start times only, so a word ends where the next one begins. Words
are grouped into captions that fit two lines; a gap longer than GAP also
starts a new caption, because a caption that spans a pause reads as one breath
when it was two.
"""
import json
from PIL import Image, ImageDraw
import design as D

LEAD = 0.12          # a word lights this early so it is up ON the syllable
TAIL = 0.40          # how long the last word of a caption holds
GAP  = 0.45          # a real pause this long breaks the caption

def dur(word):
    """The transcriber returns no end times, so a word length is estimated
    from its letters. Without this, a long word looks like a pause: "שלחה"
    to "נציגת" is 0.64s start to start and is not a break at all."""
    return min(0.90, max(0.12, 0.055 * len(word) + 0.06))
MAXW = 830           # caption line width
MAXW_BY = {"run": 880, "card": 880, "hook": 700, "fig": 880}
                     # a hook wraps sooner so it splits into two lines that
                     # each say something, instead of orphaning its last word

# style per segment: list of (style, speaker, split_at_source_time_or_None)
STYLE = {
 "setup":  [("run", 3, None)],
 "vote":   [("run", 3, None)],
 "concede":[("card",1, None)],
 "sure":   [("run", 2, None)],
 "but":    [("run", 2, None)],
 "fifty6": [("fig", 2, None)],
 "claim":  [("run", 2, None)],
 "q1":     [("card",1, None)],
 "argument": [("run", 2, None)],
 "clean":  [("run", 2, None)],
 "q2hook": [("card",1, None), ("hook",2, None)],
 "eng":    [("run", 2, None)],
 "supervise": [("run", 2, None)],
 "expect": [("run", 2, None)],
 "drain":  [("run", 2, None)],
 "q3":     [("card",1, None)],
 "hook2":  [("run", 2, 201.94)],          # run, then hook from this word on
 "felt":   [("hook",2, None)],
 "q4str":  [("card",1, None), ("run",2, None)],
 "repeat": [("run", 2, None)],
 "q5":     [("card",1, None)],
 "hook3":  [("hook",2, None)],
 "empty":  [("hook",2, None)],
}

SIZE = {"run": 66, "card": 58, "hook": 66, "fig": 66}

def build(mapfile="map.json", out="track.json"):
    m = json.load(open(mapfile))
    d = ImageDraw.Draw(Image.new("RGB", (10, 10)))
    caps = []
    for seg in m["segs"]:
        base = seg["start"] - seg["in"]        # source clock -> reel clock
        styles = STYLE[seg["id"]]
        for ti, turn in enumerate(seg["turns"]):
            style, spk, split = styles[min(ti, len(styles)-1)]
            words = [(t, w) for t, w in turn["words"]]
            # split the turn where a style change was asked for
            parts = [(style, words)]
            if split is not None:
                a = [x for x in words if x[0] <  split]
                b = [x for x in words if x[0] >= split]
                parts = [(style, a), ("hook", b)]
            for st, ws in parts:
                if not ws: continue
                f = D.F(SIZE[st], 800 if st in ("hook", "run", "fig") else 500)
                sp = d.textlength(" ", font=f)

                mw = MAXW_BY[st]
                def nlines(group):
                    """greedy wrap of a word group, returns the line count"""
                    n, w = 1, 0.0
                    for _, word in group:
                        ww = D.tw(d, word, f)
                        if w and w + sp + ww > mw:
                            n += 1; w = ww
                        else:
                            w += (sp if w else 0) + ww
                    return n

                chunk = []
                for i, (t, word) in enumerate(ws):
                    gap = (t - ws[i-1][0] - dur(ws[i-1][1])) if i else 0.0
                    if chunk and gap > GAP:
                        caps.append(make(chunk, st, spk, base, seg)); chunk = []
                    chunk.append((t, word))
                    if nlines(chunk) > 2:
                        chunk.pop()
                        # break at the end of a sentence if there is one far
                        # enough in, so a caption does not stop mid-phrase and
                        # leave its last two words stranded in the next one
                        cut = len(chunk)
                        for j in range(len(chunk) - 1, max(0, len(chunk)//3) - 1, -1):
                            if chunk[j][1].rstrip().endswith((".", "?", "!")):
                                cut = j + 1; break
                        # never leave a connective as the last word on screen
                        while cut > 2 and chunk[cut-1][1] in CONNECT:
                            cut -= 1
                        caps.append(make(chunk[:cut], st, spk, base, seg))
                        chunk = chunk[cut:] + [(t, word)]
                        while nlines(chunk) > 2:
                            caps.append(make(chunk[:-1], st, spk, base, seg))
                            chunk = chunk[-1:]
                if chunk:
                    caps.append(make(chunk, st, spk, base, seg))

    caps = _absorb(caps, d)
    caps = _unorphan(caps, d)
    caps.sort(key=lambda c: c["start"])
    # Never let one caption sit on top of the next. They all share one zone
    # now, so an overlap is not a soft handover, it is two lines of text drawn
    # over each other. A caption whose successor follows straight on is cut,
    # not faded: that is how subtitles have always worked.
    for i in range(len(caps)-1):
        caps[i]["end"] = min(caps[i]["end"], caps[i+1]["start"] - 0.02)
        caps[i]["hard"] = caps[i+1]["start"] - caps[i]["end"] < 0.35
    if caps: caps[-1]["hard"] = False
    json.dump(caps, open(out, "w"), ensure_ascii=False, indent=1)
    return caps

# Words that belong to what comes after them, not to what came before. A
# caption that ends on one of these reads as a sentence that fell over.
CONNECT = {"אם","אז","כי","אבל","וגם","ואז","שגם","גם","וזה","זה","את","של","על",
           "עם","כשאתה","שאתה","ואף","מה","לא","הוא","היא","הם","מכוח","אין","יש"}
UNITS   = {"מיליון","אלף","שקל","שקלים","₪"}

def _unorphan(caps, d):
    """Move a trailing connective, or a figure stranded from its unit, into the
    caption that follows it."""
    for i in range(len(caps) - 1):
        c, nx = caps[i], caps[i + 1]
        if len(c["words"]) < 2 or c["style"] != nx["style"] or c["speaker"] != nx["speaker"]:
            continue
        if nx["start"] - c["end"] > 1.6:
            continue
        last = c["words"][-1]
        move = last in CONNECT or (D.is_num(last) and nx["words"][0] in UNITS)
        if not move:
            continue
        f = D.F(SIZE[nx["style"]], 800 if nx["style"] in ("hook","run","fig") else 500)
        n, w, sp = 1, 0.0, d.textlength(" ", font=f)
        for word in [last] + nx["words"]:
            ww = D.tw(d, word, f)
            if w and w + sp + ww > MAXW_BY[nx["style"]]: n += 1; w = ww
            else: w += (sp if w else 0) + ww
        if n > 2:
            continue
        nx["words"] = [last] + nx["words"]
        nx["times"] = [c["times"][-1]] + nx["times"]
        nx["ends"]  = [c["ends"][-1]] + nx["ends"]
        nx["start"] = min(nx["start"], c["times"][-1])
        c["words"] = c["words"][:-1]; c["times"] = c["times"][:-1]; c["ends"] = c["ends"][:-1]
        c["end"] = min(c["end"], nx["start"] - 0.02)
    return [c for c in caps if c["words"]]

def _absorb(caps, d):
    """A caption of one or two words is a flicker, not a line. Fold it into the
    neighbour it belongs to whenever the two still fit two lines."""
    def fits(words, style):
        f = D.F(SIZE[style], 800 if style in ("hook","run","fig") else 500)
        n, w, sp = 1, 0.0, d.textlength(" ", font=f)
        for word in words:
            ww = D.tw(d, word, f)
            if w and w + sp + ww > MAXW_BY[style]: n += 1; w = ww
            else: w += (sp if w else 0) + ww
        return n <= 2

    # a short caption with nothing before it in its turn folds into the one after
    fwd = []
    for i, c in enumerate(caps):
        if (len(c["words"]) <= 2 and i + 1 < len(caps)):
            nx = caps[i+1]
            if (nx["style"] == c["style"] and nx["speaker"] == c["speaker"]
                    and nx["seg"] == c["seg"] and nx["start"] - c["end"] < 1.2
                    and fits(c["words"] + nx["words"], c["style"])):
                nx["words"] = c["words"] + nx["words"]
                nx["times"] = c["times"] + nx["times"]
                nx["ends"] = c["ends"] + nx["ends"]
                nx["start"] = c["start"]
                continue
        fwd.append(c)
    caps = fwd

    out = []
    for c in caps:
        if (out and len(c["words"]) <= 2 and out[-1]["style"] == c["style"]
                and out[-1]["speaker"] == c["speaker"] and out[-1]["seg"] == c["seg"]
                and c["start"] - out[-1]["end"] < 0.9):
            p = out[-1]
            f = D.F(SIZE[p["style"]], 800 if p["style"] in ("hook","run","fig") else 500)
            merged = p["words"] + c["words"]
            n, w, sp = 1, 0.0, d.textlength(" ", font=f)
            for word in merged:
                ww = D.tw(d, word, f)
                if w and w + sp + ww > MAXW_BY[p["style"]]: n += 1; w = ww
                else: w += (sp if w else 0) + ww
            if n <= 2:
                p["words"] = merged
                p["times"] += c["times"]; p["ends"] += c["ends"]
                p["end"] = c["end"]
                continue
        out.append(c)
    return out

def make(chunk, style, spk, base, seg):
    ends = [min(chunk[i+1][0], chunk[i][0] + dur(chunk[i][1]) + 0.12)
            for i in range(len(chunk)-1)] + [chunk[-1][0] + TAIL]
    return dict(style=style, speaker=spk, seg=seg["id"],
                start=round(base + chunk[0][0] - LEAD, 3),
                end=round(min(base + ends[-1], seg["start"] + seg["len"] + 0.25), 3),
                words=[w for _, w in chunk],
                times=[round(base + t - LEAD, 3) for t, _ in chunk],
                ends=[round(base + e, 3) for e in ends])

if __name__ == "__main__":
    caps = build()
    print("%d captions" % len(caps))
    for c in caps:
        print("  %6.2f-%6.2f %-4s s%d  %s" % (c["start"], c["end"], c["style"],
                                              c["speaker"], " ".join(c["words"])))
