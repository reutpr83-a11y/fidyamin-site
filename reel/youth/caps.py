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

# How far the spoken word grows, and how much extra air the line reserves so
# that growth never collides with its neighbour.
POP, SPACE = 0.10, 1.9

# The entrance takes 140ms to finish, so a word timed at t only becomes
# readable at t+0.14 - the whole track reads late even when the times are
# right. LEAD starts it early so the word is fully up ON the syllable, and
# a caption reading a hair early is far less noticeable than one lagging.
LEAD = 0.13

def _word_tile(word, font, stroke, pad):
    """A word on its own transparent tile, so it can be scaled without
    reflowing the line around it."""
    probe = ImageDraw.Draw(Image.new("RGBA", (1, 1)))
    w = int(tw(probe, word, font)) + pad * 2
    h = int(font.size * 1.9) + pad * 2
    tile = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(tile)
    d.text((pad, pad), word, font=font, fill=WHITE,
           direction="ltr" if is_num(word) else "rtl",
           stroke_width=stroke, stroke_fill=(0, 0, 0, 255))
    return tile

def _pop(dt):
    """Scale curve for the word being spoken: out to 1.14, then settle."""
    if dt < 0:            return 0.0, 1.0
    if dt < 0.09:         k = dt / 0.09;  return k, 1.0 + POP * (k * k * (3 - 2 * k))
    if dt < 0.31:         k = (dt - 0.09) / 0.22; return 1.0, 1.0 + POP * (1 - k * k * (3 - 2 * k))
    return 1.0, 1.0

def draw_cue(img, words, times, t, style, lines_spec=None):
    """words in logical order, times = when each is spoken, t = now."""
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
            lines.append(lw)
        sp = d.textlength(" ", font=f) * SPACE
        def width(lw, ff, spc):
            return sum(tw(d, x, ff) for x in lw) + spc * max(0, len(lw) - 1)
        while max(width(lw, f, sp) for lw in lines) > maxw and size > 56:
            size -= 2; f = F(size, wt); sp = d.textlength(" ", font=f) * SPACE
        lines = [(lw, width(lw, f, sp)) for lw in lines]
    else:
        lines, sp = layout(words, f, d, maxw)

    lh   = int(size * (1.14 if emph else 1.22))
    base = 1620
    top  = base - lh * len(lines)
    stroke, pad = 6, 14

    idx = 0
    for li, (lw, lwidth) in enumerate(lines):
        y = top + li * lh
        x = (880 if emph else (W + lwidth) / 2)
        for word in lw:
            ww = tw(d, word, f)
            ts = times[idx] if idx < len(times) else times[-1]
            nxt = times[idx + 1] if idx + 1 < len(times) else ts + 0.45
            idx += 1
            dt = t - (ts - LEAD)
            if dt < 0:
                x -= ww + sp; continue
            k  = min(1.0, dt / 0.14); k = k * k * (3 - 2 * k)   # entrance
            rise = int((1 - k) * 16)
            # the pop still lands on the syllable itself, not on the entrance
            _, scale = _pop(t - ts) if t < nxt + 0.31 else (1.0, 1.0)
            tile = _word_tile(word, f, stroke, pad)
            if scale != 1.0:
                tile = tile.resize((max(1, int(tile.width * scale)),
                                    max(1, int(tile.height * scale))), Image.LANCZOS)
            if k < 1.0:
                tile.putalpha(tile.getchannel("A").point(lambda a: int(a * k)))
            cx = x - ww / 2
            cy = y + f.size * 0.95
            img.alpha_composite(tile, (int(cx - tile.width / 2),
                                       int(cy - tile.height / 2) + rise))
            x -= ww + sp
    if emph:
        d.rectangle([912, top + 8, 918, base - 6], fill=(255, 255, 255, 235))
