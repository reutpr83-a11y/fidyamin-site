# The 90FM interview — source

`radio-audio.m4a` is the audio of the broadcast, copied out of the uploaded
`.mov` with `-c:a copy`, so it is the original AAC stream: 271.8s, 48 kHz
stereo, 64 kbps. No re-encode, nothing lost relative to what was uploaded.

The video was 640x360 at 324 kbps and shows the studio webcam of the host
alone, under the station's own burned in lower thirds and news ticker. She is
on the phone and never appears. That is why the reel is built on a designed
ground rather than on this picture — see `reel/radio/`.

## What is where

Measured, not guessed: frames every 20 ms, F0 by autocorrelation, speaker by
pitch (the host sits low, she sits high), smoothed over 0.6s and merged into
turns. `turns.json` carries the result as `[start, end, speaker]` with
1 = host, 2 = Greenberg.

| | |
|---|---|
| 0 - 78s | the news bulletin. Mixed voices, male dominant. Not our material |
| 78 - 271.8s | the interview |

Inside the interview she holds 190 of the 194 seconds. The host's turns are
few and short — roughly 105.9-108.8, 146.8-148.0, 196.3-197.3, 218.7-220.6 and
257.9-262.4 — which suits the question-card design: each one is a beat, not a
paragraph.

Per ten second block, the share of voiced frames above 165 Hz jumps from about
40% before 78s to over 90% after it. That is the cleanest boundary in the file.
