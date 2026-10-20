# Efectos de sonido sintetizados (originales) colocados según events.json
import numpy as np, json, sys
from scipy.io import wavfile
from scipy.signal import butter, sosfilt

SR = 44100
OUT = sys.argv[1]
d = json.load(open("events.json")); T = d["total"]
N = int(SR * T); out = np.zeros((N, 2))
rng = np.random.default_rng(11)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, hi], 'band', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)

def whoosh(dur=.45):
    n = int(dur*SR); t = np.linspace(0, 1, n)
    noise = rng.standard_normal(n)
    sig = np.zeros(n); seg = 512
    for i in range(0, n, seg):  # barrido de filtro
        f = 400 + 3500*np.sin(np.pi*t[i])**1.5
        sig[i:i+seg] = bp(noise[i:i+seg+256], f*.6, min(f*1.6, 20000))[:len(sig[i:i+seg])]
    return sig*np.sin(np.pi*t)**2*.5
def pop(f=520):
    n = int(.14*SR); tt = np.arange(n)/SR
    fr = f*(1+1.2*np.exp(-tt*60))
    return np.sin(2*np.pi*np.cumsum(fr)/SR)*np.exp(-tt*32)*.55
def tick():
    n = int(.05*SR); tt = np.arange(n)/SR
    return (np.sin(2*np.pi*2400*tt)+.4*rng.standard_normal(n))*np.exp(-tt*120)*.22
def ding():
    n = int(.9*SR); tt = np.arange(n)/SR
    s = sum(g*np.sin(2*np.pi*f*tt) for f, g in [(1318, 1), (1976, .45), (2637, .2)])
    return s*np.exp(-tt*5)*np.minimum(1, tt/.004)*.22
def swish():
    n = int(.25*SR); t = np.linspace(0, 1, n)
    return bp(rng.standard_normal(n), 2500, 9000)*np.sin(np.pi*t)**3*.35
def riser():
    n = int(1.4*SR); tt = np.arange(n)/SR; t = tt/tt[-1]
    s = np.sin(2*np.pi*np.cumsum(180+900*t**2)/SR)*.25 + lp(rng.standard_normal(n), 3000)*.15*t
    s *= t**2; s[-int(.03*SR):] *= np.linspace(1, 0, int(.03*SR))
    return s*.6

GEN = {"whoosh": whoosh, "pop": lambda: pop(480), "pop2": lambda: pop(700), "tick": tick, "ding": ding, "swish": swish}
for t, k in d["events"]:
    if k == "riser": continue
    x = GEN[k](); i = int(t*SR)
    if k == "whoosh": i = max(0, i-int(.12*SR))
    x = x[:max(0, N-i)]
    pan = rng.uniform(-.3, .3)
    out[i:i+len(x), 0] += x*(1-pan); out[i:i+len(x), 1] += x*(1+pan)
# boom de impacto suave en el gancho
n = int(.6*SR); tt = np.arange(n)/SR
boom = np.sin(2*np.pi*np.cumsum(60+80*np.exp(-tt*20))/SR)*np.exp(-tt*6)*.6
out[:n] += boom[:, None]
wavfile.write(OUT, SR, (np.clip(out, -1, 1)*32767).astype(np.int16))
