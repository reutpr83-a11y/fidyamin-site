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

---

# v12 — the claim moves to the end, and stays there only

v11 left her claim in both places. The instruction was one place: the end. The
three blocks — "אבל אנחנו מדברים פה על מצב", the figure, and
"סעיפים שונים, ובזיהוי של איך הכסף הזה זז. מה שאנחנו רואים שזה שם אותנו על
המסלול הישיר להקרסת שירותי העירייה. ממש בכל התחומים." — are moved, not copied.

**What that costs, recorded honestly.** The anchor's question at 0:24,
"למה **הקרסת** שירותי העירייה?", used to follow her saying "להקרסת" thirteen
seconds earlier. It no longer does. It still reads as him challenging a claim
of hers, and the header names the subject, so it holds — but it is a real
seam and it is the price of the ending.

**The end card drops the addressee and the attribution.** It goes up on her own
page, so "לחברי מועצת העיר חריש" and her name under the figure were both saying
something the page already says.

> **56** מיליון שקלים
> **תפסיקו לשתוק.**
> **צאו נגד זה.**

156.0s, -13.8 LUFS, 0 samples of A/V lag.

---

# v13 — no full stops

Two captions were carrying a full stop while the speaker was still mid
sentence, because the cut landed where the sentence did not:

- **"זה אגף שיש בו סמכויות שלטוניות כמו פיקוח."** — she goes on to
  "לדוגמה, צווי סגירה על הבנייה"
- **"יש לא מעט ספקים חיצוניים, לא רק בניקיון."** — he goes on to
  "בדברים נוספים"

Rather than fix two and leave the rest to judgement, captions carry no full
stops at all now. A caption is a fragment of speech, not a paragraph. Commas
and question marks stay, because they are real and they carry meaning; only a
trailing point is stripped, so "2.4" and "1.3" are untouched. The end card
follows the same rule.

---

# v14 — two more of hers, and the full stop rule made precise

**"עושה סיבוב ורואה שבאמת הקבלן עושה את העבודה שלו?"** (141.3-145.0). The third
of the three questions she asks in one breath, and the only one that is not
abstract — somebody actually driving around to see the contractor did the job.
What sits between it and "מפנים את הפחים?" came back garbled, so the cut steps
over it.

**"שבאמת כל השיפוצים שנעשים ברחבי העיר, כאילו בשם העירייה, יש עליהם פיקוח
נאות?"** (179.5-186.2). Contiguous with the question before it, so no splice.
It is the line that takes the argument out of the budget and onto the street:
every renovation in the city is done in the city's name.

## The full stop rule, corrected

v13 stripped every point, which took two that were doing work: "לא הורידו**.**
והצביעו באותו ערב" and "בוודאי**.** אבל אין לה עובדים". The rule is narrower
now and applies where the complaint actually was — **a caption never ends in a
full stop**, because that is where the cut may not agree with the sentence. A
point *inside* a caption sits between two sentences that really did end, and it
stays.

It is applied last, after every merge and move, so a word that was stripped
while it was last does not come back mid-caption without its point.

166.3s, -13.8 LUFS, 0 samples of A/V lag.

---

# v15 — three corrections

**The anchor's "אבל בעיריות ובכלל יש לא מעט ספקים חיצוניים" is out**, and her
answer to it had to go with it. "אתה לא עושה את המהלך הזה באופן שיטתי ורחב" is
addressed to *him*, about other municipalities: they use contractors, but not
systematically and not on this scale. Standing alone after "והסיפור הזה חוזר
על עצמו", the same sentence reads as being about Harish and says the opposite
of what she means. Both blocks are gone; the reel runs from the repeat straight
into "איך את מסבירה את זה?"

**"עדיין" is cut out of the middle of the sentence** — 120.30 to 120.72, the
word and nothing else — so the line lands as "אתה צריך מערכת שיודעת לפקח
מבפנים" rather than "you still need". Levels either side of the cut are within
0.3 dB of each other, so the splice sits inside continuous speech and does not
click.

