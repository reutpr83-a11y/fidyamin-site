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


---

# v2 — more of her, one caption zone, a darker ground

126.1s, -13.7 LUFS, 0 samples of lag at three probes. Four notes from the
client, and what each one changed.

## More of Greenberg

Two passages of hers came back in, both verifiable word for word:

- **175.7-186.2** — "אתה מעביר את כל הכסף הזה לקבלנים ומה אתה מצפה שיקרה?
  שבאמת כל השיפוצים שנעשים ברחבי העיר כאילו בשם העירייה יש עליהם פיקוח נאות?"
  Ten and a half seconds, and it is the consequence of the engineering
  figures stated as a question. It should not have been left out.
- **216.0-217.8** — "כבר עכשיו זה מורגש." It is also the line that earns his
  next question, so it now sits directly before "למשל איפה? תן לי דוגמאות."

And three of his questions lost their run-ups: q1 starts on "למה הקרסת שירותי
העירייה?" rather than "אבל אני רוצה להבין", q2 on "העירייה צריכה לעשות את
זה?", q5 on "לא מעט ספקים חיצוניים". Nothing was lost; the operative clause
is the question.

She now holds **78%** of the speech, against 74% before.

## One caption zone

Every caption starts at y=1230, whatever it is. The question cards, the hooks
and the figure captions used to live in the middle of the frame with their own
furniture — a "יוסי הדר שואל" label, a gold rule, a second type size — which
put four separate blocks of text on screen at once. They are all captions now,
told apart by weight and colour and nothing else:

| | |
|---|---|
| her | 66px / 800, cream, spoken word in blue |
| her, on a hook | 66px / 800, **gold** |
| him | 58px / 500, dimmed cream |

Gone with them: the credit line under the title, the speaker's role, the
station under his name. **A title at the top, the names, the captions.** Every
other word on the frame was furniture.

## Captions that break where the sentence breaks

Splitting on width alone stranded last words: "בוודאי. אבל אין לה עובדים. היא
מרוקנת את" / "האגפים שלה." The chunker now looks back for a sentence end
before it breaks, and takes it if it falls beyond the first third:
"בוודאי. אבל אין לה עובדים." / "היא מרוקנת את האגפים שלה."

Hooks also wrap at 690px rather than 830, so they split into two lines that
each say something. 48 captions, 263 words, zero overlaps.

**And they no longer overlap each other.** Sharing one zone means a soft
handover is two lines of text drawn on top of each other. A caption whose
successor follows within 0.35s is now cut, not faded — which is how subtitles
have always worked. 32 of the 48 are hard swaps.

## Darker, bluer

The ground runs (5,15,35) to (11,36,82), from (11,43,68) to (18,61,96), and
the radial lift came down from 14 to 10. The brand blue and gold are unchanged
so the two reels still read as one family.

---

# v3 — the ending

127.3s. The reel was ending on "אתה לא עושה את המהלך הזה באופן שיטתי ורחב",
which is a rebuttal inside an argument, not a close.

**The order is argued now, not chronological.** The two blocks that came 13th
and 14th in the broadcast are last here:

> **איך את מסבירה את זה?**
> תראה, אני לא יודעת להסביר את הפעולות שלהם. **בעיניי, הם מובילים אותנו
> למסלול ישיר לקריסה.**

That is the headline of the article, it is the verdict of everything the reel
has just shown, and it lands as an answer to a question he asks — which is
worth more than the same sentence volunteered. Nothing else moved: he pushes
back, she answers, and only then does he ask the one she cannot answer.

**The address to the council is on the end card, not in her mouth.** The
interview contains no appeal to the coalition — she is answering questions for
four minutes, not making one — and assembling an appeal out of her sentences
would be putting words in her mouth. So the card makes it plainly, in the
campaign's own voice:

> פחות אנשי מקצוע בעירייה.
> יותר כסף לקבלנים מבחוץ.
> **חברי המועצה, דרשו לעצור עד שיוסבר.**

The first two lines are the same pair the budget reel's end card carries, so
the two films close the same way.

