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

---

# v2 — the full strength cut (`*6.py`)

`video/out/harish-main-reel-v2-1080x1920.mp4`, 131.3s, -14.1 LUFS, -1.4 dBTP,
0.000s beat lag against the take. Same take, same measured offset, same grade.
Encoded at crf 18 rather than 16 so it stays under GitHub's 100MB limit; on a
source this soft the two are indistinguishable. What changed:

## More of the argument

Six beats instead of seven, but longer ones, because a beat is a contiguous
stretch of the take and the cut now keeps whole stretches rather than
sampling them:

| beat | take | what it carries |
|---|---|---|
| הטענה | 10.70–19.99 | מקצצת מיליונים ושופכת על קבלנים חיצוניים |
| אז פוליטי | 3.95–9.18 | ביקורת על מיליונים היא פוליטית? |
| הראיות | 29.28–56.90 | דוגמאות, הנדסה, תברואה, ניהול מערכות, **קריסה** |
| המציאות | 60.11–96.74 | הפחים, הכביש, החלטורה, הבורות, האחריות, **הם ורק הם** |
| הפנייה | 98.30–120.27 | בית המשפט, משה נגה איציק רויטל, הסתירו מכם |
| פחות | 124.80–128.50 | **פחות פיקוח, פחות ניקיון ופחות שירות לתושבים** |
| מנהיגות | 133.20–156.73 | לא ידעתם, זו מנהיגות, תתנגדו, **מוסרית וגם פוליטית** |

Dropped: the false start at 57.11, "אם המהלך הזה יעבור ... לא יישאר מי
שיבדוק" (the reel says it twice more, better), "להגיד שזו פוליטיקה לא ינקה
מהאחריות", and — at the client's request — "לאסון", which took with it the
sentence it completes ("ואתם אמורים לראות בדיוק כמונו לאן המהלך הזה מוביל,"),
since that dangles without its ending. Both new cut points fall inside real
silences: 119.92-120.31 and 124.54-125.13.

## Transcription fixes

Checked against the budget document, not guessed:

- `לממלאי המקום` → `לממלא המקום`. Slide 11 names the line as
  "סעיף תקשורת הנהלת העירייה ולשכת **ממלא מקום** ראש העיר" — one person.
- `נגע` → `נגה`
- `והעבירו את עדכון לתקציב הזה` → `עדכון התקציב הזה`

## A third panel

Slide 11: the management communications budget goes 900 אלף → מיליון, and the
document says the line covers the acting mayor's office. It comes up under
"ברור לכולם שגם לכם לא הסבירו כלום" and holds through "הסתירו מכם מידע
שאנחנו מגלים לכם אותו", so the reveal is on screen by the time she says she is
making it. It is what gives her closing
question its weight: by the time she asks "לציבור או לממלא המקום", the viewer
has seen his office's number.

## Five emphasis captions

קריסה. / עם בורות ליד בתי הספר. / הם ורק הם. / פחות פיקוח, פחות ניקיון ופחות
שירות לתושבים. / מוסרית וגם פוליטית.
One per act, which is what BRAND.md's emphasis style is for. The previous cut
used none.

## Two defects fixed

- **Captions overlapped for four frames.** `LEAD` in `caps.py` puts a word on
  screen 0.13s before it is spoken, so the next caption's first word arrived
  while the previous caption was still up. `GAP` in `caps6.py` clears the
  previous caption before the lead instead of 0.02s before the nominal start.
- **A first word could be swallowed by its own dissolve.** She false starts at
  57.11 and restarts at 60.21 after "סליחה", leaving 100ms of silence — less
  than the 0.35s crossfade. Every beat is cut to end in silence, so only the
  outgoing side needs a fade: the audio crossfades now use `c2=nofade` and the
  incoming beat enters at full level.


---

# The camera original

`video/out/harish-main-reel-hq-1080x1920.mp4`, 131.3s, and the full quality
master in `video/out/hq-master/`.

The reel had been cut from a 576x1024 WhatsApp export at 772 kbps, because
that was the only copy of the take that existed anywhere I could reach. The
camera original was then pushed to `youth-source-upload:video/src/155953/`
in six byte exact parts, rejoined here, and verified against its sha256:

    0a9d12ff3c42f0edc1d764a145e36259491cf5f78b7d78c19c1d69d80c893861
    520673951 bytes, HEVC 2160x3840, 26 Mbps, 159.367s

