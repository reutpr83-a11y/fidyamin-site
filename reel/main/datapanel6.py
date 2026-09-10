# -*- coding: utf-8 -*-
"""The three budget panels, drawn over her while the picture recedes.

All three come off the budget document, and all three are the same shape,
because the reel's argument is that the shape repeats:

  slide 09  הנדסה, תכנון ובנייה   1.3 מיליון פחות לשכר / 970 אלף יותר לייעוץ
  slide 06  ניקיון העיר            421 אלף פחות לשכר / 2.43 מיליון יותר לקבלנים
  slide 11  תקשורת ההנהלה          100 אלף נוספים, ללשכת ממלא מקום ראש העיר

The third one comes up under "ברור לכולם שגם לכם לא הסבירו כלום" and is still
there for "הסתירו מכם מידע שאנחנו מגלים לכם אותו", so the reveal is on screen
by the time she says she is making it. It is also what makes her last sentence
land, because the choice she puts to them, "לציבור או לממלא המקום", is now a
figure they have seen.

Every cue below is the time the word is spoken, taken from the transcript's
word times, because BRAND.md puts the number on her word. They used to run
0.6 to 1.4s ahead of her, which is worse than late: the graphic pre-empts the
speaker and then sits there waiting, and that is what made the examples feel
drawn out.

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
m = json.load(open(os.path.join(HERE, "map6.json")))
S, B = m["starts"], m["beats"]

def clk(i, t):
    """take clock -> reel clock, inside beat i"""
    return S[i] - B[i][0] + t

PANELS = [
    dict(label="הנדסה, תכנון ובנייה",
         rows=[("1.3", "מיליון ₪", -1, ("פחות לשכר עובדי האגף",)),
               ("970", "אלף ₪",    +1, ("יותר לייעוץ, פיקוח ועבודות קבלניות",))],
         note=None,
         t_in=clk(2, 32.30), t_a=clk(2, 33.54), t_b=clk(2, 38.16),
         t_out=clk(2, 40.20), t_end=clk(2, 40.85)),
    dict(label="ניקיון העיר",
         rows=[("421",  "אלף ₪",    -1, ("פחות לשכר עובדי העירייה באגף",)),
               ("2.43", "מיליון ₪", +1, ("יותר לקבלנים חיצוניים",))],
         note=None,
         t_in=clk(2, 41.05), t_a=clk(2, 43.08), t_b=clk(2, 45.82),
         t_out=clk(2, 47.95), t_end=clk(2, 48.60)),
    # Slide 08. It lands on "האחריות, הפיקוח והיכולת לוודא שהעיר מתפקדת חייבים
    # להישאר בתוך העירייה" — she names oversight, and the document shows the
    # oversight salaries being cut while the bought in guarding goes up. It is
    # also the fourth time the same shape appears, which is the argument.
    dict(label="תקציב הביטחון",
         rows=[("650", "אלף ₪",  +1, ("יותר לשמירה",)),
               ("206", "אלף ₪",  -1, ("פחות לשכר בשיטור ובפיקוח העירוני",))],
         note=None,
         t_in=clk(3, 85.20), t_a=clk(3, 85.60), t_b=clk(3, 87.30),
         t_out=clk(3, 91.60), t_end=clk(3, 92.30)),
    dict(label="תקציב התקשורת של ההנהלה",
         rows=[("100", "אלף ₪ נוספים", +1, ("לתקשורת הנהלת העירייה",
                                            "ולשכת ממלא מקום ראש העיר"))],
         note="מ-900 אלף ₪ למיליון ₪",
         t_in=clk(5, 113.70), t_a=clk(5, 114.10), t_b=None,
         t_out=clk(5, 119.30), t_end=clk(5, 119.95)),
]

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

def block(d, y, fig, unit, up, caps_, a, rise):
    f_fig = caps.F(112, 800); f_un = caps.F(46, 600); f_cap = caps.F(42, 500)
    col = (255, 255, 255, int(235 * a)) if up is False else (*BLUE, int(255 * a))
    x = RIGHT
    wf = caps.tw(d, fig, f_fig)
    d.text((x - wf, y + rise), fig, font=f_fig, fill=col, direction="ltr",
           stroke_width=6, stroke_fill=(*INK, int(210 * a)))
    wu = caps.tw(d, " " + unit, f_un)
    d.text((x - wf - wu, y + 52 + rise), " " + unit, font=f_un,
           fill=(255, 255, 255, int(215 * a)), direction="rtl",
           stroke_width=5, stroke_fill=(*INK, int(200 * a)))
    if up is not None:
        arrow(d, x - wf - wu - 34, y + 76 + rise, up, a)
    for j, line in enumerate(caps_):
        wc = caps.tw(d, line, f_cap)
        d.text((RIGHT - wc, y + 132 + j * 54 + rise), line, font=f_cap,
               fill=(255, 255, 255, int(205 * a)), direction="rtl",
               stroke_width=4, stroke_fill=(*INK, int(195 * a)))

def frame(t):
    img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    p = next((p for p in PANELS if p["t_in"] <= t <= p["t_end"]), None)
    if p is None:
        return img, 0.0
    fade = (1.0 if p.get("instant") else ease((t - p["t_in"]) / 0.42)) \
           if t < p["t_in"] + 0.42 else \
           (1.0 - ease((t - p["t_out"]) / (p["t_end"] - p["t_out"])) if t > p["t_out"] else 1.0)
    d = ImageDraw.Draw(img)
    f_lab = caps.F(46, 500)
    wl = caps.tw(d, p["label"], f_lab)
    d.text((RIGHT - wl, 250), p["label"], font=f_lab,
           fill=(255, 255, 255, int(195 * fade)), direction="rtl",
           stroke_width=4, stroke_fill=(*INK, int(180 * fade)))
    d.rectangle([RIGHT - 130, 330, RIGHT, 334], fill=(255, 255, 255, int(155 * fade)))

    cues = [p["t_a"]] + ([p["t_b"]] if p["t_b"] is not None else [])
    for i, (t0, (fig, unit, dirn, cs)) in enumerate(zip(cues, p["rows"])):
        k = ease((t - t0) / 0.45)
        if k <= 0: continue
        block(d, 400 + i * 300, fig, unit, None if dirn == 0 else dirn > 0,
              cs, k * fade, int((1 - k) * 18))
    if p["note"]:
        k = ease((t - p["t_a"] - 0.55) / 0.45)
        if k > 0:
            f = caps.F(46, 600)
            wn = caps.tw(d, p["note"], f)
            d.text((RIGHT - wn, 660), p["note"], font=f,
                   fill=(255, 255, 255, int(215 * k * fade)), direction="rtl",
                   stroke_width=5, stroke_fill=(*INK, int(200 * k * fade)))
    if p["t_b"] is not None:
        k2 = ease((t - p["t_b"]) / 0.45)
        if k2 > 0:
            d.rectangle([RIGHT - 420, 664, RIGHT, 666],
                        fill=(255, 255, 255, int(70 * k2 * fade)))
    return img, fade

if __name__ == "__main__":
    FPS = 30
    out = os.path.join(HERE, "panel6"); os.makedirs(out, exist_ok=True)
    dims, n = {}, 0
    for p in PANELS:
        for i in range(int(p["t_in"] * FPS) - 2, int(p["t_end"] * FPS) + 3):
            img, fade = frame(i / FPS)
            img.save(os.path.join(out, "p%05d.png" % i))
            dims[i] = round(fade, 4); n += 1
    json.dump({"dim": dims}, open(os.path.join(HERE, "panel6.json"), "w"))
    print("panel frames %d   windows: %s" % (n, "   ".join(
        "%.2f-%.2f" % (p["t_in"], p["t_end"]) for p in PANELS)))
