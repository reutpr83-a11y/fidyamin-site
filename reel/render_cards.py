# -*- coding: utf-8 -*-
"""Reel text cards, 1080x1920.
RGBA output for compositing over the blurred freeze frame + flattened preview
for visual RTL verification. Layout of the comparison cards is identical by
construction: geometry constants below are shared, only content differs."""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
WHITE = (255, 255, 255, 255)
BLUE  = (0, 168, 255, 255)          # #00A8FF  -> ASS &H00FFA800&
DIM   = (255, 255, 255, 175)
BOXBG = (255, 255, 255, 20)
BOXLN = (255, 255, 255, 60)

HERE  = os.path.dirname(os.path.abspath(__file__))
FDIR  = os.path.join(HERE, "fonts")
REG   = os.path.join(FDIR, "buE0po24ccnh31GVMABJ8A.ttf")
BOLD  = os.path.join(FDIR, "buExpo24ccnh31GVMABxTC8f-A.ttf")

_fc = {}
def F(path, size):
    if (path, size) not in _fc:
        _fc[(path, size)] = ImageFont.truetype(path, size)
    return _fc[(path, size)]

def is_num(s):
    return any(c.isdigit() for c in s)

def tw(d, s, font):
    if not s:
        return 0
    return d.textlength(s, font=font, direction="ltr" if is_num(s) else "rtl")

def tokenize(segs):
    """(text,color)* in logical order -> [(word, color, space_after)] preserving
    original spacing, including across segment boundaries."""
    toks = []
    for text, col in segs:
        parts = text.split(" ")
        for i, p in enumerate(parts):
            last = i == len(parts) - 1
            if p:
                toks.append([p, col, not last])
            elif toks and not last:
                toks[-1][2] = True
    return toks

def line_w(d, toks, font):
    sp = d.textlength(" ", font=font)
    w = sum(tw(d, t, font) for t, _, _ in toks)
    w += sp * sum(1 for i, (_, _, s) in enumerate(toks) if s and i < len(toks) - 1)
    return w

def draw_line_rtl(d, toks, font, cx, y, default=WHITE, stroke=0, stroke_fill=None):
    """Draws a single line centred on cx, laid out right-to-left."""
    sp = d.textlength(" ", font=font)
    x = cx + line_w(d, toks, font) / 2
    for i, (t, col, space) in enumerate(toks):
        w = tw(d, t, font)
        d.text((x - w, y), t, font=font, fill=col or default,
               direction="ltr" if is_num(t) else "rtl",
               stroke_width=stroke, stroke_fill=stroke_fill)
        x -= w
        if space and i < len(toks) - 1:
            x -= sp

def wrap(d, segs, font, maxw):
    toks, lines, cur = tokenize(segs), [], []
    for t in toks:
        if cur and line_w(d, cur + [t], font) > maxw:
            lines.append(cur); cur = [t]
        else:
            cur.append(t)
    if cur:
        lines.append(cur)
    return lines

def block(d, segs, font, cx, y, maxw, lh, default=WHITE):
    for l in wrap(d, segs, font, maxw):
        draw_line_rtl(d, l, font, cx, y, default)
        y += lh
    return y

def block_h(d, segs, font, maxw, lh):
    return len(wrap(d, segs, font, maxw)) * lh

def new_card():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))

def save(img, name):
    img.save(os.path.join(HERE, "cards", name + ".png"))
    prev = Image.new("RGBA", (W, H), (14, 17, 22, 255))
    prev.alpha_composite(img)
    prev.convert("RGB").save(os.path.join(HERE, "cards", name + "_preview.jpg"), quality=92)

# ------------------------------------------------------------------ statements
def statement_card(name, blocks, size=86, para_gap=40):
    img = new_card(); d = ImageDraw.Draw(img)
    f, lh = F(BOLD, size), int(size * 1.2)
    laid = [wrap(d, b, f, W - 150) for b in blocks]
    th = sum(len(b) * lh for b in laid) + para_gap * (len(laid) - 1)
    y = (H - th) // 2
    for b in laid:
        for l in b:
            draw_line_rtl(d, l, f, W / 2, y); y += lh
        y += para_gap
    save(img, name)

# ------------------------------------------------- comparison card (fixed grid)
TOPLINE_Y        = 330
BOX_TOP, BOX_BOT = 640, 1360
BOX_W, MARGIN    = 470, 50
GAP              = W - 2 * MARGIN - 2 * BOX_W
BOX_R_X          = MARGIN + BOX_W + GAP     # right box  = 2018
BOX_L_X          = MARGIN                   # left  box  = 2026
HEAD_Y           = BOX_TOP + 44

def comparison_card(name, topline, r_head, r_body, l_head, l_body):
    img = new_card(); d = ImageDraw.Draw(img)
    f_top, f_head, f_body = F(REG, 56), F(BOLD, 50), F(BOLD, 66)
    lh_body, inner = int(66 * 1.22), BOX_W - 56

    block(d, topline, f_top, W / 2, TOPLINE_Y, W - 150, int(56 * 1.22), default=DIM)

    for bx, head, body in ((BOX_R_X, r_head, r_body), (BOX_L_X, l_head, l_body)):
        d.rounded_rectangle([bx, BOX_TOP, bx + BOX_W, BOX_BOT], radius=26,
                            fill=BOXBG, outline=BOXLN, width=3)
        cx = bx + BOX_W / 2
        block(d, head, f_head, cx, HEAD_Y, inner, int(50 * 1.2), default=DIM)
        # body vertically centred in the area under the header
        area_top, area_bot = BOX_TOP + 150, BOX_BOT - 40
        gap = 30
        th = sum(block_h(d, p, f_body, inner, lh_body) for p in body) + gap * (len(body) - 1)
        y = area_top + (area_bot - area_top - th) / 2
        for p in body:
            y = block(d, p, f_body, cx, y, inner, lh_body) + gap
    save(img, name)
