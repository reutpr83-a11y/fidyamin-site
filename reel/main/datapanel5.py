# -*- coding: utf-8 -*-
"""The two budget comparisons, drawn over her while the picture recedes.

Both come straight off the budget document: slide 09 (הנדסה, תכנון ובנייה)
and slide 06 (ניקיון העיר). Each is the same shape, because the reel's whole
argument is that it is the same shape everywhere: less to the people who work
for the city, more to the people who invoice it.

Figures in the light blue v3-youth-fix.md sets for exactly this. The arrow and
the word carry the direction, so the colour never has to mean up or down."""
import os, json
from PIL import Image, ImageDraw
import caps

W, H = 1080, 1920
BLUE  = (99, 203, 234)           # #63cbea
INK   = (8, 22, 38)
RIGHT = 940
HERE  = os.path.dirname(os.path.abspath(__file__))
m = json.load(open(os.path.join(HERE, "map5.json")))
S = m["starts"]

# (label, [(figure, unit, direction, caption), ...], t_in, t_first, t_second, t_out, t_end)
# times are on the take's clock inside beat 2, converted below
B2 = S[2] - m["beats"][2][0]     # take clock -> reel clock inside the evidence beat
PANELS = [
    dict(label="הנדסה, תכנון ובנייה",
         rows=[("1.3", "מיליון ₪", -1, "פחות לשכר עובדי האגף"),
               ("970", "אלף ₪",     +1, "יותר לייעוץ, פיקוח ועבודות קבלניות")],
         t_in=B2 + 32.60, t_a=B2 + 32.95, t_b=B2 + 36.90,
         t_out=B2 + 40.10, t_end=B2 + 40.75),
    dict(label="ניקיון העיר",
         rows=[("421", "אלף ₪",  -1, "פחות לשכר עובדי העירייה באגף"),
               ("2.43", "מיליון ₪", +1, "יותר לקבלנים חיצוniים")],
         t_in=B2 + 41.35, t_a=B2 + 41.70, t_b=B2 + 44.60,
         t_out=B2 + 47.90, t_end=B2 + 48.55),
]
PANELS[1]["rows"][1] = ("2.43", "מיליון ₪", +1, "יותר לקבלנים חיצוניים")

def ease(x):
    x = max(0.0, min(1.0, x))
    return x * x * (3 - 2 * x)

def arrow(d, x, y, up, a):
    """A small solid triangle. Heebo has no arrow glyph and a drawn one keeps
    its weight next to the figure."""
    w, h = 26, 30
    pts = [(x, y - h/2), (x - w/2, y + h/2), (x + w/2, y + h/2)] if up else \
          [(x, y + h/2), (x - w/2, y - h/2), (x + w/2, y - h/2)]
    d.polygon(pts, fill=(*BLUE, int(230 * a)) if up else (255, 255, 255, int(190 * a)))

def block(d, y, fig, unit, up, cap, a, rise):
    f_fig = caps.F(112, 800); f_un = caps.F(46, 600); f_cap = caps.F(42, 500)
    col = (*BLUE, int(255 * a)) if up else (255, 255, 255, int(235 * a))
    x = RIGHT
    wf = caps.tw(d, fig, f_fig)
    d.text((x - wf, y + rise), fig, font=f_fig, fill=col, direction="ltr",
           stroke_width=6, stroke_fill=(*INK, int(210 * a)))
    wu = caps.tw(d, " " + unit, f_un)
    d.text((x - wf - wu, y + 52 + rise), " " + unit, font=f_un,
           fill=(255, 255, 255, int(215 * a)), direction="rtl",
           stroke_width=5, stroke_fill=(*INK, int(200 * a)))
    arrow(d, x - wf - wu - 34, y + 76 + rise, up, a)
    wc = caps.tw(d, cap, f_cap)
    d.text((RIGHT - wc, y + 132 + rise), cap, font=f_cap,
           fill=(255, 255, 255, int(205 * a)), direction="rtl",
           stroke_width=4, stroke_fill=(*INK, int(195 * a)))

def frame(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p = next((p for p in PANELS if p["t_in"] <= t <= p["t_end"]), None)
    if p is None:
        return img, 0.0
    fade = ease((t - p["t_in"]) / 0.42) if t < p["t_in"] + 0.42 else \
           (1.0 - ease((t - p["t_out"]) / (p["t_end"] - p["t_out"])) if t > p["t_out"] else 1.0)
    d = ImageDraw.Draw(img)
    f_lab = caps.F(46, 500)
    wl = caps.tw(d, p["label"], f_lab)
    d.text((RIGHT - wl, 250), p["label"], font=f_lab,
           fill=(255, 255, 255, int(195 * fade)), direction="rtl",
           stroke_width=4, stroke_fill=(*INK, int(180 * fade)))
    d.rectangle([RIGHT - 130, 330, RIGHT, 334], fill=(255, 255, 255, int(155 * fade)))
    for i, (t0, (fig, unit, dirn, cap)) in enumerate(zip((p["t_a"], p["t_b"]), p["rows"])):
        k = ease((t - t0) / 0.45)
        if k <= 0: continue
        block(d, 400 + i * 300, fig, unit, dirn > 0, cap, k * fade, int((1 - k) * 18))
    # hairline between the two halves, once the second is up
    k2 = ease((t - p["t_b"]) / 0.45)
    if k2 > 0:
        d.rectangle([RIGHT - 420, 664, RIGHT, 666],
                    fill=(255, 255, 255, int(70 * k2 * fade)))
    return img, fade

if __name__ == "__main__":
    FPS = 30
    out = os.path.join(HERE, "panel5"); os.makedirs(out, exist_ok=True)
    dims, n = {}, 0
    for p in PANELS:
        for i in range(int(p["t_in"] * FPS) - 2, int(p["t_end"] * FPS) + 3):
            img, fade = frame(i / FPS)
            img.save(os.path.join(out, "p%05d.png" % i))
            dims[i] = round(fade, 4); n += 1
    json.dump({"dim": dims}, open(os.path.join(HERE, "panel5.json"), "w"))
    print("panel frames %d   windows: %s" % (n, "  ".join(
        "%.2f-%.2f" % (p["t_in"], p["t_end"]) for p in PANELS)))
