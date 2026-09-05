#!/usr/bin/env python3
"""
Score for the Harish budget explainer.

Minimal investigative editorial: 84 BPM, a soft low pulse, dry minimal
percussion, one clean synth layer, and a build made of layers arriving
rather than of anything getting louder. No vocals, no melody, no trailer
drums, no heartbeat, no news sting.

Six distinct effects in the whole piece and nothing else:
  four small ticks on the four figure reveals,
  one low layer arriving when the film turns from data to meaning,
  one clean resolve under the closing line.

Layers thin out under the council screen so the type carries that beat.
Output is a stereo 48k WAV; ffmpeg does the loudness pass afterwards.
"""
import math, struct, wave
import numpy as np

SR = 48000
BPM = 84.0
BEAT = 60.0 / BPM               # 0.714s

# scene starts, from script.js
SCENES = [
    ('hook', 0.0, 4.2), ('eng', 4.2, 3.8), ('san', 8.0, 3.8), ('col', 11.8, 2.8),
    ('life', 14.6, 4.2), ('msg1', 18.8, 4.2), ('growth', 23.0, 3.6), ('msg2', 26.6, 4.2),
    ('msg3', 30.8, 4.4), ('service', 35.2, 4.0), ('ask', 39.2, 4.8), ('end', 44.0, 5.2),
]
AT = {n: s for n, s, d in SCENES}
DUR = 49.2
TAIL = 1.4                      # room for the resolve to decay
N = int((DUR + TAIL) * SR)

t = np.arange(N) / SR
L = np.zeros(N)
R = np.zeros(N)


def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i < 0:
        sig = sig[-i:]
        i = 0
    j = min(N, i + len(sig))
    if j > i:
        buf[i:j] += sig[:j - i] * gain


def env(n, attack, decay, hold=0.0, curve=2.5):
    """attack/hold/decay envelope in seconds"""
    a = int(attack * SR); h = int(hold * SR); d = max(1, n - a - h)
    e = np.empty(n)
    e[:a] = np.linspace(0, 1, a) ** 1.4 if a else 1
    if h: e[a:a + h] = 1.0
    e[a + h:] = np.linspace(1, 0, d) ** curve
    return e


def sine(f, n, phase=0.0):
    return np.sin(2 * np.pi * f * np.arange(n) / SR + phase)


def onepole_lp(x, cutoff):
    a = math.exp(-2 * math.pi * cutoff / SR)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc
        y[i] = acc
    return y


def fade(x, ms=8):
    n = int(ms / 1000 * SR)
    if len(x) > 2 * n:
        x[:n] *= np.linspace(0, 1, n)
        x[-n:] *= np.linspace(1, 0, n)
    return x


# ----------------------------------------------------------------- 1. pulse
# One soft low note on every beat. It is the clock of the piece.
# Level ramps in over the first two bars and never gets louder after that.
beats = int((DUR + 0.5) / BEAT)
for b in range(beats):
    ts = b * BEAT
    strong = (b % 4 == 0)
    n = int(0.42 * SR)
    e = env(n, 0.006, 0.41, curve=3.2)
    body = (sine(55.0, n) * 0.70 + sine(110.0, n) * 0.26 +
            sine(165.0, n) * 0.11 + sine(220.0, n) * 0.06) * e
    ramp = min(1.0, 0.25 + 0.75 * ts / 5.0)
    # thin out under the council screen so the type carries that beat
    duck = 0.66 if AT['ask'] - 0.2 <= ts < AT['end'] - 0.2 else 1.0
    g = (0.30 if strong else 0.19) * ramp * duck
    add(L, ts, body, g); add(R, ts, body, g)

# ----------------------------------------------------------------- 2. sub
# A continuous floor that arrives with the first central message and gives
# the second half its weight. Felt more than heard.
sub_start = AT['msg1']
n = int((DUR + TAIL - sub_start) * SR)
sub = sine(41.0, n) * 0.5 + sine(41.0 * 2, n) * 0.08
ramp = np.clip(np.linspace(0, (DUR + TAIL - sub_start) / 3.0, n), 0, 1)
# one extra low layer at the turn from data to meaning
deep = np.where(np.arange(n) / SR + sub_start >= AT['msg3'], 1.35, 1.0)
add(L, sub_start, sub * ramp * deep, 0.085); add(R, sub_start, sub * ramp * deep, 0.085)

