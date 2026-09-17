# -*- coding: utf-8 -*-
"""Render the reel, one PNG per frame.

Nothing here dissolves: the ground never changes, so a full frame dissolve
would be invisible. Every element animates on its own — a caption rises and
fades, a figure counts in, the panel slides. That is also why the cut can be
fast without looking cut.
"""
import json, os, sys, math, subprocess
import numpy as np
from PIL import Image, ImageDraw
import design as D

W, H, FPS = 1080, 1920, 30
NAVY, GOLD, CREAM, BLUE, DIM = D.NAVY, D.GOLD, D.CREAM, D.BLUE, D.DIM
RIGHT = D.RIGHT
TAIL = 5.0                         # end card

m     = json.load(open("map.json"))
caps  = json.load(open("track.json"))
VOICE = m["dur"]
TOTAL = VOICE + TAIL

def ease(x):
    x = max(0.0, min(1.0, x)); return x * x * (3 - 2 * x)

# ---------------------------------------------------------------- waveform
def envelope():
    raw = subprocess.run(["ffmpeg","-v","error","-i","voice.wav","-map","0:a","-ac","1",
                          "-ar","48000","-f","f32le","-"],capture_output=True).stdout
    x = np.frombuffer(raw, np.float32)
    h = 48000 // FPS
    n = len(x) // h
    e = np.sqrt((x[:n*h].reshape(n, h) ** 2).mean(axis=1))
    e = e / (np.percentile(e, 97) + 1e-9)
    return np.clip(e, 0, 1.4)
ENV = envelope()

