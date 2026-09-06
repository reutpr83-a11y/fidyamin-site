# -*- coding: utf-8 -*-
import sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from render_cards import statement_card, comparison_card, BLUE, WHITE

B = BLUE
# ---- 6-11s
statement_card("card_01_2018", [
    [("2018", B), (". אותו אדם. שר הביטחון.", None)],
    [("המתווה שלו: אפס סנקציות אישיות.", None)],
], size=88)

# ---- 11-18s
statement_card("card_02_setup", [
    [("נשווה שני מתווים —", None)],
    [("זה שליברמן ניסח ב-", None), ("2018", B), (",", None)],
    [("וזה שהוא תוקף היום.", None)],
], size=84)

# ---- 30-38s  comparison 1
comparison_card("card_03_cmp_personal",
    topline=[("היום אומר: ", None), ("“רישום פלילי ושלילת קצבאות”", None)],
    r_head=[("המתווה שלו, ", None), ("2018", B)],
    r_body=[[("אפס", B)], [("חסינות אישית מלאה לבחור הישיבה", None)]],
    l_head=[("המתווה שהוא תוקף, ", None), ("2026", B)],
    l_body=[[("סנקציות אישיות", None)], [("בנוסח ביסמוט — עד גיל ", None), ("26", B)]])

# ---- 46-54s comparison 3 (timeline)
comparison_card("card_05_cmp_timeline",
    topline=[("מה קרה למתווה שלו", None)],
    r_head=[("נובמבר ", None), ("2019", B)],
    r_body=[[("תנאי סף:", None)], [("להעביר את המתווה שלו “ככתבו וכלשונו”", None)]],
    l_head=[("אחר כך", None)],
    l_body=[[("זנח אותו", None)], [("ופתח ב“", None), ("100%", B), (" גיוס”", None)]])

# ---- 66-76s
statement_card("card_06_year_after", [
    [("שנה אחרי שהתפטר", None)],
    [("הוא עוד נלחם על אותו מתווה.", None)],
    [("רק כשזה נכשל — הוא החליף עמדה.", None)],
], size=82)

# ---- 76-86s bottom line
statement_card("card_07_bottomline", [
    [("המתווה שהוא תוקף היום", None)],
    [("כולל בדיוק את מה", None)],
    [("שהמתווה שלו השמיט.", None)],
], size=92)
print("cards rendered")

# ---- 86-92s  sources
from render_cards import (new_card, save, F, BOLD, REG, block, DIM, W, H)
from PIL import ImageDraw
img = new_card(); d = ImageDraw.Draw(img)
y = block(d, [("מקורות", None)], F(BOLD, 76), W/2, 560, W-150, 92)
y += 60
rows = [
    [("סנקציות אישיות עד גיל ", None), ("26", B), (" — נוסח ביסמוט", None)],
    [("הארץ, ", None), ("27.11.2025", B)],
    [("המלצות ועדת ליברמן, משרד הביטחון", None)],
    [("יוני ", None), ("2018", B)],
    [("“ככתבו וכלשונו” — תנאי סף קואליציוני", None)],
    [("מעריב, נובמבר ", None), ("2019", B)],
]
f_a, f_b = F(BOLD, 50), F(REG, 44)
for i, r in enumerate(rows):
    if i % 2 == 0:
        y = block(d, r, f_a, W/2, y, W-160, 60)
    else:
        y = block(d, r, f_b, W/2, y, W-160, 54, default=DIM) + 46
save(img, "card_08_sources")
print("sources card done")