**Nothing about the edit changed.** The speech mask correlation put it at the
same +0.09s offset against `transcript_155953` (0.557, against 0.383 for the
next best), and the take is the same length as the export, so every beat,
every caption time and every panel window came out identical: 126.00s of body,
46 captions, 5 emphasis lines, panels at 17.19, 25.94 and 92.87. Beat lag
against the source measured 0.000s on all seven beats.

What changed is the grade, and that matters as much as the resolution:

| | from the export | from the original |
|---|---|---|
| `hqdn3d=3:2:6:6` | hiding compression artefacts | **removed** |
| `unsharp=7:7:0.9` | putting back what the upscale lost | **removed** |
| contrast / saturation | 1.06 / 1.05 | 1.03 / 1.02 |
| scale | up 2x from 576x1024 | **down** from 2160x3840 |

Both filters existed only to serve a damaged source. On a real one they do
harm. The contrast lift came down too, because the picture is no longer
washed out by compression.



## Restored to the approved edit, at camera quality

A run of changes went too far: an opening panel, an opening beat from a
different take, a reordering. The client's instruction was to put the approved
edit back exactly and improve only the picture. All of that is reverted.

The seven beats are in their approved order — הטענה, אז פוליטי, הראיות,
המציאות, הפנייה, פחות, מנהיגות — all from the 15:59:53 take. 46 captions, 284
words, five emphasis lines, three panels.

Two things differ from the version the client approved, and only two.

**The frames come from the camera original.** 2160x3840 HEVC at 26 Mbps rather
than a 576x1024 WhatsApp export at 772 kbps, and `hqdn3d` and `unsharp` are out
of the grade because both existed only to hide that export's damage.

**Each dissolve has room.** A 0.35s dissolve takes the last 0.35s of the
outgoing beat, and five beats ended just 0.10s after their last word, so the
picture began changing 0.25s before the sentence had finished and the
transition read as trampling the line. Every out point moved far enough past
its last word for the whole dissolve to fall in silence:

| beat | out was | out now | silence before the dissolve |
|---|---|---|---|
| הטענה | 19.99 | 20.36 | 0.12s |
| אז פוליטי | 9.18 | 9.55 | 0.12s |
| הראיות | 56.90 | 56.90 | 0.23s, already clear |
| המציאות | 96.74 | 97.11 | 0.12s |
| הפנייה | 120.27 | 120.27 | see below |
| פחות | 128.50 | 128.86 | 0.11s |
| מנהיגות | 156.73 | 157.10 | 0.12s |

Everything added is silence. No word was added and none was removed.

הפנייה cannot be fixed: 0.06s separates its last word from the sentence cut
after it, so there is nowhere to move to. Its overlap is 0.02s, under one
frame, and it stays as approved.

133.1s, 0.000s beat lag on all seven, -14.1 LUFS, -1.4 dBTP.

## Build time

The composite is the slow stage and it ran on one core. `fastbuild.sh` splits
the frame range across four workers, each decoding its own slice of the plate
and encoding its own chunk, then concatenates them with a stream copy and
**fails if the frame count does not match**, so a split can never silently lose
or duplicate a frame. `REEL_FRAMES` is passed through so each worker computes
the push in against the whole reel rather than against its chunk, which keeps
the zoom continuous across the joins.

The plate and the beat cuts are intermediates that get re-encoded anyway, so
they use a fast preset at a lower crf: faster and slightly cleaner at once. The
master itself stays crf 18.

Whole build: **16 minutes, down from about 40.**

## Two outputs

| file | size | for |
|---|---|---|
| `harish-main-reel-hq-1080x1920.mp4` | 87 MB, 5.3 Mbps | posting. One file, one click, already above what Instagram and Facebook keep after their own re-encode |
| `hq-master/` | 170 MB in 2 parts, 10.7 Mbps | archive and any future re-edit |


---

# v3 — flow, and a score

`video/out/harish-main-reel-hq-1080x1920.mp4` (voice only — **this is the
approved final**, see `video/out/FINAL.md`) and
`video/out/harish-main-reel-hq-music-1080x1920.mp4` (with the score). Identical
picture, identical length: 131.306s, 1080x1920, 30fps, -14.1 LUFS, -1.4 dBTP.
0.000s beat lag on all seven beats.

