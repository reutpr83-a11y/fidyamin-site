#!/usr/bin/env python3
"""Voice plus score, with the ducking BRAND.md asks for.

The music sits about 10dB down whenever she is speaking and comes back up in
the gaps, which is what lets a bed exist under a talking head without fighting
it. The envelope is taken from her own track rather than from the caption
times, so it follows breaths and not just words.

Attack is fast and release is slow: the music must be out of the way before
the syllable lands, and must not pump back up between two words of a sentence."""
import os, subprocess, wave
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
SR = 48000
DUCK_DB = 10.0
ATT, REL = 0.08, 0.55          # seconds

def read(p):
    w = wave.open(p, "rb")
    n, ch = w.getnframes(), w.getnchannels()
    x = np.frombuffer(w.readframes(n), "<i2").astype(np.float32) / 32768
    w.close()
    return x.reshape(-1, ch) if ch > 1 else x.reshape(-1, 1)

voice = read(os.path.join(HERE, "audio6.wav"))
music = read(os.path.join(HERE, "music6.wav"))
n = max(len(voice), len(music))
def pad(x):
    if len(x) >= n: return x[:n]
    return np.vstack([x, np.zeros((n - len(x), x.shape[1]), np.float32)])
voice, music = pad(voice), pad(music)

# how loud is she, smoothed
env = np.abs(voice).max(1)
win = int(0.03 * SR)
env = np.convolve(env, np.ones(win) / win, mode="same")
thresh = np.percentile(env[env > 1e-4], 55) if (env > 1e-4).any() else 1e-3
speaking = (env > thresh * 0.6).astype(np.float32)

# one pole follower, fast down and slow up
g = np.empty(n, np.float32)
a_att = np.exp(-1.0 / (ATT * SR)); a_rel = np.exp(-1.0 / (REL * SR))
cur = 0.0
for i in range(n):
    tgt = speaking[i]
    a = a_att if tgt > cur else a_rel
    cur = tgt + (cur - tgt) * a
    g[i] = cur
duck = 10 ** (-DUCK_DB * g / 20.0)

mix = voice + music * duck[:, None] * 0.55
peak = np.max(np.abs(mix))
if peak > 0.97: mix *= 0.97 / peak

out = np.empty(n * 2, np.float32)
out[0::2] = mix[:, 0]; out[1::2] = mix[:, min(1, mix.shape[1] - 1)]
w = wave.open(os.path.join(HERE, "mix_raw.wav"), "wb")
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(out, -1, 1) * 32767).astype("<i2").tobytes()); w.close()

subprocess.run(["ffmpeg", "-y", "-v", "error", "-i", os.path.join(HERE, "mix_raw.wav"),
    "-af", "loudnorm=I=-14:TP=-1.5:LRA=11", "-c:a", "pcm_s16le", "-ar", "48000", "-ac", "2",
    os.path.join(HERE, "audio6_music.wav")], check=True)
print("audio6_music.wav  %.2fs   music ducked %.0f dB under speech (%.0f%% of the reel)"
      % (n / SR, DUCK_DB, 100 * speaking.mean()))
