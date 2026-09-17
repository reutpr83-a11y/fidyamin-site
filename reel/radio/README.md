# The radio interview reel — design

The source is a 90FM interview: audio-led, with no picture worth building a
reel on. So the design carries it. Clean navy ground, no photography behind the
words, the same Heebo and the same palette as the budget reels so the two read
as one family.

`design.py` renders five still frames, one per frame type. It is the look, not
the film — the cut gets built once the interview audio and its transcript are in
`video/src/radio-90fm/` on the `radio-source` branch.

| frame | what it is |
|---|---|
| A | the cold open. What was said, before who said it |
| B | the interviewer's turn. Gold, smaller, its own mark |
| C | her turn. Portrait, running caption, the spoken word lit |
| D | a figure panel, the same shape the budget reel uses |
| E | the hook. The frame people screenshot |

## Rules the frames hold to

**The station is on every frame.** 90FM and the programme name at the top, the
topic under them, the date and "the full interview at" under that. This material
is worth more than a selfie video for exactly one reason — somebody else is
asking her — and the design has to say so continuously.

**Both speakers are named, and they never look alike.** She is cream, large,
centred captions. He is gold, smaller, right aligned, under a "יוסי הדר שואל"
mark. A viewer scrubbing with the sound off still knows who is talking.

**One caption position.** Every running caption starts at y=1268, whatever else
is on the frame, so the eye never hunts for it between cuts.

**Nothing below y=1620.** Instagram covers roughly the bottom 250px of a Reel
with its own username, caption and audio row. The source credit moved up under
the header for this reason rather than sitting in a footer that gets eaten.

**The waveform is the audio, not decoration.** In the build it follows the
envelope of the voice, so a static frame still moves with the speech.

**Arrow and word carry direction, never colour.** Figures stay `#63cbea`
whether they are a cut or an increase, as in `datapanel6.py`.

The words in the mockups are placeholders: hers come from the verified
transcript of the earlier take, his are invented to show the frame type. The
real lines come from the interview.

---

# The cut

`video/out/harish-radio-90fm-1080x1920.mp4` — 116.7s, 1080x1920, 30fps,
-13.7 LUFS, 697 kbps. Audio to picture lag measured 0 samples at three probes.

## Where the material is

The upload is 4:31. The first 48 seconds are the host's own item introduction
and the news bulletin around it; the interview proper starts when he hands
over at 48.4s. Speaker turns were measured before the transcript existed —
F0 by autocorrelation every 20 ms, the host low and Greenberg high, smoothed
and merged — and the share of voiced frames above 165 Hz jumps from about 40%
to over 90% at the 78 second mark, which is where her first long answer
begins.

## Seventeen stretches

`blocks.py` holds them. The reel opens on the host, not on her, because the
strongest factual material in the whole recording is his:

> בבוקר יום ההצבעה על התקציב, שלחה נציגת משרד הפנים מכתב למנכ״ל העירייה...
> ואם צריך, להוריד את הנושא מסדר היום. **לא הורידו. והצביעו באותו ערב.**

That is a reporter stating a fact, not an opposition leader making a claim,
and it buys the rest of the reel its credit.

Her five answers then run in domain order — the concession that consultants
are sometimes necessary, the 56 million, the management argument, ניקיון
ותברואה, הנדסה — with the host's five questions kept as beats between them.

## What was left out, and why

**"הם מקורבים או קשורים לכאורה לאנשים שנכנסו שם לשלטון"** (239.6s). The one
sentence in the interview that is an accusation rather than an analysis, and
the only one with no document behind it. Anyone wanting to discredit the reel
would hang it on that line and take the 56 million, the 1.3 and the Interior
Ministry letter down with it. The client agreed to leave it out.

Two further passages were dropped because the transcriber returned them
garbled and they could not be verified by ear: the words before "56 מיליון"
at 88.2s, and "אם אתה מקצץ בתברואה" at 127.4s. **Rather than guess at a word
and put it in her mouth, the cut starts after it** — which is why the
tberua'a block opens on "420" and lets the panel name the department, and why
the engineering block is in two pieces with the unverifiable 160.8-161.3
removed.

## Captions

The transcriber returns start times only, and stretches some end times past
the next word's start, so ends are derived and never trusted. A word's length
is estimated from its letters, which is what separates a real pause from a
long word: "שלחה" to "נציגת" is 0.64s start to start and is not a break at
all. Captions group to at most two lines and break on a real pause of 0.45s;
anything left at one or two words is folded into its neighbour. 44 captions,
245 words, zero overlaps.

Every caption line is corrected by hand. Hebrew ASR mangles figures —
"1000000" for מיליון, "420 1000" for 420 אלף — and words: הטרסת for הקרסת,
מהמשקורות for מהמשכורות, שיתפחו for שיפקחו, והכוס for והסיפור.

## Nothing dissolves

The ground never changes, so a full frame dissolve would be invisible. Every
element animates on its own instead — a caption rises and fades, a figure
lands, a panel slides — which is what lets the cut be fast without looking
cut. The audio splices are 0.07s equal-power: the broadcast is so compressed
that there are no pauses to hide a long dissolve in. Measured, the 18th
percentile of level is only 2.8 dB below the speech p90, so there is no noise
floor to clean either. The audio chain is a high-pass at 80 Hz, which removes
a 25 Hz rumble and its harmonics, and `loudnorm`. Nothing else.

## The waveform is the picture

It follows the envelope of the finished voice track, and it changes places
with whatever else wants the middle of the frame: big and central when the
stage is empty, a quiet strip at the bottom when a question card, a hook, a
figure or a panel is up. It also carries the speaker colour — gold for the
host, blue for her — so a viewer scrubbing with the sound off still knows who
is talking.

## A bug worth recording

`voice.wav` was first written by piping raw f32le into ffmpeg with `-ac 2` as
an input option. It came back as mono, twice as long, and every frame's
waveform was then drawn from the first half of the speech stretched over the
whole reel — silently, with no error anywhere. It is written with Python's
`wave` module now. The check that caught it was simply comparing the file's
duration against `len(out)/SR`.
