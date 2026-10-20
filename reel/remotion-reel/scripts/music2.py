# Música original con arreglo que crece escena por escena (pop/electrónico animado).
# Uso (desde public/): python3 ../scripts/music2.py <segundos> music.wav   -> lee timing.json
import numpy as np, json, sys
from scipy.io import wavfile
from scipy.signal import butter, sosfilt, fftconvolve

SR = 44100
T = float(sys.argv[1]); OUT = sys.argv[2]
S = json.load(open("timing.json"))["starts"]
N = int(SR * T)
rng = np.random.default_rng(5)
BPM = 118.0; BEAT = 60 / BPM; BAR = 4 * BEAT; STEP = BEAT / 4

def lp(x, f): return sosfilt(butter(2, f, 'low', fs=SR, output='sos'), x)
def hp(x, f): return sosfilt(butter(2, f, 'high', fs=SR, output='sos'), x)
def bp(x, lo, hi): return sosfilt(butter(2, [lo, min(hi, 20000)], 'band', fs=SR, output='sos'), x)
def mtof(m): return 440.0 * 2 ** ((np.asarray(m, float) - 69) / 12)
def saw(f, t, ph=0.0): return 2 * ((f * t + ph) % 1.0) - 1
def env_at(points):
    xs, ys = zip(*points); return np.interp(np.arange(N) / SR, xs, ys)

# --- estructura: intensidad de cada capa en el tiempo (s0..s6 = inicios de escena) ---
s = S + [T]
lay = {
    "pad":  env_at([(0, .9), (s[1], 1.0), (s[2], 1), (s[5], 1.15), (T - 1.8, 1), (T, 0)]),
    "arp":  env_at([(0, 0), (.6, 1.0), (s[1], 1.0), (s[2] - .3, .6), (s[2], .9), (s[5], 1), (T, 0)]),
    "kick": env_at([(0, 0), (s[1] - .02, 0), (s[1], .7), (s[2] - .02, .7), (s[2], 1), (T - 1.6, 1), (T - 1.5, 0), (T, 0)]),
    "hat":  env_at([(0, 0), (s[1], .5), (s[2], 1), (T - 1.6, 1), (T - 1.5, 0), (T, 0)]),
    "clap": env_at([(0, 0), (s[2] - .02, 0), (s[2], 1), (T - 1.6, 1), (T - 1.5, 0), (T, 0)]),
    "bass": env_at([(0, 0), (s[1] - .02, 0), (s[1], .6), (s[2], 1), (T - 1.6, 1), (T - 1.4, 0), (T, 0)]),
    "lead": env_at([(0, 0), (s[4] + 4.2, 0), (s[4] + 4.5, .7), (s[5] - .02, .7), (s[5], 1), (T - 1.6, 1), (T - 1.2, 0), (T, 0)]),
}

# acordes: Am - F - C - G (vi-IV-I-V), un compás cada uno
CH = [([57, 60, 64], 33), ([53, 57, 60], 29), ([60, 64, 67], 36), ([55, 59, 62], 31)]  # (tríada grave-media, raíz del bajo)
LEAD = [[76, 76, 79, 76, 74, 72, 74, 76], [77, 77, 81, 77, 76, 72, 76, 77],
        [79, 79, 76, 79, 76, 74, 72, 74], [74, 74, 79, 74, 71, 74, 76, 74]]
nbars = int(T / BAR) + 2

def add(buf, x, start, gain=1.0, pan=0.0):
    i = int(start * SR)
    if i >= N or i < 0: return
    x = x[:N - i]
    buf[i:i + len(x), 0] += x * gain * (1 - pan) / 1.0
    buf[i:i + len(x), 1] += x * gain * (1 + pan) / 1.0

pad = np.zeros((N, 2)); arp = np.zeros((N, 2)); bass = np.zeros((N, 2))
lead = np.zeros((N, 2)); drums = np.zeros((N, 2)); fx = np.zeros((N, 2))
kick_times = []

