# -*- coding: utf-8 -*-
"""Design mockup for the radio interview reel.

Clean navy ground, no photography behind the words. The station and the
programme sit at the top, the topic under them, the speaker is named on every
frame, and the captions carry the body. Built from the same palette and the
same Heebo as the budget reels so the two read as one family.
"""
import os, math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import numpy as np

W, H = 1080, 1920
NAVY, MID = (5, 15, 35), (11, 36, 82)
GOLD, CREAM = (245, 176, 74), (251, 250, 246)
BLUE = (99, 203, 234)
DIM  = (126, 152, 184)
HERE = os.path.dirname(os.path.abspath(__file__))
FONT = os.path.join(HERE, "Heebo.ttf")
RIGHT = 940          # RTL text right edge
LEFT  = 140

_fc = {}
def F(size, weight):
    k = (size, weight)
    if k not in _fc:
        f = ImageFont.truetype(FONT, size); f.set_variation_by_axes([weight]); _fc[k] = f
    return _fc[k]

def is_num(s): return any(c.isdigit() for c in s)
def tw(d, s, f): return d.textlength(s, font=f, direction="ltr" if is_num(s) else "rtl") if s else 0

def rtl(d, s, size, weight, y, fill, right=RIGHT, a=255):
    f = F(size, weight)
    w = tw(d, s, f)
    d.text((right - w, y), s, font=f, fill=(*fill, int(a)),
           direction="ltr" if is_num(s) else "rtl")
    return w

def ground():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    k = np.clip(0.30 * (xx / W) + 0.70 * (1 - yy / H), 0, 1)[..., None]
    g = np.array(NAVY, np.float32) + (np.array(MID, np.float32) - np.array(NAVY, np.float32)) * k
    r = np.sqrt(((xx - W * 0.30) / (W * 1.05)) ** 2 + ((yy - H * 0.34) / (H * 0.62)) ** 2)
    g = g + (10.0 * np.clip(1 - r, 0, 1) ** 2)[..., None]
    return Image.fromarray(g.clip(0, 255).astype(np.uint8), "RGB").convert("RGBA")
BG = ground()

def header(d, topic="עדכון תקציב 2026, עיריית חריש"):
    """Where the interview was broadcast, and what it was about.

    The programme's own title is "יומן החדשות עם יוסי הדר", but the anchor's
    name is left out of it on purpose: it sat at the top of every frame while
    the speaker's name sat above the caption, so two names were on screen at
    once and neither one clearly belonged to the voice. The only name on the
    frame now is the person talking."""
    f = F(29, 700)
    x = RIGHT
    w = d.textlength("90FM", font=f, direction="ltr")
    d.text((x - w, 128), "90FM", font=f, fill=(*BLUE, 255), direction="ltr")
    d.rectangle([x - w, 178, x, 181], fill=(*GOLD, 235))
    x -= w
    for run in ["  ·  ", "יומן החדשות"]:
        ww = d.textlength(run, font=f, direction="rtl")
        d.text((x - ww, 128), run, font=f, fill=(*BLUE, 255), direction="rtl")
        x -= ww
    rtl(d, topic, 52, 800, 212, CREAM)

def speaker(d, name, role, y, accent=GOLD):
    d.rectangle([RIGHT + 2, y + 6, RIGHT + 7, y + 74], fill=(*accent, 240))
    x = rtl(d, name, 40, 800, y, CREAM, right=RIGHT - 22)
    rtl(d, role, 32, 400, y + 50, DIM, right=RIGHT - 22)

