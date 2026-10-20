# Efectos de sonido sintetizados (originales), sincronizados con la animación.
# Uso (desde public/): python3 ../scripts/sfx2.py sfx.wav   -> lee events.json
import numpy as np, json, sys
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
OUT = sys.argv[1]
d = json.load(open("events.json")); T = d["total"]; S = d["starts"]
BIG = json.load(open("timing.json")).get("bigAt")  # momento exacto en que la voz dice cada palabra grande
N = int(SR * T)
rng = np.random.default_rng(7)

def bp(x, lo, hi): return sosfilt(butter(2, [lo, min(hi, 20000)], 'band', fs=SR, output='sos'), x)
def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
def tt_(n): return np.arange(n) / SR

def whoosh(dur=.5, lo=1, hi=5, gain=.5):
    """Ruido que barre de grave a agudo con envolvente suave (sin clics)."""
    n = int(dur * SR); t = np.linspace(0, 1, n); noise = rng.standard_normal(n)
    edges = [150 * 2 ** k for k in range(7)]  # 150..9600
    bands = [bp(noise, edges[k], edges[k + 1]) for k in range(6)]
    pos = lo + (hi - lo) * t ** 1.4
    sig = sum(b * np.exp(-((pos - (k + .5)) ** 2) / 1.1) for k, b in enumerate(bands))
    return sig * np.sin(np.pi * t) ** 2 * gain

def whip(): return whoosh(.55, .5, 5.2, .75)          # transición entre escenas
def enter(): return whoosh(.45, 1, 4, .42)           # entrada de objetos
def impact():                                         # golpe de la palabra grande
    n = int(.8 * SR); t = tt_(n)
    sub = np.sin(2 * np.pi * np.cumsum(42 + 90 * np.exp(-t * 14)) / SR) * np.exp(-t * 6)
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 22) * .35
    click = lp(rng.standard_normal(n), 5000) * np.exp(-t * 90) * .45
    return (sub * .8 + body + click) * .9
def sparkle():                                        # brillo de confeti
    n = int(.55 * SR); x = np.zeros(n)
    for _ in range(9):
        i = int(rng.uniform(0, .3) * SR); f = rng.choice([2093, 2637, 3136, 3951, 4699])
        m = n - i; t = tt_(m); x[i:] += np.sin(2 * np.pi * f * t) * np.exp(-t * 24) * rng.uniform(.4, 1)
    return x * .13
def pop2(f=620):                                      # burbuja
    n = int(.16 * SR); t = tt_(n)
    fr = f * (1 + .9 * np.exp(-t * 45))
    return np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 26) * .5
def boing():                                          # sticker que rebota
    n = int(.22 * SR); t = tt_(n); fr = 380 + 700 * (t / t[-1]) ** .6
    return (np.sin(2 * np.pi * np.cumsum(fr) / SR) * np.exp(-t * 14) + .25 * np.sin(2 * np.pi * 2 * np.cumsum(fr) / SR) * np.exp(-t * 20)) * .35
def tick():                                           # clic de interfaz
    n = int(.06 * SR); t = tt_(n); f = rng.choice([1800, 2200, 2600])
    return (np.sin(2 * np.pi * f * t) * .6 + hp(rng.standard_normal(n), 3000) * .35) * np.exp(-t * 110) * .35
def tap():                                            # toque de dedo
    n = int(.09 * SR); t = tt_(n)
    return (np.sin(2 * np.pi * 320 * t) * np.exp(-t * 55) + lp(rng.standard_normal(n), 2500) * np.exp(-t * 90) * .5) * .6
def ding(f=1568):                                     # campanita de cristal
    n = int(1.4 * SR); t = tt_(n)
    parts = [(1, 1, 4), (2.01, .5, 6), (3.02, .28, 9), (4.2, .14, 13)]
    s = sum(g * np.sin(2 * np.pi * f * k * t) * np.exp(-t * dk) for k, g, dk in parts)
    return s * np.minimum(1, t / .003) * .26
