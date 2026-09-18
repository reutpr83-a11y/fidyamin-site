# -*- coding: utf-8 -*-
"""The cut: 18 contiguous stretches of the broadcast, in order.

Word times come from the transcription; the words themselves are corrected by
hand against what is audibly said, because Hebrew ASR mangles figures
("1000000" for מיליון) and a handful of words. Where a word came back garbled
and could not be verified, the cut starts after it rather than guessing — that
is why the tberua'a block opens on "420" and the engineering block is in two
pieces.

Only word START times are used. The transcriber stretches some end times past
the next word's start, so ends are derived, never trusted.

The order is argued, not chronological. The two blocks that were 13th and
14th in the broadcast — "איך את מסבירה את זה?" and her answer — are last here,
because the collapse line is the verdict of the whole reel and the reel was
ending on a technical rebuttal instead.

speaker: 1 = Yossi Hadar, the anchor  ·  2 = Shani Greenberg
         3 = Itamar Rotem, the station's reporter, who files the opening
             item. The anchor thanks him by name at 66.1s ("תודה איתמר")
             before greeting her, which is how the two were told apart.
"""

SRC = "audio48.wav"
XF  = 0.07          # audio: a short equal-power splice. The broadcast is
                    # compressed and has no real pauses to hide a long
                    # dissolve in, so the picture dissolves at 0.25s while the
                    # sound simply cuts.