**"העירייה צריכה לעשות את זה" loses its question mark.** He is telling her the
municipality should be doing it, not asking whether it should.

157.0s, -13.7 LUFS, 0 samples of A/V lag. `script.txt` carries the full
running script as text.

---

# v16 — the ending starts where the money leads

**The figure comes off the front of the closing block.** The ending used to open
on "אנחנו מדברים פה על מצב 56 מיליון שקלים, סעיפים שונים, ובזיהוי של איך הכסף
הזה זז" and only then reach the line that matters. The cut now starts at 97.38s,
on **"שם אותנו על המסלול הישיר להקרסת שירותי העירייה — ממש בכל התחומים"**, and
the run-up is gone. Two reasons it is better this way: the last thing said in
the reel is where the money leads rather than how much of it there is, and the
accounting sentence ("סעיפים שונים, ובזיהוי של איך הכסף הזה זז") was the one
place in the closing block that asked the viewer to follow a mechanism instead
of a claim. The `but` and `fifty6` blocks are removed outright; `claim` is a
single unspliced piece of speech, 97.38-103.00.

**The end card drops the number too.** It now carries one message and nothing
else:

    תפסיקו לשתוק
    צאו נגד זה
    מתוך הראיון ביומן החדשות

Both lines went to 96px/800 (from 84) now that they are alone on the card, the
gold rule sits at y=640 and grows to 280px, and the card tail is 5.8s instead of
6.8 — there is less to read, so it does not need as long.

146.7s total (2:27), 4401 frames, -13.7 LUFS, 0 samples of A/V lag.

---

# v17 — the design audit

Four changes, all of them measured on the v16 frames before they were made.

**The speech block moved down 90px.** The lowest ink on four frames out of five
was y=1400 of 1920 — a quarter of the picture doing nothing, and a composition
that floated in the middle of the frame. The waveform stage, the speaker's name
and the caption zone all moved together: 820→880, 1136→1226, 1230→1320. A
two-line hook now bottoms out at 1502 and the waveform strip under a panel is
unchanged at 1610, both clear of 1620 where Instagram's own furniture starts.

**Hooks are 76px, not 66px.** A hook and an ordinary caption were the same size
and the same weight, separated by colour alone — gold against cream reads as "a
slightly different colour", not "this is the line". The line width went with it,
700→760, so the chunking came out identical: same 53 captions, same splits, just
bigger where it matters.

**The domain is named on screen.** The cut is ordered by domain, which was the
brief, but the only place that order was visible was the two number panels;
supervision, manpower and refuse all went by unmarked. `DOMAINS` maps segment
ids to a label and `domain_spans()` reads their times out of the segment map, so
the tag cannot drift from the cut. Spans are chained end-to-start, so there is
exactly one boundary between any two domains and the outgoing label finishes
fading before the incoming one begins. While a number panel is up the tag fades
out and the panel's own bigger label carries the domain — it is never named
twice on the same frame.

    0.00-23.43   ההצבעה על התקציב
    23.43-44.84  קבלנים במקום עובדים
    44.84-66.74  ניקיון ותברואה          ← panel
    66.74-101.43 הנדסה, תכנון ובנייה     ← panel
    101.43-120.04 אשפה ברחובות
    120.04-125.99 כוח אדם בכל האגפים
    125.99-140.93 התמונה הכוללת

**A progress bar, and the ground drifts.** The bar is 4px at the very top and
fills right to left like the words, completing exactly at the end of the card.
The drift pans an oversized ground on two long periods (46s and 61s) that do not
repeat inside a reel, under two pixels a second — the frame stops being
literally static between two caption fades without anything appearing to move.

## What was measured and left alone

Contrast of every text colour against the actual pixels behind it: captions
17.1:1, the anchor's questions 13.6:1, gold hooks 9.5:1, the dim sub-line under
a figure 6.0:1. The threshold is 4.5:1. Caption length runs to a median of 28
characters and never more than two lines. None of it needed changing.