def wave(d, y, n=54, seed=3, amp=1.0, col=BLUE):
    random.seed(seed)
    gap, bw = 18, 6
    total = n * gap
    x0 = (W - total) // 2
    for i in range(n):
        env = math.sin(math.pi * i / (n - 1)) ** 0.6
        h = int((14 + 108 * env * abs(math.sin(i * 1.7 + seed)) ** 1.4) * amp)
        x = x0 + i * gap
        d.rounded_rectangle([x, y - h // 2, x + bw, y + h // 2], radius=3,
                            fill=(*col, 205))

def caption(d, lines, y, size=72, weight=800, lit=None, col=CREAM):
    """centred caption block; `lit` is (line, word) rendered in blue"""
    f = F(size, weight)
    for li, words in enumerate(lines):
        widths = [tw(d, w, f) for w in words]
        sp = d.textlength(" ", font=f)
        total = sum(widths) + sp * (len(words) - 1)
        x = (W + total) / 2                      # RTL: start at the right edge
        for wi, wd in enumerate(words):
            c = BLUE if lit == (li, wi) else col
            d.text((x - widths[wi], y + li * int(size * 1.34)), wd, font=f,
                   fill=(*c, 255), direction="ltr" if is_num(wd) else "rtl")
            x -= widths[wi] + sp

def circle_portrait(src, size=430, ring=GOLD):
    im = Image.open(src).convert("RGB")
    s = min(im.size)
    im = im.crop(((im.width - s) // 2, int(im.height * 0.18),
                  (im.width + s) // 2, int(im.height * 0.18) + s)).resize((size, size), Image.LANCZOS)
    m = Image.new("L", (size * 4, size * 4), 0)
    ImageDraw.Draw(m).ellipse([0, 0, size * 4, size * 4], fill=255)
    m = m.resize((size, size), Image.LANCZOS)
    out = Image.new("RGBA", (size + 20, size + 20), (0, 0, 0, 0))
    d = ImageDraw.Draw(out)
    d.ellipse([0, 0, size + 19, size + 19], outline=(*ring, 235), width=5)
    out.paste(im.convert("RGBA"), (10, 10), m)
    return out

def _credit(d):
    col = (108, 134, 158)
    f = F(27, 400)
    w = rtl(d, "מתוך הראיון המלא ב־", 27, 400, 288, col, right=RIGHT)
    x = RIGHT - w
    for run, rl in [("90FM", False), ("  ·  ", True), ("16.9.2026", False)]:
        ww = d.textlength(run, font=f, direction="rtl" if rl else "ltr")
        d.text((x - ww, 288), run, font=f, fill=(*col, 255),
               direction="rtl" if rl else "ltr")
        x -= ww

def footer(d):
    pass

# ----------------------------------------------------------------- frames

def f_open():
    """cold open: what was said, before who said it"""
    img = BG.copy(); d = ImageDraw.Draw(img)
    header(d)
    d.rectangle([RIGHT - 3, 470, RIGHT + 2, 470 + 330], fill=(*GOLD, 235))
    rtl(d, "״העירייה מרוקנת", 92, 800, 470, CREAM, right=RIGHT - 34)
    rtl(d, "עובדים מקצועיים", 92, 800, 590, CREAM, right=RIGHT - 34)
    rtl(d, "ומעבירה מיליונים", 92, 800, 710, CREAM, right=RIGHT - 34)
    rtl(d, "לקבלנים״", 92, 800, 830, GOLD, right=RIGHT - 34)
    wave(d, 1120, amp=0.85)
    speaker(d, "שני גרינברג", "יו״ר האופוזיציה בחריש", 1330)
    footer(d)
    return img

def f_question():
    """the interviewer's turn: gold, smaller, its own mark"""
    img = BG.copy(); d = ImageDraw.Draw(img)
    header(d)
    f = F(34, 800)
    s = "יוסי הדר שואל"
    w = tw(d, s, f)
    d.text((RIGHT - w, 690), s, font=f, fill=(*GOLD, 255), direction="rtl")
    d.rectangle([RIGHT - 78, 742, RIGHT, 745], fill=(*GOLD, 200))
    rtl(d, "״אבל בעירייה אומרים", 64, 500, 800, CREAM)
    rtl(d, "שהמידע נמסר כדין,", 64, 500, 886, CREAM)
    rtl(d, "ושהתקציב אושר.״", 64, 500, 972, CREAM)
    wave(d, 1240, n=40, seed=9, amp=0.5, col=GOLD)
    footer(d)
    return img

def f_answer():
    """her turn: the running caption, word by word"""
    img = BG.copy(); d = ImageDraw.Draw(img)
    header(d)
    p = circle_portrait("portrait_src.png", 390)
    img.paste(p, ((W - p.width) // 2, 420), p)
    wave(d, 900, n=46, seed=5, amp=0.55)
    speaker(d, "שני גרינברג", "יו״ר האופוזיציה בחריש", 1000)
    caption(d, [["בהנדסה", "מקצצים", "1.3", "מיליון"],
                ["שקלים", "מהשכר", "של", "העובדים"]], 1268,
            lit=(0, 2))
    wave(d, 1560, n=44, seed=11, amp=0.42)
    footer(d)
    return img

def f_panel():
    """a figure panel, same shape as the budget reel's"""
    img = BG.copy(); d = ImageDraw.Draw(img)
    header(d)
    rtl(d, "הנדסה, תכנון ובנייה", 40, 700, 470, BLUE)
    d.rectangle([RIGHT - 250, 524, RIGHT, 527], fill=(*BLUE, 170))
    for i, (num, unit, sign, sub) in enumerate([
            ("1.3", "מיליון ₪", -1, "פחות לשכר עובדי האגף"),
            ("970", "אלף ₪", +1, "יותר לייעוץ, פיקוח ועבודות קבלניות")]):
        y = 580 + i * 250
        fn = F(112, 800)
        wn = tw(d, num, fn)
        d.text((RIGHT - wn, y), num, font=fn, fill=(*BLUE, 255), direction="ltr")
        wu = rtl(d, unit, 44, 500, y + 52, CREAM, right=RIGHT - wn - 16)
        ax = RIGHT - wn - 16 - wu - 40
        d.polygon([(ax, y + 78), (ax + 26, y + 78), (ax + 13, y + 78 - 26 * sign)],
                  fill=(*CREAM, 230))
        rtl(d, sub, 36, 400, y + 132, DIM)
    caption(d, [["מול", "תוספת", "של", "כמעט"], ["מיליון", "ליועצים", "חיצוניים"]],
            1268, size=64, lit=(1, 0))
    wave(d, 1560, n=44, seed=11, amp=0.42)
    footer(d)
    return img

def f_hook():
    """the frame people screenshot"""
    img = BG.copy(); d = ImageDraw.Draw(img)
    header(d)
    wave(d, 560, n=50, seed=2, amp=0.5)
    d.rectangle([RIGHT - 3, 700, RIGHT + 2, 700 + 250], fill=(*GOLD, 235))
    rtl(d, "זו הדרך הבטוחה", 100, 800, 700, CREAM, right=RIGHT - 34)
    rtl(d, "לקריסת", 100, 800, 826, CREAM, right=RIGHT - 34)
    rtl(d, "השירותים.", 100, 800, 952, GOLD, right=RIGHT - 34)
    speaker(d, "שני גרינברג", "יו״ר האופוזיציה בחריש", 1330)
    footer(d)
    return img

if __name__ == "__main__":
    for name, fn in [("A_open", f_open), ("B_question", f_question),
                     ("C_answer", f_answer), ("D_panel", f_panel), ("E_hook", f_hook)]:
        fn().convert("RGB").save("%s.png" % name)
    tiles = [Image.open("%s.png" % n).resize((360, 640), Image.LANCZOS)
             for n in ["A_open", "B_question", "C_answer", "D_panel", "E_hook"]]
    labs = ["A  פתיח", "B  שאלה", "C  תשובה", "D  נתון", "E  הוק"]
    sheet = Image.new("RGB", (360 * 5 + 30 * 6, 640 + 100), (16, 18, 22))
    dd = ImageDraw.Draw(sheet)
    for i, (t, l) in enumerate(zip(tiles, labs)):
        x = 30 + i * 390
        sheet.paste(t, (x, 70))
        f = F(26, 600); w = tw(dd, l, f)
        dd.text((x, 30), l, font=f, fill=(235, 238, 242), direction="rtl")
    sheet.save("sheet.png")
    print("ok")
