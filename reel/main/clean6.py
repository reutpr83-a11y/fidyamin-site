#!/usr/bin/env python3
"""Clean the reel's voice track.

Three things, in this order, and nothing else:

  1. highpass 90 Hz + narrow notches at 50 and 100 Hz.
     Wind, handling and mains hum. This is the loudest part of the
     background and none of it is her voice.
  2. a parallel spectral denoiser at half strength, profiled on a real
     0.8s gap in the reel rather than guessed. Half strength on purpose:
     at full strength the residue turns into musical noise, which is the
     metallic artefact this is meant to remove. The dry path is delayed to
     match the denoiser's 25 ms latency so the two sum instead of combing.
  3. a downward expander that only acts below -38 dB, so the background
     falls in the gaps between phrases and her voice is untouched.

Then loudnorm, and the 25 ms of latency is trimmed off the head so the
result is sample aligned with the picture.
"""
import subprocess, sys, os

SRC = sys.argv[1] if len(sys.argv) > 1 else "audio6.wav"
DST = sys.argv[2] if len(sys.argv) > 2 else "audio6_clean.wav"

NOISE_START, NOISE_END = 31.90, 32.70   # a measured gap between phrases
LATENCY = "1200S"                          # afftdn, 1200 samples at 48 kHz
WET = 0.65

HUM = ("highpass=f=90:poles=2,"
       "equalizer=f=50:t=q:w=6:g=-24,"
       "equalizer=f=100:t=q:w=6:g=-18")
EXPAND = ("compand=attacks=0.015:decays=0.20:"
          "points=-90/-105|-50/-62|-38/-44|-22/-22|0/0")
LOUD = "loudnorm=I=-14:TP=-1.5:LRA=11"

dur = float(subprocess.run(
    ["ffprobe", "-v", "error", "-show_entries", "format=duration",
     "-of", "csv=p=0", SRC], capture_output=True, text=True).stdout.strip())

fc = (
    f"[0:a]{HUM},asplit=2[d][w];"
    f"[d]adelay={LATENCY}:all=1[dd];"
    f"[w]asendcmd=c='{NOISE_START} afftdn sn start; {NOISE_END} afftdn sn stop',"
    f"afftdn=nr=8[wd];"
    f"[dd][wd]amix=inputs=2:weights={1-WET} {WET}:normalize=0[m];"
    f"[m]atrim=start=0.025,asetpts=N/SR/TB,{EXPAND},{LOUD},"
    f"asetpts=N/SR/TB,apad,atrim=0:{dur:.6f},asetpts=N/SR/TB[out]"
)
subprocess.run(["ffmpeg", "-v", "error", "-i", SRC, "-filter_complex", fc,
                "-map", "[out]", "-c:a", "pcm_s16le", "-ar", "48000",
                "-ac", "2", DST, "-y"], check=True)
print(DST, "written")