146.7s (2:27), 4401 frames, -13.7 LUFS, 0 samples of A/V lag.

---

# v18 — the stray half-second under her answer

Between "אני לא יודעת להסביר את הפעולות שלהם" and "בעיניי, הם מובילים אותנו
למסלול ישיר לקריסה" the broadcast carries **0.56s of speech that no transcript
accounts for** — not the word-level one, not the block-level one. It was in the
reel because `hook2` was lifted as one piece, 199.00-205.20, and it sat under
her answer with no caption of its own, which is exactly how it reads: a second
sentence bleeding through hers.

What the source actually contains across that stretch:

    200.58-201.20  "שלהם", emphatic, F0 rising 210→390 into a continuation rise
    201.20-201.34  a real pause, -45 to -56 dB
    201.34-201.86  voiced speech, no transcribed word anywhere in it
    201.94         "בעיניי" starts

`hook2` is now split in two around it: 199.00-201.30 and 201.86-205.20. The
split points are chosen so the 0.07s equal-power crossfade itself lands in quiet
audio — the outgoing tail is 201.23-201.30, inside the pause, and the incoming
head is 201.86-201.93, the dip before the word starts. The pause is kept, so her
answer still has its natural beat before the hook; only the speech between the
pause and the word comes out.

Nothing else was touched. `hook2b` inherits the hook style, so the split is
invisible in the captions: the same words, the same two chunks, the same colour.

140.30s of voice (0.63s shorter), 4383 frames.

146.1s (2:26), 4383 frames, -13.7 LUFS, 0 samples of A/V lag including across the new splice at 129s.

---

# v19 — the question comes out, because the mess is in the broadcast

v18 removed a stray half-second and it was not what was being heard. What is
being heard sits **under the anchor's question** "איך את מסבירה את זה?", where
she is still audible through his words — a second voice you cannot make out.

## Proving whose fault it is

The reel's audio across that span was subtracted against the source, sample
aligned:

    gain reel/source                 0.9994
    source level                     -24.9 dB
    residual after removing source   -91.4 dB   (66.5 dB down)

66.5 dB down is numerical noise, so the reel carries that span **bit for bit as
the broadcast has it**. The edit introduced nothing; the overlap is in the 90FM
recording and cannot be lifted off his voice. A two-comb detector was tried
first and thrown away: run against clean single-speaker passages it fired on
31-46% of frames (`q4` 30.9%, `repeat` 40.8%, `eng` 45.6%) against 28.8% on the
suspect span, so it could not tell one voice from two and nothing was decided
on it.

There is no clean take of the same question anywhere in the interview — the
other four are already in the reel or were cut on request — so the question goes
rather than the mess. Her answer needs no prompt: "והסיפור הזה חוזר על עצמו"
runs straight into "תראה, אני לא יודעת להסביר את הפעולות שלהם".

## Two splices improved, now that they can be

Removing the question put `repeat` next to `hook2`, so both edges could move off
speech and into silence:

- **`repeat` out 257.72 → 257.68.** 257.72 was 0.02s into her *next* sentence
  and put the crossfade tail on its onset. 257.68 puts the whole tail inside the
  -49 to -53 dB dip after "עצמו".
- **`hook2` in 199.00 → 198.72.** 199.00 was 0.2s inside "תראה", clipping it to
  a fragment. 198.72 is in the real silence before she speaks, so the crossfade
  is inaudible and the word comes back whole — and it is captioned now, because
  it is audible and the transcript has it.

Measured at the new splice: her sentence decays to -61 dB and "תראה" starts
0.02s later. The crossfade sits entirely inside that pause.

139.42s of voice, 4357 frames.

145.2s (2:25), 4357 frames, -13.7 LUFS, 0 samples of A/V lag including across the new splice at 126s.

---

