import math, wave, array, random, os
OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'score.wav')
SR = 44100
DUR = 223.4
N = int(SR*DUR)
random.seed(7)

# --- key accent moments (scene starts of major beats) ---
HITS = [0.0, 4.2, 9.4, 14.8, 28.0, 33.4, 50.4, 72.6, 91.2, 97.2, 112.6,
        117.0, 121.2, 130.4, 135.8, 150.2, 165.6, 171.2, 180.2, 186.6,
        192.8, 197.4, 204.0, 210.2, 218.8]
# --- intensity curve: (time, level) ---
CURVE = [(0,0.35),(14,0.45),(33,0.55),(90,0.62),(112,0.68),(117,0.85),(130,0.72),
         (135,0.70),(165,0.86),(186,0.92),(197,0.80),(204,1.0),(210,0.60),(218.8,0.75),(223.4,0.0)]
def curve(t):
    for i in range(len(CURVE)-1):
        t0,v0=CURVE[i]; t1,v1=CURVE[i+1]
        if t0<=t<=t1:
            p=(t-t0)/(t1-t0) if t1>t0 else 0
            p=p*p*(3-2*p)
            return v0+(v1-v0)*p
    return CURVE[-1][1]

buf = array.array('h', bytes(2*2*N))   # stereo int16

# pre-compute pulse train times
pulses=[]
t=1.0
while t < DUR-2:
    pulses.append(t)
    t += 2.0 if t < 160 else 1.3
pulse_idx = 0

# noise state for one-pole lowpass
nz = 0.0
ph1=ph2=ph3=ph4=0.0
w1=2*math.pi*55.0/SR; w2=2*math.pi*82.5/SR; w3=2*math.pi*110.0/SR; w4=2*math.pi*36.7/SR

# active envelopes
active_pulses=[]   # [start_sample]
active_hits=[]
pn = [int(p*SR) for p in pulses]
hn = [int(h*SR) for h in HITS]
pi_=0; hi_=0

for i in range(N):
    t = i/SR
    lv = curve(t)
    # drone
    ph1+=w1; ph2+=w2; ph3+=w3; ph4+=w4
    lfo = 0.5+0.5*math.sin(2*math.pi*t/17.0)
    lfo2= 0.5+0.5*math.sin(2*math.pi*t/11.0+1.3)
    s  = 0.34*math.sin(ph1)*(0.55+0.45*lfo)
    s += 0.16*math.sin(ph2)*(0.40+0.60*lfo2)
    s += 0.10*math.sin(ph3)*(0.30+0.70*lfo)
    s += 0.07*math.sin(ph4)
    # air texture (lowpassed noise)
    nz = nz*0.9985 + (random.random()*2-1)*0.0015
    s += nz*3.2
    s *= lv
    # pulses
    while pi_ < len(pn) and pn[pi_] <= i:
        active_pulses.append(pn[pi_]); pi_+=1
    for st in active_pulses[:]:
        d = (i-st)/SR
        if d > 0.9: active_pulses.remove(st); continue
        env = math.exp(-d*5.2)*(1-math.exp(-d*400))
        s += 0.30*env*math.sin(2*math.pi*55.0*d)*lv
        s += 0.10*env*math.sin(2*math.pi*110.0*d)*lv
    # hits
    while hi_ < len(hn) and hn[hi_] <= i:
        active_hits.append(hn[hi_]); hi_+=1
    for st in active_hits[:]:
        d = (i-st)/SR
        if d > 2.4: active_hits.remove(st); continue
        env = math.exp(-d*1.9)*(1-math.exp(-d*220))
        f = 44.0*math.exp(-d*0.55)
        s += 0.34*env*math.sin(2*math.pi*f*d)
        s += 0.05*env*math.exp(-d*7)*(random.random()*2-1)
    # global fades
    if t < 2.0: s *= t/2.0
    if t > DUR-3.5: s *= max(0.0,(DUR-t)/3.5)
    # soft clip
    s = math.tanh(s*1.05)*0.50
    v = int(s*32767)
    if v>32767: v=32767
    if v<-32768: v=-32768
    buf[2*i]=v; buf[2*i+1]=v

w = wave.open(OUT,'wb')
w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
w.writeframes(buf.tobytes()); w.close()
print("score.wav written", N, "samples")