# (id, in, out, [(speaker, [(t, word), ...]), ...])
SEGS = [
 # The item begins with why the Interior Ministry wrote at all: she went to the
 # district supervisor with a lawyer. Cutting in at "בבוקר יום ההצבעה" left the
 # letter arriving out of nowhere.
 ("setup",    1.46,  19.35, [(3, [
    (1.52,"אז"),(1.84,"לאחר"),(2.56,"פניות"),(3.04,"של"),(3.52,"יושב"),(3.76,"ראש"),
    (4.00,"האופוזיציה"),(4.64,"עם"),(4.96,"עורך"),(5.20,"דין"),
    (6.16,"לממונה"),(6.88,"המחוז"),(7.44,"במשרד"),(7.92,"הפנים,"),
    (8.48,"בבוקר"),(8.80,"יום"),(9.04,"ההצבעה"),(9.44,"על"),(9.76,"התקציב,"),
    (10.72,"שלחה"),(11.12,"נציגת"),(11.76,"משרד"),(12.16,"הפנים"),(12.48,"מכתב"),
    (12.88,"למנכ״ל"),(13.36,"העירייה."),
    (14.27,"היא"),(14.51,"כתבה"),(14.83,"שככל"),(15.31,"הנראה"),(15.63,"נפל"),
    (16.03,"פגם"),(16.83,"בהעברת"),(17.55,"המסמכים"),(17.95,"לחברי"),(18.51,"המועצה")])]),

 ("vote",    26.37,  32.05, [(3, [
    (26.43,"ואם"),(26.83,"צריך,"),(27.07,"להוריד"),(27.39,"את"),(27.55,"הנושא"),
    (27.79,"מסדר"),(28.19,"היום."),
    (29.00,"לא"),(29.24,"הורידו."),(30.36,"והצביעו"),(31.00,"באותו"),(31.24,"ערב.")])]),

 # The anchor puts the counter-case to her; she is not conceding it.
 ("concede", 70.64,  77.90, [(1, [
    (70.70,"יכול"),(71.10,"להיות"),(71.26,"שיש"),(71.66,"דברים"),(72.22,"שעובדי"),
    (72.86,"העירייה"),(73.34,"לא"),(73.82,"יכולים"),(74.22,"לעשות"),(74.46,"וצריכים"),
    (75.18,"לפעמים"),(76.14,"יועצים"),(76.70,"חיצוניים.")])]),

 # Her answer. Its middle — "בתקופה שאני הייתי רוב הזמן הזה [?] ראש עיר, תמיד
 # העלינו יועצים חיצוניים" — came back too uncertain to caption, so the cut
 # keeps the two ends that are clean.
 ("sure",    78.24,  79.95, [(2, [
    (78.30,"ברור."),(79.18,"מה"),(79.42,"זאת"),(79.58,"אומרת?")])]),

 ("q1",     106.96, 108.90, [(1, [
    (107.02,"למה"),(107.26,"הקרסת"),(107.74,"שירותי"),(108.06,"העירייה?")])]),

 # One unbroken stretch: she answers him, says where she is answering from,
 # gives the principle, and applies it to sanitation. "אני אסביר" and "אני באה
 # מהעולם הזה" were cut before and the credentials line arrived with nothing
 # behind it; "אם אתה מקצץ בתברואה" was cut too, and the figures arrived with
 # no verb.
 ("argument", 109.52, 120.30, [(2, [
    (109.58,"אני"),(109.74,"אסביר."),
    (110.14,"אני"),(110.22,"באה"),(110.46,"מהעולם"),(110.78,"הזה,"),(111.10,"בסדר?"),
    (111.42,"בסוף"),(112.14,"זו"),(112.38,"ההתמחות"),(112.78,"שלי,"),
    (113.18,"זה"),(113.34,"הניסיון"),(113.90,"שלי."),
    (114.46,"בניהול"),(115.02,"מערכות"),(115.42,"ציבוריות,"),
    (116.28,"כשאתה"),(117.08,"מוציא"),(117.80,"יותר"),(118.20,"כסף"),
    (118.44,"לקבלנים"),(119.08,"חיצוניים,")])]),

 # "עדיין" is cut out of the middle of the sentence, 120.30 to 120.72, so the
 # line lands as "אתה צריך מערכת שיודעת לפקח מבפנים" rather than "you still
 # need". Everything either side of it is untouched.
 ("argument2", 120.72, 139.05, [(2, [
    (120.76,"אתה"),(121.16,"צריך"),(121.48,"מערכת"),(122.04,"שיודעת"),
    (122.52,"לפקח"),(123.40,"מבפנים."),
    (124.52,"אתה"),(124.76,"חייב"),(125.16,"את"),(125.40,"זה."),
    (125.72,"אם"),(127.08,"אתה"),(127.40,"מקצץ"),(128.04,"בתברואה"),
    (128.84,"420"),(129.72,"אלף"),(129.96,"שקל"),(130.36,"מהמשכורות"),
    (131.35,"ואז"),(131.59,"גם"),(131.83,"מוציא"),(132.07,"2.4"),(133.03,"מיליון"),
    (133.43,"שקל"),(133.75,"לקבלנים."),
    (134.87,"אין"),(135.11,"לך"),(135.35,"אנשים"),(135.59,"שיפקחו"),(136.15,"על"),
    (136.31,"הכסף,"),(136.79,"אז"),(136.87,"מי"),(137.11,"בודק"),(137.35,"שבאמת"),
    (137.75,"מפנים"),(138.23,"את"),(138.39,"הפחים?")])]),

 # "מה זאת אומרת מי?" answers the "מי" she has just asked four times.
 # The third of the three questions she asks in one breath, and the one that
 # is not abstract: somebody driving around to see the contractor did the job.
 # What sits between it and "מפנים את הפחים?" — "מי בודק ומי נותן קנסות?" —
 # came back garbled, so the cut steps over it.
 ("round",  141.29, 145.00, [(2, [
    (141.35,"עושה"),(141.67,"סיבוב"),(142.15,"ורואה"),(142.55,"שבאמת"),(143.27,"הקבלן"),
    (143.67,"עושה"),(143.99,"את"),(144.15,"העבודה"),(144.63,"שלו?")])]),

 ("q2hook", 145.20, 149.96, [
   (1, [(145.26,"מה"),(145.74,"זאת"),(145.90,"אומרת"),(146.14,"מי?"),
        (146.46,"העירייה"),(147.02,"צריכה"),(147.42,"לעשות"),(147.74,"את"),(147.90,"זה")]),
   (2, [(148.38,"בוודאי."),(149.02,"אבל"),(149.18,"אין"),(149.34,"לה"),(149.50,"עובדים.")])]),

 # One block, not two: the verb was falling into the gap between them, so the
 # 1.3 million arrived without anyone having cut it.
 ("eng",    153.92, 167.90, [(2, [
    (153.98,"גם"),(154.54,"בהנדסה,"),(154.94,"בוועדה"),(155.26,"לתכנון"),(155.66,"ובנייה,"),
    (155.90,"הם"),(156.46,"קיצצו."),
    (156.86,"היה"),(156.94,"להם"),(157.18,"תקציב"),(157.42,"מקורי"),(158.06,"של"),
    (158.38,"3"),(159.10,"מיליון"),(159.74,"שקלים"),(160.10,"לעובדים."),
    (160.83,"קיצצו"),
    (161.39,"1.3"),(162.59,"מיליון"),(162.99,"שקלים"),(163.39,"מהעובדים"),(163.95,"באגף"),
    (164.43,"הזה."),
    (164.83,"זה"),(165.07,"אגף"),(165.39,"שיש"),(165.63,"בו"),(165.79,"סמכויות"),
    (166.19,"שלטוניות"),(166.83,"כמו"),(167.07,"פיקוח.")])]),

 ("supervise", 171.40, 175.50, [(2, [
    (171.47,"הוא"),(171.63,"מפקח"),(172.03,"על"),(172.27,"כל"),(172.43,"העבודות"),
    (172.83,"שנעשות"),(173.47,"בעיר."),
    (174.17,"תסביר"),(174.65,"לי"),(174.81,"איך"),(174.97,"עושים"),(175.29,"את"),
    (175.37,"זה?")])]),

 # Contiguous, so no splice: the question and the picture it opens onto.
 # "באמת" at 180.17 is a stutter on the word before it and is not captioned.
 ("expect", 175.71, 186.15, [(2, [
    (175.77,"אתה"),(175.93,"מעביר"),(176.25,"את"),(176.41,"כל"),(176.49,"הכסף"),
    (176.81,"הזה"),(176.97,"לקבלנים"),(177.53,"ומה"),(177.77,"אתה"),(177.93,"מצפה"),
    (178.25,"שיקרה?"),
    (179.53,"שבאמת"),(180.49,"כל"),(180.81,"השיפוצים"),(181.29,"שנעשים"),(181.85,"ברחבי"),
    (182.25,"העיר"),(182.73,"כאילו"),(183.13,"בשם"),(183.53,"העירייה"),(184.25,"שיש"),
    (184.65,"עליהם"),(184.97,"פיקוח"),(185.45,"נאות?")])]),

 ("felt",   216.02, 217.78, [(2, [
    (216.08,"כבר"),(216.48,"עכשיו"),(216.88,"זה"),(217.04,"מורגש.")])]),

 ("q4str", 217.70, 228.90, [
   (1, [(217.76,"למשל"),(218.24,"איפה?"),(218.88,"תני"),(219.28,"לי"),(219.44,"דוגמאות.")]),
   (2, [(220.24,"אפילו"),(220.96,"בניקיון."),
        (223.28,"האשפה"),(223.84,"שפשוט"),(224.32,"נערמת"),(224.96,"ברחובות,"),
        (225.52,"ואף"),(225.92,"אחד"),(226.16,"לא"),(226.32,"מבין"),(226.64,"למה,"),
        (227.04,"מה"),(227.20,"קרה"),(227.52,"ומה"),(227.84,"השתנה.")])]),

 ("drain",  187.25, 194.80, [(2, [
    (187.31,"אז"),(187.39,"כן,"),(187.55,"בניהול"),(187.95,"מערכות"),(188.27,"ציבוריות,"),
    (188.91,"לא"),(189.07,"מתרוקן"),(189.55,"מכוח"),(190.03,"אדם"),(190.35,"שיש"),
    (190.59,"לו"),(190.83,"ידע,"),(191.55,"ניסיון,"),(192.35,"הבנה"),(192.75,"של"),
    (192.99,"מה"),(193.15,"שקורה"),(193.47,"בעיר,"),
    (193.79,"ופשוט"),(194.03,"זורק"),(194.51,"אותו.")])]),

 ("repeat", 251.70, 257.68, [(2, [
    (251.76,"בתברואה,"),(252.48,"וזה"),(252.88,"בשיטור"),(253.36,"ובפיקוח,"),
    (254.08,"וזה"),(254.48,"ברווחה"),(255.26,"וזה"),(255.58,"בנוער,"),
    (256.06,"והסיפור"),(256.70,"הזה"),(256.86,"חוזר"),(257.26,"על"),(257.50,"עצמו.")])]),

 # His question is back, and it starts where the question starts. In the
 # broadcast he says "כן, אבל איך את מסבירה את זה?" - the old in-point of 194.86
 # landed in the decay of "אבל", so what played was the wreck of a word and then
 # the question, which is what was being heard as two things at once.
 #
 # 194.94 is the in-point, with a 0.02s crossfade (see XF_BY). 194.880-194.950
 # reads as silence at -46 to -57 dB, but the first half of it is the voiced
 # decay of "אבל", and a 0.07s fade from 194.88 played it: faint, but in the one
 # gap where nothing else is sounding. 194.94 is on the floor itself, and the
 # short fade means his first word, which starts at 194.955, is not faded in to
 # get there. The out-point stops at 196.03, just short of the next voice's
 # onset at 196.04.
 ("q3",     194.94, 196.03, [(1, [
    (194.96,"איך"),(195.07,"את"),(195.31,"מסבירה"),(195.63,"את"),(195.79,"זה?")])]),

 # Split, to drop 201.22-201.90. Between "שלהם" and "בעיניי" the broadcast
 # carries 0.68s of speech that neither the word transcript nor the block
 # transcript accounts for - the tail of something said earlier, left in
 # because the block was lifted whole. It sat under her answer with no caption
 # of its own and read as a second sentence bleeding through. Both splice
 # points are placed so that the 0.07s crossfade itself lands in quiet audio:
 # the outgoing tail is 201.23-201.30, inside the 201.20-201.34 pause where the
 # signal is -45 to -56 dB, and the incoming head is 201.86-201.93, the dip
 # immediately before "בעיניי" starts at 201.94. The pause is kept, so her
 # answer still has its natural beat before the hook; only the speech between
 # the pause and the word comes out, and no transcribed word is touched.
 ("hook2",  198.72, 201.30, [(2, [
    (198.80,"תראה,"),(199.06,"אני"),(199.14,"לא"),(199.30,"יודעת"),(199.46,"להסביר"),
    (199.94,"את"),(200.18,"הפעולות"),(200.58,"שלהם.")])]),

 ("hook2b", 201.86, 205.20, [(2, [
    (201.94,"בעיניי,"),(202.50,"הם"),(202.66,"מובילים"),(202.98,"אותנו"),(203.38,"למסלול"),
    (203.94,"ישיר"),(204.34,"לקריסה.")])]),

 # Held back from q2hook and spent here. Contiguous with what it was cut from.
 ("empty",  149.92, 152.06, [(2, [
    (149.98,"היא"),(150.30,"מרוקנת"),(150.78,"את"),(151.02,"האגפים"),(151.50,"שלה.")])]),

 # The reprise. Her own words from the top of the interview, spent again as the
 # last thing said: the figure, and where the figure leads. Nothing was moved
 # to make room for it — the passage still runs whole in its own place at 0:32,
 # because the anchor's next question depends on her having just said it there.
 # The ending starts on "שם אותנו": the figure and the run up to it come out,
 # so the last thing said in the reel is where the money leads, not how much
 # of it there is.
 ("claim",   97.38, 103.00, [(2, [
    (97.44,"שם"),(97.76,"אותנו"),(98.08,"על"),(98.32,"המסלול"),(98.72,"הישיר"),
    (99.12,"להקרסת"),(99.76,"שירותי"),(100.16,"העירייה."),
    (101.18,"ממש"),(101.50,"בכל"),(101.90,"התחומים.")])]),
]

# the two figure panels, keyed to the segment they sit over and the word they land on
PANELS = {
  "clean": dict(label="ניקיון ותברואה",
                rows=[("420","אלף ₪",-1,"פחות לשכר העובדים"),
                      ("2.4","מיליון ₪",+1,"יותר לתשלום לקבלנים")],
                cue_a=128.84, cue_b=132.07, hold_to=134.60),
  "eng_b": dict(label="הנדסה, תכנון ובנייה",
                rows=[("3","מיליון ₪",0,"התקציב המקורי לשכר העובדים"),
                      ("1.3","מיליון ₪",-1,"קוצצו מהשכר באגף")],
                cue_a=161.39, cue_b=161.39, hold_to=164.60),
}

HOOKS = {"q2hook": "היא מרוקנת את האגפים שלה.",
         "hook2":  "הם מובילים אותנו למסלול ישיר לקריסה.",
         "hook3":  "באופן שיטתי ורחב."}