# ----------------------------------------------------------------- 3. ticks
# Dry, tiny, off the downbeat. Enters after the opening so the hook is clean.
tick_from = AT['eng']
n = int(0.05 * SR)
rng = np.random.default_rng(7)
noise = rng.standard_normal(n)
tick = fade(onepole_lp(noise, 5200) - onepole_lp(noise, 1400), 4) * env(n, 0.001, 0.049, curve=6)
tick /= np.max(np.abs(tick))
b = int(tick_from / BEAT) + 1
while b * BEAT < DUR - 0.3:
    ts = b * BEAT
    if b % 4 == 2:                     # one per bar, on the third beat
        duck = 0.5 if AT['ask'] - 0.2 <= ts < AT['end'] - 0.2 else 1.0
        add(L, ts, tick, 0.055 * duck); add(R, ts, tick, 0.048 * duck)
    b += 1

# ----------------------------------------------------------------- 4. pad
# One clean sustained layer. It changes chord at section boundaries and
# does not carry a tune.
CHORDS = [
    (0.0,          [220.00, 261.63, 329.63]),   # A minor
    (AT['life'],   [196.00, 261.63, 329.63]),   # G add
    (AT['msg1'],   [174.61, 261.63, 349.23]),   # F
    (AT['msg3'],   [164.81, 246.94, 329.63]),   # E minor, the turn
    (AT['ask'],    [174.61, 220.00, 349.23]),   # F, thinner
    (AT['end'],    [220.00, 261.63, 329.63]),   # back to A minor for the resolve
]
for i, (start, freqs) in enumerate(CHORDS):
    stop = CHORDS[i + 1][0] if i + 1 < len(CHORDS) else DUR + TAIL
    n = int((stop - start + 2.2) * SR)
    if n <= 0:
        continue
    voice = np.zeros(n)
    for k, f in enumerate(freqs):
        voice += sine(f, n, phase=k * 1.7) * (0.6 ** k)
        voice += sine(f * 1.003, n, phase=k * 0.9) * (0.6 ** k) * 0.5   # slow beating
    voice = onepole_lp(voice, 1800) * 0.85 + onepole_lp(voice, 5200) * 0.15
    voice *= env(n, 1.6, min(2.0, (stop - start) * 0.5), hold=max(0.1, stop - start - 1.9), curve=1.6)
    g = 0.075
    if start == AT['ask']:
        g = 0.048                       # one layer down for the council screen
    if start == AT['msg3']:
        g = 0.092                       # the turn to meaning sits a little deeper
    add(L, start, voice, g * 1.00); add(R, start, voice, g * 0.94)

# ------------------------------------------------------- 5. figure impacts
# Four of them, one per figure reveal, small enough to feel like punctuation.
for name, gain in [('hook', 0.16), ('eng', 0.12), ('san', 0.12), ('col', 0.10)]:
    n = int(0.30 * SR)
    hit = (sine(72.0, n) * 0.66 + sine(108.0, n) * 0.20 +
           sine(216.0, n) * 0.10 + sine(432.0, n) * 0.04) * env(n, 0.003, 0.297, curve=4.0)
    add(L, AT[name] + 0.06, hit, gain); add(R, AT[name] + 0.06, hit, gain)
    add(L, AT[name] + 0.06, tick, gain * 0.55); add(R, AT[name] + 0.06, tick, gain * 0.48)

# ------------------------------------------------------------- 6. resolve
# A clean half second under the closing line. No boom.
res_at = DUR - 1.15
n = int(2.4 * SR)
res = np.zeros(n)
for k, f in enumerate([110.0, 220.0, 329.63]):
    res += sine(f, n, phase=k * 2.1) * (0.62 ** k)
res = (onepole_lp(res, 2000) * 0.86 + onepole_lp(res, 6000) * 0.14) * env(n, 0.02, 2.3, curve=2.0)
add(L, res_at, res, 0.10); add(R, res_at, res, 0.095)

# a last soft pulse note lands on the resolve, then the clock stops
n = int(0.7 * SR)
last = (sine(55.0, n) * 0.8 + sine(110.0, n) * 0.2) * env(n, 0.006, 0.69, curve=2.6)
add(L, res_at, last, 0.20); add(R, res_at, last, 0.20)

# ----------------------------------------------------------------- master
# Gentle top and tail, soft limiter, then ffmpeg does the loudness pass.
for buf in (L, R):
    fade(buf, 60)
mix = np.stack([L, R])
mix = np.tanh(mix * 1.25) / 1.25
peak = np.max(np.abs(mix))
mix = mix / peak * 0.82

inter = np.empty(N * 2)
inter[0::2] = mix[0]; inter[1::2] = mix[1]
data = (np.clip(inter, -1, 1) * 32767).astype('<i2').tobytes()

with wave.open('out/score.wav', 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
    w.writeframes(data)
print('wrote out/score.wav  %.2fs  peak %.3f' % (N / SR, peak))