def stamp():                                          # sello "$0 SUELDO"
    n = int(.9 * SR); t = tt_(n)
    thud = np.sin(2 * np.pi * np.cumsum(55 + 110 * np.exp(-t * 30)) / SR) * np.exp(-t * 9)
    ring = (np.sin(2 * np.pi * 1180 * t) + .6 * np.sin(2 * np.pi * 1870 * t)) * np.exp(-t * 11) * .25
    crack = hp(rng.standard_normal(n), 1500) * np.exp(-t * 70) * .5
    return (thud * .9 + ring + crack) * .95
def boom():                                           # arranque suave
    n = int(.7 * SR); t = tt_(n)
    return np.sin(2 * np.pi * np.cumsum(50 + 70 * np.exp(-t * 18)) / SR) * np.exp(-t * 5) * .5

GEN = {"whoosh": enter, "whip": whip, "pop": impact, "sparkle": sparkle, "pop2": pop2,
       "boing": boing, "tick": tick, "tap": tap, "ding": ding, "stamp": stamp,
       "swish": lambda: whoosh(.3, 3, 5.5, .4), "boom": boom}

ev = [(t, k) for t, k in d["events"] if k != "riser" and not (BIG and k == "pop")]
if BIG: ev += [(t, "pop") for t in BIG]
ev.append((0.0, "boom"))
for a in S[1:]:
    ev.append((a - .27, "whip"))                       # pico justo cuando la franja cubre la pantalla
# destellos de confeti tras cada impacto de palabra grande
ev += [(t + .04, "sparkle") for t in (BIG or [t for t, k in d["events"] if k == "pop"])]
# stickers / elementos extra (mismos tiempos que Reel.tsx)
st = {0: [.6, .9], 1: [.5, 1.0], 2: [.5, 1.2], 3: [.5, 2.1], 4: [.5, 2.0], 5: [1.0, 1.3], 6: [.8]}
for i, offs in st.items(): ev += [(S[i] + o, "boing") for o in offs]
ev.append((S[1] + .7, "pop2"))                          # badge 99+
ev += [(S[5] + .6, "pop2"), (S[5] + .95, "pop2"), (S[5] + 2.2, "stamp")]
ev += [(S[6] + o, "pop2") for o in (1.8, 1.95, 2.1)]
k = 0
while S[6] + 2.2 + k * .7 < T - .5:
    ev.append((S[6] + 2.2 + k * .7, "tap")); k += 1

dry = np.zeros((N, 2))
for t, k in sorted(ev):
    x = GEN[k](); i = int(max(0, t) * SR)
    if i >= N: continue
    x = x[:N - i]
    pan = rng.uniform(-.35, .35) if k not in ("pop", "stamp", "boom", "whip") else 0
    if k in ("whip", "whoosh"):                          # barrido estéreo
        g = np.linspace(-.6, .6, len(x)) * (1 if rng.random() > .5 else -1)
        dry[i:i + len(x), 0] += x * (1 - g) / 1.2; dry[i:i + len(x), 1] += x * (1 + g) / 1.2
    else:
        dry[i:i + len(x), 0] += x * (1 - pan); dry[i:i + len(x), 1] += x * (1 + pan)

# reverb corta (cola sintética) para dar espacio
m = int(.7 * SR); ir = rng.standard_normal((m, 2)) * np.exp(-tt_(m) * 7)[:, None]
ir = lp(ir.T, 6000).T; ir[0] = 0
wet = np.stack([fftconvolve(dry[:, c], ir[:, c])[:N] for c in range(2)], 1) * .06
out = dry + wet
out = np.tanh(out * 1.1) / np.tanh(1.1)                # saturación suave anti-clip
out *= .5 / max(1e-9, np.abs(out).max())
wavfile.write(OUT, SR, (out * 32767).astype(np.int16))
print("sfx ok", len(ev), "eventos, pico", float(np.abs(out).max()))
