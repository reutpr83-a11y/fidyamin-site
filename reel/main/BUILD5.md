# The main reel — how it was built

`harish-main-reel.mp4`, 1080x1920, 30fps, 72.7s.

## Source and transcript

The uploaded take is the **15:59:53 recording** (159.4s). It arrived as a
576x1024 export at 772 kbps, not the phone original — see *Picture quality*
below.

No transcript came with it, and there is no speech recogniser in this
environment, so the take had to be matched to one of the three transcripts
already in the repo (`video/work/transcript*.json`). Two of them are the same
script recorded four minutes apart, so guessing was not an option. The take's
speech envelope was correlated against each transcript's word mask:

| transcript | offset | normalised peak |
|---|---|---|
| `transcript_155953.json` | +0.09s | **0.5552** |
| `transcript_160335.json` | +0.10s | 0.3791 |
| `transcript.json` | +2.13s | 0.1185 |

`transcript_155953` it is, with its clock running 0.09s ahead of the file.
That offset is carried in `map5.json` and applied at every cut.

## Order

Seven beats, argued rather than chronological:

1. **הטענה** — מקצצת מיליונים מאנשי המקצוע ושופכת את הכסף על קבלנים חיצוניים
2. **אז פוליטי אמרתם?** — the dismissal, answered before it is made
3. **הראיות** — הנדסה ותברואה, with the two data panels over her
4. **הכביש** — what that buys you on your own street
5. **העיקרון** — האחריות והפיקוח חייבים להישאר בפנים; התושבים משלמים
6. **לא ידענו** — לא תוכלו להגיד שלא ידעתם, לא הזמן לשבת על הגדר
7. **הדרישה** — תתנגדו למחטף, ומוסרית וגם פוליטית

The last line answers the second beat, so the reel closes its own loop.

A beat is a contiguous stretch of the take, so every join inside a beat is not
a cut at all; only the six jumps between beats need a dissolve, and each is
0.35s. The shot never cuts: one continuous 1.00 to 1.0667 push runs across the
whole reel, and the held beat before the card is frame continuous with the
last one.

## The data panels

Both come off the budget document: **slide 09** (הנדסה, תכנון ובנייה —
1.3 מיליון ₪ פחות לשכר, 970 אלף ₪ יותר לייעוץ ופיקוח) and **slide 06**
(ניקיון העיר — 421 אלף ₪ פחות לשכר, 2.43 מיליון ₪ יותר לקבלנים). They are
drawn to the same shape on purpose: the reel's claim is that the shape repeats.
Figures in `#63cbea`; the arrow and the word carry the direction, so the colour
never has to mean up or down. The captions under them stay regular — the
panels are the emphasis, and a second right aligned element would crowd them.

## Sync

Each beat's video is cut to whole frames and so runs a few milliseconds longer
than the audio that came with it; `audio5.py` recuts every beat's audio to the
exact length of its own video before crossfading, which is what keeps eleven
(here seven) chained beats from drifting. `sync5.py` cross correlates the
finished master against the take beat by beat.

## Picture quality

The take is a 576x1024 / 772 kbps export. The output is 1080x1920, so the
picture is upscaled 1.875x. The pipeline does what can be done — denoise before
scaling, a clean 2x to 1152x2048, then unsharp and grade, and a push that ends
at 1:1 rather than upscaling further — but it cannot invent detail that the
export threw away. The phone original (or a full quality export) would run
through the same scripts unchanged and look as sharp as the youth reel.
