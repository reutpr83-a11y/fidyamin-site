# -*- coding: utf-8 -*-
"""Heebo captions, word by word on the speech, rendered as RGBA frames.
RTL through libraqm - ffmpeg's drawtext reverses Hebrew, so text never goes
near it. Follows BRAND.md: white only, no coloured words, navy scrim."""
import os, json, math
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
NAVY  = (11, 43, 68)
WHITE = (255, 255, 255, 255)
HERE  = os.path.dirname(os.path.abspath(__file__))
FONT  = os.path.join(HERE, "Heebo.ttf")

_fc = {}
def F(size, weight):
    k = (size, weight)
    if k not in _fc:
        f = ImageFont.truetype(FONT, size)
        f.set_variation_by_axes([weight])
        _fc[k] = f
    return _fc[k]

def is_num(s):
    return any(c.isdigit() for c in s)

def tw(d, s, f):
    return d.textlength(s, font=f, direction="ltr" if is_num(s) else "rtl") if s else 0

def scrim():
    """Navy gradient: 0 at y1380, .66 at y1660, solid to the bottom."""
    g = Image.new("RGBA", (W, H), (0, 0, 0, 0)); px = g.load()
    for y in range(H):
        if y < 1380:   a = 0.0
        elif y < 1660: a = 0.66 * ((y - 1380) / 280) ** 1.4
        else:          a = 0.66 + 0.34 * min(1.0, (y - 1660) / 180)
        if a > 0:
            v = int(255 * a)
            for x in range(W):
                px[x, y] = (*NAVY, v)
    return g

def layout(words, f, d, maxw):
    """Greedy two-line wrap, returns [[(word, x_right_offset)], ...] widths in RTL."""
    sp = d.textlength(" ", font=f)
    lines, cur, curw = [], [], 0.0
    for w in words:
        ww = tw(d, w, f)
        add = ww + (sp if cur else 0)
        if cur and curw + add > maxw:
            lines.append((cur, curw)); cur, curw = [w], ww
        else:
            cur.append(w); curw += add
    if cur: lines.append((cur, curw))
    return lines[:2], sp

def draw_cue(img, words, times, t, style, lines_spec=None):
    """words: list[str]; times: list[float] start per word; t: current time.
    lines_spec: word counts per line, so the cue's own break is honoured
    instead of auto wrapping (which silently dropped the tail)."""
    d = ImageDraw.Draw(img)
    emph  = style == "emphasis"
    size  = 104 if emph else 84
    wt    = 800 if emph else 600
    maxw  = 760 if emph else 880
    f     = F(size, wt)
    if lines_spec:
        lines, i = [], 0
        for n in lines_spec:
            lw = words[i:i + n]; i += n
            lines.append((lw, sum(tw(d, w, f) for w in lw)
                          + d.textlength(" ", font=f) * max(0, len(lw) - 1)))
        sp = d.textlength(" ", font=f)
        # shrink until the widest line fits the column
        while lines and max(l[1] for l in lines) > maxw and size > 56:
            size -= 2; f = F(size, wt); sp = d.textlength(" ", font=f)
            lines = [(lw, sum(tw(d, w, f) for w in lw) + sp * max(0, len(lw) - 1))
                     for lw, _ in lines]
    else:
        lines, sp = layout(words, f, d, maxw)
    lh    = int(size * (1.14 if emph else 1.22))
    base  = 1620
    top   = base - lh * len(lines)

    idx = 0
    for li, (lw, lwidth) in enumerate(lines):
        y = top + li * lh
        # emphasis is flush right to the 880 column; regular is centred
        x = (880 if emph else (W + lwidth) / 2)
        for w in lw:
            ww = tw(d, w, f)
            ts = times[idx]; idx += 1
            dt = t - ts
            if dt < 0:
                x -= ww + sp; continue
            k  = min(1.0, dt / 0.14)              # 140ms rise + fade
            k  = k * k * (3 - 2 * k)
            off = int((1 - k) * 16)
            a   = int(255 * k)
            for pass_ in ((3, (11, 43, 68, int(a * .55))), (0, (255, 255, 255, a))):
                blur, col = pass_
                d.text((x - ww, y + off), w, font=f, fill=col,
                       direction="ltr" if is_num(w) else "rtl",
                       stroke_width=blur, stroke_fill=col if blur else None)
            x -= ww + sp
    if emph:
        # white rule beside the block, at 912px
        d.rectangle([912, top + 8, 918, base - 6], fill=(255, 255, 255, 235))