def wave(d, y, t, col=BLUE, amp=1.0, bars=46, gap=19, bw=6, a=1.0):
    """The voice itself, drawn. It is the only moving thing on a frame that has
    no footage, so when the stage is empty it becomes the picture."""
    if a <= 0.01: return
    f = int(t * FPS)
    x0 = (W - bars * gap) // 2
    for i in range(bars):
        k = f - (bars // 2 - abs(i - bars // 2)) * 2          # a little lag outward
        v = ENV[max(0, min(len(ENV) - 1, k))]
        shape = math.sin(math.pi * i / (bars - 1)) ** 0.7
        hgt = int((7 + 96 * v * shape * (0.55 + 0.45 * abs(math.sin(i * 2.3)))) * amp)
        d.rounded_rectangle([x0 + i*gap, y - hgt//2, x0 + i*gap + bw, y + hgt//2],
                            radius=3, fill=(*col, int(200 * a)))

# ---------------------------------------------------------------- panels
PANELS = [
  dict(label="ניקיון ותברואה",
       rows=[("420","אלף ₪",-1,"פחות לשכר העובדים"),
             ("2.4","מיליון ₪",+1,"יותר לתשלום לקבלנים")],
       seg="clean", src_a=128.84, src_b=132.07, src_in=128.60, src_out=136.40),
  dict(label="הנדסה, תכנון ובנייה",
       rows=[("3","מיליון ₪",0,"התקציב המקורי לשכר העובדים באגף"),
             ("1.3","מיליון ₪",-1,"קוצצו מהשכר של העובדים")],
       seg="eng_a", src_a=158.38, seg_b="eng_b", src_b=161.39,
       src_in=157.90, src_out=165.20),
]
def base_of(sid):
    s = [x for x in m["segs"] if x["id"] == sid][0]
    return s["start"] - s["in"]
for p in PANELS:
    b  = base_of(p["seg"])
    b2 = base_of(p.get("seg_b", p["seg"]))
    p["t_in"], p["t_a"] = b + p["src_in"], b + p["src_a"]
    p["t_b"] = b2 + p["src_b"]
    p["t_out"] = b2 + p["src_out"] if "seg_b" in p else b + p["src_out"]

def panel(img, d, p, t):
    a = ease((t - p["t_in"]) / 0.45) * (1 - ease((t - p["t_out"]) / 0.40))
    if a <= 0.01: return
    rise = int((1 - ease((t - p["t_in"]) / 0.45)) * 18)
    y0 = 470 + rise
    D.rtl(d, p["label"], 40, 700, y0, BLUE, a=255 * a)
    d.rectangle([RIGHT - 250, y0 + 54, RIGHT, y0 + 57], fill=(*BLUE, int(170 * a)))
    for i, (num, unit, sign, sub) in enumerate(p["rows"]):
        ta = p["t_a"] if i == 0 else p["t_b"]
        ra = ease((t - ta) / 0.32)
        if ra <= 0: continue
        y = y0 + 110 + i * 250
        fn = D.F(112, 800)
        wn = D.tw(d, num, fn)
        k = 1 + 0.10 * (1 - ra)
        d.text((RIGHT - wn, y + int((1 - ra) * 10)), num, font=fn,
               fill=(*BLUE, int(255 * ra * a)), direction="ltr")
        wu = D.rtl(d, unit, 44, 500, y + 52, CREAM, right=RIGHT - wn - 16, a=255*ra*a)
        if sign:
            ax = RIGHT - wn - 16 - wu - 40
            d.polygon([(ax, y + 78), (ax + 26, y + 78), (ax + 13, y + 78 - 26 * sign)],
                      fill=(*CREAM, int(230 * ra * a)))
        D.rtl(d, sub, 34, 400, y + 132, DIM, a=255 * ra * a)

def panel_at(t):
    for p in PANELS:
        if p["t_in"] - 0.5 <= t <= p["t_out"] + 0.5: return p
    return None

# ---------------------------------------------------------------- captions
SPK = {1: ("יוסי הדר", "מגיש יומן החדשות", GOLD),
       2: ("שני גרינברג", "יו״ר האופוזיציה בחריש", BLUE)}

def chip(d, spk, t, a=1.0):
    name, role, col = SPK[spk]
    y = 1150
    d.rectangle([RIGHT + 2, y + 6, RIGHT + 7, y + 74], fill=(*col, int(240 * a)))
    D.rtl(d, name, 40, 800, y, CREAM, right=RIGHT - 22, a=255 * a)
    D.rtl(d, role, 30, 400, y + 50, DIM, right=RIGHT - 22, a=255 * a)

def lines_of(words, f, d, maxw):
    sp = d.textlength(" ", font=f)
    out, cur, w = [], [], 0.0
    for i, word in enumerate(words):
        ww = D.tw(d, word, f)
        if cur and w + sp + ww > maxw:
            out.append(cur); cur, w = [(i, word, ww)], ww
        else:
            cur.append((i, word, ww)); w += (sp if len(cur) > 1 else 0) + ww
    if cur: out.append(cur)
    return out, sp

def draw_words(d, c, t, size, weight, ytop, col, lit=BLUE, centre=True, a=1.0,
               maxw=860, right=RIGHT):
    f = D.F(size, weight)
    rows, sp = lines_of(c["words"], f, d, maxw)
    lh = int(size * 1.34)
    for li, row in enumerate(rows):
        total = sum(r[2] for r in row) + sp * (len(row) - 1)
        x = (W + total) / 2 if centre else right
        for idx, word, ww in row:
            on = c["times"][idx] <= t
            wa = ease((t - c["times"][idx]) / 0.14) if on else 0.0
            live = on and t < c["ends"][idx]
            cc = lit if live else col
            aa = a * (0.30 + 0.70 * wa)
            d.text((x - ww, ytop + li * lh), word, font=f,
                   fill=(*cc, int(255 * min(1.0, aa))),
                   direction="ltr" if D.is_num(word) else "rtl")
            x -= ww + sp
    return len(rows)

def caption(img, d, c, t):
    a = ease((t - c["start"]) / 0.22) * (1 - ease((t - c["end"]) / 0.28))
    if a <= 0.01: return
    rise = int((1 - ease((t - c["start"]) / 0.30)) * 16)
    st = c["style"]
    if st == "card":
        f = D.F(34, 800); s = "יוסי הדר שואל"
        d.text((RIGHT - D.tw(d, s, f), 690 + rise), s, font=f,
               fill=(*GOLD, int(255 * a)), direction="rtl")
        d.rectangle([RIGHT - 78, 742 + rise, RIGHT, 745 + rise], fill=(*GOLD, int(200 * a)))
        draw_words(d, c, t, 58, 500, 800 + rise, CREAM, lit=CREAM, centre=False, a=a,
                   maxw=800, right=RIGHT)
    elif st == "hook":
        f = D.F(84, 800)
        rows, _ = lines_of(c["words"], f, d, 760)
        d.rectangle([RIGHT - 3, 700 + rise, RIGHT + 2,
                     700 + rise + int(84 * 1.34) * len(rows) - 14],
                    fill=(*GOLD, int(230 * a)))
        draw_words(d, c, t, 84, 800, 700 + rise, CREAM, lit=GOLD, centre=False, a=a,
                   maxw=760, right=RIGHT - 34)
    elif st == "fig":
        fn = D.F(150, 800)
        num = c["words"][0]
        wn = D.tw(d, num, fn)
        d.text((RIGHT - wn, 640 + rise), num, font=fn, fill=(*BLUE, int(255*a)), direction="ltr")
        D.rtl(d, " ".join(c["words"][1:]), 56, 500, 700 + rise, CREAM,
              right=RIGHT - wn - 20, a=255 * a)
    else:
        draw_words(d, c, t, 62, 800, 1268 + rise, CREAM, a=a, maxw=860)

def stage_busy(t):
    """0 when nothing occupies the middle of the frame, 1 when something does,
    with a short ramp so the waveform can trade places with it."""
    k = 0.0
    for p in PANELS:
        k = max(k, ease((t - (p["t_in"] - 0.30)) / 0.35)
                   * (1 - ease((t - (p["t_out"] + 0.40)) / 0.35)))
    for c in caps:
        if c["style"] in ("card", "hook", "fig"):
            k = max(k, ease((t - (c["start"] - 0.20)) / 0.30)
                       * (1 - ease((t - (c["end"] + 0.28)) / 0.30)))
    return k

def cap_at(t):
    return [c for c in caps if c["start"] - 0.25 <= t <= c["end"] + 0.30]

def speaker_at(t):
    cur = [c for c in caps if c["start"] <= t <= c["end"]]
    if cur: return cur[0]["speaker"]
    nxt = [c for c in caps if c["start"] > t]
    return nxt[0]["speaker"] if nxt else 2

# ---------------------------------------------------------------- end card
END = [("מיליונים עוברים החוצה,", 72, 800, CREAM, 0.15),
       ("ומי שאמור לפקח",         72, 800, CREAM, 0.55),
       ("כבר לא שם.",             72, 800, CREAM, 0.95),
       ("תשאלו את חברי המועצה.",  58, 800, GOLD,  1.70)]

def endcard(t):
    img = D.BG.copy(); d = ImageDraw.Draw(img)
    a = ease(t / 0.5)
    D.header(d)
    d.rectangle([RIGHT + 4, 640, RIGHT + 9, 640 + int(400 * ease(t / 0.8))],
                fill=(*GOLD, int(230 * a)))
    y = 640
    for s, size, wt, col, t0 in END:
        k = ease((t - t0) / 0.45)
        if k <= 0:
            y += size + 42; continue
        D.rtl(d, s, size, wt, y + int((1 - k) * 14), col, right=RIGHT - 30, a=255 * k)
        y += size + 42
    D.rtl(d, "מתוך הראיון ביומן החדשות", 32, 400, 1180, (150, 176, 198),
          a=255 * ease((t - 2.3) / 0.5))
    return img

# ---------------------------------------------------------------- frame
def frame(i):
    t = i / FPS
    if t >= VOICE:
        return endcard(t - VOICE)
    img = D.BG.copy(); d = ImageDraw.Draw(img)
    D.header(d)
    p = panel_at(t)
    if p: panel(img, d, p, t)
    for c in cap_at(t):
        caption(img, d, c, t)
    chip(d, speaker_at(t), t)
    live = [c for c in caps if c["start"] <= t <= c["end"]]
    col = GOLD if (live and live[0]["speaker"] == 1) else BLUE
    k = stage_busy(t)
    wave(d, 1600, t, col=col, amp=0.85, a=k)                       # the quiet strip
    wave(d, 760, t, col=col, amp=2.6, bars=62, gap=15, bw=5, a=1 - k)   # the stage
    return img

if __name__ == "__main__":
    a = int(sys.argv[1]); b = int(sys.argv[2]); out = sys.argv[3]
    os.makedirs(out, exist_ok=True)
    for i in range(a, b):
        frame(i).convert("RGB").save(os.path.join(out, "f%05d.png" % i))
    print("frames %d-%d done" % (a, b))
