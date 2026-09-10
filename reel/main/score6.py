#!/usr/bin/env python3
"""Score for the main reel.

BRAND.md specifies one and the reel has been running without it: minimal
investigative editorial, 84 BPM, a soft low pulse, dry minimal percussion, one
clean synth layer, and a build made of layers arriving rather than of anything
getting louder. No vocals, no melody, no trailer drums, no heartbeat, no sting.

Six distinct effects in the whole piece and nothing else: a tick on each of the
four figure reveals, one low layer arriving at the turn from data to meaning,
and one resolve under the closing line.

The layers thin out before the demand, because shooting-script.md is right that
the short silence there is worth more than any effect.

Structure is read from map6.json, so the score follows the cut rather than a
table that has to be kept in step with it by hand."""
import json, os, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR, BPM = 48000, 84.0
BEAT = 60.0 / BPM

m = json.load(open(os.path.join(HERE, "map6.json")))
starts, durs, roles = m["starts"], m["durs"], m["roles"]
AT = {r: s for r, s in zip(roles, starts)}
TAIL_V = 26 / 30.0
BODY = m["total"] + TAIL_V
DUR = BODY + 4.9 - 0.5              # picture plus the card, minus the dissolve
N = int((DUR + 1.4) * SR)

L = np.zeros(N); R = np.zeros(N)
TURN = AT["המציאות"]                 # data becomes meaning
QUIET_A, QUIET_B = AT["הפנייה"], AT["מנהיגות"]   # the address to the four
DEMAND = AT["מנהיגות"]

def add(buf, start, sig, gain=1.0):
    i = int(start * SR)
    if i < 0: sig = sig[-i:]; i = 0
    j = min(N, i + len(sig))
    if j > i: buf[i:j] += sig[:j - i] * gain

def env(n, attack, decay, hold=0.0, curve=2.5):
    a = int(attack * SR); h = int(hold * SR); d = max(1, n - a - h)
    e = np.empty(n)
    e[:a] = np.linspace(0, 1, a) ** 1.4 if a else 1
    if h: e[a:a + h] = 1.0
    e[a + h:] = np.linspace(1, 0, d) ** curve
    return e

def sine(f, n, phase=0.0):
    return np.sin(2 * np.pi * f * np.arange(n) / SR + phase)

def lp(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x); acc = 0.0
    for i in range(len(x)):
        acc = (1 - a) * x[i] + a * acc; y[i] = acc
    return y

def fade(x, ms=8):
    n = int(ms / 1000 * SR)
    if len(x) > 2 * n:
        x[:n] *= np.linspace(0, 1, n); x[-n:] *= np.linspace(1, 0, n)
    return x

def hush(ts):
    """the two places the score steps back"""
    if QUIET_A - 0.2 <= ts < QUIET_B - 0.2: return 0.62      # under the names
    if DEMAND - 0.9 <= ts < DEMAND + 1.4:   return 0.0       # before the demand
    return 1.0

# 1. pulse, the clock of the piece
for b in range(int((DUR + 0.5) / BEAT)):
    ts = b * BEAT
    n = int(0.42 * SR)
    body = (sine(55.0, n) * 0.70 + sine(110.0, n) * 0.26 +
            sine(165.0, n) * 0.11 + sine(220.0, n) * 0.06) * env(n, 0.006, 0.41, curve=3.2)
    ramp = min(1.0, 0.25 + 0.75 * ts / 5.0)
    g = (0.30 if b % 4 == 0 else 0.19) * ramp * max(0.45, hush(ts))
    add(L, ts, body, g); add(R, ts, body, g)

# 2. sub floor, arriving at the turn
n = int((DUR + 1.4 - TURN) * SR)
sub = sine(41.0, n) * 0.5 + sine(82.0, n) * 0.08
ramp = np.clip(np.linspace(0, (DUR + 1.4 - TURN) / 3.0, n), 0, 1)
add(L, TURN, sub * ramp, 0.085); add(R, TURN, sub * ramp, 0.085)

# 3. ticks, dry and off the downbeat, entering after the opening
n = int(0.05 * SR)
noise = np.random.default_rng(7).standard_normal(n)
tick = fade(lp(noise, 5200) - lp(noise, 1400), 4) * env(n, 0.001, 0.049, curve=6)
tick /= np.max(np.abs(tick))
b = int(AT["הראיות"] / BEAT) + 1
while b * BEAT < DUR - 0.3:
    ts = b * BEAT
    if b % 4 == 2:
        add(L, ts, tick, 0.055 * hush(ts)); add(R, ts, tick, 0.048 * hush(ts))
    b += 1

# 4. the six effects: one accent on each figure reveal
panel = json.load(open(os.path.join(HERE, "panel6.json")))
dim = {int(k): v for k, v in panel["dim"].items()}
rises = []
prev = 0.0
for f in sorted(dim):
    if prev < 0.02 <= dim[f]: rises.append(f / 30.0)
    prev = dim[f]
n2 = int(0.09 * SR)
acc = fade(lp(np.random.default_rng(11).standard_normal(n2), 3000), 5) * env(n2, 0.002, 0.088, curve=5)
acc /= np.max(np.abs(acc))
for ts in rises[:4]:
    add(L, ts, acc, 0.075); add(R, ts, acc, 0.068)

# 5. pad, one clean sustained layer, no tune, chord changes on act boundaries
CH = [(0.0, [220.00, 261.63, 329.63]), (AT["הראיות"], [196.00, 261.63, 329.63]),
      (TURN, [174.61, 261.63, 349.23]), (AT["פחות"], [164.81, 246.94, 329.63]),
      (QUIET_A, [174.61, 220.00, 349.23]), (DEMAND, [220.00, 261.63, 329.63])]
for i, (start, freqs) in enumerate(CH):
    stop = CH[i + 1][0] if i + 1 < len(CH) else DUR + 1.4
    n = int((stop - start + 2.2) * SR)
    if n <= 0: continue
    e = env(n, 1.1, 1.9, hold=max(0.0, (stop - start) - 1.1), curve=1.6)
    v = np.zeros(n)
    for k, f in enumerate(freqs):
        v += sine(f, n, phase=k * 1.7) * (0.5 / (k + 1))
        v += sine(f * 2.0, n, phase=k) * (0.10 / (k + 1))
    v = lp(v, 1800) * e
    ts = np.arange(n) / SR + start
    g = np.array([0.055 * hush(x) for x in ts[::256]]).repeat(256)[:n]
    add(L, start, v * g); add(R, start, v * np.roll(g, 400))

# 6. the resolve, under the closing line
n = int(3.4 * SR)
res = (sine(110.0, n) * 0.5 + sine(164.81, n) * 0.3 + sine(220.0, n) * 0.2)
add(L, DUR - 3.1, lp(res, 1200) * env(n, 0.9, 2.4, curve=1.8), 0.075)
add(R, DUR - 3.1, lp(res, 1200) * env(n, 0.9, 2.4, curve=1.8), 0.075)

mx = max(np.max(np.abs(L)), np.max(np.abs(R)), 1e-9)
L, R = L / mx * 0.82, R / mx * 0.82
out = np.empty(N * 2, np.float32); out[0::2] = L; out[1::2] = R
w = wave.open(os.path.join(HERE, "music6.wav"), "wb")
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes()); w.close()
print("music6.wav  %.2fs   pulse from 0, sub at %.1f, ticks from %.1f, %d figure accents"
      % (N / SR, TURN, AT["הראיות"], len(rises[:4])))
