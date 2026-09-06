# -*- coding: utf-8 -*-
"""Subtitle cues as transparent PNGs, rendered through the same RTL engine as
the cards (Pillow + libraqm). libass reverses Hebrew word order here, so we
never hand it text."""
import os, json, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_cards import F, BOLD, BLUE, WHITE, draw_line_rtl, wrap, line_w, tokenize
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT  = os.path.join(HERE, "subs"); os.makedirs(OUT, exist_ok=True)
W, SUB_H, SIZE = 1080, 150, 66

def render(segs, path):
    img = Image.new("RGBA", (W, SUB_H), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    f = F(BOLD, SIZE)
    # shrink to fit one line
    size = SIZE
    while line_w(d, tokenize(segs), F(BOLD, size), ) > W - 110 and size > 40:
        size -= 2
        f = F(BOLD, size)
    y = (SUB_H - int(size * 1.2)) // 2
    # soft dark shadow for legibility, then the text
    sh = Image.new("RGBA", (W, SUB_H), (0, 0, 0, 0))
    ds = ImageDraw.Draw(sh)
    for l in wrap(ds, segs, f, W - 110)[:1]:
        draw_line_rtl(ds, l, f, W / 2, y, default=(0, 0, 0, 230))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(7)))
    img.alpha_composite(sh.filter(ImageFilter.GaussianBlur(3)))
    for l in wrap(d, segs, f, W - 110)[:1]:
        draw_line_rtl(d, l, f, W / 2, y, default=WHITE)
    img.save(path)

B = BLUE
CUES = {
 "shotA": [
   (0.00, 2.15, [("לא יהיה ", None), ("פטור", B), (", לא לאברך אחד", None)]),
   (2.15, 4.35, [("ולא לרבע אברך — ", None), ("מאה אחוז גיוס", B)]),
   (4.95, 6.15, [("שום ", None), ("פשרה", B)]),
 ],
 "shotB": [
   (0.00,  2.80, [("כל צעיר בן שמונה עשרה ", None), ("מתייצב", B), (" בבקו״ם", None)]),
   (3.19,  6.51, [("וכל צעיר — זה יהודי, נוצרי", None)]),
   (6.75,  7.86, [("צ׳רקסי", None)]),
   (8.27,  9.91, [("שני מסלולים", B), (": או מסלול צבאי", None)]),
   (10.17,11.86, [("והשאר למסלול", None)]),
   (11.86,13.66, [("אזרחי. לא יהיה ", None), ("פטור", B), (" לאחד", None)]),
   (13.66,14.91, [("גם לא יהיה משא ומתן על זה", None)]),
 ],
}

index = {}
for shot, cues in CUES.items():
    index[shot] = []
    for i, (a, b, segs) in enumerate(cues):
        p = os.path.join(OUT, "%s_%02d.png" % (shot, i))
        render(segs, p)
        index[shot].append({"start": a, "end": b, "png": p})
json.dump(index, open(os.path.join(OUT, "index.json"), "w"), ensure_ascii=False, indent=1)
print("rendered", sum(len(v) for v in index.values()), "cues")