# v20 — the question back, from where the question starts

v19 removed the anchor's question on the theory that she was audible underneath
it. That was wrong, and the right diagnosis came from the person who could hear
it: in the broadcast he says **"כן, אבל איך את מסבירה את זה?"**, and the old
in-point of 194.86 landed inside the decay of "אבל". What played was the wreck
of a word and then the question — two things at once, which is exactly what it
sounded like.

Measured at 5ms, the head of that question is unambiguous:

    194.82-194.88  "אבל" decaying, -31 → -46 dB
    194.88-194.95  silence, -46 dB down to a -57 dB floor
    194.955        "איך" starts, -28 dB

So the in-point is **194.88**: the whole 0.07s crossfade lands inside that
silence, and the question opens at full level on its own first word with nothing
of "כן, אבל" left. The out-point moves 196.05 → 196.03, stopping just short of
the next voice's onset at 196.04.

Verified on the cut: her sentence decays through the crossfade to a -57 dB floor
and "איך" starts 0.025s later.

The two splice improvements from v19 stay — `repeat` ends in the pause after
"עצמו" instead of 0.02s into her next sentence, and her answer starts from the
silence before "תראה" instead of 0.2s inside the word, so it is whole and
captioned.

## What the residual test did and did not prove

The sample-aligned subtraction in v19 (residual 66.5 dB down) was sound and
still holds: the reel carries that span exactly as the broadcast has it. What it
proved was that the edit added nothing *within* the span — not that the span
began in the right place. The in-point was the fault, and a subtraction against
the source cannot see an in-point, because both sides move together. Worth
remembering: that test rules out corruption, never bad framing.

140.50s of voice, 4389 frames.

146.3s (2:26), 4389 frames, -13.7 LUFS, 0 samples of A/V lag including across the restored question at 126s.

---

# v21 — the crossfade was playing the thing the cut removed

v20 put the in-point at 194.88 on the grounds that 194.880-194.950 measures as
silence, -46 dB falling to a -57 dB floor. It does. But the first half of that
window is not silence, it is the **voiced decay of "אבל"** — and a 0.07s fade
starting at 194.88 reaches back and plays it. Traced on the v20 file itself, in
the gap before his first word:

    reel 125.920  f0 174 Hz  conf 0.50  -41.0 dB
    reel 125.940  f0 178 Hz  conf 0.48  -43.5 dB

A voiced male remnant, 25 dB under the speech either side but sitting in the one
gap where nothing else is sounding, which is precisely where a thing that quiet
gets heard. The cut had removed the word; the crossfade was putting a piece of
it back.

Two changes:

- **`cut.py` takes a per-splice crossfade.** `XF_BY` overrides the global 0.07
  per segment id, and the fade windows are built inside the loop instead of once
  outside it. Everything not named in `XF_BY` is unchanged.
- **`q3` uses `XF_BY["q3"] = 0.02`, in-point 194.94.** 194.94 is on the floor
  itself, past the decay, and the short fade means his first word at 194.955 is
  not faded in to get there — a 0.07s fade from that point would have covered
  55ms of it.

Traced again on the new cut, the same gap:

    reel 125.920  -51.4 dB   conf 0.41   (noise floor, no stable period)
    reel 125.930  -50.7 dB   conf 0.38
    reel 125.950  -37.0 dB   his first word begins
    reel 125.970  f0 138 Hz  conf 0.74  -31.8 dB

The floor is 8-10 dB lower than it was and carries no voiced period. Her
sentence decays, there is a clean gap, and the question starts.

## The general lesson

Choosing an in-point by the level in the window before the first word is not
enough: an equal-power fade makes that window audible, so the window has to be
judged on what it *contains*, not what it measures. Where a quiet window is
shorter than the fade, shorten the fade.

140.44s of voice, 4387 frames.

146.2s (2:26), 4387 frames, -13.7 LUFS, 0 samples of A/V lag including across the question at 126s.
