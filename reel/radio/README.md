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