---

# v4 — three voices, and a sharper last word

126.8s, -13.7 LUFS, 0 samples of lag.

## The opening item is the reporter's, not the anchor's

It was attributed to Yossi Hadar. It is **Itamar Rotem**, the station's
reporter, and the recording says so: at 66.1s the anchor thanks him by name —
"אוקיי, תודה איתמר" — before turning to her. So the reel now carries three
names, not two: Rotem files the Interior Ministry item, Hadar asks the five
questions, Greenberg answers. Both station voices keep the same gold, because
both of them are 90FM.

The anchor's surname is left as **הדר**. The station's own lower third reads
"יומן החדשות עם יוסי הדר" in every frame of the recording, and so does 90FM's
own write-up of the interview.

## Two cuts that sharpen the end

**"תראה," is gone** from the front of her last answer. It is a softener, and
the answer starts harder without it: "אני לא יודעת להסביר את הפעולות שלהם."

**The hardest sentence in the interview was held back and spent last.** Her
answer to "העירייה צריכה לעשות את זה?" used to run whole — "בוודאי. אבל אין
לה עובדים. היא מרוקנת את האגפים שלה." The first half stays with his question;
the second half is now the reel's final line, after the verdict:

> בעיניי, הם מובילים אותנו למסלול ישיר לקריסה.
> **היא מרוקנת את האגפים שלה.**

Both halves are contiguous with what they were cut from, so nothing is
stitched and nothing is said twice.

## On "נפטר"

Kept with a ט. "אתה נפטר מהעובדים המקצועיים שלך" is the verb for getting rid
of something; with a ת, "נפתר", the word means *was solved*, which is not what
she says and not what the sentence can carry.

---

# v5 — the script, rebuilt

129.0s. One block out at the client's instruction, three in, and the argument
re-laid around them.

## Out

**"מה שהשתנה זה שאתה נפטר מהעובדים המקצועיים שלך"** (229.0-232.8). The client
judged it improper and it is: the sentence reduces people who lost their jobs
to something disposed of. Nothing of the reel's case rests on it.

## In

Three passages that were sitting unused in the recording, all verifiable word
for word:

**111.4-114.4 — "בסוף זו ההתמחות שלי, זה הניסיון שלי."** Her standing, in her
own voice, immediately after he asks why she calls it a collapse. The
management argument was making the case without ever saying who was making
it.

**171.4-175.5 — "הוא מפקח על כל העבודות שנעשות בעיר. תסביר לי איך עושים את
זה?"** What the engineering department actually does, which is what makes
cutting 1.3 million out of it mean something, and her challenge back to him.

**187.3-194.8 — "אז כן, בניהול מערכות ציבוריות, לא מתרוקן מכוח אדם שיש לו
ידע, ניסיון, הבנה של מה שקורה בעיר, ופשוט זורק אותו."** This is the sentence
the client was looking for, and it takes the removed block's place exactly:
she asks "מה קרה ומה השתנה", and this answers it.

## What moved, and why

She says **"בניהול מערכות ציבוריות"** twice in the interview. The reel used to
carry it once, in the management block; the drain sentence needs it more,
because without that frame "לא מתרוקן" has no subject. So it is cut out of the
management block — which now opens on her credentials instead — and kept in
the drain block. **She says it twice, the reel says it once.**