The complaint was that the structure did not carry, that the opening swung the
tone too far, and that the examples section smeared. Three separate problems,
and only one of them was in the writing.

## The opening no longer changes register

"ביקורת על מיליונים היא פוליטית?" is the whole answer to the dismissal, and it
is delivered straight. "תגידו, אתם השתגעתם?" that followed it is delivered as
disbelief, with the smirk — funny in the room, and a cost in credibility in a
reel that is otherwise a manager presenting evidence. It is out. `אז פוליטי`
ends at 7.72 instead of 9.18, cutting into 0.45s of measured silence
(7.34–7.79), and the reel goes straight from the rhetorical question to
"רק כמה דוגמאות קטנות."

Nothing else in the opening moved.

## The examples section no longer drags

The smear was not pacing. It was the panels arriving before the words.

Every figure cue was 0.6–1.4s ahead of the sentence that names it, which
BRAND.md forbids in as many words: *המספר נוחת על המילה של הדובר, לא אחריה*.
A number that lands early reads as an illustration of something not yet said,
and the eye goes back and forth between the graphic and her face looking for
the connection. Every cue was re-timed against the transcript's word clock:

| panel | figure lands on | at |
|---|---|---|
| הנדסה | "1.3 מיליון" | 33.54 |
| הנדסה | "כמעט מיליון" | 38.16 |
| ניקיון | "400,000" | 43.08 |
| ניקיון | "2.4 מיליון" | 45.82 |

## A fourth panel, and one address kept whole

**ביטחון (slide 08)** — 650 אלף ₪ יותר לשמירה מול 206 אלף ₪ פחות לשכר בשיטור
ובפיקוח העירוני — lands on the word "הפיקוח" at 85.38, inside
"האחריות, הפיקוח והיכולת לוודא שהעיר מתפקדת חייבים להישאר בתוך העירייה." The
reel's claim is that the shape repeats across departments, and a fourth
instance of the same shape, on the sentence that states the principle, is the
cheapest proof of it available.

**`פחות` moved up**, to sit directly after "הם ורק הם" instead of after
הפנייה. "פחות פיקוח, פחות ניקיון ופחות שירות לתושבים" is the consequence of
the four departments she has just been through; it belongs to that address, not
to the section about the court. The order is now: הטענה, אז פוליטי, הראיות,
המציאות, **פחות**, הפנייה, מנהיגות.

## Every dissolve falls in silence

The v2 pass fixed five of seven out points; this one fixed the rest. All seven
beats now end far enough past their last word that the whole 0.35s dissolve
lands in silence. Nothing was cut and nothing added but silence.

## The score (`score6.py`)

Built rather than licensed, to BRAND.md's spec, and it follows the cut — it
reads `map6.json` and `panel6.json`, so it cannot drift from the picture.

- 84 BPM. A pulse from frame one.
- A sub floor arrives at המציאות (40.1s), when the argument moves from
  documents to the street.
- Dry ticks from הראיות (12.8s), under the evidence.
- One pad, chord changes only on act boundaries.
- **Exactly six effects** in 131 seconds: four figure accents, one on each
  panel's arrival, plus the layer arrival and the resolve.
- `hush()` drops everything for 1.5s before the demand. The loudest moment in
  the reel is silence.

## The mix (`mix6.py`)

The music ducks 10 dB under her voice, keyed off the voice's own envelope
rather than a fixed automation curve: 30ms smoothing, threshold at the 55th
percentile, a one-pole follower at 0.08 attack / 0.55 release. She is talking
for 55% of the reel, so the score is effectively a floor under the speech and a
presence in the gaps. Mixed at 0.55, then `loudnorm` on the sum.

Both audio variants are rendered onto the identical picture, so the choice
between them is only ever a choice about the score.

## Files

| file | size | for |
|---|---|---|
| `harish-main-reel-hq-1080x1920.mp4` | 87 MB, 5.5 Mbps | posting, voice only |
| `harish-main-reel-hq-music-1080x1920.mp4` | 87 MB, 5.5 Mbps | posting, with the score |
| `hq-master/` | 167 MB in 2 parts, 10.2 Mbps | archive and any future re-edit |

`beats6.approved.py`, `datapanel6.approved.py` and `map6.approved.json` are the
approved v2 edit, kept so any of this can be compared against it or reverted to
it exactly.
