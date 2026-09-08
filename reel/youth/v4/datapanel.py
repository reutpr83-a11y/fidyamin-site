# -*- coding: utf-8 -*-
"""The youth slide, rebuilt for the vertical frame.

The client asked for the slide's figures in the background rather than on a
card that replaces her, so she stays on screen and recedes: the picture dims
and softens while the six budget lines build over it, then it comes back.
Figures are in the light blue v3-youth-fix.md specifies for exactly this,
which reads clean over her rather than orange the way the brand gold would."""
import os, json
from PIL import Image, ImageDraw, ImageFilter
import caps

W, H = 1080, 1920
BLUE  = (99, 203, 234, 255)      # #63cbea
WHITE = (255, 255, 255, 255)
DIM   = (255, 255, 255, 165)
HERE  = os.path.dirname(os.path.abspath(__file__))

LABEL = "קיצוץ במערכי הנוער"
HEAD  = ("653", "אלף ₪ פחות")
ROWS = [("365", "בשכר מחלקת הנוער"),
        ("150", "בקידום נוער"),
        ("60",  "במרכז הנוער היישובי"),
        ("52",  "במד״צים"),
        ("16",  "בניקיון מבנה הנוער"),
        ("10",  "במנהיגות ילדים ונוער")]

# on the reel's timeline
T_IN, T_HEAD, T_ROWS, T_OUT, T_END = 16.60, 16.90, 18.90, 23.60, 24.35
ROW_STEP = 0.55

def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def draw_row(d, y, fig, txt, a, rise):
    f_fig = caps.F(64, 700); f_txt = caps.F(40, 500)
    col_fig = (BLUE[0], BLUE[1], BLUE[2], int(255 * a))
    col_txt = (255, 255, 255, int(210 * a))
    x = 940
    for s, f, c in ((fig, f_fig, col_fig), (" אלף ₪", caps.F(40, 500), col_txt)):
        w = caps.tw(d, s, f)
        d.text((x - w, y + rise), s, font=f, fill=c,
               direction="ltr" if caps.is_num(s) else "rtl",
               stroke_width=4, stroke_fill=(8, 22, 38, int(200 * a)))
        x -= w
    w = caps.tw(d, txt, f_txt)
    d.text((940 - w, y + 66 + rise), txt, font=f_txt, fill=col_txt, direction="rtl",
           stroke_width=4, stroke_fill=(8, 22, 38, int(190 * a)))

def frame(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    if not (T_IN <= t <= T_END):
        return img, 0.0
    fade = ease((t - T_IN) / 0.45) if t < T_IN + 0.45 else \
           (1.0 - ease((t - T_OUT) / (T_END - T_OUT)) if t > T_OUT else 1.0)
    d = ImageDraw.Draw(img)
    f_lab = caps.F(46, 500)
    w = caps.tw(d, LABEL, f_lab)
    d.text((940 - w, 250), LABEL, font=f_lab,
           fill=(255, 255, 255, int(190 * fade)), direction="rtl",
           stroke_width=4, stroke_fill=(8, 22, 38, int(180 * fade)))
    d.rectangle([940, 330, 946, 336], fill=(255, 255, 255, int(150 * fade)))

    hk = ease((t - T_HEAD) / 0.5)
    if hk > 0:
        f_big = caps.F(210, 800); f_un = caps.F(58, 700)
        big = HEAD[0]; wb = caps.tw(d, big, f_big)
        d.text((940 - wb, 380 + int((1 - hk) * 22)), big, font=f_big,
               fill=(BLUE[0], BLUE[1], BLUE[2], int(255 * hk * fade)), direction="ltr",
               stroke_width=6, stroke_fill=(8, 22, 38, int(210 * hk * fade)))
        wu = caps.tw(d, HEAD[1], f_un)
        d.text((940 - wu, 640 + int((1 - hk) * 22)), HEAD[1], font=f_un,
               fill=(255, 255, 255, int(230 * hk * fade)), direction="rtl",
               stroke_width=5, stroke_fill=(8, 22, 38, int(200 * hk * fade)))

    for i, (fig, txt) in enumerate(ROWS):
        k = ease((t - (T_ROWS + i * ROW_STEP)) / 0.45)
        if k <= 0: continue
        draw_row(d, 768 + i * 106, fig, txt, k * fade, int((1 - k) * 16))
    return img, fade

if __name__ == "__main__":
    FPS = 30
    out = os.path.join(HERE, "panel"); os.makedirs(out, exist_ok=True)
    dims = {}
    n = 0
    for i in range(int(T_IN * FPS) - 2, int(T_END * FPS) + 3):
        t = i / FPS
        img, fade = frame(t)
        img.save(os.path.join(out, "p%05d.png" % i))
        dims[i] = round(fade, 4); n += 1
    json.dump({"first": int(T_IN*FPS)-2, "last": int(T_END*FPS)+2, "dim": dims},
              open(os.path.join(HERE, "panel.json"), "w"))
    print("panel frames: %d  (%.2f - %.2f s)" % (n, T_IN, T_END))