**The second half of "expect" came out** (179.5-186.1, "שבאמת כל השיפוצים
שנעשים ברחבי העיר..."). With "תסביר לי איך עושים את זה?" now immediately in
front of it, "אתה מעביר את כל הכסף הזה לקבלנים ומה אתה מצפה שיקרה?" closes the
thought on its own, and the elaboration only costs seconds the reel had
already spent.

## The shape now

| | |
|---|---|
| the fact | Rotem: the Interior Ministry letter, and the vote that went ahead |
| the concession | consultants are sometimes necessary |
| the claim | 56 million, the direct path to collapse |
| **the standing** | "זו ההתמחות שלי, זה הניסיון שלי" |
| the principle | you still need a system that supervises from within |
| the evidence | ניקיון ותברואה, then הנדסה, each with its panel |
| the consequence | what the department does, and what you expect to happen |
| what residents feel | rubbish in the streets — what changed? |
| **the answer** | a public system does not empty itself of the people who know |
| the pattern | and it repeats in policing, welfare, youth |
| the verdict | a direct path to collapse. It is emptying its departments. |

---

# v6 — the handover, and one message on the card

**The second opening block is the anchor, not the reporter.** The client hears
Yossi Hadar taking the item's last sentence — "ואם צריך, להוריד את הנושא מסדר
היום. לא הורידו. והצביעו באותו ערב." — and that is a normal radio shape: the
reporter lays it out, the anchor delivers the sting. It is labelled accordingly.

Worth recording that the measurement disagreed. Long-term average spectrum over
speech frames, cosine distance against clean references of each voice, puts
both opening blocks with the reporter (0.995 and 0.995, against 0.970 and 0.969
for the anchor) and places the handover at 57.1s, where the anchor says "אוקיי,
תודה איתמר". But every score on this recording sits between 0.96 and 0.99 —
both men go through the same studio chain, which flattens exactly the
differences the method relies on — so the margins are not wide enough to
overrule someone who knows both voices. Pitch was tried first and was worse:
octave errors put Greenberg's median at 119 Hz.

**The end card carries one message now.**

> לחברי מועצת העיר חריש
> **תפסיקו לשתוק.**
> **צאו נגד זה.**

The reel has already made the case. The card only has to say what to do with it.

---

# v7 — one name on the frame

The programme's title is "יומן החדשות עם יוסי הדר", and it sat at the top of
every frame while the speaker's name sat above the caption. So whenever she was
talking, the frame carried **two names** — his at the top, hers in the middle —
and neither one clearly belonged to the voice. A viewer scrubbing with the
sound off had no way to tell which was which.

The anchor's name comes out of the header. It reads **90FM · יומן החדשות**, and
the only name anywhere on the frame is the person speaking. He is still named,
on his own questions, where it means something.

The speaker line also grew from 33px to 37px and its rules were widened, so the
one name that is left reads as a label rather than a footnote.

---

# v8 — who says what, corrected twice over

Two attributions were wrong, and the second one was not a label problem but a
reading of the interview.

**The whole opening item is Itamar Rotem.** v6 moved its last sentence to the
anchor on the client's ear; she has since listened again and it is the reporter
throughout, which is also what the spectral measurement said in the first place
(0.995 to the reporter against 0.969 to the anchor, for that exact block). It
is back with Rotem.

**"יכול להיות שיש דברים שעובדי העירייה לא יכולים לעשות וצריכים לפעמים יועצים
חיצוניים" is the anchor, not her.** The reel had been running it as her
concession. It is his — he puts the counter-case to her — and the transcriber
had it as a separate speaker all along, which was missed.

That changes the shape of the opening for the better. What had been a flat
concession is an exchange, and her answer to it is stronger than the
concession was:

> **הדר:** יכול להיות שיש דברים שעובדי העירייה לא יכולים לעשות וצריכים לפעמים
> יועצים חיצוניים.
> **גרינברג:** ברור. מה זאת אומרת?
> **גרינברג:** אבל אנחנו מדברים פה על מצב — 56 מיליון שקלים.

The middle of her answer — "בתקופה שאני הייתי רוב הזמן הזה [?] ראש עיר, תמיד
העלינו יועצים חיצוניים" — came back too uncertain to caption, so the cut keeps
the two ends that are clean and drops what could not be verified, rather than
guessing at a word.

132.0s, 0 samples of A/V lag.

---

# v9 — the lead-ins put back

A full pass over the transcript against the cut, looking for sentences that had
lost the thing that makes them mean something. Seven were found.

| where | what had been cut away |
|---|---|
| the opening | **"אז לאחר פניות של יושב ראש האופוזיציה עם עורך דין לממונה המחוז במשרד הפנים"** — why the Ministry wrote at all. Without it the letter arrives from nowhere, and her part in causing it is gone |
| her answer to "למה קריסה" | **"אני אסביר. אני באה מהעולם הזה, בסדר?"** — the credentials line was landing with nothing behind it |
| the same block | **"בניהול מערכות ציבוריות,"** — put back, so the principle has its frame |
| the 420 | **"אם אתה מקצץ בתברואה"** — the figures were arriving with no verb and no department |
| the 1.3 | **"קיצצו"** — the same, and the reason the client caught it: 3 million, then 1.3 million, and nobody cutting anything |
| his second question | **"מה זאת אומרת מי?"** — it answers the four "מי" she has just asked |
| his last question | **"אבל בעיריות ובכלל"** — the frame of the challenge |

**"תן לי דוגמאות" is "תני לי דוגמאות".** He is talking to a woman.

Two blocks became one in the process. `creds` + `mgmt` + `clean` are a single
unbroken stretch now (109.5-139.1), and `eng_a` + `eng_b` likewise
(153.9-167.9) — which is what put "קיצצו" back, because the word had been
falling into the gap between them.

## Captions that do not fall over

The line breaker was leaving words stranded: "מבפנים. אתה חייב את זה. **אם**",
"היה להם תקציב מקורי של **3**", "לא מתרוקן **מכוח**". Two rules now:

- a caption never ends on a word that belongs to what comes after it — a list
  of connectives and pronouns, checked both when the line breaks and in a pass
  afterwards;
- a figure never ends a caption when the next word is its unit, so "2.4" and
  "מיליון שקל" stay together.

Line width went from 830 to 880, the width the budget reel uses, which also
takes pressure off the breaks. 57 captions, 326 words, zero overlaps.

## Length

**150.8s.** The reel gained nearly twenty seconds of context and it is now
2:31, which is long for a Reel. Nothing here was padding — every second of it
is a sentence that was not previously legible — but a trim pass is available
and the candidates are known: the middle clause of the Ministry item, the
second half of the engineering block, and the repeat block.

---

# v10 — the 56 million, completed and landed

**Restored in place:** "סעיפים שונים, ובזיהוי של איך הכסף הזה **זז**" (91.5-96.1).
It had been cut out of the middle of her claim for length, and it is the part
that says the money *moved* — which is the whole claim. The passage now runs
whole: 56 million, different budget lines, how the money moves, and the direct
path to the collapse of city services.

**Not moved to the end, and why.** The client asked for it as a closing beat.
Moving it breaks the interview's own logic: the anchor's question thirteen
seconds later — "למה **הקרסת** שירותי העירייה?" — exists only because she has
just used that word, and the whole long answer behind it hangs off that
question. The reel would lose her credentials, the management principle and
both figure panels to gain a repetition, because the reel already closes on
"מובילים אותנו למסלול ישיר לקריסה".

**So the number closes the reel on the card instead**, where it needs no
sentence around it:

> **56** מיליון שקלים
> שני גרינברג, על היקף המהלך
>
> לחברי מועצת העיר חריש
> **תפסיקו לשתוק. צאו נגד זה.**

The figure lands first and the ask follows it, so the last thing on screen is
the number and then what to do about it. The attribution line under it is there
because the figure is her characterisation of the budget update, not a figure
the reel can state in its own voice.

156.8s, -13.8 LUFS, 0 samples of A/V lag.

---

# v11 — the reprise

**Nothing moved.** Her claim still runs whole in its own place at 0:32, because
the anchor's next question depends on her having just said "להקרסת" there.

What is new is a **reprise at the end**: the same two pieces of her opening
answer, spent again as the last thing said in the reel.

> **56 מיליון שקלים,**
> מה שאנחנו רואים שזה שם אותנו על המסלול הישיר להקרסת שירותי העירייה.
> **ממש בכל התחומים.**

The figure gets the same large treatment it got the first time, so the two
land as a rhyme rather than as an accident, and "ממש בכל התחומים." closes in
gold. Then the card, where the number returns a third time as type.

165.6s, -13.8 LUFS, 0 samples of A/V lag.