# --- sonidos ---
def kick():
    n = int(.42 * SR); t = np.arange(n) / SR
    f = 46 + 110 * np.exp(-t * 28)
    return (np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 7.5) + .25 * lp(rng.standard_normal(n), 3000) * np.exp(-t * 90)) * .95
def clap():
    n = int(.3 * SR); t = np.arange(n) / SR; x = bp(rng.standard_normal(n), 900, 4200)
    e = sum(np.exp(-np.clip(t - d, 0, None) * 60) * (t >= d) for d in (0, .011, .022)) * .6 + np.exp(-t * 14) * .35
    return x * e * .8
def hat(open_=False):
    n = int((.22 if open_ else .06) * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 7500) * np.exp(-t * (16 if open_ else 70)) * (.35 if open_ else .3)
def crash():
    n = int(1.6 * SR); t = np.arange(n) / SR
    return hp(rng.standard_normal(n), 4500) * np.exp(-t * 3.2) * .5
def pluck(f, dur=.34):
    n = int(dur * SR); t = np.arange(n) / SR
    x = (saw(f, t) + saw(f * 1.004, t, .3)) * .5
    x = lp(x, 3800)
    return x * np.exp(-t * 9) * np.minimum(1, t / .004) * .5
def leadn(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    vib = 1 + .004 * np.sin(2 * np.pi * 5.5 * t) * np.minimum(1, t / .15)
    x = (saw(f * vib, t) + .7 * saw(f * 1.006 * vib, t, .2) + .5 * np.sin(2 * np.pi * f * 2 * t)) / 2.2
    x = lp(x, 5200)
    return x * np.minimum(1, t / .01) * np.exp(-t * 2.2) * np.minimum(1, (dur - t) / .05).clip(0, 1) * .5
def bassn(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + .45 * saw(f, t) * np.exp(-t * 4) + .35 * np.sin(2 * np.pi * 2 * f * t)
    return lp(x, 900) * np.minimum(1, t / .005) * np.minimum(1, (dur - t).clip(0, .03) / .03) * .6
def padchord(notes, dur):
    n = int(dur * SR); t = np.arange(n) / SR; x = np.zeros(n)
    for m in notes + [notes[0] + 12]:
        f = mtof(m)
        for det in (-.0045, 0, .0045): x += saw(f * (1 + det), t, rng.random())
    x = lp(x / 12, 2400)
    return x * np.minimum(1, t / .25) * np.minimum(1, (dur - t).clip(0, .35) / .35)

# --- secuenciación ---
for b in range(nbars):
    t0 = b * BAR; chord, root = CH[b % 4]
    add(pad, padchord(chord, BAR + .25), t0, .55)
    for k in range(8):                                    # bajo en corcheas con síncopa
        if k in (0, 3, 4, 6, 7) or (k == 2 and b % 2):
            f = mtof(root + 12 * (1 if k in (3, 7) else 0)) * (1 if True else 1)
            add(bass, bassn(f, BEAT / 2 * .9), t0 + k * BEAT / 2, 1.0)
    for k in range(16):                                   # arpegio en semicorcheas, ping-pong estéreo
        notes = [chord[0] + 12, chord[1] + 12, chord[2] + 12, chord[1] + 24]
        m = notes[[0, 1, 2, 3, 2, 1, 0, 1][k % 8]] + (12 if k % 8 == 3 else 0)
        add(arp, pluck(mtof(m)), t0 + k * STEP, .55 * (1.0 if k % 4 == 0 else .72), pan=(-.5 if k % 2 else .5))
    for k in range(8):                                    # melodía principal
        add(lead, leadn(mtof(LEAD[b % 4][k]), BEAT / 2 * .95), t0 + k * BEAT / 2, .8, pan=.1)
    for beat in range(4):                                 # batería
        tb = t0 + beat * BEAT
        add(drums, kick(), tb, 1.0); kick_times.append(tb)
        if beat in (1, 3): add(drums, clap(), tb, .75)
        add(drums, hat(True), tb + BEAT / 2, .9, pan=.2)
        for sub in (0, 2):
            add(drums, hat(False), tb + sub * STEP + (STEP if sub == 0 else 0) * 0, .55, pan=-.15)

# transiciones: crash al cambiar de sección y redoble antes del gran final
for a in (s[2], s[5]):
    add(fx, crash(), a, .8)
    for k in range(8):                                    # redoble de caja subiendo
        tt = a - 8 * STEP * .5 + k * STEP * .5
        add(fx, clap(), tt, .25 + .06 * k)
add(fx, crash(), s[1], .35)
# acorde final sostenido
fin = padchord([57, 60, 64, 69], 1.6); add(fx, fin, T - 2.9, .6)

# --- mezcla por capas con sidechain (bombeo con el bombo) ---
sc = np.ones(N)
for kt in kick_times:
    i = int(kt * SR)
    if i >= N: continue
    m = min(N - i, int(.35 * SR)); tt = np.arange(m) / SR
    sc[i:i + m] = np.minimum(sc[i:i + m], 1 - .65 * np.exp(-tt * 9))
kenv = lay["kick"]; scd = 1 - (1 - sc) * kenv

def lerp_filter(buf, cut_lo, cut_hi, amt):
    lo = np.stack([lp(buf[:, c], cut_lo) for c in range(2)], 1)
    return lo * (1 - amt[:, None]) + buf * amt[:, None]

pad_f = lerp_filter(pad, 700, 20000, np.clip(lay["pad"] - .3, 0, 1))  # el pad se "abre" al avanzar
mix = (pad_f * lay["pad"][:, None] * scd[:, None] * 1.1 +
       arp * lay["arp"][:, None] * scd[:, None] * 1.0 +
       bass * lay["bass"][:, None] * scd[:, None] * .6 +
       lead * lay["lead"][:, None] * .7 +
       drums[:, :] * np.stack([lay["kick"]] * 2, 1) * .6 + fx)

# retardo ping-pong sobre arpegio y lead (ancho y emoción)
d = int(BEAT * .75 * SR); echo = np.zeros_like(mix)
src = (arp * lay["arp"][:, None] + lead * lay["lead"][:, None]) * .35
echo[d:, 0] += src[:-d, 1]; echo[d:, 1] += src[:-d, 0]
echo[2 * d:, 0] += src[:-2 * d, 0] * .5; echo[2 * d:, 1] += src[:-2 * d, 1] * .5
mix += echo
master = env_at([(0, 1.0), (s[1] - .05, 1.0), (s[1], .95), (s[2] - .05, .85), (s[2], .95), (s[5] - .05, .98), (s[5], 1.25), (T - 1.8, 1.25), (T, 1.0)])
mix *= master[:, None]

m = int(1.1 * SR); ir = rng.standard_normal((m, 2)) * np.exp(-np.arange(m) / SR * 4.5)[:, None]
ir = lp(ir.T, 7000).T; ir[0] = 0
wet = np.stack([fftconvolve(mix[:, c], ir[:, c])[:N] for c in range(2)], 1) * .045
mix = mix + wet
mix = np.tanh(mix * 1.15) / np.tanh(1.15)
rms = np.sqrt(np.mean(mix[int(s[2]*SR):int(s[5]*SR)] ** 2)); mix *= 10 ** ((-19 - 20 * np.log10(rms)) / 20)   # ~-18 LUFS de referencia
fade = np.minimum(1, np.arange(N) / SR / .25) * np.minimum(1, (T - np.arange(N) / SR) / 1.0)
mix *= fade[:, None]
wavfile.write(OUT, SR, (np.clip(mix, -1, 1) * 32767).astype(np.int16))
print("music ok", T, "s, BPM", BPM)
