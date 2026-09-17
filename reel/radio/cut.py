# -*- coding: utf-8 -*-
"""Cut the 17 stretches and splice them, then write the reel clock map."""
import json, subprocess, os
import numpy as np
import blocks

SR = 48000
def read(p):
    raw = subprocess.run(["ffmpeg","-v","error","-i",p,"-map","0:a","-ac","2",
                          "-ar",str(SR),"-f","f32le","-"],capture_output=True).stdout
    return np.frombuffer(raw,np.float32).reshape(-1,2).copy()

x = read(blocks.SRC)
XF = blocks.XF
nxf = int(XF*SR)
fade_out = np.cos(np.linspace(0,np.pi/2,nxf))[:,None]   # equal power
fade_in  = np.sin(np.linspace(0,np.pi/2,nxf))[:,None]

out = np.zeros((0,2),np.float32)
starts = []
for i,(name,a,b,turns) in enumerate(blocks.SEGS):
    seg = x[int(round(a*SR)):int(round(b*SR))].copy()
    if i == 0:
        starts.append(0.0)
        out = seg
        continue
    starts.append((len(out)-nxf)/SR)
    head = out[-nxf:]*fade_out + seg[:nxf]*fade_in
    out = np.concatenate([out[:-nxf], head, seg[nxf:]])

dur = len(out)/SR
# written with the wave module, not piped into ffmpeg: a raw f32le pipe was
# being read back as mono, which doubled the length and silently desynced
# everything downstream that reads voice.wav.
import wave as wavemod
w = wavemod.open("voice.wav","wb")
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes((np.clip(out,-1,1)*32767).astype("<i2").tobytes())
w.close()
m = {"xf":XF,"dur":dur,"starts":starts,
     "segs":[{"id":n,"in":a,"out":b,"start":s,"len":b-a,
              "turns":[{"speaker":sp,"words":[[t,w] for t,w in ws]} for sp,ws in turns]}
             for (n,a,b,turns),s in zip(blocks.SEGS,starts)]}
json.dump(m,open("map.json","w"),ensure_ascii=False,indent=1)
print("voice.wav %.3fs, %d segments"%(dur,len(blocks.SEGS)))
for s in m["segs"]:
    print("  %-8s reel %7.2f  src %7.2f-%7.2f"%(s["id"],s["start"],s["in"],s["out"]))
